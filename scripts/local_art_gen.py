import argparse
import base64
import os
import re
import sys
import time
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Add root project dir to pythonpath to allow relative imports from scripts
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from scripts.art_gen.character_db import CharacterDatabase
from scripts.art_gen.chapter_context import ChapterContext
from scripts.art_gen.utils import parse_chapter_selection
from scripts.art_gen.batch import run_chapter_batch_processing, build_common_argparser



MODEL_ALTERNATIVES = {
    "sdxl-novita": {
        "label": "SDXL 1.0 via Novita (Fidelidade Máxima I2I)",
        "model": "stabilityai/stable-diffusion-xl-base-1.0",
        "provider": "novita"
    },
    "flux1-schnell": {
        "label": "FLUX.1 Schnell (Rápido para API Serverless)",
        "model": "black-forest-labs/FLUX.1-schnell"
    },
    "flux1-dev": {
        "label": "FLUX.1 Dev (Melhor Composição para API Serverless)",
        "model": "black-forest-labs/FLUX.1-dev"
    }
}


def get_character_image(char_data, search_dir="docs/public/personagens"):
    for alias in char_data["aliases"]:
        # Tenta encontrar a imagem pelo apelido ou nome (ex: gabo.jpg, val.png)
        for ext in [".jpg", ".png", ".jpeg"]:
            test_path = os.path.join(search_dir, alias.lower() + ext)
            if os.path.exists(test_path):
                return test_path
    return None

# Compile regex at module level for performance
SNIPPET_CLEAN_RE = re.compile(r"\s+")

class OllamaClient:
    def __init__(self, model="qwen3:8b"):
        self.model = model
        self.api_url = "http://localhost:11434/api/generate"
        self.session = None

    def _get_session(self):
        if self.session is None:
            import requests
            self.session = requests.Session()
        return self.session

    def check_connection(self, max_retries=3, retry_delay=2):
        try:
            session = self._get_session()
            # Check if specified model exists, otherwise fallback to first available or qwen2.5:7b
            resp = session.get("http://localhost:11434/api/tags", timeout=5)
            if resp.status_code == 200:
                models = [m["name"] for m in resp.json().get("models", [])]
                if self.model not in models and models:
                    print(f"⚠️ Model {self.model} not found in Ollama. Using {models[0]}.")
                    self.model = models[0]
                return True
        except Exception:
            pass
        return False

    def build_fallback_prompt(self, chapter_text, active_characters, style):
        canon = "; ".join(f"{c['name']}: {c['description'][:150]}" for c in active_characters[:2])
        snippet = SNIPPET_CLEAN_RE.sub(" ", chapter_text[:300]).strip()
        return (
            f"Cinematic neo-noir cyberpunk frame, {style}. "
            f"High-end visual storytelling, dynamic composition, 35mm film aesthetic, "
            f"foreground subject with intense rim lighting, dense volumetric atmosphere, "
            f"Character continuity: {canon or 'urban survivalist'}. "
            f"Narrative beat: {snippet}. "
            "ultra cinematic, noir cyberpunk, film grain, masterpiece, 8k resolution"
        )

    def generate_prompt(self, chapter_text, active_characters, style):
        char_context = "\n".join(f"- {c['name']}: {c['description'][:400]}" for c in active_characters[:3])
        if not char_context:
            char_context = "- No specific character traits provided. Use generic cyberpunk survivors."

        payload = {
            "model": self.model,
            "stream": False,
            "system": (
                "You are an elite Hollywood visual director and concept artist. "
                "Your specialty is 'Nano Banana' style: high-contrast, atmospheric, "
                "emotionally charged neo-noir cyberpunk. You emphasize character visual fidelity "
                "by strictly adhering to provided physical traits (Visual DNA)."
            ),
            "prompt": (
                "Task: Generate ONE cinematic image prompt in English for the provided scene.\n\n"
                f"Visual Style: {style}\n\n"
                "STRICT CHARACTER VISUAL DNA (Must be accurately represented):\n"
                f"{char_context}\n\n"
                "CHAPTER NARRATIVE CONTEXT:\n"
                f"{chapter_text[:2500]}\n\n"
                "PROMPT REQUIREMENTS:\n"
                "1. SUBJECT: Place the characters mentioned in the specified environment.\n"
                "2. PHYSICALITY: You MUST include their specific traits (clothing, eyes, scars, hair) from the DNA in the prompt.\n"
                "3. COMPOSITION: Cinematic wide or medium shot, dynamic perspective.\n"
                "4. ATMOSPHERE: Dense fog, rain, neon glare, deep shadows (chiaroscuro).\n"
                "5. TEXTURE: 35mm film grain, high technical detail, realistic skin and fabric.\n"
                "6. NARRATIVE: Capture the specific mood of the chapter excerpt.\n"
                "7. Output ONLY the prompt string. End with: 'masterpiece, ultra-detailed, neo-noir cyberpunk, cinematic lighting, 8k'."
            ),
        }

        try:
            session = self._get_session()
            response = session.post(self.api_url, json=payload, timeout=300)
            response.raise_for_status()
            prompt = response.json().get("response", "").strip()
            # Remove thinking or preamble if present
            if "</thought>" in prompt:
                prompt = prompt.split("</thought>")[-1].strip()
            return prompt or self.build_fallback_prompt(chapter_text, active_characters, style)
        except Exception as e:
            print(f"⚠️ Prompt generation failed: {e}")
            return self.build_fallback_prompt(chapter_text, active_characters, style)


class HuggingFaceAPIClient:
    def __init__(self, model_family="sdxl-novita"):
        self.model_family = model_family
        config = MODEL_ALTERNATIVES.get(model_family, MODEL_ALTERNATIVES["sdxl-novita"])
        model_id = config.get("model")
        provider = config.get("provider")

        self.api_url = f"https://router.huggingface.co/hf-inference/models/{model_id}"
        if provider:
            self.api_url += f"?provider={provider}"

        self.token = os.environ.get("HF_TOKEN")
        if not self.token:
            print("⚠️ HF_TOKEN not found in environment. API calls will likely fail with 401 Unauthorized.")

        self.session = None

    def _get_session(self):
        if self.session is None:
            import requests
            self.session = requests.Session()
        return self.session

    def generate_art(self, prompt, output_path, image_path=None, strength=0.1, dry_run=False):
        if dry_run:
            print(f"🧪 [DRY RUN] Prompt final:\n{prompt}\n")
            if image_path:
                print(f"🧪 [DRY RUN] Using base image for I2I: {image_path} (Strength: {strength})")
            return True

        print(f"🌐 Requesting image from {self.api_url}...")
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        payload = {"inputs": prompt}
        
        # Se houver imagem base, ativa o modo Image-to-Image
        if image_path and os.path.exists(image_path):
            print(f"🖼️ Using character base image: {image_path}")
            with open(image_path, "rb") as f:
                img_base64 = base64.b64encode(f.read()).decode('utf-8')
            payload["image"] = img_base64

            # Modelos flux1 na hf-inference podem falhar se passarmos 'strength' e afins em I2I
            if "flux1" not in self.model_family:
                payload["parameters"] = {
                    "strength": strength,
                    "guidance_scale": 12.0,
                    "num_inference_steps": 40
                }
        
        try:
            session = self._get_session()
            response = session.post(
                self.api_url, 
                headers=headers, 
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                with open(output_path, "wb") as f:
                    f.write(response.content)
                return True
            else:
                print(f"❌ API Error {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to reach Hugging Face API: {e}")
            return False


def process_chapter(chapter_num, text_engine, image_engine, db, project_root, style, dry_run):
    chapter = ChapterContext(Path(f"docs/capitulo-{chapter_num}.md"))
    active_chars = db.find_characters_in_text(chapter.body)
    prompt = text_engine.generate_prompt(chapter.body, active_chars, style)

    if active_chars:
        cast_hint = ", ".join(c["name"] for c in active_chars[:6])
        prompt = f"{prompt}. Characters featured: {cast_hint}."

    output_filename = f"capitulo_{chapter_num}.jpg"
    output_path = Path(project_root) / "docs/public" / output_filename
    output_path.parent.mkdir(parents=True, exist_ok=True)

    ok = image_engine.generate_art(prompt, str(output_path), dry_run=dry_run)
    if ok and not dry_run:
        chapter.update_frontmatter(f"/{output_filename}")
    return ok


def main():
    parser = build_common_argparser("Generate chapter art locally (Open Source Nano Banana quality)")
    parser.add_argument("--ollama-model", default="qwen2.5:7b", help="Ollama model for prompt generation")
    parser.add_argument("--model-family", default="sdxl-novita", choices=MODEL_ALTERNATIVES.keys())
    parser.add_argument("--strength", type=float, default=0.1, help="I2I transformation strength (0.1 = max face fidelity)")
    parser.add_argument("--output-suffix", default="", help="Suffix for the output filename (e.g., _heavy)")
    parser.add_argument("--dry-run", action="store_true", help="Print prompts without generating images")
    args = parser.parse_args()

    chapters = parse_chapter_selection(args.chapters)
    project_root = os.getcwd()

    text_engine = OllamaClient(model=args.ollama_model)
    if not text_engine.check_connection():
        print("⚠️ Ollama offline. Falling back to deterministic prompt templates.")

    try:
        # Pass steps override to image engine if provided
        image_engine = HuggingFaceAPIClient(model_family=args.model_family)
            
        db = CharacterDatabase(os.path.join(project_root, "docs/personagens.md"))

        def worker(chapter_num):
            print(f"\n📂 Processing chapter {chapter_num}")
            
            chapter = ChapterContext(Path(f"docs/capitulo-{chapter_num}.md"))
            active_chars = db.find_characters_in_text(chapter.body)
            
            # Buscar imagem do personagem principal (o primeiro encontrado)
            image_path = None
            if active_chars:
                image_path = get_character_image(active_chars[0])
                if image_path:
                    print(f"👤 Primary character detected: {active_chars[0]['name']} (Image found)")
                else:
                    print(f"👤 Primary character detected: {active_chars[0]['name']} (No base image found)")

            prompt = text_engine.generate_prompt(chapter.body, active_chars, args.style)

            if active_chars:
                cast_hint = ", ".join(c["name"] for c in active_chars[:6])
                prompt = f"{prompt}. Characters featured: {cast_hint}."

            output_filename = f"capitulo_{chapter_num}{args.output_suffix}.jpg"
            output_path = Path(project_root) / "docs/public" / output_filename
            output_path.parent.mkdir(parents=True, exist_ok=True)

            ok = image_engine.generate_art(
                prompt, 
                str(output_path), 
                image_path=image_path, 
                strength=args.strength,
                dry_run=args.dry_run
            )
            
            if ok and not args.dry_run:
                chapter.update_frontmatter(f"/{output_filename}")
            
            return ok

        success_count = run_chapter_batch_processing(chapters, worker, args.max_workers)

        print(f"\n🏁 Done. Successful chapters: {success_count}/{len(chapters)}")
    except Exception as exc:
        import traceback
        traceback.print_exc()
        print(f"❌ Fatal error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()

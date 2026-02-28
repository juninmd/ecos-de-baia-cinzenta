import argparse
import os
import re
import sys
import time
from pathlib import Path

import requests

try:
    import torch
    from diffusers import FluxPipeline
except ImportError:
    torch = None
    FluxPipeline = None

MODEL_ALTERNATIVES = {
    "flux2-dev": {
        "label": "FLUX.2 Dev (melhor qualidade geral)",
        "local_model_id": "black-forest-labs/FLUX.2-dev",
        "size": (768, 1024),
        "steps": 28, # Modelos 'dev' precisam de mais passos (20-30) do que os 'schnell' (4-8)
    }
}


class CharacterDatabase:
    def __init__(self, filepath):
        self.filepath = filepath
        self.characters = {}
        self.load()

    def load(self):
        if not os.path.exists(self.filepath):
            print(f"⚠️ Character file not found at {self.filepath}")
            return

        with open(self.filepath, "r", encoding="utf-8") as f:
            content = f.read()

        for section in re.split(r"\n## ", content):
            if not section.strip() or section.startswith("# "):
                continue

            lines = section.split("\n")
            name_line = lines[0].strip().replace("*", "")
            # Remove anything in parentheses or brackets
            name_clean = re.sub(r"\s*[\(\[].*?[\)\]]", "", name_line).strip()

            description = []
            for line in lines:
                clean = line.replace("*", "").strip()
                if any(
                    key in clean
                    for key in [
                        "Porte Físico:",
                        "Vestuário:",
                        "Marcas Distintivas:",
                        "Cabelo:",
                        "Olhos:",
                        "Rosto:",
                        "Idade:",
                        "Equipamento:",
                    ]
                ):
                    description.append(clean)

            aliases = {name_clean}
            nick = re.search(r'"(.*?)"', name_clean)
            if nick:
                aliases.add(nick.group(1))
            first = name_clean.split()[0] if name_clean.split() else ""
            if len(first) > 2:
                aliases.add(first)

            self.characters[name_clean] = {
                "name": name_clean,
                "aliases": list(aliases),
                "description": ". ".join(description),
            }
        print(f"📊 Loaded {len(self.characters)} characters from database.")

    def find_characters_in_text(self, text):
        found = []
        for char_data in self.characters.values():
            for alias in char_data["aliases"]:
                if re.search(rf"\b{re.escape(alias)}\b", text, re.IGNORECASE):
                    found.append(char_data)
                    break
        return found


class ChapterContext:
    def __init__(self, chapter_num):
        self.chapter_num = chapter_num
        self.filepath = Path(f"docs/capitulo-{chapter_num}.md")
        self.content = ""
        self.frontmatter = ""
        self.body = ""
        self.load()

    def load(self):
        if not self.filepath.exists():
            raise FileNotFoundError(f"Chapter file not found: {self.filepath}")

        self.content = self.filepath.read_text(encoding="utf-8")
        if self.content.startswith("---"):
            parts = self.content.split("---", 2)
            if len(parts) >= 3:
                self.frontmatter = parts[1]
                self.body = parts[2]
                return
        self.body = self.content

    def update_frontmatter(self, image_path):
        public_path = image_path if image_path.startswith("/") else f"/{os.path.basename(image_path)}"

        if self.frontmatter:
            if "image:" in self.frontmatter:
                self.frontmatter = re.sub(r"image:.*", f"image: {public_path}", self.frontmatter)
            else:
                self.frontmatter = self.frontmatter.rstrip() + f"\nimage: {public_path}\n"
        else:
            self.frontmatter = f"\nimage: {public_path}\n"

        self.filepath.write_text(f"---{self.frontmatter}---{self.body}", encoding="utf-8")
        print(f"✅ Updated {self.filepath} with image: {public_path}")


class OllamaClient:
    def __init__(self, model="qwen3:8b"):
        self.model = model
        self.api_url = "http://localhost:11434/api/generate"

    def check_connection(self, max_retries=3, retry_delay=2):
        try:
            # Check if specified model exists, otherwise fallback to first available or qwen2.5:7b
            resp = requests.get("http://localhost:11434/api/tags", timeout=5)
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
        snippet = re.sub(r"\s+", " ", chapter_text[:300]).strip()
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
                "emotionally charged neo-noir cyberpunk. You prioritize character consistency "
                "and symbolic storytelling through light and shadow."
            ),
            "prompt": (
                "Task: Select the most visually impactful moment from the chapter excerpt and write ONE production-ready image prompt in English.\n\n"
                f"Visual Style: {style}\n"
                f"Character Canon (Reference only):\n{char_context}\n\n"
                f"Chapter Excerpt (PRIORITIZE NEW EVOLUTIONS HERE):\n{chapter_text[:3000]}\n\n"
                "Requirements:\n"
                "1. Focus on ONE clear composition (Medium or Wide shot preferred).\n"
                "2. If the chapter text describes a character differently from the canon (e.g., new clothing or cybernetics), ALWAYS follow the chapter text.\n"
                "3. Describe the lighting (Rim light, neon reflections, harsh contrast).\n"
                "4. Include environmental details (smog, rain, textures like wet concrete or sterile chrome).\n"
                "5. Capture the emotional weight/action beat of the scene.\n"
                "6. No dialogue, no meta-text, max 170 words.\n"
                "7. MUST end with: ultra cinematic, neo-noir cyberpunk, volumetric lighting, film grain, masterpiece."
            ),
        }

        try:
            response = requests.post(self.api_url, json=payload, timeout=300)
            response.raise_for_status()
            prompt = response.json().get("response", "").strip()
            # Remove thinking or preamble if present
            if "</thought>" in prompt:
                prompt = prompt.split("</thought>")[-1].strip()
            return prompt or self.build_fallback_prompt(chapter_text, active_characters, style)
        except Exception as e:
            print(f"⚠️ Prompt generation failed: {e}")
            return self.build_fallback_prompt(chapter_text, active_characters, style)


class LocalDiffusionClient:
    def __init__(self, model_family="flux2-dev"):
        self.model_family = model_family
        self.pipeline = None
        self.device = "cpu"
        self.negative_prompt = (
            "low quality, blurry, bad anatomy, extra limbs, duplicated body, text, watermark, logo, anime, cartoon"
        )

    def _setup_pipeline(self):
        if not (torch and FluxPipeline):
            raise RuntimeError("Missing torch/diffusers dependencies for local generation")

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        cfg = MODEL_ALTERNATIVES[self.model_family]
        model_id = os.environ.get("ART_MODEL_ID", cfg["local_model_id"])

        self.pipeline = self._load_pipeline(self.model_family, model_id)
        self.pipeline.to(self.device)
        if hasattr(self.pipeline, "enable_attention_slicing"):
            self.pipeline.enable_attention_slicing()

    def _load_pipeline(self, family, model_id):
        if FluxPipeline is None:
            raise RuntimeError("FluxPipeline unavailable in installed diffusers version")
        dtype = torch.bfloat16 if self.device == "cuda" else torch.float32
        return FluxPipeline.from_pretrained(model_id, torch_dtype=dtype)

    def generate_art(self, prompt, output_path, dry_run=False):
        if dry_run:
            print(f"🧪 [DRY RUN] Prompt final:\n{prompt}\n")
            return True

        if self.pipeline is None:
            self._setup_pipeline()

        steps = MODEL_ALTERNATIVES[self.model_family]["steps"]
        guidance = 0.0 if "schnell" in self.model_family else 3.5 if "flux" in self.model_family else 7.0
        
        image = self.pipeline(
            prompt=prompt,
            negative_prompt=self.negative_prompt,
            num_inference_steps=steps,
            guidance_scale=guidance,
        ).images[0]
        image.save(output_path)
        return True


def parse_chapter_selection(raw: str):
    selected = []
    for chunk in raw.replace(" ", "").split(","):
        if "-" in chunk:
            start, end = map(int, chunk.split("-"))
            selected.extend(range(start, end + 1))
        elif chunk:
            selected.append(int(chunk))
    return sorted(set(selected))


def process_chapter(chapter_num, text_engine, image_engine, db, project_root, style, dry_run):
    chapter = ChapterContext(chapter_num)
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
    parser = argparse.ArgumentParser(description="Generate chapter art locally (Open Source Nano Banana quality)")
    parser.add_argument("chapters", type=str, help="Chapter number, list (1,2,3) or range (10-14)")
    parser.add_argument("--style", default="neo-noir cinematic cyberpunk", help="Visual style modifier")
    parser.add_argument("--ollama-model", default="qwen2.5:7b", help="Ollama model for prompt generation")
    parser.add_argument("--model-family", default="flux2-dev", choices=MODEL_ALTERNATIVES.keys())
    parser.add_argument("--steps", type=int, help="Override default inference steps")
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
        image_engine = LocalDiffusionClient(model_family=args.model_family)
        if args.steps:
            MODEL_ALTERNATIVES[args.model_family]["steps"] = args.steps
            
        db = CharacterDatabase(os.path.join(project_root, "docs/personagens.md"))

        success_count = 0
        for chapter_num in chapters:
            print(f"\n📂 Processing chapter {chapter_num}")
            
            # Custom process_chapter to handle suffix
            chapter = ChapterContext(chapter_num)
            active_chars = db.find_characters_in_text(chapter.body)
            prompt = text_engine.generate_prompt(chapter.body, active_chars, args.style)

            if active_chars:
                cast_hint = ", ".join(c["name"] for c in active_chars[:6])
                prompt = f"{prompt}. Characters featured: {cast_hint}."

            output_filename = f"capitulo_{chapter_num}{args.output_suffix}.jpg"
            output_path = Path(project_root) / "docs/public" / output_filename
            output_path.parent.mkdir(parents=True, exist_ok=True)

            ok = image_engine.generate_art(prompt, str(output_path), dry_run=args.dry_run)
            if ok and not args.dry_run:
                # Only update frontmatter if it's the main image (no suffix) or if we want it to be the new default
                # For multiple versions, we might not want to overwrite 'image:' unless it's the "primary" one.
                # But the user wants them to "work", so maybe the first one that finishes wins?
                # For now, let's update it anyway, the last one to finish will set the default.
                chapter.update_frontmatter(f"/{output_filename}")
            
            if ok:
                success_count += 1

        print(f"\n🏁 Done. Successful chapters: {success_count}/{len(chapters)}")
    except Exception as exc:
        print(f"❌ Fatal error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()

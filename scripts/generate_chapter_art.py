import argparse
import os
import re
import sys
import time

import requests

# Optional local backends
try:
    import torch
    from diffusers import FluxPipeline, StableDiffusionPipeline, StableDiffusionXLPipeline
except ImportError:
    torch = None
    FluxPipeline = None
    StableDiffusionPipeline = None
    StableDiffusionXLPipeline = None


MODEL_ALTERNATIVES = {
    "flux-schnell": {
        "label": "FLUX.1 Schnell (open source, melhor qualidade geral)",
        "local_model_id": "black-forest-labs/FLUX.1-schnell",
        "size": (768, 1024),
        "steps": 28,
        "sampler": "DPM++ 2M Karras",
    },
    "sdxl": {
        "label": "Stable Diffusion XL 1.0 (boa fidelidade de composição)",
        "local_model_id": "stabilityai/stable-diffusion-xl-base-1.0",
        "size": (768, 1024),
        "steps": 32,
        "sampler": "DPM++ 2M Karras",
    },
    "sd15": {
        "label": "Stable Diffusion 1.5 (rápido, menor qualidade)",
        "local_model_id": "runwayml/stable-diffusion-v1-5",
        "size": (768, 1024),
        "steps": 30,
        "sampler": "DPM++ 2M Karras",
    },
}


def print_alternatives() -> None:
    print("\n🎨 Alternativas open source próximas do Nano Banana")
    print("=" * 64)
    for key, data in MODEL_ALTERNATIVES.items():
        print(f"- {key}: {data['label']}")
        print(f"  model_id: {data['local_model_id']}")
    print("\n✅ Recomendada (implementada por padrão): flux-schnell\n")


class CharacterDatabase:
    def __init__(self, filepath):
        self.filepath = filepath
        self.characters = {}
        self.load()

    def load(self):
        if not os.path.exists(self.filepath):
            print(f"⚠️ Warning: Character file not found at {self.filepath}")
            return

        with open(self.filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        sections = re.split(r'\n## ', content)

        for section in sections:
            if not section.strip() or section.startswith('# '):
                continue

            lines = section.split('\n')
            name_line = lines[0].strip()
            name_clean = re.sub(r'\s*\[.*?\]', '', name_line).strip().replace('*', '').strip()

            image_match = re.search(r'!\[.*?\]\((.*?)\)', section)
            image_path = image_match.group(1) if image_match else None

            description_parts = []
            for line in lines:
                clean_line = line.strip().replace('*', '')
                if any(
                    key in clean_line
                    for key in [
                        "Porte Físico:",
                        "Vestuário:",
                        "Marcas Distintivas:",
                        "Cabelo:",
                        "Olhos:",
                        "Rosto:",
                        "Idade:",
                    ]
                ):
                    description_parts.append(clean_line)

            aliases = {name_clean}
            nickname_match = re.search(r'"(.*?)"', name_clean)
            if nickname_match:
                aliases.add(nickname_match.group(1))

            parts = name_clean.split()
            if parts and len(parts[0]) > 2:
                aliases.add(parts[0])

            self.characters[name_clean] = {
                "name": name_clean,
                "aliases": list(aliases),
                "image": image_path,
                "description": ". ".join(description_parts),
            }

        print(f"📚 Loaded {len(self.characters)} characters from database.")

    def find_characters_in_text(self, text):
        found = []
        text_lower = text.lower()

        alias_map = {}
        all_aliases = []
        for char_data in self.characters.values():
            for alias in char_data["aliases"]:
                lower_alias = alias.lower()
                if len(lower_alias) < 3:
                    continue
                if lower_alias not in alias_map:
                    alias_map[lower_alias] = []
                    all_aliases.append(re.escape(lower_alias))
                alias_map[lower_alias].append(char_data)

        if not all_aliases:
            return found

        all_aliases.sort(key=len, reverse=True)
        pattern = r'\b(' + '|'.join(all_aliases) + r')\b'
        matches = set(re.findall(pattern, text_lower))

        found_ids = set()
        for match in matches:
            if match in alias_map:
                for char_data in alias_map[match]:
                    if char_data["name"] not in found_ids:
                        found.append(char_data)
                        found_ids.add(char_data["name"])
        return found


class ChapterContext:
    def __init__(self, filepath):
        self.filepath = filepath
        self.content = ""
        self.frontmatter = ""
        self.body = ""
        self.load()

    def load(self):
        if not os.path.exists(self.filepath):
            print(f"❌ Error: Chapter file not found at {self.filepath}")
            sys.exit(1)

        with open(self.filepath, 'r', encoding='utf-8') as f:
            self.content = f.read()

        if self.content.startswith('---'):
            parts = self.content.split('---', 2)
            if len(parts) >= 3:
                self.frontmatter = parts[1]
                self.body = parts[2]
            else:
                self.body = self.content
        else:
            self.body = self.content

    def update_frontmatter(self, image_path):
        public_path = image_path if image_path.startswith('/') else '/' + os.path.basename(image_path)

        if self.frontmatter:
            if 'image:' in self.frontmatter:
                self.frontmatter = re.sub(r'image:.*', f'image: {public_path}', self.frontmatter)
            else:
                self.frontmatter = self.frontmatter.rstrip() + f'\nimage: {public_path}\n'
        else:
            self.frontmatter = f'\nimage: {public_path}\n'

        new_content = f'---{self.frontmatter}---{self.body}'
        with open(self.filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ Updated frontmatter in {self.filepath}")


class OllamaClient:
    def __init__(self, host=None, model="llama3.1:8b"):
        self.host = host or os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        self.model = model
        self.api_url = f"{self.host}/api/generate"
        print(f"🦙 Initializing Ollama Client ({self.host}) with model: {self.model}...")

    def check_connection(self, max_retries=3, retry_delay=2):
        for attempt in range(max_retries):
            try:
                response = requests.get(self.host, timeout=5)
                if response.status_code == 200:
                    print(f"✅ Successfully connected to Ollama at {self.host}")
                    return True
                raise Exception(f"HTTP {response.status_code}")
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"⚠️ Connection attempt {attempt + 1} failed, retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                else:
                    print(f"❌ Failed to connect to Ollama after {max_retries} attempts: {e}")
        return False

    def generate_prompt(self, chapter_text, active_characters, style):
        char_descriptions = [f"- {c['name']}: {c['description'][:240]}" for c in active_characters[:3]]
        char_context = "\n".join(char_descriptions) if char_descriptions else "- No named characters detected"

        system_prompt = (
            "You are a senior cinematic art director building prompts for a noir cyberpunk bestseller. "
            "Return ONE production-ready image prompt with coherent character continuity and strong storytelling."
        )

        user_prompt = (
            "Select the single most dramatic visual moment from this chapter excerpt.\n"
            f"TARGET STYLE: {style}\n"
            "PRIORITY: preserve canonical character appearance and emotional tone.\n"
            f"CHARACTER BIBLE (must respect):\n{char_context}\n\n"
            f"CHAPTER TEXT:\n{chapter_text[:2400]}...\n\n"
            "INSTRUCTIONS:\n"
            "1. Write in English.\n"
            "2. Include framing and camera language (wide shot / close-up / lens feeling).\n"
            "3. Include lighting design, weather, texture, and atmosphere.\n"
            "4. Include exact character poses, action beat, and key props from scene.\n"
            "5. Keep continuity with canon visuals and avoid generic substitutions.\n"
            "6. Output only the final prompt text, no quotes, no explanations.\n"
            "7. Max 170 words.\n"
            "8. End with: ultra cinematic, noir cyberpunk, volumetric rain, film grain, masterpiece."
        )

        payload = {"model": self.model, "prompt": user_prompt, "system": system_prompt, "stream": False}

        try:
            print("... Sending request to Ollama...")
            response = requests.post(self.api_url, json=payload, timeout=300)
            response.raise_for_status()
            return response.json().get("response", "").strip()
        except requests.exceptions.Timeout:
            print("⚠️ Ollama request timed out after 300 seconds")
            return None
        except Exception as e:
            print(f"⚠️ Ollama Generation Failed: {e}")
            return None


class ImageGenerator:
    def __init__(self, api_url=None, model_family="flux-schnell"):
        self.api_url = api_url or os.environ.get("SD_API_URL")
        self.model_family = model_family
        self.pipeline = None
        self.device = "cpu"
        self.negative_prompt = (
            "low quality, blurry, bad anatomy, extra limbs, deformed face, duplicated character, "
            "text, watermark, logo, frame, jpeg artifacts, cartoon, anime"
        )

    def _setup_local_pipeline(self):
        if not (torch and StableDiffusionPipeline):
            print("⚠️ Diffusers/Torch not installed. Local generation unavailable.")
            return

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        if self.device == "cpu":
            print("⚠️ No GPU detected. Local generation will be slow.")

        model_cfg = MODEL_ALTERNATIVES[self.model_family]
        model_id = os.environ.get("ART_MODEL_ID", model_cfg["local_model_id"])
        print(f"⚙️ Initializing local pipeline '{self.model_family}' with {model_id} on {self.device}...")

        try:
            if self.model_family == "flux-schnell":
                if FluxPipeline is None:
                    raise RuntimeError("FluxPipeline indisponível na versão atual do diffusers.")

                dtype = torch.bfloat16 if self.device == "cuda" else torch.float32
                self.pipeline = FluxPipeline.from_pretrained(model_id, torch_dtype=dtype)
            elif self.model_family == "sdxl":
                dtype = torch.float16 if self.device == "cuda" else torch.float32
                self.pipeline = StableDiffusionXLPipeline.from_pretrained(model_id, torch_dtype=dtype)
            else:
                self.pipeline = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float32)

            self.pipeline.to(self.device)
            if hasattr(self.pipeline, "enable_attention_slicing"):
                self.pipeline.enable_attention_slicing()
        except Exception as e:
            print(f"❌ Failed to load local model '{model_id}': {e}")
            self.pipeline = None

    def _remote_payload(self, prompt):
        cfg = MODEL_ALTERNATIVES[self.model_family]
        width, height = cfg["size"]
        payload = {
            "prompt": prompt,
            "negative_prompt": self.negative_prompt,
            "steps": cfg["steps"],
            "cfg_scale": 7.0 if self.model_family == "flux-schnell" else 7.5,
            "width": width,
            "height": height,
            "sampler_name": cfg["sampler"],
        }
        if self.model_family == "flux-schnell":
            payload["scheduler"] = "Simple"
        return payload

    def generate(self, prompt, output_path, dry_run=False):
        if dry_run:
            print(f"🧪 [DRY RUN] Would generate image using '{self.model_family}' for prompt: {prompt}")
            return True

        if self.api_url:
            return self._generate_remote(prompt, output_path)

        if self.pipeline is None:
            self._setup_local_pipeline()

        if self.pipeline:
            return self._generate_local(prompt, output_path)

        print("❌ No image generation backend available (No API URL and No Local pipeline).")
        return False

    def _generate_remote(self, prompt, output_path):
        print(f"🌐 Sending to Remote SD API: {self.api_url} (model_family={self.model_family})")
        payload = self._remote_payload(prompt)
        try:
            resp = requests.post(f"{self.api_url}/sdapi/v1/txt2img", json=payload, timeout=300)
            resp.raise_for_status()
            image_b64 = resp.json()['images'][0]

            import base64
            with open(output_path, "wb") as f:
                f.write(base64.b64decode(image_b64))
            print(f"✅ Image saved to {output_path}")
            return True
        except requests.exceptions.Timeout:
            print("❌ Remote SD API request timed out after 300 seconds")
            return False
        except Exception as e:
            print(f"❌ Remote Generation Failed: {e}")
            return False

    def _generate_local(self, prompt, output_path):
        print(f"🖥️ Generating locally on {self.device} with {self.model_family}...")
        try:
            cfg = MODEL_ALTERNATIVES[self.model_family]
            width, height = cfg["size"]

            if self.model_family == "flux-schnell":
                result = self.pipeline(
                    prompt,
                    guidance_scale=3.5,
                    num_inference_steps=cfg["steps"],
                    width=width,
                    height=height,
                    max_sequence_length=512,
                )
            else:
                result = self.pipeline(
                    prompt,
                    negative_prompt=self.negative_prompt,
                    num_inference_steps=cfg["steps"],
                    guidance_scale=7.5,
                    width=width,
                    height=height,
                )

            image = result.images[0]
            image.save(output_path)
            print(f"✅ Image saved to {output_path}")
            return True
        except Exception as e:
            print(f"❌ Local Generation Failed: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description="Automated Chapter Art Generator")
    parser.add_argument('--chapter', required=False, help="Path to chapter markdown file")
    parser.add_argument('--style', default="neo-noir cyberpunk, dramatic lighting, rainy atmosphere, realistic textures", help="Art style")
    parser.add_argument('--ollama-model', default=os.environ.get('OLLAMA_MODEL', 'llama3.1:8b'), help="Ollama model to use")
    parser.add_argument('--model-family', default=os.environ.get('ART_MODEL_FAMILY', 'flux-schnell'), choices=MODEL_ALTERNATIVES.keys(), help="Open source image model family")
    parser.add_argument('--dry-run', action='store_true', help="Skip image generation")
    parser.add_argument('--list-alternatives', action='store_true', help="List open source alternatives and exit")
    args = parser.parse_args()

    if args.list_alternatives:
        print_alternatives()
        return

    if not args.chapter:
        parser.error("--chapter is required unless --list-alternatives is used")

    project_root = os.getcwd()
    char_file = os.path.join(project_root, "docs/personagens.md")

    db = CharacterDatabase(char_file)

    chapter_path = args.chapter
    if not os.path.exists(chapter_path):
        if os.path.exists(os.path.join("docs/public", chapter_path)):
            chapter_path = os.path.join("docs/public", chapter_path)
        elif os.path.exists(os.path.join("docs", chapter_path)):
            chapter_path = os.path.join("docs", chapter_path)

    print(f"📖 Reading chapter: {chapter_path}")
    chapter = ChapterContext(chapter_path)

    active_chars = db.find_characters_in_text(chapter.body)
    print(f"👥 Characters detected: {[c['name'] for c in active_chars]}")

    ollama = OllamaClient(model=args.ollama_model)

    if not ollama.check_connection():
        print(f"⚠️ Cannot connect to Ollama at {ollama.host}. Using fallback prompt.")
        char_bits = ", ".join([f"{c['name']} ({c['description'][:110]})" for c in active_chars[:3]])
        prompt = (
            f"cinematic chapter illustration, {args.style}, rain-soaked noir city, intense dramatic moment, "
            f"consistent character canon: {char_bits}, dynamic composition, high detail, "
            "ultra cinematic, noir cyberpunk, volumetric rain, film grain, masterpiece"
        )
    else:
        prompt = ollama.generate_prompt(chapter.body, active_chars, args.style)

    if not prompt:
        print("❌ Failed to generate prompt.")
        sys.exit(1)

    print(f"\n🎨 Generated Prompt:\n{prompt}\n")

    base_name = os.path.basename(chapter_path).replace('.md', '.jpg').replace('-', '_')
    output_path = os.path.join("docs/public", base_name)

    generator = ImageGenerator(model_family=args.model_family)
    success = generator.generate(prompt, output_path, dry_run=args.dry_run)

    if success and not args.dry_run:
        chapter.update_frontmatter(f"/{base_name}")


if __name__ == "__main__":
    main()

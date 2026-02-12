import os
import re
import argparse
import sys
import requests
import time
import json

# Try to import torch/diffusers, but don't fail immediately if missing
try:
    import torch
    from diffusers import StableDiffusionPipeline
except ImportError:
    torch = None
    StableDiffusionPipeline = None

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

        # Split by level 2 headers
        sections = re.split(r'\n## ', content)

        for section in sections:
            if not section.strip() or section.startswith('# '):
                continue

            lines = section.split('\n')
            name_line = lines[0].strip()
            # Clean name from markdown links or bolding
            name_clean = re.sub(r'\s*\[.*?\]', '', name_line).strip()
            name_clean = name_clean.replace('*', '').strip()

            # Extract image path if exists
            image_match = re.search(r'!\[.*?\]\((.*?)\)', section)
            image_path = image_match.group(1) if image_match else None

            # Extract description fields
            description_parts = []
            capture = False
            for line in lines:
                clean_line = line.strip().replace('*', '')
                if any(key in clean_line for key in ["Porte Físico:", "Vestuário:", "Marcas Distintivas:", "Cabelo:", "Olhos:", "Rosto:", "Idade:"]):
                    description_parts.append(clean_line)

            full_desc = ". ".join(description_parts)

            # Generate aliases for searching in text
            aliases = set()
            aliases.add(name_clean)

            # Extract nickname from quotes e.g. Gabriel "Gabo" Moretti
            nickname_match = re.search(r'"(.*?)"', name_clean)
            if nickname_match:
                aliases.add(nickname_match.group(1))

            # First name
            parts = name_clean.split()
            if parts and len(parts[0]) > 2:
                aliases.add(parts[0])

            self.characters[name_clean] = {
                "name": name_clean,
                "aliases": list(aliases),
                "image": image_path,
                "description": full_desc,
                "raw_section": section
            }
        print(f"📚 Loaded {len(self.characters)} characters from database.")

    def find_characters_in_text(self, text):
        found = []
        text_lower = text.lower()

        # Build map and pattern
        alias_map = {}
        all_aliases = []
        for char_data in self.characters.values():
            for alias in char_data["aliases"]:
                lower_alias = alias.lower()
                # avoid short common words unless specific
                if len(lower_alias) < 3:
                    continue

                if lower_alias not in alias_map:
                    alias_map[lower_alias] = []
                    all_aliases.append(re.escape(lower_alias))
                alias_map[lower_alias].append(char_data)

        if not all_aliases:
            return found

        # Sort by length to match longest aliases first
        all_aliases.sort(key=len, reverse=True)
        pattern = r'\b(' + '|'.join(all_aliases) + r')\b'

        matches = set(re.findall(pattern, text_lower))

        # Deduplicate characters
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
        # Ensure path format
        if not image_path.startswith('/'):
            public_path = '/' + os.path.basename(image_path)
        else:
            public_path = image_path

        if self.frontmatter:
            if 'image:' in self.frontmatter:
                self.frontmatter = re.sub(r'image:.*', f'image: {public_path}', self.frontmatter)
            else:
                # Add to end of frontmatter
                self.frontmatter = self.frontmatter.rstrip() + f'\nimage: {public_path}\n'
        else:
            self.frontmatter = f'\nimage: {public_path}\n'

        new_content = f'---{self.frontmatter}---{self.body}'

        with open(self.filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ Updated frontmatter in {self.filepath}")

class OllamaClient:
    def __init__(self, host=None, model="llama3"):
        self.host = host or os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        self.model = model
        self.api_url = f"{self.host}/api/generate"
        print(f"🦙 Initializing Ollama Client ({self.host}) with model: {self.model}...")

    def check_connection(self, max_retries=3, retry_delay=2):
        """Check if Ollama is accessible with retries"""
        for attempt in range(max_retries):
            try:
                response = requests.get(self.host, timeout=5)
                if response.status_code == 200:
                    print(f"✅ Successfully connected to Ollama at {self.host}")
                    return True
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"⚠️ Connection attempt {attempt + 1} failed, retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                else:
                    print(f"❌ Failed to connect to Ollama after {max_retries} attempts: {e}")
        return False

    def generate_prompt(self, chapter_text, active_characters, style):
        char_descriptions = []
        for c in active_characters[:2]: # Limit to top 2 characters to avoid confusion
            char_descriptions.append(f"{c['name']}: {c['description']}")

        char_context = "\n".join(char_descriptions)

        system_prompt = (
            "You are an expert visual director for a sci-fi noir graphic novel. "
            "Your task is to create a SINGLE, highly detailed Stable Diffusion prompt based on the provided text."
        )

        user_prompt = (
            f"Analyze this chapter snippet and extract the most visually striking scene.\n"
            f"STYLE: {style}\n"
            f"CHARACTERS TO INCLUDE (Use their visual traits):\n{char_context}\n\n"
            f"CHAPTER TEXT:\n{chapter_text[:2000]}...\n\n" # Limit text length
            f"INSTRUCTIONS:\n"
            f"1. Describe the scene vividly (lighting, camera angle, atmosphere).\n"
            f"2. Describe the characters appearance based on the provided traits.\n"
            f"3. Output ONLY the prompt text. Do not add 'Here is the prompt' or quotes.\n"
            f"4. Keep it under 100 words."
        )

        payload = {
            "model": self.model,
            "prompt": user_prompt,
            "system": system_prompt,
            "stream": False
        }

        try:
            print("... Sending request to Ollama...")
            # Increase timeout to 5 minutes for larger models and slower systems
            response = requests.post(self.api_url, json=payload, timeout=300)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "").strip()
        except requests.exceptions.Timeout:
            print(f"⚠️ Ollama request timed out after 300 seconds")
            return None
        except Exception as e:
            print(f"⚠️ Ollama Generation Failed: {e}")
            return None

class ImageGenerator:
    def __init__(self, api_url=None):
        self.api_url = api_url or os.environ.get("SD_API_URL")
        self.pipeline = None
        self.device = "cpu"

        if not self.api_url:
            self._setup_local_pipeline()

    def _setup_local_pipeline(self):
        if torch and StableDiffusionPipeline:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            if self.device == "cpu":
                print("⚠️  No GPU detected. Local generation will be VERY slow.")

            print(f"⚙️  Initializing Local Diffusers pipeline on {self.device}...")
            try:
                # Use a lightweight model or standard SD 1.5
                model_id = "runwayml/stable-diffusion-v1-5"
                self.pipeline = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float32)
                self.pipeline.to(self.device)
                self.pipeline.enable_attention_slicing()
            except Exception as e:
                print(f"❌ Failed to load local model: {e}")
        else:
            print("⚠️  Diffusers/Torch not installed. Local generation unavailable.")

    def generate(self, prompt, output_path, dry_run=False):
        if dry_run:
            print(f"🧪 [DRY RUN] Would generate image for prompt: {prompt}")
            return True

        if self.api_url:
            return self._generate_remote(prompt, output_path)
        elif self.pipeline:
            return self._generate_local(prompt, output_path)
        else:
            print("❌ No image generation backend available (No API URL and No Local Libs).")
            return False

    def _generate_remote(self, prompt, output_path):
        print(f"🌐 Sending to Remote SD API: {self.api_url}")
        # Assumes Automatic1111 Text2Img API format
        payload = {
            "prompt": prompt,
            "steps": 20,
            "width": 512,
            "height": 512,
            "sampler_name": "Euler a"
        }
        try:
            resp = requests.post(f"{self.api_url}/sdapi/v1/txt2img", json=payload, timeout=120)
            resp.raise_for_status()
            r = resp.json()
            image_b64 = r['images'][0]

            import base64
            with open(output_path, "wb") as f:
                f.write(base64.b64decode(image_b64))
            print(f"✅ Image saved to {output_path}")
            return True
        except Exception as e:
            print(f"❌ Remote Generation Failed: {e}")
            return False

    def _generate_local(self, prompt, output_path):
        print(f"🖥️  Generating locally on {self.device}...")
        try:
            image = self.pipeline(prompt, num_inference_steps=25).images[0]
            image.save(output_path)
            print(f"✅ Image saved to {output_path}")
            return True
        except Exception as e:
            print(f"❌ Local Generation Failed: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description="Automated Chapter Art Generator")
    parser.add_argument('--chapter', required=True, help="Path to chapter markdown file")
    parser.add_argument('--style', default="cyberpunk noir, dark atmosphere, cinematic lighting, 8k", help="Art style")
    parser.add_argument('--ollama-model', default="tinyllama", help="Ollama model to use")
    parser.add_argument('--dry-run', action='store_true', help="Skip image generation")

    args = parser.parse_args()

    # Paths
    project_root = os.getcwd()
    char_file = os.path.join(project_root, "docs/personagens.md")

    # 1. Load Database
    db = CharacterDatabase(char_file)

    # 2. Load Chapter
    chapter_path = args.chapter
    if not os.path.exists(chapter_path):
        # Try finding it in docs/public or docs
        if os.path.exists(os.path.join("docs/public", chapter_path)):
            chapter_path = os.path.join("docs/public", chapter_path)
        elif os.path.exists(os.path.join("docs", chapter_path)):
            chapter_path = os.path.join("docs", chapter_path)

    print(f"📖 Reading chapter: {chapter_path}")
    chapter = ChapterContext(chapter_path)

    # 3. Analyze Text
    active_chars = db.find_characters_in_text(chapter.body)
    names = [c['name'] for c in active_chars]
    print(f"👥 Characters detected: {names}")

    # 4. Generate Prompt
    ollama = OllamaClient(model=args.ollama_model)

    # Check if we can prompt
    if not ollama.check_connection():
        print(f"⚠️  Cannot connect to Ollama at {ollama.host}. Skipping prompt generation.")
        # Fallback prompt
        prompt = f"{args.style}, scene from chapter. " + ", ".join([f"{c['name']} ({c['description'][:50]}...)" for c in active_chars])
    else:
        prompt = ollama.generate_prompt(chapter.body, active_chars, args.style)

    if not prompt:
        print("❌ Failed to generate prompt.")
        sys.exit(1)

    print(f"\n🎨 Generated Prompt:\n{prompt}\n")

    # 5. Generate Image
    # Determine output path based on chapter filename
    base_name = os.path.basename(chapter_path).replace('.md', '.jpg').replace('-', '_')
    output_path = os.path.join("docs/public", base_name)

    generator = ImageGenerator()
    success = generator.generate(prompt, output_path, dry_run=args.dry_run)

    # 6. Update Frontmatter
    if success and not args.dry_run:
        chapter.update_frontmatter(f"/{base_name}")

if __name__ == "__main__":
    main()

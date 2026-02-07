import os
import re
import argparse
import sys
import requests
import io
import time
from PIL import Image

# Try to import torch/diffusers, but don't fail immediately if missing (for checking help etc)
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
            print(f"Error: Character file not found at {self.filepath}")
            return

        with open(self.filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        sections = re.split(r'\n## ', content)

        for section in sections:
            if not section.strip() or section.startswith('# '):
                continue

            lines = section.split('\n')
            name_line = lines[0].strip()
            name_clean = re.sub(r'\s*\[.*?\]', '', name_line).strip()

            image_match = re.search(r'!\[.*?\]\((.*?)\)', section)
            image_path = image_match.group(1) if image_match else None

            description = []
            for line in lines:
                if any(key in line for key in ["Porte Físico:", "Vestuário:", "Marcas Distintivas:", "Cabelo:", "Olhos:"]):
                    description.append(line.replace('*', '').strip())

            full_desc = " ".join(description)

            aliases = set()
            aliases.add(name_clean)
            nickname_match = re.search(r'"(.*?)"', name_clean)
            if nickname_match:
                aliases.add(nickname_match.group(1))

            parts = name_clean.split()
            if parts:
                if len(parts[0]) > 2:
                    aliases.add(parts[0])

            self.characters[name_clean] = {
                "name": name_clean,
                "aliases": list(aliases),
                "image": image_path,
                "description": full_desc,
                "raw_section": section
            }

    def find_characters_in_text(self, text):
        found = []
        text_lower = text.lower()

        # Build map and pattern
        alias_map = {}
        all_aliases = []
        for char_data in self.characters.values():
            for alias in char_data["aliases"]:
                lower_alias = alias.lower()
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
    def __init__(self, chapter_num):
        self.chapter_num = chapter_num
        self.filepath = f"docs/capitulo-{chapter_num}.md"
        self.content = ""
        self.frontmatter = ""
        self.body = ""
        self.load()

    def load(self):
        if not os.path.exists(self.filepath):
            print(f"Error: Chapter file not found at {self.filepath}")
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
        if not image_path.startswith('/'):
            public_path = '/' + os.path.basename(image_path)
        else:
            public_path = image_path

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
        print(f"✅ Updated {self.filepath} with image: {public_path}")

class OllamaClient:
    def __init__(self, model="llama2"):
        self.model = model
        self.api_url = "http://localhost:11434/api/generate"
        print(f"🦙 Initializing Ollama Client (Model: {self.model})...")

    def extract_scene(self, chapter_text, active_characters):
        char_names = ", ".join([c['name'] for c in active_characters])

        prompt = (
            f"You are an expert visual director. Your task is to identify the most visually striking scene from the text and write a detailed image generation prompt for it.\n\n"
            f"Analyze this chapter snippet.\n"
            f"Characters present: {char_names}\n\n"
            f"CHAPTER TEXT:\n{chapter_text[:1500]}...\n\n"
            f"Write a single paragraph describing the visual scene for an image generator. Focus on lighting, atmosphere, and action. Do not include dialogue."
        )

        try:
            response = requests.post(self.api_url, json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            })
            response.raise_for_status()
            result = response.json()
            return result.get("response", "").strip()
        except Exception as e:
            print(f"⚠️ Ollama Text Extraction Failed: {e}")
            print("Make sure Ollama is running (ollama serve) and the model is pulled.")
            return "Dark dystopian city scene, high contrast, cinematic lighting."

class LocalDiffusionClient:
    def __init__(self):
        print("🖥️ Initializing Local Stable Diffusion (Diffusers)...")
        if torch is None or StableDiffusionPipeline is None:
            raise ImportError("Missing dependencies. Please run: pip install torch diffusers transformers accelerate")

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"⚙️ Running on device: {self.device}")

        # Use a small/compatible model. "runwayml/stable-diffusion-v1-5" is standard and widely compatible.
        self.model_id = "runwayml/stable-diffusion-v1-5"

        print(f"... Loading model {self.model_id}...")
        try:
            self.pipe = StableDiffusionPipeline.from_pretrained(self.model_id, torch_dtype=torch.float32) # float32 for CPU safety
            self.pipe = self.pipe.to(self.device)
            # Enable attention slicing to save memory
            self.pipe.enable_attention_slicing()
        except Exception as e:
             raise RuntimeError(f"Failed to load Stable Diffusion model: {e}")

    def generate_art(self, prompt, output_path):
        print("\n" + "="*50)
        print("🖥️ LOCAL GENERATION REQUEST")
        print("="*50)
        print(f"**PROMPT:**\n{prompt}\n")

        try:
            print(f"... Generating image (this may take time on CPU)...")
            # Low steps for CI speed, but enough for "proof"
            image = self.pipe(prompt, num_inference_steps=20).images[0]

            image.save(output_path)
            print(f"✅ IMAGE GENERATED: {output_path}")
            return output_path

        except Exception as e:
            print(f"❌ Generation Failed: {e}")
            return None

def process_chapter(chapter_num, text_engine, image_engine, db, project_root, style):
    print(f"\n📂 PROCESSING CHAPTER {chapter_num} (LOCAL MODE)...")
    try:
        chapter = ChapterContext(chapter_num)
        active_chars = db.find_characters_in_text(chapter.body)
        char_names = [c['name'] for c in active_chars]
        print(f"Detected Characters: {', '.join(char_names)}")

        # Extract Scene using Text Engine (Ollama)
        scene_prompt = text_engine.extract_scene(chapter.body, active_chars)

        # Build Final Prompt for Image Engine
        final_prompt = f"{scene_prompt}, {style}, 8k resolution, cinematic lighting, masterpiece"

        if active_chars:
            main_char = active_chars[0]
            desc_snippet = active_chars[0]['description'][:100]
            final_prompt += f", featuring character: {main_char['name']} ({desc_snippet})"

        # Define Output
        output_filename = f"capitulo_{chapter_num}.jpg"
        output_path = os.path.join(project_root, "docs/public", output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Generate using Image Engine (Local SD)
        result_path = image_engine.generate_art(final_prompt, output_path)

        if result_path:
            chapter.update_frontmatter(f"/{output_filename}")
            return True
        return False

    except Exception as e:
        print(f"❌ Error processing Chapter {chapter_num}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Generate Art (Fully Local Mode)")
    parser.add_argument('chapters', type=str, help="Chapter number")
    parser.add_argument('--style', type=str, help="Style modifier", default="cyberpunk, noir")
    parser.add_argument('--ollama-model', type=str, default="llama2", help="Model to use with Ollama")
    args = parser.parse_args()

    project_root = os.getcwd()
    char_file = os.path.join(project_root, "docs/personagens.md")

    try:
        # Initialize Engines
        text_engine = OllamaClient(model=args.ollama_model)
        image_engine = LocalDiffusionClient()

        db = CharacterDatabase(char_file)

        process_chapter(int(args.chapters), text_engine, image_engine, db, project_root, args.style)

    except Exception as e:
        print(f"❌ Fatal Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

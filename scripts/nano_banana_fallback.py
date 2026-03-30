import os
import re
import argparse
import sys
import requests
import io
import time
from PIL import Image

from scripts.character_match import CharacterMatcherMixin

class CharacterDatabase(CharacterMatcherMixin):
    def __init__(self, filepath):
        self.filepath = filepath
        self.characters = {}
        self._alias_map = {}
        self._alias_pattern = None
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

        self._alias_map = self._build_alias_map()
        self._alias_pattern = self._build_alias_pattern()


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

    def check_connection(self, max_retries=3, retry_delay=2):
        """Check if Ollama is accessible with retries"""
        host = "http://localhost:11434"
        for attempt in range(max_retries):
            try:
                response = requests.get(host, timeout=5)
                if response.status_code == 200:
                    print(f"✅ Successfully connected to Ollama at {host}")
                    return True
                else:
                    raise Exception(f"HTTP {response.status_code}")
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"⚠️ Connection attempt {attempt + 1} failed, retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                else:
                    print(f"❌ Failed to connect to Ollama after {max_retries} attempts: {e}")
        return False

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
            # Increase timeout to 5 minutes for larger models and slower systems
            response = requests.post(self.api_url, json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }, timeout=300)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "").strip()
        except requests.exceptions.Timeout:
            print(f"⚠️ Ollama request timed out after 300 seconds")
            print("Using fallback prompt instead.")
            return "Dark dystopian city scene, high contrast, cinematic lighting."
        except Exception as e:
            print(f"⚠️ Ollama Text Extraction Failed: {e}")
            print("Make sure Ollama is running (ollama serve) and the model is pulled.")
            return "Dark dystopian city scene, high contrast, cinematic lighting."

class HuggingFaceClient:
    def __init__(self):
        print("🤗 Initializing Open Source Fallback (Hugging Face Inference API)...")
        self.api_key = os.environ.get("HF_API_KEY")
        if not self.api_key:
            raise ValueError("HF_API_KEY not found. Please set your Hugging Face Access Token.")

        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        # Model for Text Generation (Scene Extraction)
        self.text_model_url = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"
        # Model for Image Generation
        self.image_model_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"

    def query_text(self, payload):
        response = requests.post(self.text_model_url, headers=self.headers, json=payload)
        return response.json()

    def query_image(self, payload):
        response = requests.post(self.image_model_url, headers=self.headers, json=payload)
        return response.content

    def extract_scene(self, chapter_text, active_characters):
        char_names = ", ".join([c['name'] for c in active_characters])

        prompt = (
            f"<|system|>\n"
            f"You are an expert visual director. Your task is to identify the most visually striking scene from the text and write a detailed image generation prompt for it.\n"
            f"</s>\n"
            f"<|user|>\n"
            f"Analyze this chapter snippet.\n"
            f"Characters present: {char_names}\n\n"
            f"CHAPTER TEXT:\n{chapter_text[:1500]}...\n\n"
            f"Write a single paragraph describing the visual scene for an image generator. Focus on lighting, atmosphere, and action. Do not include dialogue."
            f"</s>\n"
            f"<|assistant|>\n"
        )

        try:
            output = self.query_text({
                "inputs": prompt,
                "parameters": {"max_new_tokens": 256, "return_full_text": False}
            })

            if isinstance(output, list) and 'generated_text' in output[0]:
                return output[0]['generated_text'].strip()
            elif isinstance(output, dict) and 'error' in output:
                 print(f"⚠️ HF Text API Error: {output['error']}")
                 return "Cyberpunk city street at dawn, rain, neon lights reflecting on wet asphalt, characters standing in shadows."
            else:
                return str(output)

        except Exception as e:
            print(f"⚠️ Text Extraction Failed: {e}")
            return "Dark dystopian city scene, high contrast, cinematic lighting."

    def generate_art(self, prompt, output_path):
        print("\n" + "="*50)
        print("🤗 HUGGING FACE GENERATION REQUEST")
        print("="*50)
        print(f"**PROMPT:**\n{prompt}\n")

        try:
            print(f"... Generating with Stable Diffusion 2.1...")
            image_bytes = self.query_image({"inputs": prompt})

            try:
                image = Image.open(io.BytesIO(image_bytes))
                image.save(output_path)
                print(f"✅ IMAGE GENERATED: {output_path}")
                return output_path
            except Exception as e:
                 # Check if it's a JSON error response
                 try:
                     import json
                     error_json = json.loads(image_bytes)
                     print(f"❌ HF Image API Error: {error_json.get('error', 'Unknown Error')}")
                 except:
                     print(f"❌ Failed to parse image response: {e}")
                 return None

        except Exception as e:
            print(f"❌ Generation Failed: {e}")
            return None

def process_chapter(chapter_num, text_engine, image_engine, db, project_root, style):
    print(f"\n📂 PROCESSING CHAPTER {chapter_num} (FALLBACK MODE)...")
    try:
        chapter = ChapterContext(chapter_num)
        active_chars = db.find_characters_in_text(chapter.body)
        char_names = [c['name'] for c in active_chars]
        print(f"Detected Characters: {', '.join(char_names)}")

        # Extract Scene using Text Engine
        scene_prompt = text_engine.extract_scene(chapter.body, active_chars)

        # Build Final Prompt for Image Engine
        final_prompt = f"{scene_prompt}, {style}, 8k resolution, cinematic lighting, masterpiece"

        # Add minimal character visual cues since SD doesn't support image input easily via simple API
        if active_chars:
            main_char = active_chars[0]
            # Add a brief text description from the DB to help
            desc_snippet = active_chars[0]['description'][:100]
            final_prompt += f", featuring character: {main_char['name']} ({desc_snippet})"

        # Define Output
        output_filename = f"capitulo_{chapter_num}.jpg"
        output_path = os.path.join(project_root, "docs/public", output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Generate using Image Engine (always HF for now)
        result_path = image_engine.generate_art(final_prompt, output_path)

        if result_path:
            chapter.update_frontmatter(f"/{output_filename}")
            return True
        return False

    except Exception as e:
        print(f"❌ Error processing Chapter {chapter_num}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Generate Art (Fallback Mode)")
    parser.add_argument('chapters', type=str, help="Chapter number")
    parser.add_argument('--style', type=str, help="Style modifier", default="cyberpunk, noir")
    parser.add_argument('--ollama', action='store_true', help="Use Ollama (local) for text analysis instead of HF")
    parser.add_argument('--ollama-model', type=str, default="llama2", help="Model to use with Ollama")
    args = parser.parse_args()

    project_root = os.getcwd()
    char_file = os.path.join(project_root, "docs/personagens.md")

    try:
        # Image Engine is always Hugging Face for now in fallback script
        image_engine = HuggingFaceClient()

        # Text Engine depends on flag
        if args.ollama:
            text_engine = OllamaClient(model=args.ollama_model)
        else:
            text_engine = image_engine # HF Client handles both

        db = CharacterDatabase(char_file)

        process_chapter(int(args.chapters), text_engine, image_engine, db, project_root, args.style)

    except ValueError as ve:
        print(f"ℹ️ CONFIGURATION NEEDED: {ve}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Fatal Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

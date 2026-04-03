import os
import re
import argparse
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# Add root project dir to pythonpath to allow relative imports from scripts
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from scripts.art_gen.character_db import CharacterDatabase

# Compile regex at module level for performance
IMAGE_FRONTMATTER_RE = re.compile(r'image:.*')

class ChapterContext:
    def __init__(self, chapter_num):
        self.chapter_num = chapter_num
        self.filepath = f"docs/capitulo-{chapter_num}.md"
        self._content = None
        self._frontmatter = None
        self._body = None

    def _load(self):
        if not os.path.exists(self.filepath):
            print(f"Error: Chapter file not found at {self.filepath}")
            sys.exit(1)

        with open(self.filepath, 'r', encoding='utf-8') as f:
            self._content = f.read()

        if self._content.startswith('---'):
            parts = self._content.split('---', 2)
            if len(parts) >= 3:
                self._frontmatter = parts[1]
                self._body = parts[2]
            else:
                self._body = self._content
                self._frontmatter = ""
        else:
            self._body = self._content
            self._frontmatter = ""

    @property
    def content(self):
        if self._content is None:
            self._load()
        return self._content

    @property
    def frontmatter(self):
        if self._frontmatter is None:
            self._load()
        return self._frontmatter

    @frontmatter.setter
    def frontmatter(self, value):
        self._frontmatter = value

    @property
    def body(self):
        if self._body is None:
            self._load()
        return self._body

    def update_frontmatter(self, image_path):
        if not image_path.startswith('/'):
            public_path = '/' + os.path.basename(image_path)
        else:
            public_path = image_path

        if self.frontmatter:
            if 'image:' in self.frontmatter:
                self.frontmatter = IMAGE_FRONTMATTER_RE.sub(f'image: {public_path}', self.frontmatter)
            else:
                self.frontmatter = self.frontmatter.rstrip() + f'\nimage: {public_path}\n'
        else:
            self.frontmatter = f'\nimage: {public_path}\n'

        new_content = f'---{self.frontmatter}---{self.body}'

        with open(self.filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ Updated {self.filepath} with image: {public_path}")

class CostCalculator:
    def __init__(self):
        # Pricing constants (USD) - Gemini Flash Tier (Approximate)
        self.PRICE_INPUT_1M = 0.075
        self.PRICE_OUTPUT_1M = 0.30
        self.PRICE_IMAGE_GEN = 0.040 # Imagen 3 Fast / Flash Image approx
        self.USD_TO_BRL = 6.00
        
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_images = 0

    def add_text_usage(self, usage):
        if usage:
            self.total_input_tokens += usage.prompt_token_count
            self.total_output_tokens += usage.candidates_token_count

    def add_image_gen(self, count=1):
        self.total_images += count

    def print_summary(self):
        cost_input = (self.total_input_tokens / 1_000_000) * self.PRICE_INPUT_1M
        cost_output = (self.total_output_tokens / 1_000_000) * self.PRICE_OUTPUT_1M
        cost_images = self.total_images * self.PRICE_IMAGE_GEN
        
        total_usd = cost_input + cost_output + cost_images
        total_brl = total_usd * self.USD_TO_BRL
        
        print("\n" + "-"*30)
        print("💰 ESTIMATIVA DE CUSTOS")
        print("-"*30)
        print(f"🔤 Text Input ({self.total_input_tokens} toks): ${cost_input:.6f}")
        print(f"💬 Text Output ({self.total_output_tokens} toks): ${cost_output:.6f}")
        print(f"🎨 Images ({self.total_images}): ${cost_images:.4f}")
        print(f"💵 Total (USD): ${total_usd:.4f}")
        print(f"🇧🇷 Total (BRL): R$ {total_brl:.4f}")
        print("-"*30 + "\n")

class NanoBanana:
    def __init__(self):
        from google import genai
        print("🍌 Initializing Nano Banana Core (Gemini 2.5 Powered - via google.genai)...")
        
        # Load keys from env or default
        key_text = os.environ.get('NANO_BANANA_API_KEY_TEXT')
        key_image = os.environ.get('NANO_BANANA_API_KEY_IMAGE')
        
        # Fallback to generic key
        if not key_text:
            key_text = os.environ.get('NANO_BANANA_API_KEY')
        if not key_image:
            key_image = os.environ.get('NANO_BANANA_API_KEY')

        if not key_text:
            raise ValueError("Text API Key not found.")
        if not key_image:
            raise ValueError("Image API Key not found.")
        
        # Initialize separate clients
        self.client_text = genai.Client(api_key=key_text)
        self.client_image = genai.Client(api_key=key_image)
        
        # Models
        self.text_model_name = os.environ.get('NANO_BANANA_TEXT_MODEL', 'gemini-2.5-flash')
        self.generation_model_name = 'gemini-2.5-flash-image' 
        
        # Cost Tracker
        self.costs = CostCalculator()

    def get_real_image_path(self, char_data, project_root):
        image_rel_path = char_data.get('image')
        if not image_rel_path:
            return None
            
        if image_rel_path.startswith('/'):
            real_path = os.path.join(project_root, 'docs/public', image_rel_path.lstrip('/'))
        else:
             real_path = os.path.join(project_root, 'docs', image_rel_path)
             
        if os.path.exists(real_path):
            return real_path
        return None

    def extract_scene(self, chapter_text, active_characters):
        """Uses Gemini Text to pick a scene and prompt"""
        char_names = ", ".join([c['name'] for c in active_characters]) or "sem personagens nomeados"
        character_bible = "\n".join(
            f"- {c['name']}: {c['description'][:240]}" for c in active_characters[:3]
        )
        
        prompt = (
            "You are the art director of a cyberpunk noir bestseller cover pipeline.\n"
            "Produce a prompt that feels close to Nano Banana quality: cinematic, emotional, consistent with canon.\n\n"
            f"CHARACTERS IN SCENE: {char_names}\n"
            f"CANON VISUAL TRAITS (mandatory):\n{character_bible}\n\n"
            "TASK:\n"
            "1. Select ONE scene with the highest dramatic tension and visual storytelling value.\n"
            "2. Keep character appearance coherent with canon traits above.\n"
            "3. Write a single production-ready prompt in English, max 170 words.\n"
            "4. Include: camera framing, lens feeling, lighting design, weather, props, mood, action beat.\n"
            "5. No dialogue, no bullet list, no meta commentary, no NSFW.\n"
            "6. End with style tags: 'ultra cinematic, noir cyberpunk, volumetric rain, film grain, masterpiece'.\n\n"
            f"CHAPTER TEXT:\n{chapter_text[:1400]}..."
        )
        
        response = self.client_text.models.generate_content(
            model=self.text_model_name,
            contents=prompt
        )
        # Track usage
        if response.usage_metadata:
            self.costs.add_text_usage(response.usage_metadata)
            
        return response.text

    def generate_art(self, prompt, ref_image_paths, output_path):
        from PIL import Image
        import io
        print("\n" + "="*50)
        print("🍌 NANO BANANA GENERATION REQUEST 🍌")
        print("="*50)
        print(f"**PROMPT:**\n{prompt}\n")
        
        contents = [prompt]
        if ref_image_paths and isinstance(ref_image_paths, list):
            for ref_path in ref_image_paths:
                print(f"**REFERENCE IMAGE:** {ref_path}")
                try:
                    reference_image = Image.open(ref_path)
                    contents.append(reference_image)
                except Exception as e:
                    print(f"⚠️ Failed to load reference image {ref_path}: {e}")
        elif ref_image_paths:
            # Fallback for single path string
            print(f"**REFERENCE IMAGE:** {ref_image_paths}")
            try:
                reference_image = Image.open(ref_image_paths)
                contents.append(reference_image)
            except Exception as e:
                print(f"⚠️ Failed to load reference image {ref_image_paths}: {e}")

        try:
            print(f"... Generating with {self.generation_model_name}...")
            response = self.client_image.models.generate_content(
                model=self.generation_model_name,
                contents=contents
            )
            
            # Track Usage (Text part if available, plus image count)
            if response.usage_metadata:
                self.costs.add_text_usage(response.usage_metadata)
            
            generated = False
            if response.parts:
                for part in response.parts:
                    if part.inline_data:
                        print("✅ Image data received.")
                        # The SDK part.as_image() is safest if available as per user snippet
                        try:
                            img = part.as_image()
                        except:
                            # Fallback if as_image is not there but bytes are
                            img = Image.open(io.BytesIO(part.inline_data.data))
                            
                        img.save(output_path)
                        print(f"✅ IMAGE GENERATED: {output_path}")
                        self.costs.add_image_gen(1) # Track successful image
                        generated = True
                        return output_path
                    elif part.text:
                        print(f"ℹ️ Model Text Output: {part.text}")
            
            if not generated:
                print("❌ No image generated in response.")
                return None
                
        except Exception as e:
            print(f"❌ Generation Failed: {e}")
            return None

def process_chapter(chapter_num, engine, db, project_root, style):
    print(f"\n📂 PROCESSING CHAPTER {chapter_num}...")
    try:
        chapter = ChapterContext(chapter_num)
        
        print(f"Reading Chapter {chapter_num}...")
        active_chars = db.find_characters_in_text(chapter.body)
        
        char_names = [c['name'] for c in active_chars]
        print(f"Detected Characters: {', '.join(char_names)}")

        # Extract Scene
        print("🧠 Analyzing text for scene selection...")
        scene_prompt = engine.extract_scene(chapter.body, active_chars)
        
        final_prompt = scene_prompt
        if style:
            final_prompt += f"\nSTYLE: {style}"
        else:
            final_prompt += "\nSTYLE: Digital Art, Cinematic Lighting."

        # Collect Character Images
        ref_image_paths = []
        if active_chars:
            for char_data in active_chars:
                ref_path = engine.get_real_image_path(char_data, project_root)
                if ref_path:
                    ref_image_paths.append(ref_path)
                    print(f"⭐️ Found Reference Image for: {char_data['name']}")

            if ref_image_paths:
                final_prompt += f"\n(Generate the image featuring the characters from the provided reference images in the described scene.)"
        
        # Define Output
        output_filename = f"capitulo_{chapter_num}.jpg"
        output_path = os.path.join(project_root, "docs/public", output_filename)
        
        # Ensure dir exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Generate
        result_path = engine.generate_art(final_prompt, ref_image_paths, output_path)
        
        if result_path:
            # Update Chapter only if success
            chapter.update_frontmatter(f"/{output_filename}")
            return True
        else:
            print(f"❌ Skipping frontmatter update for Chapter {chapter_num} due to generation failure.")
            return False
        
    except Exception as e:
        print(f"❌ Error processing Chapter {chapter_num}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Generate Art for a Chapter using Nano Banana")
    parser.add_argument('chapters', type=str, help="Chapter number (e.g., '102') or range (e.g., '7-104')")
    parser.add_argument('--style', type=str, help="Optional style/prompt modifier", default="")
    parser.add_argument("--max-workers", type=int, default=4, help="Maximum number of concurrent workers")
    args = parser.parse_args()

    project_root = os.getcwd()
    char_file = os.path.join(project_root, "docs/personagens.md")

    # Parse Range
    chapter_list = []
    # Remove spaces just in case
    clean_args = args.chapters.replace(' ', '')
    
    if ',' in clean_args:
        parts = clean_args.split(',')
        for part in parts:
            if '-' in part:
                start, end = map(int, part.split('-'))
                chapter_list.extend(range(start, end + 1))
            else:
                chapter_list.append(int(part))
    elif '-' in clean_args:
        start, end = map(int, clean_args.split('-'))
        chapter_list = list(range(start, end + 1))
    else:
        chapter_list = [int(clean_args)]
    
    # Sort and unique
    chapter_list = sorted(list(set(chapter_list)))

    try:
        engine = NanoBanana()
        db = CharacterDatabase(char_file)
        
        def worker(chapter_num):
            return process_chapter(chapter_num, engine, db, project_root, args.style)

        with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
            futures = {executor.submit(worker, chapter_num): chapter_num for chapter_num in chapter_list}
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    chapter_num = futures[future]
                    print(f"❌ Error processing chapter {chapter_num}: {e}")
            
        # Print Final Costs
        print("\n" + "="*50)
        print("🏁 BATCH COMPLETE")
        engine.costs.print_summary()
        
    except Exception as e:
        print(f"❌ Fatal Global Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

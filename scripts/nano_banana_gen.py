import os
import re
import argparse
import sys
from google import genai
from PIL import Image
import io

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
            
            # Resolve relative image path to absolute if possible
            if image_path:
                if image_path.startswith('/'):
                    # Assuming / refers to docs/public or root
                     # Heuristic: try finding it in docs/public relative to project root
                    pass 
                
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
        for char_data in self.characters.values():
            for alias in char_data["aliases"]:
                escaped_alias = re.escape(alias)
                if re.search(r'\b' + escaped_alias + r'\b', text_lower, re.IGNORECASE):
                    found.append(char_data)
                    break
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
        print("🍌 Initializing Nano Banana Core (Gemini 2.5 Powered - via google.genai)...")
        
        # Load keys from env or default
        key_text = os.environ.get('NANO_BANANA_API_KEY_TEXT')
        key_image = os.environ.get('NANO_BANANA_API_KEY_IMAGE')
        
        if not key_text:
            raise ValueError("Text API Key not found.")
        if not key_image:
            raise ValueError("Image API Key not found.")
        
        # Initialize separate clients
        self.client_text = genai.Client(api_key=key_text)
        self.client_image = genai.Client(api_key=key_image)
        
        # Models
        self.text_model_name = 'gemini-2.5-flash'
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
        char_names = ", ".join([c['name'] for c in active_characters])
        
        prompt = (
            f"Analyze the following book chapter text.\n"
            f"Characters present: {char_names}\n\n"
            f"TASK:\n"
            f"1. Select the most visually striking scene.\n"
            f"2. Write a detailed image generation prompt for this scene. "
            f"Describe the setting, lighting, action, and atmosphere. "
            f"Do NOT describe the main character's face in detail (we have their photo), but DO describe their pose and expression. "
            f"Focus on the ACTION and ENVIRONMENT.\n\n"
            f"CHAPTER TEXT:\n{chapter_text[:1000]}..."
        )
        
        response = self.client_text.models.generate_content(
            model=self.text_model_name,
            contents=prompt
        )
        # Track usage
        if response.usage_metadata:
            self.costs.add_text_usage(response.usage_metadata)
            
        return response.text

    def generate_art(self, prompt, ref_image_path, output_path):
        print("\n" + "="*50)
        print("🍌 NANO BANANA GENERATION REQUEST 🍌")
        print("="*50)
        print(f"**PROMPT:**\n{prompt}\n")
        
        contents = [prompt]
        if ref_image_path:
            print(f"**REFERENCE IMAGE:** {ref_image_path}")
            try:
                reference_image = Image.open(ref_image_path)
                contents.append(reference_image)
            except Exception as e:
                print(f"⚠️ Failed to load reference image: {e}")

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

        # Find Main Character Image
        ref_image_path = None
        if active_chars:
            main_char = active_chars[0]
            ref_image_path = engine.get_real_image_path(main_char, project_root)
            if ref_image_path:
                print(f"⭐️ Using Reference Image for: {main_char['name']}")
                final_prompt += f"\n(Generate the image featuring the character from the provided reference image in the described scene.)"
        
        # Define Output
        output_filename = f"capitulo_{chapter_num}.jpg"
        output_path = os.path.join(project_root, "docs/public", output_filename)
        
        # Ensure dir exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Generate
        result_path = engine.generate_art(final_prompt, ref_image_path, output_path)
        
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
        
        for chapter_num in chapter_list:
            process_chapter(chapter_num, engine, db, project_root, args.style)
            
        # Print Final Costs
        print("\n" + "="*50)
        print("🏁 BATCH COMPLETE")
        engine.costs.print_summary()
        
    except Exception as e:
        print(f"❌ Fatal Global Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

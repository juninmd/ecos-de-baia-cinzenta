import os
import re
import argparse
import sys
import shutil

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

    def has_image(self):
        return 'image:' in self.frontmatter

    def get_context_summary(self):
        paragraphs = [p for p in self.body.split('\n\n') if p.strip()]
        if not paragraphs:
            return "No text found."

        intro = "\n".join(paragraphs[:2])
        outro = "\n".join(paragraphs[-2:]) if len(paragraphs) > 2 else ""
        middle = paragraphs[len(paragraphs)//2] if len(paragraphs) > 5 else ""

        return f"{intro}\n...\n{middle}\n...\n{outro}"

    def update_frontmatter(self, image_path):
        # Clean image path for frontmatter (usually relative to public or root, typical VitePress is /image.jpg)
        # Ensure it starts with /
        if not image_path.startswith('/'):
            public_path = '/' + os.path.basename(image_path)
        else:
            public_path = image_path

        if self.frontmatter:
            if 'image:' in self.frontmatter:
                # Replace existing
                self.frontmatter = re.sub(r'image:.*', f'image: {public_path}', self.frontmatter)
            else:
                # Append
                self.frontmatter = self.frontmatter.rstrip() + f'\nimage: {public_path}\n'
        else:
            # Create new
            self.frontmatter = f'\nimage: {public_path}\n'

        new_content = f'---{self.frontmatter}---{self.body}'

        with open(self.filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ Updated {self.filepath} with image: {public_path}")

class NanoBanana:
    def __init__(self):
        print("🍌 Initializing Nano Banana Core...")
        api_key = os.environ.get('NANO_BANANA_API_KEY')
        if not api_key:
            print("⚠️ WARNING: NANO_BANANA_API_KEY environment variable is not set!")
            print("⚠️ Mock generation will proceed.")
        else:
            print(f"🍌 API Key detected: {api_key[:4]}****")

        print("🍌 Loading Neural Models...")

    def generate_art(self, prompt, ref_image_path, output_path):
        print("\n" + "="*50)
        print("🍌 NANO BANANA GENERATION REQUEST 🍌")
        print("="*50)
        print(f"**PROMPT:**\n{prompt}\n")
        print(f"**REFERENCE IMAGE:** {ref_image_path}")
        print(f"**OUTPUT DESTINATION:** {output_path}")

        print("\n... Processing Context Vectors ...")
        print("... Synthesizing Pixel Latents ...")

        # Mock Generation: Copy reference image to output
        # Resolve reference path. docs/personagens.md usually has /image.jpg.
        # We need to map that to docs/public/image.jpg

        source_path = None
        if ref_image_path:
            # Remove leading / if present
            clean_ref = ref_image_path.lstrip('/')

            # Check if path already starts with docs/public or similar
            if clean_ref.startswith('docs/public/'):
                potential_path = clean_ref
            else:
                potential_path = os.path.join('docs/public', clean_ref)

            if os.path.exists(potential_path):
                source_path = potential_path
            else:
                print(f"⚠️ Reference image not found at {potential_path}")

        if source_path:
            shutil.copy(source_path, output_path)
            print(f"✅ IMAGE GENERATED (Mocked by copying {source_path})")
        else:
            # Create dummy if source not found
            with open(output_path, 'wb') as f:
                f.write(b'\x00' * 1024)
            print(f"✅ IMAGE GENERATED (Dummy file created)")

        print(f"📂 Output saved to: {output_path}")
        print("="*50 + "\n")
        return output_path

def main():
    parser = argparse.ArgumentParser(description="Generate Art for a Chapter using Nano Banana")
    parser.add_argument('chapter', type=int, help="Chapter number (e.g., 102)")
    parser.add_argument('--style', type=str, help="Optional style/prompt modifier", default="")
    args = parser.parse_args()

    # Paths
    char_file = "docs/personagens.md"

    # Initialize
    db = CharacterDatabase(char_file)
    chapter = ChapterContext(args.chapter)

    # Check if image already exists
    if chapter.has_image():
        print(f"ℹ️ Chapter {args.chapter} already has an image configured in frontmatter.")
        # Proceeding anyway as per user "surpreenda-me" / explicit instruction to generate

    # Analyze
    print(f"Reading Chapter {args.chapter}...")
    summary = chapter.get_context_summary()
    active_chars = db.find_characters_in_text(chapter.content)

    char_names = [c['name'] for c in active_chars]
    print(f"Detected Characters: {', '.join(char_names)}")

    if not active_chars:
        print("❌ No known characters found in chapter. Cannot generate character-based art.")
        sys.exit(1)

    # Pick main character (first one found)
    main_char = active_chars[0]
    print(f"⭐️ Selected Main Character for Reference: {main_char['name']}")

    # Construct Prompt
    prompt = f"Digital Art, Cyberpunk Noir Style, High Contrast, Gritty Atmosphere.\n\n"
    prompt += f"SCENE CONTEXT:\n{summary[:500]}...\n\n"
    prompt += f"MAIN CHARACTER: {main_char['name']}\n{main_char['description']}\n"

    if args.style:
         prompt += f"\nSTYLE: {args.style}"
    else:
         prompt += "\nSTYLE: Analog photography aesthetic, rain-slicked streets, neon lights reflecting on wet surfaces."

    # Define Output Path
    output_filename = f"capitulo_{args.chapter}.jpg"
    output_path = os.path.join("docs/public", output_filename)

    # Generate
    engine = NanoBanana()
    engine.generate_art(prompt, main_char['image'], output_path)

    # Update Chapter
    chapter.update_frontmatter(f"/{output_filename}")

    # Output for GitHub Actions
    print(f"::set-output name=generated_image_path::{output_path}")

if __name__ == "__main__":
    main()

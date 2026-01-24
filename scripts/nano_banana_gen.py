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

        # Split by character sections (Markdown header 2)
        # Using a lookahead to split but keep the delimiter or just iterating logic
        # Simple approach: Split by "\n## "
        sections = re.split(r'\n## ', content)

        for section in sections:
            if not section.strip() or section.startswith('# '): # Skip title or empty
                continue

            # Extract Name (first line usually)
            lines = section.split('\n')
            name_line = lines[0].strip()
            # Remove status tags like [STATUS: ...]
            name_clean = re.sub(r'\s*\[.*?\]', '', name_line).strip()

            # Extract Image
            image_match = re.search(r'!\[.*?\]\((.*?)\)', section)
            image_path = image_match.group(1) if image_match else None

            # Extract Description (Naively grab everything else or specific fields)
            # Let's try to grab "Porte Físico", "Vestuário", "Marcas Distintivas"
            description = []
            for line in lines:
                if any(key in line for key in ["Porte Físico:", "Vestuário:", "Marcas Distintivas:", "Cabelo:", "Olhos:"]):
                    description.append(line.replace('*', '').strip())

            full_desc = " ".join(description)

            # Generate aliases
            aliases = set()
            aliases.add(name_clean)
            # Handle nicknames in quotes e.g. Gabriel "Gabo" Moretti
            nickname_match = re.search(r'"(.*?)"', name_clean)
            if nickname_match:
                aliases.add(nickname_match.group(1))

            # First name
            parts = name_clean.split()
            if parts:
                # Avoid adding common articles or titles as aliases (e.g., "O", "A", "Dr.")
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
        # Sort characters by name length to match specific names first?
        # Actually, we check every character in the DB against the text.

        text_lower = text.lower()

        for char_data in self.characters.values():
            for alias in char_data["aliases"]:
                # Simple word boundary check to avoid partial matches
                # e.g. "Val" matching "Valor" -> Use regex \bVal\b
                escaped_alias = re.escape(alias)
                if re.search(r'\b' + escaped_alias + r'\b', text_lower, re.IGNORECASE):
                    found.append(char_data)
                    break # Found this character, move to next character
        return found

class ChapterContext:
    def __init__(self, chapter_num):
        self.chapter_num = chapter_num
        self.filepath = f"docs/capitulo-{chapter_num}.md"
        self.content = ""
        self.load()

    def load(self):
        if not os.path.exists(self.filepath):
            print(f"Error: Chapter file not found at {self.filepath}")
            sys.exit(1)

        with open(self.filepath, 'r', encoding='utf-8') as f:
            self.content = f.read()

    def get_context_summary(self):
        # Remove frontmatter
        body = re.sub(r'^---.*?---\n', '', self.content, flags=re.DOTALL)

        # Simple extraction: First 2 paragraphs + Last 2 paragraphs
        paragraphs = [p for p in body.split('\n\n') if p.strip()]

        if not paragraphs:
            return "No text found."

        intro = "\n".join(paragraphs[:2])
        outro = "\n".join(paragraphs[-2:]) if len(paragraphs) > 2 else ""

        # Find a middle paragraph with action
        middle = ""
        if len(paragraphs) > 5:
             # Just pick the middle one
             middle = paragraphs[len(paragraphs)//2]

        return f"{intro}\n...\n{middle}\n...\n{outro}"

class NanoBanana:
    def __init__(self):
        print("🍌 Initializing Nano Banana Core...")
        api_key = os.environ.get('NANO_BANANA_API_KEY')
        if not api_key:
            print("⚠️ WARNING: NANO_BANANA_API_KEY environment variable is not set!")
            print("⚠️ Mock generation will proceed, but remote endpoints are unreachable.")
        else:
            print(f"🍌 API Key detected: {api_key[:4]}****")

        print("🍌 Loading Neural Models...")
        print("🍌 Status: READY.")

    def generate_art(self, prompt, ref_images):
        print("\n" + "="*50)
        print("🍌 NANO BANANA GENERATION REQUEST 🍌")
        print("="*50)
        print(f"**PROMPT:**\n{prompt}\n")

        if ref_images:
            print("**REFERENCE IMAGES (ControlNet/Img2Img):**")
            for img in ref_images:
                print(f" - {img}")
        else:
            print("**NO REFERENCE IMAGES FOUND.** (Text-to-Image Mode)")

        print("\n... Processing Context Vectors ...")
        print("... Synthesizing Pixel Latents ...")
        print("... Refining Details (Cyber-Noir Filter) ...")

        # Mock Output - Actually creating a dummy file now for artifacts
        output_dir = "docs/public"
        output_path = f"{output_dir}/generated_art_mock.png"

        # Ensure directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Create a simple placeholder file
        with open(output_path, 'wb') as f:
            # Writing 1KB of null bytes as a dummy image
            f.write(b'\x00' * 1024)

        print(f"\n✅ IMAGE GENERATED SUCCESSFULLY!")
        print(f"📂 Output saved to: {output_path} (Mock)")
        print("="*50 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Generate Art for a Chapter using Nano Banana")
    parser.add_argument('chapter', type=int, help="Chapter number (e.g., 102)")
    args = parser.parse_args()

    # Paths
    char_file = "docs/personagens.md"

    # Initialize
    db = CharacterDatabase(char_file)
    chapter = ChapterContext(args.chapter)

    # Analyze
    print(f"Reading Chapter {args.chapter}...")
    summary = chapter.get_context_summary()
    active_chars = db.find_characters_in_text(chapter.content)

    char_names = [c['name'] for c in active_chars]
    print(f"Detected Characters: {', '.join(char_names)}")

    # Construct Prompt
    # 1. Scene Setting
    prompt = f"Digital Art, Cyberpunk Noir Style, High Contrast, Gritty Atmosphere.\n\n"
    prompt += f"SCENE CONTEXT:\n{summary[:500]}...\n\n" # Limit context length

    # 2. Character Details
    prompt += "CHARACTERS PRESENT:\n"
    ref_images = []

    for char in active_chars:
        prompt += f"- {char['name']}: {char['description']}\n"
        if char['image']:
            ref_images.append(char['image'])

    # 3. Style Modifiers
    prompt += "\nSTYLE: Analog photography aesthetic, rain-slicked streets, neon lights reflecting on wet surfaces, film grain, cinematic lighting."

    # Generate
    engine = NanoBanana()
    engine.generate_art(prompt, ref_images)

if __name__ == "__main__":
    main()

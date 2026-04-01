import os
import re


class CharacterDatabase:
    def __init__(self, filepath):
        self.filepath = filepath
        self.characters = {}
        self._alias_map = None
        self._compiled_pattern = None
        self.load()

    def load(self):
        if not os.path.exists(self.filepath):
            print(f"⚠️ Warning: Character file not found at {self.filepath}")
            return

        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except (IOError, OSError) as e:
            print(f"⚠️ Error reading character file: {e}")
            return

        sections = re.split(r'\n## ', content)

        for section in sections:
            self._parse_character_section(section)

        print(f"📚 Loaded {len(self.characters)} characters from database.")

    def _parse_character_section(self, section):
        if not section.strip() or section.startswith('# '):
            return

        lines = section.split('\n')
        name_line = lines[0].strip()
        # Strip simple markdown links/brackets without risking ReDoS via non-greedy quantifiers
        name_clean = re.sub(r'\[([^\]]+)\](?:\([^\)]+\))?', r'\1', name_line)
        name_clean = name_clean.replace('[', '').replace(']', '')
        name_clean = name_clean.strip().replace('*', '').strip()

        # Capture markdown image links
        image_match = re.search(r'!\[[^\]]*\]\(([^\)]+)\)', section)
        image_path = image_match.group(1) if image_match else None

        description_parts = self._extract_description_parts(lines)

        aliases = self._generate_aliases(name_clean)

        self.characters[name_clean] = {
            "name": name_clean,
            "aliases": list(aliases),
            "image": image_path,
            "description": ". ".join(description_parts),
        }

    def _extract_description_parts(self, lines):
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
        return description_parts

    def _generate_aliases(self, name_clean):
        aliases = {name_clean}
        nickname_match = re.search(r'"(.*?)"', name_clean)
        if nickname_match:
            aliases.add(nickname_match.group(1))

        parts = name_clean.split()
        if parts and len(parts[0]) > 2:
            aliases.add(parts[0])

        return aliases

    def find_characters_in_text(self, text):
        found = []
        if not text:
            return found
        text_lower = text.lower()

        if self._alias_map is None:
            self._alias_map = self._build_alias_map()

        if self._compiled_pattern is None:
            all_aliases = list(self._alias_map.keys())
            # Avoid zero-length aliases matching empty strings
            all_aliases = [a for a in all_aliases if a]
            if not all_aliases:
                return found

            all_aliases.sort(key=len, reverse=True)
            pattern_str = r'\b(' + '|'.join(map(re.escape, all_aliases)) + r')\b'
            self._compiled_pattern = re.compile(pattern_str)

        matches = set(self._compiled_pattern.findall(text_lower))

        found_ids = set()
        for match in matches:
            if match in self._alias_map:
                for char_data in self._alias_map[match]:
                    if char_data["name"] not in found_ids:
                        found.append(char_data)
                        found_ids.add(char_data["name"])
        return found

    def _build_alias_map(self):
        alias_map = {}
        for char_data in self.characters.values():
            for alias in char_data["aliases"]:
                lower_alias = alias.lower()
                if lower_alias not in alias_map:
                    alias_map[lower_alias] = []
                alias_map[lower_alias].append(char_data)
        return alias_map

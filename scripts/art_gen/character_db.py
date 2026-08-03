import os
import re

# Compile regex at module level for performance
NAME_CLEAN_RE = re.compile(r'\[([^\]]+)\](?:\([^\)]+\))?')
IMAGE_MATCH_RE = re.compile(r'!\[[^\]]*\]\(([^\)]+)\)')
NICKNAME_MATCH_RE = re.compile(r'"(.*?)"')
# Nem toda seção "## " do dossiê é uma ficha: o mapa de papéis também é uma.
# Quem não é personagem se declara com esta marca na primeira linha do bloco.
NAO_PERSONAGEM_RE = re.compile(r'<!--\s*nao-personagem\s*-->')
DESCRIPTION_KEYS_RE = re.compile(
    r'(Porte Físico|Vestuário|Marcas Distintivas|Cabelo|Olhos|Rosto|Idade|Prompt Visual):')

# Títulos viram alias genérico: "Dra." casava com Nise, Elara e Cecília ao mesmo tempo.
HONORIFICS = {
    "dr.", "dra.", "doutor", "doutora", "padre", "capitão", "capitao", "inspetor",
    "inspetora", "prefeito", "prefeita", "comissário", "comissario", "sargento",
    "tenente", "coronel", "major", "agente", "detetive", "chefe", "senhor", "senhora",
}


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

        self._drop_ambiguous_aliases()
        print(f"📚 Loaded {len(self.characters)} characters from database.")

    def _drop_ambiguous_aliases(self):
        """"Moretti" pertence a seis personagens: alias disputado não identifica ninguém.

        Só o nome completo sobrevive ao empate — é o que distingue Marco de Dante.
        """
        donos = {}
        for char in self.characters.values():
            for alias in char["aliases"]:
                donos.setdefault(alias.lower(), set()).add(char["name"])
        for char in self.characters.values():
            char["aliases"] = [
                a for a in char["aliases"]
                if a == char["name"] or len(donos[a.lower()]) == 1
            ]

    def _parse_character_section(self, section):
        # O primeiro bloco do arquivo é o comentário de regras + o título: não é personagem.
        if not section.strip() or section.startswith('# ') or section.startswith('<!--'):
            return
        # Seções editoriais (mapa de papéis, índices) marcam-se com NAO_PERSONAGEM_RE.
        if NAO_PERSONAGEM_RE.search(section):
            return

        lines = section.split('\n')
        name_line = lines[0].strip()
        # Strip simple markdown links/brackets without risking ReDoS via non-greedy quantifiers
        name_clean = NAME_CLEAN_RE.sub(r'\1', name_line)
        name_clean = name_clean.replace('[', '').replace(']', '')
        name_clean = name_clean.strip().replace('*', '').strip()

        # Capture markdown image links
        image_match = IMAGE_MATCH_RE.search(section)
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
        clean_lines = (line.strip().replace('*', '') for line in lines)
        return [cl for cl in clean_lines if DESCRIPTION_KEYS_RE.search(cl)]

    def _generate_aliases(self, name_clean):
        aliases = {name_clean}
        nickname_match = NICKNAME_MATCH_RE.search(name_clean)
        if nickname_match:
            aliases.add(nickname_match.group(1))

        # A prosa quase nunca usa o nome completo: "Vilar" aparece 128 vezes e
        # "Capitão Jonas Vilar" nenhuma. Sem o sobrenome, a cena perde a âncora.
        partes = [p.strip('",') for p in NICKNAME_MATCH_RE.sub("", name_clean).split()]
        proprios = [p for p in partes if len(p) >= 4 and p.lower() not in HONORIFICS]
        if proprios:
            aliases.add(proprios[0])
            aliases.add(proprios[-1])

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

        matches = {m.group() for m in self._compiled_pattern.finditer(text_lower)}

        found_ids = set()
        found = [
            char_data
            for match in matches if match in self._alias_map
            for char_data in self._alias_map[match]
            if char_data["name"] not in found_ids and not found_ids.add(char_data["name"])
        ]
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

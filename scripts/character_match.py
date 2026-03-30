import re

class CharacterMatcherMixin:
    """Mixin for CharacterDatabase classes to handle efficient regex-based character search."""

    def _build_alias_map(self, min_alias_length=1):
        alias_map = {}
        for char_data in self.characters.values():
            for alias in char_data["aliases"]:
                lower_alias = alias.lower()
                if len(lower_alias) < min_alias_length:
                    continue
                if lower_alias not in alias_map:
                    alias_map[lower_alias] = []
                alias_map[lower_alias].append(char_data)
        return alias_map

    def _build_alias_pattern(self):
        all_aliases = list(self._alias_map.keys())
        if not all_aliases:
            return None

        all_aliases.sort(key=len, reverse=True)
        all_aliases = [a for a in all_aliases if a]
        if not all_aliases:
            return None

        pattern = r'\b(' + '|'.join(map(re.escape, all_aliases)) + r')\b'
        return re.compile(pattern)

    def find_characters_in_text(self, text):
        found = []
        if not self._alias_pattern:
            return found

        text_lower = text.lower()
        matches = set(self._alias_pattern.findall(text_lower))

        for char_data in self.characters.values():
            for alias in char_data["aliases"]:
                if alias.lower() in matches:
                    found.append(char_data)
                    break
        return found

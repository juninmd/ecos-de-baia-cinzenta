from pathlib import Path
from typing import Dict, List, Optional

from scripts.art_gen.character_db import CharacterDatabase

REPO_ROOT = Path(__file__).resolve().parents[2]
PERSONAGENS_MD = REPO_ROOT / "docs" / "personagens.md"
PUBLIC_DIR = REPO_ROOT / "docs" / "public"

_db: Optional[CharacterDatabase] = None


def get_db() -> CharacterDatabase:
    """Character database from docs/personagens.md (cached)."""
    global _db
    if _db is None:
        _db = CharacterDatabase(str(PERSONAGENS_MD))
    return _db


def reference_image(char: Dict) -> Optional[Path]:
    """Portrait committed under docs/public/personagens/ — the identity anchor."""
    image = char.get("image")
    if not image:
        return None
    candidate = PUBLIC_DIR / image.lstrip("/")
    return candidate if candidate.exists() else None


# Ordem de prioridade: o que mais define a aparência vem primeiro e nunca é cortado.
VISUAL_KEYS = ("Vestuário", "Cabelo", "Olhos", "Marcas Distintivas", "Porte Físico", "Rosto", "Idade")


def describe(char: Dict, max_chars: int = 420) -> str:
    """Canonical visual description used to keep the look stable between chapters."""
    descricao = (char.get("description") or "").strip()
    if not descricao:
        return char["name"]
    partes = [p.strip() for p in descricao.split(". ") if p.strip()]
    ordenadas = [p for chave in VISUAL_KEYS for p in partes if p.startswith(chave)]
    texto = ". ".join(ordenadas) or descricao
    return f"{char['name']}: {texto[:max_chars]}"


MIN_ALIAS_LEN = 4


def mention_score(char: Dict, texto_lower: str) -> int:
    """Mentions of a character, ignoring aliases too short to be unambiguous.

    Nomes como "O Taxidermista" geram o alias "O", que casaria com todo artigo
    do texto em português e dominaria o ranking.
    """
    return max(
        (texto_lower.count(a.lower()) for a in char["aliases"] if len(a) >= MIN_ALIAS_LEN),
        default=0,
    )


def wardrobe(char: Dict) -> str:
    """Só o vestuário canônico — é o traço que os modelos mais trocam sozinhos."""
    for bruto in (char.get("description") or "").split(". "):
        parte = bruto.strip()  # os trechos vêm indentados do markdown
        if parte.startswith("Vestuário:"):
            return parte.split(":", 1)[1].strip().rstrip(".")
    return ""


def detect(texto: str, limit: int = 3) -> List[Dict]:
    """Characters actually mentioned in a scene, most relevant first."""
    encontrados = get_db().find_characters_in_text(texto)
    if not encontrados:
        return []
    texto_lower = texto.lower()
    pontuados = [(mention_score(c, texto_lower), c) for c in encontrados]
    relevantes = sorted(
        ((score, c) for score, c in pontuados if score > 0), key=lambda t: t[0], reverse=True
    )
    return [c for _, c in relevantes[:limit]]


def pick_anchor(chars: List[Dict]) -> Optional[Dict]:
    """First character with a usable reference portrait."""
    for char in chars:
        if reference_image(char):
            return char
    return None

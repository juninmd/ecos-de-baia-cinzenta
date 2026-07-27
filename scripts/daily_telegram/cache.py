from pathlib import Path
from typing import List, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
CENAS_DIR = REPO_ROOT / "docs" / "public" / "cenas"
MIN_BYTES = 2048


def scene_path(numero: int, indice: int) -> Path:
    """Canonical location of a scene frame — committed art, reused forever (AGENTS.md §6)."""
    return CENAS_DIR / f"capitulo_{numero}" / f"cena_{indice}.jpg"


def cached(numero: int, indice: int) -> Optional[Path]:
    """Existing scene art, if it was already generated in a previous run."""
    caminho = scene_path(numero, indice)
    if caminho.exists() and caminho.stat().st_size > MIN_BYTES:
        return caminho
    return None


def chapter_scenes(numero: int) -> List[Path]:
    """All cached frames of a chapter, in scene order."""
    pasta = CENAS_DIR / f"capitulo_{numero}"
    if not pasta.is_dir():
        return []
    return sorted(
        (p for p in pasta.glob("cena_*.jpg") if p.stat().st_size > MIN_BYTES),
        key=lambda p: int(p.stem.split("_")[1]),
    )


def coverage(numero: int, total: int) -> str:
    """Human readable progress of a chapter's storyboard."""
    return f"{len(chapter_scenes(numero))}/{total} cenas em cache"

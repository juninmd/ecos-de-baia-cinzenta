import re
from pathlib import Path
from typing import Dict, List, Optional

from scripts.video_gen.parser import ChapterParser

REPO_ROOT = Path(__file__).resolve().parents[2]
CHAPTER_DIRS = [REPO_ROOT / "docs" / "public", REPO_ROOT / "docs"]
CHAPTER_FILE_RE = re.compile(r"^capitulo-(\d+)\.md$")
TITLE_PREFIX_RE = re.compile(r"^Cap[íi]tulo\s+[\d.]+\s*[:\-–]\s*", re.IGNORECASE)
FRONTMATTER_KEYS = ("Título", "Data In-Game", "Localização", "Personagens Presentes")


def list_chapters() -> List[int]:
    """All chapter numbers available on disk (integers only, no 30.5 side-chapters)."""
    numeros = set()
    for directory in CHAPTER_DIRS:
        if not directory.is_dir():
            continue
        for path in directory.glob("capitulo-*.md"):
            match = CHAPTER_FILE_RE.match(path.name)
            if match:
                numeros.add(int(match.group(1)))
    return sorted(numeros)


def find_chapter_file(numero: int) -> Optional[Path]:
    """Chapter markdown path, preferring docs/public (mais atualizado)."""
    for directory in CHAPTER_DIRS:
        candidate = directory / f"capitulo-{numero}.md"
        if candidate.exists():
            return candidate
    return None


def find_local_art(numero: int) -> Optional[Path]:
    """Existing artwork committed in the repo, if any."""
    for directory in CHAPTER_DIRS:
        for name in (f"capitulo_{numero}.jpg", f"capitulo_{numero}.png"):
            candidate = directory / name
            if candidate.exists():
                return candidate
    return None


def read_metadata(chapter_path: Path) -> Dict[str, str]:
    """Frontmatter fields used to build the art prompt and the Telegram caption."""
    content = chapter_path.read_text(encoding="utf-8")
    meta: Dict[str, str] = {}
    if not content.startswith("---"):
        return meta
    parts = content.split("---", 2)
    if len(parts) < 3:
        return meta
    for line in parts[1].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        if key in FRONTMATTER_KEYS:
            meta[key] = value.strip()
    return meta


def load_chapter(numero: int) -> Dict:
    """Parsed chapter (numero, titulo, texto) plus frontmatter and local artwork."""
    path = find_chapter_file(numero)
    if path is None:
        raise FileNotFoundError(f"Capítulo {numero} não encontrado em docs/ ou docs/public/")
    data = ChapterParser.parse_chapter(path)
    # "Capítulo 1: Olhos de Vidro" -> "Olhos de Vidro" (o número já vai na legenda)
    data["titulo"] = TITLE_PREFIX_RE.sub("", data["titulo"]).strip() or data["titulo"]
    data["meta"] = read_metadata(path)
    data["local_art"] = find_local_art(numero)
    return data

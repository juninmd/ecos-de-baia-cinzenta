#!/usr/bin/env python3
"""Padroniza a pasta de capítulos para docs/capitulo-<n>.md."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"
PUBLIC_DIR = DOCS_DIR / "public"
CHAPTER_PATTERN = re.compile(r"^capitulo-(\d+(?:\.5)?)\.md$")


def chapter_sort_key(path: Path):
    match = CHAPTER_PATTERN.match(path.name)
    if not match:
        return (10_000, 0)
    value = float(match.group(1))
    return (int(value), 1 if value % 1 else 0)


def move_public_chapters() -> list[tuple[Path, Path]]:
    moved: list[tuple[Path, Path]] = []
    public_files = list(PUBLIC_DIR.glob("capitulo-*.md"))
    if not public_files:
        return moved

    for file in sorted(public_files, key=chapter_sort_key):
        if not CHAPTER_PATTERN.match(file.name):
            print(f"⚠️ Ignorando nome fora do padrão: {file.relative_to(ROOT)}")
            continue

        target = DOCS_DIR / file.name
        if target.exists():
            # Suppress print for speed, it's just noise and delays the console
            continue

        shutil.move(str(file), str(target))
        moved.append((file, target))
    return moved


def validate_docs_folder() -> tuple[list[Path], list[str]]:
    files = sorted(DOCS_DIR.glob("capitulo-*.md"), key=chapter_sort_key)
    invalid_names = [f.name for f in files if not CHAPTER_PATTERN.match(f.name)]
    return files, invalid_names


def main() -> int:
    moved = move_public_chapters()
    files, invalid_names = validate_docs_folder()

    if moved:
        print("✅ Arquivos movidos para pasta padrão:")
        for src, dst in moved:
            print(f"  - {src.relative_to(ROOT)} -> {dst.relative_to(ROOT)}")
    else:
        print("ℹ️ Nenhum capítulo fora do padrão encontrado em docs/public/.")

    if invalid_names:
        print("❌ Há capítulos com nome fora do padrão em docs/:")
        for name in invalid_names:
            print(f"  - {name}")
        return 1

    print(f"📚 Total de capítulos padronizados em docs/: {len(files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

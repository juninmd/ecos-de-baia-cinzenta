#!/usr/bin/env python3
"""Padroniza a pasta de capítulos para docs/capitulo-<n>.md."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

import os
ROOT = Path(os.path.normpath(str(Path(__file__).absolute()))).parents[1]
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
    from concurrent.futures import ThreadPoolExecutor
    moved: list[tuple[Path, Path]] = []
    public_files = list(PUBLIC_DIR.glob("capitulo-*.md"))
    if not public_files:
        return moved

    def process_move(file: Path) -> tuple[Path, Path] | None:
        if not CHAPTER_PATTERN.match(file.name):
            print(f"⚠️ Ignorando nome fora do padrão: {file.relative_to(ROOT)}")
            return None

        target = DOCS_DIR / file.name
        if target.exists():
            return None

        shutil.move(str(file), str(target))
        return (file, target)

    sorted_files = sorted(public_files, key=chapter_sort_key)
    with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as executor:
        results = executor.map(process_move, sorted_files)
        moved = [r for r in results if r is not None]

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

"""Read the same local Markdown includes rendered by VitePress."""

import re
from pathlib import Path

INCLUDE_RE = re.compile(r"^\s*<!--@include:\s*(.+?)\s*-->\s*$", re.MULTILINE)


def read_markdown(path: Path, ancestors: tuple[Path, ...] = ()) -> str:
    path = Path(path).resolve()
    root = ancestors[0].parent if ancestors else path.parent
    if path.suffix.lower() != ".md" or not path.is_relative_to(root):
        raise ValueError(f"Unsafe Markdown include: {path}")
    if path in ancestors:
        raise ValueError(f"Cyclic Markdown include: {path}")
    with open(path, encoding="utf-8") as source:
        content = source.read()

    def include(match: re.Match) -> str:
        target = (path.parent / match.group(1)).resolve()
        return read_markdown(target, (*ancestors, path))

    return INCLUDE_RE.sub(include, content)

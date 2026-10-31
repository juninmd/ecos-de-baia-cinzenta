#!/usr/bin/env python3
"""Liga as capas geradas ao frontmatter dos capítulos.

O gerador grava `docs/public/capitulo_N.jpg`; o site só mostra a capa se o
frontmatter tiver `image:`. Este passo fecha a lacuna e é idempotente: capítulo
com `image:` válido não é tocado, capítulo sem arquivo continua sem capa.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def capa_valida(texto: str) -> bool:
    m = re.search(r"^image:\s*(\S+)", texto, re.M)
    return bool(m) and (DOCS / "public" / m.group(1).lstrip("/")).exists()


def main() -> int:
    alterados = 0
    for p in sorted(DOCS.glob("capitulo-*.md")):
        num = p.stem.split("-", 1)[1]
        capa = DOCS / "public" / f"capitulo_{num}.jpg"
        if not capa.exists():
            continue
        texto = p.read_text(encoding="utf-8")
        if capa_valida(texto):
            continue
        novo = f"/capitulo_{num}.jpg"
        if re.search(r"^image:\s*\S+", texto, re.M):
            texto = re.sub(r"^image:\s*\S+", f"image: {novo}", texto, count=1, flags=re.M)
        elif texto.startswith("---\n"):
            texto = "---\n" + f"image: {novo}\n" + texto[4:]
        else:
            texto = "---\n" + f"image: {novo}\n" + "---\n\n" + texto
        p.write_text(texto, encoding="utf-8", newline="")
        alterados += 1
        print(f"{p.name} -> {novo}")
    print(f"capas integradas: {alterados}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

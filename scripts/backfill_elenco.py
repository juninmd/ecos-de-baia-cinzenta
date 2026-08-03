#!/usr/bin/env python3
"""Declara o elenco dos capítulos que não o declaram.

O portão D3 do AGENTS.md exige `Personagens Presentes` — é o que permite
escolher a âncora de identidade correta na hora de gerar arte da cena.
A lista é derivada da detecção real de menções, não inventada.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.art_gen.character_db import CharacterDatabase  # noqa: E402

DOCS = ROOT / "docs"
MIN_MENCOES = 2  # uma menção solta é citação, não presença em cena


def num(p: Path):
    m = re.match(r"capitulo-(\d+)(?:\.(\d+))?\.md$", p.name)
    return (int(m.group(1)), int(m.group(2) or 0)) if m else (10**6, 0)


def elenco(db: CharacterDatabase, texto: str) -> list[str]:
    baixo = texto.lower()
    presentes = []
    for char in db.characters.values():
        hits = max((baixo.count(a.lower()) for a in char["aliases"] if len(a) >= 4), default=0)
        if hits >= MIN_MENCOES:
            presentes.append((hits, char["name"]))
    presentes.sort(reverse=True)
    return [nome for _, nome in presentes[:6]]


def main() -> int:
    db = CharacterDatabase(str(DOCS / "personagens.md"))
    alterados = 0
    for p in sorted(DOCS.glob("capitulo-*.md"), key=num):
        texto = p.read_text(encoding="utf-8")
        if re.search(r"(Personagens Presentes|^characters:)", texto, re.M):
            continue
        nomes = elenco(db, texto)
        if not nomes:
            print(f"  ⚠ {p.name}: nenhum personagem canônico detectado")
            continue
        linha = f"Personagens Presentes: {', '.join(nomes)}"
        fm = re.match(r"^---\n(.*?)\n---\n", texto, re.S)
        if fm:
            novo = texto[: fm.end(1)] + f"\n{linha}" + texto[fm.end(1):]
        else:
            novo = f"---\n{linha}\n---\n\n{texto}"
        p.write_text(novo, encoding="utf-8")
        alterados += 1
    print(f"\n✅ elenco declarado em {alterados} capítulos")
    return 0


if __name__ == "__main__":
    sys.exit(main())

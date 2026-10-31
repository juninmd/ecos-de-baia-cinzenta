#!/usr/bin/env python3
"""Monta a fila de capas que faltam, para o agy gerar com a ferramenta nativa.

Uma capa por capítulo sem `image:` no frontmatter (ou apontando para arquivo
inexistente). O prompt vem do manifesto de cenas já montado, com o retrato
canônico anexado; o destino é `docs/public/capitulo_N.jpg`, em 16:9, o mesmo
formato das capas existentes.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
MANIFESTO = DOCS / "public" / "cenas" / "manifesto_pendentes.json"
SAIDA_MD = DOCS / "public" / "cenas" / "manifesto_capas.md"
SAIDA_JSON = DOCS / "public" / "cenas" / "manifesto_capas.json"
FORMATO = "Cinematic chapter cover, widescreen 16:9 landscape composition."


def capa_ok(p: Path) -> bool:
    m = re.search(r"^image:\s*(\S+)", p.read_text(encoding="utf-8"), re.M)
    return bool(m) and (DOCS / "public" / m.group(1).lstrip("/")).exists()


def escolher_cena(opcoes: list[dict]) -> dict | None:
    """A capa precisa do protagonista, não do figurante do primeiro bloco."""
    if not opcoes:
        return None
    return next((c for c in opcoes if "Gabo" in (c.get("ancora") or "")), None) or max(
        opcoes, key=lambda c: len(c.get("elenco") or [])
    )


def main() -> int:
    if not MANIFESTO.exists():
        print("manifesto de cenas ausente: rode build_scene_manifest.py")
        return 1
    cenas = json.loads(MANIFESTO.read_text(encoding="utf-8"))
    por_capitulo = {}
    for c in cenas:
        por_capitulo.setdefault(c["capitulo"], []).append(c)

    fila = []
    for p in sorted(DOCS.glob("capitulo-*.md")):
        if capa_ok(p):
            continue
        num = p.stem.split("-", 1)[1]
        opcoes = por_capitulo.get(num, [])
        cena = escolher_cena(opcoes)
        if cena is None:
            print(f"sem prompt no manifesto: capítulo {num}")
            continue
        fila.append({
            "capitulo": num,
            "saida": f"docs/public/capitulo_{num}.jpg",
            "seed": cena["seed"],
            "referencias": [e["referencia"] for e in cena["elenco"] if e.get("referencia")],
            "prompt": f"{cena['prompt']} {FORMATO}",
        })

    SAIDA_JSON.write_text(json.dumps(fila, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    linhas = [
        f"# Capas pendentes ({len(fila)})",
        "",
        "Para cada bloco: gere uma capa 16:9 com a ferramenta nativa de imagem,",
        "anexando os retratos de referência, e grave exatamente no caminho de saída.",
        "Não sobrescreva arquivo existente. Não escreva texto na imagem.",
        "",
    ]
    for i, item in enumerate(fila, 1):
        refs = ", ".join(f"`{r}`" for r in item["referencias"]) or "(sem retrato)"
        linhas += [
            f"## {i}. Capítulo {item['capitulo']}",
            f"- **Saída:** `{item['saida']}`",
            f"- **Referências:** {refs}",
            f"- **Seed:** {item['seed']}",
            "", "```text", item["prompt"], "```", "",
        ]
    SAIDA_MD.write_text("\n".join(linhas), encoding="utf-8")
    print(f"capas pendentes: {len(fila)}")
    print(f"briefing: {SAIDA_MD.relative_to(ROOT)}")
    print(f"json: {SAIDA_JSON.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

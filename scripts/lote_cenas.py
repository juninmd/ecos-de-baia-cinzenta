"""Corta o manifesto em lotes do tamanho da quota do dia, para o agy executar em ordem.

Duas mil e duzentas cenas não cabem numa sessão nem numa quota. O lote é a unidade de
trabalho: sai pronto para o CLI (prompt, retratos de referência e caminho de saída), e o
que já virou arquivo no disco nunca reaparece — a retomada é o próprio disco.

Uso:
    python scripts/lote_cenas.py                      # próximas 40 cenas
    python scripts/lote_cenas.py --tamanho 100        # lote maior
    python scripts/lote_cenas.py --capitulo 12        # só um capítulo
    python scripts/lote_cenas.py --briefing lote.md   # versão legível para colar no chat
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts.build_scene_manifest import DESTINO, carregar_regerar  # noqa: E402

LOTE_PADRAO = 40


def pendentes(manifesto: List[Dict], regerar: set) -> List[Dict]:
    """Entradas cuja imagem ainda não existe (ou existe e foi reprovada)."""
    return [
        entrada for entrada in manifesto
        if not (REPO_ROOT / entrada["saida"]).exists() or entrada["saida"] in regerar
    ]


def briefing(lote: List[Dict]) -> str:
    """Lote em markdown: uma cena por bloco, sem nada que o gerador precise adivinhar."""
    linhas = [
        f"# Lote de {len(lote)} cenas", "",
        "Para cada bloco: gere a imagem com o prompt, anexando os retratos de referência,",
        "e grave no caminho de saída. Não sobrescreva arquivo que já exista.", "",
    ]
    for i, cena in enumerate(lote, 1):
        referencias = [p["referencia"] for p in cena["elenco"]] or ["(sem retrato)"]
        linhas += [
            f"## {i}. Capítulo {cena['capitulo']}, cena {cena['cena']} — {cena['titulo']}",
            f"- **Saída:** `{cena['saida']}`",
            f"- **Seed:** {cena['seed']}",
            f"- **Enquadramento:** {cena['enquadramento']}",
            f"- **Referências:** {', '.join(f'`{r}`' for r in referencias)}",
            "", "```text", cena["prompt"], "```", "",
        ]
    return "\n".join(linhas)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tamanho", type=int, default=LOTE_PADRAO)
    parser.add_argument("--capitulo", help="Limita o lote a um capítulo")
    parser.add_argument("--saida", type=Path, help="Arquivo JSON do lote")
    parser.add_argument("--briefing", type=Path, help="Arquivo markdown do lote")
    args = parser.parse_args()

    if not DESTINO.exists():
        print("❌ manifesto ausente: rode python scripts/build_scene_manifest.py")
        return 1

    manifesto = json.loads(DESTINO.read_text(encoding="utf-8"))
    fila = pendentes(manifesto, carregar_regerar())
    if args.capitulo:
        fila = [c for c in fila if c["capitulo"] == args.capitulo]
    lote = fila[:args.tamanho]

    if args.saida:
        args.saida.write_text(json.dumps(lote, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"💾 {args.saida}")
    if args.briefing:
        args.briefing.write_text(briefing(lote), encoding="utf-8")
        print(f"💾 {args.briefing}")
    if not args.saida and not args.briefing:
        print(briefing(lote))

    print(f"📦 lote de {len(lote)} | fila total: {len(fila)} cenas pendentes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

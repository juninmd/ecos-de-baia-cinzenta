#!/usr/bin/env python3
"""Gera a amostra de voz de cada personagem e a tabela `docs/vozes.md`.

    uv run --no-sync --with edge-tts python scripts/gerar_vozes.py [--refazer]

Cada personagem do elenco (`scripts/daily_telegram/elenco.py`) ganha
`docs/public/vozes/<slug>.mp3` com a sua fala de prova. Amostra existente não é
regerada (a voz é canônica, como o retrato); `--refazer` apaga e sintetiza de novo.
"""
from __future__ import annotations

import argparse
import asyncio
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.daily_telegram.elenco import CASTING  # noqa: E402

SAIDA = ROOT / "docs" / "public" / "vozes"
TABELA = ROOT / "docs" / "vozes.md"
MIN_BYTES = 512


def slug(nome: str) -> str:
    base = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", base.lower()).strip("-")


async def sintetizar(texto: str, voz: str, rate: str, pitch: str, destino: Path) -> None:
    import edge_tts

    await edge_tts.Communicate(texto, voz, rate=rate, pitch=pitch).save(str(destino))


def gerar(refazer: bool) -> list[str]:
    SAIDA.mkdir(parents=True, exist_ok=True)
    falhas = []
    for nome, (voz, rate, pitch, fala) in CASTING.items():
        destino = SAIDA / f"{slug(nome)}.mp3"
        if refazer and destino.exists():
            destino.unlink()
        if destino.exists() and destino.stat().st_size > MIN_BYTES:
            continue
        try:
            asyncio.run(sintetizar(fala, voz, rate, pitch, destino))
        except Exception as exc:  # rede/serviço: reporta e segue para os demais
            falhas.append(f"{nome}: {type(exc).__name__}")
            continue
        if destino.stat().st_size <= MIN_BYTES:
            destino.unlink()
            falhas.append(f"{nome}: áudio vazio")
    return falhas


def escrever_tabela() -> None:
    linhas = [
        "---\npageClass: pagina-larga\naside: false\n---\n",
        "# Vozes do elenco\n",
        "Cada personagem tem uma identidade sonora única: a trinca *voz, ritmo e tom* nunca se repete",
        "(travado por `tests/test_vozes_unicas.py`). A voz de um personagem não muda entre capítulos.",
        "Gerado por `scripts/gerar_vozes.py`; elenco em `scripts/daily_telegram/elenco.py`.\n",
        "| Personagem | Voz | Ritmo | Tom | Amostra |",
        "| --- | --- | --- | --- | --- |",
    ]
    for nome, (voz, rate, pitch, fala) in CASTING.items():
        arq = f"/vozes/{slug(nome)}.mp3"
        linhas.append(f"| {nome} | `{voz}` | {rate} | {pitch} | <audio controls preload=\"none\" src=\"{arq}\"></audio><br>*{fala}* |")
    TABELA.write_text("\n".join(linhas) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--refazer", action="store_true")
    falhas = gerar(ap.parse_args().refazer)
    escrever_tabela()
    for f in falhas:
        print("⚠", f)
    print(f"{len(CASTING) - len(falhas)}/{len(CASTING)} amostras em {SAIDA}")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Mede as capas dos capítulos com o mesmo portão das cenas.

Capa não é cena: a antiga pode ser quadrada (1024x1024) e continua publicada.
Por isso o script **relata** e não reprova sozinho; ele existe para separar capa
boa de capa borrada/quadro chapado e alimentar a fila de regeração.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.art_gen.homologacao import avaliar, medir  # noqa: E402

DOCS = ROOT / "docs"
RELATORIO = DOCS / "qualidade_capas.md"


def capa_do_capitulo(p: Path) -> Path | None:
    m = re.search(r"^image:\s*(\S+)", p.read_text(encoding="utf-8"), re.M)
    if not m:
        return None
    return DOCS / "public" / m.group(1).lstrip("/")


def main() -> int:
    linhas = [
        "# Homologação das capas",
        "",
        "> Gerado por `python scripts/verificar_capas.py`.",
        "> Capa quadrada antiga é alerta, não reprovação automática.",
        "",
        "| Capítulo | Arquivo | Medida | Situação |",
        "|---|---|---|---|",
    ]
    ruins = []
    for p in sorted(DOCS.glob("capitulo-*.md")):
        capa = capa_do_capitulo(p)
        if capa is None or not capa.exists():
            linhas.append(f"| {p.stem} | (ausente) | - | **sem capa** |")
            continue
        medida = medir(capa)
        reprovas, alertas = avaliar(medida)
        situacao = "ok"
        if reprovas:
            situacao = "reprovar: " + "; ".join(reprovas)
            ruins.append((p.stem, capa.name, reprovas))
        elif alertas:
            situacao = "alerta: " + "; ".join(alertas)
        linhas.append(
            f"| {p.stem} | `{capa.name}` | {medida.largura}x{medida.altura}, "
            f"nitidez {medida.nitidez:.0f} | {situacao} |"
        )
    linhas += ["", f"**{len(ruins)} capas com defeito objetivo.**", ""]
    for nome, arquivo, motivos in ruins:
        linhas.append(f"- `{nome}` (`{arquivo}`): {'; '.join(motivos)}")
    RELATORIO.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(f"capas com defeito: {len(ruins)}")
    for nome, arquivo, motivos in ruins[:15]:
        print(f"  {nome} {arquivo}: {'; '.join(motivos)}")
    print(f"relatório: {RELATORIO.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

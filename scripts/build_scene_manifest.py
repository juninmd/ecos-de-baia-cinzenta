"""Monta o manifesto das cenas pendentes, para o agy não gastar quota lendo capítulo.

A quota de imagem do Gemini é o recurso escasso: cada rodada do agy que lê capítulo,
divide cenas e escolhe âncora queima tokens que não viram imagem. Aqui isso tudo é
resolvido offline, e o agy recebe prompt pronto + retrato de referência por cena.

O alvo da obra é **dez cenas por capítulo** (`CENAS_POR_CAPITULO`): três imagens não
cobrem um capítulo de 1.100 palavras e deixavam o livro inteiro com o mesmo trio de
planos. As cláusulas de fidelidade ficam em `scripts/art_gen/prompt_cena.py`.
"""

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts.art_gen.chapters import get_chapter_files, ler_capitulo  # noqa: E402
from scripts.art_gen.prompt_cena import montar_elenco, montar_entrada  # noqa: E402
from scripts.daily_telegram import scenes  # noqa: E402

DESTINO = REPO_ROOT / "docs" / "public" / "cenas" / "manifesto_pendentes.json"
CENAS_POR_CAPITULO = 10


def carregar_regerar() -> set:
    """Cenas que já têm arquivo mas precisam ser refeitas por violarem a fisionomia.

    Nunca se apaga a imagem antiga: ela fica no lugar até a nova existir. O portão de
    homologação (`scripts/homologar_cenas.py`) realimenta esta lista sozinho.
    """
    lista = DESTINO.parent / "regerar.txt"
    if not lista.exists():
        return set()
    return {
        linha.strip()
        for linha in lista.read_text(encoding="utf-8").splitlines()
        if linha.strip() and not linha.startswith("#")
    }


def cenas_faltantes(cap: dict, regerar: set, total: int) -> list:
    """Índices de 1 a `total` que ainda não têm arquivo (ou foram marcados para regerar)."""
    pasta = cap["folder_path"]
    return [
        m for m in range(1, total + 1)
        if not (pasta / f"cena_{m}.jpg").exists()
        or f"docs/public/cenas/{cap['folder_name']}/cena_{m}.jpg" in regerar
    ]


def build(cenas_por_capitulo: int = CENAS_POR_CAPITULO) -> list:
    regerar = carregar_regerar()
    pendentes = []
    for cap in get_chapter_files():
        faltando = cenas_faltantes(cap, regerar, cenas_por_capitulo)
        if not faltando:
            continue

        titulo, corpo = ler_capitulo(cap)
        cenas = scenes.split_scenes(corpo, quantidade=cenas_por_capitulo)
        # Capítulo curto pode render menos blocos que o alvo; a última cena se repete
        # com outro enquadramento em vez de deixar buraco na numeração.
        while len(cenas) < cenas_por_capitulo:
            cenas.append(cenas[-1])

        for idx in faltando:
            cena = cenas[idx - 1]
            cena.indice = idx
            pendentes.append(
                montar_entrada(cap, titulo, cena, montar_elenco(cena.personagens, float(cap["num_str"])))
            )
    return pendentes


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cenas", type=int, default=CENAS_POR_CAPITULO,
                        help="Cenas por capítulo (padrão: 10)")
    args = parser.parse_args()

    pendentes = build(args.cenas)
    DESTINO.write_text(
        json.dumps(pendentes, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    com_ancora = sum(1 for p in pendentes if p["referencia"])
    capitulos = len({p["capitulo"] for p in pendentes})
    print(f"📋 {len(pendentes)} cenas pendentes em {capitulos} capítulos "
          f"({com_ancora} com retrato de referência)")
    print(f"💾 {DESTINO.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()

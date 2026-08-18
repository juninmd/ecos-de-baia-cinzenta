"""Portão de homologação das imagens de cena: mede, reprova e devolve para a fila.

Sem isto, "gerar dez imagens por capítulo" vira dois mil arquivos que ninguém olhou.
O que reprova aqui não é gosto: é resolução, nitidez, contraste, arquivo chapado e
cena repetida. Fidelidade de rosto é medida à parte, com visão (`--visao`).

Uso:
    python scripts/homologar_cenas.py                # mede e escreve o relatório
    python scripts/homologar_cenas.py --realimentar  # + manda reprovadas para regerar.txt
    python scripts/homologar_cenas.py --estrito      # + sai com erro se algo reprovou
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts.art_gen import fidelidade, homologacao, relatorio_imagens  # noqa: E402
from scripts.art_gen.acervo import (  # noqa: E402
    contar_cobertura, elenco_de, imagens_canonicas, relativo,
)
from scripts.build_scene_manifest import CENAS_POR_CAPITULO  # noqa: E402

CENAS_DIR = REPO_ROOT / "docs" / "public" / "cenas"
RELATORIO = REPO_ROOT / "docs" / "qualidade_imagens.md"
REGERAR = CENAS_DIR / "regerar.txt"
CABECALHO_REGERAR = (
    "# Cenas reprovadas na homologação. O build_scene_manifest.py recoloca cada uma na\n"
    "# fila. A imagem antiga fica no lugar até a nova existir (regra 6 do AGENTS.md).\n"
)
def avaliar_acervo(imagens: List[Path]) -> Dict:
    defeitos: List[Dict] = []
    alertas: List[Dict] = []
    hashes: Dict[str, int] = {}
    aprovadas = 0

    for imagem in imagens:
        nome = relativo(imagem)
        medida = homologacao.carregar(imagem)
        if medida is None:
            defeitos.append({"arquivo": nome, "motivos": ["arquivo ilegível ou truncado"]})
            continue
        reprovas, avisos = homologacao.avaliar(medida)
        hashes[nome] = medida.hash_visual
        if reprovas:
            defeitos.append({"arquivo": nome, "motivos": reprovas})
        else:
            aprovadas += 1
        if avisos:
            alertas.append({"arquivo": nome, "motivos": avisos})

    for a, b, dist in homologacao.duplicatas(hashes):
        # Duas cenas iguais no mesmo capítulo é defeito; em capítulos diferentes, alerta.
        destino = defeitos if Path(a).parent == Path(b).parent else alertas
        destino.append({"arquivo": b, "motivos": [f"quase idêntica a `{a}` (distância {dist})"]})

    return {
        "total": len(imagens),
        "aprovadas": aprovadas,
        "defeitos": defeitos,
        "alertas": alertas,
        "cobertura": contar_cobertura(imagens),
        "hashes": hashes,
    }


def realimentar_fila(defeitos: List[Dict]) -> int:
    """Escreve as reprovadas em regerar.txt, preservando o que já estava lá."""
    existentes = set()
    if REGERAR.exists():
        existentes = {
            linha.strip() for linha in REGERAR.read_text(encoding="utf-8").splitlines()
            if linha.strip() and not linha.startswith("#")
        }
    novas = {d["arquivo"] for d in defeitos} - existentes
    todas = sorted(existentes | novas)
    REGERAR.write_text(CABECALHO_REGERAR + "\n".join(todas) + "\n", encoding="utf-8")
    return len(novas)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--realimentar", action="store_true",
                        help="Manda as reprovadas para docs/public/cenas/regerar.txt")
    parser.add_argument("--estrito", action="store_true",
                        help="Sai com código 1 se houver reprovação")
    parser.add_argument("--alvo", type=int, default=CENAS_POR_CAPITULO)
    parser.add_argument("--visao", type=int, default=0, metavar="N",
                        help="Audita a fidelidade de N imagens com o Gemini (0 = não audita)")
    args = parser.parse_args()

    imagens = imagens_canonicas()
    resultado = avaliar_acervo(imagens)
    if args.visao:
        resultado["defeitos"] += fidelidade.auditar_acervo(
            imagens, lambda p: elenco_de(p, args.alvo), REPO_ROOT, args.visao
        )
    relatorio_imagens.escrever(RELATORIO, resultado, args.alvo)

    faltam = sum(max(0, args.alvo - n) for n in resultado["cobertura"].values())
    print(f"🖼️  {resultado['total']} imagens | ✅ {resultado['aprovadas']} "
          f"| ❌ {len(resultado['defeitos'])} | ⚠️ {len(resultado['alertas'])}")
    print(f"📊 cobertura: faltam {faltam} cenas para {args.alvo} por capítulo")
    print(f"💾 {RELATORIO.relative_to(REPO_ROOT)}")

    if args.realimentar and resultado["defeitos"]:
        print(f"♻️  {realimentar_fila(resultado['defeitos'])} cenas novas em regerar.txt")
    return 1 if args.estrito and resultado["defeitos"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

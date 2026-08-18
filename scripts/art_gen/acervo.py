"""Leitura do acervo de cenas no disco: quais arquivos contam e a que capítulo pertencem."""

import re
from pathlib import Path
from typing import Dict, List

from scripts.art_gen.chapters import CENAS_DIR, REPO_ROOT, get_chapter_files
from scripts.art_gen.prompt_cena import elenco_da_cena

# Só as cenas canônicas: as pastas `Ncenas/` são cache do modo animado, com outro padrão.
CENA_CANONICA = re.compile(r"^cena_\d+(_v\d+)?\.jpg$")


def imagens_canonicas(raiz: Path = CENAS_DIR) -> List[Path]:
    return sorted(p for p in raiz.glob("capitulo_*/*.jpg") if CENA_CANONICA.match(p.name))


def relativo(caminho: Path) -> str:
    return caminho.relative_to(REPO_ROOT).as_posix()


def capitulo_de(caminho: Path) -> str:
    return caminho.parent.name.replace("capitulo_", "").replace("_", ".")


def indice_da_cena(caminho: Path) -> int:
    return int(caminho.name.split("_")[1].split(".")[0])


def elenco_de(caminho: Path, alvo: int) -> List[Dict]:
    """Elenco canônico da cena, recalculado a partir do capítulo no disco."""
    caps = {cap["num_str"]: cap for cap in get_chapter_files()}
    cap = caps.get(capitulo_de(caminho))
    return elenco_da_cena(cap, indice_da_cena(caminho), alvo) if cap else []


def contar_cobertura(imagens: List[Path]) -> Dict[str, int]:
    """Cenas distintas por capítulo — versão `_v2` não conta como cena nova."""
    cobertura = {cap["num_str"]: 0 for cap in get_chapter_files()}
    vistas = set()
    for imagem in imagens:
        chave = (imagem.parent.name, indice_da_cena(imagem))
        if chave in vistas:
            continue
        vistas.add(chave)
        capitulo = capitulo_de(imagem)
        cobertura[capitulo] = cobertura.get(capitulo, 0) + 1
    return cobertura

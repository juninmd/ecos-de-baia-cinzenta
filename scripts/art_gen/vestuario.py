"""Guarda-roupa canônico por capítulo — o traço que os modelos mais trocam sozinhos."""

import re
from typing import Dict, List

from scripts.art_gen import continuidade

FASE_ATUAL_RE = re.compile(r"Fase atual[^:]*:\s*", re.IGNORECASE)
FASE_ORIGINAL_RE = re.compile(r"Fase original[^:]*:\s*", re.IGNORECASE)


def na_fase(nome: str, vestuario: str, capitulo: float) -> str:
    """Escolhe a fase do guarda-roupa quando a ficha declara mais de uma.

    Mandar as duas fases no prompt é pior que mandar a errada: o modelo mistura o fedora
    da fase antiga com o macacão da atual e inventa um terceiro personagem.
    """
    atual = FASE_ATUAL_RE.search(vestuario)
    if not atual:
        return vestuario
    texto_atual = vestuario[atual.end():].strip()
    original = FASE_ORIGINAL_RE.search(vestuario)
    if original is None:
        return texto_atual
    texto_original = vestuario[original.end():atual.start()].strip().rstrip(".")
    marco = continuidade.primeiro_marco(nome)
    return texto_atual if marco is None or capitulo >= marco else texto_original


def reforco(elenco: List[Dict]) -> str:
    """Última cláusula do prompt, repetindo a roupa de cada personagem.

    A auditoria mostrou que a fisionomia se mantém, mas o vestuário escapa em cena de
    ação: o modelo troca o sobretudo bege por qualquer coisa que "combine" com a briga.
    Repetir no fecho é o que mais segura, porque é a última instrução que ele lê.
    """
    # Nome inteiro: cortar no primeiro espaço produz "Dra." e "O", que não identificam ninguém.
    roupas = [f"{p['nome']} wears {p['vestuario']}" for p in elenco if p["vestuario"]]
    if not roupas:
        return ""
    return ". MANDATORY WARDROBE, no substitutions even in action scenes: " + "; ".join(roupas)

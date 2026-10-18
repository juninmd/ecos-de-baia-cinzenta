"""Invariantes da rota Qwen-Image-Edit: vinte cenas por capítulo, sem plano espelhado.

O Edit exige imagem de entrada e reescreve o mundo em volta dela. Duas coisas quebram
o capítulo em silêncio e por isso são travadas aqui: cena sem âncora (não gera nada, e
o capítulo fica com buraco permanente na numeração) e instrução que pede proximidade
em plano aberto (o que devolve retrato 3x4 no lugar da cena).
"""
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts.art_gen.chapters import get_chapter_files, ler_capitulo  # noqa: E402
from scripts.art_gen.prompt_cena import seed_da_cena  # noqa: E402
from scripts.daily_telegram import characters, scenes  # noqa: E402
from scripts.gerar_cenas_qwen_edit import (  # noqa: E402
    CENAS_POR_CAPITULO, ancora_do_capitulo, cenas_do_capitulo, instrucao,
)


@pytest.fixture(scope="module")
def capitulo():
    caps = get_chapter_files()
    assert caps, "nenhum capítulo encontrado em docs/"
    return caps[0]


@pytest.fixture(scope="module")
def corpo(capitulo):
    return ler_capitulo(capitulo)[1]


@pytest.fixture(scope="module")
def lista(corpo):
    return cenas_do_capitulo(corpo)


def test_sempre_vinte_cenas(lista):
    assert len(lista) == CENAS_POR_CAPITULO


def test_capitulo_curto_ainda_rende_vinte():
    """`split_scenes` limita à quantidade de parágrafos: sem o preenchimento, um capítulo
    de três parágrafos ficaria eternamente incompleto — a retomada é por arquivo faltando."""
    curto = "Primeiro parágrafo do capítulo.\n\nSegundo.\n\nTerceiro."
    assert len(cenas_do_capitulo(curto)) == CENAS_POR_CAPITULO


def test_segunda_volta_nao_repete_a_ordem_de_planos(lista):
    """Dez planos para vinte cenas: sem deslocamento a cena 11 sairia igual à 1."""
    primeira = [c.shot for c in lista[:len(scenes.SHOTS)]]
    segunda = [c.shot for c in lista[len(scenes.SHOTS):]]
    assert primeira != segunda
    assert len(set(segunda)) == len(scenes.SHOTS)


def test_seed_e_deterministica_e_nao_colide_com_capitulo_fracionario():
    assert seed_da_cena("30", 20) != seed_da_cena("30.5", 20)
    assert seed_da_cena("7", 3) == seed_da_cena("7", 3)


def test_toda_cena_recebe_ancora(lista, corpo):
    """O Edit não gera sem imagem de entrada: cena sem personagem citado herda a do capítulo."""
    padrao = ancora_do_capitulo(lista, corpo)
    assert padrao is not None
    for cena in lista:
        anchor = characters.pick_anchor(cena.personagens) or padrao
        assert characters.reference_image(anchor) is not None


def test_instrucao_separa_o_que_preserva_do_que_muda(lista, corpo):
    cena = lista[1]
    anchor = characters.pick_anchor(cena.personagens) or ancora_do_capitulo(lista, corpo)
    texto = instrucao(cena, anchor)
    assert "Keep the same person" in texto
    assert "NEW photograph" in texto
    assert cena.shot in texto


def test_plano_aberto_nao_pede_corpo_grande_no_quadro(lista, corpo):
    """Pedir "upper body large in the frame" em plano aberto devolve retrato 3x4."""
    padrao = ancora_do_capitulo(lista, corpo)
    abertas = [c for c in lista if "wide" in c.shot]
    assert abertas, "a rotação de planos deveria conter plano aberto"
    for cena in abertas:
        anchor = characters.pick_anchor(cena.personagens) or padrao
        texto = instrucao(cena, anchor)
        assert "upper body large in the frame" not in texto
        assert "the environment dominates" in texto

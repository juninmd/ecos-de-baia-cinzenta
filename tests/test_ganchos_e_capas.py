"""Ganchos: triagem de abertura/fecho e fila de capas."""

import json

from scripts import auditoria_ganchos as ganchos
from scripts import integrar_capas, manifesto_capas


def test_abertura_com_formula_perde_nota():
    formula = "O silêncio não era vazio. Era uma coisa pesada que enchia o corredor inteiro."
    concreta = "— Corre — disse Val, e o corredor inteiro apagou às 03h14."
    assert ganchos.avalia_abertura(formula)[0] < ganchos.avalia_abertura(concreta)[0]


def test_fecho_generico_perde_nota():
    fraco = "Ele sabia que a caçada ainda não havia começado."
    forte = "Do outro lado da porta, alguém começou a contar."
    assert ganchos.avalia_fecho(fraco)[0] < ganchos.avalia_fecho(forte)[0]


def test_fecho_que_vira_a_pagina_nao_e_penalizado_por_pergunta():
    nota, motivos = ganchos.avalia_fecho("Quantos prédios?")
    assert nota >= 3
    assert "fecha com pergunta" in motivos


def test_capa_escolhe_o_protagonista_e_nao_o_figurante():
    cenas = [
        {"capitulo": "125", "cena": 1, "ancora": "Operativo Aeterna Sec", "elenco": []},
        {"capitulo": "125", "cena": 2, "ancora": 'Gabriel "Gabo" Moretti', "elenco": []},
    ]
    assert manifesto_capas.escolher_cena(cenas)["cena"] == 2


def test_capa_sem_protagonista_usa_a_cena_com_mais_elenco():
    cenas = [
        {"capitulo": "200", "cena": 1, "ancora": "Elias", "elenco": [{"nome": "Elias"}]},
        {"capitulo": "200", "cena": 2, "ancora": "Valéria", "elenco": [{"nome": "Val"}, {"nome": "Elias"}]},
    ]
    assert manifesto_capas.escolher_cena(cenas)["cena"] == 2


def test_manifesto_de_capas_nao_duplica_capa_existente():
    fila = json.loads((manifesto_capas.SAIDA_JSON).read_text(encoding="utf-8"))
    saidas = [item["saida"] for item in fila]
    assert len(saidas) == len(set(saidas))
    assert all("16:9" in item["prompt"] for item in fila)


def test_capa_so_entra_no_frontmatter_se_o_arquivo_existe():
    existente = integrar_capas.capa_valida("---\nimage: /capitulo_1.jpg\n---\n")
    faltando = integrar_capas.capa_valida("---\nimage: /nao-existe.jpg\n---\n")
    assert existente is True
    assert faltando is False


def test_variante_antiga_da_vez_lugar_a_capa_padrao():
    assert integrar_capas.deve_trocar("image: /capitulo_117_pro.jpg", "/capitulo_117.jpg") is True
    assert integrar_capas.deve_trocar("image: /capitulo_1.jpg", "/capitulo_1.jpg") is False

"""Portão de homologação: o que reprova sozinho, o que alerta e o que entra no relatório."""

import numpy as np
import pytest
from PIL import Image

from scripts.art_gen import acervo, homologacao, relatorio_imagens

TAMANHO = (1376, 768)


def _salvar(tmp_path, arranjo, nome="cena_1.jpg"):
    destino = tmp_path / nome
    Image.fromarray(arranjo.astype("uint8")).save(destino, quality=92)
    return destino


def _ruido(semente=0, tamanho=TAMANHO):
    gerador = np.random.default_rng(semente)
    return gerador.integers(0, 255, (tamanho[1], tamanho[0], 3))


def test_imagem_chapada_reprova(tmp_path):
    chapada = np.full((TAMANHO[1], TAMANHO[0], 3), 40)
    medida = homologacao.medir(_salvar(tmp_path, chapada))
    reprovas, _ = homologacao.avaliar(medida)
    assert any("contraste" in m for m in reprovas)
    assert any("chapado" in m for m in reprovas)


def test_imagem_pequena_reprova(tmp_path):
    medida = homologacao.medir(_salvar(tmp_path, _ruido(1, (320, 180))))
    reprovas, _ = homologacao.avaliar(medida)
    assert any("resolução" in m for m in reprovas)


def test_imagem_quadrada_reprova_por_proporcao(tmp_path):
    medida = homologacao.medir(_salvar(tmp_path, _ruido(2, (1200, 1200))))
    reprovas, _ = homologacao.avaliar(medida)
    assert any("proporção" in m for m in reprovas)


def test_cena_do_acervo_e_aprovada():
    publicadas = acervo.imagens_canonicas()
    assert publicadas, "o acervo publicado não pode estar vazio"
    reprovas, _ = homologacao.avaliar(homologacao.medir(publicadas[0]))
    assert reprovas == []


def test_arquivo_ilegivel_nao_explode(tmp_path):
    quebrado = tmp_path / "cena_1.jpg"
    quebrado.write_bytes(b"nao sou um jpeg")
    assert homologacao.carregar(quebrado) is None


def test_faixa_de_texto_sobe_com_legenda_queimada():
    limpo = _ruido(3).astype("float32").mean(axis=2)
    suave = np.repeat(np.repeat(limpo[::8, ::8], 8, axis=0), 8, axis=1)
    com_texto = suave.copy()
    # Faixa estreita de alto contraste horizontal, como uma legenda.
    com_texto[700:716, ::6] = 255
    assert homologacao.faixa_de_texto(com_texto) > homologacao.faixa_de_texto(suave)


def test_duplicata_e_detectada_por_hash(tmp_path):
    base = _ruido(4)
    a = homologacao.medir(_salvar(tmp_path, base, "cena_1.jpg"))
    b = homologacao.medir(_salvar(tmp_path, base, "cena_2.jpg"))
    c = homologacao.medir(_salvar(tmp_path, _ruido(5), "cena_3.jpg"))
    pares = homologacao.duplicatas({"a": a.hash_visual, "b": b.hash_visual, "c": c.hash_visual})
    assert [(x, y) for x, y, _ in pares] == [("a", "b")]


def test_acervo_le_capitulo_e_indice_do_caminho(tmp_path):
    caminho = tmp_path / "capitulo_30_5" / "cena_10_v2.jpg"
    assert acervo.capitulo_de(caminho) == "30.5"
    assert acervo.indice_da_cena(caminho) == 10


def test_cobertura_nao_conta_versao_como_cena_nova(tmp_path):
    pasta = tmp_path / "capitulo_1"
    pasta.mkdir()
    for nome in ("cena_1.jpg", "cena_1_v2.jpg", "cena_2.jpg"):
        (pasta / nome).touch()
    cobertura = acervo.contar_cobertura(sorted(pasta.glob("*.jpg")))
    assert cobertura["1"] == 2


def test_relatorio_mostra_reprovadas_e_cobertura():
    resultado = {
        "total": 1, "aprovadas": 0,
        "defeitos": [{"arquivo": "docs/public/cenas/capitulo_1/cena_1.jpg",
                      "motivos": ["nitidez 10.0 abaixo de 120.0"]}],
        "alertas": [], "cobertura": {"1": 1, "2": 10},
    }
    texto = relatorio_imagens.montar(resultado, 10)
    assert "## Reprovadas" in texto
    assert "nitidez" in texto
    assert "| 1 | 1 | 9 |" in texto
    assert "9 cenas a gerar" in texto


@pytest.mark.parametrize("indicador", ["Cobertura", "Aprovadas", "Reprovadas"])
def test_relatorio_tem_o_placar(indicador):
    resultado = {"total": 0, "aprovadas": 0, "defeitos": [], "alertas": [], "cobertura": {}}
    assert indicador in relatorio_imagens.montar(resultado, 10)

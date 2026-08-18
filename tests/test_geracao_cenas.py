"""Fila em lotes e o runner que gera, homologa e desiste sem deixar refugo no disco."""

import numpy as np
from PIL import Image

from scripts import gerar_cenas_manifesto as runner
from scripts import lote_cenas
from scripts.art_gen import fidelidade, gemini, provedores

ENTRADA = {
    "capitulo": "7", "cena": 2, "acao": "Gabo desce a escada alagada",
    "referencia": "docs/public/personagens/gabo.jpg", "ancora": "Gabo", "saida": "docs/public/cenas/capitulo_7/cena_2.jpg",
    "seed": 702, "titulo": "Capítulo 7", "enquadramento": "medium shot",
    "prompt": "prompt de teste", "elenco": [
        {"nome": "Gabo", "referencia": "docs/public/personagens/gabo.jpg",
         "vestuario": "sobretudo bege", "descricao": "Gabo: ..."},
    ],
}


def _entrada(tmp_path, nome="cena_2.jpg"):
    dados = dict(ENTRADA)
    dados["saida"] = nome
    return dados


class ProvedorFalso:
    """Dublê do provedor: grava o que o teste mandar, sem tocar em rede."""

    nome = "falso"

    def __init__(self, pintor):
        self.pintor = pintor
        self.chamadas = 0

    def gerar(self, entrada, referencias, destino):
        self.chamadas += 1
        self.pintor(destino)
        return True


def _boa(caminho):
    gerador = np.random.default_rng(7)
    Image.fromarray(gerador.integers(0, 255, (768, 1376, 3)).astype("uint8")).save(
        caminho, quality=92
    )


def _ruim(caminho):
    Image.fromarray(np.full((768, 1376, 3), 40, dtype="uint8")).save(caminho, quality=92)


def test_pendentes_ignora_o_que_ja_existe(tmp_path, monkeypatch):
    monkeypatch.setattr(lote_cenas, "REPO_ROOT", tmp_path)
    (tmp_path / "existe.jpg").touch()
    manifesto = [{"saida": "existe.jpg"}, {"saida": "falta.jpg"}]
    assert lote_cenas.pendentes(manifesto, set()) == [{"saida": "falta.jpg"}]


def test_pendentes_traz_de_volta_a_cena_reprovada(tmp_path, monkeypatch):
    monkeypatch.setattr(lote_cenas, "REPO_ROOT", tmp_path)
    (tmp_path / "existe.jpg").touch()
    manifesto = [{"saida": "existe.jpg"}]
    assert lote_cenas.pendentes(manifesto, {"existe.jpg"}) == manifesto


def test_briefing_traz_saida_referencia_e_prompt():
    texto = lote_cenas.briefing([ENTRADA])
    assert "docs/public/cenas/capitulo_7/cena_2.jpg" in texto
    assert "docs/public/personagens/gabo.jpg" in texto
    assert "prompt de teste" in texto


def test_runner_aprova_imagem_que_passa_no_portao(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(runner, "PAUSA_SEGUNDOS", 0)
    provedor = ProvedorFalso(_boa)
    assert runner.gerar_uma(provedor, _entrada(tmp_path), tentativas=2, com_visao=False) is None
    assert (tmp_path / "cena_2.jpg").exists()
    assert provedor.chamadas == 1


def test_runner_apaga_o_refugo_e_desiste(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(runner, "PAUSA_SEGUNDOS", 0)
    provedor = ProvedorFalso(_ruim)
    motivos = runner.gerar_uma(provedor, _entrada(tmp_path), tentativas=2, com_visao=False)
    assert provedor.chamadas == 2
    assert motivos and any("contraste" in m for m in motivos)
    # Regra 6 protege arte aprovada; imagem reprovada não pode ficar ocupando a cena.
    assert not (tmp_path / "cena_2.jpg").exists()


def test_runner_reprova_quando_a_visao_acusa_troca_de_fisionomia(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(runner, "PAUSA_SEGUNDOS", 0)
    monkeypatch.setattr(gemini, "cliente", lambda: object())
    monkeypatch.setattr(fidelidade, "auditar", lambda *a, **k: {
        "fiel": False,
        "personagens": [{"nome": "Val", "confere": False, "motivo": "cabelo rosa"}],
    })
    motivos = runner.gerar_uma(ProvedorFalso(_boa), _entrada(tmp_path),
                               tentativas=1, com_visao=True)
    assert motivos == ["Val fora do canônico: cabelo rosa"]


def test_fidelidade_traduz_o_veredito_do_modelo():
    veredito = {"personagens": [{"nome": "Gabo", "confere": True}],
                "texto_na_imagem": True}
    assert fidelidade.reprovacoes(veredito) == ["texto queimado na imagem"]
    assert fidelidade.reprovacoes({}) == []


def test_pergunta_de_fidelidade_nomeia_personagens_e_roupa():
    pergunta = fidelidade.montar_pergunta(ENTRADA["elenco"])
    assert "Gabo" in pergunta and "sobretudo bege" in pergunta
    assert "JSON" in pergunta


def test_sem_chave_o_cliente_nao_e_criado(monkeypatch):
    for nome in gemini.CHAVES:
        monkeypatch.delenv(nome, raising=False)
    assert gemini.cliente() is None


def test_pollinations_usa_kontext_com_o_retrato_da_ancora():
    url = provedores.ProvedorPollinations(intervalo=0).url(ENTRADA)
    assert url.startswith(provedores.POLLINATIONS_URL)
    assert "model=kontext" in url
    assert "seed=702" in url
    assert "width=1376" in url and "height=768" in url
    # O Kontext lê a referência por URL pública: o repositório é público, o raw serve.
    assert "docs%2Fpublic%2Fpersonagens%2Fgabo.jpg" in url


def test_pollinations_cai_para_flux_quando_a_cena_nao_tem_ancora():
    sem_ancora = dict(ENTRADA, referencia=None, ancora=None, elenco=[])
    url = provedores.ProvedorPollinations(intervalo=0).url(sem_ancora)
    assert "model=flux" in url and "image=" not in url


def test_prompt_curto_cabe_na_url_e_mantem_as_travas():
    curto = provedores.prompt_curto(ENTRADA)
    assert len(curto) <= 1100
    assert ENTRADA["enquadramento"] in curto
    assert ENTRADA["acao"] in curto
    assert "sobretudo bege" in curto           # vestuário obrigatório sobrevive ao corte
    assert "Do not render any text" in curto   # proibição de texto sobrevive ao corte


def test_pollinations_respeita_o_intervalo_do_tier(monkeypatch):
    dormiu = []
    monkeypatch.setattr(provedores.time, "sleep", dormiu.append)
    provedor = provedores.ProvedorPollinations(intervalo=15)
    provedor._esperar()
    provedor._esperar()
    assert dormiu and dormiu[-1] > 14


def test_escolher_cai_no_pollinations_sem_chave(monkeypatch):
    monkeypatch.setattr(provedores.gemini, "cliente", lambda: None)
    assert provedores.escolher("auto").nome == "pollinations"

"""Fila em lotes e o runner que gera, homologa e desiste sem deixar refugo no disco."""

import numpy as np
from PIL import Image

from scripts import gerar_cenas_manifesto as runner
from scripts import lote_cenas
from scripts.art_gen import fidelidade, gemini, provedores, provedores_livres

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

    trava_identidade = True

    def __init__(self, pintor):
        self.pintor = pintor
        self.chamadas = 0

    def disponivel(self):
        return True

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
    # O Kontext ficou atrás do cadastro (sonda de 18/08 no CI): só com token.
    url = provedores.ProvedorPollinations(intervalo=0, token="secreto").url(ENTRADA)
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


def test_pollinations_sem_token_nao_promete_travar_fisionomia():
    provedor = provedores.ProvedorPollinations(intervalo=0, token=None)
    assert provedor.trava_identidade is False
    # Sem Kontext não adianta mandar a referência: o endpoint público devolve 500.
    assert "model=flux" in provedor.url(ENTRADA)


def test_cena_com_retrato_nao_desce_para_provedor_que_inventa_rosto(tmp_path):
    class SemAncora:
        nome = "texto_puro"
        trava_identidade = False

        def disponivel(self):
            return True

        def gerar(self, *a):
            raise AssertionError("cena com retrato não pode cair aqui sem permissão")

    cadeia = provedores.ProvedorCadeia([SemAncora()], permitir_sem_ancora=False)
    assert cadeia.gerar(ENTRADA, [], tmp_path / "cena_1.jpg") is False


def test_cena_sem_retrato_pode_usar_qualquer_provedor(tmp_path):
    usado = ProvedorFalso(_boa)
    usado.trava_identidade = False
    ambiente = dict(ENTRADA, referencia=None, ancora=None, elenco=[])
    assert provedores.ProvedorCadeia([usado]).gerar(
        ambiente, [], tmp_path / "cena_1.jpg"
    ) is True


def test_queda_permitida_marca_a_cena_para_refazer(tmp_path):
    usado = ProvedorFalso(_boa)
    usado.trava_identidade = False
    cadeia = provedores.ProvedorCadeia([usado], permitir_sem_ancora=True)
    assert cadeia.gerar(ENTRADA, [], tmp_path / "cena_1.jpg") is True
    assert cadeia.sem_ancora == [ENTRADA["saida"]]


def test_prompt_curto_cabe_na_url_e_mantem_as_travas():
    curto = provedores.prompt_curto(ENTRADA)
    assert len(curto) <= 1100
    assert ENTRADA["enquadramento"] in curto
    assert ENTRADA["acao"] in curto
    assert "sobretudo bege" in curto           # vestuário obrigatório sobrevive ao corte
    assert "Do not render any text" in curto   # proibição de texto sobrevive ao corte


def test_pollinations_respeita_o_intervalo_do_tier(monkeypatch):
    dormiu = []
    monkeypatch.setattr(provedores_livres.time, "sleep", dormiu.append)
    provedor = provedores.ProvedorPollinations(intervalo=15)
    provedor._esperar()
    provedor._esperar()
    assert dormiu and dormiu[-1] > 14


def test_cadeia_pula_o_elo_indisponivel_e_usa_o_seguinte(tmp_path):
    class Indisponivel:
        nome = "morto"
        trava_identidade = True

        def disponivel(self):
            return False

        def gerar(self, *a):
            raise AssertionError("elo indisponível não pode ser chamado")

    usado = ProvedorFalso(_boa)
    cadeia = provedores.ProvedorCadeia([Indisponivel(), usado])
    assert cadeia.gerar(ENTRADA, [], tmp_path / "cena_1.jpg") is True
    assert usado.chamadas == 1


def test_cadeia_cai_para_o_proximo_quando_o_elo_falha(tmp_path):
    class Falha:
        nome = "falha"
        trava_identidade = True

        def disponivel(self):
            return True

        def gerar(self, *a):
            return False

    usado = ProvedorFalso(_boa)
    assert provedores.ProvedorCadeia([Falha(), usado]).gerar(
        ENTRADA, [], tmp_path / "cena_1.jpg"
    ) is True
    assert usado.chamadas == 1


def test_escolher_sem_chave_ainda_devolve_provedor(monkeypatch):
    monkeypatch.setattr(provedores.gemini, "cliente", lambda: None)
    # Sem chave a cadeia continua de pé: o Pollinations não exige cadastro.
    assert provedores.escolher("auto").disponivel()
    assert provedores.escolher("pollinations").nome == "pollinations"


def test_provedor_pedido_sem_credencial_falha_com_mensagem(monkeypatch):
    import pytest

    monkeypatch.setattr(provedores.gemini, "cliente", lambda: None)
    with pytest.raises(SystemExit, match="indisponível"):
        provedores.escolher("gemini")


def test_quota_estourada_tira_o_elo_da_rodada_sem_derrubar(tmp_path):
    class SemQuota:
        nome = "sem_quota"
        trava_identidade = True
        esgotado = False

        def disponivel(self):
            return not self.esgotado

        def gerar(self, *a):
            raise RuntimeError("429 RESOURCE_EXHAUSTED: quota exceeded, limit: 0")

    morto, vivo = SemQuota(), ProvedorFalso(_boa)
    cadeia = provedores.ProvedorCadeia([morto, vivo])
    assert cadeia.gerar(ENTRADA, [], tmp_path / "cena_1.jpg") is True
    # O 429 nao pode subir: ele tira o elo da rodada e a cena sai pelo provedor de baixo.
    assert morto.esgotado is True
    assert vivo.chamadas == 1


def test_erro_comum_do_provedor_nao_esgota_o_elo(tmp_path):
    class Instavel:
        nome = "instavel"
        trava_identidade = True
        esgotado = False

        def disponivel(self):
            return not self.esgotado

        def gerar(self, *a):
            raise ConnectionError("conexão caiu no meio")

    instavel = Instavel()
    cadeia = provedores.ProvedorCadeia([instavel, ProvedorFalso(_boa)])
    assert cadeia.gerar(ENTRADA, [], tmp_path / "cena_1.jpg") is True
    # Falha de rede é episódica: o elo continua na fila para a próxima cena.
    assert instavel.esgotado is False

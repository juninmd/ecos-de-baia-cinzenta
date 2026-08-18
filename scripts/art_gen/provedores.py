"""Provedores de imagem: de onde a cena sai, sem amarrar a fila a um fornecedor só.

O Gemini dá a melhor fidelidade (aceita o retrato de todos os personagens da cena), mas
depende de chave e de quota. O Pollinations expõe o FLUX Kontext de graça e sem cadastro
— e Kontext é exatamente o image-to-image que a regra 1 do AGENTS.md pede. Ter os dois
atrás da mesma interface é o que permite virar a chave sem reescrever o runner.
"""

import os
import time
import urllib.parse
from pathlib import Path
from typing import List, Optional

from scripts.art_gen import gemini

LARGURA = 1376
ALTURA = 768
POLLINATIONS_URL = "https://image.pollinations.ai/prompt/"
# O retrato precisa de URL pública para o Kontext: o repositório é público, então o raw
# do GitHub serve. Trocar de fork/branch é só mudar a variável de ambiente.
BASE_RETRATOS = os.environ.get(
    "CENAS_REF_BASE_URL",
    "https://raw.githubusercontent.com/juninmd/ecos-de-baia-cinzenta/master/",
)
# Tarifa do tier anônimo: uma imagem a cada 15 s. Com cadastro grátis (tier Seed) cai
# para 5 s — daí o intervalo ser configurável em vez de constante.
INTERVALO_PADRAO = float(os.environ.get("POLLINATIONS_INTERVALO", "15"))


class ProvedorGemini:
    """Melhor fidelidade: manda o prompt inteiro e o retrato de todo o elenco."""

    nome = "gemini"

    def __init__(self):
        self.cliente = gemini.cliente()

    def disponivel(self) -> bool:
        return self.cliente is not None

    def gerar(self, entrada: dict, referencias: List[Path], destino: Path) -> bool:
        return gemini.gerar_imagem(self.cliente, entrada["prompt"], referencias, destino)


class ProvedorPollinations:
    """FLUX Kontext de graça: image-to-image a partir do retrato canônico da âncora.

    O Kontext recebe um retrato só, então a identidade travada é a da âncora — os demais
    personagens continuam vindo por descrição, que é a degradação já prevista na regra 7.
    """

    nome = "pollinations"

    def __init__(self, intervalo: float = INTERVALO_PADRAO, token: Optional[str] = None):
        self.intervalo = intervalo
        self.token = token or os.environ.get("POLLINATIONS_TOKEN")
        self._ultimo = 0.0

    def disponivel(self) -> bool:
        return True  # sem chave obrigatória: é o piso da cadeia de fallback

    def _esperar(self) -> None:
        atraso = self.intervalo - (time.monotonic() - self._ultimo)
        if atraso > 0:
            time.sleep(atraso)
        self._ultimo = time.monotonic()

    def url(self, entrada: dict) -> str:
        prompt = urllib.parse.quote(prompt_curto(entrada), safe="")
        parametros = {
            "width": LARGURA,
            "height": ALTURA,
            "seed": entrada["seed"],
            "nologo": "true",
            "safe": "false",
            "referrer": "ecos-de-baia-cinzenta",
        }
        if entrada.get("referencia"):
            parametros["model"] = "kontext"
            parametros["image"] = BASE_RETRATOS + entrada["referencia"]
        else:
            parametros["model"] = "flux"
        return POLLINATIONS_URL + prompt + "?" + urllib.parse.urlencode(parametros)

    def gerar(self, entrada: dict, referencias: List[Path], destino: Path) -> bool:
        import requests
        from PIL import Image

        from scripts.art_gen.arquivo import salvar_jpeg

        self._esperar()
        cabecalhos = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        resposta = requests.get(self.url(entrada), headers=cabecalhos, timeout=180)
        if resposta.status_code != 200 or not resposta.content:
            print(f"   ⚠️ pollinations respondeu {resposta.status_code}")
            return False
        import io

        salvar_jpeg(Image.open(io.BytesIO(resposta.content)), destino)
        return destino.exists()


def prompt_curto(entrada: dict, limite: int = 1100) -> str:
    """Versão enxuta do prompt, para provedores que recebem tudo pela URL.

    Com image-to-image o descritor canônico vira redundância cara: a identidade já vem
    na imagem de referência. O que não pode cair é o que a imagem não carrega — ação,
    enquadramento, vestuário, fase do capítulo e a proibição de texto.
    """
    from scripts.art_gen import prompt_cena, vestuario
    from scripts.art_gen import continuidade

    partes = [entrada["enquadramento"], entrada["acao"]]
    if entrada.get("ancora"):
        partes.append(f"the person in the reference photo, {entrada['ancora']}")
    texto = ". ".join(p for p in partes if p)
    texto += vestuario.reforco(entrada.get("elenco", []))
    texto += continuidade.clausula(entrada.get("elenco", []), float(entrada["capitulo"]))
    texto += ". " + prompt_cena.ESTILO + " " + prompt_cena.SEM_TEXTO
    return texto[:limite]


def escolher(nome: str = "auto"):
    """Provedor pedido, ou o primeiro disponível na ordem de fidelidade."""
    if nome == "gemini":
        return ProvedorGemini()
    if nome == "pollinations":
        return ProvedorPollinations()
    for provedor in (ProvedorGemini(), ProvedorPollinations()):
        if provedor.disponivel():
            return provedor
    raise SystemExit("❌ nenhum provedor de imagem disponível")

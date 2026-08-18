"""Os dois provedores que não custam nada — a base da cadeia de fallback.

Ambos rodam FLUX Kontext, que é o image-to-image que a regra 1 do AGENTS.md elege para
travar fisionomia. A diferença é o pedágio: o Space do ZeroGPU tem cota diária e fila,
mas aceita o retrato como arquivo local; o Pollinations não tem cota nem cadastro, mas
lê a referência por URL e cobra 15 s entre chamadas.
"""

import os
import time
import urllib.parse
from pathlib import Path
from typing import List, Optional

LARGURA = 1376
ALTURA = 768
POLLINATIONS_URL = "https://image.pollinations.ai/prompt/"
# O retrato precisa de URL pública para o Kontext do Pollinations: o repositório é
# público, então o raw do GitHub serve. Fork ou branch diferente é só trocar a variável.
BASE_RETRATOS = os.environ.get(
    "CENAS_REF_BASE_URL",
    "https://raw.githubusercontent.com/juninmd/ecos-de-baia-cinzenta/master/",
)
# Tarifa do tier anônimo: uma imagem a cada 15 s. Com cadastro grátis (tier Seed) cai
# para 5 s — daí o intervalo ser configurável em vez de constante.
INTERVALO_PADRAO = float(os.environ.get("POLLINATIONS_INTERVALO", "15"))


class ProvedorKontextSpace:
    """FLUX.1-Kontext-Dev no ZeroGPU: melhor fidelidade entre os gratuitos.

    A cota diária acaba, e insistir depois disso só queima tempo de execução — por isso
    `disponivel()` passa a mentir para baixo assim que o Space acusa quota esgotada.
    """

    nome = "kontext_space"

    def disponivel(self) -> bool:
        from scripts.daily_telegram import hf_space

        try:
            import gradio_client  # noqa: F401
        except ImportError:
            return False
        return not hf_space.quota_exhausted(hf_space.KONTEXT_SPACE)

    def gerar(self, entrada: dict, referencias: List[Path], destino: Path) -> bool:
        from scripts.art_gen.provedores import prompt_curto
        from scripts.daily_telegram import hf_space

        if not referencias:
            return False
        resultado = hf_space.edit_with_identity(
            reference=referencias[0],
            prompt=prompt_curto(entrada),
            output_path=destino,
            seed=entrada["seed"],
        )
        return resultado is not None and destino.exists()


class ProvedorPollinations:
    """Kontext sem chave e sem cadastro: o piso da cadeia, sempre disponível."""

    nome = "pollinations"

    def __init__(self, intervalo: float = INTERVALO_PADRAO, token: Optional[str] = None):
        self.intervalo = intervalo
        self.token = token or os.environ.get("POLLINATIONS_TOKEN")
        self._ultimo = 0.0

    def disponivel(self) -> bool:
        return True

    def _esperar(self) -> None:
        atraso = self.intervalo - (time.monotonic() - self._ultimo)
        if atraso > 0:
            time.sleep(atraso)
        self._ultimo = time.monotonic()

    def url(self, entrada: dict) -> str:
        from scripts.art_gen.provedores import prompt_curto

        prompt = urllib.parse.quote(prompt_curto(entrada), safe="")
        parametros = {
            "width": LARGURA,
            "height": ALTURA,
            "seed": entrada["seed"],
            "nologo": "true",
            "referrer": "ecos-de-baia-cinzenta",
        }
        if entrada.get("referencia"):
            parametros["model"] = "kontext"
            parametros["image"] = BASE_RETRATOS + entrada["referencia"]
        else:
            parametros["model"] = "flux"
        return POLLINATIONS_URL + prompt + "?" + urllib.parse.urlencode(parametros)

    def gerar(self, entrada: dict, referencias: List[Path], destino: Path) -> bool:
        import io

        import requests
        from PIL import Image

        from scripts.art_gen.arquivo import salvar_jpeg

        self._esperar()
        cabecalhos = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        try:
            resposta = requests.get(self.url(entrada), headers=cabecalhos, timeout=120)
        except requests.RequestException as exc:
            print(f"   ⚠️ pollinations falhou: {type(exc).__name__}")
            return False
        if resposta.status_code != 200 or not resposta.content:
            print(f"   ⚠️ pollinations respondeu {resposta.status_code}")
            return False
        salvar_jpeg(Image.open(io.BytesIO(resposta.content)), destino)
        return destino.exists()

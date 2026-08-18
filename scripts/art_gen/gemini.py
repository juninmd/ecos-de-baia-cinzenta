"""Cliente mínimo do Gemini para arte de cena: gerar imagem e julgar imagem.

O repositório já tinha a chamada de geração dentro do `nano_banana_gen.py`, misturada com
cálculo de custo e leitura de capítulo. Aqui ela fica isolada, para o runner do manifesto
e o portão de fidelidade usarem a mesma porta.
"""

import io
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional

MODELO_IMAGEM = os.environ.get("NANO_BANANA_IMAGE_MODEL", "gemini-2.5-flash-image")
MODELO_VISAO = os.environ.get("NANO_BANANA_VISION_MODEL", "gemini-2.5-flash")
CHAVES = ("NANO_BANANA_API_KEY_IMAGE", "NANO_BANANA_API_KEY", "GEMINI_API_KEY",
          "GOOGLE_API_KEY")
JSON_RE = re.compile(r"\{.*\}", re.DOTALL)


def chave() -> Optional[str]:
    """Primeira chave disponível — o projeto usa nomes diferentes por script."""
    return next((os.environ[n] for n in CHAVES if os.environ.get(n)), None)


def cliente():
    """Cliente do google-genai, ou None quando não há chave/biblioteca no ambiente."""
    if not chave():
        return None
    try:
        from google import genai
    except ImportError:
        return None
    return genai.Client(api_key=chave())


def _anexos(caminhos: List[Path]) -> List:
    from PIL import Image

    anexos = []
    for caminho in caminhos:
        try:
            anexos.append(Image.open(caminho))
        except Exception:
            continue
    return anexos


def gerar_imagem(cliente_genai, prompt: str, referencias: List[Path], destino: Path) -> bool:
    """Grava a imagem em `destino`. Só devolve True quando o arquivo existe de fato."""
    from PIL import Image

    resposta = cliente_genai.models.generate_content(
        model=MODELO_IMAGEM, contents=[prompt] + _anexos(referencias)
    )
    for parte in getattr(resposta, "parts", None) or []:
        dados = getattr(parte, "inline_data", None)
        if not dados:
            continue
        from scripts.art_gen.arquivo import salvar_jpeg

        salvar_jpeg(Image.open(io.BytesIO(dados.data)), destino)
        return destino.exists()
    return False


def perguntar_json(cliente_genai, pergunta: str, imagens: List[Path]) -> Dict:
    """Resposta do modelo já em dicionário; `{}` quando ele não devolve JSON."""
    resposta = cliente_genai.models.generate_content(
        model=MODELO_VISAO, contents=[pergunta] + _anexos(imagens)
    )
    casou = JSON_RE.search(resposta.text or "")
    if not casou:
        return {}
    try:
        return json.loads(casou.group())
    except json.JSONDecodeError:
        return {}

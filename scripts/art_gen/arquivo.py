"""Gravação das cenas em disco — o peso do acervo é decidido aqui.

Dez cenas por capítulo são 2.350 arquivos versionados no git. As imagens antigas foram
salvas sem otimização e ficaram em 810 KB cada; com `optimize` e JPEG progressivo, a
mesma imagem, na mesma qualidade visual, cai para ~240 KB. Na escala da obra isso é a
diferença entre 1,9 GB e 0,55 GB de repositório.
"""

import os
from pathlib import Path

from PIL import Image

QUALIDADE = int(os.environ.get("CENAS_JPEG_QUALIDADE", "88"))


def salvar_jpeg(imagem: Image.Image, destino: Path, qualidade: int = QUALIDADE) -> Path:
    destino.parent.mkdir(parents=True, exist_ok=True)
    imagem.convert("RGB").save(
        destino, "JPEG", quality=qualidade, optimize=True, progressive=True
    )
    return destino

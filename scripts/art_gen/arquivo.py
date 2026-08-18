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


LARGURA_CENA = 1376
ALTURA_CENA = 768
# Cinza-chumbo em vez de preto: fundo preto puro faz o Kontext tratar a borda como
# vinheta e devolver a cena centralizada num buraco escuro.
FUNDO = (26, 28, 32)


def tela_cinematografica(retrato: Path, destino: Path) -> Path:
    """Encaixa o retrato canônico numa tela 16:9, para o Kontext pintar em 16:9.

    O FLUX Kontext devolve a imagem na proporção que recebe, e os retratos do dossiê são
    1:1, 0,68 ou 1,83 — nenhum deles é o quadro cinematográfico das cenas. Mandar o
    retrato cru fazia a cena nascer quadrada e reprovar no portão por proporção e por
    altura. Sobra de tela também dá ao modelo o espaço onde ele vai pintar o cenário.
    """
    with Image.open(retrato) as imagem:
        original = imagem.convert("RGB")
        escala = min(LARGURA_CENA / original.width, ALTURA_CENA / original.height)
        reduzido = original.resize(
            (max(1, int(original.width * escala)), max(1, int(original.height * escala))),
            Image.LANCZOS,
        )
    tela = Image.new("RGB", (LARGURA_CENA, ALTURA_CENA), FUNDO)
    tela.paste(reduzido, ((LARGURA_CENA - reduzido.width) // 2,
                          (ALTURA_CENA - reduzido.height) // 2))
    return salvar_jpeg(tela, destino, qualidade=95)

"""Medidas objetivas de uma imagem de cena — o que reprova sozinho e o que só alerta.

Homologar 2.350 imagens no olho é inviável, e o defeito típico da geração em lote não é
sutil: quadro chapado, imagem borrada, texto queimado no canto, ou a mesma foto repetida
em dez cenas. Tudo isso é medível com Pillow + numpy, que o projeto já usa.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from PIL import Image

LARGURA_MIN = 1024
ALTURA_MIN = 576
PROPORCAO_MIN = 1.25
PROPORCAO_MAX = 2.10
# Calibrados sobre as 118 cenas canônicas já publicadas (medidas em docs/qualidade_imagens.md):
# nitidez mínima observada 166, contraste 21,3, faixa de texto mediana 1,6.
# O corte de bytes é o único que não sai dali: aquelas imagens foram gravadas sem
# otimização, a 810 KB. No padrão atual (optimize + progressivo) a mesma cena dá ~240 KB
# e o Kontext do ZeroGPU devolve ~83 KB. O que precisa reprovar é quadro vazio, e esse
# mede 6 KB chapado, 14 KB em gradiente puro — daí o piso ficar em 40 KB.
BYTES_MIN = 40_000
NITIDEZ_MIN = 120.0
CONTRASTE_MIN = 18.0
DISTANCIA_DUPLICATA = 6
# As duas imagens do acervo acima de 2,3 tinham mesmo texto queimado ("CHAPTER 9", "ERROR CODE").
FAIXA_TEXTO_MIN = 2.3


@dataclass
class Medida:
    """Métricas cruas de uma imagem; a decisão de aprovar fica em `avaliar`."""
    largura: int
    altura: int
    bytes: int
    nitidez: float
    contraste: float
    faixa_texto: float
    hash_visual: int

    @property
    def proporcao(self) -> float:
        return self.largura / self.altura if self.altura else 0.0


def _luma(imagem: Image.Image) -> np.ndarray:
    return np.asarray(imagem.convert("L"), dtype=np.float32)


def nitidez(luma: np.ndarray) -> float:
    """Variância do laplaciano: imagem borrada tem pouca energia de alta frequência."""
    laplaciano = (
        -4 * luma[1:-1, 1:-1]
        + luma[:-2, 1:-1] + luma[2:, 1:-1]
        + luma[1:-1, :-2] + luma[1:-1, 2:]
    )
    return float(laplaciano.var())


def faixa_de_texto(luma: np.ndarray) -> float:
    """Quanto a linha mais "letrada" da imagem destoa das demais.

    Legenda e título queimados são faixas horizontais estreitas com muito mais borda
    vertical que o resto do quadro. A medida é a razão entre o pico e a mediana das
    linhas — só alerta, nunca reprova sozinha, porque grade de neon também pontua.
    """
    bordas = np.abs(np.diff(luma, axis=1))
    por_linha = bordas.mean(axis=1)
    if por_linha.size < 16:
        return 0.0
    mediana = float(np.median(por_linha))
    return float(por_linha.max() / mediana) if mediana > 0.1 else 0.0


def hash_visual(imagem: Image.Image) -> int:
    """dHash de 64 bits: compara composição, não pixels — sobrevive ao JPEG."""
    reduzida = np.asarray(
        imagem.convert("L").resize((9, 8), Image.LANCZOS), dtype=np.int16
    )
    bits = (reduzida[:, 1:] > reduzida[:, :-1]).flatten()
    valor = 0
    for bit in bits:
        valor = (valor << 1) | int(bit)
    return valor


def distancia(a: int, b: int) -> int:
    return bin(a ^ b).count("1")


def medir(caminho: Path) -> Medida:
    with Image.open(caminho) as imagem:
        imagem.load()
        luma = _luma(imagem)
        return Medida(
            largura=imagem.width,
            altura=imagem.height,
            bytes=caminho.stat().st_size,
            nitidez=nitidez(luma),
            contraste=float(luma.std()),
            faixa_texto=faixa_de_texto(luma),
            hash_visual=hash_visual(imagem),
        )


def avaliar(medida: Medida) -> Tuple[List[str], List[str]]:
    """(reprovações, alertas) — reprovação manda a cena de volta para a fila."""
    reprovas, alertas = [], []
    if medida.largura < LARGURA_MIN or medida.altura < ALTURA_MIN:
        reprovas.append(f"resolução {medida.largura}x{medida.altura} abaixo de "
                        f"{LARGURA_MIN}x{ALTURA_MIN}")
    if not PROPORCAO_MIN <= medida.proporcao <= PROPORCAO_MAX:
        reprovas.append(f"proporção {medida.proporcao:.2f} fora do quadro cinematográfico")
    if medida.bytes < BYTES_MIN:
        reprovas.append(f"arquivo de {medida.bytes // 1024} KB: provável quadro chapado")
    if medida.nitidez < NITIDEZ_MIN:
        reprovas.append(f"nitidez {medida.nitidez:.1f} abaixo de {NITIDEZ_MIN}")
    if medida.contraste < CONTRASTE_MIN:
        reprovas.append(f"contraste {medida.contraste:.1f} abaixo de {CONTRASTE_MIN}")
    if medida.faixa_texto >= FAIXA_TEXTO_MIN:
        alertas.append(f"faixa horizontal suspeita de texto queimado "
                       f"({medida.faixa_texto:.1f}x a mediana)")
    return reprovas, alertas


def duplicatas(hashes: Dict[str, int], limite: int = DISTANCIA_DUPLICATA) -> List[Tuple[str, str, int]]:
    """Pares visualmente iguais dentro do conjunto avaliado."""
    itens = sorted(hashes.items())
    pares = []
    for i, (nome_a, hash_a) in enumerate(itens):
        for nome_b, hash_b in itens[i + 1:]:
            dist = distancia(hash_a, hash_b)
            if dist <= limite:
                pares.append((nome_a, nome_b, dist))
    return pares


def carregar(caminho: Path) -> Optional[Medida]:
    """Medida da imagem, ou None quando o arquivo não abre (JPEG truncado)."""
    try:
        return medir(caminho)
    except Exception:
        return None

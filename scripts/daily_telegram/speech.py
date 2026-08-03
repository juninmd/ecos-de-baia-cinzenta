"""Fala sintetizada por personagem via edge-tts (grátis, sem chave)."""
import asyncio
import subprocess
from pathlib import Path
from typing import Optional

from scripts.daily_telegram import voices

MIN_BYTES = 512


def _probe(media: Path) -> float:
    resultado = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(media)],
        capture_output=True, text=True,
    )
    if resultado.returncode != 0:
        raise RuntimeError(f"ffprobe falhou: {resultado.stderr.strip()[-160:]}")
    return float(resultado.stdout.strip())


async def _sintetizar(texto: str, voz: str, rate: str, pitch: str, destino: Path) -> None:
    import edge_tts

    comunicado = edge_tts.Communicate(texto, voz, rate=rate, pitch=pitch)
    await comunicado.save(str(destino))


def say(texto: str, personagem: Optional[dict], destino: Path) -> Optional[float]:
    """Gera a fala e devolve a duração — é ela que define o tempo da imagem em cena."""
    if destino.exists() and destino.stat().st_size > MIN_BYTES:
        return _probe(destino)  # cache: não re-sintetiza fala já gerada

    voz, rate, pitch = voices.for_character(personagem)
    destino.parent.mkdir(parents=True, exist_ok=True)
    try:
        asyncio.run(_sintetizar(texto, voz, rate, pitch, destino))
    except BaseException as exc:
        print(f"⚠ edge-tts falhou ({type(exc).__name__}): {str(exc)[:120]}")
        return None
    if not destino.exists() or destino.stat().st_size <= MIN_BYTES:
        print("⚠ edge-tts devolveu áudio vazio")
        return None
    return _probe(destino)

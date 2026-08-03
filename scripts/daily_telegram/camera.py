"""Movimentos de câmera 2D. Zoom sempre igual é o que faz um filme virar slideshow."""
import subprocess
from pathlib import Path
from typing import Optional

from scripts.daily_telegram import film

SIZE = "1280:720"
FPS = 30

MOVIMENTOS = (
    # (zoom, x, y) — %(d)s é substituído pela duração do plano
    ("min(1.25,1+0.0011*on)", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),                      # push-in
    ("max(1.02,1.25-0.0011*on)", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),                   # pull-out
    ("1.14", "(iw-iw/zoom)*on/(24*%(d)s)", "ih/2-(ih/zoom/2)"),                             # pan →
    ("1.14", "(iw-iw/zoom)*(1-on/(24*%(d)s))", "ih/2-(ih/zoom/2)"),                         # pan ←
    ("min(1.2,1+0.0008*on)", "iw/2-(iw/zoom/2)", "(ih-ih/zoom)*(1-on/(30*%(d)s))"),         # tilt ↑
    ("min(1.22,1+0.0009*on)", "(iw-iw/zoom)*on/(36*%(d)s)", "(ih-ih/zoom)*on/(40*%(d)s)"),  # diagonal
)


def ken_burns(imagem: Path, destino: Path, duracao: float, indice: int) -> Optional[Path]:
    """Plano com movimento de câmera, duração exata e micro fade nas pontas."""
    zoom, x, y = MOVIMENTOS[(indice // 100 + indice) % len(MOVIMENTOS)]
    subs = {"d": f"{max(duracao, 0.5):.2f}"}
    # d=1: cada frame de entrada vira um de saída. Com d>1 e imagem em loop, o zoompan
    # multiplica os frames e o clipe estoura para dezenas de minutos.
    filtro = (
        f"scale=2400:1350,zoompan=z='{zoom}':x='{x % subs}':y='{y % subs}':"
        f"d=1:s={SIZE.replace(':', 'x')}:fps={FPS},"
        f"{film.fade_filter(duracao)},format=yuv420p"
    )
    # -framerate 30 na entrada: sem isso o loop entra a 25fps e o clipe sai mais curto.
    resultado = subprocess.run(
        ["ffmpeg", "-y", "-loop", "1", "-framerate", str(FPS), "-t", str(duracao),
         "-i", str(imagem), "-vf", filtro, "-c:v", "libx264", "-preset", "veryfast",
         str(destino)],
        capture_output=True, text=True,
    )
    if resultado.returncode != 0:
        print(f"⚠ ffmpeg (câmera) falhou: {resultado.stderr.strip()[-200:]}")
        return None
    return destino

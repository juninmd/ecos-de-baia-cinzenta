"""Monta o vídeo narrado de um capítulo com as cenas canônicas já aprovadas.

Diferente de `scripts/video_gen/main.py`, que usa uma imagem só (a capa do frontmatter)
e trunca a narração em 3000 caracteres, aqui entra o capítulo inteiro e as três cenas
de `docs/public/cenas/capitulo_<N>/`, que são as imagens auditadas contra a Regra Zero.

Uso: python -m scripts.video_capitulo 1
"""

import asyncio
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts.daily_telegram import voices  # noqa: E402
from scripts.daily_telegram.video import clean_for_tts, probe_duration  # noqa: E402
from scripts.generate_missing_scenes import (  # noqa: E402
    extract_chapter_title_and_clean_text,
)

SAIDA = REPO_ROOT / "docs" / "public" / "videos"
TEMP = REPO_ROOT / ".temp_video"
LARGURA, ALTURA, FPS = 1280, 720, 30
# Um plano de ~45s por imagem: mais que isso o olho cansa, menos que isso a narração
# fica picotada demais para só três cenas cobrirem o capítulo inteiro.
SEGUNDOS_POR_PLANO = 45


async def _falar(texto: str, destino: Path) -> None:
    import edge_tts

    voz, rate, pitch = voices.NARRADOR
    await edge_tts.Communicate(texto, voz, rate=rate, pitch=pitch).save(str(destino))


def narrar(texto: str, destino: Path) -> float:
    """Narração na voz canônica do Gabo — o mesmo timbre do elenco de áudio."""
    asyncio.run(_falar(clean_for_tts(texto), destino))
    return probe_duration(destino)


def plano(imagem: Path, duracao: float, indice: int, destino: Path) -> Path:
    """Ken Burns alternando zoom-in e zoom-out para os planos não se repetirem."""
    quadros = int(duracao * FPS)
    if indice % 2 == 0:
        zoom = f"min(1.25,1+0.0009*on)"
        pos = "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
    else:
        zoom = f"max(1.02,1.25-0.0009*on)"
        pos = "x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*0.35'"
    filtro = (
        f"scale={LARGURA*3}:{ALTURA*3},"
        f"zoompan=z='{zoom}':{pos}:d={quadros}:s={LARGURA}x{ALTURA}:fps={FPS},"
        f"noise=alls=6:allf=t+u,format=yuv420p"
    )
    subprocess.run(
        ["ffmpeg", "-y", "-loop", "1", "-i", str(imagem), "-vf", filtro,
         "-t", f"{duracao:.2f}", "-c:v", "libx264", "-preset", "veryfast",
         "-crf", "20", "-r", str(FPS), str(destino)],
        check=True, capture_output=True,
    )
    return destino


def montar(numero: int) -> Path:
    capitulo = REPO_ROOT / "docs" / f"capitulo-{numero}.md"
    cenas_dir = REPO_ROOT / "docs" / "public" / "cenas" / f"capitulo_{numero}"
    imagens = sorted(cenas_dir.glob("cena_[123].jpg"))
    if not imagens:
        raise SystemExit(f"sem cenas canônicas em {cenas_dir}")

    TEMP.mkdir(exist_ok=True)
    SAIDA.mkdir(parents=True, exist_ok=True)
    titulo, corpo = extract_chapter_title_and_clean_text(
        capitulo.read_text(encoding="utf-8")
    )
    print(f"🎬 {titulo} — {len(imagens)} cenas canônicas")

    voz = TEMP / f"cap{numero}_voz.mp3"
    duracao = narrar(corpo, voz)
    print(f"🎙️ narração: {duracao/60:.1f} min")

    total_planos = max(len(imagens), round(duracao / SEGUNDOS_POR_PLANO))
    por_plano = duracao / total_planos
    clipes = []
    for i in range(total_planos):
        # Cicla as imagens: com 3 cenas e 16 planos, cada uma reaparece com outro movimento.
        destino = TEMP / f"cap{numero}_plano{i:02d}.mp4"
        clipes.append(plano(imagens[i % len(imagens)], por_plano, i, destino))
        print(f"  plano {i+1}/{total_planos}: {imagens[i % len(imagens)].name}")

    lista = TEMP / f"cap{numero}_lista.txt"
    lista.write_text(
        "".join(f"file '{c.as_posix()}'\n" for c in clipes), encoding="utf-8"
    )
    mudo = TEMP / f"cap{numero}_mudo.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lista),
         "-c", "copy", str(mudo)], check=True, capture_output=True,
    )

    final = SAIDA / f"capitulo_{numero}.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(mudo), "-i", str(voz),
         "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-shortest", str(final)],
        check=True, capture_output=True,
    )
    print(f"✅ {final} ({final.stat().st_size/1024/1024:.1f} MB)")
    return final


if __name__ == "__main__":
    montar(int(sys.argv[1]) if len(sys.argv) > 1 else 1)

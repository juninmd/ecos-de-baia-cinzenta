import subprocess
from pathlib import Path
from typing import List, Optional

from scripts.daily_telegram import art, characters, hf_space
from scripts.daily_telegram.scenes import Scene

SIZE = "1280:720"
FPS = 30


def _run(cmd: List[str]) -> bool:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"⚠ ffmpeg falhou: {result.stderr.strip()[-200:]}")
        return False
    return True


def scene_image(cena: Scene, titulo: str, local: str, destino: Path, seed: int) -> Optional[Path]:
    """Identity-locked image when the scene has a character portrait; else text-to-image."""
    ancora = characters.pick_anchor(cena.personagens)
    if ancora:
        referencia = characters.reference_image(ancora)
        imagem = hf_space.edit_with_identity(
            referencia, cena.edit_prompt(ancora, local), destino, seed=seed
        )
        if imagem:
            return imagem
        print("↩ Fallback: geração sem referência de identidade.")
    return art.generate_image(cena.image_prompt(titulo, local), destino, seed=seed)


def _ken_burns(imagem: Path, destino: Path, duracao: float, indice: int) -> Optional[Path]:
    """Deterministic fallback motion: zoom + pan, direction varies per scene."""
    sinal = "+" if indice % 2 else "-"
    # d=1: cada frame de entrada vira um frame de saída. Com d>1 e imagem em loop,
    # o zoompan multiplica os frames e o vídeo estoura para dezenas de minutos.
    filtro = (
        f"scale=2200:1238,zoompan=z='min(1.2,1+0.0008*on)':"
        f"x='iw/2-(iw/zoom/2){sinal}sin(on/40)*18':"
        f"y='ih/2-(ih/zoom/2)+cos(on/45)*10':"
        f"d=1:s={SIZE.replace(':', 'x')}:fps={FPS},format=yuv420p"
    )
    # -framerate 30 na entrada: sem isso o loop entra a 25fps e o clipe sai mais curto.
    ok = _run(["ffmpeg", "-y", "-loop", "1", "-framerate", str(FPS), "-t", str(duracao),
               "-i", str(imagem), "-vf", filtro, "-c:v", "libx264", "-preset", "veryfast",
               str(destino)])
    return destino if ok else None


def _fit_duration(clipe: Path, destino: Path, duracao: float) -> Optional[Path]:
    """Ping-pong loop the short AI clip until it covers the scene duration."""
    filtro = f"[0:v]split[a][b];[b]reverse[r];[a][r]concat=n=2:v=1[pp];[pp]scale={SIZE},fps={FPS}[v]"
    ok = _run(["ffmpeg", "-y", "-stream_loop", "-1", "-i", str(clipe),
               "-filter_complex", filtro, "-map", "[v]", "-t", str(duracao),
               "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", str(destino)])
    return destino if ok else None


def scene_clip(imagem: Path, cena: Scene, duracao: float, temp_dir: Path, use_ai: bool) -> Optional[Path]:
    """Animated shot for one scene: real AI motion when possible, Ken Burns otherwise."""
    destino = temp_dir / f"clip_{cena.indice}.mp4"
    if use_ai:
        bruto = hf_space.image_to_video(
            imagem, cena.motion_prompt, temp_dir / f"ai_{cena.indice}.mp4", seed=cena.indice * 7
        )
        if bruto:
            ajustado = _fit_duration(bruto, destino, duracao)
            if ajustado:
                return ajustado
            print("↩ Fallback: não foi possível ajustar a duração do clipe de IA.")
    return _ken_burns(imagem, destino, duracao, cena.indice)


def stitch(clipes: List[Path], audio: Path, destino: Path, temp_dir: Path) -> Optional[Path]:
    """Concatenate the scene clips and lay the narration over them."""
    lista = temp_dir / "concat.txt"
    lista.write_text("".join(f"file '{c.absolute().as_posix()}'\n" for c in clipes), encoding="utf-8")
    mudo = temp_dir / "mudo.mp4"
    if not _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lista),
                 "-c", "copy", str(mudo)]):
        return None
    # crf 30 mantém o arquivo bem abaixo do limite de 50 MB do bot do Telegram
    ok = _run(["ffmpeg", "-y", "-stream_loop", "-1", "-i", str(mudo), "-i", str(audio),
               "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium",
               "-crf", "30", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
               "-shortest", str(destino)])
    return destino if ok else None

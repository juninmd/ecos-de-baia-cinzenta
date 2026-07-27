"""Movimento real: Stable Video Diffusion local, sem cota e sem fila."""
import subprocess
from pathlib import Path
from typing import Optional

MODELO = "stabilityai/stable-video-diffusion-img2vid-xt"
LARGURA, ALTURA = 1024, 576
FPS_SAIDA = 24

_pipe = None


def disponivel() -> bool:
    try:
        import torch

        return torch.cuda.is_available()
    except ImportError:
        return False


def _load():
    global _pipe
    if _pipe is not None:
        return _pipe

    import torch
    from diffusers import StableVideoDiffusionPipeline

    print("🎥 Carregando Stable Video Diffusion na GPU...")
    pipe = StableVideoDiffusionPipeline.from_pretrained(
        MODELO, torch_dtype=torch.float16, variant="fp16"
    )
    pipe.enable_model_cpu_offload()
    pipe.set_progress_bar_config(disable=True)
    _pipe = pipe
    return _pipe


def animar(imagem: Path, destino: Path, duracao: float, seed: int,
           frames: int = 25, motion: int = 90) -> Optional[Path]:
    """Anima a imagem e estica o clipe até cobrir a duração da fala.

    `motion_bucket_id` controla a intensidade do movimento: baixo demais fica parado,
    alto demais distorce o rosto — e rosto distorcido quebra a Regra Zero.
    """
    try:
        import torch
        from PIL import Image

        pipe = _load()
        origem = Image.open(imagem).convert("RGB").resize((LARGURA, ALTURA))
        gerador = torch.manual_seed(seed)
        quadros = pipe(
            origem, decode_chunk_size=4, generator=gerador,
            num_frames=frames, motion_bucket_id=motion, noise_aug_strength=0.02,
        ).frames[0]

        destino.parent.mkdir(parents=True, exist_ok=True)
        # PNG + ffmpeg em vez de export_to_video: aquele exige cv2/imageio instalados,
        # e perder 5 minutos de GPU por causa de codec ausente é caro demais.
        pasta = destino.with_name(f"{destino.stem}_frames")
        pasta.mkdir(parents=True, exist_ok=True)
        for i, quadro in enumerate(quadros):
            quadro.save(pasta / f"{i:04d}.png")

        bruto = destino.with_name(f"{destino.stem}_bruto.mp4")
        montado = subprocess.run(
            ["ffmpeg", "-y", "-framerate", "7", "-i", str(pasta / "%04d.png"),
             "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", str(bruto)],
            capture_output=True, text=True,
        )
        if montado.returncode != 0:
            print(f"⚠ ffmpeg (frames) falhou: {montado.stderr.strip()[-160:]}")
            return None
        return _esticar(bruto, destino, duracao)
    except BaseException as exc:
        print(f"⚠ SVD falhou ({type(exc).__name__}): {str(exc)[:150]}")
        return None


def _esticar(clipe: Path, destino: Path, duracao: float) -> Optional[Path]:
    """Desacelera o clipe para a duração exata da fala e interpola para 24 fps.

    O SVD entrega ~3,5s a 7 fps; a fala pode durar 12s. Sem isso, ou o vídeo acaba
    antes da voz, ou vira um loop visível.
    """
    atual = _duracao(clipe)
    if not atual:
        return None
    fator = duracao / atual
    filtro = (f"setpts={fator:.4f}*PTS,minterpolate=fps={FPS_SAIDA}:mi_mode=mci:"
              f"mc_mode=aobmc:vsbmc=1,scale=1280:720")
    resultado = subprocess.run(
        ["ffmpeg", "-y", "-i", str(clipe), "-vf", filtro, "-t", f"{duracao:.3f}",
         "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", str(destino)],
        capture_output=True, text=True,
    )
    if resultado.returncode != 0:
        print(f"⚠ ffmpeg (esticar) falhou: {resultado.stderr.strip()[-160:]}")
        return None
    return destino


def _duracao(media: Path) -> Optional[float]:
    resultado = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(media)],
        capture_output=True, text=True,
    )
    return float(resultado.stdout.strip()) if resultado.returncode == 0 else None

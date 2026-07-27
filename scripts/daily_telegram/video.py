import re
import shutil
import subprocess
from pathlib import Path
from typing import Optional

MARKDOWN_NOISE = re.compile(r"[*_`#>]|\[|\]|\(https?://[^)]+\)")
MAX_TTS_CHARS = 3000


def clean_for_tts(texto: str) -> str:
    """Strip markdown noise so the narration doesn't read symbols out loud."""
    limpo = MARKDOWN_NOISE.sub("", texto)
    return re.sub(r"\n{2,}", "\n", limpo).strip()


def narrate(texto: str, output_path: Path) -> float:
    """gTTS narration (free). Duration comes from ffprobe — pydub breaks on Python 3.13."""
    from gtts import gTTS

    if len(texto) > MAX_TTS_CHARS:
        print(f"⚠ Texto truncado de {len(texto)} para {MAX_TTS_CHARS} chars na narração")
        texto = texto[:MAX_TTS_CHARS] + "..."
    gTTS(text=texto, lang="pt", tld="com.br").save(str(output_path))
    return probe_duration(output_path)


def probe_duration(media_path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(media_path)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe falhou: {result.stderr.strip()}")
    return float(result.stdout.strip())


def build_video(
    image_path: Path,
    texto: str,
    titulo: str,
    numero: str,
    output_path: Path,
    temp_dir: Path,
) -> Optional[Path]:
    """Ken Burns video with gTTS narration. Returns None when it can't be produced."""
    if shutil.which("ffmpeg") is None:
        print("⚠ ffmpeg não encontrado; pulando geração de vídeo.")
        return None

    from scripts.video_gen.composer import VideoComposer

    temp_dir.mkdir(parents=True, exist_ok=True)
    audio_path = temp_dir / f"narracao_{numero}.mp3"

    try:
        duracao = narrate(clean_for_tts(texto), audio_path)
        print(f"🎙 Narração gerada: {duracao:.1f}s")
    except Exception as exc:  # gTTS depende de rede; falha não pode quebrar o envio
        print(f"⚠ Falha na narração: {exc}")
        return None

    composer = VideoComposer(temp_dir)
    composer.create_video_from_image(
        image_path=image_path,
        audio_path=audio_path,
        output_path=output_path,
        titulo=titulo,
        numero=numero,
        duration_seconds=int(duracao) + 2,
    )

    if not output_path.exists() or output_path.stat().st_size == 0:
        print("⚠ Vídeo não foi gerado.")
        return None
    print(f"🎬 Vídeo pronto: {output_path} ({output_path.stat().st_size // 1024} KB)")
    return output_path

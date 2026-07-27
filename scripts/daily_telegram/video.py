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


def split_for_tts(texto: str, limite: int = 2200) -> list:
    """Quebra o texto em blocos que o gTTS aguenta, sempre no fim de uma frase."""
    blocos, atual = [], ""
    for frase in re.split(r"(?<=[.!?])\s+", texto):
        if len(atual) + len(frase) + 1 <= limite:
            atual = f"{atual} {frase}".strip()
            continue
        if atual:
            blocos.append(atual)
        while len(frase) > limite:
            blocos.append(frase[:limite])
            frase = frase[limite:]
        atual = frase
    if atual:
        blocos.append(atual)
    return blocos


def narrate_full(texto: str, output_path: Path, temp_dir: Path) -> float:
    """Narração do capítulo inteiro: gTTS por bloco e concatenação via ffmpeg.

    O `narrate` normal corta em 3000 caracteres; um episódio precisa do texto todo.
    """
    from gtts import gTTS

    blocos = split_for_tts(clean_for_tts(texto))
    temp_dir.mkdir(parents=True, exist_ok=True)
    partes = []
    for i, bloco in enumerate(blocos, 1):
        parte = temp_dir / f"tts_{i:03d}.mp3"
        if not parte.exists() or parte.stat().st_size == 0:
            gTTS(text=bloco, lang="pt", tld="com.br").save(str(parte))
        partes.append(parte)
        print(f"🎙 bloco {i}/{len(blocos)} narrado")

    lista = temp_dir / "tts_concat.txt"
    lista.write_text("".join(f"file '{p.absolute().as_posix()}'\n" for p in partes), encoding="utf-8")
    resultado = subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lista),
         "-c:a", "libmp3lame", "-b:a", "128k", str(output_path)],
        capture_output=True, text=True,
    )
    if resultado.returncode != 0:
        raise RuntimeError(f"concat da narração falhou: {resultado.stderr.strip()[-200:]}")
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


def build_animated_video(
    texto: str,
    titulo: str,
    local: str,
    numero: str,
    output_path: Path,
    temp_dir: Path,
    n_cenas: int = 4,
    use_ai: bool = True,
    max_clip_seconds: float = 12.0,
) -> Optional[Path]:
    """Multi-scene animated video: identity-locked art + real motion, narrated."""
    if shutil.which("ffmpeg") is None:
        print("⚠ ffmpeg não encontrado; pulando geração de vídeo.")
        return None

    from scripts.daily_telegram import animate
    from scripts.daily_telegram.scenes import split_scenes

    temp_dir.mkdir(parents=True, exist_ok=True)
    audio_path = temp_dir / f"narracao_{numero}.mp3"
    try:
        duracao = narrate(clean_for_tts(texto), audio_path)
    except Exception as exc:
        print(f"⚠ Falha na narração: {exc}")
        return None
    print(f"🎙 Narração gerada: {duracao:.1f}s")

    cenas = split_scenes(texto, n_cenas)
    print(f"🎬 Storyboard: {len(cenas)} cenas")
    duracao_cena = min(max_clip_seconds, duracao / len(cenas))

    clipes = []
    for cena in cenas:
        nomes = ", ".join(c["name"] for c in cena.personagens) or "—"
        print(f"— Cena {cena.indice}/{len(cenas)} | personagens: {nomes}")
        imagem = animate.scene_image(
            cena, titulo, local, temp_dir / f"cena_{numero}_{cena.indice}.jpg",
            seed=int(numero) * 100 + cena.indice,
        )
        if not imagem:
            continue
        clipe = animate.scene_clip(imagem, cena, duracao_cena, temp_dir, use_ai)
        if clipe:
            clipes.append(clipe)

    if not clipes:
        print("⚠ Nenhuma cena pôde ser gerada.")
        return None

    final = animate.stitch(clipes, audio_path, output_path, temp_dir)
    if final and final.exists() and final.stat().st_size > 0:
        print(f"🎬 Vídeo animado pronto: {final} ({final.stat().st_size // 1024} KB)")
        return final
    return None


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

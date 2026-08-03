import subprocess
from pathlib import Path
from typing import List, Optional

from scripts.daily_telegram import art, camera, characters, film, hf_space
from scripts.daily_telegram.scenes import Scene

SIZE = "1280:720"
FPS = 30


def _run(cmd: List[str]) -> bool:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"⚠ ffmpeg falhou: {result.stderr.strip()[-200:]}")
        return False
    return True


def scene_image(
    cena: Scene, titulo: str, local: str, destino: Path, seed: int, local_gen=None
) -> Optional[Path]:
    """Identity-locked image when the scene has a character portrait; else text-to-image.

    Ordem de fallback definida no AGENTS.md §7: GPU local -> Space Kontext -> texto-para-imagem.
    """
    ancora = characters.pick_anchor(cena.personagens)
    if ancora and local_gen is not None:
        referencia = characters.reference_image(ancora)
        imagem = local_gen(referencia, cena.compact_prompt(ancora, local), destino, seed,
                           identity_scale=cena.identity_scale)
        if imagem:
            return imagem
        print("↩ Fallback: GPU local indisponível para esta cena.")
    if ancora:
        referencia = characters.reference_image(ancora)
        imagem = hf_space.edit_with_identity(
            referencia, cena.edit_prompt(ancora, local), destino, seed=seed
        )
        if imagem:
            return imagem
        print("↩ Fallback: geração sem referência de identidade.")
    if local_gen is not None:
        # Sem personagem na cena ainda vale gerar local: é grátis e não depende de rede.
        imagem = local_gen(None, cena.compact_prompt_sem_personagem(local), destino, seed)
        if imagem:
            return imagem
    return art.generate_image(cena.image_prompt(titulo, local), destino, seed=seed)


ken_burns = camera.ken_burns  # mantido aqui pelo nome usado no resto do pipeline


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
    return ken_burns(imagem, destino, duracao, cena.indice)


def title_card(numero: int, titulo: str, destino: Path, duracao: float = 2.5) -> Optional[Path]:
    """Short card announcing the chapter, so the full-story cut stays readable."""
    from PIL import Image, ImageDraw, ImageFont

    imagem = Image.new("RGB", (1280, 720), (6, 10, 14))
    draw = ImageDraw.Draw(imagem)
    try:
        fonte_num = ImageFont.truetype("arialbd.ttf", 64)
        fonte_tit = ImageFont.truetype("arial.ttf", 40)
    except OSError:
        fonte_num = fonte_tit = ImageFont.load_default()

    for texto, fonte, y, cor in (
        (f"CAPÍTULO {numero}", fonte_num, 300, (0, 229, 255)),
        (titulo, fonte_tit, 400, (235, 235, 235)),
    ):
        largura = draw.textbbox((0, 0), texto, font=fonte)[2]
        draw.text(((1280 - largura) // 2, y), texto, font=fonte, fill=cor)

    destino.parent.mkdir(parents=True, exist_ok=True)
    png = destino.with_suffix(".png")
    imagem.save(png)
    return ken_burns(png, destino, duracao, indice=2)


def silent_audio(duracao: float, destino: Path) -> Optional[Path]:
    """Trilha muda do mesmo tamanho de um clipe — mantém a cartela em sincronia."""
    ok = _run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
               "-t", f"{duracao:.3f}", "-c:a", "libmp3lame", "-b:a", "64k", str(destino)])
    return destino if ok else None


def concat_trilhas(pares: List, temp_dir: Path):
    """Concatena vídeo e voz na mesma ordem — é o que preserva a sincronia."""
    lista_v = temp_dir / "concat_v.txt"
    lista_a = temp_dir / "concat_a.txt"
    lista_v.write_text("".join(f"file '{c.absolute().as_posix()}'\n" for c, _ in pares), encoding="utf-8")
    lista_a.write_text("".join(f"file '{a.absolute().as_posix()}'\n" for _, a in pares), encoding="utf-8")

    video_mudo = temp_dir / "episodio_mudo.mp4"
    voz = temp_dir / "episodio_voz.mp3"
    if not _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lista_v),
                 "-c", "copy", str(video_mudo)]):
        return None, None
    if not _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lista_a),
                 "-c:a", "libmp3lame", "-b:a", "128k", str(voz)]):
        return None, None
    return video_mudo, voz


def stitch_synced(pares: List, destino: Path, temp_dir: Path, crf: int = 30,
                  audio_pronto: Optional[Path] = None, grade: bool = True) -> Optional[Path]:
    """Montagem final: vídeo + trilha, com o acabamento de cor aplicado numa passada só."""
    video_mudo, voz = concat_trilhas(pares, temp_dir)
    if video_mudo is None:
        return None

    cmd = ["ffmpeg", "-y", "-i", str(video_mudo), "-i", str(audio_pronto or voz)]
    if grade:
        cmd += ["-vf", film.grade_filter()]
    cmd += ["-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium",
            "-crf", str(crf), "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
            str(destino)]
    return destino if _run(cmd) else None


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

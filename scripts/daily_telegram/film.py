"""Acabamento de cinema: grade de cor, letterbox, grão, vinheta e desenho de som."""
import subprocess
from pathlib import Path
from typing import Optional

LARGURA, ALTURA = 1280, 720
# 2.39:1 é a proporção de cinema; as barras entram por cima do 16:9.
ALTURA_UTIL = int(LARGURA / 2.39) // 2 * 2
BARRA = (ALTURA - ALTURA_UTIL) // 2


def grade_filter(grao: float = 6.0) -> str:
    """Look neo-noir: sombras em teal, pele quente, contraste em S, grão e vinheta."""
    return (
        # curvas: levanta o azul nas sombras e segura o verde nos médios
        "curves=b='0/0.06 0.5/0.5 1/0.96':r='0/0 0.5/0.52 1/1':g='0/0.01 0.5/0.49 1/0.98',"
        "eq=contrast=1.12:saturation=1.06:gamma=0.98,"
        "vignette=angle=PI/5,"
        f"noise=alls={int(grao)}:allf=t+u,"
        f"crop={LARGURA}:{ALTURA_UTIL}:0:{BARRA},"
        f"pad={LARGURA}:{ALTURA}:0:{BARRA}:black"
    )


def fade_filter(duracao: float, entrada: float = 0.18, saida: float = 0.18) -> str:
    """Micro fade no início e no fim do plano: o corte seco denuncia slideshow."""
    inicio_saida = max(0.0, duracao - saida)
    return f"fade=t=in:st=0:d={entrada:.2f},fade=t=out:st={inicio_saida:.2f}:d={saida:.2f}"


def _run(cmd) -> bool:
    resultado = subprocess.run(cmd, capture_output=True, text=True)
    if resultado.returncode != 0:
        print(f"⚠ ffmpeg falhou: {resultado.stderr.strip()[-200:]}")
        return False
    return True


def ambiencia(duracao: float, destino: Path) -> Optional[Path]:
    """Cama sonora sintetizada: chuva, zumbido da cidade e um drone grave.

    Tudo gerado pelo ffmpeg — sem baixar trilha, sem licença, sem custo.
    """
    chuva = f"anoisesrc=color=brown:amplitude=0.35:duration={duracao:.2f}"
    cidade = f"anoisesrc=color=pink:amplitude=0.10:duration={duracao:.2f}"
    drone = f"sine=frequency=52:duration={duracao:.2f}"
    filtro = (
        f"{chuva}[ch];{cidade}[cid];{drone}[dr];"
        "[ch]highpass=f=600,lowpass=f=7000,volume=0.16[chuva];"
        "[cid]lowpass=f=400,volume=0.10[cidade];"
        "[dr]tremolo=f=0.15:d=0.4,volume=0.07[grave];"
        "[chuva][cidade][grave]amix=inputs=3:normalize=0[bed]"
    )
    ok = _run(["ffmpeg", "-y", "-filter_complex", filtro, "-map", "[bed]",
               "-t", f"{duracao:.2f}", "-c:a", "libmp3lame", "-b:a", "128k", str(destino)])
    return destino if ok else None


def montar_trilha(voz: Path, temp_dir: Path, duracao: float) -> Optional[Path]:
    """Voz + ambiência com ducking. Silêncio absoluto entre as falas mata o clima."""
    ambiente = ambiencia(duracao, temp_dir / "ambiencia.mp3")
    if not ambiente:
        return voz
    print(f"🔊 Ambiência de {duracao / 60:.1f} min mixada sob as falas")
    return mixar(voz, ambiente, temp_dir / "trilha.mp3") or voz


def fit_telegram(video: Path, temp_dir: Path, limite_mb: int = 48) -> Optional[Path]:
    """Reduz o episódio para caber no limite de 50 MB do bot, se necessário."""
    if video.stat().st_size / (1024 * 1024) <= limite_mb:
        return video
    print(f"↩ {video.stat().st_size // 1024 // 1024} MB excede o limite; reencodando em 540p...")
    reduzido = temp_dir / f"{video.stem}_540p.mp4"
    if not _run(["ffmpeg", "-y", "-i", str(video), "-vf", "scale=960:540",
                 "-c:v", "libx264", "-preset", "medium", "-crf", "34",
                 "-c:a", "aac", "-b:a", "96k", str(reduzido)]):
        return None
    reduzido.replace(video)
    return video


def mixar(voz: Path, ambiente: Path, destino: Path) -> Optional[Path]:
    """Mistura voz e ambiência com ducking: o ambiente abaixa quando alguém fala."""
    filtro = (
        "[1:a]aformat=channel_layouts=stereo[amb];"
        "[0:a]aformat=channel_layouts=stereo,volume=1.35[voz];"
        # sidechain: a voz comprime a ambiência, como numa mixagem de verdade
        "[amb][voz]sidechaincompress=threshold=0.03:ratio=9:attack=8:release=420[ducked];"
        "[voz][ducked]amix=inputs=2:duration=first:normalize=0,"
        "loudnorm=I=-16:TP=-1.5:LRA=11[out]"
    )
    ok = _run(["ffmpeg", "-y", "-i", str(voz), "-i", str(ambiente),
               "-filter_complex", filtro, "-map", "[out]",
               "-c:a", "libmp3lame", "-b:a", "160k", str(destino)])
    return destino if ok else None

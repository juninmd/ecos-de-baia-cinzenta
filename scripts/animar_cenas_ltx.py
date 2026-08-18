"""Anima as cenas em clipes de vídeo pelo LTX-Video (Space gratuito do HF).

A cota do ZeroGPU é diária e pequena (~3 clipes), então isto é feito para rodar várias
vezes: pula o que já existe e para sozinho quando a cota acaba, sem queimar tentativa.

Uso: python -m scripts.animar_cenas_ltx [capitulo_inicial] [capitulo_final]
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(REPO_ROOT / ".env")

from scripts.daily_telegram import hf_space, scenes  # noqa: E402

CENAS = REPO_ROOT / "docs" / "public" / "cenas"
CLIPES = REPO_ROOT / "docs" / "public" / "videos" / "clipes"


def alvos(inicio: int, fim: int):
    """Cenas canônicas na faixa, em ordem de capítulo e cena."""
    for pasta in sorted(
        (p for p in CENAS.iterdir() if p.is_dir() and p.name.startswith("capitulo_")),
        key=lambda p: float(p.name.split("_", 1)[1].replace("_", ".")),
    ):
        numero = float(pasta.name.split("_", 1)[1].replace("_", "."))
        if not inicio <= numero <= fim:
            continue
        for imagem in sorted(pasta.glob("cena_[123].jpg")):
            yield pasta.name, imagem


def main(inicio: int, fim: int) -> None:
    CLIPES.mkdir(parents=True, exist_ok=True)
    feitos = pulados = 0
    for nome_cap, imagem in alvos(inicio, fim):
        destino = CLIPES / f"{nome_cap}__{imagem.stem}.mp4"
        if destino.exists():
            pulados += 1
            continue
        indice = int(imagem.stem.split("_")[1])
        movimento = scenes.MOTION_HINTS[(indice - 1) % len(scenes.MOTION_HINTS)]
        clipe = hf_space.image_to_video(
            imagem, movimento, destino, duracao=3, seed=indice * 977
        )
        if clipe is None:
            # Cota esgotada ou Space fora do ar: insistir só queima tempo.
            print(f"⏹️ parando em {nome_cap}/{imagem.name} — rode de novo quando a cota voltar")
            break
        feitos += 1
        print(f"🎞️ {destino.name}")

    total = len(list(CLIPES.glob('*.mp4')))
    print(f"✅ {feitos} novos | ⏭️ {pulados} já existiam | 📁 {total} clipes no total")


if __name__ == "__main__":
    inicio = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    fim = int(sys.argv[2]) if len(sys.argv) > 2 else 999
    main(inicio, fim)

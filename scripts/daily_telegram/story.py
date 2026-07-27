"""Monta o filme da história: várias cenas por capítulo, encadeadas num vídeo só."""
import argparse
import sys
from pathlib import Path
from typing import List, Optional

from scripts.daily_telegram import animate, cache, chapter, video
from scripts.daily_telegram.scenes import split_scenes

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = REPO_ROOT / ".daily_telegram_out" / "story"


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Gera o filme animado da história.")
    parser.add_argument("--from", dest="inicio", type=int, default=1)
    parser.add_argument("--to", dest="fim", type=int, default=1)
    parser.add_argument("--scenes", type=int, default=8, help="Cenas por capítulo")
    parser.add_argument("--clip-seconds", type=float, default=8.0)
    parser.add_argument("--no-ai-motion", action="store_true")
    parser.add_argument("--art-only", action="store_true",
                        help="Só gera e cacheia as imagens das cenas, sem montar vídeo")
    parser.add_argument("--local", action="store_true",
                        help="Gera na GPU local (SDXL + IP-Adapter): sem cota, sem fila")
    parser.add_argument("--output", type=Path, default=OUTPUT_DIR / "historia_completa.mp4")
    return parser.parse_args(argv)


def build_scene_art(numero: int, n_cenas: int, local_gen=None) -> List[Path]:
    """Generate the missing frames of a chapter; cached ones are never regenerated."""
    dados = chapter.load_chapter(numero)
    local = dados["meta"].get("Localização", "")
    print(f"📖 Capítulo {numero}: {dados['titulo']} | {cache.coverage(numero, n_cenas)}")

    imagens = []
    for cena in split_scenes(dados["texto"], n_cenas):
        destino = cache.scene_path(numero, cena.indice)
        existente = cache.cached(numero, cena.indice)
        if existente:
            print(f"  ⏭ cena {cena.indice}: cache")
            imagens.append(existente)
            continue
        nomes = ", ".join(c["name"] for c in cena.personagens) or "—"
        print(f"  🎨 cena {cena.indice}: {nomes}")
        destino.parent.mkdir(parents=True, exist_ok=True)
        imagem = animate.scene_image(
            cena, dados["titulo"], local, destino,
            seed=numero * 100 + cena.indice, local_gen=local_gen,
        )
        if imagem:
            imagens.append(imagem)
    return imagens


def build_chapter_video(numero: int, args, temp_dir: Path, local_gen=None) -> Optional[Path]:
    """One chapter: title card + animated scenes + narration."""
    dados = chapter.load_chapter(numero)
    imagens = build_scene_art(numero, args.scenes, local_gen)
    if not imagens:
        return None

    audio = temp_dir / f"narracao_{numero}.mp3"
    try:
        video.narrate(video.clean_for_tts(dados["texto"]), audio)
    except Exception as exc:
        print(f"⚠ Narração falhou no capítulo {numero}: {exc}")
        return None

    # Diretório por capítulo: scene_clip nomeia os arquivos por índice de cena e
    # capítulos diferentes sobrescreveriam os clipes uns dos outros.
    cap_dir = temp_dir / f"cap_{numero}"
    cap_dir.mkdir(parents=True, exist_ok=True)

    clipes = []
    cartela = animate.title_card(numero, dados["titulo"], cap_dir / "cartela.mp4")
    if cartela:
        clipes.append(cartela)
    for cena in split_scenes(dados["texto"], len(imagens)):
        clipe = animate.scene_clip(
            imagens[cena.indice - 1], cena, args.clip_seconds, cap_dir, not args.no_ai_motion
        )
        if clipe:
            clipes.append(clipe)

    destino = temp_dir / f"capitulo_{numero}_animado.mp4"
    return animate.stitch(clipes, audio, destino, temp_dir)


def main(argv=None) -> int:
    args = parse_args(argv)
    temp_dir = OUTPUT_DIR / "tmp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    capitulos = range(args.inicio, args.fim + 1)

    local_gen = None
    if args.local:
        from scripts.daily_telegram import local_gpu

        if local_gpu.available():
            local_gen = local_gpu.generate
            print("🖥️ Modo local: gerando na GPU, sem cota.")
        else:
            print("⚠ GPU indisponível; seguindo pelos Spaces gratuitos.")

    if args.art_only:
        for numero in capitulos:
            build_scene_art(numero, args.scenes, local_gen)
        return 0

    partes = []
    for numero in capitulos:
        parte = build_chapter_video(numero, args, temp_dir, local_gen)
        if parte:
            partes.append(parte)
            print(f"✅ Capítulo {numero} animado")

    if not partes:
        print("❌ Nenhum capítulo pôde ser animado.")
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    lista = temp_dir / "filme.txt"
    lista.write_text("".join(f"file '{p.absolute().as_posix()}'\n" for p in partes), encoding="utf-8")
    if not animate._run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lista),
                         "-c", "copy", str(args.output)]):
        return 1
    print(f"🎬 Filme pronto: {args.output} ({args.output.stat().st_size // 1024 // 1024} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

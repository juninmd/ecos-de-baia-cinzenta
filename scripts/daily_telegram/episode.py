"""Episódio de série: personagens falando, cada plano durando exatamente a fala."""
import argparse
import math
import sys
from pathlib import Path
from typing import List, Optional, Tuple

from scripts.daily_telegram import (animate, cache, chapter, characters, film, screenplay,
                                    speech, svd)
from scripts.daily_telegram.scenes import Scene

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = REPO_ROOT / ".daily_telegram_out" / "episodios"
SHOTS_DIALOGO = ("close-up", "over-the-shoulder shot")


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Gera o episódio animado de um capítulo.")
    parser.add_argument("--chapter", type=int, default=1)
    parser.add_argument("--local", action="store_true", help="Gera as imagens na GPU local")
    parser.add_argument("--max-beats", type=int, help="Limita o número de planos (teste rápido)")
    parser.add_argument("--crf", type=int, default=32, help="Qualidade do encode final")
    parser.add_argument("--sem-grade", action="store_true", help="Desliga o acabamento de cor")
    parser.add_argument("--svd", type=int, default=0,
                        help="Quantos planos-chave ganham movimento real por IA (SVD local)")
    parser.add_argument("--output", type=Path)
    return parser.parse_args(argv)


SEGUNDOS_POR_PLANO = 11.0


def planos_do_beat(duracao: float) -> int:
    """Quantos planos cabem numa fala: 30 segundos numa imagem só vira slideshow."""
    return max(1, math.ceil(duracao / SEGUNDOS_POR_PLANO))


def beat_scene(beat, indice_dialogo: int) -> Scene:
    """Plano correspondente ao beat: quem fala é a âncora visual da imagem."""
    if beat.is_fala:
        personagens = [beat.personagem] if beat.personagem else []
        return Scene(beat.indice, beat.texto, personagens,
                     shot_hint=SHOTS_DIALOGO[indice_dialogo % len(SHOTS_DIALOGO)])
    return Scene(beat.indice, beat.texto, characters.detect(beat.texto))


def beat_clip(beat, cena: Scene, duracao: float, numero: int, total: int, dados: dict,
              local: str, temp_dir: Path, local_gen, com_svd: bool = False) -> Optional[Path]:
    """Vídeo do beat: uma ou mais imagens dividindo igualmente a duração da fala."""
    quantidade = planos_do_beat(duracao)
    fatia = duracao / quantidade
    partes = []
    for j in range(quantidade):
        indice = beat.indice * 100 + j
        variante = Scene(indice, cena.texto, cena.personagens,
                         shot_hint=cena.shot_hint if j == 0 else None)
        imagem = cache.cached(numero, indice, total) or animate.scene_image(
            variante, dados["titulo"], local, cache.scene_path(numero, indice, total),
            seed=numero * 1000 + indice, local_gen=local_gen,
        )
        if not imagem:
            continue
        alvo = temp_dir / f"plano_{indice:05d}.mp4"
        parte = None
        if com_svd and j == 0:
            # Movimento real só no primeiro plano do beat: cada clipe de SVD custa
            # ~5 min de GPU, então ele vai onde mais aparece.
            parte = svd.animar(imagem, temp_dir / f"svd_{indice:05d}.mp4", fatia,
                               seed=numero * 1000 + indice)
            if parte:
                print(f"    🎥 movimento real (SVD) no plano {indice}")
        parte = parte or animate.ken_burns(imagem, alvo, fatia, indice)
        if parte:
            partes.append(parte)

    if not partes:
        return None
    if len(partes) == 1:
        return partes[0]

    lista = temp_dir / f"beat_{beat.indice:03d}.txt"
    lista.write_text("".join(f"file '{p.absolute().as_posix()}'\n" for p in partes), encoding="utf-8")
    destino = temp_dir / f"beat_{beat.indice:03d}.mp4"
    ok = animate._run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lista),
                       "-c", "copy", str(destino)])
    return destino if ok else partes[0]


def build(numero: int, args, local_gen=None) -> Optional[Path]:
    dados = chapter.load_chapter(numero)
    beats = screenplay.parse(dados["texto"])
    if args.max_beats:
        beats = beats[:args.max_beats]
    total = len(beats)
    local = dados["meta"].get("Localização", "")
    print(f"🎬 Episódio — Capítulo {numero}: {dados['titulo']}")
    print(f"   {total} planos | {sum(1 for b in beats if b.is_fala)} falas | "
          f"elenco: {', '.join(screenplay.falantes_do_capitulo(beats)) or '—'}")
    print(f"   {cache.coverage(numero, total)}")

    temp_dir = OUTPUT_DIR / f"capitulo_{numero}"
    temp_dir.mkdir(parents=True, exist_ok=True)
    pares: List[Tuple[Path, Path]] = []

    cartela = animate.title_card(numero, dados["titulo"], temp_dir / "cartela.mp4", duracao=3.0)
    if cartela:
        silencio = animate.silent_audio(3.0, temp_dir / "cartela.mp3")
        if silencio:
            pares.append((cartela, silencio))

    # Primeira passada: sintetiza todas as falas. Só com as durações na mão dá para
    # escolher onde investir os minutos caros de movimento real.
    duracoes = {}
    for beat in beats:
        caminho = temp_dir / f"fala_{beat.indice:03d}.mp3"
        duracao = speech.say(beat.texto, beat.personagem if beat.is_fala else None, caminho)
        if duracao:
            duracoes[beat.indice] = duracao

    herois = set()
    if args.svd and svd.disponivel():
        herois = {i for i, _ in sorted(duracoes.items(), key=lambda kv: -kv[1])[:args.svd]}
        print(f"🎥 Movimento real por IA nos {len(herois)} planos mais longos: "
              f"{sorted(herois)}")

    indice_dialogo = 0
    for beat in beats:
        cena = beat_scene(beat, indice_dialogo)
        if beat.is_fala:
            indice_dialogo += 1

        caminho_audio = temp_dir / f"fala_{beat.indice:03d}.mp3"
        duracao = duracoes.get(beat.indice)
        if not duracao:
            continue

        # O clipe dura exatamente a fala: é isso que mantém imagem e voz em sincronia.
        clipe = beat_clip(beat, cena, duracao, numero, total, dados, local, temp_dir,
                          local_gen, com_svd=beat.indice in herois)
        if clipe:
            pares.append((clipe, caminho_audio))
            quem = beat.personagem["name"].split()[0] if beat.personagem else "narração"
            print(f"  ▸ beat {beat.indice}/{total} · {quem} · {duracao:.1f}s "
                  f"· {planos_do_beat(duracao)} plano(s)")

    if not pares:
        print("❌ Nenhum plano pôde ser montado.")
        return None

    destino = args.output or OUTPUT_DIR / f"episodio_capitulo_{numero}.mp4"
    destino.parent.mkdir(parents=True, exist_ok=True)
    _, voz = animate.concat_trilhas(pares, temp_dir)
    trilha = film.montar_trilha(voz, temp_dir, speech._probe(voz)) if voz else None
    final = animate.stitch_synced(pares, destino, temp_dir, crf=args.crf,
                                  audio_pronto=trilha, grade=not args.sem_grade)
    if final:
        final = film.fit_telegram(final, temp_dir) or final
        print(f"🎞️ Episódio pronto: {final} ({final.stat().st_size // 1024 // 1024} MB)")
    return final


def main(argv=None) -> int:
    args = parse_args(argv)
    local_gen = None
    if args.local:
        from scripts.daily_telegram import local_gpu

        if local_gpu.available():
            local_gen = local_gpu.generate
            print("🖥️ Imagens na GPU local, sem cota.")
        else:
            print("⚠ GPU indisponível; usando os serviços gratuitos.")
    return 0 if build(args.chapter, args, local_gen) else 1


if __name__ == "__main__":
    sys.exit(main())

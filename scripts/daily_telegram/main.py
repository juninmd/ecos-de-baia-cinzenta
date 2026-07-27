import argparse
import os
import sys
from pathlib import Path

from scripts.daily_telegram import art, chapter, state, video
from scripts.daily_telegram.telegram import TelegramClient

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = REPO_ROOT / ".daily_telegram_out"


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Envia um capítulo por dia no Telegram.")
    parser.add_argument("--chapter", type=int, help="Força um capítulo específico")
    parser.add_argument("--no-video", action="store_true", help="Envia só imagem + texto")
    parser.add_argument("--dry-run", action="store_true", help="Não envia nada ao Telegram")
    parser.add_argument("--state-file", type=Path, default=state.DEFAULT_STATE_FILE)
    return parser.parse_args(argv)


def resolve_chapter(args) -> int:
    disponiveis = chapter.list_chapters()
    if not disponiveis:
        raise SystemExit("❌ Nenhum capítulo encontrado em docs/ ou docs/public/")
    if args.chapter:
        return args.chapter
    numero = state.pick_next(disponiveis, state.load_state(args.state_file))
    if numero is None:
        raise SystemExit("❌ Não foi possível determinar o próximo capítulo")
    return numero


def resolve_art(dados: dict, numero: int) -> Path | None:
    if dados["local_art"]:
        print(f"🖼️ Usando arte já existente: {dados['local_art']}")
        return dados["local_art"]
    prompt = art.build_prompt(dados["titulo"], dados["meta"], dados["texto"])
    destino = OUTPUT_DIR / f"capitulo_{numero}.jpg"
    return art.generate_image(prompt, destino, seed=numero)


def main(argv=None) -> int:
    args = parse_args(argv)
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    if not args.dry_run and not (token and chat_id):
        raise SystemExit("❌ Defina TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID")

    numero = resolve_chapter(args)
    dados = chapter.load_chapter(numero)
    print(f"📖 Capítulo {numero}: {dados['titulo']} ({len(dados['texto'])} chars)")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    client = TelegramClient(token, chat_id, dry_run=args.dry_run)
    legenda = f"📖 Capítulo {numero} — {dados['titulo']}"

    imagem = resolve_art(dados, numero)
    if imagem:
        client.send_photo(imagem, legenda)
    else:
        client.send_message(legenda)

    client.send_chapter_text(dados["texto"])

    if not args.no_video and imagem:
        destino = OUTPUT_DIR / f"capitulo_{numero}.mp4"
        arquivo = video.build_video(
            image_path=imagem,
            texto=dados["texto"],
            titulo=dados["titulo"],
            numero=str(numero),
            output_path=destino,
            temp_dir=OUTPUT_DIR / "tmp",
        )
        if arquivo:
            client.send_video(arquivo, f"🎬 {legenda}")

    if not args.dry_run:
        state.save_state(numero, args.state_file)
    print(f"✅ Capítulo {numero} entregue.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

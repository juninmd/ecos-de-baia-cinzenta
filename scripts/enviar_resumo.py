"""Envia um texto para o Telegram — usado para mandar os resumos de capítulo.

Uso: python -m scripts.enviar_resumo <arquivo.md>
"""

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(REPO_ROOT / ".env")

from scripts.daily_telegram.telegram import TelegramClient  # noqa: E402


def enviar(caminho: Path) -> None:
    cliente = TelegramClient(
        os.getenv("TELEGRAM_BOT_TOKEN", ""), os.getenv("TELEGRAM_CHAT_ID", "")
    )
    # send_chapter_text já quebra em pedaços dentro do limite da API.
    cliente.send_chapter_text(caminho.read_text(encoding="utf-8"))
    print(f"✈️ enviado: {caminho.name}")


if __name__ == "__main__":
    enviar(Path(sys.argv[1]))

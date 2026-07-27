import time
from pathlib import Path
from typing import List, Optional

import requests

API_URL = "https://api.telegram.org/bot{token}/{method}"
MESSAGE_LIMIT = 4000
CAPTION_LIMIT = 1000


def split_text(texto: str, limit: int = MESSAGE_LIMIT) -> List[str]:
    """Split chapter text into Telegram-sized chunks, respecting paragraph breaks."""
    chunks: List[str] = []
    atual = ""
    for paragrafo in texto.split("\n"):
        candidato = f"{atual}\n{paragrafo}" if atual else paragrafo
        if len(candidato) <= limit:
            atual = candidato
            continue
        if atual:
            chunks.append(atual)
        while len(paragrafo) > limit:
            chunks.append(paragrafo[:limit])
            paragrafo = paragrafo[limit:]
        atual = paragrafo
    if atual:
        chunks.append(atual)
    return chunks


class TelegramClient:
    """Minimal Telegram Bot API client (free tier, no dependencies beyond requests)."""

    def __init__(self, token: str, chat_id: str, dry_run: bool = False):
        self.token = token
        self.chat_id = chat_id
        self.dry_run = dry_run

    def _post(self, method: str, data: dict, files: Optional[dict] = None, retries: int = 3):
        if self.dry_run:
            print(f"🧪 [dry-run] {method} -> {list(data.keys())}")
            return None
        url = API_URL.format(token=self.token, method=method)
        for attempt in range(1, retries + 1):
            try:
                response = requests.post(url, data=data, files=files, timeout=300)
                if response.status_code == 429:
                    espera = response.json().get("parameters", {}).get("retry_after", 10)
                    print(f"⏳ Rate limit, aguardando {espera}s...")
                    time.sleep(espera)
                    continue
                response.raise_for_status()
                return response.json()
            except requests.RequestException as exc:
                print(f"⚠ {method} falhou (tentativa {attempt}/{retries}): {exc}")
                if attempt == retries:
                    raise
                time.sleep(5 * attempt)
        return None

    def send_message(self, texto: str) -> None:
        self._post("sendMessage", {"chat_id": self.chat_id, "text": texto,
                                   "disable_web_page_preview": True})

    def send_chapter_text(self, texto: str) -> None:
        for parte in split_text(texto):
            self.send_message(parte)
            time.sleep(1)

    def send_photo(self, image_path: Path, caption: str = "") -> None:
        with open(image_path, "rb") as handle:
            self._post(
                "sendPhoto",
                {"chat_id": self.chat_id, "caption": caption[:CAPTION_LIMIT]},
                files={"photo": handle},
            )

    def send_video(self, video_path: Path, caption: str = "") -> None:
        size_mb = video_path.stat().st_size / (1024 * 1024)
        if size_mb > 49:
            print(f"⚠ Vídeo de {size_mb:.1f} MB excede o limite do bot (50 MB); pulando.")
            return
        with open(video_path, "rb") as handle:
            self._post(
                "sendVideo",
                {"chat_id": self.chat_id, "caption": caption[:CAPTION_LIMIT],
                 "supports_streaming": True},
                files={"video": handle},
            )

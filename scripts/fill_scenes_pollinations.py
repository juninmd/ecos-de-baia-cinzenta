"""Preenche as cenas faltantes via Pollinations, em ordem reversa.

Roda em paralelo ao agy/Gemini, que sobe do capítulo 17 para frente: este desce do 235
para trás, então os dois se encontram no meio sem refazer trabalho. O tier anônimo do
Pollinations aceita uma requisição por IP na fila, logo a geração aqui é estritamente
serial.
"""

import os
import re
import sys
import time
from pathlib import Path
from urllib.parse import quote

import dotenv
import requests

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
dotenv.load_dotenv(REPO_ROOT / ".env")

from scripts.daily_telegram import characters, scenes  # noqa: E402
from scripts.generate_missing_scenes import (  # noqa: E402
    extract_chapter_title_and_clean_text,
    get_chapter_files,
    send_telegram_photo,
)

POLLINATIONS_URL = "https://image.pollinations.ai/prompt/{prompt}"
# Único modelo aberto ao tier anônimo; `flux` e `kontext` saíram do grátis.
MODEL = "sana"
NEGATIVE = "text, watermark, logo, deformed face, extra limbs, blurry"
MAX_ATTEMPTS = 8


def generate(prompt: str, destino: Path, seed: int) -> bool:
    """Uma imagem por vez, com espera crescente no 429 de fila cheia."""
    url = POLLINATIONS_URL.format(prompt=quote(prompt[:1500]))
    params = {
        "width": 1280,
        "height": 720,
        "seed": seed,
        "model": MODEL,
        "nologo": "true",
        "negative": NEGATIVE,
    }
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            resp = requests.get(url, params=params, timeout=300)
            if resp.status_code == 429:
                espera = 30 * attempt
                print(f"⏳ fila cheia (429), aguardando {espera}s")
                time.sleep(espera)
                continue
            resp.raise_for_status()
            if len(resp.content) < 2048:
                raise ValueError("resposta vazia ou muito pequena")
        except (requests.RequestException, ValueError) as exc:
            print(f"⚠ tentativa {attempt}/{MAX_ATTEMPTS} falhou: {exc}")
            time.sleep(10 * attempt)
            continue

        # Escrita atômica: o agy roda em paralelo e não pode ver arquivo pela metade.
        parcial = destino.with_suffix(".tmp")
        parcial.write_bytes(resp.content)
        if destino.exists():  # o agy chegou nesta cena antes — a dele vale mais
            parcial.unlink()
            return False
        parcial.replace(destino)
        return True
    return False


def process(inicio: float, fim: float) -> None:
    chapters = [c for c in get_chapter_files() if inicio <= c["val"] <= fim]
    chapters.reverse()
    print(f"📚 {len(chapters)} capítulos na faixa {inicio}-{fim} (ordem reversa)")

    for cap in chapters:
        pasta = cap["folder_path"]
        pasta.mkdir(parents=True, exist_ok=True)
        faltando = [m for m in range(1, 4) if not (pasta / f"cena_{m}.jpg").exists()]
        if not faltando:
            continue

        titulo, corpo = extract_chapter_title_and_clean_text(
            cap["file_path"].read_text(encoding="utf-8")
        )
        cenas = scenes.split_scenes(corpo, quantidade=3)
        while len(cenas) < 3:
            cenas.append(cenas[-1])

        for idx in faltando:
            destino = pasta / f"cena_{idx}.jpg"
            if destino.exists():
                continue
            cena = cenas[idx - 1]
            cena.indice = idx
            # Sem kontext no tier grátis, a identidade só pode vir por texto:
            # image_prompt já injeta a descrição canônica de cada personagem detectado.
            prompt = cena.image_prompt(titulo)
            seed = int(cap["val"] * 1000) + idx
            print(f"📸 {cap['folder_name']}/cena_{idx}.jpg (seed={seed})")
            if generate(prompt, destino, seed):
                send_telegram_photo(destino, f"{cap['folder_name']} cena_{idx}")
            else:
                print(f"❌ pulando {cap['folder_name']}/cena_{idx}.jpg")


if __name__ == "__main__":
    inicio = float(sys.argv[1]) if len(sys.argv) > 1 else 1
    fim = float(sys.argv[2]) if len(sys.argv) > 2 else 999
    process(inicio, fim)

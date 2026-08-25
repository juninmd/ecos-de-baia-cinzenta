"""Gerador antigo, por SD/HF, mantido como plano B do `gerar_cenas_manifesto.py`.

A raiz do repositório era um caminho absoluto do Windows: fora da máquina do autor este
script achava zero capítulos e não gerava nada, sem reclamar. Agora ele usa a descoberta
compartilhada de `scripts/art_gen/chapters.py`, igual ao resto da pipeline.
"""

import os
import sys
import time
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts.art_gen import prompt_cena  # noqa: E402
from scripts.art_gen.chapters import (  # noqa: E402
    extract_chapter_title_and_clean_text, get_chapter_files, limpar_titulos,
)
from scripts.build_scene_manifest import CENAS_POR_CAPITULO  # noqa: E402
from scripts.daily_telegram import art, characters, local_gpu, scenes  # noqa: E402

# GPU local primeiro (sem cota, identidade travada por IP-Adapter): AGENTS.md §7.
_LOCAL_GEN = local_gpu.generate if local_gpu.available() else None
if _LOCAL_GEN:
    print("🖥️ GPU local disponível: SDXL + IP-Adapter tem prioridade sobre Pollinations.")
else:
    print("⚠ GPU local indisponível; usando Pollinations (sem fidelidade de personagem).")

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram_photo(image_path: Path, caption: str):
    """Sends a photo to Telegram via sendPhoto API."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print(f"⚠️ Telegram token or chat ID missing. Skipping Telegram notification for {image_path.name}")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "caption": caption
    }
    
    for attempt in range(1, 4):
        try:
            with open(image_path, "rb") as photo_file:
                files = {"photo": photo_file}
                resp = requests.post(url, data=data, files=files, timeout=60)
                if resp.status_code == 429:
                    retry_after = resp.json().get("parameters", {}).get("retry_after", 10)
                    print(f"⏳ Telegram Rate limit (429), waiting {retry_after}s...")
                    time.sleep(retry_after)
                    continue
                resp.raise_for_status()
                print(f"✈️ Telegram sent: {caption}")
                return True
        except Exception as exc:
            print(f"⚠️ Telegram send photo attempt {attempt} failed for {caption}: {exc}")
            time.sleep(2 * attempt)
    
    print(f"❌ Telegram send photo failed permanently for {caption}")
    return False

def process_all_chapters():
    chapters = get_chapter_files()
    print(f"📚 Total chapters identified: {len(chapters)}")
    
    for cap in chapters:
        folder_path = cap["folder_path"]
        folder_path.mkdir(parents=True, exist_ok=True)
        
        missing_scenes = []
        for m in range(1, CENAS_POR_CAPITULO + 1):
            scene_path = folder_path / f"cena_{m}.jpg"
            if not scene_path.exists():
                missing_scenes.append(m)
                
        if not missing_scenes:
            print(f"⏩ Chapter {cap['folder_name']} completo com {CENAS_POR_CAPITULO} cenas.")
            continue
            
        print(f"\n🎨 Processing {cap['folder_name']} (missing scenes: {missing_scenes})...")
        raw_text = cap["file_path"].read_text(encoding="utf-8")
        title, body_text = extract_chapter_title_and_clean_text(raw_text)
        title, body_text = limpar_titulos(title, body_text)
        
        scene_objects = scenes.split_scenes(body_text, quantidade=CENAS_POR_CAPITULO)

        while len(scene_objects) < CENAS_POR_CAPITULO:
            scene_objects.append(scene_objects[-1] if scene_objects else scenes.Scene(len(scene_objects)+1, body_text))
            
        for scene_idx in missing_scenes:
            s_obj = scene_objects[scene_idx - 1]
            s_obj.indice = scene_idx
            
            # Character detection and anchor selection
            detected_chars = s_obj.personagens
            anchor = characters.pick_anchor(detected_chars)

            # Regra 4 do AGENTS.md: seed = capítulo * 100 + índice da cena.
            seed = prompt_cena.seed_da_cena(cap["num_str"], scene_idx)
            scene_file_path = folder_path / f"cena_{scene_idx}.jpg"

            print(f"📸 Generating {cap['folder_name']} cena_{scene_idx}.jpg (seed={seed})...")

            # GPU local primeiro (SDXL + IP-Adapter, identidade travada); Pollinations é
            # só o plano B se a GPU estiver indisponível ou a geração local falhar.
            gen_res = None
            if _LOCAL_GEN is not None:
                if anchor:
                    referencia = characters.reference_image(anchor)
                    gen_res = _LOCAL_GEN(
                        referencia, s_obj.compact_prompt(anchor), scene_file_path, seed,
                        identity_scale=s_obj.identity_scale,
                    )
                else:
                    gen_res = _LOCAL_GEN(
                        None, s_obj.compact_prompt_sem_personagem(), scene_file_path, seed,
                    )
                if gen_res:
                    print(f"🖥️ GPU local: {scene_file_path.name}")
                else:
                    print("↩ Fallback: GPU local indisponível para esta cena.")

            if gen_res is None:
                prompt = s_obj.edit_prompt(anchor) if anchor else s_obj.image_prompt(title)
                gen_res = art.generate_image(
                    prompt=prompt,
                    output_path=scene_file_path,
                    seed=seed,
                    width=1280,
                    height=720,
                    retries=3,
                )

            if gen_res and scene_file_path.exists():
                caption = f"{cap['folder_name']} cena_{scene_idx}"
                send_telegram_photo(scene_file_path, caption)
            else:
                print(f"❌ Failed to generate {cap['folder_name']} cena_{scene_idx}.jpg")
                
            time.sleep(1) # Gentle pause between generations

if __name__ == "__main__":
    process_all_chapters()

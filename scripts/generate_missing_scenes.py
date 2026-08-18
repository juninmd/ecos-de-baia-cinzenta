import os
import re
import sys
import time
from pathlib import Path
import dotenv
import requests

# Load environment variables
REPO_ROOT = Path(r"D:\Solutions\pessoal\meu-livro")
dotenv.load_dotenv(REPO_ROOT / ".env")

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

from scripts.daily_telegram import art, scenes, characters

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

def extract_chapter_title_and_clean_text(raw_text: str):
    """Extracts chapter title from frontmatter or text and cleans metadata."""
    title = "Capítulo"
    lines = raw_text.splitlines()
    body_lines = []
    in_frontmatter = False
    
    for line in lines:
        if line.strip() == "---":
            in_frontmatter = not in_frontmatter
            continue
        if in_frontmatter:
            if line.startswith("title:"):
                title = line.split("title:", 1)[1].strip().strip('"\'')
        else:
            body_lines.append(line)
            
    body_text = "\n".join(body_lines).strip()
    return title, body_text

def get_chapter_files():
    """Finds all chapter markdown files and sorts them numerically."""
    docs_dir = REPO_ROOT / "docs"
    cap_files = [f for f in docs_dir.glob("capitulo-*.md")]
    
    chapters = []
    for cap_path in cap_files:
        m = re.search(r"capitulo-(\d+(\.\d+)?)\.md$", cap_path.name)
        if m:
            val = float(m.group(1))
            num_str = m.group(1)
            folder_name = f"capitulo_{num_str}".replace(".", "_")
            chapters.append({
                "val": val,
                "num_str": num_str,
                "file_path": cap_path,
                "folder_name": folder_name,
                "folder_path": REPO_ROOT / "docs" / "public" / "cenas" / folder_name
            })
            
    chapters.sort(key=lambda x: x["val"])
    return chapters

def process_all_chapters():
    chapters = get_chapter_files()
    print(f"📚 Total chapters identified: {len(chapters)}")
    
    for cap in chapters:
        folder_path = cap["folder_path"]
        folder_path.mkdir(parents=True, exist_ok=True)
        
        # Check missing scenes (cena_1.jpg, cena_2.jpg, cena_3.jpg)
        missing_scenes = []
        for m in range(1, 4):
            scene_path = folder_path / f"cena_{m}.jpg"
            if not scene_path.exists():
                missing_scenes.append(m)
                
        if not missing_scenes:
            print(f"⏩ Chapter {cap['folder_name']} already complete with 3 scenes. Skipping.")
            continue
            
        print(f"\n🎨 Processing {cap['folder_name']} (missing scenes: {missing_scenes})...")
        raw_text = cap["file_path"].read_text(encoding="utf-8")
        title, body_text = extract_chapter_title_and_clean_text(raw_text)
        
        # Split text into 3 scenes
        scene_objects = scenes.split_scenes(body_text, quantidade=3)
        
        # Ensure we have 3 scene objects
        while len(scene_objects) < 3:
            scene_objects.append(scene_objects[-1] if scene_objects else scenes.Scene(len(scene_objects)+1, body_text))
            
        for scene_idx in missing_scenes:
            s_obj = scene_objects[scene_idx - 1]
            s_obj.indice = scene_idx
            
            # Character detection and anchor selection
            detected_chars = s_obj.personagens
            anchor = characters.pick_anchor(detected_chars)
            
            if anchor:
                prompt = s_obj.edit_prompt(anchor)
            else:
                prompt = s_obj.image_prompt(title)
                
            # Deterministic seed per chapter & scene
            seed = int(cap["val"] * 1000) + scene_idx
            scene_file_path = folder_path / f"cena_{scene_idx}.jpg"
            
            print(f"📸 Generating {cap['folder_name']} cena_{scene_idx}.jpg (seed={seed})...")
            gen_res = art.generate_image(
                prompt=prompt,
                output_path=scene_file_path,
                seed=seed,
                width=1280,
                height=720,
                retries=3
            )
            
            if gen_res and scene_file_path.exists():
                caption = f"{cap['folder_name']} cena_{scene_idx}"
                send_telegram_photo(scene_file_path, caption)
            else:
                print(f"❌ Failed to generate {cap['folder_name']} cena_{scene_idx}.jpg")
                
            time.sleep(1) # Gentle pause between generations

if __name__ == "__main__":
    process_all_chapters()

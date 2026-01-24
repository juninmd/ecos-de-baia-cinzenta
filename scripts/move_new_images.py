
import os
import shutil
import glob

ARTIFACT_DIR = r"C:/Users/jr_ac/.gemini/antigravity/brain/e3d53e6d-8e34-4de4-a5a1-655118d4581f"
PERSONAGENS_DIR = r"d:/Solutions/pessoal/meu-livro/docs/public/personagens"

mapping = {
    "clara_moretti_sister": "clara.png",
    "enzo_sofia_rossi_pizza": "enzo_sofia.png",
    "helena_moretti_memory": "helena.png"
}

if not os.path.exists(PERSONAGENS_DIR):
    os.makedirs(PERSONAGENS_DIR)

src_files = glob.glob(os.path.join(ARTIFACT_DIR, "*.png"))
for src in src_files:
    basename = os.path.basename(src)
    for key, new_name in mapping.items():
        if key in basename:
            dst = os.path.join(PERSONAGENS_DIR, new_name)
            shutil.copy2(src, dst)
            print(f"Copied {src} to {dst}")

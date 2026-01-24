
import os
import shutil
import glob

ARTIFACT_DIR = r"C:/Users/jr_ac/.gemini/antigravity/brain/e3d53e6d-8e34-4de4-a5a1-655118d4581f"
PERSONAGENS_DIR = r"d:/Solutions/pessoal/meu-livro/docs/public/personagens"

if not os.path.exists(PERSONAGENS_DIR):
    os.makedirs(PERSONAGENS_DIR)

# Map specific generated files to nice names
mapping = {
    "aria_entity": "aria_generated.png", 
    "clara_moretti_sister": "clara_generated.png",
    "dante_moretti_biohost": "dante_generated.png",
    "elara_vance": "elara_generated.png",
    "elena_moretti_formerly_livia": "elena_generated.png",
    "enzo_sofia_rossi_pizza": "enzo_sofia_generated.png",
    "gabo_moretti": "gabo_generated.png",
    "helena_moretti_memory": "helena_generated.png",
    "marco_moretti_mayor": "marco_generated.png",
    "roberto_miranda_cyborg": "roberto_generated.png",
    "silas_vance_simple_v3": "silas_generated.png",
    "the_taxidermist": "taxidermista_generated.png",
    "valeria_cruz_realistic": "val_realistic.png",
    "valeria_cruz_val": "val_v1.png"
}

print(f"Scanning {ARTIFACT_DIR}...")
src_files = glob.glob(os.path.join(ARTIFACT_DIR, "*.png"))

for src in src_files:
    basename = os.path.basename(src)
    # Find matching key in mapping
    dest_name = None
    for key, val in mapping.items():
        if key in basename:
            dest_name = val
            break
    
    if not dest_name:
        # If no mapping, just use the basename
        dest_name = basename

    dst = os.path.join(PERSONAGENS_DIR, dest_name)
    
    # Check if file exists, if so, maybe skip or overwrite?
    # Let's overwrite to ensure we have the generated version
    if not os.path.exists(dst):
        shutil.copy2(src, dst)
        print(f"Copied {basename} -> {dest_name}")
    else:
        print(f"Skipped {dest_name} (already exists)")

print("Done.")

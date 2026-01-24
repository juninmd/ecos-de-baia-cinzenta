
import os
import shutil
import glob
import re

ARTIFACT_DIR = r"C:/Users/jr_ac/.gemini/antigravity/brain/e3d53e6d-8e34-4de4-a5a1-655118d4581f"
PROJECT_ROOT = r"d:/Solutions/pessoal/meu-livro"
DOCS_DIR = os.path.join(PROJECT_ROOT, "docs")
PUBLIC_DIR = os.path.join(DOCS_DIR, "public")
PERSONAGENS_DIR = os.path.join(PUBLIC_DIR, "personagens")

def copy_images():
    print("--- Organizing Images ---")
    if not os.path.exists(PERSONAGENS_DIR):
        os.makedirs(PERSONAGENS_DIR)
    
    # 1. Copy generated images from Artifacts to Personagens dir
    mapping = {
        "gabo_moretti": "gabo.png",
        "valeria_cruz_realistic": "val.png", 
        "valeria_cruz_val": "val_old.png",
        "aria_entity": "aria.png",
        "elena_moretti_formerly_livia": "elena.png",
        "dante_moretti_biohost": "dante.png",
        "roberto_miranda_cyborg": "roberto.png",
        "elara_vance": "elara.png",
        "marco_moretti_mayor": "marco.png",
        "silas_vance_simple": "silas.png",
        "the_taxidermist": "taxidermista.png"
    }

    src_files = glob.glob(os.path.join(ARTIFACT_DIR, "*.png"))
    for src in src_files:
        basename = os.path.basename(src)
        for key, new_name in mapping.items():
            if key in basename:
                dst = os.path.join(PERSONAGENS_DIR, new_name)
                shutil.copy2(src, dst)
                print(f"Copied {src} to {dst}")

    # 2. Move existing non-chapter images to Personagens dir
    # Rule: Move if it doesn't start with "capitulo" and is an image
    public_files = glob.glob(os.path.join(PUBLIC_DIR, "*.*"))
    for f in public_files:
        if os.path.isdir(f): continue
        filename = os.path.basename(f)
        ext = os.path.splitext(filename)[1].lower()
        
        if ext in ['.jpg', '.jpeg', '.png', '.webp'] and not filename.startswith("capitulo"):
            dst = os.path.join(PERSONAGENS_DIR, filename)
            try:
                shutil.move(f, dst)
                print(f"Moved {filename} to /personagens/")
            except Exception as e:
                print(f"Error moving {filename}: {e}")

def rename_character():
    print("\n--- Renaming Lívia to Elena ---")
    files_to_check = glob.glob(os.path.join(DOCS_DIR, "**/*.md"), recursive=True)
    files_to_check += glob.glob(os.path.join(PROJECT_ROOT, ".gemini/*.md"))

    for fpath in files_to_check:
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            changes = 0
            # Text replacement
            if "Lívia" in content:
                content = content.replace("Lívia", "Elena")
                changes += 1
            
            # Image path updates (generic)
            # Replaces /public/filename.ext with /public/personagens/filename.ext ONLY if it's not a chapter image
            # But specific logic for characters is safer.
            # Let's fix specific known character references to point to /personagens/
            
            # Update known character image refs
            # Regex to find ![Alt](/filename.ext) and replace with ![Alt](/personagens/filename.ext)
            # We assume user uses absolute path from root or relative. 
            # Given the file view, it seems to be `![Alt](/filename.jpg)` which implies root is `docs/public` or configured that way?
            # Actually standard vitepress/doc site usually maps / to public. 
            # So `![Gabo](/gabo.jpg)` -> `![Gabo](/personagens/gabo.jpg)`
            
            def replace_image_path(match):
                alt = match.group(1)
                path = match.group(2)
                if "capitulo" not in path and "personagens" not in path:
                     return f"![{alt}](/personagens{path})"
                return match.group(0)

            new_content = re.sub(r'!\[(.*?)\]\((/.*?)\)', replace_image_path, content)
            if new_content != content:
                content = new_content
                changes += 1

            if changes > 0:
                with open(fpath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Updated {fpath}")
        except Exception as e:
            print(f"Error reading {fpath}: {e}")

def unify_timelines():
    print("\n--- Unifying Timelines ---")
    t1_path = os.path.join(PROJECT_ROOT, ".gemini", "linha_do_tempo.md")
    t2_path = os.path.join(PROJECT_ROOT, ".gemini", "cronologia.md")
    dest_path = os.path.join(PROJECT_ROOT, ".gemini", "linha_do_tempo_unificada.md")

    content = "# Timeline Unificada de Baía Cinzenta\n\n<spoilers>\n\n"
    
    if os.path.exists(t1_path):
        with open(t1_path, 'r', encoding='utf-8') as f:
            content += "## Resumo Narrativo (Original: Linha do Tempo)\n\n" + f.read() + "\n\n---\n\n"
    
    if os.path.exists(t2_path):
        with open(t2_path, 'r', encoding='utf-8') as f:
            content += "## Cronologia Detalhada\n\n" + f.read() + "\n\n"

    content += "</spoilers>\n"

    with open(dest_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created {dest_path}")

def rank_chapters():
    print("\n--- Ranking Chapters ---")
    chapters = glob.glob(os.path.join(DOCS_DIR, "capitulo-*.md"))
    results = []

    for cap in chapters:
        name = os.path.basename(cap)
        with open(cap, 'r', encoding='utf-8') as f:
            text = f.read()
        
        score = 10
        length = len(text)
        
        # Heuristics
        if length < 1000: score -= 2
        if length < 500: score -= 3 # severe penalty for placeholder
        if "TODO" in text: score -= 5
        if "Lorem ipsum" in text.lower(): score -= 8
        
        # Dialogue check
        if text.count("—") < 5 and text.count("- ") < 5:
             score -= 1 # Lack of dialogue might indicate dry summary
        
        # Clamp
        score = max(1, min(10, score))
        
        results.append((name, score))
        print(f"{name}: {score}")

    low_score = [r for r in results if r[1] < 9]
    print(f"\nChapters with score < 9: {len(low_score)}")
    for l in low_score:
        print(f"LOW SCORE: {l[0]} ({l[1]})")

if __name__ == "__main__":
    copy_images()
    rename_character()
    unify_timelines()
    rank_chapters()

import time
from pathlib import Path
from typing import Dict, Optional
from urllib.parse import quote

import requests

POLLINATIONS_URL = "https://image.pollinations.ai/prompt/{prompt}"
STYLE_SUFFIX = (
    "ultra cinematic, neo-noir cyberpunk, volumetric rain, dramatic lighting, "
    "film grain, masterpiece, 8k"
)
NEGATIVE = "text, watermark, logo, signature, deformed hands, extra limbs"


def build_prompt(titulo: str, meta: Dict[str, str], trecho: str = "") -> str:
    """Cinematic prompt from the chapter frontmatter — no LLM needed, so it stays free."""
    partes = [f"Cinematic key art for the chapter '{titulo}'"]
    if meta.get("Localização"):
        partes.append(f"setting: {meta['Localização']}")
    if meta.get("Personagens Presentes"):
        partes.append(f"characters: {meta['Personagens Presentes']}")
    if trecho:
        partes.append(f"scene: {trecho[:220]}")
    partes.append(STYLE_SUFFIX)
    return ". ".join(partes)


def generate_image(
    prompt: str,
    output_path: Path,
    seed: int = 0,
    width: int = 1280,
    height: int = 720,
    retries: int = 3,
) -> Optional[Path]:
    """Generate artwork via Pollinations (free, keyless). Returns None on failure."""
    url = POLLINATIONS_URL.format(prompt=quote(prompt[:1500]))
    params = {
        "width": width,
        "height": height,
        "seed": seed,
        "model": "flux",
        "nologo": "true",
        "negative": NEGATIVE,
    }
    for attempt in range(1, retries + 1):
        try:
            print(f"🎨 Gerando arte (tentativa {attempt}/{retries})...")
            response = requests.get(url, params=params, timeout=180)
            response.raise_for_status()
            if not response.content or len(response.content) < 2048:
                raise ValueError("resposta vazia ou muito pequena")
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(response.content)
            print(f"✅ Arte salva: {output_path} ({len(response.content) // 1024} KB)")
            return output_path
        except (requests.RequestException, ValueError) as exc:
            print(f"⚠ Falha na geração de arte: {exc}")
            if attempt < retries:
                time.sleep(5 * attempt)
    print("❌ Não foi possível gerar a arte; seguindo sem imagem nova.")
    return None

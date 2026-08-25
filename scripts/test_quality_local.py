"""Teste isolado de qualidade — GPU local, parametros melhorados.

NAO toca em nenhum arquivo existente. Gera para uma pasta de teste separada.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import torch
from diffusers import AutoPipelineForText2Image
from transformers import CLIPVisionModelWithProjection
from PIL import Image

from scripts.art_gen.chapters import extract_chapter_title_and_clean_text
from scripts.daily_telegram import scenes, characters

BASE_MODEL = "SG161222/RealVisXL_V5.0"  # fine-tune fotorrealista, mesma arquitetura SDXL (IP-Adapter compatível)
IP_ADAPTER_REPO = "h94/IP-Adapter"
IP_ADAPTER_WEIGHT = "ip-adapter-plus-face_sdxl_vit-h.safetensors"
NEGATIVE = (
    "different person, changed face, deformed face, extra limbs, text, watermark, "
    "logo, blurry, low quality, low resolution, jpeg artifacts, soft focus, grain, noise"
)

DESTINO = Path(__file__).resolve().parent.parent / "docs" / "public" / "cenas" / "_teste_qualidade"
DESTINO.mkdir(parents=True, exist_ok=True)


def carregar_texto_capitulo_1():
    raw = (Path(__file__).resolve().parent.parent / "docs" / "capitulo-1.md").read_text(encoding="utf-8")
    title, body = extract_chapter_title_and_clean_text(raw)
    objs = scenes.split_scenes(body, quantidade=10)
    return title, objs[0]  # cena 1 (texto), so para o prompt -- nao mexe no arquivo cena_1.jpg


def main():
    print("Carregando SDXL + IP-Adapter (parametros melhorados)...")
    image_encoder = CLIPVisionModelWithProjection.from_pretrained(
        IP_ADAPTER_REPO, subfolder="models/image_encoder", torch_dtype=torch.float16
    )
    pipe = AutoPipelineForText2Image.from_pretrained(
        BASE_MODEL, image_encoder=image_encoder, torch_dtype=torch.float16,
        variant="fp16", use_safetensors=True,
    )
    pipe.load_ip_adapter(IP_ADAPTER_REPO, subfolder="sdxl_models", weight_name=IP_ADAPTER_WEIGHT)
    pipe.set_ip_adapter_scale(0.85)
    pipe.enable_model_cpu_offload()
    pipe.set_progress_bar_config(disable=True)
    print("Pipeline pronto.")

    title, cena = carregar_texto_capitulo_1()
    anchor = characters.pick_anchor(characters.detect(cena.texto))
    if not anchor:
        # cena 1 do cap. 1 pode nao ter personagem catalogado; forca Gabo (protagonista)
        db = characters.get_db()
        anchor = next(c for c in db.characters if "Gabo" in c["name"] or "Gabriel" in c["name"])
    referencia_path = characters.reference_image(anchor)
    print(f"Personagem ancora: {anchor['name']}  |  referencia: {referencia_path}")

    prompt = cena.compact_prompt(anchor) if hasattr(cena, "compact_prompt") else (
        f"{anchor['name']} in a cyberpunk noir crime scene, night, neon lighting, "
        "cinematic composition, rain-slicked street, detailed"
    )
    print(f"Prompt: {prompt}")

    referencia = Image.open(referencia_path).convert("RGB")
    gerador = torch.Generator(device="cuda").manual_seed(101)

    # Parametros melhorados: resolucao nativa SDXL 16:9 (1344x768, bucket valido -
    # menos artefato que redimensionar livre), mais passos (40 vs 22), guidance 7.5.
    imagem = pipe(
        prompt=prompt[:900],
        negative_prompt=NEGATIVE,
        ip_adapter_image=referencia,
        num_inference_steps=40,
        guidance_scale=7.5,
        width=1344,
        height=768,
        generator=gerador,
    ).images[0]

    destino = DESTINO / "capitulo_1_teste_realvisxl.jpg"
    imagem.save(destino, quality=95)
    print(f"Salvo: {destino}")


if __name__ == "__main__":
    main()

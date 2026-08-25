"""Lote de teste de qualidade — RealVisXL, 3+ capitulos diferentes.

NAO toca em nenhum arquivo existente. Gera para pasta de teste separada.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import requests
import torch
from diffusers import AutoPipelineForText2Image
from transformers import CLIPVisionModelWithProjection
from PIL import Image

from scripts.art_gen.chapters import extract_chapter_title_and_clean_text, limpar_titulos
from scripts.daily_telegram import scenes, characters

def _carregar_dotenv():
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        return
    for linha in env_path.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        chave, _, valor = linha.partition("=")
        os.environ.setdefault(chave.strip(), valor.strip().strip('"').strip("'"))


_carregar_dotenv()
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


def enviar_telegram(caminho: Path, legenda: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("  (sem TELEGRAM_BOT_TOKEN/CHAT_ID, pulando envio)")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    with open(caminho, "rb") as f:
        resp = requests.post(
            url, data={"chat_id": TELEGRAM_CHAT_ID, "caption": legenda},
            files={"photo": f}, timeout=60,
        )
    if resp.ok:
        print(f"  -> enviado ao Telegram: {legenda}")
    else:
        print(f"  -> falha no envio Telegram: {resp.status_code} {resp.text[:200]}")

BASE_MODEL = "RunDiffusion/Juggernaut-XL-v9"
MODEL_LABEL = "Juggernaut XL v9"
IP_ADAPTER_REPO = "h94/IP-Adapter"
IP_ADAPTER_WEIGHT = "ip-adapter-plus-face_sdxl_vit-h.safetensors"
NEGATIVE = (
    "different person, changed face, deformed face, wrong gender, extra limbs, text, "
    "watermark, logo, blurry, low quality, low resolution, jpeg artifacts, soft focus, "
    "grain, noise, nude, nudity, nsfw, exposed breasts, bare chest, shirtless, topless, "
    "underwear, lingerie, sexualized, explicit"
)
NEGATIVE_WIDE = NEGATIVE + (
    ", close-up, extreme close-up, portrait, headshot, face fills frame, id photo, "
    "passport photo, selfie, cropped body, studio backdrop, plain background, "
    "catalog photo, fashion lookbook, product shot, white background"
)

DESTINO = Path(__file__).resolve().parent.parent / "docs" / "public" / "cenas" / "_teste_qualidade"
DESTINO.mkdir(parents=True, exist_ok=True)

# (numero do capitulo, indice da cena a usar, seed)
# indices escolhidos para bater em planos "wide" (identity_scale baixo) -
# e' exatamente o que o usuario reclamou que nao estava saindo.
ALVOS = [
    (218, 1, 21801),  # wide establishing shot (indice 9 = "two-shot" nao combinava com cena solo)
]


def carregar_cena(numero: int, indice: int):
    raw = (Path(__file__).resolve().parent.parent / "docs" / f"capitulo-{numero}.md").read_text(encoding="utf-8")
    title, body = extract_chapter_title_and_clean_text(raw)
    title, body = limpar_titulos(title, body)
    objs = scenes.split_scenes(body, quantidade=max(indice, 3))
    idx = min(indice, len(objs)) - 1
    return title, objs[idx]


def main():
    print("Carregando RealVisXL + IP-Adapter...")
    image_encoder = CLIPVisionModelWithProjection.from_pretrained(
        IP_ADAPTER_REPO, subfolder="models/image_encoder", torch_dtype=torch.float16
    )
    pipe = AutoPipelineForText2Image.from_pretrained(
        BASE_MODEL, image_encoder=image_encoder, torch_dtype=torch.float16,
        variant="fp16", use_safetensors=True,
    )
    pipe.load_ip_adapter(IP_ADAPTER_REPO, subfolder="sdxl_models", weight_name=IP_ADAPTER_WEIGHT)
    pipe.enable_model_cpu_offload()
    pipe.set_progress_bar_config(disable=True)
    print("Pipeline pronto.\n")

    for numero, indice, seed in ALVOS:
        title, cena = carregar_cena(numero, indice)
        detected = characters.detect(cena.texto)
        anchor = characters.pick_anchor(detected)
        if not anchor:
            db = characters.get_db()
            anchor = next(c for c in db.characters if "Gabo" in c["name"] or "Gabriel" in c["name"])
        referencia_path = characters.reference_image(anchor)
        print(f"[cap {numero}] titulo={title!r} ancora={anchor['name']} ref={referencia_path}")

        if referencia_path is None:
            print(f"  -> sem retrato de referencia para {anchor['name']}, pulando.\n")
            continue

        prompt = cena.compact_prompt(anchor) if hasattr(cena, "compact_prompt") else (
            f"{anchor['name']} in a cyberpunk noir scene, cinematic, detailed"
        )
        is_wide = "wide" in cena.shot
        escala = cena.identity_scale  # 0.3 quebrava identidade/genero (Regra Zero) - volta ao valor do projeto
        negativo = NEGATIVE_WIDE if is_wide else NEGATIVE
        prompt = f"({cena.shot}), full body in frame, " + prompt
        print(f"  shot={cena.shot!r} identity_scale={escala} (era {cena.identity_scale})")
        print(f"  prompt={prompt}")
        pipe.set_ip_adapter_scale(escala)
        referencia = Image.open(referencia_path).convert("RGB")
        gerador = torch.Generator(device="cuda").manual_seed(seed)

        imagem = pipe(
            prompt=prompt[:900],
            negative_prompt=negativo,
            ip_adapter_image=referencia,
            num_inference_steps=40,
            guidance_scale=7.5,
            width=1344,
            height=768,
            generator=gerador,
        ).images[0]

        destino = DESTINO / f"capitulo_{numero}_teste_{MODEL_LABEL.lower().replace(' ', '_')}.jpg"
        imagem.save(destino, quality=95)
        print(f"  -> salvo: {destino}")
        if os.environ.get("TESTE_ENVIA_TELEGRAM") == "1":
            enviar_telegram(destino, f"Capítulo {numero} — modelo: {MODEL_LABEL} — plano: {cena.shot}")
        else:
            print("  (envio ao Telegram desativado; revisar antes de enviar)")
        print()


if __name__ == "__main__":
    main()

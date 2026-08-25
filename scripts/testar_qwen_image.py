"""Teste do Qwen-Image (GGUF Q2_K) contra as imagens do Gemini.

Mesma limitacao do FLUX, e vale repetir: nao ha IP-Adapter plus-face para esta
arquitetura, entao plano com personagem quebraria a Regra Zero. O teste roda so
nos planos de AMBIENTE (identity_scale 0.0), que sao ~40% das cenas e nao usam
ancora de identidade.

Memoria: o transformer vem quantizado em GGUF Q2_K (7.1 GB em vez de 40.9) e o
text encoder entra em 4-bit (5 GB em vez de 16.6). O FLUX em bf16 pedia ~35 GB
de working set numa maquina de 31.9 GB -- foi o que a travou.
"""
import argparse
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import requests
import torch
from diffusers import (QwenImagePipeline, QwenImageTransformer2DModel,
                       GGUFQuantizationConfig)
from PIL import Image

from scripts.art_gen.chapters import extract_chapter_title_and_clean_text, limpar_titulos
from scripts.daily_telegram import scenes

GGUF_REPO = "QuantStack/Qwen-Image-GGUF"
GGUF_FILE = "Qwen_Image-Q2_K.gguf"
BASE_REPO = "Qwen/Qwen-Image"
MODEL_LABEL = "Qwen-Image Q2_K"

DESTINO = REPO / "docs" / "public" / "cenas" / "_teste_qualidade"
DESTINO.mkdir(parents=True, exist_ok=True)

ALVOS = [(25, 1, 2501), (8, 9, 809)]
W, H = 1376, 768


def _dotenv():
    p = REPO / ".env"
    if not p.exists():
        return
    for linha in p.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if linha and not linha.startswith("#") and "=" in linha:
            k, _, v = linha.partition("=")
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_dotenv()


def enviar(caminho, legenda):
    tok = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat = os.environ.get("TELEGRAM_CHAT_ID")
    if not tok or not chat:
        print("  (sem credenciais Telegram)")
        return
    with open(caminho, "rb") as f:
        r = requests.post(f"https://api.telegram.org/bot{tok}/sendPhoto",
                          data={"chat_id": chat, "caption": legenda[:1024]},
                          files={"photo": f}, timeout=120)
    print(f"  telegram: {r.status_code}")


def lado_a_lado(gemini, local, saida):
    a = Image.open(gemini).convert("RGB")
    b = Image.open(local).convert("RGB")
    h = min(a.height, b.height)
    a = a.resize((int(a.width * h / a.height), h))
    b = b.resize((int(b.width * h / b.height), h))
    combo = Image.new("RGB", (a.width + b.width + 12, h), (20, 20, 20))
    combo.paste(a, (0, 0)); combo.paste(b, (a.width + 12, 0))
    combo.save(saida, quality=94)
    return saida


def carregar_cena(numero, indice):
    raw = (REPO / "docs" / f"capitulo-{numero}.md").read_text(encoding="utf-8")
    _, corpo = limpar_titulos(*extract_chapter_title_and_clean_text(raw))
    cena = scenes.split_scenes(corpo, quantidade=10)[indice - 1]
    cena.indice = indice
    return cena


def montar_prompt(cena):
    """Qwen-Image usa encoder proprio, sem o teto de 77 tokens do CLIP."""
    partes = [
        cena.shot,
        scenes.cenario_do_texto(cena.texto),
        "gritty cyberpunk Brazil, desaturated grimy colors, dramatic lighting",
        scenes.palavras_visuais(cena.texto, limite=5),
        "weathered surfaces, layered depth, foreground detail, cinematic film still, "
        "highly detailed",
    ]
    return ", ".join(p for p in partes if p)


# O Qwen obedece ao pe da letra: pedir "Brazilian storefronts" no positivo fazia ele
# pintar a bandeira do Brasil em TODA cena, inclusive dentro de um laboratorio.
# A brasilidade fica so no ESTILO_MUNDO ("cyberpunk brazil"), e o negativo cuida
# do que nao pode aparecer.
NEGATIVO = ("close-up, portrait, headshot, posing for camera, id photo, "
            "chinese text, japanese text, kanji, brazilian flag, national flag, "
            "oversaturated, blurry, low quality")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rodada", default="qwen1")
    args = ap.parse_args()

    print(f"Carregando {MODEL_LABEL}...")
    transformer = QwenImageTransformer2DModel.from_single_file(
        f"https://huggingface.co/{GGUF_REPO}/blob/main/{GGUF_FILE}",
        quantization_config=GGUFQuantizationConfig(compute_dtype=torch.bfloat16),
        torch_dtype=torch.bfloat16,
        config=BASE_REPO, subfolder="transformer",
    )
    pipe = QwenImagePipeline.from_pretrained(
        BASE_REPO, transformer=transformer, torch_dtype=torch.bfloat16,
    )
    pipe.enable_model_cpu_offload()
    pipe.set_progress_bar_config(disable=True)
    print("pronto\n")

    for numero, indice, seed in ALVOS:
        cena = carregar_cena(numero, indice)
        if cena.identity_scale > 0:
            print(f"[cap {numero} cena {indice}] plano com personagem, pulando (sem IP-Adapter)")
            continue
        prompt = montar_prompt(cena)
        print(f"[cap {numero} cena {indice}] shot={cena.shot!r}")
        print(f"  {prompt[:160]}")

        img = pipe(
            prompt=prompt, negative_prompt=NEGATIVO,
            num_inference_steps=30, true_cfg_scale=4.0,
            width=W, height=H,
            generator=torch.Generator("cpu").manual_seed(seed),
        ).images[0]

        local = DESTINO / f"QWEN2_cap{numero}_cena{indice}.jpg"
        img.save(local, quality=95)
        print(f"  -> {local.name}")

        gemini = REPO / "docs" / "public" / "cenas" / f"capitulo_{numero}" / f"cena_{indice}.jpg"
        if gemini.exists():
            combo = lado_a_lado(gemini, local,
                                DESTINO / f"COMPARA_QWEN2_cap{numero}_cena{indice}.jpg")
            enviar(combo, f"Capitulo {numero} cena {indice} | ESQ=Gemini DIR={MODEL_LABEL} | {cena.shot}")
        else:
            enviar(local, f"Capitulo {numero} cena {indice} | {MODEL_LABEL} | {cena.shot}")
        print()


if __name__ == "__main__":
    main()

"""Teste do FLUX.1-dev contra as imagens do Gemini, nas mesmas cenas do ZavyChromaXL.

Duas diferencas de metodo em relacao ao SDXL, que mudam o que da para comparar:

1. FLUX nao aceita prompt negativo. O modelo e guidance-distilled: nao ha CFG, entao
   todos os negativos que fizeram diferenca no Zavy (anti-retrato, anti-nudez,
   anti-placa-asiatica) simplesmente nao existem aqui. O que der para pedir tem de
   entrar no prompt positivo.
2. FLUX usa T5 (512 tokens) em vez do CLIP de 77. O prompt pode ser longo e descritivo
   -- some o corte por prioridade que eu tive de construir para o SDXL.

Por isso o teste roda so nos planos de AMBIENTE (identity_scale 0.0): o IP-Adapter
plus-face e SDXL e nao funciona no FLUX, entao plano com personagem quebraria a
Regra Zero. Planos de ambiente sao ~40% das cenas e nao dependem de ancora.
"""
import argparse
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import requests
import torch
from diffusers import FluxPipeline
from PIL import Image

from scripts.art_gen.chapters import extract_chapter_title_and_clean_text, limpar_titulos
from scripts.daily_telegram import scenes

BASE_MODEL = "black-forest-labs/FLUX.1-dev"
MODEL_LABEL = "FLUX.1-dev"

DESTINO = REPO / "docs" / "public" / "cenas" / "_teste_qualidade"
DESTINO.mkdir(parents=True, exist_ok=True)

# Mesmas cenas usadas para escolher o Zavy, para a comparacao ser direta.
ALVOS = [(38, 1, 3801), (1, 1, 101), (25, 1, 2501), (8, 9, 809)]

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


def enviar(caminho: Path, legenda: str):
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


def lado_a_lado(gemini: Path, local: Path, saida: Path) -> Path:
    a = Image.open(gemini).convert("RGB")
    b = Image.open(local).convert("RGB")
    altura = min(a.height, b.height)
    a = a.resize((int(a.width * altura / a.height), altura))
    b = b.resize((int(b.width * altura / b.height), altura))
    combo = Image.new("RGB", (a.width + b.width + 12, altura), (20, 20, 20))
    combo.paste(a, (0, 0))
    combo.paste(b, (a.width + 12, 0))
    combo.save(saida, quality=94)
    return saida


def carregar_cena(numero: int, indice: int):
    raw = (REPO / "docs" / f"capitulo-{numero}.md").read_text(encoding="utf-8")
    titulo, corpo = limpar_titulos(*extract_chapter_title_and_clean_text(raw))
    objs = scenes.split_scenes(corpo, quantidade=10)
    cena = objs[min(indice, len(objs)) - 1]
    cena.indice = indice
    return titulo, cena


def prompt_flux(cena) -> str:
    """Sem limite de 77 tokens e sem negativo: tudo tem de ser dito no positivo."""
    partes = [
        cena.shot,
        scenes.cenario_do_texto(cena.texto),
        "gritty cyberpunk Brazil, desaturated grimy colors, dramatic lighting",
        scenes.palavras_visuais(cena.texto, limite=5),
        # No SDXL isto era prompt negativo; aqui vira afirmacao.
        "signage written in Portuguese, Brazilian storefronts",
        "weathered surfaces, layered depth, foreground detail, cinematic film still, "
        "highly detailed, no people posing for the camera",
    ]
    return ", ".join(p for p in partes if p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rodada", default="flux1")
    args = ap.parse_args()

    print(f"Carregando {MODEL_LABEL} (offload para CPU: o transformer nao cabe em 16GB)...")
    pipe = FluxPipeline.from_pretrained(BASE_MODEL, torch_dtype=torch.bfloat16)
    pipe.enable_model_cpu_offload()
    pipe.set_progress_bar_config(disable=True)
    print("pronto\n")

    for numero, indice, seed in ALVOS:
        gemini = REPO / "docs" / "public" / "cenas" / f"capitulo_{numero}" / f"cena_{indice}.jpg"
        titulo, cena = carregar_cena(numero, indice)
        if cena.identity_scale > 0:
            print(f"[cap {numero} cena {indice}] plano com personagem, pulando (FLUX sem IP-Adapter)")
            continue

        prompt = prompt_flux(cena)
        print(f"[cap {numero} cena {indice}] shot={cena.shot!r}")
        print(f"  {prompt[:170]}")

        img = pipe(
            prompt=prompt,
            num_inference_steps=28,
            guidance_scale=3.5,          # FLUX.1-dev trabalha bem mais baixo que SDXL
            width=W, height=H,
            generator=torch.Generator("cpu").manual_seed(seed),
        ).images[0]

        local = DESTINO / f"FLUX_cap{numero}_cena{indice}.jpg"
        img.save(local, quality=95)
        print(f"  -> {local.name}")

        if gemini.exists():
            combo = lado_a_lado(gemini, local, DESTINO / f"COMPARA_FLUX_cap{numero}_cena{indice}.jpg")
            enviar(combo, f"Capitulo {numero} cena {indice} | ESQ=Gemini DIR={MODEL_LABEL} | {cena.shot}")
        else:
            enviar(local, f"Capitulo {numero} cena {indice} | {MODEL_LABEL} | {cena.shot}")
        print()


if __name__ == "__main__":
    main()

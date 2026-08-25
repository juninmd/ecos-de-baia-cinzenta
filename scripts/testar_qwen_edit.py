"""Qwen-Image-Edit-2509 (GGUF Q2_K): personagem de referencia colocado na cena.

Diferente dos testes anteriores. Aqui o alvo NAO e o ambiente -- e a Regra Zero:
a fisionomia do personagem nao pode mudar. E a mesma abordagem do agy/Gemini
(referencia + instrucao), que segundo a memoria do projeto e a unica rota que
preserva rosto E vestuario.

Compara contra o que o Zavy+IP-Adapter produz na mesma cena. O IP-Adapter obrigou
a baixar o peso de identidade para 0.30 (senao a composicao virava retrato 3x4),
e a 0.30 a semelhanca fica solta. Se o Edit preservar melhor sem esse custo,
muda a decisao de qual modelo faz as cenas com personagem.
"""
import argparse
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import requests
import torch
from diffusers import (QwenImageEditPlusPipeline, QwenImageTransformer2DModel,
                       GGUFQuantizationConfig)
from PIL import Image

from scripts.art_gen.chapters import extract_chapter_title_and_clean_text, limpar_titulos
from scripts.daily_telegram import scenes, characters

GGUF_REPO = "QuantStack/Qwen-Image-Edit-2509-GGUF"
GGUF_FILE = "Qwen-Image-Edit-2509-Q2_K.gguf"
BASE_REPO = "Qwen/Qwen-Image-Edit-2509"
MODEL_LABEL = "Qwen-Image-Edit-2509 Q2_K"

DESTINO = REPO / "docs" / "public" / "cenas" / "_teste_qualidade"
DESTINO.mkdir(parents=True, exist_ok=True)

# Cenas COM personagem, que e onde o Zavy tem o problema de semelhanca.
# Variedade proposital: personagens diferentes e tipos de plano diferentes,
# para ver se a fidelidade se sustenta fora do Gabo.
ALVOS = [
    (9, 7, 907),
    (33, 2, 3302),
    (38, 3, 3803),
    (218, 3, 21803),
    (25, 3, 2503),
    (12, 2, 1202),
]
W, H = 1376, 768


def _dotenv():
    p = REPO / ".env"
    for linha in p.read_text(encoding="utf-8").splitlines() if p.exists() else []:
        linha = linha.strip()
        if linha and not linha.startswith("#") and "=" in linha:
            k, _, v = linha.partition("=")
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_dotenv()


def enviar(caminho, legenda):
    tok = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat = os.environ.get("TELEGRAM_CHAT_ID")
    if not tok or not chat:
        print("  (sem credenciais Telegram)"); return
    with open(caminho, "rb") as f:
        r = requests.post(f"https://api.telegram.org/bot{tok}/sendPhoto",
                          data={"chat_id": chat, "caption": legenda[:1024]},
                          files={"photo": f}, timeout=120)
    print(f"  telegram: {r.status_code}")


def trio(ref, zavy, edit, saida):
    """Referencia | Zavy+IP-Adapter | Qwen-Edit -- lado a lado, mesma altura."""
    ims = [Image.open(p).convert("RGB") for p in (ref, zavy, edit) if p and Path(p).exists()]
    h = min(i.height for i in ims)
    ims = [i.resize((int(i.width * h / i.height), h)) for i in ims]
    larg = sum(i.width for i in ims) + 12 * (len(ims) - 1)
    combo = Image.new("RGB", (larg, h), (20, 20, 20))
    x = 0
    for i in ims:
        combo.paste(i, (x, 0)); x += i.width + 12
    combo.save(saida, quality=94)
    return saida


def carregar_cena(numero, indice):
    raw = (REPO / "docs" / f"capitulo-{numero}.md").read_text(encoding="utf-8")
    _, corpo = limpar_titulos(*extract_chapter_title_and_clean_text(raw))
    cena = scenes.split_scenes(corpo, quantidade=10)[indice - 1]
    cena.indice = indice
    return cena


def instrucao(cena, anchor):
    """Instrucao de edicao para o Qwen-Edit.

    A primeira versao pedia so "mantenha o rosto e coloque nesta cena": o modelo
    recortava a referencia e trocava o fundo -- mesma pose, mesmo angulo, o mesmo
    copo na mesma mao. Dez cenas de um capitulo virariam dez retratos iguais.

    Entao a instrucao agora separa o que PRESERVA do que MUDA, e pede a mudanca de
    postura de forma explicita, com a acao da cena como motivo.
    """
    roupa = characters.wardrobe(anchor)
    acao = scenes.palavras_visuais(cena.texto, limite=4)
    encenacao = scenes.ENCENACAO.get(cena.shot, scenes.ENCENACAO_PADRAO)

    partes = [
        # PRESERVAR
        "Keep the same person: identical face, beard, hair and skin.",
    ]
    if roupa:
        partes.append(f"Keep the same outfit: {roupa[:70]}.")
    partes += [
        # MUDAR -- e a parte que faltava
        "Change the pose and the camera completely: this is a NEW photograph of him, "
        "not the same photo with a different background.",
        f"New framing: {cena.shot}, {encenacao}."
        " He is close to the camera, upper body large in the frame, face sharp and"
        " clearly readable -- but caught mid-action, never posing.",
        f"He is doing something in the scene: {acao}." if acao else
        "He is in the middle of an action, not standing still and posing.",
        f"Setting: {scenes.cenario_do_texto(cena.texto)}.",
        "Gritty cyberpunk Brazil, desaturated grimy colors, dramatic lighting, "
        "cinematic film still.",
    ]
    return " ".join(partes)


NEGATIVO = ("different person, changed face, deformed face, "
            # Contra o modo "recorte com fundo novo":
            "same pose as reference, copy of the input photo, cut-out person, "
            "pasted subject, standing still, posing for camera, headshot, "
            "chinese text, japanese text, brazilian flag, oversaturated, blurry")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--rodada", default="edit1")
    args = ap.parse_args()

    print(f"Carregando {MODEL_LABEL}...")
    transformer = QwenImageTransformer2DModel.from_single_file(
        f"https://huggingface.co/{GGUF_REPO}/blob/main/{GGUF_FILE}",
        quantization_config=GGUFQuantizationConfig(compute_dtype=torch.bfloat16),
        torch_dtype=torch.bfloat16, config=BASE_REPO, subfolder="transformer",
    )
    pipe = QwenImageEditPlusPipeline.from_pretrained(
        BASE_REPO, transformer=transformer, torch_dtype=torch.bfloat16)
    pipe.enable_model_cpu_offload()
    pipe.set_progress_bar_config(disable=True)
    print("pronto\n")

    for numero, indice, seed in ALVOS:
        cena = carregar_cena(numero, indice)
        anchor = characters.pick_anchor(cena.personagens)
        if not anchor:
            print(f"[cap {numero} cena {indice}] sem ancora, pulando"); continue
        ref = characters.reference_image(anchor)
        if not ref:
            print(f"[cap {numero} cena {indice}] sem retrato de {anchor['name']}, pulando"); continue

        prompt = instrucao(cena, anchor)
        print(f"[cap {numero} cena {indice}] {anchor['name']} | shot={cena.shot!r}")
        print(f"  {prompt[:170]}")

        img = pipe(
            image=[Image.open(ref).convert("RGB")],
            prompt=prompt, negative_prompt=NEGATIVO,
            num_inference_steps=30, true_cfg_scale=4.0,
            width=W, height=H,
            generator=torch.Generator("cpu").manual_seed(seed),
        ).images[0]

        local = DESTINO / f"QE_cap{numero}_cena{indice}.jpg"
        img.save(local, quality=95)
        print(f"  -> {local.name}")

        # A cena que o Zavy ja gerou, para o confronto direto.
        zavy = REPO / "docs" / "public" / "cenas" / f"capitulo_{numero}" / f"cena_{indice}.jpg"
        combo = trio(ref, zavy if zavy.exists() else None, local,
                     DESTINO / f"COMPARA_QE_cap{numero}_cena{indice}.jpg")
        enviar(combo, f"Capitulo {numero} cena {indice} | {anchor['name']} | "
                      f"REF | Zavy+IPAdapter | {MODEL_LABEL}")
        print()


if __name__ == "__main__":
    main()

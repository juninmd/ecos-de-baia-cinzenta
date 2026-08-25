"""Varredura de parametros do Qwen-Image-Edit-2511: qualidade x velocidade.

A ~4 min/imagem as 1.200 cenas que faltam levam 80 h. O passo (num_inference_steps)
e o parametro que domina o tempo -- e linear nele. Entao a pergunta que importa e:
qual o menor numero de passos que ainda entrega imagem aceitavel.

Carrega o modelo UMA vez e varre em memoria; recarregar por combinacao custaria
~3 min de desquantizacao GGUF a cada teste.
Monta um contact sheet rotulado para comparacao direta, e mede o tempo real de cada.
"""
import os
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import requests
import torch
from diffusers import (QwenImageEditPlusPipeline, QwenImageTransformer2DModel,
                       GGUFQuantizationConfig)
from PIL import Image, ImageDraw

from scripts.art_gen.chapters import extract_chapter_title_and_clean_text, limpar_titulos
from scripts.daily_telegram import scenes, characters

GGUF_REPO = "unsloth/Qwen-Image-Edit-2511-GGUF"
GGUF_FILE = "qwen-image-edit-2511-Q2_K.gguf"
BASE_REPO = "Qwen/Qwen-Image-Edit-2511"

DESTINO = REPO / "docs" / "public" / "cenas" / "_teste_qualidade" / "varredura"
DESTINO.mkdir(parents=True, exist_ok=True)

CAP, CENA, SEED = 9, 7, 907          # cena que a 2511 acertou: base justa de comparacao
W, H = 1376, 768

# Fase 1: passo domina o tempo. Fase 2 varre cfg no melhor passo.
PASSOS = [4, 8, 12, 20, 30]
CFG_PADRAO = 4.0
CFGS = [2.5, 4.0, 6.0]

NEGATIVO = ("different person, changed face, deformed face, "
            "same pose as reference, copy of the input photo, cut-out person, "
            "pasted subject, standing still, posing for camera, headshot, "
            "chinese text, japanese text, brazilian flag, oversaturated, blurry")


def _dotenv():
    p = REPO / ".env"
    for linha in (p.read_text(encoding="utf-8").splitlines() if p.exists() else []):
        linha = linha.strip()
        if linha and not linha.startswith("#") and "=" in linha:
            k, _, v = linha.partition("=")
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_dotenv()


def enviar(caminho, legenda):
    tok, chat = os.environ.get("TELEGRAM_BOT_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
    if not tok or not chat:
        print("  (sem Telegram)"); return
    with open(caminho, "rb") as f:
        r = requests.post(f"https://api.telegram.org/bot{tok}/sendPhoto",
                          data={"chat_id": chat, "caption": legenda[:1024]},
                          files={"photo": f}, timeout=120)
    print(f"  telegram: {r.status_code}")


def contact_sheet(itens, saida, titulo):
    """itens = [(rotulo, caminho)] -- grade rotulada, 3 por linha."""
    ims = [(r, Image.open(p).convert("RGB")) for r, p in itens]
    cols = min(3, len(ims))
    linhas = (len(ims) + cols - 1) // cols
    lw = 460
    lh = int(lw * H / W)
    faixa = 26
    sheet = Image.new("RGB", (cols * lw, linhas * (lh + faixa)), (18, 18, 18))
    d = ImageDraw.Draw(sheet)
    for i, (rot, im) in enumerate(ims):
        x, y = (i % cols) * lw, (i // cols) * (lh + faixa)
        sheet.paste(im.resize((lw, lh)), (x, y + faixa))
        d.text((x + 6, y + 7), rot, fill=(235, 235, 235))
    sheet.save(saida, quality=95)
    print(f"  contact sheet: {saida.name}  [{titulo}]")
    return saida


def carregar_cena():
    raw = (REPO / "docs" / f"capitulo-{CAP}.md").read_text(encoding="utf-8")
    _, corpo = limpar_titulos(*extract_chapter_title_and_clean_text(raw))
    cena = scenes.split_scenes(corpo, quantidade=10)[CENA - 1]
    cena.indice = CENA
    return cena


def instrucao(cena, anchor):
    roupa = characters.wardrobe(anchor)
    acao = scenes.palavras_visuais(cena.texto, limite=4)
    partes = ["Keep the same person: identical face, beard, hair and skin."]
    if roupa:
        partes.append(f"Keep the same outfit: {roupa[:70]}.")
    partes += [
        "Change the pose and the camera completely: this is a NEW photograph of him, "
        "not the same photo with a different background.",
        f"New framing: {cena.shot}, {scenes.ENCENACAO.get(cena.shot, scenes.ENCENACAO_PADRAO)}."
        " He is close to the camera, upper body large in the frame, face sharp and"
        " clearly readable -- but caught mid-action, never posing.",
        f"He is doing something in the scene: {acao}." if acao else
        "He is in the middle of an action, not standing still.",
        f"Setting: {scenes.cenario_do_texto(cena.texto)}.",
        "Gritty cyberpunk Brazil, desaturated grimy colors, dramatic lighting, "
        "cinematic film still.",
    ]
    return " ".join(partes)


def main():
    print("Carregando Qwen-Image-Edit-2511 Q2_K (uma vez para toda a varredura)...")
    t0 = time.time()
    transformer = QwenImageTransformer2DModel.from_single_file(
        f"https://huggingface.co/{GGUF_REPO}/blob/main/{GGUF_FILE}",
        quantization_config=GGUFQuantizationConfig(compute_dtype=torch.bfloat16),
        dtype=torch.bfloat16, config=BASE_REPO, subfolder="transformer")
    pipe = QwenImageEditPlusPipeline.from_pretrained(
        BASE_REPO, transformer=transformer, dtype=torch.bfloat16)
    pipe.enable_model_cpu_offload()
    pipe.set_progress_bar_config(disable=True)
    print(f"carregado em {time.time()-t0:.0f}s\n")

    cena = carregar_cena()
    anchor = characters.pick_anchor(cena.personagens)
    ref = Image.open(characters.reference_image(anchor)).convert("RGB")
    prompt = instrucao(cena, anchor)
    print(f"cena: cap {CAP} cena {CENA} | {anchor['name']} | {cena.shot}\n")

    def gerar(passos, cfg, tag):
        t = time.time()
        img = pipe(image=[ref], prompt=prompt, negative_prompt=NEGATIVO,
                   num_inference_steps=passos, true_cfg_scale=cfg,
                   width=W, height=H,
                   generator=torch.Generator("cpu").manual_seed(SEED)).images[0]
        seg = time.time() - t
        p = DESTINO / f"{tag}.jpg"
        img.save(p, quality=95)
        print(f"  {tag:22s} {seg:6.1f}s")
        # Envia na hora: se a execucao for interrompida, o que ja saiu chegou ao autor.
        enviar(p, f"Qwen-Image-Edit-2511 Q2_K | cap {CAP} cena {CENA} | {tag} | "
                  f"{seg:.0f}s/img -> {seg*1200/3600:.1f} h nas 1.200 cenas restantes")
        return seg, p

    print("=== FASE 1: passos (cfg fixo em %.1f)" % CFG_PADRAO)
    itens, tempos = [], {}
    for passos in PASSOS:
        seg, p = gerar(passos, CFG_PADRAO, f"passos{passos:02d}")
        tempos[passos] = seg
        itens.append((f"{passos} passos - {seg:.0f}s", p))
    sheet = contact_sheet(itens, DESTINO / "VARREDURA_passos.jpg", "passos")
    enviar(sheet, f"Varredura de PASSOS | Qwen-Image-Edit-2511 Q2_K | cap {CAP} cena {CENA} | "
                  f"cfg {CFG_PADRAO} | tempos: " +
                  ", ".join(f"{k}p={v:.0f}s" for k, v in tempos.items()))

    print("\n=== FASE 2: true_cfg_scale (passos fixos em 20)")
    itens = []
    for cfg in CFGS:
        seg, p = gerar(20, cfg, f"cfg{str(cfg).replace('.','_')}")
        itens.append((f"cfg {cfg} - {seg:.0f}s", p))
    sheet = contact_sheet(itens, DESTINO / "VARREDURA_cfg.jpg", "cfg")
    enviar(sheet, f"Varredura de CFG | Qwen-Image-Edit-2511 Q2_K | cap {CAP} cena {CENA} | 20 passos")

    print("\n=== projecao para as 1.200 cenas restantes:")
    for passos, seg in tempos.items():
        print(f"  {passos:2d} passos -> {seg:5.1f}s/img -> {seg*1200/3600:5.1f} h")


if __name__ == "__main__":
    main()

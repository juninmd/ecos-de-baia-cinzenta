"""Gera as cenas locais de cada capítulo: dois modelos, escolhidos pelo plano.

Ponto de entrada ÚNICO da rota local. A GPU é uma só: dois processos Python
gerando ao mesmo tempo disputam a mesma VRAM, os pesos passam a ir e voltar
para a RAM e as duas gerações ficam lentas. Por isso a rota de personagem
(Qwen-Edit) mora aqui dentro em vez de num módulo à parte, e a medição de
parâmetros é a flag `--bench` deste mesmo arquivo, não outro script.

Saída em `docs/public/cenas/capitulo_N/local/`, separada das imagens do Gemini
que ficam na raiz de `capitulo_N/` — dá para comparar as duas rotas e trocar
uma sem tocar na outra.

A divisão de modelos está na regra 7 do AGENTS.md:
  - cena de ambiente (`identity_scale == 0`, planos `wide`) -> ZavyChromaXL, ~40 s
  - cena com personagem -> Qwen-Image-Edit-2511, ~4 min, preserva rosto e vestuário

Uso:
    python scripts/generate_missing_scenes.py                # todos os capítulos
    python scripts/generate_missing_scenes.py 1 2 30.5       # só estes
    python scripts/generate_missing_scenes.py --bench 8,12,20 --cap 38
"""

import argparse
import os
import sys
import time
from pathlib import Path
from typing import Dict, Optional

import requests
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

# No CI as credenciais vêm do ambiente; na máquina do autor elas estão no .env —
# sem isto a geração funcionava mas nenhuma imagem chegava no Telegram.
load_dotenv(REPO_ROOT / ".env")

from scripts.art_gen import prompt_cena  # noqa: E402
from scripts.art_gen.chapters import (  # noqa: E402
    extract_chapter_title_and_clean_text, get_chapter_files, limpar_titulos,
)
from scripts.build_scene_manifest import CENAS_POR_CAPITULO  # noqa: E402
from scripts.daily_telegram import art, characters, local_gpu, scenes  # noqa: E402

# ---------------------------------------------------------------------------
# Rota de personagem: Qwen-Image-Edit-2511 (GGUF Q2_K)
#
# Complementa o ZavyChromaXL de `local_gpu.py`, que faz as cenas de ambiente.
# Este modelo recebe o retrato de referência como imagem de ENTRADA e edita o
# mundo em volta — é o que preserva rosto **e** vestuário canônico. O
# IP-Adapter do SDXL preserva o rosto mas troca a roupa.
#
# Exige `diffusers >= 0.40`: na 0.39 o modelo carrega (os seis componentes do
# pipeline sobem sem erro) mas o processo morre sem traceback ao gerar.
# ---------------------------------------------------------------------------

QWEN_GGUF_REPO = "unsloth/Qwen-Image-Edit-2511-GGUF"
QWEN_GGUF_FILE = "qwen-image-edit-2511-Q2_K.gguf"
QWEN_BASE_REPO = "Qwen/Qwen-Image-Edit-2511"
QWEN_LABEL = "Qwen-Image-Edit-2511 Q2_K"

QWEN_PASSOS = 20
QWEN_CFG = 4.0
QWEN_LARGURA, QWEN_ALTURA = 1376, 768

QWEN_NEGATIVO = (
    "different person, changed face, deformed face, deformed hands, extra fingers, "
    # Sem isto o modelo recorta a referência e troca só o fundo.
    "same pose as reference, copy of the input photo, cut-out person, pasted subject, "
    "standing still, posing for camera, headshot, "
    "chinese text, japanese text, kanji, brazilian flag, oversaturated, blurry, "
    "nude, nudity, nsfw, sexualized"
)

_qwen_pipe = None


def qwen_disponivel() -> bool:
    try:
        import torch
        from diffusers import QwenImageEditPlusPipeline  # noqa: F401
        return torch.cuda.is_available()
    except Exception:
        return False


def qwen_carregar():
    """Pipeline em cache: a desquantização do GGUF custa ~37 s por processo."""
    global _qwen_pipe
    if _qwen_pipe is not None:
        return _qwen_pipe
    import torch
    from diffusers import (QwenImageEditPlusPipeline, QwenImageTransformer2DModel,
                           GGUFQuantizationConfig)
    print(f"🖥️ Carregando {QWEN_LABEL}...")
    transformer = QwenImageTransformer2DModel.from_single_file(
        f"https://huggingface.co/{QWEN_GGUF_REPO}/blob/main/{QWEN_GGUF_FILE}",
        quantization_config=GGUFQuantizationConfig(compute_dtype=torch.bfloat16),
        dtype=torch.bfloat16, config=QWEN_BASE_REPO, subfolder="transformer",
    )
    pipe = QwenImageEditPlusPipeline.from_pretrained(
        QWEN_BASE_REPO, transformer=transformer, dtype=torch.bfloat16)
    pipe.enable_model_cpu_offload()
    pipe.set_progress_bar_config(disable=True)
    _qwen_pipe = pipe
    print("✅ Qwen-Edit pronto.")
    return _qwen_pipe


def qwen_instrucao(cena, anchor: Dict) -> str:
    """Separa o que PRESERVA do que MUDA.

    Só pedir "mantenha o rosto" faz o modelo recortar a referência e trocar o
    fundo: mesma pose, mesmos adereços, e as dez cenas do capítulo viram dez
    retratos iguais. É preciso afirmar que é uma fotografia nova, com pose e
    ação diferentes, **e** cravar o enquadramento na mesma instrução — uma sem
    a outra derruba a outra.
    """
    roupa = characters.wardrobe(anchor)
    acao = scenes.palavras_visuais(cena.texto, limite=4)
    encenacao = scenes.ENCENACAO.get(cena.shot, scenes.ENCENACAO_PADRAO)

    partes = ["Keep the same person: identical face, beard, hair and skin."]
    if roupa:
        partes.append(f"Keep the same outfit: {roupa[:70]}.")
    partes += [
        "Change the pose and the camera completely: this is a NEW photograph of him, "
        "not the same photo with a different background.",
        f"New framing: {cena.shot}, {encenacao}."
        " He is close to the camera, upper body large in the frame, face sharp and"
        " clearly readable -- but caught mid-action, never posing.",
        f"He is doing something in the scene: {acao}." if acao else
        "He is in the middle of an action, not standing still.",
        f"Setting: {scenes.cenario_do_texto(cena.texto)}.",
        "Gritty cyberpunk Brazil, desaturated grimy colors, dramatic lighting, "
        "cinematic film still.",
    ]
    return " ".join(partes)


def qwen_gerar(pipe, referencia: Path, prompt: str, destino: Path, seed: int,
               passos: int = QWEN_PASSOS, cfg: float = QWEN_CFG) -> Optional[Path]:
    try:
        import torch
        from PIL import Image
        img = pipe(
            image=[Image.open(referencia).convert("RGB")],
            prompt=prompt, negative_prompt=QWEN_NEGATIVO,
            num_inference_steps=passos, true_cfg_scale=cfg,
            width=QWEN_LARGURA, height=QWEN_ALTURA,
            generator=torch.Generator("cpu").manual_seed(seed),
        ).images[0]
        destino.parent.mkdir(parents=True, exist_ok=True)
        img.save(destino, quality=95)
        return destino
    except BaseException as exc:
        print(f"⚠ Qwen-Edit falhou ({type(exc).__name__}): {str(exc)[:160]}")
        return None


# Dois modelos locais (AGENTS.md §7). Pollinations só se a GPU sumir.
_LOCAL_GEN = local_gpu.generate if local_gpu.available() else None
_QWEN_OK = qwen_disponivel()

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


def send_telegram_photo(image_path: Path, caption: str):
    """Sends a photo to Telegram via sendPhoto API."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print(f"⚠️ Telegram token or chat ID missing. Skipping Telegram notification for {image_path.name}")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "caption": caption
    }

    for attempt in range(1, 4):
        try:
            with open(image_path, "rb") as photo_file:
                files = {"photo": photo_file}
                resp = requests.post(url, data=data, files=files, timeout=60)
                if resp.status_code == 429:
                    retry_after = resp.json().get("parameters", {}).get("retry_after", 10)
                    print(f"⏳ Telegram Rate limit (429), waiting {retry_after}s...")
                    time.sleep(retry_after)
                    continue
                resp.raise_for_status()
                print(f"✈️ Telegram sent: {caption}")
                return True
        except Exception as exc:
            print(f"⚠️ Telegram send photo attempt {attempt} failed for {caption}: {exc}")
            time.sleep(2 * attempt)

    print(f"❌ Telegram send photo failed permanently for {caption}")
    return False


def _carregar_cena(cap, scene_idx):
    """Título, objeto da cena e âncora de personagem de uma cena do capítulo."""
    raw_text = cap["file_path"].read_text(encoding="utf-8")
    title, body_text = limpar_titulos(*extract_chapter_title_and_clean_text(raw_text))
    scene_objects = scenes.split_scenes(body_text, quantidade=CENAS_POR_CAPITULO)
    while len(scene_objects) < CENAS_POR_CAPITULO:
        scene_objects.append(scene_objects[-1] if scene_objects
                             else scenes.Scene(len(scene_objects) + 1, body_text))
    s_obj = scene_objects[scene_idx - 1]
    s_obj.indice = scene_idx
    return title, s_obj, characters.pick_anchor(s_obj.personagens)


def process_all_chapters(somente=None, passos=QWEN_PASSOS, cfg=QWEN_CFG, limite=None):
    """`somente`: números de capítulo (como texto), para validar um antes da corrida inteira.

    Comparação por string porque há capítulos fracionários ("30.5") que `int()` rejeita.

    `limite`: para depois de N imagens. Uma imagem por execução deixa julgar o
    resultado antes de queimar horas de GPU no mesmo erro.
    """
    feitas = 0
    chapters = get_chapter_files()
    if somente:
        chapters = [c for c in chapters if c["num_str"] in somente]
    print(f"📚 Total chapters identified: {len(chapters)}")

    for cap in chapters:
        # Subpasta própria: as imagens do Gemini ficam na raiz de capitulo_N/ e
        # nunca são tocadas; a rota local escreve só aqui.
        folder_path = cap["folder_path"] / "local"
        folder_path.mkdir(parents=True, exist_ok=True)

        missing_scenes = [m for m in range(1, CENAS_POR_CAPITULO + 1)
                          if not (folder_path / f"cena_{m}.jpg").exists()]

        if not missing_scenes:
            print(f"⏩ Chapter {cap['folder_name']} completo com {CENAS_POR_CAPITULO} cenas.")
            continue

        print(f"\n🎨 Processing {cap['folder_name']} (missing scenes: {missing_scenes})...")

        for scene_idx in missing_scenes:
            title, s_obj, anchor = _carregar_cena(cap, scene_idx)

            # Regra 4 do AGENTS.md: seed = capítulo * 100 + índice da cena.
            seed = prompt_cena.seed_da_cena(cap["num_str"], scene_idx)
            scene_file_path = folder_path / f"cena_{scene_idx}.jpg"

            print(f"📸 Generating {cap['folder_name']} cena_{scene_idx}.jpg (seed={seed})...")

            gen_res = None
            rota = None
            referencia = characters.reference_image(anchor) if anchor else None
            # Plano aberto é cena de ambiente: identity_scale 0.0 e sem âncora. Forçar
            # personagem aqui era o que transformava todo plano aberto em retrato 3x4.
            com_personagem = bool(referencia) and s_obj.identity_scale > 0

            if com_personagem and _QWEN_OK:
                gen_res = qwen_gerar(
                    qwen_carregar(), referencia, qwen_instrucao(s_obj, anchor),
                    scene_file_path, seed, passos=passos, cfg=cfg,
                )
                if gen_res:
                    rota = f"Qwen-Edit · {QWEN_LABEL}"

            if gen_res is None and _LOCAL_GEN is not None:
                if com_personagem:
                    gen_res = _LOCAL_GEN(
                        referencia, s_obj.compact_prompt(anchor), scene_file_path, seed,
                        identity_scale=s_obj.identity_scale,
                    )
                else:
                    gen_res = _LOCAL_GEN(
                        None, s_obj.compact_prompt_sem_personagem(), scene_file_path, seed,
                    )
                if gen_res:
                    rota = f"SDXL · {local_gpu.BASE_MODEL.split('/')[-1]}"

            if gen_res:
                print(f"🖥️ {rota}: {scene_file_path.name}")
            else:
                print("↩ Fallback: rota local indisponível para esta cena.")
                prompt = s_obj.edit_prompt(anchor) if anchor else s_obj.image_prompt(title)
                gen_res = art.generate_image(
                    prompt=prompt, output_path=scene_file_path, seed=seed,
                    width=1280, height=720, retries=3,
                )

            if gen_res and scene_file_path.exists():
                # O autor acompanha pelo Telegram e precisa saber de que rota veio a
                # imagem para julgar a qualidade.
                caption = f"{cap['folder_name']}/local cena_{scene_idx} — {rota or 'Pollinations'}"
                send_telegram_photo(scene_file_path, caption)
            else:
                print(f"❌ Failed to generate {cap['folder_name']} cena_{scene_idx}.jpg")

            feitas += 1
            if limite and feitas >= limite:
                print(f"⏹ Limite de {limite} imagem(ns) atingido.")
                return

            time.sleep(1)  # Gentle pause between generations


def bench(passos_lista, cfg, cap_num, scene_idx):
    """Mede tempo/qualidade do Qwen por nº de passos, no mesmo processo.

    Passos é o único parâmetro que corta tempo proporcionalmente, e a maioria
    das cenas passa por aqui. Reaproveitar o pipeline já carregado torna a
    medição honesta: só a geração é cronometrada, sem os ~37 s de carga.
    """
    if not _QWEN_OK:
        print("⚠ Qwen-Edit indisponível; nada a medir.")
        return
    cap = next(c for c in get_chapter_files() if c["num_str"] == cap_num)
    _, s_obj, anchor = _carregar_cena(cap, scene_idx)
    referencia = characters.reference_image(anchor) if anchor else None
    if not referencia or s_obj.identity_scale <= 0:
        print(f"⚠ cap {cap_num} cena {scene_idx} é plano de ambiente; escolha outra.")
        return

    destino_dir = REPO_ROOT / "docs" / "public" / "cenas" / "_teste_qualidade" / "varredura"
    pipe = qwen_carregar()
    prompt = qwen_instrucao(s_obj, anchor)
    seed = prompt_cena.seed_da_cena(cap_num, scene_idx)

    for passos in passos_lista:
        destino = destino_dir / f"p{passos}_cfg{str(cfg).replace('.', '_')}.jpg"
        inicio = time.time()
        ok = qwen_gerar(pipe, referencia, prompt, destino, seed, passos=passos, cfg=cfg)
        dur = time.time() - inicio
        if not ok:
            continue
        # ~1650 das ~2350 cenas do livro têm personagem e passam pelo Qwen.
        projecao = dur * 1650 / 3600
        print(f"RESULTADO passos={passos} cfg={cfg} geracao={dur:.0f}s "
              f"projecao_livro={projecao:.0f}h")
        send_telegram_photo(destino, f"varredura passos={passos} cfg={cfg} — {dur:.0f}s/imagem")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Gera as cenas locais dos capítulos.")
    ap.add_argument("capitulos", nargs="*", help="números de capítulo; vazio = todos")
    ap.add_argument("--bench", help="lista de passos a medir, ex: 8,12,20")
    ap.add_argument("--cfg", type=float, default=QWEN_CFG)
    ap.add_argument("--cap", default="38", help="capítulo usado pelo --bench")
    ap.add_argument("--cena", type=int, default=4, help="cena usada pelo --bench")
    ap.add_argument("--passos", type=int, default=QWEN_PASSOS,
                    help="passos do Qwen na geração normal")
    ap.add_argument("--limite", type=int, help="para depois de N imagens (ex: --limite 1)")
    args = ap.parse_args()

    if _LOCAL_GEN:
        print(f"🖥️ Ambiente: {local_gpu.BASE_MODEL.split('/')[-1]}")
    else:
        print("⚠ GPU local indisponível; usando Pollinations (sem fidelidade de personagem).")
    print(f"🎭 Personagem: {QWEN_LABEL}" if _QWEN_OK
          else "⚠ Qwen-Edit indisponível; personagem cai no SDXL + IP-Adapter.")

    if args.bench:
        bench([int(p) for p in args.bench.split(",")], args.cfg, args.cap, args.cena)
    else:
        process_all_chapters(set(args.capitulos) or None, passos=args.passos,
                             cfg=args.cfg, limite=args.limite)

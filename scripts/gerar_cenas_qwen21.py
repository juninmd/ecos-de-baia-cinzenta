"""Geração local de cenas com Qwen-Image-2.1 (GGUF Q2_K) via Unsloth.

Unifica cenas de ambiente (text-to-image) e cenas com personagem (image-to-image),
preservando a Regra Zero ao receber o retrato canônico como âncora visual.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from scripts.art_gen import homologacao  # noqa: E402
from scripts.build_scene_manifest import DESTINO  # noqa: E402

GGUF_REPO = "unsloth/Qwen-Image-2.1-GGUF"
GGUF_FILE = "qwen-image-2.1-Q2_K.gguf"
BASE_REPO = "Qwen/Qwen-Image-2.1"
LARGURA, ALTURA = 1376, 768
PASSOS = 25
CFG = 1.0
NEGATIVO = (
    "different person, deformed face, deformed hands, extra fingers, "
    "same pose as reference, cut-out person, pasted subject, standing still, "
    "chinese text, japanese text, kanji, blurry, oversaturated, nsfw"
)

_pipe = None


def resolver_caminhos_locais():
    hub_dir = Path.home() / ".cache" / "huggingface" / "hub"
    gguf_snap = hub_dir / f"models--{GGUF_REPO.replace('/', '--')}" / "snapshots"
    base_snap = hub_dir / f"models--{BASE_REPO.replace('/', '--')}" / "snapshots"

    gguf_path = f"https://huggingface.co/{GGUF_REPO}/blob/main/{GGUF_FILE}"
    if gguf_snap.exists():
        for s in gguf_snap.iterdir():
            cand = s / GGUF_FILE
            if cand.exists():
                gguf_path = str(cand)
                break

    base_path = BASE_REPO
    if base_snap.exists():
        for s in base_snap.iterdir():
            if (s / "model_index.json").exists():
                base_path = str(s)
                break

    local_only = not gguf_path.startswith("http") and base_path != BASE_REPO
    return gguf_path, base_path, local_only


def carregar_pipeline():
    global _pipe
    if _pipe is not None:
        return _pipe
    import torch
    from diffusers import (GGUFQuantizationConfig, QwenImage21Pipeline,
                           QwenImage21Transformer2DModel)

    gguf_path, base_path, local_only = resolver_caminhos_locais()
    print(f"🖥️ Carregando Qwen-Image-2.1 ({Path(gguf_path).name})...")
    transformer = QwenImage21Transformer2DModel.from_single_file(
        gguf_path,
        quantization_config=GGUFQuantizationConfig(compute_dtype=torch.bfloat16),
        dtype=torch.bfloat16,
        config=base_path,
        subfolder="transformer",
        local_files_only=local_only,
    )
    pipe = QwenImage21Pipeline.from_pretrained(
        base_path, transformer=transformer, dtype=torch.bfloat16,
        local_files_only=local_only,
    )
    pipe.enable_model_cpu_offload()
    pipe.set_progress_bar_config(disable=True)
    _pipe = pipe
    print("✅ Qwen-Image-2.1 pronto.")
    return _pipe


def gerar_cena(pipe, entrada: Dict, destino: Path) -> bool:
    import torch

    refs = [REPO_ROOT / p["referencia"] for p in entrada.get("elenco", [])
            if p.get("referencia") and (REPO_ROOT / p["referencia"]).exists()]
    imagens = [Image.open(r).convert("RGB") for r in refs] if refs else None

    prompt = entrada.get("prompt", "")
    seed = int(entrada.get("seed", 42))

    try:
        kwargs = {
            "prompt": prompt,
            "width": LARGURA,
            "height": ALTURA,
            "num_inference_steps": PASSOS,
            "generator": torch.Generator("cpu").manual_seed(seed),
        }
        if CFG > 1.0:
            kwargs["true_cfg_scale"] = CFG
            kwargs["negative_prompt"] = NEGATIVO
        if imagens:
            kwargs["image"] = imagens

        resultado = pipe(**kwargs).images[0]
        destino.parent.mkdir(parents=True, exist_ok=True)
        resultado.save(destino, quality=94, optimize=True)

        medida = homologacao.carregar(destino)
        reprovas, _ = homologacao.avaliar(medida) if medida else (["ilegível"], [])
        if reprovas:
            print(f"   ❌ Reprovada ({'; '.join(reprovas)}), descartando refugo...")
            destino.unlink(missing_ok=True)
            return False
        return True
    except Exception as exc:
        print(f"   ⚠️ Falha ao gerar: {type(exc).__name__}: {str(exc)[:120]}")
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capitulo", help="Filtrar por capítulo")
    parser.add_argument("--limite", type=int, default=10, help="Máximo de cenas")
    parser.add_argument("--subpasta", help="Subpasta opcional dentro de capitulo_N/")
    args = parser.parse_args()

    manifesto = json.loads(DESTINO.read_text(encoding="utf-8"))
    fila = [x for x in manifesto if not (REPO_ROOT / x["saida"]).exists()]
    if args.capitulo:
        fila = [x for x in fila if str(x.get("capitulo")) == str(args.capitulo)]

    if not fila:
        print("✅ Nenhuma cena pendente no filtro informado.")
        return 0

    total_processar = min(args.limite, len(fila))
    print(f"🎬 Processando até {total_processar} cenas pendentes (de {len(fila)})...")
    pipe = carregar_pipeline()
    aprovadas = 0

    for i, item in enumerate(fila[:args.limite], start=1):
        saida = REPO_ROOT / item["saida"]
        if args.subpasta:
            saida = saida.parent / args.subpasta / saida.name
        t0 = time.time()
        print(f"[{i}/{total_processar}] cap_{item['capitulo']}:{item['cena']} -> {saida.name}...")
        if gerar_cena(pipe, item, saida):
            aprovadas += 1
            print(f"   ✅ Homologada em {time.time()-t0:.1f}s.")

    print(f"🏁 Concluído: {aprovadas}/{total_processar} cenas aprovadas nesta rodada.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

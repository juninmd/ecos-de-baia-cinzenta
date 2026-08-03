"""Retratos canônicos: gera em `docs/public/personagens/` quem ainda não tem imagem.

A fonte do prompt é `docs/personagens.md` — a mesma que trava a identidade nas cenas.
Nunca sobrescreve um retrato existente (AGENTS.md, regra 3: retrato é imutável).
"""
import argparse
import sys
from pathlib import Path

from scripts.art_gen.character_db import CharacterDatabase

REPO_ROOT = Path(__file__).resolve().parents[2]
PERSONAGENS_MD = REPO_ROOT / "docs" / "personagens.md"
PUBLIC_DIR = REPO_ROOT / "docs" / "public"

BASE_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"
# Retrato: 832x1216 é a razão 2:3 nativa do SDXL. Em 16:9 o rosto sai pequeno
# demais para servir de âncora de identidade.
LARGURA, ALTURA = 832, 1216

# Curto de propósito: estilo e descrição dividem o mesmo orçamento de 77 tokens do CLIP.
# Um bloco de estilo longo empurrava as marcas distintivas para fora da janela.
STYLE = "cinematic neo-noir portrait, photorealistic, moody rim lighting, film grain"
NEGATIVE = (
    "deformed face, extra limbs, extra fingers, text, watermark, signature, logo, "
    "blurry, low quality, cartoon, anime, doll, plastic skin, duplicate head"
)

# Vestuário primeiro: é o traço que o modelo mais troca por conta própria.
PROMPT_KEYS = ("Vestuário", "Rosto", "Cabelo", "Olhos", "Marcas Distintivas",
               "Porte Físico", "Idade")

_pipe = None


def _partes(char):
    return [p.strip() for p in (char.get("description") or "").split(". ") if p.strip()]


def build_prompt(char) -> str:
    """Prompt do retrato a partir dos campos visuais canônicos do dossiê.

    `Prompt Visual` é a tradução fiel da descrição física para inglês e tem
    prioridade: o CLIP do SDXL é treinado em inglês e ignora metade do
    português, que é justamente onde moram cabelo, olhos e vestuário.

    Estilo e descrição vão no MESMO prompt (os dois encoders recebem o texto
    inteiro). Mandar o estilo sozinho em `prompt_2` parece resolver o limite de
    tokens, mas o encoder 2 é quem produz o embedding agrupado: sem o
    personagem nele, sai uma foto no estilo certo de uma pessoa qualquer.
    """
    partes = _partes(char)
    for parte in partes:
        if parte.startswith("Prompt Visual:"):
            return f"{parte.split(':', 1)[1].strip()}, {STYLE}"
    ordenadas = [p for chave in PROMPT_KEYS for p in partes if p.startswith(chave)]
    corpo = ". ".join(ordenadas) or ". ".join(partes)
    return f"{char['name']}. {corpo}. {STYLE}"


def _avisa_truncamento(pipe, char, prompt: str) -> None:
    limite = pipe.tokenizer.model_max_length
    tokens = len(pipe.tokenizer(prompt).input_ids)
    if tokens > limite:
        print(f"   ⚠ Prompt Visual de {char['name']} tem {tokens} tokens; o CLIP corta em "
              f"{limite}. Encurte o campo em docs/personagens.md ou traços vão sumir.")


def seed_for(char) -> int:
    """Seed determinística e estável entre processos (hash() do Python é randomizado)."""
    return sum((i + 1) * ord(c) for i, c in enumerate(char["name"])) % 100_000


def _load():
    global _pipe
    if _pipe is not None:
        return _pipe
    import torch
    from diffusers import StableDiffusionXLPipeline

    print("🖥️ Carregando SDXL na GPU...")
    pipe = StableDiffusionXLPipeline.from_pretrained(
        BASE_MODEL, torch_dtype=torch.float16, variant="fp16", use_safetensors=True
    )
    pipe.enable_model_cpu_offload()
    pipe.set_progress_bar_config(disable=True)
    _pipe = pipe
    return _pipe


def generate(char, destino: Path, steps: int = 34) -> Path:
    import torch

    pipe = _load()
    prompt = build_prompt(char)
    _avisa_truncamento(pipe, char, prompt)
    imagem = pipe(
        prompt=prompt,
        negative_prompt=NEGATIVE,
        num_inference_steps=steps,
        guidance_scale=6.5,
        width=LARGURA,
        height=ALTURA,
        generator=torch.Generator("cuda").manual_seed(seed_for(char)),
    ).images[0]
    destino.parent.mkdir(parents=True, exist_ok=True)
    imagem.save(destino)
    return destino


def pendentes(db: CharacterDatabase):
    """Personagens com retrato declarado no dossiê mas sem arquivo no disco."""
    faltando = []
    for char in db.characters.values():
        ref = char.get("image")
        if not ref:
            print(f"⚠ {char['name']}: sem ![imagem] no dossiê — nada a gerar.")
            continue
        destino = PUBLIC_DIR / ref.lstrip("/")
        if not destino.exists():
            faltando.append((char, destino))
    return faltando


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", help="gera apenas o personagem cujo nome contém este texto")
    parser.add_argument("--dry-run", action="store_true", help="mostra os prompts e sai")
    args = parser.parse_args(argv)

    db = CharacterDatabase(str(PERSONAGENS_MD))
    alvos = pendentes(db)
    if args.only:
        alvo = args.only.lower()
        alvos = [(c, d) for c, d in alvos if alvo in c["name"].lower()]

    if not alvos:
        print("✅ Todos os personagens do dossiê já têm retrato.")
        return 0

    for char, destino in alvos:
        print(f"\n🎨 {char['name']} → {destino.name} (seed {seed_for(char)})")
        print(f"   {build_prompt(char)[:220]}...")
        if args.dry_run:
            continue
        generate(char, destino)
        print(f"   ✅ salvo em {destino.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Geração local na GPU: identidade travada por IP-Adapter, sem cota de serviço."""
from pathlib import Path
from typing import Optional

BASE_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"
IP_ADAPTER_REPO = "h94/IP-Adapter"
# plus-face: treinado em rosto. O ip-adapter_sdxl genérico devolve "alguém parecido",
# o que viola a Regra Zero do AGENTS.md (fisionomia nunca muda).
IP_ADAPTER_WEIGHT = "ip-adapter-plus-face_sdxl_vit-h.safetensors"
IDENTITY_SCALE = 0.85
NEGATIVE = (
    "different person, changed face, deformed face, extra limbs, text, watermark, "
    "logo, blurry, low quality"
)

FLUX_MODEL = "black-forest-labs/FLUX.1-Kontext-dev"

_pipe = None
_flux = None


def _load_flux():
    """FLUX.1-Kontext local: mesma fidelidade de identidade do Space, sem cota."""
    global _flux
    if _flux is not None:
        return _flux

    import torch
    from diffusers import FluxKontextPipeline

    print("🖥️ Carregando FLUX.1-Kontext na GPU (offload sequencial)...")
    pipe = FluxKontextPipeline.from_pretrained(FLUX_MODEL, torch_dtype=torch.bfloat16)
    # 12B não cabe inteiro em 16 GB: o offload sequencial troca velocidade por caber.
    pipe.enable_sequential_cpu_offload()
    pipe.set_progress_bar_config(disable=True)
    _flux = pipe
    return _flux


def kontext_generate(reference: Path, prompt: str, destino: Path, seed: int,
                     steps: int = 28, largura: int = 1024) -> Optional[Path]:
    """Cena gerada a partir do retrato, preservando a fisionomia (AGENTS.md Regra Zero)."""
    if reference is None or not Path(reference).exists():
        return None
    try:
        import torch
        from PIL import Image

        pipe = _load_flux()
        referencia = Image.open(reference).convert("RGB")
        altura = int(largura * referencia.height / referencia.width) // 16 * 16
        imagem = pipe(
            image=referencia.resize((largura, altura)),
            prompt=prompt[:900],
            guidance_scale=2.5,
            num_inference_steps=steps,
            generator=torch.Generator("cpu").manual_seed(seed),
        ).images[0]
        destino.parent.mkdir(parents=True, exist_ok=True)
        imagem.save(destino, quality=92)
        print(f"🧬 Kontext local: {destino.name}")
        return destino
    except BaseException as exc:
        print(f"⚠ Kontext local falhou ({type(exc).__name__}): {str(exc)[:160]}")
        return None


def available() -> bool:
    try:
        import torch

        return torch.cuda.is_available()
    except ImportError:
        return False


def _load():
    """Load SDXL + IP-Adapter once per process (≈7 GB de VRAM)."""
    global _pipe
    if _pipe is not None:
        return _pipe

    import torch
    from diffusers import AutoPipelineForText2Image
    from transformers import CLIPVisionModelWithProjection

    print("🖥️ Carregando SDXL + IP-Adapter na GPU...")
    # Os pesos *_vit-h exigem o encoder ViT-H; o SDXL traz ViT-bigG por padrão e o
    # produto de matrizes falha ("mat1 and mat2 shapes cannot be multiplied").
    image_encoder = CLIPVisionModelWithProjection.from_pretrained(
        IP_ADAPTER_REPO, subfolder="models/image_encoder", torch_dtype=torch.float16
    )
    pipe = AutoPipelineForText2Image.from_pretrained(
        BASE_MODEL, image_encoder=image_encoder, torch_dtype=torch.float16,
        variant="fp16", use_safetensors=True
    )
    pipe.load_ip_adapter(IP_ADAPTER_REPO, subfolder="sdxl_models", weight_name=IP_ADAPTER_WEIGHT)
    pipe.set_ip_adapter_scale(IDENTITY_SCALE)
    pipe.enable_model_cpu_offload()
    pipe.set_progress_bar_config(disable=True)
    _pipe = pipe
    print("✅ Pipeline local pronto.")
    return _pipe


def generate(reference: Path, prompt: str, destino: Path, seed: int,
             steps: int = 22, size: int = 1024,
             identity_scale: float = IDENTITY_SCALE) -> Optional[Path]:
    """Scene image anchored on the character portrait — assinatura usada por animate.scene_image."""
    try:
        import torch
        from PIL import Image

        pipe = _load()
        if reference is None or not Path(reference).exists():
            # Plano sem personagem (paisagem, objeto): o adaptador entra com peso zero,
            # mas precisa de alguma imagem — cinza neutro não injeta identidade nenhuma.
            referencia = Image.new("RGB", (512, 512), (128, 128, 128))
            identity_scale = 0.0
        else:
            referencia = Image.open(reference).convert("RGB")
        pipe.set_ip_adapter_scale(identity_scale)
        gerador = torch.Generator(device="cuda").manual_seed(seed)
        imagem = pipe(
            prompt=prompt[:900],
            negative_prompt=NEGATIVE,
            ip_adapter_image=referencia,
            num_inference_steps=steps,
            guidance_scale=6.0,
            width=size,
            height=int(size * 9 / 16) // 8 * 8,
            generator=gerador,
        ).images[0]
        destino.parent.mkdir(parents=True, exist_ok=True)
        imagem.save(destino, quality=92)
        print(f"🖥️ GPU local: {destino.name}")
        return destino
    except BaseException as exc:
        print(f"⚠ GPU local falhou ({type(exc).__name__}): {str(exc)[:160]}")
        return None

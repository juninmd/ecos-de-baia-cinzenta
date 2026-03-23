DEFAULT_SIZE = (768, 1024)
DEFAULT_SAMPLER = "DPM++ 2M Karras"

MODEL_ALTERNATIVES = {
    "flux-schnell": {
        "label": "FLUX.1 Schnell (open source, melhor qualidade geral)",
        "local_model_id": "black-forest-labs/FLUX.1-schnell",
        "size": DEFAULT_SIZE,
        "steps": 28,
        "sampler": DEFAULT_SAMPLER,
    },
    "sdxl": {
        "label": "Stable Diffusion XL 1.0 (boa fidelidade de composição)",
        "local_model_id": "stabilityai/stable-diffusion-xl-base-1.0",
        "size": DEFAULT_SIZE,
        "steps": 32,
        "sampler": DEFAULT_SAMPLER,
    },
    "sd15": {
        "label": "Stable Diffusion 1.5 (rápido, menor qualidade)",
        "local_model_id": "runwayml/stable-diffusion-v1-5",
        "size": DEFAULT_SIZE,
        "steps": 30,
        "sampler": DEFAULT_SAMPLER,
    },
}


def print_alternatives() -> None:
    print("\n🎨 Alternativas open source próximas do Nano Banana")
    print("=" * 64)
    for key, data in MODEL_ALTERNATIVES.items():
        print(f"- {key}: {data['label']}")
        print(f"  model_id: {data['local_model_id']}")
    print("\n✅ Recomendada (implementada por padrão): sdxl\n")

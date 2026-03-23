MODEL_ALTERNATIVES = {
    "flux-schnell": {
        "label": "FLUX.1 Schnell (open source, melhor qualidade geral)",
        "local_model_id": "black-forest-labs/FLUX.1-schnell",
        "size": (768, 1024),
        "steps": 28,
        "sampler": "DPM++ 2M Karras",
    },
    "sdxl": {
        "label": "Stable Diffusion XL 1.0 (boa fidelidade de composição)",
        "local_model_id": "stabilityai/stable-diffusion-xl-base-1.0",
        "size": (768, 1024),
        "steps": 32,
        "sampler": "DPM++ 2M Karras",
    },
    "sd15": {
        "label": "Stable Diffusion 1.5 (rápido, menor qualidade)",
        "local_model_id": "runwayml/stable-diffusion-v1-5",
        "size": (768, 1024),
        "steps": 30,
        "sampler": "DPM++ 2M Karras",
    },
}


def print_alternatives() -> None:
    print("\n🎨 Alternativas open source próximas do Nano Banana")
    print("=" * 64)
    for key, data in MODEL_ALTERNATIVES.items():
        print(f"- {key}: {data['label']}")
        print(f"  model_id: {data['local_model_id']}")
    print("\n✅ Recomendada (implementada por padrão): sdxl\n")

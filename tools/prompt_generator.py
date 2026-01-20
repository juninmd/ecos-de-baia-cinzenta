import argparse

# Definições de Personagens (Baseado em docs/personagens.md)
CHARACTERS = {
    "gabo": {
        "name": "Gabriel 'Gabo' Moretti",
        "visuals": "30 years old man, detective, rugged, messy dark hair, full beard with gray patches, deep brown eyes with dark circles, tired expression, wearing a beige trench coat with soot stains over a crumpled white shirt, athletic build but exhausted, noir atmosphere.",
        "trigger": "gabo moretti"
    },
    "val": {
        "name": "Valéria 'Val' Cruz",
        "visuals": "23 years old woman, cyberpunk hacker, small slender build, pixie cut hair with holographic pink and blue tint, silver cybernetic eyes, LED implants on cheekbones, barcode tattoo on neck, wearing leather jacket and cargo pants, holding a futuristic deck, cyberpunk aesthetic.",
        "trigger": "val cruz"
    },
    "marco": {
        "name": "Marco Moretti",
        "visuals": "35 years old man, politician, handsome, clean cut dark hair, cold calculating brown eyes, wearing an expensive tailored italian suit, charismatic but sinister smile, cinematic lighting.",
        "trigger": "marco moretti"
    },
    "elara": {
        "name": "Dra. Elara Vance",
        "visuals": "45 years old woman looking 30, elegant, silver hair in geometric bun, ice blue eyes, porcelain skin, wearing futuristic high-fashion grey dress, cold demeanor, sci-fi laboratory background.",
        "trigger": "elara vance"
    },
    "taxidermista": {
        "name": "O Taxidermista",
        "visuals": "Older man, 60s, long grey hair tied back, grey eyes, wearing a leather craftsman apron over dark clothes, wearing fine leather gloves, holding surgical tools, creepy atmosphere, dim lighting.",
        "trigger": "taxidermista"
    },
    "clara": {
        "name": "Clara Moretti",
        "visuals": "18 years old girl, thin, brown hair tied back, big expressive brown eyes, wearing simple worn-out clothes, holding an old tablet, hopeful but scared expression.",
        "trigger": "clara moretti"
    },
    "nise": {
        "name": "Dra. Nise",
        "visuals": "65 years old woman, doctor, curved posture, white hair in messy bun, wearing a stained medical lab coat over comfortable clothes, kind wise eyes, underground clinic setting.",
        "trigger": "dra nise"
    },
    "aria": {
        "name": "Aria (A Menina)",
        "visuals": "Holographic projection of a 10 year old girl, platinum blonde hair, heterochromatic eyes (one blue, one gold), glowing barcode on neck, wearing a simple white dress, glitch effect, ethereal lighting.",
        "trigger": "aria hologram"
    },
    "generic_male": {
        "name": "Personagem Genérico (Masculino)",
        "visuals": "Cyberpunk citizen, male, gritty, worn clothes, rain-soaked, neon reflection.",
        "trigger": "man"
    },
    "generic_female": {
        "name": "Personagem Genérico (Feminino)",
        "visuals": "Cyberpunk citizen, female, gritty, worn clothes, rain-soaked, neon reflection.",
        "trigger": "woman"
    }
}

# Definições de Estilo Global
STYLES = {
    "noir": "Neo-noir style, heavy shadows, high contrast, dramatic chiaroscuro lighting, rain, wet streets, gloom, cinematic 8k, masterpiece, hyperrealistic texture.",
    "cyberpunk": "Cyberpunk atmosphere, neon lights (blue and pink), fog, technological debris, holographic advertisements, metallic textures, futuristic, detailed.",
    "action": "Dynamic action shot, motion blur, intense expression, cinematic angle, debris flying, dramatic lighting.",
    "portrait": "Close-up portrait, shallow depth of field, sharp focus on eyes, emotional, highly detailed skin texture, studio lighting."
}

def generate_prompt(character_key, action, setting, style_key="noir"):
    char_data = CHARACTERS.get(character_key.lower())
    if not char_data:
        return f"Erro: Personagem '{character_key}' não encontrado."

    style_prompt = STYLES.get(style_key.lower(), STYLES["noir"])

    # Construção do Prompt (Flux/Midjourney Optimized)
    # Estrutura: [Sujeito + Visual] + [Ação] + [Ambiente] + [Estilo/Atmosfera] + [Qualidade]

    prompt = (
        f"{char_data['visuals']} "
        f"{action}. "
        f"Located in {setting}. "
        f"{style_prompt} "
        f"Best quality, ultra detailed, 8k, ray tracing."
    )

    return prompt

def list_characters():
    print("Personagens disponíveis:")
    for key in CHARACTERS:
        print(f"- {key}")

def main():
    parser = argparse.ArgumentParser(description="Gerador de Prompts para Baía Cinzenta")
    parser.add_argument("--char", help="Nome do personagem (ex: gabo, val)")
    parser.add_argument("--action", help="Ação que o personagem está fazendo")
    parser.add_argument("--setting", help="Cenário/Ambiente")
    parser.add_argument("--style", default="noir", help="Estilo (noir, cyberpunk, action, portrait)")
    parser.add_argument("--list", action="store_true", help="Listar personagens disponíveis")

    args = parser.parse_args()

    if args.list:
        list_characters()
        return

    if args.char and args.action and args.setting:
        prompt = generate_prompt(args.char, args.action, args.setting, args.style)
        print("\n--- Prompt Gerado ---\n")
        print(prompt)
        print("\n---------------------\n")
    else:
        print("Erro: Forneça --char, --action e --setting.")
        parser.print_help()

if __name__ == "__main__":
    main()

"""Loop de iteracao de qualidade: gera local, compara lado a lado com a versao Gemini.

NAO sobrescreve nenhuma imagem canonica. Tudo vai para _teste_qualidade/.
Cada rodada envia ao Telegram a comparacao (Gemini | local) com o nome do modelo.

Uso:
    python scripts/iterar_qualidade.py --rodada v1
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
from diffusers import AutoPipelineForText2Image
from transformers import CLIPVisionModelWithProjection
from PIL import Image

from scripts.art_gen.chapters import extract_chapter_title_and_clean_text, limpar_titulos
from scripts.daily_telegram import scenes, characters

BASE_MODEL = "RunDiffusion/Juggernaut-XL-v9"
MODEL_LABEL = "Juggernaut XL v9"
IP_ADAPTER_REPO = "h94/IP-Adapter"
IP_ADAPTER_WEIGHT = "ip-adapter-plus-face_sdxl_vit-h.safetensors"

# Referencia Gemini = o alvo de qualidade. Só capitulos que ja tem imagem dele.
# Capitulos que nao foram usados para afinar: teste de generalizacao.
ALVOS = [
    (12, 1, 1201),
    (12, 2, 1202),
    (25, 1, 2501),
    (25, 3, 2503),
    (33, 2, 3302),
]

DESTINO = REPO / "docs" / "public" / "cenas" / "_teste_qualidade"
DESTINO.mkdir(parents=True, exist_ok=True)

# Vocabulario extraido da saida do Gemini: cidade brasileira arruinada, placas em
# portugues, carcaças de carro, fumaça, skyline em camadas, profundidade atmosferica.
# O que NUNCA pode ser truncado: humor, luz e hora do dia. Vem primeiro no prompt.
# Na v1 esse bloco ficou no fim e o CLIP cortou fora em 77 tokens -> saiu dia pastel.
# Nucleo curto e inegociavel: humor, hora e pais. Entra cedo, nunca e' truncado.
# Compacto de proposito: cada conceito extra rouba token de outro e dilui os dois.
# So estilo e mundo - NUNCA lugar nem clima. Fixar "rua chuvosa a noite" aqui
# fazia laboratorio (cap 25) e caverna (cap 12) virarem rua molhada tambem.
STYLE_NUCLEO = "gritty cyberpunk brazil, desaturated grimy colors, dramatic lighting"

# O cenario sai do texto da cena. So cai no default quando nada e' reconhecido.
CENARIOS = {
    "laboratório": "sterile white high-tech laboratory interior",
    "laboratorio": "sterile white high-tech laboratory interior",
    "caverna": "vast underground cavern",
    "túnel": "concrete tunnel interior", "tunel": "concrete tunnel interior",
    "esgoto": "sewer tunnel interior",
    "hospital": "hospital corridor interior",
    "delegacia": "police precinct interior",
    "distrito": "police precinct interior",
    "escritório": "office interior", "escritorio": "office interior",
    "sala": "room interior", "quarto": "bedroom interior",
    "cozinha": "kitchen interior", "bar": "dim bar interior",
    "elevador": "elevator interior", "corredor": "long corridor interior",
    "galpão": "warehouse interior", "galpao": "warehouse interior",
    "porão": "basement interior", "porao": "basement interior",
    "igreja": "church interior", "tribunal": "courtroom interior",
    "praia": "grey beach at dusk", "mar": "dark sea",
    "dique": "massive sea wall", "porto": "industrial docks",
    "favela": "hillside favela at night",
    "floresta": "dark forest", "mata": "dark overgrown vegetation",
    "deserto": "dry wasteland", "telhado": "rooftop at night",
    "avenida": "wide city avenue at night, rain, neon signs",
    "rua": "city street at night, rain, neon signs",
    "beco": "narrow alley at night, rain, neon signs",
}
CENARIO_PADRAO = "city street at night, rain, neon signs"


def cenario_da_cena(texto: str) -> str:
    baixo = texto.lower()
    for pt, en in CENARIOS.items():
        if re.search(rf"\b{re.escape(pt)}s?\b", baixo):
            return en
    return CENARIO_PADRAO
# Textura urbana brasileira: e' o que da densidade de camadas que o Gemini tem.
STYLE_RICO = "weathered surfaces, layered depth, foreground detail, cinematic, highly detailed"
NEGATIVE = (
    "chinese text, japanese text, kanji, asian signage, tokyo, "
    "watermark, logo, deformed face, deformed hands, extra limbs, blurry, "
    "low quality, low resolution, jpeg artifacts, nude, nudity, nsfw, exposed breasts, "
    "topless, underwear, sexualized, studio backdrop, plain background, catalog photo, "
    "fashion lookbook, product shot, white background"
)
NEGATIVE_ANCORA = NEGATIVE + ", posing for camera, looking at viewer, centered portrait, static pose"
NEGATIVE_WIDE = NEGATIVE + (
    ", close-up, portrait, headshot, face fills frame, id photo, selfie, "
    "oversaturated, garish colors, cyan and magenta only, clean pristine city"
)

W, H = 1376, 768

# O CLIP e' treinado em ingles: a acao em portugues virava ruido e era cortada.
# Lexico do universo do livro -> substantivos/verbos visuais que o modelo entende.
LEXICO = {
    "cadáver": "dead body on the ground", "corpo": "dead body on the ground",
    "morto": "dead body", "sangue": "blood", "chuva": "pouring rain",
    "beco": "narrow alley", "delegacia": "police station", "distrito": "police precinct",
    "dique": "sea wall", "torre": "tall tower", "ponte": "bridge", "porto": "docks",
    "esgoto": "sewer", "névoa": "fog", "neblina": "fog", "fumaça": "smoke",
    "smog": "thick smog", "arma": "gun", "revólver": "revolver", "faca": "knife",
    "carro": "car", "ambulância": "ambulance", "hospital": "hospital",
    "laboratório": "laboratory", "implante": "cybernetic implant",
    "prótese": "prosthetic limb", "andaime": "scaffolding", "favela": "hillside slum",
    "escada": "staircase", "porta": "doorway", "janela": "window", "espelho": "mirror",
    "mesa": "table", "cigarro": "cigarette", "uísque": "whiskey glass",
    "bar": "bar counter", "chão": "floor", "parede": "wall", "teto": "ceiling",
    "lanterna": "flashlight beam", "tela": "glowing screen", "monitor": "monitor screen",
    "multidão": "crowd of people", "policial": "police officer", "detetive": "detective",
    "criança": "child", "cão": "dog", "rato": "rat", "pássaro": "bird",
    "fogo": "fire", "explosão": "explosion", "ruína": "ruins", "escombros": "rubble",
    "casulo": "biomechanical cocoon", "máquina": "machine", "robô": "robot",
    # Vocabulario de desastre/pos-batalha: e' o que separa "cidade intacta" de "A Ressaca".
    "queimado": "burned wreckage", "queimada": "burned wreckage",
    "cordite": "gunsmoke haze", "tiroteio": "aftermath of a firefight",
    "barricada": "makeshift barricade", "avenida": "wide avenue",
    "destroços": "scattered debris", "cinzas": "ash falling",
    "chorando": "crying", "correndo": "running", "caído": "collapsed on the ground",
    "ajoelhado": "kneeling", "sentado": "sitting", "deitado": "lying down",
    "apontando": "aiming a weapon", "abraço": "embracing",
}


def acao_em_ingles(texto: str, limite: int = 4) -> str:
    """Palavras visuais da cena traduzidas; e' isso que faz o modelo desenhar o que acontece.

    Casamento por limite de palavra: sem isso "porta" casava dentro de "importante" e
    a cena ganhava "doorway" que nao existe no texto.
    """
    baixo = texto.lower()
    achados = []
    for pt, en in LEXICO.items():
        if re.search(rf"\b{re.escape(pt)}s?\b", baixo) and en not in achados:
            achados.append(en)
        if len(achados) >= limite:
            break
    return ", ".join(achados)


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
        r = requests.post(
            f"https://api.telegram.org/bot{tok}/sendPhoto",
            data={"chat_id": chat, "caption": legenda[:1024]},
            files={"photo": f}, timeout=90,
        )
    print(f"  telegram: {r.status_code}")


def lado_a_lado(gemini: Path, local: Path, saida: Path):
    """Gemini a esquerda, local a direita, mesma altura."""
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
    titulo, corpo = extract_chapter_title_and_clean_text(raw)
    titulo, corpo = limpar_titulos(titulo, corpo)
    objs = scenes.split_scenes(corpo, quantidade=10)
    return titulo, objs[min(indice, len(objs)) - 1]


def caber_em_tokens(pipe, partes, teto: int = 74) -> str:
    """Monta o prompt cortando por prioridade ate caber nos 77 tokens do CLIP.

    Deixar o tokenizer truncar sozinho descartava sempre o FIM do prompt - que era
    onde estavam luz e estilo. Aqui o corte e' escolhido, nao sofrido.
    """
    tok = pipe.tokenizer
    escolhidas = []
    for parte in partes:
        if not parte:
            continue
        candidato = ", ".join(escolhidas + [parte])
        if len(tok(candidato).input_ids) <= teto:
            escolhidas.append(parte)
    return ", ".join(escolhidas)


def montar_prompt(pipe, cena, anchor, usa_ancora: bool) -> str:
    """Partes em ordem de prioridade; o que nao couber nos 77 tokens cai pelo fim."""
    # O cenario vem antes do estilo: e' o que decide se a cena e' rua ou laboratorio.
    cenario = cenario_da_cena(cena.texto)
    partes = [cena.shot, cenario, STYLE_NUCLEO]
    if "wide" in cena.shot and cenario is CENARIO_PADRAO:
        partes.append("vast skyline, towering skyscrapers")
    # A acao traduzida vem cedo: e' o que diferencia a cena de um cartao-postal.
    partes.append(acao_em_ingles(cena.texto, limite=3))
    if usa_ancora and anchor:
        # Equilibrio: "subject small in frame" (v5) matava o personagem no quadro;
        # sem nada (v4) virava retrato 3x4. Meio-termo: corpo inteiro, mas legivel.
        # O Gemini poe o personagem EM acao dentro do ambiente, nao posando de frente.
        partes.append("full body visible, mid-distance framing, candid action, looking away")
        roupa = characters.wardrobe(anchor)
        if roupa:
            partes.append(f"wearing {roupa[:32]}")
    partes.append(STYLE_RICO)
    return caber_em_tokens(pipe, partes)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rodada", default="v1")
    args = ap.parse_args()

    print(f"Carregando {MODEL_LABEL}...")
    enc = CLIPVisionModelWithProjection.from_pretrained(
        IP_ADAPTER_REPO, subfolder="models/image_encoder", torch_dtype=torch.float16
    )
    pipe = AutoPipelineForText2Image.from_pretrained(
        BASE_MODEL, image_encoder=enc, torch_dtype=torch.float16,
        variant="fp16", use_safetensors=True,
    )
    pipe.load_ip_adapter(IP_ADAPTER_REPO, subfolder="sdxl_models", weight_name=IP_ADAPTER_WEIGHT)
    pipe.enable_model_cpu_offload()
    pipe.set_progress_bar_config(disable=True)
    print("pronto\n")

    for numero, indice, seed in ALVOS:
        gemini = REPO / "docs" / "public" / "cenas" / f"capitulo_{numero}" / f"cena_{indice}.jpg"
        if not gemini.exists():
            print(f"[cap {numero} cena {indice}] sem referencia Gemini, pulando")
            continue

        titulo, cena = carregar_cena(numero, indice)
        cena.indice = indice
        anchor = characters.pick_anchor(characters.detect(cena.texto))

        # Gemini faz establishing shot SEM personagem: a cidade preenche o quadro.
        # Forcar ancora de identidade em plano aberto era o que virava retrato.
        is_wide = "wide" in cena.shot
        usa_ancora = bool(anchor) and not is_wide

        prompt = montar_prompt(pipe, cena, anchor, usa_ancora)
        negativo = NEGATIVE_WIDE if is_wide else (NEGATIVE_ANCORA if usa_ancora else NEGATIVE)
        print(f"[cap {numero} cena {indice}] shot={cena.shot!r} ancora={'sim: ' + anchor['name'] if usa_ancora else 'NAO (plano de ambiente)'}")
        print(f"  {prompt[:160]}")

        kwargs = dict(
            prompt=prompt[:900], negative_prompt=negativo,
            # 7.0 saturava e "plastificava"; 5.5 devolve textura de filme.
            num_inference_steps=40, guidance_scale=5.5,
            width=W, height=H,
            generator=torch.Generator(device="cuda").manual_seed(seed),
        )
        if usa_ancora:
            # Teto de 0.6: acima disso a referencia de rosto domina e a cena vira retrato.
            pipe.set_ip_adapter_scale(min(cena.identity_scale, 0.6))
            ref = characters.reference_image(anchor)
            kwargs["ip_adapter_image"] = Image.open(ref).convert("RGB")
        else:
            pipe.set_ip_adapter_scale(0.0)
            kwargs["ip_adapter_image"] = Image.new("RGB", (224, 224), (0, 0, 0))

        img = pipe(**kwargs).images[0]
        local = DESTINO / f"cap{numero}_cena{indice}_{args.rodada}.jpg"
        img.save(local, quality=95)

        combo = lado_a_lado(gemini, local, DESTINO / f"COMPARA_cap{numero}_cena{indice}_{args.rodada}.jpg")
        print(f"  -> {local.name}")
        enviar(combo, f"[{args.rodada}] Capitulo {numero} cena {indice} | ESQ=Gemini DIR={MODEL_LABEL} | {cena.shot}")
        print()


if __name__ == "__main__":
    main()

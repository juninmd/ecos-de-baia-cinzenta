from dataclasses import dataclass, field
from typing import Dict, List, Optional

from scripts.daily_telegram import characters

STYLE = (
    "cinematic still, neo-noir cyberpunk, volumetric rain, teal and orange neon, "
    "dramatic lighting, film grain, 8k"
)
NEGATIVE = "text, watermark, logo, deformed face, extra limbs, blurry"
MOTION_HINTS = [
    "slow cinematic push-in, rain falling, neon signs flickering",
    "slow lateral dolly, drifting fog, subtle character breathing",
    "gentle crane up, flickering lights, distant sparks",
    "slow pull-back reveal, rain streaks on the lens",
]
# Enquadramentos alternados: sem isso toda cena vira o mesmo close-up frontal.
SHOTS = [
    "wide establishing shot",
    "medium shot",
    "over-the-shoulder shot",
    "low angle shot",
    "close-up",
    "high angle wide shot",
    # Com dez cenas por capítulo a lista de seis reciclava a partir da sétima e o
    # capítulo terminava com dois pares de imagens quase idênticas.
    "dutch angle medium shot",
    "extreme close-up on hands",
    "wide two-shot",
    "medium tracking shot from behind",
]
STYLE_CURTO = "neo-noir cyberpunk, rainy night, neon lighting, cinematic, film grain"


@dataclass
class Scene:
    indice: int
    texto: str
    personagens: List[Dict] = field(default_factory=list)
    shot_hint: Optional[str] = None

    @property
    def motion_prompt(self) -> str:
        return MOTION_HINTS[(self.indice - 1) % len(MOTION_HINTS)]

    @property
    def shot(self) -> str:
        # Diálogo pede enquadramento de conversa, não a rotação padrão de cenas.
        return self.shot_hint or SHOTS[(self.indice - 1) % len(SHOTS)]

    @property
    def identity_scale(self) -> float:
        """Peso da âncora de identidade conforme o enquadramento.

        O IP-Adapter puxa a composição para retrato: com peso alto, plano aberto vira
        close-up. Em plano fechado o rosto domina o quadro e o peso pode ser alto.
        """
        if "wide" in self.shot:
            return 0.55
        if self.shot in ("close-up", "medium shot"):
            return 0.9
        return 0.75

    @property
    def texto_limpo(self) -> str:
        """Trecho sem marcação: o negrito do markdown vira texto queimado na imagem.

        "**BRAGA, A. — 1º Distrito.**" entrava inteiro no prompt e o modelo desenhava a
        placa com o nome escrito nela, justamente o que a cláusula SEM_TEXTO proíbe.
        """
        return " ".join(self.texto.replace("*", "").replace("_", " ").split())

    @property
    def action(self) -> str:
        """Frase-chave visual da cena, curta o bastante para o limite do CLIP.

        Falas viram prompts ruins ("Ameace com obstrução de justiça") — a preferência
        é sempre por narração descritiva.
        """
        frases = [" ".join(b.replace("*", "").split()) for b in self.texto.split(".")]
        candidatas = [f for f in frases if len(f) > 30]
        narrativas = [f for f in candidatas if "—" not in f and "disse" not in f.lower()]
        escolhida = (narrativas or candidatas or [self.texto])[0]
        return " ".join(escolhida.replace("—", " ").split())[:110]

    def compact_prompt_sem_personagem(self, local: str = "") -> str:
        """Plano de ambiente: sem âncora de identidade, só enquadramento, lugar e ação."""
        partes = [self.shot]
        if local:
            partes.append(local[:40])
        partes.append(self.action)
        partes.append(STYLE_CURTO)
        return ", ".join(partes)

    def compact_prompt(self, anchor: Dict, local: str = "") -> str:
        """Prompt curto para modelos com CLIP (77 tokens): SDXL corta o resto fora.

        A identidade vem da imagem de referência, então aqui só entra o que o texto
        precisa carregar: roupa, enquadramento, ação e estilo.
        """
        partes = [self.shot]
        roupa = characters.wardrobe(anchor)
        if roupa:
            partes.append(f"person wearing {roupa[:60]}")
        if local:
            partes.append(local[:40])
        partes.append(self.action)
        partes.append(STYLE_CURTO)
        return ", ".join(partes)

    def image_prompt(self, titulo: str, local: str = "") -> str:
        partes = [f"Scene from the chapter '{titulo}'"]
        if local:
            partes.append(f"setting: {local}")
        if self.personagens:
            partes.append("characters: " + "; ".join(characters.describe(c) for c in self.personagens))
        partes.append(f"action: {self.texto_limpo[:260]}")
        partes.append(STYLE)
        return ". ".join(partes)

    def edit_prompt(self, anchor: Dict, local: str = "", roupa: str = "") -> str:
        """Prompt for Kontext: keep the reference identity, change the scene around it.

        `roupa` chega resolvida quando a ficha declara fases de vestuário — o Dante do
        capítulo 27 usa fedora, o do 104 em diante usa macacão técnico.
        """
        partes = [
            f"Keep this exact person's face, hair and beard unchanged: {anchor['name']}",
        ]
        roupa = roupa or characters.wardrobe(anchor)
        if roupa:
            # Cláusula própria e cedo no prompt: enterrado no descritor, o modelo troca a roupa.
            partes.append(f"he must keep wearing his signature outfit: {roupa}")
        partes.append(f"place the same person in this scene: {self.texto_limpo[:200]}")
        canonico = characters.describe(anchor)
        if canonico:
            partes.append(f"canonical look that must not change: {canonico}")
        if local:
            partes.append(f"setting: {local}")
        partes.append(STYLE)
        return ". ".join(partes)


def blocos_de_texto(texto: str) -> List[str]:
    """Todos os parágrafos, sem descartar nada.

    Falas curtas ("— Some daqui.") são parágrafos válidos: se forem descartadas, a
    narração do episódio pula pedaços da história. Elas são anexadas ao bloco anterior.
    """
    blocos: List[str] = []
    for linha in texto.split("\n"):
        linha = linha.strip()
        if not linha:
            continue
        if len(linha) < 60 and blocos:
            blocos[-1] = f"{blocos[-1]} {linha}"
        else:
            blocos.append(linha)
    return blocos


def split_scenes(texto: str, quantidade: int = 4) -> List[Scene]:
    """Split the chapter into N narrative beats, covering the whole text."""
    paragrafos = blocos_de_texto(texto)
    if not paragrafos:
        paragrafos = [texto.strip()]
    quantidade = max(1, min(quantidade, len(paragrafos)))
    passo = len(paragrafos) / quantidade
    cenas = []
    for i in range(quantidade):
        bloco = paragrafos[int(i * passo):int((i + 1) * passo)] or [paragrafos[-1]]
        trecho = " ".join(bloco)
        cenas.append(Scene(indice=i + 1, texto=trecho, personagens=characters.detect(trecho)))
    return cenas

import re
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

# --- Receita validada contra as imagens do Gemini (ver scripts/iterar_qualidade.py) ---

# Só estilo e mundo; NUNCA lugar nem clima. Fixar "rua chuvosa" aqui fazia
# laboratório (cap. 25) e caverna (cap. 12) virarem rua molhada também.
ESTILO_MUNDO = "gritty cyberpunk brazil, desaturated grimy colors, dramatic lighting"
ESTILO_ACABAMENTO = "weathered surfaces, layered depth, foreground detail, cinematic, highly detailed"

CENARIO_PADRAO = "city street at night, rain, neon signs"
CENARIOS = {
    "laboratório": "sterile white high-tech laboratory interior",
    "caverna": "vast underground cavern",
    "túnel": "concrete tunnel interior", "esgoto": "sewer tunnel interior",
    "hospital": "hospital corridor interior", "delegacia": "police precinct interior",
    "distrito": "police precinct interior", "escritório": "office interior",
    "sala": "room interior", "quarto": "bedroom interior",
    "cozinha": "kitchen interior", "bar": "dim bar interior",
    "elevador": "elevator interior", "corredor": "long corridor interior",
    "galpão": "warehouse interior", "porão": "basement interior",
    "igreja": "church interior", "tribunal": "courtroom interior",
    "praia": "grey beach at dusk", "dique": "massive sea wall",
    "porto": "industrial docks", "favela": "hillside favela at night",
    "floresta": "dark forest", "telhado": "rooftop at night",
    "avenida": "wide city avenue at night, rain, neon signs",
    "rua": CENARIO_PADRAO, "beco": "narrow alley at night, rain, neon signs",
}

# O IP-Adapter plus-face recentraliza o rosto: sem dizer ONDE o corpo está no
# quadro, todo plano com personagem vira retrato 3x4.
ENCENACAO = {
    "medium shot": "person in the foreground at the left, seen from the side, waist up",
    "over-the-shoulder shot": "seen from behind over the shoulder, back of head in foreground",
    "low angle shot": "camera low near the ground looking up, full body against the sky",
    "close-up": "face fills the frame, shallow depth of field",
    "dutch angle medium shot": "tilted camera, person off-center, full body",
    "extreme close-up on hands": "only the hands, no face visible",
    "wide two-shot": "two people far apart, both full body, wide empty space between",
    "medium tracking shot from behind": "following behind the person, back turned to camera",
}
ENCENACAO_PADRAO = "full body visible, off-center, candid action, looking away"

# O CLIP é treinado em inglês: ação em português vira ruído e ainda gasta token.
LEXICO_VISUAL = {
    "cadáver": "dead body on the ground", "corpo": "dead body on the ground",
    "sangue": "blood", "chuva": "pouring rain", "beco": "narrow alley",
    "dique": "sea wall", "torre": "tall tower", "ponte": "bridge",
    "esgoto": "sewer", "névoa": "fog", "fumaça": "smoke", "smog": "thick smog",
    "arma": "gun", "faca": "knife", "carro": "car", "ambulância": "ambulance",
    "implante": "cybernetic implant", "prótese": "prosthetic limb",
    "escada": "staircase", "janela": "window", "espelho": "mirror",
    "cigarro": "cigarette", "lanterna": "flashlight beam", "tela": "glowing screen",
    "multidão": "crowd of people", "policial": "police officer",
    "criança": "child", "fogo": "fire", "explosão": "explosion",
    "escombros": "rubble", "casulo": "biomechanical cocoon",
    "queimado": "burned wreckage", "queimada": "burned wreckage",
    "cordite": "gunsmoke haze", "barricada": "makeshift barricade",
    "destroços": "scattered debris", "chorando": "crying", "correndo": "running",
    "ajoelhado": "kneeling", "deitado": "lying down", "apontando": "aiming a weapon",
}


def _casa(termo: str, texto_lower: str) -> bool:
    """Limite de palavra: sem isso "porta" casava dentro de "importante"."""
    return re.search(rf"\b{re.escape(termo)}s?\b", texto_lower) is not None


def cenario_do_texto(texto: str) -> str:
    baixo = texto.lower()
    for pt, en in CENARIOS.items():
        if _casa(pt, baixo):
            return en
    return CENARIO_PADRAO


def palavras_visuais(texto: str, limite: int = 3) -> str:
    baixo = texto.lower()
    achados: List[str] = []
    for pt, en in LEXICO_VISUAL.items():
        if _casa(pt, baixo) and en not in achados:
            achados.append(en)
        if len(achados) >= limite:
            break
    return ", ".join(achados)


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

        Valores calibrados na comparação contra as imagens do Gemini: plano aberto vai
        com peso ZERO (o establishing shot do Gemini também não tem personagem — era o
        adaptador que virava toda cena em retrato 3x4), e o teto dos demais é 0.6, que
        ainda preserva a fisionomia. Abaixo de ~0.4 a identidade quebra de vez.
        """
        if "wide" in self.shot:
            return 0.0
        # Plano de mãos não precisa de identidade facial: com o plus-face ativo o
        # modelo insistia em desenhar o rosto — contra a própria instrução do plano —
        # e ainda entregava mão deformada (cap. 8 cena 8).
        if self.shot == "extreme close-up on hands":
            return 0.0
        if self.shot == "close-up":
            return 0.85
        # 0.6 e 0.45 ainda saíam como retrato selfie: o plus-face recentraliza o rosto
        # e vence a encenação. Em 0.30 a composição finalmente obedece (corpo inteiro,
        # descentralizado, ambiente à volta) e a fisionomia continua reconhecível.
        # A troca de gênero que eu tinha visto em peso baixo vinha do "man wearing"
        # fixo no prompt, já corrigido — não do peso.
        # Custo assumido: a semelhança fica um pouco mais solta que em 0.6.
        return 0.30

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

    def _partes_base(self, local: str) -> List[str]:
        """Ordem = prioridade. O que não couber nos 77 tokens do CLIP cai pelo fim."""
        cenario = local[:40] if local else cenario_do_texto(self.texto)
        partes = [self.shot, cenario, ESTILO_MUNDO]
        if "wide" in self.shot and cenario == CENARIO_PADRAO:
            partes.append("vast skyline, towering skyscrapers")
        partes.append(palavras_visuais(self.texto))
        return partes

    def compact_prompt_sem_personagem(self, local: str = "") -> str:
        """Plano de ambiente: sem âncora de identidade, só enquadramento, lugar e ação."""
        partes = self._partes_base(local)
        partes.append(ESTILO_ACABAMENTO)
        return ", ".join(p for p in partes if p)

    def compact_prompt(self, anchor: Dict, local: str = "") -> str:
        """Prompt curto para modelos com CLIP (77 tokens): SDXL corta o resto fora.

        A identidade vem da imagem de referência, então aqui só entra o que o texto
        precisa carregar: cenário, ação traduzida, encenação, roupa e estilo.
        """
        partes = self._partes_base(local)
        partes.append(ENCENACAO.get(self.shot, ENCENACAO_PADRAO))
        roupa = characters.wardrobe(anchor)
        if roupa:
            # "person", não "man": a âncora pode ser personagem feminina.
            partes.append(f"wearing {roupa[:32]}")
        partes.append(ESTILO_ACABAMENTO)
        return ", ".join(p for p in partes if p)

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

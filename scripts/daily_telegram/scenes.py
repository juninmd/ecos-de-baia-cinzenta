from dataclasses import dataclass, field
from typing import Dict, List

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


@dataclass
class Scene:
    indice: int
    texto: str
    personagens: List[Dict] = field(default_factory=list)

    @property
    def motion_prompt(self) -> str:
        return MOTION_HINTS[(self.indice - 1) % len(MOTION_HINTS)]

    def image_prompt(self, titulo: str, local: str = "") -> str:
        partes = [f"Scene from the chapter '{titulo}'"]
        if local:
            partes.append(f"setting: {local}")
        if self.personagens:
            partes.append("characters: " + "; ".join(characters.describe(c) for c in self.personagens))
        partes.append(f"action: {self.texto[:260]}")
        partes.append(STYLE)
        return ". ".join(partes)

    def edit_prompt(self, anchor: Dict, local: str = "") -> str:
        """Prompt for Kontext: keep the reference identity, change the scene around it."""
        partes = [
            f"Keep this exact person's face, hair, beard and clothing unchanged: {anchor['name']}",
            f"place the same person in this scene: {self.texto[:200]}",
        ]
        canonico = characters.describe(anchor)
        if canonico:
            partes.append(f"canonical look that must not change: {canonico}")
        if local:
            partes.append(f"setting: {local}")
        partes.append(STYLE)
        return ". ".join(partes)


def split_scenes(texto: str, quantidade: int = 4) -> List[Scene]:
    """Split the chapter into N narrative beats, keeping paragraphs intact."""
    paragrafos = [p.strip() for p in texto.split("\n") if len(p.strip()) > 60]
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

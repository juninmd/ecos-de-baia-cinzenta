"""Identidade adulta de Aria em projeções holográficas, sem corpo físico.

Decisão do autor (23/11/2026): o avatar só aparece nos três capítulos em que o texto
o mostra. No resto do livro, Aria é voz e o drive físico, nunca uma mulher em cena.
"""

HOLOGRAMAS = frozenset({57, 136, 168})

ROUPA = (
    "closed high-neck charcoal geometric data-mesh jacket, long sleeves, blue seams"
)
IDENTIDADE = (
    "Aria is a mature adult woman avatar, with an oval face, long straight platinum "
    "hair, one blue and one amber eye, and a calm assured gaze. Preserve her exact "
    "canonical reference face and adult expression lines."
)
SUPORTE = (
    "Aria exists in a 7cm matte titanium and black polymer computational drive. "
    "Her mature adult avatar may appear as a translucent volumetric hologram "
    "projected by the module or connected equipment, naturally integrated into "
    "the scene. Use luminous data-mesh edges, visible light and partial transparency "
    "to distinguish her from flesh. Never depict a child, a flesh body or an android. "
    "Do not insert a giant monitor, laptop or television to stand in for her. "
    "If power or projection is unavailable, show only the inactive physical drive."
)


def prompt_ancora(texto: str, plano: str, roupa: str = "") -> str:
    """A âncora é um avatar, portanto o comando genérico de pessoa não se aplica."""
    return (
        f"Wardrobe: {ROUPA}. {IDENTIDADE} {SUPORTE} "
        f"Canonical wardrobe details: {roupa}. "
        f"Create a new photograph of this scene, with a different pose and action: "
        f"{texto[:260]}. Mandatory framing: {plano}. "
        "Preserve identity while adapting her holographic pose and scale to the scene. "
        "Photorealistic dirty 35mm film still, practical lighting, fine film grain."
    )


def holograma(capitulo: float) -> bool:
    """Só os capítulos em que o texto mostra a projeção podem desenhar o avatar."""
    return int(capitulo) in HOLOGRAMAS


def filtrar(personagens: list, capitulo: float) -> list:
    """Fora dos capítulos de holograma, Aria não é âncora nem retrato da cena."""
    if holograma(capitulo):
        return list(personagens)
    return [p for p in personagens if p.get("name") != "Aria"]


def clausula(elenco: list, capitulo: float = 0) -> str:
    """Vale também quando Aria aparece com outro personagem como âncora."""
    if not any(p.get("nome") == "Aria" for p in elenco):
        return ""
    if capitulo > 169:
        return (
            ". ARIA CONTINUITY: Aria is destroyed in chapter 169. In present-time "
            "action, do not add a live avatar, a functioning drive, or her voice. "
            "A mention of her is not physical presence."
        )
    if not holograma(capitulo):
        return (
            ". ARIA DRIVE ONLY: Aria is a voice inside a 7cm matte titanium and black "
            "polymer drive with a blue LED. Do not depict any woman, avatar, face or "
            "hologram for her; show at most the small physical drive."
        )
    return f". ARIA HOLOGRAM: Wardrobe: {ROUPA}. {IDENTIDADE} {SUPORTE}"

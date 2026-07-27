"""Elenco de vozes: cada personagem fala sempre com a mesma voz (edge-tts, grátis)."""
from typing import Dict, Optional, Tuple

# Voz fixa para os principais — a identidade sonora é tão canônica quanto a visual.
ELENCO: Dict[str, Tuple[str, str, str]] = {
    "Gabriel \"Gabo\" Moretti": ("pt-BR-AntonioNeural", "-8%", "-6Hz"),
    "Valéria \"Val\" Cruz": ("pt-BR-FranciscaNeural", "+6%", "+8Hz"),
    "Elena Moretti": ("pt-BR-ThalitaMultilingualNeural", "+0%", "+0Hz"),
    "Aria Moretti (Unidade Autônoma)": ("pt-BR-ThalitaMultilingualNeural", "-4%", "-12Hz"),
    "Inspetor Rangel": ("pt-PT-DuarteNeural", "+0%", "+6Hz"),
    "Diretor Dantas": ("en-US-BrianMultilingualNeural", "-10%", "-10Hz"),
    "Capitão Jonas Vilar": ("en-US-AndrewMultilingualNeural", "-6%", "-4Hz"),
    "O Taxidermista (Alvo Prioritário #1)": ("it-IT-GiuseppeMultilingualNeural", "-14%", "-16Hz"),
}

NARRADOR = ("pt-BR-AntonioNeural", "-6%", "-4Hz")  # Gabo narra em primeira pessoa

# Antonio e Francisca ficam no fim: são as vozes do Gabo e da Val, e figurante com o
# mesmo timbre do protagonista confunde quem está ouvindo.
POOL_MASCULINO = [
    ("pt-PT-DuarteNeural", "-4%", "-8Hz"),
    ("en-US-BrianMultilingualNeural", "+0%", "+4Hz"),
    ("de-DE-FlorianMultilingualNeural", "-8%", "-6Hz"),
    ("en-AU-WilliamMultilingualNeural", "+2%", "-2Hz"),
    ("pt-BR-AntonioNeural", "+6%", "+14Hz"),
]
POOL_FEMININO = [
    ("pt-PT-RaquelNeural", "+0%", "+0Hz"),
    ("pt-BR-ThalitaMultilingualNeural", "+4%", "+6Hz"),
    ("pt-BR-FranciscaNeural", "-4%", "-6Hz"),
    ("en-US-EmmaMultilingualNeural", "+2%", "+8Hz"),
    ("fr-FR-VivienneMultilingualNeural", "-2%", "+2Hz"),
]


def _feminino(char: Dict) -> bool:
    """Gênero pelo texto do dossiê: conta pronomes em vez de adivinhar pelo nome."""
    descricao = f" {(char.get('description') or '').lower()} "
    elas = descricao.count(" ela ") + descricao.count(" dela ") + descricao.count(" sua ")
    eles = descricao.count(" ele ") + descricao.count(" dele ") + descricao.count(" seu ")
    if elas != eles:
        return elas > eles
    return char["name"].split()[0].rstrip('"').endswith("a")


def for_character(char: Optional[Dict]) -> Tuple[str, str, str]:
    """Voz do personagem: elenco fixo quando existe, senão sorteio estável pelo nome."""
    if char is None:
        return NARRADOR
    if char["name"] in ELENCO:
        return ELENCO[char["name"]]
    pool = POOL_FEMININO if _feminino(char) else POOL_MASCULINO
    # hash do nome: o mesmo personagem cai sempre na mesma voz, entre execuções
    return pool[sum(ord(c) for c in char["name"]) % len(pool)]

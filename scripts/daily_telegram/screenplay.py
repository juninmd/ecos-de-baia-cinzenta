"""Converte o capítulo em roteiro: quem fala o quê, e o que é narração."""
import re
from dataclasses import dataclass
from typing import Dict, List, Optional

from scripts.daily_telegram import characters
from scripts.daily_telegram.scenes import blocos_de_texto

TRAVESSAO = re.compile(r"[—–]")
LIMPEZA = re.compile(r"[*`#>\[\]]")
VERBOS_FALA = ("disse", "murmurou", "rosnou", "gritou", "respondeu", "perguntou",
               "sussurrou", "ordenou", "completou", "avisou", "retrucou")


@dataclass
class Beat:
    """Um trecho contínuo dito por uma única voz."""
    indice: int
    tipo: str            # "fala" ou "narracao"
    texto: str
    personagem: Optional[Dict] = None

    @property
    def is_fala(self) -> bool:
        return self.tipo == "fala"


def _limpar(texto: str) -> str:
    return " ".join(LIMPEZA.sub("", texto).split()).strip(" ,;")


FIGURANTE = re.compile(
    r"\b(?:" + "|".join(VERBOS_FALA) + r"|voz d[oe])\s+(?:d[oa]\s+)?(?:o|a)\s+([a-zà-ú]+(?:\s+de\s+[a-zà-ú]+)?)",
    re.IGNORECASE,
)


def _figurante(atribuicao: str) -> Optional[Dict]:
    """Falante sem ficha em personagens.md ('disse o oficial de patrulha').

    Sem isso a conversa perde o interlocutor e a alternância de falas quebra.
    """
    achado = FIGURANTE.search(atribuicao)
    if not achado:
        return None
    nome = achado.group(1).strip().capitalize()
    return {"name": nome, "aliases": [nome], "description": "", "image": None}


def _quem_fala(atribuicao: str, anteriores: List[Dict]) -> Optional[Dict]:
    """Identifica o falante pela deixa ('— disse o oficial') ou alternando a conversa."""
    encontrados = characters.detect(atribuicao, limit=1) if atribuicao else []
    if encontrados:
        return encontrados[0]
    figurante = _figurante(atribuicao) if atribuicao else None
    if figurante:
        return figurante
    # Sem deixa: numa conversa a fala alterna entre os dois últimos falantes.
    anteriores_unicos = []
    for char in reversed(anteriores):
        if char and all(char["name"] != c["name"] for c in anteriores_unicos):
            anteriores_unicos.append(char)
        if len(anteriores_unicos) == 2:
            break
    return anteriores_unicos[1] if len(anteriores_unicos) == 2 else None


def parse(texto: str) -> List[Beat]:
    """Roteiro do capítulo, em ordem, alternando narração e falas."""
    beats: List[Beat] = []
    falantes: List[Dict] = []

    for paragrafo in blocos_de_texto(texto):
        if not TRAVESSAO.match(paragrafo):
            limpo = _limpar(paragrafo)
            if limpo:
                beats.append(Beat(len(beats) + 1, "narracao", limpo))
            continue

        partes = TRAVESSAO.split(paragrafo)[1:]
        falas = [_limpar(p) for p in partes[::2]]
        atribuicoes = [_limpar(p) for p in partes[1::2]]
        falante = _quem_fala(" ".join(atribuicoes), falantes)
        falantes.append(falante)

        for i, fala in enumerate(falas):
            if fala:
                beats.append(Beat(len(beats) + 1, "fala", fala, falante))
            # A deixa ("Gabo rosnou, empurrando o ombro do rapaz") é ação: vira narração
            # quando traz informação, e é descartada quando só diz quem falou.
            if i < len(atribuicoes):
                deixa = atribuicoes[i]
                if len(deixa) > 60 and not deixa.lower().startswith(VERBOS_FALA):
                    beats.append(Beat(len(beats) + 1, "narracao", deixa))
    return beats


def falantes_do_capitulo(beats: List[Beat]) -> List[str]:
    """Elenco que aparece falando, para log e para escolher as âncoras visuais."""
    nomes = []
    for beat in beats:
        if beat.is_fala and beat.personagem and beat.personagem["name"] not in nomes:
            nomes.append(beat.personagem["name"])
    return nomes

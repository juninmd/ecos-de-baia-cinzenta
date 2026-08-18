"""Fase física de cada personagem no capítulo, lida da "Linha do Tempo e Evolução Visual".

A regra 9 do AGENTS.md ("Gabo com exoesqueleto no cap. 105 não pode aparecer sem ele")
não tinha nenhuma implementação: o prompt mandava sempre a descrição canônica do topo da
ficha, que é atemporal. Resultado: o Gabo do capítulo 220 nascia com os dois braços, e o
do 47 sem o exoesqueleto. Aqui a linha do tempo vira um intervalo de capítulos por bullet,
e a cena recebe só o trecho que vale para aquele número.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
PERSONAGENS_MD = REPO_ROOT / "docs" / "personagens.md"

TIMELINE_RE = re.compile(r"^###\s+.*Linha do Tempo", re.MULTILINE)
# O marco pode ser o rótulo do bullet ou vir no meio dele ("... **Capítulo 47:** Confronto").
MARCO_RE = re.compile(r"\*\*(?P<rotulo>[^*\n]*Cap[íi]tulos?[^*\n]*?):?\*\*")
# "Capítulo 105", "Capítulos 115-140", "Capítulos 176 a 217", "Pós-Capítulo 128".
CAPITULOS_RE = re.compile(
    r"(?P<pos>Pós-)?Cap[íi]tulos?\s*(?P<ini>\d+(?:\.\d+)?)"
    r"(?:\s*(?:[-–—]|a)\s*(?P<fim>\d+(?:\.\d+)?))?",
    re.IGNORECASE,
)
INFINITO = 10_000.0
MAX_TEXTO = 300

_cache: Optional[Dict[str, List[Dict]]] = None


def _fases_do_bloco(bloco: str) -> List[Dict]:
    """Marcos de capítulo da linha do tempo, já com intervalo resolvido."""
    fases: List[Dict] = []
    for linha in bloco.splitlines():
        if not linha.lstrip().startswith("*"):
            continue
        marcos = list(MARCO_RE.finditer(linha))
        for i, marco in enumerate(marcos):
            # O texto do marco vai até o próximo marco da mesma linha, ou até o fim dela.
            corte = marcos[i + 1].start() if i + 1 < len(marcos) else len(linha)
            capitulos = CAPITULOS_RE.search(marco.group("rotulo"))
            if not capitulos:
                continue
            inicio = float(capitulos.group("ini"))
            fim = float(capitulos.group("fim")) if capitulos.group("fim") else None
            # "Pós-Capítulo 128" começa depois do 128, não nele.
            if capitulos.group("pos"):
                inicio += 1
            fases.append({
                "rotulo": marco.group("rotulo").strip(),
                "inicio": inicio,
                "fim": fim,
                "texto": linha[marco.end():corte].strip(),
            })

    fases.sort(key=lambda f: f["inicio"])
    # A ficha é cumulativa: o último estado declarado vale até o próximo marco aparecer.
    # Sem isso o capítulo 180 ficava sem fase — entre "175-176" e "185-217" — e o Gabo
    # voltava a ter os dois braços justamente no arco em que perdeu um.
    for i, fase_atual in enumerate(fases):
        proximo = fases[i + 1]["inicio"] if i + 1 < len(fases) else INFINITO
        limite = max(fase_atual["inicio"], proximo - 1)
        fase_atual["fim"] = max(fase_atual["fim"] or 0, limite)
    return fases


def _carregar(caminho: Path = PERSONAGENS_MD) -> Dict[str, List[Dict]]:
    if not caminho.exists():
        return {}
    linhas_por_personagem: Dict[str, List[Dict]] = {}
    for secao in caminho.read_text(encoding="utf-8").split("\n## ")[1:]:
        nome = secao.splitlines()[0].strip().replace("*", "").strip()
        marcador = TIMELINE_RE.search(secao)
        if not marcador:
            continue
        fases = _fases_do_bloco(secao[marcador.end():])
        if fases:
            linhas_por_personagem[nome] = fases
    return linhas_por_personagem


def linhas_do_tempo(caminho: Path = PERSONAGENS_MD) -> Dict[str, List[Dict]]:
    global _cache
    if _cache is None or caminho != PERSONAGENS_MD:
        dados = _carregar(caminho)
        if caminho != PERSONAGENS_MD:
            return dados
        _cache = dados
    return _cache


def _resumir(texto: str) -> str:
    """Frase visual do bullet: o prompt não aguenta o parágrafo inteiro da ficha."""
    limpo = " ".join(texto.replace("*", "").split())
    aparencia = re.search(r"Apar[êe]ncia:\s*(.+)", limpo)
    if aparencia:
        limpo = aparencia.group(1)
    if len(limpo) <= MAX_TEXTO:
        return limpo
    corte = limpo[:MAX_TEXTO]
    ponto = corte.rfind(". ")
    return (corte[:ponto + 1] if ponto > 80 else corte).strip()


def fase(nome: str, capitulo: float) -> str:
    """Estado físico canônico do personagem naquele capítulo ("" se a ficha não diz)."""
    aplicaveis = [
        f for f in linhas_do_tempo().get(nome, [])
        if f["inicio"] <= capitulo <= f["fim"]
    ]
    if not aplicaveis:
        return ""
    # A fase mais recente que ainda cobre o capítulo é a que vale.
    escolhida = max(aplicaveis, key=lambda f: f["inicio"])
    return _resumir(escolhida["texto"])


def clausula(elenco: List[Dict], capitulo: float) -> str:
    """Cláusula de continuidade para o fim do prompt, um item por personagem em cena."""
    marcos = []
    for personagem in elenco:
        estado = fase(personagem["nome"], capitulo)
        if estado:
            marcos.append(f"{personagem['nome']}: {estado}")
    if not marcos:
        return ""
    return (
        ". MANDATORY CONTINUITY for this exact chapter, the physical state below is "
        "canon and must be visible (it overrides the general character description): "
        + " | ".join(marcos)
    )


def primeiro_marco(nome: str) -> Optional[float]:
    """Capítulo em que o personagem entra na forma atual dele, se a ficha declarar um.

    É o que decide qual fase do vestuário vale: o Dante do capítulo 27 ainda é o
    sobretudo de couro, e o do 104 em diante é o macacão técnico.
    """
    fases = linhas_do_tempo().get(nome)
    return fases[0]["inicio"] if fases else None

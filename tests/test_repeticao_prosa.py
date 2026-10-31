"""Impede que a prosa volte a se copiar entre capitulos.

A revisao de 30/10/2026 mediu o que se repetia: a mesma descricao de Valeria em
12 capitulos, o mesmo LED de Aria em 6, 74 paragrafos abrindo com "Gabo olhou
para". Estes limites sao o piso conquistado, nao um ideal: passam com margem e
falham quando alguem volta a colar a descricao canonica em cada cena.
"""

from __future__ import annotations

import re
import unicodedata
from collections import defaultdict
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent / "docs"

DENSIDADE_MAXIMA = 1.8
CAPITULOS_MAXIMOS_POR_FRASE = 6
FRASES_CANONICAS = ("filamentos de led azul na franja",)


def normalizar(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", texto.lower())
    return "".join(c for c in sem_acento if not unicodedata.combining(c))


def texto_do_capitulo(caminho: Path) -> str:
    bruto = caminho.read_text(encoding="utf-8")
    bruto = re.sub(r"\A---.*?---\s*", "", bruto, flags=re.S)
    bruto = re.sub(r"^#.*$", "", bruto, flags=re.M)
    bruto = re.sub(r"<!--.*?-->", "", bruto, flags=re.S)
    return normalizar(bruto)


def capitulos() -> list[tuple[str, str]]:
    def ordem(p: Path) -> float:
        return float(re.search(r"capitulo-([\d.]+)", p.name).group(1).rstrip("."))

    return [(p.stem, texto_do_capitulo(p)) for p in sorted(DOCS.glob("capitulo-*.md"), key=ordem)]


def test_frases_de_sete_palavras_nao_se_espalham():
    onde: dict[str, set[str]] = defaultdict(set)
    for nome, texto in capitulos():
        palavras = re.findall(r"[a-z0-9]+", texto)
        for i in range(len(palavras) - 6):
            onde[" ".join(palavras[i : i + 7])].add(nome)

    piores = sorted(onde.items(), key=lambda kv: -len(kv[1]))[:3]
    relato = "; ".join(f"{len(c)}x '{g}'" for g, c in piores)
    assert len(piores[0][1]) <= CAPITULOS_MAXIMOS_POR_FRASE, relato


def test_descricao_canonica_nao_vira_estribilho():
    for frase in FRASES_CANONICAS:
        repetidores = [nome for nome, texto in capitulos() if frase in texto]
        assert len(repetidores) <= 1, f"'{frase}' em {len(repetidores)} capitulos: {repetidores}"


def test_densidade_de_tiques_nao_sobe():
    from scripts.auditoria_tiques import medir

    dados = medir()
    media = sum(d["por_mil"] for d in dados) / len(dados)
    assert media <= DENSIDADE_MAXIMA, f"densidade media {media:.2f} > {DENSIDADE_MAXIMA}"
    pior = max(dados, key=lambda d: d["por_mil"])
    assert pior["por_mil"] <= 7.5, f"capitulo {pior['cap']} com {pior['por_mil']} tiques/mil"


def test_formula_de_incerteza_fica_contida():
    """Aria precisa ter limites, nao um bordao: 'nao consigo/posso' em toda cena."""
    falada = re.compile(r"não (?:consigo|posso|tenho como)|não há garantia", re.I)
    total = 0
    for caminho in sorted(DOCS.glob("capitulo-*.md")):
        bruto = caminho.read_text(encoding="utf-8")
        for bloco in re.findall(r"\*([^*]+)\*", bruto):
            total += len(falada.findall(bloco))
    assert total <= 45, f"{total} formulas de incerteza em falas; teto 45"

    # Guarda global: o bordao tambem nao pode voltar pelo dialogo sem italico.
    bruto_geral = " ".join(c.read_text(encoding="utf-8") for c in sorted(DOCS.glob("capitulo-*.md")))
    assert len(falada.findall(bruto_geral)) <= 175

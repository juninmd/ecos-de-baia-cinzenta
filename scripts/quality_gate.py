#!/usr/bin/env python3
"""Aplica a régua de qualidade do AGENTS.md em todos os capítulos.

Mede o que é mensurável (portões duros + eixos com pegada textual) e gera
`docs/qualidade_capitulos.md` ordenado do pior para o melhor, para que a
revisão manual comece por onde dói.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
RELATORIO = DOCS / "qualidade_capitulos.md"

MIN_PALAVRAS = 600  # portão duro: abaixo disso é cena, não capítulo
ALVO_PALAVRAS = 1100  # alvo editorial; entre o portão e o alvo o capítulo entra em "curto"

SENTIDOS = {
    "olfato": r"cheir|fedor|odor|aroma|perfume|f[ée]tid",
    "audição": r"som|ru[íi]do|ecoa|zumbi|estalo|silêncio|gemi|rang|assobi|estrondo",
    "tato": r"frio|quente|áspero|úmid|liso|gelad|queima|mord[ei]|pele|textura",
    "paladar": r"gosto|sabor|amarg|azed|bile|salgad|metálico na l[íi]ngua",
}
CUSTO = r"perde[u]?|perd[ai]|morre|morri|morto|amputa|quebr|arranc|sangr|cicatriz|sacrif|nunca mais"
CONFLITO = r"—\s*\w"  # travessão de diálogo
CONSEQUENCIA = r"Cap[íi]tulo \d+|lembr|desde (o|a) |anos atrás|na Torre|no Dil[úu]vio"

# Traços canônicos que não podem ser violados (ver docs/personagens.md).
VIOLACOES = {
    "Gabo fumando": r"\b(Gabo|Gabriel)\b[^.!?\n]{0,40}?\b(fuma|fumou|fumava|fumando|tragou)\b",
    "vício em nicotina": r"(v[íi]cio|abstin[êe]ncia|fissura)[^.!?\n]{0,40}(nicotina|cigarro|tabaco)",
}


def num(p: Path) -> tuple[int, int]:
    m = re.match(r"capitulo-(\d+)(?:\.(\d+))?\.md$", p.name)
    return (int(m.group(1)), int(m.group(2) or 0)) if m else (10**6, 0)


def corpo(texto: str) -> str:
    """Só a narrativa: metadados e frontmatter não contam como prosa."""
    texto = re.sub(r"^---\n.*?\n---\n", "", texto, flags=re.S)
    texto = re.sub(r"^##? (Metadados|Resumo)\n(?:[-*].*\n|\n)*", "", texto, flags=re.M)
    return texto


def avalia(p: Path) -> dict:
    bruto = p.read_text(encoding="utf-8")
    texto = corpo(bruto)
    palavras = len(texto.split())
    baixo = texto.lower()

    duros, avisos = [], []
    if palavras < MIN_PALAVRAS:
        duros.append(f"D1 extensão ({palavras} palavras)")
    elif palavras < ALVO_PALAVRAS:
        avisos.append(f"curto ({palavras})")
    h1 = re.findall(r"^# (.+)$", bruto, re.M)
    if len(h1) != 1:
        duros.append(f"D2 títulos H1: {len(h1)}")
    if not re.search(r"(Personagens Presentes|characters)", bruto):
        duros.append("D3 elenco não declarado")
    for nome, padrao in VIOLACOES.items():
        if re.search(padrao, texto, re.I):
            duros.append(f"D4 {nome}")

    sentidos = sum(1 for rx in SENTIDOS.values() if re.search(rx, baixo))
    notas = {
        "atmosfera": 2 if sentidos >= 3 else sentidos and 1 or 0,
        "custo": 2 if len(re.findall(CUSTO, baixo)) >= 4 else (1 if re.search(CUSTO, baixo) else 0),
        "voz": 2 if len(re.findall(CONFLITO, texto)) >= 12 else
              (1 if len(re.findall(CONFLITO, texto)) >= 4 else 0),
        "ritmo": 2 if palavras and len(re.findall(CONFLITO, texto)) / max(palavras, 1) > 0.008
                 else (1 if re.search(CONFLITO, texto) else 0),
        "consequência": 2 if len(re.findall(CONSEQUENCIA, texto, re.I)) >= 3 else
                        (1 if re.search(CONSEQUENCIA, texto, re.I) else 0),
    }
    return {
        "arquivo": p.name,
        "titulo": h1[0] if h1 else "(sem título)",
        "palavras": palavras,
        "sentidos": sentidos,
        "notas": notas,
        "total": sum(notas.values()),
        "duros": duros,
        "avisos": avisos,
    }


def veredito(r: dict) -> str:
    if r["duros"]:
        return "🚫 REPROVADO"
    return {10: "⭐ obra-prima", 9: "⭐ obra-prima"}.get(
        r["total"], "✅ publicável" if r["total"] >= 7 else
        ("⚠️ revisar" if r["total"] >= 5 else "🔴 reescrever"))


def main() -> int:
    caps = sorted(DOCS.glob("capitulo-*.md"), key=num)
    resultados = [avalia(p) for p in caps]
    ruins = sorted(resultados, key=lambda r: (not r["duros"], r["total"], r["palavras"]))

    linhas = [
        "# Régua de Qualidade dos Capítulos",
        "",
        "> Gerado por `scripts/quality_gate.py` conforme o padrão do `AGENTS.md`.",
        "> Ordenado do pior para o melhor: a revisão manual começa no topo.",
        "",
        f"- **Capítulos avaliados:** {len(resultados)}",
        f"- **Reprovados em portão duro:** {sum(1 for r in resultados if r['duros'])}",
        f"- **Abaixo do alvo de {ALVO_PALAVRAS} palavras:** {sum(1 for r in resultados if r['avisos'])}",
        f"- **Nota média:** {sum(r['total'] for r in resultados) / max(len(resultados), 1):.1f}/10",
        "",
        "| Capítulo | Palavras | Atm | Custo | Voz | Ritmo | Conseq | Nota | Veredito | Portões |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in ruins:
        n = r["notas"]
        linhas.append(
            f"| {r['titulo'][:44]} | {r['palavras']} | {n['atmosfera']} | {n['custo']} | "
            f"{n['voz']} | {n['ritmo']} | {n['consequência']} | **{r['total']}** | "
            f"{veredito(r)} | {', '.join(r['duros'] + r['avisos']) or '—'} |"
        )
    RELATORIO.write_text("\n".join(linhas) + "\n", encoding="utf-8")

    reprovados = [r for r in resultados if r["duros"]]
    print(f"📏 {len(resultados)} capítulos avaliados")
    print(f"   média: {sum(r['total'] for r in resultados) / len(resultados):.1f}/10")
    print(f"   reprovados em portão duro: {len(reprovados)}")
    for r in reprovados[:20]:
        print(f"   🚫 {r['arquivo']}: {', '.join(r['duros'])}")
    print(f"\n📝 relatório em {RELATORIO.relative_to(ROOT)}")
    return 1 if reprovados else 0


if __name__ == "__main__":
    sys.exit(main())

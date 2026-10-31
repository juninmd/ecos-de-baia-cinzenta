"""Mede o que se repete entre capítulos: frases, aberturas e fechamentos.

Uso:
    uv run --no-sync python scripts/auditoria_repeticao.py
    uv run --no-sync python scripts/auditoria_repeticao.py --min 5 --top 15

O relatório responde à pergunta "o que soa parecido?" com evidência:
n-gramas repetidos, primeiras palavras de parágrafo e última linha de cada
capítulo. Não julga qualidade; localiza tique para a revisão humana.
"""

from __future__ import annotations

import argparse
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DOCS = RAIZ / "docs"


def normalizar(texto: str) -> str:
    """Minúsculas sem acento, para comparar superfície sem perder palavras."""
    sem_acento = unicodedata.normalize("NFKD", texto.lower())
    return "".join(c for c in sem_acento if not unicodedata.combining(c))


def limpar(caminho: Path) -> str:
    texto = caminho.read_text(encoding="utf-8")
    texto = re.sub(r"\A---.*?---\s*", "", texto, flags=re.S)
    texto = re.sub(r"^#.*$", "", texto, flags=re.M)
    texto = re.sub(r"<!--.*?-->", "", texto, flags=re.S)
    return texto


def capitulos() -> list[tuple[str, str]]:
    def chave(p: Path) -> float:
        m = re.search(r"capitulo-([\d.]+)\.md$", p.name)
        return float(m.group(1).rstrip(".")) if m else 0.0

    arquivos = sorted(DOCS.glob("capitulo-*.md"), key=chave)
    return [(a.stem.replace("capitulo-", "cap "), limpar(a)) for a in arquivos]


def paragrafos(texto: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", texto) if p.strip()]


def palavras(texto: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", normalizar(texto))


def ngramas(texto: str, n: int) -> list[str]:
    p = palavras(texto)
    return [" ".join(p[i : i + n]) for i in range(len(p) - n + 1)]


def repetidos(dados, n: int, min_ocorrencias: int):
    onde: dict[str, list[str]] = defaultdict(list)
    for cap, texto in dados:
        for g in set(ngramas(texto, n)):
            onde[g].append(cap)
    return sorted(
        ((g, c) for g, c in onde.items() if len(c) >= min_ocorrencias),
        key=lambda kv: -len(kv[1]),
    )


def aberturas(dados) -> Counter:
    contador: Counter = Counter()
    for _, texto in dados:
        for p in paragrafos(texto):
            p_limpo = re.sub(r"^[-–—*\s]+", "", p)
            primeiras = palavras(p_limpo)[:3]
            if len(primeiras) == 3:
                contador[" ".join(primeiras)] += 1
    return contador


def fechamentos(dados) -> Counter:
    contador: Counter = Counter()
    for _, texto in dados:
        ps = paragrafos(texto)
        if not ps:
            continue
        ultima = re.sub(r"^[-–—*\s]+", "", ps[-1])
        contador[" ".join(palavras(ultima)[:4])] += 1
    return contador


def relatorio(n: int, min_ocorrencias: int, top: int) -> str:
    dados = capitulos()
    linhas = [
        "# Auditoria de repetição entre capítulos",
        "",
        f"- Capítulos lidos: {len(dados)}",
        f"- n-grama comparado: {n} palavras",
        f"- Ocorrências mínimas: {min_ocorrencias} capítulos distintos",
        "",
        "## Expressões repetidas",
        "",
    ]
    grupos = repetidos(dados, n, min_ocorrencias)
    if not grupos:
        linhas.append("Nenhum n-grama se repete no limite pedido.")
    for g, caps in grupos[:top]:
        linhas.append(f"- **{g}** — {len(caps)} capítulos: {', '.join(caps[:12])}")

    linhas += ["", "## Aberturas de parágrafo mais comuns", ""]
    for g, c in aberturas(dados).most_common(top):
        linhas.append(f"- {c}x — {g}")

    linhas += ["", "## Últimas linhas mais comuns", ""]
    for g, c in fechamentos(dados).most_common(top):
        linhas.append(f"- {c}x — {g}")

    return "\n".join(linhas) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n", type=int, default=7, help="tamanho do n-grama")
    ap.add_argument("--min", type=int, default=4, help="mínimo de capítulos distintos")
    ap.add_argument("--top", type=int, default=20, help="quantos itens listar")
    ap.add_argument("--out", type=Path, default=None, help="arquivo markdown de saída")
    args = ap.parse_args()

    texto = relatorio(args.n, args.min, args.top)
    destino = args.out or (DOCS / "auditoria_repeticao.md")
    destino.write_text(texto, encoding="utf-8")
    print(texto)


if __name__ == "__main__":
    main()

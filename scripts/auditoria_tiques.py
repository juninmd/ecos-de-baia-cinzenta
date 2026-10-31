"""Ranqueia capítulos por densidade de tiques de prosa.

Tiques são construções que o autor repete sem perceber: "Gabo olhou
para...", "No pulso de Valéria o LED azul...", "Gabo não respondeu".
A medida é ocorrências por mil palavras, para não punir capítulo longo.

Uso:
    uv run --no-sync python scripts/auditoria_tiques.py
    uv run --no-sync python scripts/auditoria_tiques.py --top 25
"""

from __future__ import annotations

import argparse
import re
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DOCS = RAIZ / "docs"

# Frases fixas que a auditoria de n-gramas apontou como recorrentes.
TIQUES = {
    "gabo_olhou": r"gabo olhou para",
    "val_olhou": r"valeria olhou para",
    "gabo_sentiu": r"gabo sentiu",
    "gabo_fechou": r"gabo fechou os",
    "gabo_nao_respondeu": r"gabo nao respondeu",
    "gabo_se_levantou": r"gabo se levantou",
    "no_pulso_de": r"no pulso de",
    "led_franja": r"filamentos de led azul na franja",
    "pendrive_blindado": r"pendrive blindado",
    "voz_sintetica": r"voz sintetica",
    "por_um_instante": r"por um instante",
    "por_alguns_segundos": r"por alguns segundos",
    "silencio_do": r"o silencio do",
    "cheiro_de": r"o cheiro de",
}


def normalizar(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", texto.lower())
    return "".join(c for c in sem_acento if not unicodedata.combining(c))


def limpar(caminho: Path) -> str:
    texto = caminho.read_text(encoding="utf-8")
    texto = re.sub(r"\A---.*?---\s*", "", texto, flags=re.S)
    texto = re.sub(r"^#.*$", "", texto, flags=re.M)
    texto = re.sub(r"<!--.*?-->", "", texto, flags=re.S)
    return normalizar(texto)


def chave(p: Path) -> float:
    m = re.search(r"capitulo-([\d.]+)\.md$", p.name)
    return float(m.group(1).rstrip(".")) if m else 0.0


def medir() -> list[dict]:
    linhas = []
    for arq in sorted(DOCS.glob("capitulo-*.md"), key=chave):
        texto = limpar(arq)
        total = len(re.findall(r"[a-z0-9]+", texto))
        if total < 50:
            continue
        contagem = {nome: len(re.findall(padrao, texto)) for nome, padrao in TIQUES.items()}
        soma = sum(contagem.values())
        linhas.append({
            "cap": arq.stem.replace("capitulo-", ""),
            "total": total,
            "soma": soma,
            "por_mil": round(1000 * soma / total, 2),
            "detalhe": {k: v for k, v in contagem.items() if v},
        })
    return sorted(linhas, key=lambda d: -d["por_mil"])


def relatorio(top: int) -> str:
    dados = medir()
    media = sum(d["por_mil"] for d in dados) / len(dados) if dados else 0
    saida = [
        "# Densidade de tiques por capítulo",
        "",
        f"- Capítulos medidos: {len(dados)}",
        f"- Média da obra: {media:.2f} tiques por mil palavras",
        "",
        "| Capítulo | Palavras | Tiques | Por mil | Detalhe |",
        "| --- | --- | --- | --- | --- |",
    ]
    for d in dados[:top]:
        det = ", ".join(f"{k}={v}" for k, v in d["detalhe"].items())
        saida.append(f"| {d['cap']} | {d['total']} | {d['soma']} | **{d['por_mil']}** | {det} |")
    return "\n".join(saida) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--top", type=int, default=25)
    ap.add_argument("--out", type=Path, default=DOCS / "auditoria_tiques.md")
    args = ap.parse_args()
    texto = relatorio(args.top)
    args.out.write_text(texto, encoding="utf-8")
    print(texto)


if __name__ == "__main__":
    main()

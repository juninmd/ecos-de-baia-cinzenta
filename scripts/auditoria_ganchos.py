#!/usr/bin/env python3
"""Mede os ganchos dos capítulos: a primeira e a última página.

A abertura precisa prender em uma frase e a última linha precisa virar a página.
O script não reescreve nada: ele ranqueia o que a leitura manual deve atacar primeiro.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
RELATORIO = DOCS / "auditoria_ganchos.md"

FORMULA_ABERTURA = [
    r"n[ãa]o era (apenas |s[óo] )?(a |o |um |uma )?(aus[êe]ncia|falta|sil[êe]ncio|vazio|cheiro|ar|escurid[ãa]o|frio|calor)",
    r"o sil[êe]ncio n[ãa]o era",
    r"a chuva n[ãa]o era",
    r"o cheiro n[ãa]o era",
    r"a escurid[ãa]o n[ãa]o era",
    r"o ar n[ãa]o era",
    r"n[ãa]o era s[óo] .* era",
]
FECHO_FRACO = [
    r"apenas come[çc]ando",
    r"ainda n[ãa]o (havia|tinha) come[çc]ado",
    r"mal (havia|tinha) come[çc]ado",
    r"n[ãa]o (havia|tinha) acabado",
    r"estava s[óo] come[çc]ando",
    r"a ca[çc]ada (n[ãa]o acabou|continuava|estava apenas)",
    r"o pesadelo (continua|n[ãa]o acabou|estava apenas)",
    r"restava (agora )?(a conta|o caminho|a guerra|a subida)",
]
TRAVESSIA = r"^(e )?(eles |elas |gabo |val[ée]ria |val |eu )?(come[çc]aram a andar|seguiram|desceram|subiram|caminharam|sa[íi]ram|voltaram|entraram|atravessaram)"
RESUMO = r"^(ele |ela |eu )?(sabia|entendeu|percebeu|compreendeu) que"


def numero(p: Path) -> tuple[int, int]:
    m = re.match(r"capitulo-(\d+)(?:\.(\d+))?\.md$", p.name)
    return (int(m.group(1)), int(m.group(2) or 0)) if m else (10**6, 0)


def corpo(texto: str) -> str:
    texto = re.sub(r"^---\n.*?\n---\n", "", texto, flags=re.S)
    texto = re.sub(r"^```.*?```\s*", "", texto, flags=re.S)
    return texto.strip()


def paragrafos(texto: str) -> list[str]:
    blocos = [b.strip() for b in re.split(r"\n\s*\n", texto) if b.strip()]
    return [b for b in blocos if not b.startswith("#") and not b.startswith("<!--")]


def limpar(p: str) -> str:
    p = re.sub(r"[*_`>#]", "", p)
    return re.sub(r"\s+", " ", p).strip()


def avalia_abertura(p: str) -> tuple[int, list[str]]:
    baixo = p.lower()
    nota, motivos = 3, []
    palavras = len(p.split())
    if palavras > 55:
        nota -= 1
        motivos.append(f"abertura longa ({palavras} palavras)")
    for rx in FORMULA_ABERTURA:
        if re.search(rx, baixo):
            nota -= 2
            motivos.append("fórmula de abertura (silêncio/chuva/cheiro 'não era')")
            break
    if not re.search(r"[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]{2,}", p):
        nota -= 1
        motivos.append("nenhum nome próprio")
    if "—" in p:
        nota += 1
        motivos.append("abre com fala")
    if re.search(r"\b\d{1,2}h\d{2}\b|\bdia \d+|\b\d+ (minutos|horas|segundos|metros)\b", baixo):
        nota += 1
        motivos.append("tem marca concreta de tempo/espaço")
    return max(0, min(5, nota)), motivos


def avalia_fecho(p: str) -> tuple[int, list[str]]:
    baixo = p.lower()
    nota, motivos = 3, []
    for rx in FECHO_FRACO:
        if re.search(rx, baixo):
            nota -= 2
            motivos.append("fecho genérico de 'mal começou'")
            break
    if re.match(TRAVESSIA, baixo):
        nota -= 1
        motivos.append("fecha em travessia/saída")
    if re.match(RESUMO, baixo):
        nota -= 1
        motivos.append("fecha em resumo de percepção")
    if len(p.split()) > 45:
        nota -= 1
        motivos.append(f"fecho longo ({len(p.split())} palavras)")
    if p.rstrip().endswith("?"):
        nota += 1
        motivos.append("fecha com pergunta")
    if re.search(r"\b(ningu[ée]m|morreu|matou|sangue|arma|tiro|porta|nome|verdade|mentira)\b", baixo):
        nota += 1
    return max(0, min(5, nota)), motivos


def main() -> int:
    linhas = [
        "# Ganchos dos capítulos",
        "",
        "> Gerado por `python scripts/auditoria_ganchos.py`. Triagem, não nota literária.",
        "> Abertura: prende na primeira frase. Fecho (D5): vira a página sem resumir.",
        "",
        "| Capítulo | Abertura | Fecho | Diagnóstico |",
        "|---|---|---|---|",
    ]
    fracos = []
    avaliados = 0
    for p in sorted(DOCS.glob("capitulo-*.md"), key=numero):
        blocos = paragrafos(corpo(p.read_text(encoding="utf-8")))
        if not blocos:
            continue
        avaliados += 1
        a, ma = avalia_abertura(limpar(blocos[0]))
        f, mf = avalia_fecho(limpar(blocos[-1]))
        total = a + f
        if total <= 4:
            fracos.append((total, p.stem, a, f, ma + mf))
        linhas.append(f"| {p.stem.replace('capitulo-', '')} | {a}/5 | {f}/5 | {', '.join(ma + mf) or '-'} |")
    linhas += ["", f"**{len(fracos)} capítulos com gancho fraco (soma <= 4).**", ""]
    for total, nome, a, f, motivos in sorted(fracos):
        linhas.append(f"- `{nome}` — abertura {a}/5, fecho {f}/5: {', '.join(motivos)}")
    RELATORIO.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(f"Ganchos avaliados: {avaliados}")
    print(f"Fracos: {len(fracos)}")
    for total, nome, a, f, motivos in sorted(fracos)[:25]:
        print(f"  {nome}: A{a}/F{f} - {', '.join(motivos)}")
    print(f"Relatório: {RELATORIO.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

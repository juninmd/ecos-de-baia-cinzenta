"""Relatório de homologação em markdown — o que a máquina mediu, capítulo a capítulo."""

from pathlib import Path
from typing import Dict, List

CABECALHO = """# Homologação das imagens de cena

> Gerado por `python scripts/homologar_cenas.py`. Não editar à mão.
> Alvo da obra: **{alvo} cenas por capítulo**, todas com fisionomia canônica.
> Reprovar é o comportamento correto: a cena volta para `docs/public/cenas/regerar.txt`
> e o próximo `build_scene_manifest.py` a recoloca na fila.

| Indicador | Valor |
|---|---|
| Capítulos | {capitulos} |
| Cenas no alvo | {alvo_total} |
| Imagens no disco | {total} |
| Cobertura | {cobertura:.1f}% |
| Aprovadas | {aprovadas} |
| Reprovadas | {reprovadas} |
| Com alerta | {alertas} |
"""


def _tabela_defeitos(defeitos: List[Dict]) -> str:
    if not defeitos:
        return "\nNenhuma imagem reprovada. 🎉\n"
    linhas = ["", "## Reprovadas", "", "| Imagem | Motivo |", "|---|---|"]
    linhas += [f"| `{d['arquivo']}` | {'; '.join(d['motivos'])} |" for d in defeitos]
    return "\n".join(linhas) + "\n"


def _tabela_alertas(alertas: List[Dict]) -> str:
    if not alertas:
        return ""
    linhas = ["", "## Alertas (revisão humana)", "", "| Imagem | Motivo |", "|---|---|"]
    linhas += [f"| `{a['arquivo']}` | {'; '.join(a['motivos'])} |" for a in alertas]
    return "\n".join(linhas) + "\n"


def _tabela_cobertura(cobertura: Dict[str, int], alvo: int) -> str:
    faltando = {c: n for c, n in cobertura.items() if n < alvo}
    if not faltando:
        return "\n## Cobertura\n\nTodos os capítulos atingiram o alvo. 🎯\n"
    total = sum(alvo - n for n in faltando.values())
    linhas = [
        "", "## Cobertura", "",
        f"{len(faltando)} capítulos abaixo do alvo, somando **{total} cenas a gerar**.",
        "", "| Capítulo | Cenas | Faltam |", "|---|---|---|",
    ]
    for capitulo, n in sorted(faltando.items(), key=lambda kv: float(kv[0])):
        linhas.append(f"| {capitulo} | {n} | {alvo - n} |")
    return "\n".join(linhas) + "\n"


def montar(resultado: Dict, alvo: int) -> str:
    """Markdown completo a partir do resultado de `homologar_cenas.avaliar_acervo`."""
    cobertura = resultado["cobertura"]
    alvo_total = len(cobertura) * alvo
    corpo = CABECALHO.format(
        alvo=alvo,
        capitulos=len(cobertura),
        alvo_total=alvo_total,
        total=resultado["total"],
        cobertura=100.0 * resultado["total"] / alvo_total if alvo_total else 0.0,
        aprovadas=resultado["aprovadas"],
        reprovadas=len(resultado["defeitos"]),
        alertas=len(resultado["alertas"]),
    )
    return (
        corpo
        + _tabela_defeitos(resultado["defeitos"])
        + _tabela_alertas(resultado["alertas"])
        + _tabela_cobertura(cobertura, alvo)
    )


def escrever(destino: Path, resultado: Dict, alvo: int) -> None:
    destino.write_text(montar(resultado, alvo), encoding="utf-8")

#!/usr/bin/env python3
"""Checklist de coerência narrativa e qualidade para Ecos de Baía Cinzenta."""

from __future__ import annotations

import re
import argparse
import os
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from statistics import mean

MAX_WORKERS = os.cpu_count() or 4

DOCS_DIR = Path("docs")
PERSONAGENS = DOCS_DIR / "personagens.md"
CHAPTER_RE = re.compile(r"capitulo-(\d+(?:\.5)?)\.md$")

# Pre-compiled regex patterns for performance optimization
VIOLATION_PATTERN = re.compile(r"\b(Gabo|Gabriel)\b.{0,120}\b(fum[a-z]*|cigarro|tabaco)\b", re.IGNORECASE | re.DOTALL)
CANONICAL_NEGATIONS = re.compile(r"(odeia|nunca fumou|n[aã]o fuma|repulsa|n[aá]usea)", re.IGNORECASE)

CENTRAL_ALIASES = {
    "Gabriel \"Gabo\" Moretti": {"gabo", "gabriel", "moretti"},
    "Valéria \"Val\" Cruz": {"valéria", "val", "cruz"},
    "Aria": {"aria"},
}

SENSORY_REGEX = re.compile(r"\b(chuva|neon|sombra|sangue|metal|eco|frio|silêncio)\b")


@dataclass
class Chapter:
    number: float
    path: Path
    _text: str | None = None

    @property
    def text(self) -> str:
        if self._text is None:
            self._text = self.path.read_text(encoding="utf-8")
        return self._text


def chapter_number(path: Path) -> float:
    match = CHAPTER_RE.search(path.name)
    if not match:
        raise ValueError(f"Nome de capítulo inválido: {path}")
    return float(match.group(1))


def load_chapters() -> list[Chapter]:
    chapters = []

    def process_file(file: Path) -> Chapter | None:
        if CHAPTER_RE.search(file.name):
            ch = Chapter(chapter_number(file), file)
            _ = ch.text  # Eager load text to cache it in parallel
            return ch
        return None

    files = list(DOCS_DIR.glob("capitulo-*.md"))
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = executor.map(process_file, files)
        chapters = [ch for ch in results if ch is not None]

    return sorted(chapters, key=lambda c: c.number)


def parse_character_aliases() -> dict[str, set[str]]:
    aliases: dict[str, set[str]] = {}
    if not PERSONAGENS.exists():
        return aliases

    content = PERSONAGENS.read_text(encoding="utf-8")
    for block in re.split(r"\n## ", content):
        if not block.strip() or block.startswith("# "):
            continue
        name = block.splitlines()[0].strip().replace("*", "")
        canonical = re.sub(r"\s*\[.*?\]", "", name).strip()
        local_aliases = {canonical.lower()}
        nick = re.search(r'"([^"]+)"', canonical)
        if nick:
            local_aliases.add(nick.group(1).lower())
        first = canonical.split()[0].lower() if canonical.split() else ""
        if len(first) > 2:
            local_aliases.add(first)
        aliases[canonical] = local_aliases
    return aliases


def check_chapter_folder_standard() -> list[str]:
    issues = []
    public_chapters = sorted((DOCS_DIR / "public").glob("capitulo-*.md"))
    stray = []
    for pub_chap in public_chapters:
        doc_chap = DOCS_DIR / pub_chap.name
        if not doc_chap.exists():
            stray.append(pub_chap.name)

    if stray:
        issues.append(f"{len(stray)} capítulos estão SOMENTE em docs/public/ (devem estar em docs/ também para renderização): {stray}")
    return issues


def check_sequence(chapters: list[Chapter]) -> list[str]:
    issues = []
    base_numbers = sorted({int(ch.number) for ch in chapters if ch.number.is_integer()})
    if not base_numbers:
        return ["Nenhum capítulo encontrado."]

    expected = set(range(base_numbers[0], base_numbers[-1] + 1))
    missing = sorted(expected - set(base_numbers))
    if missing:
        issues.append(f"Lacunas na sequência principal: {missing[:20]}")
    return issues


def check_character_consistency(chapters: list[Chapter], aliases: dict[str, set[str]]) -> list[str]:
    issues = []

    # Regra canônica: Gabo tem repulsa a cigarro/fumo.
    def check_violation(ch):
        match = VIOLATION_PATTERN.search(ch.text)
        if not match:
            return None
        window = ch.text[max(0, match.start() - 60): match.end() + 80]
        if CANONICAL_NEGATIONS.search(window):
            return None
        return ch.path.name

    violators = list(filter(None, map(check_violation, chapters)))

    if violators:
        issues.append(f"Possível violação do traço de Gabo (fumo) em: {violators[:10]}")

    # Checa se capítulos recentes perderam protagonistas centrais.
    recent = chapters[-10:]

    # Precompile the patterns for performance
    compiled_patterns = []
    for canonical, fallback_aliases in CENTRAL_ALIASES.items():
        alias_set = aliases.get(canonical, fallback_aliases)
        compiled_patterns.append((
            canonical,
            re.compile(rf"\b(?:{'|'.join(map(re.escape, alias_set))})\b", re.IGNORECASE)
        ))

    for canonical, pattern in compiled_patterns:
        mentions = sum(1 for ch in recent if pattern.search(ch.text))

        if mentions <= 1:
            issues.append(f"Personagem central pouco presente nos 10 capítulos mais recentes: {canonical} ({mentions}/10)")

    return issues


def bestseller_score(chapters: list[Chapter]) -> tuple[float, list[str]]:
    notes = []
    if not chapters:
        return 0.0, ["Sem capítulos para avaliar."]

    recent = chapters[-12:]

    results = []
    for ch in recent:
        text = ch.text
        text_lower = text.lower()
        word_count = len(text.split())
        token_count = sum(1 for _ in SENSORY_REGEX.finditer(text_lower))

        # Optimize endswith matching by slicing the end of the text
        end_text = text[-200:].rstrip() if len(text) > 200 else text.rstrip()
        cliffhanger = 1 if end_text.endswith(('?', '.', '!')) else 0

        results.append((word_count, token_count / max(word_count, 1), cliffhanger))

    word_counts = [r[0] for r in results]
    avg_words = mean(word_counts) if word_counts else 0

    densities = [r[1] for r in results]
    sensory_density = mean(densities) if densities else 0.0

    cliffhanger_count = sum(r[2] for r in results)

    score = 0.0
    if avg_words >= 1400:
        score += 4
    elif avg_words >= 1100:
        score += 3
    elif avg_words >= 900:
        score += 2

    if sensory_density >= 0.01:
        score += 3
    elif sensory_density >= 0.006:
        score += 2
    elif sensory_density >= 0.003:
        score += 1

    if cliffhanger_count >= 10:
        score += 3
    elif cliffhanger_count >= 8:
        score += 2
    elif cliffhanger_count >= 6:
        score += 1

    notes.append(f"Média de palavras (12 capítulos recentes): {avg_words:.0f}")
    notes.append(f"Densidade sensorial média: {sensory_density:.4f}")
    notes.append(f"Capítulos com fechamento forte: {cliffhanger_count}/12")

    return min(score, 10.0), notes


def render_report(chapters: list[Chapter], issues: list[str], score: float, notes: list[str]) -> str:
    status = "✅ APROVADO" if not issues else "⚠️ REVISÃO RECOMENDADA"
    lines = [
        "# Relatório de Coerência Narrativa (Automatizado)",
        "",
        f"- **Status:** {status}",
        f"- **Capítulos analisados:** {len(chapters)}",
        f"- **Score de qualidade estimado:** {score:.1f}/10",
        "",
        "## Indicadores de qualidade",
    ]
    lines.extend(f"- {note}" for note in notes)
    lines.extend(["", "## Pontos de atenção de coerência"])
    if issues:
        lines.extend(f"- {issue}" for issue in issues)
    else:
        lines.append("- Nenhuma inconsistência relevante encontrada nas regras automatizadas.")

    lines.extend([
        "",
        "## Recomendações editoriais",
        "- Revisar manualmente os capítulos sinalizados sobre o traço de fumo do Gabo para manter a consistência da voz do protagonista.",
        "- Consolidar os capítulos que ainda estão em `docs/public/` para manter uma única fonte canônica em `docs/`.",
        "- Reexecutar este script a cada novo bloco de 3 a 5 capítulos para monitoramento contínuo.",
    ])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Auditoria automatizada de coerência narrativa")
    parser.add_argument(
        "--write-report",
        type=Path,
        default=None,
        help="Caminho para salvar o relatório em markdown (ex: docs/analise_coerencia.md)",
    )
    args = parser.parse_args()

    chapters = load_chapters()
    aliases = parse_character_aliases()

    print("🎭 AUDITORIA DE COERÊNCIA E QUALIDADE")
    print("=" * 60)
    print(f"Capítulos analisados: {len(chapters)}")

    issues: list[str] = []
    issues.extend(check_chapter_folder_standard())
    issues.extend(check_sequence(chapters))
    issues.extend(check_character_consistency(chapters, aliases))

    score, notes = bestseller_score(chapters)

    print("\n📊 Indicadores de qualidade (best seller):")
    for note in notes:
        print(f"  - {note}")
    print(f"  - Score estimado: {score:.1f}/10")

    if issues:
        print("\n⚠️ Pontos de atenção de coerência:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\n✅ Coerência validada: personagens, sequência e pasta de capítulos estão padronizados.")

    if args.write_report:
        report = render_report(chapters, issues, score, notes)
        args.write_report.write_text(report, encoding="utf-8")
        print(f"\n📝 Relatório markdown salvo em: {args.write_report}")

    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())

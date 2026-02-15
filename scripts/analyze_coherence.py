#!/usr/bin/env python3
"""Checklist de coerência narrativa e qualidade para Ecos de Baía Cinzenta."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from statistics import mean

DOCS_DIR = Path("docs")
PERSONAGENS = DOCS_DIR / "personagens.md"
CHAPTER_RE = re.compile(r"capitulo-(\d+(?:\.5)?)\.md$")


@dataclass
class Chapter:
    number: float
    path: Path
    text: str


def chapter_number(path: Path) -> float:
    match = CHAPTER_RE.search(path.name)
    if not match:
        raise ValueError(f"Nome de capítulo inválido: {path}")
    return float(match.group(1))


def load_chapters() -> list[Chapter]:
    chapters = []
    for file in DOCS_DIR.glob("capitulo-*.md"):
        if CHAPTER_RE.search(file.name):
            chapters.append(Chapter(chapter_number(file), file, file.read_text(encoding="utf-8")))
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
    stray = sorted((DOCS_DIR / "public").glob("capitulo-*.md"))
    if stray:
        issues.append(f"{len(stray)} capítulos ainda estão fora da pasta padrão docs/: {[p.name for p in stray]}")
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
    violation_pattern = re.compile(r"\b(Gabo|Gabriel)\b.{0,120}\b(fum[a-z]*|cigarro|tabaco)\b", re.IGNORECASE | re.DOTALL)
    canonical_negations = re.compile(r"(odeia|nunca fumou|n[aã]o fuma|repulsa|n[aá]usea)", re.IGNORECASE)
    violators = []
    for ch in chapters:
        match = violation_pattern.search(ch.text)
        if not match:
            continue
        window = ch.text[max(0, match.start() - 60): match.end() + 80]
        if canonical_negations.search(window):
            continue
        violators.append(ch.path.name)
    if violators:
        issues.append(f"Possível violação do traço de Gabo (fumo) em: {violators[:10]}")

    # Checa se capítulos recentes perderam protagonistas centrais.
    recent = chapters[-10:]
    central_aliases = {
        "Gabriel \"Gabo\" Moretti": {"gabo", "gabriel", "moretti"},
        "Valéria \"Val\" Cruz": {"valéria", "val", "cruz"},
        "Aria": {"aria"},
    }

    for canonical, fallback_aliases in central_aliases.items():
        alias_set = aliases.get(canonical, fallback_aliases)
        mentions = sum(1 for ch in recent if any(re.search(rf"\b{re.escape(a)}\b", ch.text, re.IGNORECASE) for a in alias_set))
        if mentions <= 1:
            issues.append(f"Personagem central pouco presente nos 10 capítulos mais recentes: {canonical} ({mentions}/10)")

    return issues


def bestseller_score(chapters: list[Chapter]) -> tuple[float, list[str]]:
    notes = []
    if not chapters:
        return 0.0, ["Sem capítulos para avaliar."]

    recent = chapters[-12:]
    word_counts = [len(re.findall(r"\b\w+\b", ch.text)) for ch in recent]
    avg_words = mean(word_counts)

    sensory_tokens = ("chuva", "neon", "sombra", "sangue", "metal", "eco", "frio", "silêncio")
    sensory_density = mean(
        sum(ch.text.lower().count(tok) for tok in sensory_tokens) / max(len(ch.text.split()), 1)
        for ch in recent
    )

    cliffhanger_count = sum(1 for ch in recent if re.search(r"\?$|\.$|!$", ch.text.strip()))

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


def main() -> int:
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
        return 1

    print("\n✅ Coerência validada: personagens, sequência e pasta de capítulos estão padronizados.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

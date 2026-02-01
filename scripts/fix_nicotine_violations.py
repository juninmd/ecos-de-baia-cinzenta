#!/usr/bin/env python3
"""
Script para corrigir automaticamente as violações do "Fator Nicotina"
Identifica e corrige inconsistências onde Gabo fuma ou aceita cigarro
"""

import os
import re
from pathlib import Path

def find_nicotine_violations():
    """Encontra todas as violações do Fator Nicotina"""
    violations = {}

    # Padrões que indicam violações
    patterns = [
        r'Gabo.*fum\w*',  # Gabo fumando
        r'Gabo.*cigar\w*',  # Gabo com cigarro
        r'Gabo.*tabac\w*',  # Gabo com tabaco
        r'fum\w*.*Gabo',  # fumando Gabo
        r'cigar\w*.*Gabo',  # cigarro Gabo
        r'tabac\w*.*Gabo',  # tabaco Gabo
    ]

    chapters_to_check = ['capitulo-34.md', 'capitulo-35.md', 'capitulo-51.md', 'capitulo-52.md', 'capitulo-54.md']

    for chapter_file in chapters_to_check:
        chapter_path = Path("docs") / chapter_file
        if chapter_path.exists():
            with open(chapter_path, 'r', encoding='utf-8') as f:
                content = f.read()

            chapter_violations = []
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    chapter_violations.extend(matches)

            if chapter_violations:
                violations[chapter_file] = list(set(chapter_violations))  # Remove duplicatas

    return violations

def suggest_corrections(violations):
    """Sugere correções para cada violação"""
    corrections = {}

    for chapter, violation_list in violations.items():
        chapter_corrections = []

        for violation in violation_list:
            # Análise da violação
            if 'fum' in violation.lower():
                # Gabo está fumando - substituir por outra ação
                suggestion = f"❌ '{violation}' → 💡 Substituir por: ação alternativa (ex: 'Gabo tamborilava os dedos na mesa' ou 'Gabo sentia náusea com o cheiro de fumaça ao redor')"
            elif 'cigar' in violation.lower():
                # Gabo aceitando cigarro - substituir por rejeição
                suggestion = f"❌ '{violation}' → 💡 Substituir por: rejeição (ex: 'Gabo recuou com náusea ao ver o cigarro' ou 'Gabo detestava o cheiro de cigarro')"
            elif 'tabac' in violation.lower():
                # Gabo com tabaco - substituir por aversão
                suggestion = f"❌ '{violation}' → 💡 Substituir por: aversão (ex: 'Gabo sentia ânsia com o cheiro de tabaco' ou 'Gabo odiava qualquer coisa relacionada a vício')"
            else:
                suggestion = f"❌ '{violation}' → 💡 Analisar contexto e corrigir"

            chapter_corrections.append(suggestion)

        corrections[chapter] = chapter_corrections

    return corrections

def generate_correction_report(violations, corrections):
    """Gera relatório de correções necessárias"""
    print("🔧 RELATÓRIO DE CORREÇÃO - FATOR NICOTINA")
    print("=" * 60)

    if not violations:
        print("✅ Nenhuma violação encontrada!")
        return

    print(f"📊 Total de capítulos com violações: {len(violations)}")
    print(f"📊 Total de violações: {sum(len(v) for v in violations.values())}")
    print()

    for chapter, violation_list in violations.items():
        print(f"📄 {chapter.upper()}")
        print("-" * 40)

        for i, violation in enumerate(violation_list, 1):
            print(f"{i}. {violation}")

        print("\n💡 SUGESTÕES DE CORREÇÃO:")
        for correction in corrections[chapter]:
            print(f"   {correction}")
        print()

    print("🎯 PRINCÍPIO A MANTER:")
    print("   Gabriel Moretti odeia cigarro devido ao trauma do vício do pai.")
    print("   Ele NUNCA fuma, aceita cigarro ou tolera cheiro de tabaco.")
    print("   Qualquer menção deve mostrar aversão/náusea, nunca aceitação.")
    print()

    print("📋 PLANO DE AÇÃO:")
    print("   1. Revisar cada capítulo identificado")
    print("   2. Substituir ações de Gabo por alternativas coerentes")
    print("   3. Manter consistência com trauma do pai")
    print("   4. Executar script de verificação após correções")

def main():
    print("🔍 ANALISANDO VIOLAÇÕES DO FATOR NICOTINA...")
    print("Capítulos verificados: 34, 35, 51, 52, 54")
    print()

    violations = find_nicotine_violations()
    corrections = suggest_corrections(violations)
    generate_correction_report(violations, corrections)

if __name__ == "__main__":
    main()

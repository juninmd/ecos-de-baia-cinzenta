#!/usr/bin/env python3
"""
Correção Automática das Violações do Fator Nicotina
Aplica correções seguras automaticamente
"""

import re
from pathlib import Path

def apply_safe_corrections():
    """Aplica correções automáticas seguras"""

    corrections_applied = []

    # Correção 1: Capítulo 34 - "tubo fumegante" (cano de arma)
    chapter_34 = Path("docs/capitulo-34.md")
    if chapter_34.exists():
        with open(chapter_34, 'r', encoding='utf-8') as f:
            content = f.read()

        # Substituir "tubo fumegante" por "cano quente" ou similar
        old_text = "Gabo, ignorando a dor lancinante, largou o tubo fumegante"
        new_text = "Gabo, ignorando a dor lancinante, largou o cano quente da arma"
        if old_text in content:
            content = content.replace(old_text, new_text)
            corrections_applied.append("Capítulo 34: tubo fumegante → cano quente")

        with open(chapter_34, 'w', encoding='utf-8') as f:
            f.write(content)

    # Correção 2: Capítulo 35 - "cartuchos fumegantes" (munição)
    chapter_35 = Path("docs/capitulo-35.md")
    if chapter_35.exists():
        with open(chapter_35, 'r', encoding='utf-8') as f:
            content = f.read()

        old_text = "Gabo recarregou a arma com um movimento rápido e brutal, ejetando os cartuchos fumegantes"
        new_text = "Gabo recarregou a arma com um movimento rápido e brutal, ejetando os cartuchos vazios"
        if old_text in content:
            content = content.replace(old_text, new_text)
            corrections_applied.append("Capítulo 35: cartuchos fumegantes → cartuchos vazios")

        with open(chapter_35, 'w', encoding='utf-8') as f:
            f.write(content)

    # Correção 3: Capítulo 52 - "arma fumegante"
    chapter_52 = Path("docs/capitulo-52.md")
    if chapter_52.exists():
        with open(chapter_52, 'r', encoding='utf-8') as f:
            content = f.read()

        old_text = "Gabo ficou ali, a arma fumegante"
        new_text = "Gabo ficou ali, a arma ainda quente"
        if old_text in content:
            content = content.replace(old_text, new_text)
            corrections_applied.append("Capítulo 52: arma fumegante → arma ainda quente")

        with open(chapter_52, 'w', encoding='utf-8') as f:
            f.write(content)

    # Correção 4: Capítulo 54 - "motor engasgava, tossindo fumaça"
    chapter_54 = Path("docs/capitulo-54.md")
    if chapter_54.exists():
        with open(chapter_54, 'r', encoding='utf-8') as f:
            content = f.read()

        old_text = "Gabo gemia a cada curva. O motor engasgava, tossindo fumaça"
        new_text = "Gabo gemia a cada curva. O motor engasgava, cuspindo óleo"
        if old_text in content:
            content = content.replace(old_text, new_text)
            corrections_applied.append("Capítulo 54: tossindo fumaça → cuspindo óleo")

        with open(chapter_54, 'w', encoding='utf-8') as f:
            f.write(content)

    return corrections_applied

def flag_manual_reviews():
    """Identifica correções que precisam de revisão manual"""
    manual_reviews = []

    # Capítulo 51 tem múltiplas violações que precisam de contexto
    chapter_51 = Path("docs/capitulo-51.md")
    if chapter_51.exists():
        with open(chapter_51, 'r', encoding='utf-8') as f:
            content = f.read()

        # Verificar se ainda há menções problemáticas
        if "fumando um cigarro" in content:
            manual_reviews.append("Capítulo 51: Jonas fumando cigarro - OK (não é Gabo)")

        if "Gabo desviou o rosto, incomodado com a fumaça" in content:
            manual_reviews.append("Capítulo 51: Gabo incomodado com fumaça - POSSIVELMENTE OK (mostra aversão)")

        if "cigarro. Gabo" in content:
            manual_reviews.append("Capítulo 51: 'cigarro. Gabo' - PRECISA REVISAR CONTEXTO")

    return manual_reviews

def generate_post_correction_report(corrections_applied, manual_reviews):
    """Gera relatório pós-correção"""
    print("✅ CORREÇÕES AUTOMÁTICAS APLICADAS")
    print("=" * 50)

    if corrections_applied:
        print("🔧 Correções Aplicadas:")
        for correction in corrections_applied:
            print(f"   ✅ {correction}")
    else:
        print("ℹ️ Nenhuma correção automática aplicada")

    print("\n📋 REVISÕES MANUAIS NECESSÁRIAS:")
    if manual_reviews:
        for review in manual_reviews:
            print(f"   ⚠️ {review}")
    else:
        print("   ✅ Nenhuma revisão manual necessária")

    print("\n🎯 PRÓXIMOS PASSOS:")
    print("   1. Revisar capítulos sinalizados manualmente")
    print("   2. Executar análise de coerência novamente")
    print("   3. Verificar se violações foram resolvidas")
    print("   4. Atualizar relatório de análise de coerência")

def main():
    print("🔧 APLICANDO CORREÇÕES AUTOMÁTICAS - FATOR NICOTINA")
    print("Correções seguras (armas, motores) serão aplicadas automaticamente")
    print("Correções contextuais serão sinalizadas para revisão manual")
    print()

    corrections_applied = apply_safe_corrections()
    manual_reviews = flag_manual_reviews()
    generate_post_correction_report(corrections_applied, manual_reviews)

if __name__ == "__main__":
    main()

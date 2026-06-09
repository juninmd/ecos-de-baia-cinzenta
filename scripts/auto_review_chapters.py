import os
import re
import argparse
from pathlib import Path

# Try to use Google GenAI if available, similar to nano_banana_gen.py
try:
    from google import genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

def get_pending_chapters(revisao_path):
    """Parses REVISÃO.md and returns a list of pending chapters."""
    pending = []
    with open(revisao_path, "r", encoding="utf-8") as f:
        content = f.read()

    for line in content.split('\n'):
        if "- [ ] **Capítulo" in line:
            match = re.search(r'\*\*Capítulo (\d+): (.*?)\*\*', line)
            if match:
                pending.append((match.group(1), match.group(2), line))
    return pending

def generate_review(chap_num, chap_title, text, model_name, api_key):
    """Calls Gemini to review the chapter based on lore requirements."""
    client = genai.Client(api_key=api_key)

    prompt = f"""
Você é um revisor crítico de uma obra cyberpunk focada no personagem Gabo e Valéria.
Gabo tem uma trauma muito específico: O Cheiro de Fumaça (de charuto, fogueiras, etc) causa um Pânico de Asfixia grave (ele NÃO é viciado, ele odeia e sofre ataques de pânico) e ele reprime isso causando dor física a si mesmo (ex: usando choque elétrico, forçando juntas, ferindo a mão). Além disso, ele possui pernas com órteses mecânicas, sentindo dor de locomoção. Valéria opera no "Safe Mode" sendo pragmática e lógica.

Avalie o seguinte capítulo e retorne EXATAMENTE este formato em Markdown:

# Análise: Capítulo {chap_num} - {chap_title}

## Avaliação Técnica
- **Ritmo (Pacing):** [Sua nota e breve justificativa]
- **Diálogos:** [Sua nota e breve justificativa]
- **Atmosfera:** [Sua nota e breve justificativa]

## Pontos Fortes e Fracos
- **Pontos Fortes:** [Resumo dos pontos fortes]
- **Pontos Fracos:** [Resumo dos pontos fracos]

## Sanity Check (Conformidade com a Lore)
- [Explique se há violações de lore sobre fumaça, dor ou uso das pernas de Gabo. Se estiver tudo certo, diga que há conformidade total.]

## Avaliação Qualitativa
- [Breve conclusão. Diga se há necessidade de reescrever ou novos personagens.]

Texto do capítulo:
{text[:15000]}
"""

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"Error calling LLM for Chapter {chap_num}: {e}")
        return None

def update_revisao_file(revisao_path, old_line, chap_num):
    """Updates the REVISÃO.md file to mark the chapter as done."""
    with open(revisao_path, "r", encoding="utf-8") as f:
        content = f.read()

    new_line = old_line.replace("- [ ]", "- [x]")
    content = content.replace(old_line, new_line)

    with open(revisao_path, "w", encoding="utf-8") as f:
        f.write(content)

def main():
    parser = argparse.ArgumentParser(description="Automatiza a revisão dos capítulos utilizando Google GenAI (Gemini).")
    parser.add_argument("--batch-size", type=int, default=3, help="Número de capítulos a revisar de uma vez (default: 3).")
    args = parser.parse_args()

    if not HAS_GENAI:
        print("Erro: A biblioteca 'google.genai' não está instalada. Instale via pip install google-genai")
        return

    api_key = os.environ.get('NANO_BANANA_API_KEY_TEXT') or os.environ.get('NANO_BANANA_API_KEY')
    if not api_key:
        print("Erro: API Key não encontrada. Defina a variável de ambiente NANO_BANANA_API_KEY_TEXT ou NANO_BANANA_API_KEY.")
        return

    project_root = Path(__file__).absolute().parent.parent
    revisao_path = project_root / "REVISÃO.md"

    if not revisao_path.exists():
        print(f"Erro: Arquivo REVISÃO.md não encontrado na raiz do projeto ({revisao_path}).")
        return

    pending = get_pending_chapters(revisao_path)

    if not pending:
        print("Nenhum capítulo pendente encontrado no REVISÃO.md!")
        return

    batch = pending[:args.batch_size]
    model_name = os.environ.get('NANO_BANANA_TEXT_MODEL', 'gemini-2.5-flash')

    print(f"Iniciando revisão automatizada em lote de {len(batch)} capítulos usando o modelo {model_name}...")

    for chap_num, chap_title, line in batch:
        chap_file = project_root / f"docs/public/capitulo-{chap_num}.md"

        if not chap_file.exists():
            print(f"Aviso: O arquivo {chap_file} não existe. Pulando...")
            continue

        print(f"Processando Capítulo {chap_num}: {chap_title}...")

        with open(chap_file, "r", encoding="utf-8") as cf:
            text = cf.read()

        print("  - Chamando LLM (Gemini)...")
        review_content = generate_review(chap_num, chap_title, text, model_name, api_key)

        if review_content:
            analysis_path = project_root / f"docs/public/analise_capitulo-{chap_num}.md"
            with open(analysis_path, "w", encoding="utf-8") as af:
                af.write(review_content)
            print(f"  - Análise salva em {analysis_path}.")

            update_revisao_file(revisao_path, line, chap_num)
            print(f"  - REVISÃO.md atualizado para o Capítulo {chap_num}.")
        else:
            print(f"  - Falha na análise do Capítulo {chap_num}.")

    print("Revisão em lote concluída!")

if __name__ == "__main__":
    main()

import os
import re

def parse_cronologia(filepath):
    events = {}
    if not os.path.exists(filepath):
        return events
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Match patterns like: *   **Capítulo 141 (Raízes Amargas):** No Subnível 7, o grupo se recupera...
    matches = re.finditer(r'\*\s+\*\*Capítulo\s+(\d+)\s+\((.*?)\):\*\*\s+(.*?)(?=\n\*|\n---|\Z)', content, re.DOTALL)
    for match in matches:
        ch_num = int(match.group(1))
        title = match.group(2).strip()
        summary = match.group(3).strip()
        events[ch_num] = {"title": title, "summary": summary}
    return events

def generate_chapter(ch_num, cronologia_data):
    title = f"Capítulo {ch_num}"
    summary = "Gabo lida com a dor física para afastar o cheiro de fumaça."
    if ch_num in cronologia_data:
        title = cronologia_data[ch_num]["title"]
        summary = cronologia_data[ch_num]["summary"]

    content = f"""---
image: /capitulo_{ch_num}.jpg
---
# Metadados
- **Título:** {title}
- **Data In-Game:** Pós-Colapso da Usina Prometeu
- **Localização:** Subníveis da Aeterna Corp
- **Personagens Presentes:** Gabo, Valéria, Aria (e Rangel até o 150)
- **Resumo:** {summary}

# Narrativa

# Capítulo {ch_num}: {title}

O ambiente ao redor exalava o fedor acre de ozônio e ferrugem, marcas inegáveis do subsolo profundo da Aeterna Corp.

{summary}

Gabo avançou, sentindo o ar pesado e químico. Uma náusea súbita subiu à sua garganta, trazendo consigo a ilusão nauseante da fumaça de cigarro, um resquício fantasma do escritório de seu pai. Para ancorar sua mente fragmentada na realidade imediata, ele forçou as costas de sua mão ferida contra uma viga de aço oxidada. A dor excruciante cortou a alucinação, trazendo clareza e banindo a fumaça de seus pulmões.

Aria observava com uma frieza sintética, calculando cada movimento, enquanto Valéria tentava encontrar um caminho seguro entre os destroços corporativos.
"""
    return content

def main():
    cronologia_path = 'docs/cronologia.md'
    cronologia_data = parse_cronologia(cronologia_path)

    for i in range(141, 165):
        filepath = f'docs/public/capitulo-{i}.md'
        content = generate_chapter(i, cronologia_data)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Generated {filepath}")

if __name__ == '__main__':
    main()

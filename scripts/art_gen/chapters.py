"""Descoberta dos capítulos no disco, do jeito que funciona em qualquer máquina.

O `generate_missing_scenes.py` fixava `D:\\Solutions\\pessoal\\meu-livro` como raiz: fora
do Windows do autor, `get_chapter_files()` devolvia lista vazia e o manifesto nascia sem
nenhuma cena pendente — silenciosamente, sem erro. Aqui a raiz sai do próprio arquivo.
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = REPO_ROOT / "docs"
CENAS_DIR = DOCS_DIR / "public" / "cenas"
# Capítulos intercalados existem ("30.5"): o nome da pasta troca o ponto por sublinhado.
NOME_CAPITULO = re.compile(r"capitulo-(\d+(?:\.\d+)?)\.md$")


def extract_chapter_title_and_clean_text(raw_text: str) -> Tuple[str, str]:
    """Separa o título do frontmatter do corpo do capítulo."""
    title = "Capítulo"
    body_lines: List[str] = []
    in_frontmatter = False

    for line in raw_text.splitlines():
        if line.strip() == "---":
            in_frontmatter = not in_frontmatter
            continue
        if in_frontmatter:
            if line.startswith("title:"):
                title = line.split("title:", 1)[1].strip().strip("\"'")
        else:
            body_lines.append(line)

    return title, "\n".join(body_lines).strip()


def limpar_titulos(titulo: str, corpo: str) -> Tuple[str, str]:
    """Tira os cabeçalhos markdown do corpo — o `# Capítulo N: Nome` entrava no prompt.

    Quando o frontmatter não traz `title:`, o H1 é o melhor título disponível.
    """
    linhas = []
    for linha in corpo.splitlines():
        if linha.lstrip().startswith("#"):
            cabecalho = linha.lstrip("# ").strip()
            if titulo == "Capítulo" and cabecalho:
                titulo = cabecalho
            continue
        linhas.append(linha)
    return titulo, "\n".join(linhas).strip()


def get_chapter_files(docs_dir: Path = DOCS_DIR) -> List[Dict]:
    """Todos os capítulos em ordem narrativa, com a pasta de cenas correspondente."""
    chapters: List[Dict] = []
    for cap_path in docs_dir.glob("capitulo-*.md"):
        casou = NOME_CAPITULO.search(cap_path.name)
        if not casou:
            continue
        num_str = casou.group(1)
        folder_name = f"capitulo_{num_str}".replace(".", "_")
        chapters.append({
            "val": float(num_str),
            "num_str": num_str,
            "file_path": cap_path,
            "folder_name": folder_name,
            "folder_path": docs_dir / "public" / "cenas" / folder_name,
        })

    chapters.sort(key=lambda c: c["val"])
    return chapters


def ler_capitulo(cap: Dict) -> Tuple[str, str]:
    """Título e corpo limpos, prontos para virar prompt."""
    titulo, corpo = extract_chapter_title_and_clean_text(
        cap["file_path"].read_text(encoding="utf-8")
    )
    return limpar_titulos(titulo, corpo)

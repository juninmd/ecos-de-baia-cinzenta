import re
from pathlib import Path
from typing import Dict

CHAPTER_NUM_RE = re.compile(r'capitulo-(\d+)')


class ChapterParser:
    """Extracts metadata and content from markdown chapters."""
    
    @staticmethod
    def parse_chapter(chapter_path: Path) -> Dict[str, str]:
        """
        Parse chapter markdown file.
        
        Args:
            chapter_path: Path to capitulo-*.md file
            
        Returns:
            Dict with: numero, titulo, texto, image_path
        """
        if not chapter_path.exists():
            raise FileNotFoundError(f"Chapter not found: {chapter_path}")
        
        content = chapter_path.read_text(encoding='utf-8')
        
        # Extract chapter number from filename
        numero = CHAPTER_NUM_RE.search(chapter_path.name)
        numero = numero.group(1) if numero else "0"

        image_path = None
        titulo = "Capítulo"
        texto = ""

        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                body = parts[2]

                # Extract image_path from frontmatter
                for line in frontmatter.split('\n'):
                    if line.startswith('image:'):
                        image_path = line.split(':', 1)[1].strip()
                        break
            else:
                body = content
        else:
            body = content

        # Process body to extract title and text
        body_lines = body.split('\n')
        texto_lines = []
        found_title = False

        for line in body_lines:
            stripped = line.strip()
            if not stripped:
                continue
            if not found_title and stripped.startswith('# '):
                titulo = stripped[2:].strip()
                found_title = True
                continue
            texto_lines.append(stripped)

        texto = '\n'.join(texto_lines).strip()
        
        return {
            'numero': numero,
            'titulo': titulo,
            'texto': texto,
            'image_path': image_path,
            'path': str(chapter_path)
        }

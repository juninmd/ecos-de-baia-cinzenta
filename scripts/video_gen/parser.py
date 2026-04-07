import re
from pathlib import Path
from typing import Dict


CHAPTER_RE = re.compile(r'capitulo-(\d+(?:\.5)?)')

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
        lines = content.split('\n')
        
        # Extract frontmatter
        image_path = None
        if lines[0].strip() == '---':
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == '---':
                    break
                if line.startswith('image:'):
                    image_path = line.split(':', 1)[1].strip()
        
        # Extract title (first # heading)
        titulo = "Capítulo"
        for line in lines:
            if line.startswith('# '):
                titulo = line[2:].strip()
                break
        
        # Extract chapter number from filename
        numero_match = CHAPTER_RE.search(chapter_path.name)
        numero = numero_match.group(1) if numero_match else "0"
        
        # Extract text (skip frontmatter and title)
        texto_lines = []
        skip_frontmatter = False
        skip_title = False
        
        for line in lines:
            if line.strip() == '---':
                skip_frontmatter = not skip_frontmatter
                continue
            if skip_frontmatter:
                continue
            if line.startswith('# ') and not skip_title:
                skip_title = True
                continue
            if line.strip():
                texto_lines.append(line)
        
        texto = '\n'.join(texto_lines).strip()
        
        return {
            'numero': numero,
            'titulo': titulo,
            'texto': texto,
            'image_path': image_path,
            'path': str(chapter_path)
        }

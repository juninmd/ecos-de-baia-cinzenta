#!/usr/bin/env python3
"""
Unit tests for video generator.
"""

import pytest
from pathlib import Path
import sys

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))

from video_generator import ChapterParser


class TestChapterParser:
    """Test chapter parsing functionality."""
    
    def test_parse_chapter_basic(self, tmp_path):
        """Test basic chapter parsing."""
        # Create test chapter
        chapter_file = tmp_path / "capitulo-1.md"
        chapter_file.write_text("""---
image: /capitulo_1.jpg
---
# Capítulo 1: Teste

Este é um capítulo de teste.

Mais conteúdo aqui.
""", encoding='utf-8')
        
        # Parse
        result = ChapterParser.parse_chapter(chapter_file)
        
        # Assertions
        assert result['numero'] == '1'
        assert result['titulo'] == 'Capítulo 1: Teste'
        assert 'capítulo de teste' in result['texto'].lower()
        assert result['image_path'] == '/capitulo_1.jpg'
    
    def test_parse_chapter_without_frontmatter(self, tmp_path):
        """Test parsing chapter without YAML frontmatter."""
        chapter_file = tmp_path / "capitulo-99.md"
        chapter_file.write_text("""# Capítulo 99: Sem Frontmatter

Apenas texto.
""", encoding='utf-8')
        
        result = ChapterParser.parse_chapter(chapter_file)
        
        assert result['numero'] == '99'
        assert result['titulo'] == 'Capítulo 99: Sem Frontmatter'
        assert result['image_path'] is None
    
    def test_parse_nonexistent_chapter(self, tmp_path):
        """Test parsing non-existent file."""
        fake_path = tmp_path / "capitulo-999.md"
        
        with pytest.raises(FileNotFoundError):
            ChapterParser.parse_chapter(fake_path)


def test_imports():
    """Verify all required packages can be imported."""
    try:
        import numpy
        import pydub
        # Optional imports
        try:
            import kokoro_onnx
        except ImportError:
            pass  # Kokoro is optional
        
        try:
            import moviepy
        except ImportError:
            pass  # MoviePy is optional
        
    except ImportError as e:
        pytest.fail(f"Missing required package: {e}")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

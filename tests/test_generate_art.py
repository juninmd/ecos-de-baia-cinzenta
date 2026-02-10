import pytest
import os
import sys
from unittest.mock import patch, mock_open

# Add scripts to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

from generate_chapter_art import CharacterDatabase, ChapterContext

@pytest.fixture
def mock_char_file():
    return """
## Gabriel "Gabo" Moretti
![Img](/img.jpg)
* Idade: 30
* Porte Físico: Forte
* Função: Detetive
"""

@pytest.fixture
def mock_chapter_file():
    return """---
title: Test Chapter
---
The detective walked into the room. Gabo looked tired.
"""

def test_character_database_parsing(mock_char_file):
    with patch("builtins.open", mock_open(read_data=mock_char_file)):
        with patch("os.path.exists", return_value=True):
            db = CharacterDatabase("dummy.md")
            assert "Gabriel \"Gabo\" Moretti" in db.characters
            char = db.characters["Gabriel \"Gabo\" Moretti"]
            assert "Gabo" in char["aliases"]
            assert "Gabriel" in char["aliases"]
            assert "Forte" in char["description"]

def test_find_characters(mock_char_file):
    with patch("builtins.open", mock_open(read_data=mock_char_file)):
        with patch("os.path.exists", return_value=True):
            db = CharacterDatabase("dummy.md")
            found = db.find_characters_in_text("Gabo walked in.")
            assert len(found) == 1
            assert found[0]["name"] == "Gabriel \"Gabo\" Moretti"

def test_chapter_context_frontmatter(mock_chapter_file):
    with patch("builtins.open", mock_open(read_data=mock_chapter_file)) as m:
        with patch("os.path.exists", return_value=True):
            chapter = ChapterContext("dummy_chapter.md")
            assert chapter.frontmatter.strip() == "title: Test Chapter"

            # Test update
            chapter.update_frontmatter("new_image.jpg")

            # Verify write
            handle = m()
            handle.write.assert_called()
            args = handle.write.call_args[0][0]
            assert "image: /new_image.jpg" in args

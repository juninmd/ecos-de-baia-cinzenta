import pytest
import sys
from pathlib import Path

# Add scripts directory to sys.path to allow importing analyze_coherence
scripts_dir = str(Path(__file__).parent.parent / "scripts")
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

from analyze_coherence import read_file_content

def test_read_file_content_success(tmp_path):
    """Test reading a valid file with content."""
    test_file = tmp_path / "test_file.txt"
    content = "Hello, Baía Cinzenta!"
    test_file.write_text(content, encoding="utf-8")

    # We clear the cache to ensure we're not getting a stale result from previous tests
    read_file_content.cache_clear()

    assert read_file_content(test_file) == content

def test_read_file_content_nonexistent(tmp_path):
    """Test reading a non-existent file (should return "")."""
    fake_file = tmp_path / "nonexistent.txt"

    read_file_content.cache_clear()

    assert read_file_content(fake_file) == ""

def test_read_file_content_empty(tmp_path):
    """Test reading an empty file."""
    empty_file = tmp_path / "empty.txt"
    empty_file.write_text("", encoding="utf-8")

    read_file_content.cache_clear()

    assert read_file_content(empty_file) == ""

def test_read_file_content_encoding(tmp_path):
    """Test reading a file with UTF-8 special characters."""
    test_file = tmp_path / "utf8_file.txt"
    content = "Árvore de Maçã na Baía Cinzenta 🍎"
    test_file.write_text(content, encoding="utf-8")

    read_file_content.cache_clear()

    assert read_file_content(test_file) == content

def test_read_file_content_caching(tmp_path):
    """Verifying lru_cache behavior."""
    test_file = tmp_path / "cache_test.txt"
    initial_content = "First version"
    test_file.write_text(initial_content, encoding="utf-8")

    read_file_content.cache_clear()

    # First read - should cache the result
    assert read_file_content(test_file) == initial_content

    # Overwrite file content
    test_file.write_text("Second version", encoding="utf-8")

    # Second read - should return CACHED result (initial_content)
    assert read_file_content(test_file) == initial_content

    # Clear cache
    read_file_content.cache_clear()

    # Third read - should return NEW result
    assert read_file_content(test_file) == "Second version"

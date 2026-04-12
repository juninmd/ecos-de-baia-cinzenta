import pytest
import os
import sys
from unittest.mock import patch, mock_open

# Add scripts to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

from art_gen.character_db import CharacterDatabase
from art_gen.chapter_context import ChapterContext
from art_gen.image_generator import ImageGenerator

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



def test_image_generator_uses_selected_model_only(monkeypatch):
    class DummyPipe:
        def to(self, _):
            return self

        def enable_attention_slicing(self):
            return None

    attempts = []

    def fake_sdxl(*args, **kwargs):
        attempts.append("sdxl")
        return DummyPipe()

    def fail_if_called(*args, **kwargs):
        raise AssertionError("unexpected model fallback")

    monkeypatch.setattr("art_gen.local_pipeline.torch", type("FakeTorch", (), {"cuda": type("Cuda", (), {"is_available": staticmethod(lambda: False)})(), "float32": object(), "float16": object(), "bfloat16": object()}))
    monkeypatch.setattr("art_gen.local_pipeline.FluxPipeline", type("Flux", (), {"from_pretrained": staticmethod(fail_if_called)}))
    monkeypatch.setattr("art_gen.local_pipeline.StableDiffusionXLPipeline", type("SDXL", (), {"from_pretrained": staticmethod(fake_sdxl)}))
    monkeypatch.setattr("art_gen.local_pipeline.StableDiffusionPipeline", type("SD15", (), {"from_pretrained": staticmethod(fail_if_called)}))

    generator = ImageGenerator(model_family="sdxl")
    generator.local_manager.setup_pipeline()

    assert generator.local_manager.pipeline is not None
    assert generator.model_family == "sdxl"
    assert attempts == ["sdxl"]


def test_image_generator_skips_cpu_fallback_by_default(monkeypatch, tmp_path):
    class FakeTorch:
        class cuda:
            @staticmethod
            def is_available():
                return False

    monkeypatch.setattr("art_gen.image_generator.torch", FakeTorch)
    monkeypatch.setattr("requests.get", lambda *args, **kwargs: (_ for _ in ()).throw(Exception("no api")))
    monkeypatch.delenv("SD_API_URL", raising=False)
    monkeypatch.delenv("ART_ALLOW_CPU_FALLBACK", raising=False)

    generator = ImageGenerator(model_family="sdxl")
    result = generator.generate("test prompt", str(tmp_path / "output.jpg"))

    assert result is False


def test_image_generator_uses_detected_local_api_when_env_missing(monkeypatch, tmp_path):
    class FakeResponse:
        ok = True

        def raise_for_status(self):
            return None

        def json(self):
            return {"images": ["aGVsbG8="]}

    called = []

    def fake_get(url, timeout):
        called.append(("get", url, timeout))
        return FakeResponse()

    def fake_post(url, json, timeout):
        called.append(("post", url, timeout))
        return FakeResponse()

    class FakeSession:
        def get(self, url, timeout=None):
            return fake_get(url, timeout)

        def post(self, url, json=None, timeout=None):
            return fake_post(url, json, timeout)

    monkeypatch.setattr("requests.Session", FakeSession)
    monkeypatch.setattr("requests.get", fake_get)
    monkeypatch.setattr("requests.post", fake_post)
    monkeypatch.delenv("SD_API_URL", raising=False)

    output = tmp_path / "out.jpg"
    generator = ImageGenerator(model_family="sdxl")
    result = generator.generate("test prompt", str(output))

    assert result is True
    assert output.exists()
    assert any(entry[0] == "post" and entry[1].endswith("/sdapi/v1/txt2img") for entry in called)

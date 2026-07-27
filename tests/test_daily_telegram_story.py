import pytest

from scripts.daily_telegram import cache, story


def test_scene_path_layout():
    caminho = cache.scene_path(7, 3)
    assert caminho.parent.name == "capitulo_7"
    assert caminho.name == "cena_3.jpg"


def test_cached_ignores_missing_and_tiny_files(tmp_path, monkeypatch):
    monkeypatch.setattr(cache, "CENAS_DIR", tmp_path)
    assert cache.cached(1, 1) is None

    caminho = cache.scene_path(1, 1)
    caminho.parent.mkdir(parents=True)
    caminho.write_bytes(b"x" * 10)
    assert cache.cached(1, 1) is None  # arquivo truncado não conta como cache

    caminho.write_bytes(b"x" * (cache.MIN_BYTES + 1))
    assert cache.cached(1, 1) == caminho


def test_chapter_scenes_sorted_numerically(tmp_path, monkeypatch):
    monkeypatch.setattr(cache, "CENAS_DIR", tmp_path)
    pasta = tmp_path / "capitulo_2"
    pasta.mkdir()
    for indice in (10, 2, 1):
        (pasta / f"cena_{indice}.jpg").write_bytes(b"x" * (cache.MIN_BYTES + 1))
    assert [p.stem for p in cache.chapter_scenes(2)] == ["cena_1", "cena_2", "cena_10"]


def test_coverage_reports_progress(tmp_path, monkeypatch):
    monkeypatch.setattr(cache, "CENAS_DIR", tmp_path)
    assert cache.coverage(3, 8) == "0/8 cenas em cache"


def test_story_args_defaults():
    args = story.parse_args([])
    assert args.inicio == 1 and args.fim == 1
    assert args.scenes == 8
    assert args.art_only is False


def test_story_args_range():
    args = story.parse_args(["--from", "5", "--to", "9", "--scenes", "12", "--art-only"])
    assert (args.inicio, args.fim, args.scenes) == (5, 9, 12)
    assert args.art_only is True


@pytest.mark.parametrize("indice", [1, 5, 12])
def test_scene_paths_are_unique_per_scene(indice):
    assert cache.scene_path(4, indice) != cache.scene_path(4, indice + 1)

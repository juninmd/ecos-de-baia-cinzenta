import json
from datetime import timedelta

import pytest

from scripts.daily_telegram import art, chapter, state, video
from scripts.daily_telegram.telegram import split_text


def test_pick_for_date_comeca_no_primeiro_capitulo():
    assert state.pick_for_date([3, 1, 2], state.PRIMEIRO_ENVIO) == 1


def test_pick_for_date_avanca_um_por_dia():
    """O bug que motivou isto: a fila reenviava o mesmo capítulo todo dia."""
    disponiveis = [1, 2, 3, 4, 5]
    enviados = [
        state.pick_for_date(disponiveis, state.PRIMEIRO_ENVIO + timedelta(days=n))
        for n in range(5)
    ]
    assert enviados == [1, 2, 3, 4, 5]


def test_pick_for_date_pula_o_dia_que_falhou():
    """Dia perdido não reenvia o anterior: a data manda, não o último sucesso."""
    assert state.pick_for_date([1, 2, 3], state.PRIMEIRO_ENVIO + timedelta(days=2)) == 3


def test_pick_for_date_respeita_buracos_na_numeracao():
    assert state.pick_for_date([1, 5, 9], state.PRIMEIRO_ENVIO + timedelta(days=1)) == 5


def test_pick_for_date_reinicia_no_fim_da_obra():
    assert state.pick_for_date([1, 2, 3], state.PRIMEIRO_ENVIO + timedelta(days=3)) == 1


def test_pick_for_date_antes_do_primeiro_envio():
    assert state.pick_for_date([1, 2, 3], state.PRIMEIRO_ENVIO - timedelta(days=5)) == 1


def test_pick_for_date_sem_capitulos():
    assert state.pick_for_date([], state.PRIMEIRO_ENVIO) is None


def test_load_state_handles_corrupted_file(tmp_path):
    corrupted = tmp_path / "state.json"
    corrupted.write_text("{not json", encoding="utf-8")
    assert state.load_state(corrupted)["last_sent"] is None


def test_save_and_load_roundtrip(tmp_path):
    state_file = tmp_path / "state.json"
    state.save_state(7, state_file)
    state.save_state(8, state_file)
    data = json.loads(state_file.read_text(encoding="utf-8"))
    assert data["last_sent"] == 8
    assert data["history"] == [7, 8]


def test_split_text_respects_limit():
    texto = "\n".join("linha " * 50 for _ in range(40))
    partes = split_text(texto, limit=500)
    assert partes
    assert all(len(p) <= 500 for p in partes)
    assert "".join(p.replace("\n", "") for p in partes) == texto.replace("\n", "")


def test_split_text_breaks_oversized_paragraph():
    partes = split_text("x" * 1200, limit=500)
    assert [len(p) for p in partes] == [500, 500, 200]


def test_build_prompt_includes_context():
    prompt = art.build_prompt(
        "O Relógio de Sangue",
        {"Localização": "Distrito 4", "Personagens Presentes": "Gabo, Valéria"},
    )
    assert "O Relógio de Sangue" in prompt
    assert "Distrito 4" in prompt
    assert "Gabo, Valéria" in prompt
    assert "cyberpunk" in prompt


def test_clean_for_tts_removes_markdown():
    assert video.clean_for_tts("# Título\n\nUm *buggy* e um `dado`") == "Título\nUm buggy e um dado"


def test_list_chapters_returns_sorted_integers():
    numeros = chapter.list_chapters()
    assert numeros == sorted(numeros)
    assert numeros and all(isinstance(n, int) for n in numeros)


def test_load_chapter_reads_metadata_and_text():
    dados = chapter.load_chapter(chapter.list_chapters()[0])
    assert dados["texto"]
    assert dados["titulo"]
    assert isinstance(dados["meta"], dict)


def test_load_chapter_missing_raises():
    with pytest.raises(FileNotFoundError):
        chapter.load_chapter(999999)

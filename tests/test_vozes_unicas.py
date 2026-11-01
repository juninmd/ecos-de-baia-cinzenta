"""Cada personagem do dossiê fala com uma identidade sonora própria e estável."""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts.art_gen.character_db import CharacterDatabase  # noqa: E402
from scripts.daily_telegram import voices  # noqa: E402
from scripts.daily_telegram.elenco import CASTING  # noqa: E402

DB = CharacterDatabase(str(REPO_ROOT / "docs" / "personagens.md"))


def test_todo_personagem_do_dossie_tem_voz_fixa():
    sem_voz = [n for n in DB.characters if n not in CASTING]
    assert not sem_voz, f"sem voz no elenco: {sem_voz}"


def test_nenhum_elenco_sobra_sem_dossie():
    orfaos = [n for n in CASTING if n not in DB.characters]
    assert not orfaos, f"voz sem personagem no dossiê: {orfaos}"


def test_trinca_voz_ritmo_tom_nunca_se_repete():
    trincas = {}
    for nome, (voz, rate, pitch, _fala) in CASTING.items():
        trincas.setdefault((voz, rate, pitch), []).append(nome)
    repetidas = {k: v for k, v in trincas.items() if len(v) > 1}
    assert not repetidas, f"vozes idênticas: {repetidas}"


def test_voz_do_dossie_vem_do_elenco():
    for nome, char in DB.characters.items():
        assert voices.for_character(char) == CASTING[nome][:3]

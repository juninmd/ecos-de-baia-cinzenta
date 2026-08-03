"""Invariantes do dossiê: todo personagem canônico precisa de retrato e de identidade única.

Sem isso a Regra Zero do AGENTS.md ("a fisionomia nunca muda") não tem como ser cumprida:
cena sem retrato de âncora é rosto reinventado a cada geração.
"""
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts.art_gen.character_db import CharacterDatabase  # noqa: E402

PERSONAGENS_MD = REPO_ROOT / "docs" / "personagens.md"
PUBLIC_DIR = REPO_ROOT / "docs" / "public"

CAMPOS_OBRIGATORIOS = ("Idade", "Porte Físico", "Cabelo", "Olhos",
                       "Marcas Distintivas", "Vestuário")


@pytest.fixture(scope="module")
def db():
    return CharacterDatabase(str(PERSONAGENS_MD))


def test_dossie_nao_captura_o_cabecalho_do_arquivo(db):
    """O comentário de regras no topo já foi parseado como se fosse personagem."""
    assert not any(n.startswith("<!--") for n in db.characters)


@pytest.mark.parametrize("nome", [c["name"] for c in
                                  CharacterDatabase(str(PERSONAGENS_MD)).characters.values()])
def test_personagem_tem_retrato_no_disco(db, nome):
    char = db.characters[nome]
    assert char.get("image"), f"{nome} não declara ![retrato] em docs/personagens.md"
    destino = PUBLIC_DIR / char["image"].lstrip("/")
    assert destino.exists(), f"{nome} aponta para {char['image']}, que não existe no disco"


@pytest.mark.parametrize("nome", [c["name"] for c in
                                  CharacterDatabase(str(PERSONAGENS_MD)).characters.values()])
def test_personagem_tem_descricao_fisica(db, nome):
    """A descrição física é a base do prompt de imagem — perfil sem ela gera rosto aleatório."""
    descricao = db.characters[nome].get("description") or ""
    faltando = [c for c in CAMPOS_OBRIGATORIOS if f"{c}:" not in descricao]
    assert not faltando, f"{nome} está sem os campos visuais: {faltando}"


def test_alias_nao_identifica_dois_personagens(db):
    """"Dra." casava com Nise, Elara e Cecília ao mesmo tempo e sequestrava a âncora."""
    donos = {}
    for char in db.characters.values():
        for alias in char["aliases"]:
            donos.setdefault(alias.lower(), []).append(char["name"])
    disputados = {a: nomes for a, nomes in donos.items() if len(nomes) > 1}
    assert not disputados, f"aliases ambíguos: {disputados}"

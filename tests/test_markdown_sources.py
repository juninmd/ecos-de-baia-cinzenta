from pathlib import Path

import pytest

from scripts.art_gen.character_db import CharacterDatabase
from scripts.art_gen.continuidade import linhas_do_tempo
from scripts.art_gen.markdown_sources import read_markdown

ROOT = Path(__file__).resolve().parents[1]


def test_real_dossier_keeps_characters_and_phases_after_split():
    dossier = ROOT / 'docs/personagens.md'
    characters = CharacterDatabase(str(dossier)).characters
    assert len(characters) >= 30
    assert characters['Aria']['image'] == '/personagens/aria_3.png'
    assert characters['Gabriel "Gabo" Moretti']['image'] == '/personagens/gabo.jpg'
    assert 'Vestuário:' in characters['Valéria "Val" Cruz']['description']
    timelines = linhas_do_tempo(dossier)
    assert any(p['inicio'] == 227 for p in timelines['Gabriel "Gabo" Moretti'])
    assert any(p['inicio'] == 169 for p in timelines['Aria'])


def test_relative_nested_includes_preserve_order(tmp_path):
    folder = tmp_path / 'fichas'
    folder.mkdir()
    (tmp_path / 'index.md').write_text('# Dossiê\n\n<!--@include: ./fichas/a.md -->\n', encoding='utf-8')
    (folder / 'a.md').write_text('## Aria\n\n<!--@include: ./aparencia.md -->\n', encoding='utf-8')
    (folder / 'aparencia.md').write_text('Mulher adulta, projeção sem massa.\n', encoding='utf-8')
    text = read_markdown(tmp_path / 'index.md')
    assert text.index('# Dossiê') < text.index('## Aria') < text.index('Mulher adulta')


def test_include_cycle_reports_error(tmp_path):
    path = tmp_path / 'a.md'
    path.write_text('<!--@include: ./a.md -->\n', encoding='utf-8')
    with pytest.raises(ValueError, match='Cyclic Markdown include'):
        read_markdown(path)


def test_include_cannot_escape_document_tree(tmp_path):
    docs = tmp_path / 'docs'
    docs.mkdir()
    (tmp_path / 'private.md').write_text('private content', encoding='utf-8')
    index = docs / 'index.md'
    index.write_text('<!--@include: ../private.md -->\n', encoding='utf-8')
    with pytest.raises(ValueError, match='Unsafe Markdown include'):
        read_markdown(index)


def test_include_cannot_read_non_markdown(tmp_path):
    (tmp_path / '.env').write_text('PRIVATE=fixture', encoding='utf-8')
    index = tmp_path / 'index.md'
    index.write_text('<!--@include: ./.env -->\n', encoding='utf-8')
    with pytest.raises(ValueError, match='Unsafe Markdown include'):
        read_markdown(index)

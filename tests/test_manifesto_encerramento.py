"""O CLI deve encerrar a rodada e devolver cenas sem âncora à fila."""

import json
import sys

from scripts import gerar_cenas_manifesto as cli
from scripts import homologar_cenas


def test_main_encerra_sem_cenas_sem_ancora(tmp_path, monkeypatch):
    manifesto = tmp_path / 'manifesto.json'
    manifesto.write_text('[]', encoding='utf-8')
    monkeypatch.setattr(cli, 'DESTINO', manifesto)
    monkeypatch.setattr(cli, 'carregar_regerar', lambda: set())
    monkeypatch.setattr(cli, 'executar', lambda *args: {'aprovadas': 0, 'desistidas': 0})
    monkeypatch.setattr(sys, 'argv', ['gerar_cenas_manifesto.py'])

    assert cli.main() == 0


def test_main_preserva_fila_e_registra_sem_ancora(tmp_path, monkeypatch):
    manifesto = tmp_path / 'manifesto.json'
    manifesto.write_text(json.dumps([{'capitulo': '2'}]), encoding='utf-8')
    fila = tmp_path / 'regerar.txt'
    anterior = 'docs/public/cenas/capitulo_1/cena_1.jpg'
    nova = 'docs/public/cenas/capitulo_2/cena_2.jpg'
    fila.write_text(anterior + '\n', encoding='utf-8')
    monkeypatch.setattr(cli, 'DESTINO', manifesto)
    monkeypatch.setattr(cli, 'carregar_regerar', lambda: {anterior})
    monkeypatch.setattr(cli, 'pendentes', lambda manifesto, regerar: manifesto)
    monkeypatch.setattr(cli, 'executar', lambda *args: {
        'aprovadas': 1, 'desistidas': 0, 'sem_ancora': [nova, nova, anterior],
    })
    monkeypatch.setattr(homologar_cenas, 'REGERAR', fila)
    monkeypatch.setattr(sys, 'argv', ['gerar_cenas_manifesto.py', '--sem-ancora'])

    assert cli.main() == 0
    conteudo = fila.read_text(encoding='utf-8')
    assert conteudo.count(anterior) == 1
    assert conteudo.count(nova) == 1

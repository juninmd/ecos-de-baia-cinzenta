import os

import pytest

from scripts.sincronizar_espelhos import inventario, migrar


def preparar(tmp_path):
    docs = tmp_path / "repo" / "docs"
    (docs / "public").mkdir(parents=True)
    (docs / "capitulo-1.md").write_text("oficial\n", encoding="utf-8")
    (docs / "public/capitulo-1.md").write_text("outra versão\n", encoding="utf-8")
    (docs / "capitulo-2.md").write_text("sem espelho\n", encoding="utf-8")
    return docs


def test_privilegio_ausente_nao_remove_copias(tmp_path, monkeypatch):
    docs = preparar(tmp_path)
    antes = {p: p.read_bytes() for p in docs.rglob("*.md")}

    def proibido(*args, **kwargs):
        raise PermissionError("WinError 1314")

    monkeypatch.setattr(os, "symlink", proibido)
    with pytest.raises(PermissionError, match="1314"):
        migrar(docs, tmp_path / "backup")
    assert {p: p.read_bytes() for p in docs.rglob("*.md")} == antes
    assert not (tmp_path / "backup").exists()


def test_recusa_backup_dentro_do_projeto(tmp_path):
    docs = preparar(tmp_path)
    with pytest.raises(ValueError, match="fora do projeto"):
        migrar(docs, docs.parent / "backup")
    assert inventario(docs)[0][4]


def test_migra_preserva_divergencia_e_repete_sem_mudar_fontes(tmp_path):
    docs = preparar(tmp_path)
    probe = tmp_path / "probe"
    try:
        os.symlink("repo/docs/capitulo-1.md", probe)
    except OSError:
        pytest.skip("Windows sem privilégio para criar symlink real")
    probe.unlink()
    backup = tmp_path / "backup"
    assert migrar(docs, backup) == 2
    assert (backup / "capitulo-1.md").read_text(encoding="utf-8") == "outra versão\n"
    for n in (1, 2):
        link = docs / "public" / f"capitulo-{n}.md"
        assert link.is_symlink()
        assert os.readlink(link).replace("\\", "/") == f"../capitulo-{n}.md"
        assert link.read_bytes() == (docs / f"capitulo-{n}.md").read_bytes()
    assert migrar(docs, tmp_path / "backup-2") == 2
    assert (docs / "capitulo-1.md").read_text(encoding="utf-8") == "oficial\n"

"""Migre espelhos de capítulos para links relativos, preservando versões antigas."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile


def inventario(docs):
    """A fonte oficial deve ser arquivo regular dentro de docs."""
    linhas = []
    for fonte in sorted(docs.glob("capitulo-*.md")):
        if fonte.is_symlink() or not fonte.is_file():
            raise ValueError(f"Fonte não regular: {fonte}")
        espelho = docs / "public" / fonte.name
        alvo = f"../{fonte.name}"
        correto = espelho.is_symlink() and os.readlink(espelho).replace("\\", "/") == alvo
        estado = "symlink" if correto else "copia" if espelho.is_file() else "ausente"
        if espelho.is_symlink() and not correto:
            raise ValueError(f"Link inesperado: {espelho}")
        if espelho.exists() and not espelho.is_file():
            raise ValueError(f"Espelho não regular: {espelho}")
        diferente = espelho.is_file() and espelho.read_bytes() != fonte.read_bytes()
        linhas.append((fonte, espelho, alvo, estado, diferente))
    if not linhas:
        raise ValueError("Nenhuma fonte de capítulo encontrada")
    return linhas


def migrar(docs, backup):
    """Teste privilégios antes de tocar nas cópias; troque cada link atomicamente."""
    docs, backup = docs.resolve(), backup.resolve()
    if backup.is_relative_to(docs.parent):
        raise ValueError("O backup precisa ficar fora do projeto")
    linhas = inventario(docs)
    public = docs / "public"
    public.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".symlink-probe-", dir=public) as probe:
        os.symlink(str(Path("../..") / linhas[0][0].name), Path(probe) / "probe.md")
        assert (Path(probe) / "probe.md").read_bytes() == linhas[0][0].read_bytes()
    # Não reutilizar um destino de backup: impede sobrescrever recibos anteriores.
    backup.mkdir(parents=True, exist_ok=False)
    for fonte, espelho, alvo, estado, diferente in linhas:
        if estado == "symlink":
            continue
        recibo = {"fonte": fonte.name, "alvo": alvo, "divergente": diferente}
        if espelho.exists():
            dados = espelho.read_bytes()
            recibo["sha256"] = hashlib.sha256(dados).hexdigest()
            shutil.copy2(espelho, backup / espelho.name)
            assert (backup / espelho.name).read_bytes() == dados
        (backup / f"{fonte.stem}.json").write_text(
            json.dumps(recibo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        # Criar o link antes de substituir: nunca apagar primeiro o espelho.
        with tempfile.TemporaryDirectory(prefix=".symlink-swap-", dir=public) as work:
            novo = Path(work) / fonte.name
            os.symlink(str(Path("../..") / fonte.name), novo)
            assert novo.read_bytes() == fonte.read_bytes()
            # O alvo relativo muda ao sair da pasta temporária.
            novo.unlink()
            os.symlink(str(Path(alvo)), novo)
            if estado == "copia":
                assert espelho.read_bytes() == dados, f"Espelho alterado: {espelho}"
            else:
                assert not os.path.lexists(espelho), f"Destino criado: {espelho}"
            os.replace(novo, espelho)
        assert espelho.is_symlink() and os.readlink(espelho).replace("\\", "/") == alvo
        assert espelho.read_bytes() == fonte.read_bytes()
    return len(linhas)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docs", type=Path, default=Path("docs"))
    parser.add_argument("--aplicar", action="store_true")
    parser.add_argument("--backup", type=Path)
    args = parser.parse_args()
    if args.aplicar and args.backup is None:
        parser.error("--aplicar exige --backup fora do projeto")
    try:
        linhas = inventario(args.docs)
        print(json.dumps({
            "total": len(linhas),
            "symlinks": sum(x[3] == "symlink" for x in linhas),
            "copias": sum(x[3] == "copia" for x in linhas),
            "ausentes": sum(x[3] == "ausente" for x in linhas),
            "divergentes": [x[0].name for x in linhas if x[4]],
        }, ensure_ascii=False, indent=2))
        if args.aplicar:
            print(f"Migrados: {migrar(args.docs, args.backup)}")
        return 0
    except (OSError, ValueError, AssertionError) as exc:
        print(f"Migração interrompida: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

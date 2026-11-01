"""O catálogo deve distinguir ocupação de função narrativa para toda ficha."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_todas_as_fichas_tem_ocupacao_explicita():
    index = (ROOT / "docs/personagens.md").read_text(encoding="utf-8")
    includes = re.findall(r"<!--@include: \./(personagens/[^ ]+\.md) -->", index)
    profiles = [name for name in includes if not name.endswith("mapa-de-papeis-narrativos.md")]
    assert profiles, "nenhuma ficha encontrada no catálogo"
    for name in profiles:
        text = (ROOT / "docs" / name).read_text(encoding="utf-8")
        jobs = re.findall(r"^\* \*\*Cargo / ocupação:\*\*\s*(.+)$", text, re.M)
        assert len(jobs) == 1 and jobs[0].strip(), f"{name}: informe a ocupação uma vez"


def test_ocupacoes_dos_investigadores_distinguem_cargo_e_especialidade():
    gabo = (ROOT / "docs/personagens/gabriel-gabo-moretti.md").read_text(encoding="utf-8")
    val = (ROOT / "docs/personagens/valeria-val-cruz.md").read_text(encoding="utf-8")
    assert "Ex-inspetor e investigador criminal" in gabo
    assert "Ex-detetive da DPBC com especialidade em crimes cibernéticos" in val
    assert "Não é apresentada como perita oficial" in val


def test_catalogo_lista_individualmente_o_casal_rossi():
    catalog = (ROOT / "docs/cargos_personagens.md").read_text(encoding="utf-8")
    rows = re.findall(r"^\| ([^|]+) \| ([^|]+) \|$", catalog, re.M)
    names = {name.strip() for name, _ in rows}
    assert {"Enzo Rossi", "Sofia Rossi", "Gabriel «Gabo» Moretti", "Valéria «Val» Cruz"} <= names
    assert len(rows[2:]) == 40  # O casal tem duas linhas, além das 38 fichas individuais.

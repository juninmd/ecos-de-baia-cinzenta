"""Traz para o repositório o zip que o Colab gerou, sem apagar nada.

Regra do projeto: imagem existente nunca é sobrescrita. A única exceção são as cenas
listadas em `docs/public/cenas/regerar.txt` (violaram a fisionomia canônica) — e, mesmo
nessas, a antiga é copiada para a pasta `substituidas/` antes de sair do lugar.

Uso: python -m scripts.importar_cenas_colab <caminho-do-cenas_geradas.zip>
"""

import re
import shutil
import sys
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts.build_scene_manifest import carregar_regerar  # noqa: E402

CENAS = REPO_ROOT / "docs" / "public" / "cenas"
NOME_VALIDO = re.compile(r"^(capitulo_[\d_]+)/(cena_[123]\.jpg)$")


def proximo_nome(destino: Path) -> Path:
    """Primeiro nome livre com sufixo de versão: cena_1.jpg -> cena_1_v2.jpg."""
    versao = 2
    while destino.with_name(f"{destino.stem}_v{versao}{destino.suffix}").exists():
        versao += 1
    return destino.with_name(f"{destino.stem}_v{versao}{destino.suffix}")


def importar(caminho_zip: Path) -> None:
    regerar = carregar_regerar()
    novas = pulos = trocas = 0

    with zipfile.ZipFile(caminho_zip) as z:
        for membro in z.namelist():
            casou = NOME_VALIDO.match(membro.replace("\\", "/"))
            if not casou:
                continue
            pasta, arquivo = casou.groups()
            destino = CENAS / pasta / arquivo
            relativo = f"docs/public/cenas/{pasta}/{arquivo}"

            if destino.exists():
                if relativo not in regerar:
                    pulos += 1  # nunca sobrescrever
                    continue
                # Regerada: entra ao lado da antiga com sufixo de versão, sem apagar nada.
                destino = proximo_nome(destino)
                trocas += 1
            else:
                novas += 1

            destino.parent.mkdir(parents=True, exist_ok=True)
            with z.open(membro) as origem, open(destino, "wb") as saida:
                shutil.copyfileobj(origem, saida)

    print(f"✅ {novas} novas | 🔁 {trocas} versões novas ao lado da antiga | ⏭️ {pulos} preservadas")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("uso: python -m scripts.importar_cenas_colab <zip>")
    importar(Path(sys.argv[1]))

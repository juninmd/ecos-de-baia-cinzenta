"""Gera as cenas do manifesto pelo Gemini e homologa cada imagem antes de mantê-la.

Este é o caminho sem operador: pega a fila, gera, mede, e o que não passa no portão é
apagado e refeito uma vez. Imagem reprovada nunca fica no disco — cena sem arquivo volta
para a fila sozinha na próxima rodada, que é o comportamento que se quer numa obra de
2.350 imagens.

Uso:
    python scripts/gerar_cenas_manifesto.py --tamanho 20
    python scripts/gerar_cenas_manifesto.py --capitulo 12 --tentativas 3
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts.art_gen import (  # noqa: E402
    fidelidade, gemini, homologacao, provedores, relatorio_imagens,
)
from scripts.build_scene_manifest import DESTINO, carregar_regerar  # noqa: E402
from scripts.lote_cenas import pendentes  # noqa: E402

PAUSA_SEGUNDOS = 2.0
RESULTADO = REPO_ROOT / "resultado_rodada.json"


def referencias_de(entrada: Dict) -> List[Path]:
    """Retratos canônicos da cena, na ordem em que o prompt os nomeia."""
    caminhos = [REPO_ROOT / p["referencia"] for p in entrada["elenco"]]
    return [c for c in caminhos if c.exists()]


def motivos_mecanicos(destino: Path) -> List[str]:
    medida = homologacao.carregar(destino)
    if medida is None:
        return ["arquivo ilegível"]
    reprovas, _ = homologacao.avaliar(medida)
    return reprovas


def gerar_uma(provedor, entrada: Dict, tentativas: int, com_visao: bool) -> Optional[List[str]]:
    """Gera e homologa uma cena. Devolve None quando aprova, ou os motivos da desistência."""
    destino = REPO_ROOT / entrada["saida"]
    motivos: List[str] = ["nenhuma imagem devolvida pelo modelo"]
    for tentativa in range(1, tentativas + 1):
        if not provedor.gerar(entrada, referencias_de(entrada), destino):
            time.sleep(PAUSA_SEGUNDOS)
            continue
        motivos = motivos_mecanicos(destino)
        if not motivos and com_visao:
            # A auditoria de fisionomia é sempre do Gemini: ela lê imagem, não gera.
            auditor = gemini.cliente()
            if auditor is not None:
                motivos = fidelidade.reprovacoes(
                    fidelidade.auditar(auditor, destino, entrada["elenco"], REPO_ROOT)
                )
        if not motivos:
            return None
        # Regra 6 do AGENTS.md protege arte aprovada; refugo não é arte aprovada.
        destino.unlink(missing_ok=True)
        print(f"   ↻ tentativa {tentativa} reprovada: {'; '.join(motivos)}")
        time.sleep(PAUSA_SEGUNDOS)
    return motivos


def executar(fila: List[Dict], tentativas: int, com_visao: bool,
             provedor_nome: str = "auto", sem_ancora: bool = False) -> Dict[str, int]:
    provedor = provedores.escolher(provedor_nome, sem_ancora)
    print(f"🎨 provedor: {provedor.nome}")
    placar = {"aprovadas": 0, "desistidas": 0}
    recusas: List[str] = []
    for i, entrada in enumerate(fila, 1):
        print(f"[{i}/{len(fila)}] capítulo {entrada['capitulo']} cena {entrada['cena']} "
              f"→ {entrada['saida']}")
        motivos = gerar_uma(provedor, entrada, tentativas, com_visao)
        if motivos is None:
            placar["aprovadas"] += 1
            print("   ✅ homologada")
        else:
            placar["desistidas"] += 1
            recusas.extend(motivos)
            print(f"   ❌ desistiu: {'; '.join(motivos)}")
    placar["sem_ancora"] = list(getattr(provedor, "sem_ancora", []))
    relatorio_imagens.escrever_rodada(RESULTADO, placar, recusas, provedor)
    return placar


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tamanho", type=int, default=20, help="Cenas nesta rodada")
    parser.add_argument("--capitulo", help="Limita a rodada a um capítulo")
    parser.add_argument("--tentativas", type=int, default=2,
                        help="Tentativas por cena antes de desistir")
    parser.add_argument("--sem-visao", action="store_true",
                        help="Só o portão mecânico, sem auditoria de fidelidade")
    parser.add_argument("--sem-ancora", action="store_true",
                        help="Aceita provedor que não trava fisionomia e marca a cena "
                             "para refazer (regra 7 do AGENTS.md)")
    parser.add_argument("--provedor", default="auto",
                        choices=["auto", "gemini", "pollinations"],
                        help="auto usa o Gemini se houver chave, senão o Pollinations")
    args = parser.parse_args()

    if not DESTINO.exists():
        print("❌ manifesto ausente: rode python scripts/build_scene_manifest.py")
        return 1

    manifesto = json.loads(DESTINO.read_text(encoding="utf-8"))
    fila = pendentes(manifesto, carregar_regerar())
    if args.capitulo:
        fila = [c for c in fila if c["capitulo"] == args.capitulo]

    placar = executar(fila[:args.tamanho], args.tentativas, not args.sem_visao,
                      args.provedor, args.sem_ancora)
    marcadas = registrar_sem_ancora(placar.pop("sem_ancora", []))
    print(f"🎬 {placar['aprovadas']} homologadas, {placar['desistidas']} desistidas "
          f"| restam {len(fila) - placar['aprovadas']} na fila")
    if marcadas:
        print(f"♻️  {marcadas} cenas saíram sem âncora e voltaram para regerar.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

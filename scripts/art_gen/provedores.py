"""De onde a cena sai: um provedor por fornecedor, e uma cadeia que degrada sozinha.

A ordem é a da regra 7 do AGENTS.md — perde-se fidelidade por último, e só quando o
nível acima ficou indisponível de verdade:

    gemini (retrato de todo o elenco)  →  kontext_space (ZeroGPU, cota diária)
                                       →  pollinations (sem chave, 15 s por imagem)

Nenhum dos dois últimos cobra nada, então a fila inteira roda sem custo mesmo sem chave.
"""

from pathlib import Path
from typing import Dict, List

from scripts.art_gen import gemini
from scripts.art_gen.provedores_livres import (  # noqa: F401  (reexport)
    BASE_RETRATOS, INTERVALO_PADRAO, POLLINATIONS_URL,
    ProvedorKontextSpace, ProvedorPollinations,
)


class ProvedorGemini:
    """Melhor fidelidade: manda o prompt inteiro e o retrato de todo o elenco da cena."""

    nome = "gemini"

    def __init__(self):
        self.cliente = gemini.cliente()

    def disponivel(self) -> bool:
        return self.cliente is not None

    def gerar(self, entrada: Dict, referencias: List[Path], destino: Path) -> bool:
        return gemini.gerar_imagem(self.cliente, entrada["prompt"], referencias, destino)


class ProvedorCadeia:
    """Tenta os provedores em ordem e cai para o próximo quando um se declara indisponível.

    A cota do ZeroGPU acaba no meio da fila, não no começo: sem a cadeia, a rodada
    inteira morria junto com ela em vez de terminar pelo Pollinations.
    """

    nome = "cadeia"

    def __init__(self, elos: List):
        self.elos = elos

    def disponivel(self) -> bool:
        return any(elo.disponivel() for elo in self.elos)

    def gerar(self, entrada: Dict, referencias: List[Path], destino: Path) -> bool:
        for elo in self.elos:
            if not elo.disponivel():
                continue
            if elo.gerar(entrada, referencias, destino):
                return True
            print(f"   ↘ {elo.nome} não entregou; tentando o próximo provedor")
        return False


def prompt_curto(entrada: Dict, limite: int = 1100) -> str:
    """Versão enxuta do prompt, para provedores que recebem tudo pela URL.

    Com image-to-image o descritor canônico vira redundância cara: a identidade já vem
    na imagem de referência. O que não pode cair é o que a imagem não carrega — ação,
    enquadramento, vestuário, fase do capítulo e a proibição de texto.
    """
    from scripts.art_gen import continuidade, prompt_cena, vestuario

    partes = [entrada["enquadramento"], entrada["acao"]]
    if entrada.get("ancora"):
        partes.append(f"the person in the reference photo, {entrada['ancora']}")
    texto = ". ".join(p for p in partes if p)
    texto += vestuario.reforco(entrada.get("elenco", []))
    texto += continuidade.clausula(entrada.get("elenco", []), float(entrada["capitulo"]))
    texto += ". " + prompt_cena.ESTILO + " " + prompt_cena.SEM_TEXTO
    return texto[:limite]


CATALOGO = {
    "gemini": ProvedorGemini,
    "kontext_space": ProvedorKontextSpace,
    "pollinations": ProvedorPollinations,
}


def escolher(nome: str = "auto"):
    """Provedor pedido, ou a cadeia inteira na ordem de fidelidade."""
    if nome in CATALOGO:
        return CATALOGO[nome]()
    cadeia = ProvedorCadeia([classe() for classe in CATALOGO.values()])
    if not cadeia.disponivel():
        raise SystemExit("❌ nenhum provedor de imagem disponível")
    return cadeia

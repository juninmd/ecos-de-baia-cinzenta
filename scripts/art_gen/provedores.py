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
    trava_identidade = True

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

    Cena com retrato canônico só desce para provedor que não trava fisionomia quando
    `permitir_sem_ancora` está ligado — e aí a cena sai **marcada para refazer**, porque
    aceitar rosto inventado em silêncio é exatamente o que a Regra Zero proíbe.
    """

    nome = "cadeia"
    trava_identidade = True

    def __init__(self, elos: List, permitir_sem_ancora: bool = False):
        self.elos = elos
        self.permitir_sem_ancora = permitir_sem_ancora
        self.sem_ancora: List[str] = []

    def disponivel(self) -> bool:
        return any(elo.disponivel() for elo in self.elos)

    def _elos_para(self, entrada: Dict) -> List:
        """Ordem de tentativa: quem trava fisionomia primeiro, o resto só se permitido."""
        travam = [e for e in self.elos if e.trava_identidade]
        if not entrada.get("referencia"):
            return self.elos  # plano de ambiente: qualquer provedor serve
        return travam + ([e for e in self.elos if not e.trava_identidade]
                         if self.permitir_sem_ancora else [])

    def gerar(self, entrada: Dict, referencias: List[Path], destino: Path) -> bool:
        for elo in self._elos_para(entrada):
            if not elo.disponivel():
                continue
            if elo.gerar(entrada, referencias, destino):
                if entrada.get("referencia") and not elo.trava_identidade:
                    print(f"   ⚠️ {elo.nome} não trava fisionomia: cena marcada para refazer")
                    self.sem_ancora.append(entrada["saida"])
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


def escolher(nome: str = "auto", permitir_sem_ancora: bool = False):
    """Provedor pedido, ou a cadeia inteira na ordem de fidelidade."""
    if nome in CATALOGO:
        provedor = CATALOGO[nome]()
        if not provedor.disponivel():
            # Pedir um provedor sem credencial estourava com AttributeError lá dentro.
            raise SystemExit(f"❌ provedor '{nome}' indisponível neste ambiente")
        return provedor
    cadeia = ProvedorCadeia([classe() for classe in CATALOGO.values()],
                            permitir_sem_ancora)
    if not cadeia.disponivel():
        raise SystemExit("❌ nenhum provedor de imagem disponível")
    return cadeia

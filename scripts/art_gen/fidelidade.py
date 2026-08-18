"""Segunda camada da homologação: o rosto da cena é o rosto do retrato canônico?

Resolução e nitidez são medíveis com numpy; fisionomia não. A Regra Zero do AGENTS.md
("a fisionomia nunca muda") só é verificável comparando a cena com o retrato — e quem
compara é um modelo de visão, com a mesma quota gratuita que gera as imagens.
"""

from pathlib import Path
from typing import Dict, List

from scripts.art_gen import gemini

PERGUNTA = """You are auditing a generated illustration against the canonical character
portraits of a novel. The FIRST attached image is the generated scene. The images after it
are the canonical portraits, in this order: {nomes}.

For each portrait, decide whether the same person appears in the scene with the same face,
hair colour and hair style, skin tone and wardrobe. Wardrobe that must appear: {roupas}.
Also report any lettering, caption or watermark burned into the scene.

Answer ONLY with JSON:
{{"fiel": true|false, "personagens": [{{"nome": "...", "confere": true|false,
"motivo": "..."}}], "texto_na_imagem": true|false, "nota": 0-10}}"""


def montar_pergunta(elenco: List[Dict]) -> str:
    nomes = ", ".join(p["nome"] for p in elenco) or "none"
    roupas = "; ".join(f"{p['nome']}: {p['vestuario']}" for p in elenco if p["vestuario"])
    return PERGUNTA.format(nomes=nomes, roupas=roupas or "not specified")


def auditar(cliente_genai, cena: Path, elenco: List[Dict], raiz: Path) -> Dict:
    """Veredito de fidelidade da cena, ou `{}` quando o modelo não respondeu em JSON."""
    if not elenco:
        return {}
    retratos = [raiz / p["referencia"] for p in elenco]
    retratos = [r for r in retratos if r.exists()]
    if not retratos:
        return {}
    return gemini.perguntar_json(cliente_genai, montar_pergunta(elenco), [cena] + retratos)


def reprovacoes(veredito: Dict) -> List[str]:
    """Traduz o veredito em motivos de reprovação, na linguagem do relatório."""
    if not veredito:
        return []
    motivos = []
    for personagem in veredito.get("personagens", []):
        if personagem.get("confere") is False:
            motivos.append(
                f"{personagem.get('nome', 'personagem')} fora do canônico: "
                f"{personagem.get('motivo', 'sem motivo declarado')}"
            )
    if veredito.get("texto_na_imagem"):
        motivos.append("texto queimado na imagem")
    return motivos


def auditar_acervo(imagens: List[Path], elenco_de, raiz: Path, limite: int = 0) -> List[Dict]:
    """Roda a auditoria de visão sobre as imagens e devolve as reprovações encontradas.

    `limite` existe porque a quota é o recurso escasso: dá para homologar por amostra e
    ainda assim pegar o defeito sistemático (é sempre o mesmo personagem que escapa).
    """
    cliente = gemini.cliente()
    if cliente is None:
        return [{"arquivo": "-", "motivos": ["visão indisponível: falta chave do Gemini"]}]
    achados = []
    for imagem in imagens[:limite] if limite else imagens:
        elenco = elenco_de(imagem)
        motivos = reprovacoes(auditar(cliente, imagem, elenco, raiz))
        if motivos:
            achados.append({
                "arquivo": imagem.relative_to(raiz).as_posix(), "motivos": motivos
            })
    return achados

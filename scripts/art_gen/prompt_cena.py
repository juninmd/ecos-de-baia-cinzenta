"""Montagem do prompt de uma cena: é aqui que a fidelidade dos personagens é decidida.

Separado do `build_scene_manifest` porque o manifesto só orquestra (quem falta, em que
capítulo); as cláusulas que travam rosto, roupa e fase física vivem neste arquivo.
"""

from pathlib import Path
from typing import Dict, List, Optional

from scripts.art_gen import continuidade, vestuario
from scripts.daily_telegram import characters

REPO_ROOT = Path(__file__).resolve().parents[2]

# A auditoria das cenas já geradas achou dois defeitos recorrentes: título do capítulo
# queimado dentro da arte ("CHAPTER 4") e troca do sobretudo bege por outra roupa.
SEM_TEXTO = (
    "Do not render any text, lettering, caption, chapter title, subtitle, timestamp, "
    "watermark or signature anywhere in the image."
)
# Seis das 40 imagens da primeira noite saíram em traço de HQ/ilustração. Não viola a
# Regra Zero, mas mistura estilos ao longo do livro — e o custo de corrigir depois é quota.
ESTILO = (
    "Photorealistic cinematic film still, shot on 35mm, realistic skin texture and "
    "natural lighting. Not an illustration, not a comic book panel, not digital painting."
)
# Sem esta frase o modelo trata os retratos como inspiração e devolve um sósia parecido.
REFERENCIAS = (
    "The attached reference portraits are the canonical faces: reproduce each face, "
    "hair, beard and skin tone exactly as in the reference; only the pose, the framing "
    "and the environment may change."
)
# Defeitos que a auditoria mais reprovou, na ordem em que apareceram.
NEGATIVO = (
    "Reject: extra fingers, deformed hands, warped faces, duplicated characters, "
    "modern-day clothing, sunny daylight, cartoon or anime rendering."
)


def montar_elenco(personagens: List[Dict], capitulo: float = 0.0) -> List[Dict]:
    """Retrato + vestuário + descritor de cada personagem presente na cena.

    Uma âncora só trava o protagonista: a auditoria pegou a Val (LED azul canônico)
    saindo de cabelo rosa porque o retrato dela nunca era enviado junto.
    """
    elenco = []
    for personagem in personagens:
        retrato = characters.reference_image(personagem)
        if retrato:
            elenco.append({
                "nome": personagem["name"],
                "referencia": retrato.relative_to(REPO_ROOT).as_posix(),
                "vestuario": vestuario.na_fase(
                    personagem["name"], characters.wardrobe(personagem), capitulo
                ),
                "descricao": characters.describe(personagem),
            })
    return elenco


def proximo_nome(pasta: Path, indice: int) -> str:
    """Nome livre para a cena: nunca sobrescreve, acrescenta sufixo de versão.

    As duas versões convivem — a antiga continua servindo (inclusive para vídeo) e a
    nova entra ao lado, para comparação.
    """
    if not (pasta / f"cena_{indice}.jpg").exists():
        return f"cena_{indice}.jpg"
    versao = 2
    while (pasta / f"cena_{indice}_v{versao}.jpg").exists():
        versao += 1
    return f"cena_{indice}_v{versao}.jpg"


def seed_da_cena(capitulo: str, indice: int) -> int:
    """Regra 4 do AGENTS.md: mesma cena de mesmo capítulo, mesma imagem.

    O `*100` é o que a regra manda e ainda acomoda os capítulos intercalados: o 30.5
    vira 3050 e não colide com o 30 (3000) nem com o 31 (3100).
    """
    return int(float(capitulo) * 100) + indice


def roupa_da_ancora(ancora: Optional[Dict], elenco: List[Dict]) -> str:
    """Vestuário já resolvido para o capítulo, tirado do elenco montado."""
    if not ancora:
        return ""
    return next((p["vestuario"] for p in elenco if p["nome"] == ancora["name"]), "")


def texto_do_prompt(cena, titulo: str, ancora: Optional[Dict], elenco: List[Dict],
                    capitulo: float) -> str:
    """Prompt final, na ordem em que o modelo obedece: cena, proibições, elenco, fase."""
    base = (
        cena.edit_prompt(ancora, roupa=roupa_da_ancora(ancora, elenco))
        if ancora else cena.image_prompt(titulo)
    )
    return (
        base
        + ". " + SEM_TEXTO
        + ". " + ESTILO
        + (". " + REFERENCIAS if elenco else "")
        + ". " + NEGATIVO
        + vestuario.reforco(elenco)
        + continuidade.clausula(elenco, capitulo)
    )


def montar_entrada(cap: Dict, titulo: str, cena, elenco: List[Dict]) -> Dict:
    """Uma linha do manifesto: tudo que o gerador precisa sem reabrir o capítulo."""
    ancora = characters.pick_anchor(cena.personagens)
    referencia = characters.reference_image(ancora) if ancora else None
    arquivo = proximo_nome(cap["folder_path"], cena.indice)
    return {
        "capitulo": cap["num_str"],
        "cena": cena.indice,
        "saida": f"docs/public/cenas/{cap['folder_name']}/{arquivo}",
        # Nada de sobrescrever: quando a cena já existe, a nova nasce com sufixo.
        "substituir": False,
        "seed": seed_da_cena(cap["num_str"], cena.indice),
        "titulo": titulo,
        "legenda_telegram": f"{cap['folder_name']} cena_{cena.indice}",
        "enquadramento": cena.shot,
        "acao": cena.action,
        "ancora": ancora["name"] if ancora else None,
        # Caminho do retrato canônico: é o que trava a fisionomia (Regra Zero).
        "referencia": referencia.relative_to(REPO_ROOT).as_posix() if referencia else None,
        "vestuario": roupa_da_ancora(ancora, elenco),
        "elenco": elenco,
        "personagens": [characters.describe(c) for c in cena.personagens],
        "prompt": texto_do_prompt(cena, titulo, ancora, elenco, float(cap["num_str"])),
    }


def elenco_da_cena(cap: Dict, indice: int, total: int) -> List[Dict]:
    """Reconstrói o elenco de uma cena já gerada, para auditar fidelidade depois.

    O manifesto só guarda cenas pendentes; quem já virou arquivo saiu de lá. A divisão
    do capítulo é determinística, então recalcular dá exatamente o mesmo elenco.
    """
    from scripts.art_gen.chapters import ler_capitulo
    from scripts.daily_telegram import scenes

    _, corpo = ler_capitulo(cap)
    cenas = scenes.split_scenes(corpo, quantidade=total)
    if not 1 <= indice <= len(cenas):
        return []
    return montar_elenco(cenas[indice - 1].personagens, float(cap["num_str"]))

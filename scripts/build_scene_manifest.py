"""Monta o manifesto das cenas pendentes, para o agy não gastar quota lendo capítulo.

A quota de imagem do Gemini é o recurso escasso: cada rodada do agy que lê capítulo,
divide cenas e escolhe âncora queima tokens que não viram imagem. Aqui isso tudo é
resolvido offline, e o agy recebe prompt pronto + retrato de referência por cena.
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts.daily_telegram import characters, scenes  # noqa: E402
from scripts.generate_missing_scenes import (  # noqa: E402
    extract_chapter_title_and_clean_text,
    get_chapter_files,
)

DESTINO = REPO_ROOT / "docs" / "public" / "cenas" / "manifesto_pendentes.json"
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


def limpar_titulos(titulo: str, corpo: str) -> tuple:
    """Tira os cabeçalhos markdown do corpo — o `# Capítulo N: Nome` entrava no prompt.

    Quando o frontmatter não traz `title:`, o H1 é o melhor título disponível.
    """
    linhas = []
    for linha in corpo.splitlines():
        if linha.lstrip().startswith("#"):
            cabecalho = linha.lstrip("# ").strip()
            if titulo == "Capítulo" and cabecalho:
                titulo = cabecalho
            continue
        linhas.append(linha)
    return titulo, "\n".join(linhas).strip()


def reforco_vestuario(elenco: list) -> str:
    """Última cláusula do prompt, repetindo a roupa de cada personagem.

    A auditoria mostrou que a fisionomia se mantém, mas o vestuário escapa em cena de
    ação: o modelo troca o sobretudo bege por qualquer coisa que "combine" com a briga.
    Repetir no fecho é o que mais segura, porque é a última instrução que ele lê.
    """
    if not elenco:
        return ""
    # Nome inteiro: cortar no primeiro espaço produz "Dra." e "O", que não identificam ninguém.
    roupas = [f"{p['nome']} wears {p['vestuario']}" for p in elenco if p["vestuario"]]
    if not roupas:
        return ""
    return (
        ". MANDATORY WARDROBE, no substitutions even in action scenes: "
        + "; ".join(roupas)
    )


def carregar_regerar() -> set:
    """Cenas que já têm arquivo mas precisam ser refeitas por violarem a fisionomia.

    Nunca se apaga a imagem antiga: ela fica no lugar até a nova existir.
    """
    lista = DESTINO.parent / "regerar.txt"
    if not lista.exists():
        return set()
    return {
        linha.strip()
        for linha in lista.read_text(encoding="utf-8").splitlines()
        if linha.strip() and not linha.startswith("#")
    }


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


def build() -> list:
    regerar = carregar_regerar()
    pendentes = []
    for cap in get_chapter_files():
        pasta = cap["folder_path"]
        faltando = [
            m for m in range(1, 4)
            if not (pasta / f"cena_{m}.jpg").exists()
            or f"docs/public/cenas/{cap['folder_name']}/cena_{m}.jpg" in regerar
        ]
        if not faltando:
            continue

        titulo, corpo = extract_chapter_title_and_clean_text(
            cap["file_path"].read_text(encoding="utf-8")
        )
        titulo, corpo = limpar_titulos(titulo, corpo)
        cenas = scenes.split_scenes(corpo, quantidade=3)
        while len(cenas) < 3:
            cenas.append(cenas[-1])

        for idx in faltando:
            cena = cenas[idx - 1]
            cena.indice = idx
            ancora = characters.pick_anchor(cena.personagens)
            referencia = characters.reference_image(ancora) if ancora else None
            # Uma âncora só trava o protagonista: a auditoria pegou a Val (LED azul canônico)
            # saindo de cabelo rosa porque o retrato dela nunca era enviado junto.
            elenco = []
            for personagem in cena.personagens:
                retrato = characters.reference_image(personagem)
                if retrato:
                    elenco.append({
                        "nome": personagem["name"],
                        "referencia": retrato.relative_to(REPO_ROOT).as_posix(),
                        "vestuario": characters.wardrobe(personagem),
                        "descricao": characters.describe(personagem),
                    })
            pendentes.append({
                "capitulo": cap["num_str"],
                "cena": idx,
                "saida": f"docs/public/cenas/{cap['folder_name']}/{proximo_nome(pasta, idx)}",
                # Nada de sobrescrever: quando a cena já existe, a nova nasce com sufixo.
                "substituir": False,
                "titulo": titulo,
                "legenda_telegram": f"{cap['folder_name']} cena_{idx}",
                "enquadramento": cena.shot,
                "acao": cena.action,
                "ancora": ancora["name"] if ancora else None,
                # Caminho do retrato canônico: é o que trava a fisionomia (Regra Zero).
                "referencia": referencia.relative_to(REPO_ROOT).as_posix() if referencia else None,
                "vestuario": characters.wardrobe(ancora) if ancora else "",
                "elenco": elenco,
                "personagens": [characters.describe(c) for c in cena.personagens],
                "prompt": (
                    (cena.edit_prompt(ancora) if ancora else cena.image_prompt(titulo))
                    + ". " + SEM_TEXTO
                    + ". " + ESTILO
                    + reforco_vestuario(elenco)
                ),
            })
    return pendentes


if __name__ == "__main__":
    pendentes = build()
    DESTINO.write_text(
        json.dumps(pendentes, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    com_ancora = sum(1 for p in pendentes if p["referencia"])
    print(f"📋 {len(pendentes)} cenas pendentes ({com_ancora} com retrato de referência)")
    print(f"💾 {DESTINO.relative_to(REPO_ROOT)}")

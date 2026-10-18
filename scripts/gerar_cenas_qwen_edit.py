"""Vinte imagens por capítulo com Qwen-Image-Edit-2511 (GGUF Q2_K), só este modelo.

Diferente da rota local de `generate_missing_scenes.py`, que alterna dois modelos por
tipo de plano: aqui **todas** as cenas passam pelo Qwen-Edit, inclusive as de ambiente.
É o modelo de edição mais recente da família (não existe Edit-2512) e o Q2_K é o mais
leve dos quinze quants publicados — 7,47 GB, o que deixa folga na VRAM de 16 GB.

Escrever em `docs/public/cenas/capitulo_N/qwen_edit/` mantém a regra 6 do AGENTS.md:
a arte do Gemini (raiz) e a rota local antiga (`local/`) não são tocadas, e as três
ficam comparáveis lado a lado.

O loader e o `qwen_gerar` vêm de `generate_missing_scenes.py` de propósito — a GPU é uma
só e um segundo loader significaria um segundo processo disputando a mesma VRAM.

Uso:
    python scripts/gerar_cenas_qwen_edit.py                 # todos os capítulos
    python scripts/gerar_cenas_qwen_edit.py 1 2 30.5        # só estes
    python scripts/gerar_cenas_qwen_edit.py --limite 1      # uma imagem, para julgar
    python scripts/gerar_cenas_qwen_edit.py --bench 8,12,20 --cap 1
"""

import argparse
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts.art_gen import prompt_cena  # noqa: E402
from scripts.art_gen.chapters import get_chapter_files, ler_capitulo  # noqa: E402
from scripts.daily_telegram import characters, scenes  # noqa: E402
from scripts.generate_missing_scenes import (  # noqa: E402
    QWEN_LABEL, qwen_carregar, qwen_disponivel, qwen_gerar, QWEN_PASSOS, QWEN_CFG,
)

CENAS_POR_CAPITULO = 20
SAIDA = "qwen_edit"
# A rotação de planos tem dez posições e são vinte cenas: sem deslocar a segunda volta,
# a cena 11 repetiria o mesmo plano da 1 na mesma ordem e o capítulo sairia espelhado.
DESLOCAMENTO_2A_VOLTA = 5
# Acima destes planos o corpo tem de caber inteiro: exigir "upper body large in the
# frame" em plano aberto era o que transformava toda cena num retrato 3x4.
PLANOS_ABERTOS = ("wide", "low angle shot", "high angle")


def cenas_do_capitulo(corpo: str, quantidade: int = CENAS_POR_CAPITULO) -> List[scenes.Scene]:
    """Vinte batidas narrativas, mesmo em capítulo curto.

    `split_scenes` limita a quantidade ao número de parágrafos; capítulo de doze
    parágrafos devolveria doze cenas e ficaria eternamente incompleto, porque a
    retomada é por arquivo faltando. As faltantes reciclam o texto das primeiras —
    mas com plano diferente, então não viram imagem repetida.
    """
    base = scenes.split_scenes(corpo, quantidade=quantidade)
    if not base:
        return []
    completas = []
    for i in range(1, quantidade + 1):
        origem = base[(i - 1) % len(base)]
        cena = scenes.Scene(indice=i, texto=origem.texto, personagens=origem.personagens)
        if i > len(scenes.SHOTS):
            desloc = (i - 1 + DESLOCAMENTO_2A_VOLTA) % len(scenes.SHOTS)
            cena.shot_hint = scenes.SHOTS[desloc]
        completas.append(cena)
    return completas


def instrucao(cena: scenes.Scene, anchor: Dict) -> str:
    """Separa o que PRESERVA do que MUDA — sem isso o Edit recorta a referência.

    Só pedir "mantenha o rosto" faz o modelo trocar apenas o fundo: mesma pose, mesmos
    adereços, e as vinte cenas do capítulo viram vinte retratos iguais. É preciso
    afirmar que é uma fotografia nova **e** cravar o enquadramento na mesma instrução.

    A cláusula de proximidade é condicional: em plano aberto ela briga com o próprio
    enquadramento pedido e o resultado volta a ser retrato.
    """
    roupa = characters.wardrobe(anchor)
    acao = scenes.palavras_visuais(cena.texto, limite=4)
    encenacao = scenes.ENCENACAO.get(cena.shot, scenes.ENCENACAO_PADRAO)
    aberto = any(marca in cena.shot for marca in PLANOS_ABERTOS)

    partes = ["Keep the same person: identical face, beard, hair and skin."]
    if roupa:
        partes.append(f"Keep the same outfit: {roupa[:70]}.")
    partes.append(
        "Change the pose and the camera completely: this is a NEW photograph of him, "
        "not the same photo with a different background.")
    enquadramento = f"New framing: {cena.shot}, {encenacao}."
    if aberto:
        enquadramento += (" He is small in the frame, the environment dominates,"
                          " full body visible, caught mid-action, never posing.")
    else:
        enquadramento += (" He is close to the camera, upper body large in the frame,"
                          " face sharp and clearly readable -- but caught mid-action,"
                          " never posing.")
    partes.append(enquadramento)
    partes.append(f"He is doing something in the scene: {acao}." if acao else
                  "He is in the middle of an action, not standing still.")
    partes.append(f"Setting: {scenes.cenario_do_texto(cena.texto)}.")
    partes.append("Gritty cyberpunk Brazil, desaturated grimy colors, dramatic lighting, "
                  "cinematic film still.")
    return " ".join(partes)


def ancora_do_capitulo(lista: List[scenes.Scene], corpo: str) -> Optional[Dict]:
    """Personagem que sustenta o capítulo, para as cenas onde o texto não cita ninguém.

    O Edit exige imagem de entrada: cena sem âncora simplesmente não geraria, e o
    capítulo ficaria com buracos permanentes na numeração.
    """
    for cena in lista:
        anchor = characters.pick_anchor(cena.personagens)
        if anchor:
            return anchor
    return characters.pick_anchor(characters.detect(corpo))


def processar(somente=None, passos=QWEN_PASSOS, cfg=QWEN_CFG, limite=None) -> int:
    """Gera o que falta. Comparação de capítulo por string: existe capítulo "30.5"."""
    capitulos = get_chapter_files()
    if somente:
        capitulos = [c for c in capitulos if c["num_str"] in somente]
    print(f"📚 Capítulos na fila: {len(capitulos)} · alvo {CENAS_POR_CAPITULO} cada "
          f"· modelo {QWEN_LABEL}")

    pipe = qwen_carregar()
    feitas = 0
    for cap in capitulos:
        pasta = cap["folder_path"] / SAIDA
        pasta.mkdir(parents=True, exist_ok=True)
        faltando = [i for i in range(1, CENAS_POR_CAPITULO + 1)
                    if not (pasta / f"cena_{i}.jpg").exists()]
        if not faltando:
            print(f"⏩ {cap['folder_name']} completo.")
            continue

        corpo = ler_capitulo(cap)[1]
        lista = cenas_do_capitulo(corpo)
        if not lista:
            print(f"⚠ {cap['folder_name']} sem corpo utilizável; pulando.")
            continue
        padrao = ancora_do_capitulo(lista, corpo)
        if padrao is None:
            print(f"⚠ {cap['folder_name']} sem personagem com retrato; pulando.")
            continue

        print(f"\n🎨 {cap['folder_name']} — faltam {len(faltando)}")
        for idx in faltando:
            cena = lista[idx - 1]
            anchor = characters.pick_anchor(cena.personagens) or padrao
            referencia = characters.reference_image(anchor)
            seed = prompt_cena.seed_da_cena(cap["num_str"], idx)
            destino = pasta / f"cena_{idx}.jpg"
            inicio = time.time()
            ok = qwen_gerar(pipe, referencia, instrucao(cena, anchor), destino, seed,
                            passos=passos, cfg=cfg)
            print(f"{'🖼' if ok else '❌'} {cap['folder_name']}/cena_{idx}.jpg "
                  f"ancora={anchor['name']} seed={seed} {time.time() - inicio:.0f}s")
            feitas += 1
            if limite and feitas >= limite:
                print(f"⏹ Limite de {limite} imagem(ns) atingido.")
                return feitas
    return feitas


def bench(passos_lista: List[int], cfg: float, cap_num: str, indice: int):
    """Tempo por número de passos, no mesmo processo — a carga do GGUF não é cronometrada."""
    cap = next(c for c in get_chapter_files() if c["num_str"] == cap_num)
    corpo = ler_capitulo(cap)[1]
    lista = cenas_do_capitulo(corpo)
    cena = lista[indice - 1]
    anchor = characters.pick_anchor(cena.personagens) or ancora_do_capitulo(lista, corpo)
    if anchor is None:
        print(f"⚠ cap {cap_num} não tem personagem com retrato; escolha outro.")
        return
    referencia = characters.reference_image(anchor)
    prompt = instrucao(cena, anchor)
    seed = prompt_cena.seed_da_cena(cap_num, indice)
    destino_dir = REPO_ROOT / "docs" / "public" / "cenas" / "_teste_qualidade" / SAIDA
    pipe = qwen_carregar()
    total = len(get_chapter_files()) * CENAS_POR_CAPITULO
    for passos in passos_lista:
        inicio = time.time()
        ok = qwen_gerar(pipe, referencia, prompt, destino_dir / f"p{passos}.jpg", seed,
                        passos=passos, cfg=cfg)
        if not ok:
            continue
        dur = time.time() - inicio
        print(f"RESULTADO passos={passos} cfg={cfg} geracao={dur:.0f}s "
              f"projecao_obra={dur * total / 3600:.0f}h ({total} imagens)")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("capitulos", nargs="*", help="números de capítulo; vazio = todos")
    p.add_argument("--passos", type=int, default=QWEN_PASSOS)
    p.add_argument("--cfg", type=float, default=QWEN_CFG)
    p.add_argument("--limite", type=int, help="para depois de N imagens")
    p.add_argument("--bench", help="lista de passos, ex: 8,12,20")
    p.add_argument("--cap", default="1", help="capítulo do bench")
    p.add_argument("--cena", type=int, default=2, help="cena do bench")
    args = p.parse_args()

    if not qwen_disponivel():
        print("❌ Qwen-Image-Edit indisponível: falta GPU CUDA ou diffusers >= 0.40.")
        sys.exit(1)

    if args.bench:
        bench([int(n) for n in args.bench.split(",")], args.cfg, args.cap, args.cena)
        return

    feitas = processar(somente=args.capitulos or None, passos=args.passos,
                       cfg=args.cfg, limite=args.limite)
    print(f"\n🏁 {feitas} imagem(ns) gerada(s).")


if __name__ == "__main__":
    main()

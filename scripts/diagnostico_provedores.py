"""Sonda os provedores gratuitos e diz qual combinação de parâmetros realmente responde.

Existe porque o ambiente de desenvolvimento não tem saída de rede para provedor de
imagem: a primeira rodada de fumaça no CI levou 500 em toda chamada ao Pollinations, e
adivinhar o motivo pelo log não é diagnóstico. Aqui cada variante é uma linha de
resultado — modelo, tamanho do prompt, referência, cabeçalho — e o CI responde qual vale.

Uso: python scripts/diagnostico_provedores.py [--referencia URL]
"""

import argparse
import json
import sys
import time
import urllib.parse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

import requests  # noqa: E402

BASE = "https://image.pollinations.ai/prompt/"
PROMPT_CURTO = "medium shot, a tired detective in a beige trench coat under neon rain"
PROMPT_LONGO = PROMPT_CURTO + ". " + ("cinematic film still, volumetric fog, " * 40)
PAUSA = 16.0  # tier anônimo: uma imagem a cada 15 s
# O provedor gratuito às vezes pendura em vez de recusar. Sem teto, uma variante lenta
# come o job inteiro e o diagnóstico morre sem dizer nada.
ESPERA_MAXIMA = 75.0


def sondar(nome: str, caminho: str, parametros: dict, cabecalhos: dict = None) -> dict:
    url = BASE + urllib.parse.quote(caminho, safe="") + "?" + urllib.parse.urlencode(parametros)
    try:
        resposta = requests.get(url, headers=cabecalhos or {}, timeout=ESPERA_MAXIMA)
        corpo = resposta.headers.get("content-type", "")
        detalhe = "" if corpo.startswith("image/") else resposta.text[:160].replace("\n", " ")
        return {
            "variante": nome, "status": resposta.status_code, "tipo": corpo,
            "bytes": len(resposta.content), "detalhe": detalhe,
        }
    except requests.RequestException as exc:
        return {"variante": nome, "status": 0, "tipo": "", "bytes": 0,
                "detalhe": f"{type(exc).__name__}: {exc}"}


def variantes(referencia: str) -> list:
    """Uma variante por hipótese sobre a causa do 500, isoladas uma a uma."""
    padrao = {"width": 1376, "height": 768, "seed": 42}
    return [
        ("flux mínimo", PROMPT_CURTO, {}),
        ("flux + tamanho", PROMPT_CURTO, dict(padrao, model="flux")),
        ("flux + nologo", PROMPT_CURTO, dict(padrao, model="flux", nologo="true")),
        ("flux + referrer", PROMPT_CURTO, dict(padrao, model="flux",
                                               referrer="ecos-de-baia-cinzenta")),
        ("flux + prompt longo", PROMPT_LONGO, dict(padrao, model="flux")),
        ("turbo", PROMPT_CURTO, dict(padrao, model="turbo")),
        ("kontext + referência", PROMPT_CURTO, dict(padrao, model="kontext",
                                                    image=referencia)),
        ("kontext sem tamanho", PROMPT_CURTO, {"model": "kontext", "image": referencia,
                                               "seed": 42}),
        ("kontext + nologo", PROMPT_CURTO, dict(padrao, model="kontext",
                                                image=referencia, nologo="true")),
    ]


def listar_modelos() -> None:
    for url in ("https://image.pollinations.ai/models",
                "https://gen.pollinations.ai/models"):
        try:
            resposta = requests.get(url, timeout=60)
            print(f"📚 {url} → {resposta.status_code}: {resposta.text[:400]}")
        except requests.RequestException as exc:
            print(f"📚 {url} → {type(exc).__name__}")


def sondar_space() -> dict:
    """O Space do ZeroGPU é o outro caminho gratuito, e o único que aceita o retrato
    como arquivo local. Vale a pena saber se a cota e a assinatura da API continuam de pé.
    """
    from scripts.daily_telegram import hf_space

    retrato = REPO_ROOT / "docs" / "public" / "personagens" / "gabo.jpg"
    destino = REPO_ROOT / "space_probe.jpg"
    try:
        resultado = hf_space.edit_with_identity(retrato, PROMPT_CURTO, destino, seed=42)
    except BaseException as exc:  # Space grátis: fila, cota ou app error
        return {"variante": "kontext space", "status": 0, "tipo": "",
                "bytes": 0, "detalhe": f"{type(exc).__name__}: {str(exc)[:160]}"}
    if resultado and destino.exists():
        return {"variante": "kontext space", "status": 200, "tipo": "image/jpeg",
                "bytes": destino.stat().st_size, "detalhe": ""}
    return {"variante": "kontext space", "status": 0, "tipo": "", "bytes": 0,
            "detalhe": "sem imagem (cota, fila ou assinatura mudou)"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--space", action="store_true",
                        help="Também sonda o FLUX.1-Kontext no Space do ZeroGPU")
    parser.add_argument(
        "--referencia",
        default="https://raw.githubusercontent.com/juninmd/ecos-de-baia-cinzenta/"
                "master/docs/public/personagens/gabo.jpg",
    )
    args = parser.parse_args()

    listar_modelos()
    resultados = []
    for i, (nome, prompt, parametros) in enumerate(variantes(args.referencia)):
        if i:
            time.sleep(PAUSA)
        resultado = sondar(nome, prompt, parametros)
        marca = "✅" if resultado["tipo"].startswith("image/") else "❌"
        print(f"{marca} {resultado['variante']:24} {resultado['status']} "
              f"{resultado['tipo']:12} {resultado['bytes']:>8} B  {resultado['detalhe']}")
        resultados.append(resultado)

    if args.space:
        resultado = sondar_space()
        marca = "✅" if resultado["tipo"].startswith("image/") else "❌"
        print(f"{marca} {resultado['variante']:24} {resultado['status']} "
              f"{resultado['bytes']:>8} B  {resultado['detalhe']}")
        resultados.append(resultado)

    Path("diagnostico_provedores.json").write_text(
        json.dumps(resultados, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    aprovadas = [r["variante"] for r in resultados if r["tipo"].startswith("image/")]
    print(f"\n🔎 variantes que devolveram imagem: {aprovadas or 'nenhuma'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

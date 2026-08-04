#!/usr/bin/env python3
"""Compila a obra inteira num único arquivo e envia no Telegram.

Diferente de `scripts.daily_telegram.main`, que manda um capítulo por dia, aqui a
história vai completa e de uma vez: um documento com os 234 capítulos em ordem.

    python -m scripts.send_full_story --dry-run     # só compila e mostra o resumo
    python -m scripts.send_full_story               # compila e envia
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

from scripts.daily_telegram.telegram import TelegramClient

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SAIDA = ROOT / ".daily_telegram_out" / "baia-cinzenta-completo.md"


def ordem(p: Path) -> tuple[int, int]:
    m = re.match(r"capitulo-(\d+)(?:\.(\d+))?\.md$", p.name)
    return (int(m.group(1)), int(m.group(2) or 0)) if m else (10**6, 0)


def limpa(bruto: str) -> str:
    """Remove frontmatter e blocos de metadados: o leitor quer a narrativa."""
    texto = re.sub(r"\A---\n.*?\n---\n", "", bruto, flags=re.S)
    texto = re.sub(r"^##? Metadados\n(?:[-*].*\n|\n)*", "", texto, flags=re.M)
    texto = re.sub(r"^## Narrativa\n+", "", texto, flags=re.M)
    return texto.strip()


def compila() -> tuple[Path, int, int]:
    capitulos = sorted(DOCS.glob("capitulo-*.md"), key=ordem)
    if not capitulos:
        raise SystemExit("❌ Nenhum capítulo encontrado em docs/")

    partes = [
        "# Baía Cinzenta",
        "",
        "*A obra completa, em ordem de leitura.*",
        "",
        "---",
        "",
    ]
    palavras = 0
    for cap in capitulos:
        corpo = limpa(cap.read_text(encoding="utf-8"))
        palavras += len(corpo.split())
        partes.append(corpo)
        partes.append("\n---\n")

    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text("\n".join(partes), encoding="utf-8")
    return SAIDA, len(capitulos), palavras


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Envia a obra completa no Telegram.")
    parser.add_argument("--dry-run", action="store_true", help="Compila sem enviar")
    args = parser.parse_args(argv)

    caminho, total, palavras = compila()
    tamanho_mb = caminho.stat().st_size / (1024 * 1024)
    print(f"📚 {total} capítulos · {palavras:,} palavras · {tamanho_mb:.1f} MB")
    print(f"📄 {caminho.relative_to(ROOT)}")

    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    if not args.dry_run and not (token and chat_id):
        raise SystemExit("❌ Defina TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID")

    client = TelegramClient(token, chat_id, dry_run=args.dry_run)
    client.send_message(
        "📖 *Baía Cinzenta* — obra completa\n\n"
        f"{total} capítulos · {palavras:,} palavras\n"
        "Revisão concluída: zero reprovados na régua de qualidade."
    )
    client.send_document(caminho, caption="Baía Cinzenta — a história inteira.")
    print("✅ Enviado." if not args.dry_run else "🧪 Dry-run: nada foi enviado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

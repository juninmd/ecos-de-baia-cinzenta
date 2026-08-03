import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_STATE_FILE = REPO_ROOT / ".daily_telegram_state.json"

# Dia em que o capítulo 1 foi ao ar. A fila é derivada da data justamente para
# não depender de escrita: o workflow roda com GITHUB_TOKEN e o master é
# protegido, então o `git push` do estado sempre falhou com GH006 e a fila
# ficava congelada no mesmo capítulo, dia após dia.
PRIMEIRO_ENVIO = date(2026, 7, 26)


def load_state(state_file: Path = DEFAULT_STATE_FILE) -> Dict:
    """Read the delivery state. Returns an empty state when missing/corrupted."""
    if not state_file.exists():
        return {"last_sent": None, "sent_at": None, "history": []}
    try:
        data = json.loads(state_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print(f"⚠ State file corrupted, starting over: {state_file}")
        return {"last_sent": None, "sent_at": None, "history": []}
    data.setdefault("last_sent", None)
    data.setdefault("history", [])
    return data


def save_state(numero: int, state_file: Path = DEFAULT_STATE_FILE) -> None:
    """Persist the chapter that was just delivered."""
    state = load_state(state_file)
    history = [n for n in state.get("history", []) if n != numero]
    history.append(numero)
    payload = {
        "last_sent": numero,
        "sent_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "history": history[-50:],
    }
    state_file.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"💾 State updated: last_sent={numero}")


def pick_for_date(available: List[int], hoje: Optional[date] = None) -> Optional[int]:
    """Capítulo do dia, derivado da data — um por dia, em ordem, sem estado.

    Um dia que falha é um dia pulado, e isso é intencional: é preferível perder
    um capítulo a reenviar o mesmo indefinidamente porque a gravação do
    progresso não passou pela proteção de branch.
    """
    if not available:
        return None
    ordered = sorted(available)
    dias = ((hoje or datetime.now(timezone.utc).date()) - PRIMEIRO_ENVIO).days
    if dias < 0:
        return ordered[0]
    volta, indice = divmod(dias, len(ordered))
    if volta:
        print(f"🔁 {volta}ª releitura da obra: reiniciando a fila.")
    return ordered[indice]

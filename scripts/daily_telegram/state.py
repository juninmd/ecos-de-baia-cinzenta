import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_STATE_FILE = REPO_ROOT / ".daily_telegram_state.json"


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


def pick_next(available: List[int], state: Dict) -> Optional[int]:
    """Next chapter after the last delivered one; wraps to the first when finished."""
    if not available:
        return None
    ordered = sorted(available)
    last = state.get("last_sent")
    if last is None:
        return ordered[0]
    for numero in ordered:
        if numero > last:
            return numero
    print("🔁 Todos os capítulos enviados, reiniciando do primeiro.")
    return ordered[0]

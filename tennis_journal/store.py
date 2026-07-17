"""JSON-backed in-memory store for tennis journal entries."""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "entries.json"
ENTRIES: list[dict] = []
_last_mtime: float | None = None


def load() -> None:
    global ENTRIES, _last_mtime
    if DATA_FILE.exists():
        with open(DATA_FILE, encoding="utf-8") as f:
            ENTRIES = json.load(f)
        _last_mtime = DATA_FILE.stat().st_mtime
    else:
        ENTRIES = []
        _last_mtime = None


def _ensure_loaded() -> None:
    """Reload from disk when entries.json changed (e.g. edited while server runs)."""
    global ENTRIES, _last_mtime
    if not DATA_FILE.exists():
        if ENTRIES:
            ENTRIES = []
        _last_mtime = None
        return
    mtime = DATA_FILE.stat().st_mtime
    if _last_mtime is None or mtime != _last_mtime:
        load()


def save() -> None:
    global _last_mtime
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(ENTRIES, f, indent=2)
    _last_mtime = DATA_FILE.stat().st_mtime


def get_all(q: str = "") -> list[dict]:
    _ensure_loaded()
    entries = ENTRIES
    if q:
        q_lower = q.lower()
        entries = [e for e in entries if q_lower in e.get("opponent", "").lower()]
    return sorted(entries, key=lambda e: e.get("date", ""), reverse=True)


def get_by_id(entry_id: str) -> dict | None:
    _ensure_loaded()
    for entry in ENTRIES:
        if entry["id"] == entry_id:
            return entry
    return None


def create(data: dict) -> dict:
    _ensure_loaded()
    entry = {
        "id": str(uuid.uuid4()),
        "opponent": data["opponent"],
        "date": data["date"],
        "score": data["score"],
        "notes": data.get("notes", ""),
        "result": data.get("result", ""),
        "match_type": data.get("match_type", "singles"),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    ENTRIES.append(entry)
    save()
    return entry


def update(entry_id: str, data: dict) -> dict | None:
    _ensure_loaded()
    entry = get_by_id(entry_id)
    if entry is None:
        return None
    entry["opponent"] = data["opponent"]
    entry["date"] = data["date"]
    entry["score"] = data["score"]
    entry["notes"] = data.get("notes", "")
    entry["result"] = data.get("result", "")
    entry["match_type"] = data.get("match_type", "singles")
    save()
    return entry


def delete(entry_id: str) -> bool:
    global ENTRIES
    _ensure_loaded()
    for i, entry in enumerate(ENTRIES):
        if entry["id"] == entry_id:
            ENTRIES.pop(i)
            save()
            return True
    return False

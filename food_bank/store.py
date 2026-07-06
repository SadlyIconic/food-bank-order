"""JSON-backed store for catalog, orders, archive, and aggregation."""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ITEMS_FILE = BASE_DIR / "items.json"
ORDERS_FILE = BASE_DIR / "orders.json"
ARCHIVE_FILE = BASE_DIR / "archive.json"

ITEMS: list[dict] = []
ORDERS: list[dict] = []
ARCHIVE: list[dict] = []

_mtime: dict[Path, float | None] = {
    ITEMS_FILE: None,
    ORDERS_FILE: None,
    ARCHIVE_FILE: None,
}


def _read_json(path: Path, default: list) -> list:
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return default.copy() if isinstance(default, list) else default


def _write_json(path: Path, data: list) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    _mtime[path] = path.stat().st_mtime


def _ensure_fresh(path: Path, cache: list, default: list) -> list:
    if not path.exists():
        if cache:
            cache.clear()
        _mtime[path] = None
        return cache
    mtime = path.stat().st_mtime
    if _mtime[path] is None or mtime != _mtime[path]:
        fresh = _read_json(path, default)
        cache.clear()
        cache.extend(fresh)
        _mtime[path] = mtime
    return cache


def load() -> None:
    """Load all data files into memory."""
    global ITEMS, ORDERS, ARCHIVE
    ITEMS = _read_json(ITEMS_FILE, [])
    ORDERS = _read_json(ORDERS_FILE, [])
    ARCHIVE = _read_json(ARCHIVE_FILE, [])
    for path, data in (
        (ITEMS_FILE, ITEMS),
        (ORDERS_FILE, ORDERS),
        (ARCHIVE_FILE, ARCHIVE),
    ):
        _mtime[path] = path.stat().st_mtime if path.exists() else None


def get_items() -> list[dict]:
    _ensure_fresh(ITEMS_FILE, ITEMS, [])
    return ITEMS


def get_item_map() -> dict[str, dict]:
    return {item["id"]: item for item in get_items()}


def get_categories() -> list[str]:
    items = get_items()
    seen: list[str] = []
    for item in items:
        cat = item.get("category", "")
        if cat and cat not in seen:
            seen.append(cat)
    return seen


def get_orders() -> list[dict]:
    _ensure_fresh(ORDERS_FILE, ORDERS, [])
    return ORDERS


def add_order(household_name: str, lines: list[dict]) -> dict:
    _ensure_fresh(ORDERS_FILE, ORDERS, [])
    order = {
        "id": str(uuid.uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "household_name": household_name,
        "lines": lines,
    }
    ORDERS.append(order)
    _write_json(ORDERS_FILE, ORDERS)
    return order


def aggregate_totals(orders: list[dict] | None = None) -> list[dict]:
    """Sum quantities by item_id; sort descending; attach catalog metadata."""
    if orders is None:
        orders = get_orders()
    item_map = get_item_map()
    totals: dict[str, int] = {}
    for order in orders:
        for line in order.get("lines", []):
            item_id = line.get("item_id", "")
            qty = line.get("quantity", 0)
            if item_id and qty > 0:
                totals[item_id] = totals.get(item_id, 0) + qty

    rows: list[dict] = []
    for item_id, quantity in totals.items():
        catalog = item_map.get(item_id, {})
        rows.append(
            {
                "item_id": item_id,
                "name": catalog.get("name", line_name_from_orders(orders, item_id)),
                "category": catalog.get("category", ""),
                "unit": catalog.get("unit", ""),
                "quantity": quantity,
            }
        )
    rows.sort(key=lambda r: r["quantity"], reverse=True)
    return rows


def line_name_from_orders(orders: list[dict], item_id: str) -> str:
    for order in orders:
        for line in order.get("lines", []):
            if line.get("item_id") == item_id:
                return line.get("name", item_id)
    return item_id


def archive_current_round() -> dict | None:
    """Archive aggregated totals for the current round and clear orders."""
    _ensure_fresh(ORDERS_FILE, ORDERS, [])
    if not ORDERS:
        return None
    totals = aggregate_totals(ORDERS)
    round_entry = {
        "id": str(uuid.uuid4()),
        "archived_at": datetime.now(timezone.utc).isoformat(),
        "order_count": len(ORDERS),
        "totals": totals,
    }
    _ensure_fresh(ARCHIVE_FILE, ARCHIVE, [])
    ARCHIVE.append(round_entry)
    _write_json(ARCHIVE_FILE, ARCHIVE)
    ORDERS.clear()
    _write_json(ORDERS_FILE, ORDERS)
    return round_entry


def get_archive() -> list[dict]:
    _ensure_fresh(ARCHIVE_FILE, ARCHIVE, [])
    return sorted(ARCHIVE, key=lambda r: r.get("archived_at", ""), reverse=True)


def get_archive_round(round_id: str) -> dict | None:
    for entry in get_archive():
        if entry["id"] == round_id:
            return entry
    return None

"""Store for catalog, orders, trip planning, and archive (SQLite or Turso)."""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from db import get_conn

BASE_DIR = Path(__file__).resolve().parent
ITEMS_FILE = BASE_DIR / "items.json"

# Legacy JSON paths (migrated on first init)
LEGACY_ORDERS_FILE = BASE_DIR / "orders.json"
LEGACY_ARCHIVE_FILE = BASE_DIR / "archive.json"
LEGACY_TRIP_FILE = BASE_DIR / "trip.json"
LEGACY_INVENTORY_FILE = BASE_DIR / "store_inventory.json"
LEGACY_SELECTION_FILE = BASE_DIR / "selection.json"
LEGACY_FULFILLMENT_FILE = BASE_DIR / "fulfillment.json"

DEFAULT_TRIP = {
    "weight_limit_lb": 200.0,
    "order_weight_limit_lb": 10.0,
    "trip_name": "",
    "pickup_date": "",
    "store_name": "",
    "community_published": False,
}

MAX_PLEDGE_QTY = 50
MAX_PLEDGE_QTY_PER_ITEM = 20
ANONYMOUS_DONOR_NAME = "Anonymous donor"

STAFF_THRESHOLD_LEVELS = ("critically_low", "low", "ok", "high", "full")
STORAGE_TYPES = ("shelf", "refrigerated", "frozen")
STORAGE_TYPE_LABELS = {
    "shelf": "Dry",
    "refrigerated": "Refrigerated",
    "frozen": "Frozen",
}
CATEGORY_PRIORITY = {
    "critically_low": 4,
    "low": 3,
    "ok": 2,
    "high": 1,
    "full": 0,
}
DEFAULT_STAFF_THRESHOLDS = {
    "updated_at": "",
    "categories": {},
    "storage": {},
}

ITEMS: list[dict] = []
_items_mtime: float | None = None


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path, default):
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return default.copy() if isinstance(default, (list, dict)) else default


def _init_schema(conn) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS orders (
            id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            household_name TEXT NOT NULL,
            lines_json TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS archive_rounds (
            id TEXT PRIMARY KEY,
            archived_at TEXT NOT NULL,
            order_count INTEGER NOT NULL,
            totals_json TEXT NOT NULL,
            demand_weight_lb REAL DEFAULT 0,
            trip_json TEXT,
            store_inventory_json TEXT,
            selection_json TEXT,
            fulfillment_json TEXT
        );

        CREATE TABLE IF NOT EXISTS kv_store (
            key TEXT PRIMARY KEY,
            value_json TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS donor_pledges (
            id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            round_id TEXT,
            donor_display_name TEXT NOT NULL,
            item_id TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            note TEXT,
            status TEXT NOT NULL DEFAULT 'pledged'
        );
        """
    )
    conn.commit()


def _kv_get(conn, key: str, default):
    row = conn.execute("SELECT value_json FROM kv_store WHERE key = ?", (key,)).fetchone()
    if row is None:
        return default.copy() if isinstance(default, (list, dict)) else default
    return json.loads(row["value_json"])


def _kv_set(conn, key: str, value) -> None:
    conn.execute(
        "INSERT INTO kv_store (key, value_json) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value_json = excluded.value_json",
        (key, json.dumps(value)),
    )


def _migrate_legacy_json(conn) -> None:
    order_count = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    if order_count == 0 and LEGACY_ORDERS_FILE.exists():
        for order in _read_json(LEGACY_ORDERS_FILE, []):
            conn.execute(
                "INSERT INTO orders (id, created_at, household_name, lines_json) VALUES (?, ?, ?, ?)",
                (
                    order.get("id", str(uuid.uuid4())),
                    order.get("created_at", _utc_now()),
                    order.get("household_name", ""),
                    json.dumps(order.get("lines", [])),
                ),
            )

    archive_count = conn.execute("SELECT COUNT(*) FROM archive_rounds").fetchone()[0]
    if archive_count == 0 and LEGACY_ARCHIVE_FILE.exists():
        for entry in _read_json(LEGACY_ARCHIVE_FILE, []):
            conn.execute(
                """INSERT INTO archive_rounds
                   (id, archived_at, order_count, totals_json, demand_weight_lb)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    entry.get("id", str(uuid.uuid4())),
                    entry.get("archived_at", _utc_now()),
                    entry.get("order_count", 0),
                    json.dumps(entry.get("totals", [])),
                    entry.get("demand_weight_lb", 0),
                ),
            )

    if conn.execute("SELECT COUNT(*) FROM kv_store WHERE key = 'trip'").fetchone()[0] == 0:
        if LEGACY_TRIP_FILE.exists():
            _kv_set(conn, "trip", _read_json(LEGACY_TRIP_FILE, DEFAULT_TRIP))
        else:
            _kv_set(conn, "trip", DEFAULT_TRIP)

    for key, path, default in (
        ("store_inventory", LEGACY_INVENTORY_FILE, {"lines": []}),
        ("selection", LEGACY_SELECTION_FILE, {"lines": [], "total_weight_lb": 0}),
        ("fulfillment", LEGACY_FULFILLMENT_FILE, {"items": [], "households": []}),
    ):
        if conn.execute("SELECT COUNT(*) FROM kv_store WHERE key = ?", (key,)).fetchone()[0] == 0:
            if path.exists():
                _kv_set(conn, key, _read_json(path, default))
            else:
                _kv_set(conn, key, default)

    conn.commit()


def load() -> None:
    """Initialize database and load catalog."""
    global ITEMS, _items_mtime
    with get_conn() as conn:
        _init_schema(conn)
        _migrate_legacy_json(conn)
    ITEMS = _read_json(ITEMS_FILE, [])
    _items_mtime = ITEMS_FILE.stat().st_mtime if ITEMS_FILE.exists() else None


def get_items() -> list[dict]:
    global ITEMS, _items_mtime
    if ITEMS_FILE.exists():
        mtime = ITEMS_FILE.stat().st_mtime
        if _items_mtime is None or mtime != _items_mtime:
            ITEMS = _read_json(ITEMS_FILE, [])
            _items_mtime = mtime
    return ITEMS


def get_item_map() -> dict[str, dict]:
    return {item["id"]: item for item in get_items()}


def get_categories() -> list[str]:
    seen: list[str] = []
    for item in get_items():
        cat = item.get("category", "")
        if cat and cat not in seen:
            seen.append(cat)
    return seen


def get_item_storage_type(item: dict) -> str:
    storage = item.get("storage_type", "")
    if storage in STORAGE_TYPES:
        return storage
    cat = item.get("category", "")
    if cat == "Dairy":
        return "refrigerated"
    if cat == "Frozen":
        return "frozen"
    return "shelf"


def get_staff_thresholds() -> dict:
    with get_conn() as conn:
        thresholds = _kv_get(conn, "staff_thresholds", DEFAULT_STAFF_THRESHOLDS.copy())
    thresholds.setdefault("updated_at", "")
    thresholds.setdefault("categories", {})
    thresholds.setdefault("storage", {})
    return thresholds


def save_staff_thresholds(categories: dict, storage: dict) -> dict:
    thresholds = {
        "updated_at": _utc_now(),
        "categories": {
            k: v for k, v in categories.items() if v in STAFF_THRESHOLD_LEVELS
        },
        "storage": {
            k: v
            for k, v in storage.items()
            if k in STORAGE_TYPES and v in STAFF_THRESHOLD_LEVELS
        },
    }
    with get_conn() as conn:
        _kv_set(conn, "staff_thresholds", thresholds)
        conn.commit()
    return thresholds


def capacity_is_set() -> bool:
    return bool(get_staff_thresholds().get("updated_at"))


def item_weight_lb(item_id: str) -> float:
    catalog = get_item_map().get(item_id, {})
    return float(catalog.get("weight_lb", 0) or 0)


def compute_lines_weight(lines: list[dict]) -> float:
    total = 0.0
    for line in lines:
        qty = line.get("quantity", 0)
        try:
            qty = int(qty)
        except (TypeError, ValueError):
            continue
        if qty < 1:
            continue
        total += qty * item_weight_lb(line.get("item_id", ""))
    return round(total, 2)


def get_trip_settings() -> dict:
    with get_conn() as conn:
        trip = _kv_get(conn, "trip", DEFAULT_TRIP)
    for key, val in DEFAULT_TRIP.items():
        trip.setdefault(key, val)
    return trip


def save_trip_settings(settings: dict) -> dict:
    trip = get_trip_settings()
    trip.update(settings)
    with get_conn() as conn:
        _kv_set(conn, "trip", trip)
        conn.commit()
    return trip


def get_order_weight_limit_lb() -> float:
    return float(get_trip_settings().get("order_weight_limit_lb", 10))


def get_weight_limit_lb() -> float:
    return float(get_trip_settings().get("weight_limit_lb", 200))


def get_orders() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, created_at, household_name, lines_json FROM orders ORDER BY created_at"
        ).fetchall()
    orders = []
    for row in rows:
        orders.append(
            {
                "id": row["id"],
                "created_at": row["created_at"],
                "household_name": row["household_name"],
                "lines": json.loads(row["lines_json"]),
            }
        )
    return orders


def add_order(household_name: str, lines: list[dict]) -> dict:
    del household_name  # PII not stored; column kept for migration compatibility
    order = {
        "id": str(uuid.uuid4()),
        "created_at": _utc_now(),
        "household_name": "",
        "lines": lines,
    }
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO orders (id, created_at, household_name, lines_json) VALUES (?, ?, ?, ?)",
            (order["id"], order["created_at"], "", json.dumps(lines)),
        )
        conn.commit()
    return order


def line_name_from_orders(orders: list[dict], item_id: str) -> str:
    for order in orders:
        for line in order.get("lines", []):
            if line.get("item_id") == item_id:
                return line.get("name", item_id)
    return item_id


def aggregate_totals(orders: list[dict] | None = None, sort_mode: str = "demand") -> list[dict]:
    """Sum quantities by item_id with weight metadata."""
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
        weight_lb = float(catalog.get("weight_lb", 0) or 0)
        rows.append(
            {
                "item_id": item_id,
                "name": catalog.get("name", line_name_from_orders(orders, item_id)),
                "category": catalog.get("category", ""),
                "unit": catalog.get("unit", ""),
                "quantity": quantity,
                "weight_lb": weight_lb,
                "total_weight_lb": round(quantity * weight_lb, 2),
            }
        )

    if sort_mode == "weight":
        rows.sort(key=lambda r: r["total_weight_lb"], reverse=True)
    else:
        rows.sort(key=lambda r: r["quantity"], reverse=True)
    return rows


def demand_weight_lb(orders: list[dict] | None = None) -> float:
    if orders is None:
        orders = get_orders()
    return round(sum(compute_lines_weight(o.get("lines", [])) for o in orders), 2)


def orders_with_weight() -> list[dict]:
    result = []
    for order in get_orders():
        weight = compute_lines_weight(order.get("lines", []))
        result.append({**order, "weight_lb": weight})
    return result


def get_store_inventory() -> dict:
    with get_conn() as conn:
        inv = _kv_get(conn, "store_inventory", {"lines": []})
    inv.setdefault("updated_at", "")
    inv.setdefault("store_name", "")
    inv.setdefault("expires_by", "")
    inv.setdefault("lines", [])
    return inv


def save_store_inventory(inventory: dict) -> dict:
    inventory = dict(inventory)
    inventory["updated_at"] = _utc_now()
    with get_conn() as conn:
        _kv_set(conn, "store_inventory", inventory)
        conn.commit()
    return inventory


def inventory_map() -> dict[str, dict]:
    return {line["item_id"]: line for line in get_store_inventory().get("lines", [])}


def get_selection() -> dict:
    with get_conn() as conn:
        sel = _kv_get(conn, "selection", {"lines": [], "total_weight_lb": 0})
    sel.setdefault("lines", [])
    sel.setdefault("total_weight_lb", 0)
    sel.setdefault("weight_limit_lb", get_weight_limit_lb())
    return sel


def save_selection(selection: dict) -> dict:
    selection = dict(selection)
    selection["weight_limit_lb"] = get_weight_limit_lb()
    total = 0.0
    for line in selection.get("lines", []):
        pick_qty = int(line.get("pick_qty", 0) or 0)
        weight = float(line.get("weight_lb", item_weight_lb(line.get("item_id", ""))) or 0)
        line["pick_qty"] = pick_qty
        line["line_weight_lb"] = round(pick_qty * weight, 2)
        total += line["line_weight_lb"]
    selection["total_weight_lb"] = round(total, 2)
    with get_conn() as conn:
        _kv_set(conn, "selection", selection)
        conn.commit()
    return selection


def _expires_within_24h(expires_at: str) -> bool:
    if not expires_at:
        return False
    try:
        exp = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        return (exp - now).total_seconds() <= 86400
    except ValueError:
        try:
            exp_date = datetime.strptime(expires_at[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            return (exp_date - now).total_seconds() <= 86400
        except ValueError:
            return False


def build_planner_rows() -> list[dict]:
    """Merge demand, inventory, and selection for the planner UI."""
    totals = {r["item_id"]: r for r in aggregate_totals()}
    inv_map = inventory_map()
    sel_map = {l["item_id"]: l for l in get_selection().get("lines", [])}
    item_map = get_item_map()

    all_ids = set(totals) | set(inv_map) | set(sel_map)
    rows = []
    for item_id in all_ids:
        catalog = item_map.get(item_id, {})
        demand = totals.get(item_id, {})
        inv = inv_map.get(item_id, {})
        sel = sel_map.get(item_id, {})
        requested = demand.get("quantity", 0)
        available = int(inv.get("available_qty", 0) or 0)
        unit_weight = float(
            inv.get("weight_lb") or catalog.get("weight_lb") or 0
        )
        pick_qty = int(sel.get("pick_qty", 0) or 0)
        expires_at = inv.get("expires_at", "")
        rows.append(
            {
                "item_id": item_id,
                "name": catalog.get("name", item_id),
                "category": catalog.get("category", ""),
                "unit": catalog.get("unit", ""),
                "requested": requested,
                "available_qty": available,
                "pick_qty": pick_qty,
                "weight_lb": unit_weight,
                "line_weight_lb": round(pick_qty * unit_weight, 2),
                "fill_pct": round(100 * pick_qty / requested, 1) if requested else 0,
                "expires_at": expires_at,
                "expires_soon": _expires_within_24h(expires_at),
            }
        )

    rows.sort(key=lambda r: r["requested"], reverse=True)
    return rows


def suggest_fill() -> dict:
    """Greedy fill: prioritize unmet demand, respect weight cap and availability."""
    weight_limit = get_weight_limit_lb()
    totals = aggregate_totals()
    inv_map = inventory_map()
    remaining_weight = weight_limit

    candidates = []
    for row in totals:
        item_id = row["item_id"]
        requested = row["quantity"]
        inv = inv_map.get(item_id, {})
        available = int(inv.get("available_qty", 0) or 0)
        if available <= 0 or requested <= 0:
            continue
        unit_weight = float(
            inv.get("weight_lb") or row.get("weight_lb") or item_weight_lb(item_id)
        )
        if unit_weight <= 0:
            continue
        unmet = requested
        expires_at = inv.get("expires_at", "")
        candidates.append(
            {
                "item_id": item_id,
                "requested": requested,
                "available_qty": available,
                "weight_lb": unit_weight,
                "unmet": unmet,
                "expires_soon": _expires_within_24h(expires_at),
            }
        )

    candidates.sort(
        key=lambda c: (c["expires_soon"], c["unmet"]),
        reverse=True,
    )

    lines = []
    for c in candidates:
        if remaining_weight <= 0:
            break
        max_by_weight = int(remaining_weight // c["weight_lb"]) if c["weight_lb"] > 0 else 0
        pick_qty = min(c["available_qty"], c["requested"], max_by_weight)
        if pick_qty <= 0:
            continue
        line_weight = round(pick_qty * c["weight_lb"], 2)
        lines.append(
            {
                "item_id": c["item_id"],
                "pick_qty": pick_qty,
                "weight_lb": c["weight_lb"],
                "line_weight_lb": line_weight,
            }
        )
        remaining_weight = round(remaining_weight - line_weight, 2)

    return save_selection({"lines": lines, "total_weight_lb": 0, "weight_limit_lb": weight_limit})


def compute_fulfillment() -> dict:
    """Compute item-level and household-level fulfillment from selection vs demand."""
    totals = {r["item_id"]: r for r in aggregate_totals()}
    sel_map = {l["item_id"]: l for l in get_selection().get("lines", [])}
    orders = get_orders()
    item_map = get_item_map()

    items_result = []
    picked_by_item: dict[str, int] = {}

    for item_id, demand in totals.items():
        picked = int(sel_map.get(item_id, {}).get("pick_qty", 0) or 0)
        requested = demand["quantity"]
        shortfall = max(0, requested - picked)
        picked_by_item[item_id] = picked
        catalog = item_map.get(item_id, {})
        items_result.append(
            {
                "item_id": item_id,
                "name": demand.get("name", catalog.get("name", item_id)),
                "requested": requested,
                "picked": picked,
                "shortfall": shortfall,
                "unit": demand.get("unit", catalog.get("unit", "")),
            }
        )

    items_result.sort(key=lambda r: r["shortfall"], reverse=True)

    households_result = []
    for order in orders:
        household_name = order.get("household_name") or "Anonymous"
        lines_out = []
        for line in order.get("lines", []):
            item_id = line.get("item_id", "")
            requested = int(line.get("quantity", 0) or 0)
            total_requested = totals.get(item_id, {}).get("quantity", 0)
            total_picked = picked_by_item.get(item_id, 0)
            if total_requested > 0 and total_picked > 0:
                allocated = min(requested, int(total_picked * requested / total_requested))
            else:
                allocated = 0
            shortfall = max(0, requested - allocated)
            catalog = item_map.get(item_id, {})
            lines_out.append(
                {
                    "item_id": item_id,
                    "name": line.get("name", catalog.get("name", item_id)),
                    "requested": requested,
                    "allocated": allocated,
                    "shortfall": shortfall,
                    "unit": catalog.get("unit", ""),
                }
            )
        households_result.append(
            {
                "order_id": order["id"],
                "household_name": household_name,
                "lines": lines_out,
            }
        )

    return {"items": items_result, "households": households_result, "computed_at": _utc_now()}


def get_fulfillment() -> dict:
    with get_conn() as conn:
        data = _kv_get(conn, "fulfillment", {"items": [], "households": []})
    data.setdefault("items", [])
    data.setdefault("households", [])
    return data


def save_fulfillment(fulfillment: dict | None = None) -> dict:
    if fulfillment is None:
        fulfillment = compute_fulfillment()
    with get_conn() as conn:
        _kv_set(conn, "fulfillment", fulfillment)
        conn.commit()
    return fulfillment


def lookup_household_status(household_name: str) -> dict | None:
    """Find fulfillment for a household in current round."""
    name = household_name.strip().lower()
    if not name:
        return None
    fulfillment = get_fulfillment()
    if not fulfillment.get("households"):
        fulfillment = compute_fulfillment()
    for hh in fulfillment.get("households", []):
        if (hh.get("household_name") or "").strip().lower() == name:
            return {
                "household_name": hh["household_name"],
                "lines": hh["lines"],
                "trip": get_trip_settings(),
                "has_fulfillment": bool(get_selection().get("lines")),
            }
    return None


def _add_to_selection_pick(item_id: str, quantity: int) -> None:
    """Increase planned pick qty for an item (donor delivery counts toward fulfillment)."""
    quantity = max(0, int(quantity))
    if quantity <= 0:
        return

    totals = {r["item_id"]: r for r in aggregate_totals()}
    requested = int(totals.get(item_id, {}).get("quantity", 0) or 0)
    selection = get_selection()
    lines = list(selection.get("lines", []))
    found = False
    for line in lines:
        if line.get("item_id") == item_id:
            current = int(line.get("pick_qty", 0) or 0)
            line["pick_qty"] = min(requested, current + quantity) if requested else current + quantity
            line["weight_lb"] = float(line.get("weight_lb") or item_weight_lb(item_id))
            found = True
            break
    if not found:
        pick_qty = min(requested, quantity) if requested else quantity
        lines.append(
            {
                "item_id": item_id,
                "pick_qty": pick_qty,
                "weight_lb": item_weight_lb(item_id),
            }
        )
    save_selection({"lines": lines, "total_weight_lb": selection.get("total_weight_lb", 0)})


def _add_to_store_inventory(item_id: str, quantity: int) -> None:
    """Increase on-hand store inventory when a donor delivery is recorded."""
    quantity = max(0, int(quantity))
    if quantity <= 0:
        return

    inventory = get_store_inventory()
    lines = list(inventory.get("lines", []))
    found = False
    for line in lines:
        if line.get("item_id") == item_id:
            line["available_qty"] = int(line.get("available_qty", 0) or 0) + quantity
            line["weight_lb"] = float(line.get("weight_lb") or item_weight_lb(item_id))
            found = True
            break
    if not found:
        lines.append(
            {
                "item_id": item_id,
                "available_qty": quantity,
                "weight_lb": item_weight_lb(item_id),
                "expires_at": "",
            }
        )
    save_store_inventory({**inventory, "lines": lines})


def _apply_donor_receipt(item_id: str, quantity: int) -> None:
    """Record a donor delivery: add stock, increase picks, refresh fulfillment."""
    _add_to_store_inventory(item_id, quantity)
    _add_to_selection_pick(item_id, quantity)
    save_fulfillment()


def _pledge_row_dict(row) -> dict:
    catalog = get_item_map().get(row["item_id"], {})
    return {
        "id": row["id"],
        "created_at": row["created_at"],
        "round_id": row["round_id"],
        "donor_display_name": row["donor_display_name"],
        "item_id": row["item_id"],
        "item_name": catalog.get("name", row["item_id"]),
        "quantity": row["quantity"],
        "note": row["note"] or "",
        "status": row["status"],
    }


def current_round_id() -> str:
    """Snapshot key tying pledges to the active trip."""
    trip = get_trip_settings()
    name = (trip.get("trip_name") or "").strip() or "trip"
    date = (trip.get("pickup_date") or "").strip() or "unknown"
    return f"{name}|{date}"


def _pledged_qty_by_item(round_id: str | None = None, status: str = "pledged") -> dict[str, int]:
    rid = round_id if round_id is not None else current_round_id()
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT item_id, SUM(quantity) AS total
               FROM donor_pledges
               WHERE round_id = ? AND status = ?
               GROUP BY item_id""",
            (rid, status),
        ).fetchall()
    return {row["item_id"]: int(row["total"]) for row in rows}


def get_donor_needs() -> list[dict]:
    """Compute donor board items from demand, staff thresholds, and pledges."""
    totals = aggregate_totals()
    thresholds = get_staff_thresholds()
    cat_levels = thresholds.get("categories", {})
    storage_levels = thresholds.get("storage", {})
    item_map = get_item_map()
    pledged_by_item = _pledged_qty_by_item()

    items: list[dict] = []
    for row in totals:
        demand_qty = int(row.get("quantity", 0) or 0)
        if demand_qty <= 0:
            continue
        item_id = row["item_id"]
        catalog = item_map.get(item_id, {})
        category = catalog.get("category", row.get("category", ""))
        storage_type = get_item_storage_type(catalog)

        cat_level = cat_levels.get(category, "ok")
        storage_level = storage_levels.get(storage_type, "ok")

        if cat_level in ("high", "full"):
            continue
        if storage_level == "full":
            continue

        pledged = pledged_by_item.get(item_id, 0)
        remaining = max(0, demand_qty - pledged)
        priority_score = CATEGORY_PRIORITY.get(cat_level, 2)

        items.append(
            {
                "item_id": item_id,
                "name": row.get("name", catalog.get("name", item_id)),
                "category": category,
                "category_level": cat_level,
                "storage_type": storage_type,
                "unit": row.get("unit", catalog.get("unit", "")),
                "image": f"images/items/{item_id}.svg",
                "requested": demand_qty,
                "pledged": pledged,
                "remaining_need": remaining,
                "priority_score": priority_score,
            }
        )

    items.sort(key=lambda r: (r["priority_score"], r["remaining_need"]), reverse=True)
    return items


def get_community_needs(
    *,
    include_unpublished: bool = False,
    admin_preview: bool = False,
) -> dict:
    """Public needs board data — no household names or order details."""
    show_unpublished = include_unpublished or admin_preview
    trip = get_trip_settings()
    published = bool(trip.get("community_published"))
    thresholds = get_staff_thresholds()
    capacity_set = capacity_is_set()

    trip_context = {
        "trip_name": trip.get("trip_name", ""),
        "pickup_date": trip.get("pickup_date", ""),
        "store_name": trip.get("store_name", ""),
    }

    if not capacity_set:
        return {
            "published": published,
            "ready": False,
            "capacity_set": False,
            "all_covered": False,
            "items": [],
            "pledges": [],
            "categories": [],
            "donors": [],
            "trip": trip_context,
            "capacity_updated_at": "",
            "state": "not_recorded",
            "round_id": current_round_id(),
        }

    if not published and not show_unpublished:
        return {
            "published": False,
            "ready": True,
            "capacity_set": True,
            "all_covered": False,
            "items": [],
            "pledges": [],
            "categories": [],
            "donors": [],
            "trip": trip_context,
            "capacity_updated_at": thresholds.get("updated_at", ""),
            "state": "unpublished",
            "round_id": current_round_id(),
        }

    donor_items = get_donor_needs()
    categories: set[str] = set()
    for item in donor_items:
        if item.get("category"):
            categories.add(item["category"])

    pledges = get_pledges_for_round(statuses=["pledged", "received"])
    donor_names = sorted(
        {
            p["donor_display_name"]
            for p in pledges
            if p["donor_display_name"] != ANONYMOUS_DONOR_NAME
        }
    )

    if not donor_items:
        state = "all_covered"
    elif all(i["remaining_need"] <= 0 for i in donor_items):
        state = "pledged_out"
    else:
        state = "open"

    return {
        "published": published,
        "ready": True,
        "capacity_set": True,
        "all_covered": len(donor_items) == 0,
        "items": donor_items,
        "pledges": pledges,
        "categories": sorted(categories),
        "donors": donor_names,
        "trip": trip_context,
        "capacity_updated_at": thresholds.get("updated_at", ""),
        "state": state,
        "round_id": current_round_id(),
    }


def get_pledges_for_round(
    round_id: str | None = None,
    status: str = "pledged",
    *,
    statuses: list[str] | None = None,
) -> list[dict]:
    rid = round_id if round_id is not None else current_round_id()
    if statuses:
        placeholders = ",".join("?" * len(statuses))
        query = f"""SELECT id, created_at, round_id, donor_display_name, item_id,
                           quantity, note, status
                    FROM donor_pledges
                    WHERE round_id = ? AND status IN ({placeholders})
                    ORDER BY created_at DESC"""
        params: list = [rid, *statuses]
    else:
        query = """SELECT id, created_at, round_id, donor_display_name, item_id,
                          quantity, note, status
                   FROM donor_pledges
                   WHERE round_id = ? AND status = ?
                   ORDER BY created_at DESC"""
        params = [rid, status]
    with get_conn() as conn:
        rows = conn.execute(query, params).fetchall()
    return [_pledge_row_dict(row) for row in rows]


def get_all_pledges_for_round(round_id: str | None = None) -> list[dict]:
    """All pledges for admin moderation (any status)."""
    rid = round_id if round_id is not None else current_round_id()
    item_map = get_item_map()
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT id, created_at, round_id, donor_display_name, item_id,
                      quantity, note, status
               FROM donor_pledges
               WHERE round_id = ?
               ORDER BY created_at DESC""",
            (rid,),
        ).fetchall()
    pledges = []
    for row in rows:
        catalog = item_map.get(row["item_id"], {})
        pledges.append(
            {
                "id": row["id"],
                "created_at": row["created_at"],
                "round_id": row["round_id"],
                "donor_display_name": row["donor_display_name"],
                "item_id": row["item_id"],
                "item_name": catalog.get("name", row["item_id"]),
                "quantity": row["quantity"],
                "note": row["note"] or "",
                "status": row["status"],
            }
        )
    return pledges


def add_donor_pledge(
    donor_display_name: str,
    item_id: str,
    quantity: int,
    note: str = "",
) -> dict:
    """Record a donor pledge against an item with open community need."""
    name = (donor_display_name or "").strip()
    if not name:
        name = ANONYMOUS_DONOR_NAME
    if len(name) > 100:
        raise ValueError("Donor name is too long.")

    item_map = get_item_map()
    if item_id not in item_map:
        raise ValueError("Invalid item.")

    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        raise ValueError("Quantity must be a positive number.") from None

    if quantity < 1:
        raise ValueError("Quantity must be at least 1.")
    if quantity > MAX_PLEDGE_QTY:
        raise ValueError(f"Maximum quantity per pledge is {MAX_PLEDGE_QTY}.")

    trip = get_trip_settings()
    if not trip.get("community_published"):
        raise ValueError("Community board is not open for pledges yet.")

    needs = get_community_needs(include_unpublished=True)
    if not needs.get("ready"):
        raise ValueError("Today's shortages have not been set yet.")

    need_row = next((i for i in needs["items"] if i["item_id"] == item_id), None)
    if need_row is None:
        raise ValueError("This item is not on the needs board.")
    if need_row["remaining_need"] < quantity:
        raise ValueError(
            f"Only {need_row['remaining_need']} still needed for this item."
        )
    if quantity > MAX_PLEDGE_QTY_PER_ITEM:
        raise ValueError(f"Maximum quantity per pledge is {MAX_PLEDGE_QTY_PER_ITEM}.")

    note = (note or "").strip()[:500]
    pledge = {
        "id": str(uuid.uuid4()),
        "created_at": _utc_now(),
        "round_id": current_round_id(),
        "donor_display_name": name,
        "item_id": item_id,
        "quantity": quantity,
        "note": note,
        "status": "pledged",
    }
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO donor_pledges
               (id, created_at, round_id, donor_display_name, item_id, quantity, note, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                pledge["id"],
                pledge["created_at"],
                pledge["round_id"],
                pledge["donor_display_name"],
                pledge["item_id"],
                pledge["quantity"],
                pledge["note"],
                pledge["status"],
            ),
        )
        conn.commit()
    catalog = item_map[item_id]
    return {
        **pledge,
        "item_name": catalog.get("name", item_id),
    }


def update_pledge_status(pledge_id: str, status: str) -> dict | None:
    if status not in ("pledged", "received", "cancelled"):
        raise ValueError("Invalid pledge status.")
    with get_conn() as conn:
        row = conn.execute(
            """SELECT id, created_at, round_id, donor_display_name, item_id,
                      quantity, note, status
               FROM donor_pledges WHERE id = ?""",
            (pledge_id,),
        ).fetchone()
        if row is None:
            return None

        conn.execute(
            "UPDATE donor_pledges SET status = ? WHERE id = ?",
            (status, pledge_id),
        )
        conn.commit()

    updated = _pledge_row_dict(row)
    updated["status"] = status
    return updated


def set_community_published(published: bool) -> dict:
    return save_trip_settings({"community_published": bool(published)})


def archive_current_round() -> dict | None:
    """Archive current round with capacity data and clear working state."""
    orders = get_orders()
    if not orders:
        return None

    round_id = current_round_id()
    pledges_snapshot = get_all_pledges_for_round(round_id)
    totals = aggregate_totals(orders)
    demand_wt = demand_weight_lb(orders)
    trip = get_trip_settings()
    staff_thresholds = get_staff_thresholds()

    round_entry = {
        "id": str(uuid.uuid4()),
        "archived_at": _utc_now(),
        "order_count": len(orders),
        "totals": totals,
        "demand_weight_lb": demand_wt,
        "trip": trip,
        "staff_thresholds": staff_thresholds,
        "donor_pledges": pledges_snapshot,
    }

    with get_conn() as conn:
        conn.execute(
            """INSERT INTO archive_rounds
               (id, archived_at, order_count, totals_json, demand_weight_lb,
                trip_json, store_inventory_json, selection_json, fulfillment_json)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                round_entry["id"],
                round_entry["archived_at"],
                round_entry["order_count"],
                json.dumps(totals),
                demand_wt,
                json.dumps(trip),
                json.dumps({}),
                json.dumps(staff_thresholds),
                json.dumps({}),
            ),
        )
        conn.execute("DELETE FROM orders")
        conn.execute(
            "UPDATE donor_pledges SET status = 'received' WHERE round_id = ? AND status = 'pledged'",
            (round_id,),
        )
        _kv_set(conn, "staff_thresholds", DEFAULT_STAFF_THRESHOLDS.copy())
        trip = _kv_get(conn, "trip", DEFAULT_TRIP)
        trip["community_published"] = False
        _kv_set(conn, "trip", trip)
        conn.commit()

    return round_entry


def get_archive() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT id, archived_at, order_count, totals_json, demand_weight_lb,
                      trip_json, store_inventory_json, selection_json, fulfillment_json
               FROM archive_rounds ORDER BY archived_at DESC"""
        ).fetchall()
    result = []
    for row in rows:
        entry = {
            "id": row["id"],
            "archived_at": row["archived_at"],
            "order_count": row["order_count"],
            "totals": json.loads(row["totals_json"]),
            "demand_weight_lb": row["demand_weight_lb"] or 0,
        }
        if row["trip_json"]:
            entry["trip"] = json.loads(row["trip_json"])
        if row["selection_json"]:
            selection_data = json.loads(row["selection_json"])
            if selection_data.get("categories") is not None:
                entry["staff_thresholds"] = selection_data
        if row["fulfillment_json"]:
            fulfillment_data = json.loads(row["fulfillment_json"])
            if fulfillment_data.get("items") is not None or fulfillment_data.get("households") is not None:
                entry["fulfillment"] = fulfillment_data
        result.append(entry)
    return result


def get_archive_round(round_id: str) -> dict | None:
    with get_conn() as conn:
        row = conn.execute(
            """SELECT id, archived_at, order_count, totals_json, demand_weight_lb,
                      trip_json, store_inventory_json, selection_json, fulfillment_json
               FROM archive_rounds WHERE id = ?""",
            (round_id,),
        ).fetchone()
    if row is None:
        return None
    entry = {
        "id": row["id"],
        "archived_at": row["archived_at"],
        "order_count": row["order_count"],
        "totals": json.loads(row["totals_json"]),
        "demand_weight_lb": row["demand_weight_lb"] or 0,
    }
    if row["trip_json"]:
        entry["trip"] = json.loads(row["trip_json"])
    if row["store_inventory_json"]:
        store_inv = json.loads(row["store_inventory_json"])
        if store_inv:
            entry["store_inventory"] = store_inv
    if row["selection_json"]:
        selection_data = json.loads(row["selection_json"])
        if selection_data.get("categories") is not None:
            entry["staff_thresholds"] = selection_data
        elif selection_data:
            entry["selection"] = selection_data
    if row["fulfillment_json"]:
        fulfillment_data = json.loads(row["fulfillment_json"])
        if fulfillment_data.get("items") is not None or fulfillment_data.get("households") is not None:
            entry["fulfillment"] = fulfillment_data
    return entry

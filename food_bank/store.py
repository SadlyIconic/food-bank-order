"""Store for catalog, orders, trip planning, and archive (SQLite or Turso)."""

import json
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from db import get_conn

BASE_DIR = Path(__file__).resolve().parent
ITEMS_FILE = BASE_DIR / "items.json"
CATEGORIES_FILE = BASE_DIR / "categories.json"
FLL_PALLETS_FILE = BASE_DIR / "fll_pallets.json"

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

DEFAULT_APP_SETTINGS = {
    "food_bank_id": "default",
    "agency_display_name": "Food Bank",
    "rolling_weeks": 4,
    "max_fll_pallets": 7,
    "high_demand_threshold": 50,
}

DEFAULT_FOOD_BANK_ID = "default"

STAFF_THRESHOLD_LABELS = {
    "critically_low": "Critically low",
    "low": "Low",
    "ok": "OK",
    "high": "High",
    "full": "Full",
}

LEGACY_CATALOG_TO_PLANNING_ID = {
    "Produce": "produce",
    "Protein": "protein",
    "Dairy": "dairy",
    "Grains": "grains",
    "Canned Goods": "canned",
    "Snacks": "snacks",
    "Beverages": "snacks",
    "Frozen": "protein",
    "Household": "personal_care",
}

PLANNING_CATEGORY_STORAGE = {
    "produce": "refrigerated",
    "protein": "shelf",
    "dairy": "refrigerated",
    "grains": "shelf",
    "gluten_free": "shelf",
    "canned": "shelf",
    "baby": "shelf",
    "diapers": "shelf",
    "personal_care": "shelf",
    "snacks": "shelf",
}

# Map planning categories to items.json catalog categories and/or explicit item IDs.
PLANNING_ITEM_SOURCES: dict[str, dict] = {
    "produce": {"catalog_categories": ["Produce"]},
    "protein": {"catalog_categories": ["Protein"], "item_ids": ["frozen-fish"]},
    "dairy": {"catalog_categories": ["Dairy"]},
    "grains": {"catalog_categories": ["Grains"]},
    "gluten_free": {
        "item_ids": ["rice-white", "rice-brown", "oatmeal", "peanut-butter", "tuna", "lentils-dry"]
    },
    "canned": {"catalog_categories": ["Canned Goods"]},
    "baby": {
        "item_ids": ["diapers"],
        "extra_examples": ["Baby formula", "Baby food pouches"],
    },
    "diapers": {"item_ids": ["diapers"], "extra_examples": ["Diaper wipes"]},
    "personal_care": {
        "item_ids": ["soap-bar", "toothpaste", "toilet-paper", "laundry-detergent"]
    },
    "snacks": {"catalog_categories": ["Snacks", "Beverages"]},
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

        CREATE TABLE IF NOT EXISTS categories (
            id TEXT PRIMARY KEY,
            food_bank_id TEXT NOT NULL DEFAULT 'default',
            display_name TEXT NOT NULL,
            donor_friendly_translation TEXT,
            sort_order INTEGER DEFAULT 0,
            active INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS client_requests (
            id TEXT PRIMARY KEY,
            client_id TEXT NOT NULL,
            food_bank_id TEXT NOT NULL DEFAULT 'default',
            category_id TEXT NOT NULL,
            requested_at TEXT NOT NULL,
            visit_week TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_client_requests_week
            ON client_requests (food_bank_id, visit_week);

        CREATE INDEX IF NOT EXISTS idx_client_requests_client_week
            ON client_requests (food_bank_id, visit_week, client_id);

        CREATE TABLE IF NOT EXISTS trend_snapshots (
            id TEXT PRIMARY KEY,
            food_bank_id TEXT NOT NULL,
            week_key TEXT NOT NULL,
            computed_at TEXT NOT NULL,
            total_clients INTEGER NOT NULL,
            metrics_json TEXT NOT NULL
        );

        CREATE UNIQUE INDEX IF NOT EXISTS idx_trend_snapshots_week
            ON trend_snapshots (food_bank_id, week_key);

        CREATE TABLE IF NOT EXISTS category_pledges (
            id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            round_id TEXT,
            category_id TEXT NOT NULL,
            donor_display_name TEXT NOT NULL,
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


def _seed_planning_categories(conn, food_bank_id: str = DEFAULT_FOOD_BANK_ID) -> None:
    count = conn.execute(
        "SELECT COUNT(*) FROM categories WHERE food_bank_id = ?",
        (food_bank_id,),
    ).fetchone()[0]
    if count > 0:
        return

    seed_rows = _read_json(CATEGORIES_FILE, [])
    for row in seed_rows:
        conn.execute(
            """INSERT INTO categories
               (id, food_bank_id, display_name, donor_friendly_translation, sort_order, active)
               VALUES (?, ?, ?, ?, ?, 1)""",
            (
                row["id"],
                food_bank_id,
                row["display_name"],
                row.get("donor_friendly_translation", ""),
                int(row.get("sort_order", 0)),
            ),
        )
    conn.commit()


def load() -> None:
    """Initialize database and load catalog."""
    global ITEMS, _items_mtime
    with get_conn() as conn:
        _init_schema(conn)
        _migrate_legacy_json(conn)
        _seed_planning_categories(conn)
        if conn.execute("SELECT COUNT(*) FROM kv_store WHERE key = 'app_settings'").fetchone()[0] == 0:
            _kv_set(conn, "app_settings", DEFAULT_APP_SETTINGS.copy())
            conn.commit()
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


def _normalize_threshold_categories(raw: dict) -> dict:
    normalized: dict[str, str] = {}
    planning_ids = set(_planning_category_seed().keys())
    for key, level in raw.items():
        if level not in STAFF_THRESHOLD_LEVELS:
            continue
        if key in planning_ids:
            normalized[key] = level
            continue
        mapped = LEGACY_CATALOG_TO_PLANNING_ID.get(key)
        if mapped and mapped in planning_ids:
            normalized[mapped] = level
    return normalized


def get_staff_thresholds() -> dict:
    with get_conn() as conn:
        thresholds = _kv_get(conn, "staff_thresholds", DEFAULT_STAFF_THRESHOLDS.copy())
    thresholds.setdefault("updated_at", "")
    thresholds.setdefault("categories", {})
    thresholds.setdefault("storage", {})
    thresholds["categories"] = _normalize_threshold_categories(thresholds.get("categories", {}))
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
    """Public category needs board — no household names or client counts."""
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
            "category_items": [],
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
            "category_items": [],
            "pledges": [],
            "categories": [],
            "donors": [],
            "trip": trip_context,
            "capacity_updated_at": thresholds.get("updated_at", ""),
            "state": "unpublished",
            "round_id": current_round_id(),
        }

    category_items = get_category_donor_board()
    tab_labels = sorted({row["display_name"] for row in category_items})
    pledges = get_category_pledges_for_round(statuses=["pledged", "received"])
    donor_names = sorted(
        {
            p["donor_display_name"]
            for p in pledges
            if p["donor_display_name"] != ANONYMOUS_DONOR_NAME
        }
    )

    if not category_items:
        state = "all_covered"
    else:
        state = "open"

    return {
        "published": published,
        "ready": True,
        "capacity_set": True,
        "all_covered": len(category_items) == 0,
        "items": [],
        "category_items": category_items,
        "pledges": pledges,
        "categories": tab_labels,
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


def visit_week_key(dt: datetime | None = None) -> str:
    if dt is None:
        dt = datetime.now(timezone.utc)
    year, week, _ = dt.isocalendar()
    return f"{year}-W{week:02d}"


def _week_key_to_date(week_key: str) -> datetime:
    year_str, week_str = week_key.split("-W", 1)
    return datetime.fromisocalendar(int(year_str), int(week_str), 1).replace(tzinfo=timezone.utc)


def prior_week_key(week_key: str) -> str:
    prior = _week_key_to_date(week_key) - timedelta(days=7)
    return visit_week_key(prior)


def rolling_week_keys(week_key: str, count: int) -> list[str]:
    keys: list[str] = []
    current = week_key
    for _ in range(max(0, count)):
        current = prior_week_key(current)
        keys.append(current)
    return keys


def get_app_settings() -> dict:
    with get_conn() as conn:
        settings = _kv_get(conn, "app_settings", DEFAULT_APP_SETTINGS.copy())
    for key, value in DEFAULT_APP_SETTINGS.items():
        settings.setdefault(key, value)
    settings["rolling_weeks"] = max(1, min(12, int(settings.get("rolling_weeks", 4) or 4)))
    settings["max_fll_pallets"] = max(6, min(8, int(settings.get("max_fll_pallets", 7) or 7)))
    settings["high_demand_threshold"] = max(
        20, min(90, int(settings.get("high_demand_threshold", 50) or 50))
    )
    return settings


def save_app_settings(settings: dict) -> dict:
    current = get_app_settings()
    if "agency_display_name" in settings:
        current["agency_display_name"] = str(settings["agency_display_name"]).strip()[:120]
    if "food_bank_id" in settings:
        current["food_bank_id"] = str(settings["food_bank_id"]).strip()[:64] or DEFAULT_FOOD_BANK_ID
    if "rolling_weeks" in settings:
        try:
            current["rolling_weeks"] = max(1, min(12, int(settings["rolling_weeks"])))
        except (TypeError, ValueError):
            pass
    if "max_fll_pallets" in settings:
        try:
            current["max_fll_pallets"] = max(6, min(8, int(settings["max_fll_pallets"])))
        except (TypeError, ValueError):
            pass
    if "high_demand_threshold" in settings:
        try:
            current["high_demand_threshold"] = max(20, min(90, int(settings["high_demand_threshold"])))
        except (TypeError, ValueError):
            pass
    with get_conn() as conn:
        _kv_set(conn, "app_settings", current)
        conn.commit()
    return current


def _planning_category_seed() -> dict[str, dict]:
    return {row["id"]: row for row in _read_json(CATEGORIES_FILE, [])}


def _example_items_for_planning(planning_id: str, limit: int = 8) -> list[dict]:
    source = PLANNING_ITEM_SOURCES.get(planning_id, {})
    item_map = get_item_map()
    items: list[dict] = []
    seen: set[str] = set()

    def add_item(item_id: str, name: str) -> None:
        cleaned = (name or "").strip()
        if not cleaned or cleaned in seen:
            return
        seen.add(cleaned)
        items.append({"id": item_id, "name": cleaned})

    for item_id in source.get("item_ids", []):
        catalog = item_map.get(item_id)
        if catalog:
            add_item(item_id, catalog.get("name", item_id))

    for catalog_category in source.get("catalog_categories", []):
        for item in get_items():
            if item.get("category") == catalog_category:
                add_item(item["id"], item.get("name", item["id"]))
                if len(items) >= limit:
                    break
        if len(items) >= limit:
            break

    for idx, extra in enumerate(source.get("extra_examples", [])):
        add_item(f"extra:{planning_id}:{idx}", extra)
        if len(items) >= limit:
            break

    return items[:limit]


def _enrich_planning_category(row: dict) -> dict:
    seed = _planning_category_seed().get(row["id"], {})
    example_items = seed.get("example_items")
    if not example_items:
        example_items = _example_items_for_planning(row["id"])
    return {
        **row,
        "description": seed.get("description", row.get("donor_friendly_translation", "")),
        "example_items": example_items,
    }


def get_planning_categories(food_bank_id: str | None = None, *, active_only: bool = True) -> list[dict]:
    fb_id = food_bank_id or get_app_settings()["food_bank_id"]
    query = """SELECT id, food_bank_id, display_name, donor_friendly_translation, sort_order, active
               FROM categories
               WHERE food_bank_id = ?"""
    params: list = [fb_id]
    if active_only:
        query += " AND active = 1"
    query += " ORDER BY sort_order, display_name"
    with get_conn() as conn:
        rows = conn.execute(query, params).fetchall()
    categories = [
        {
            "id": row["id"],
            "food_bank_id": row["food_bank_id"],
            "display_name": row["display_name"],
            "donor_friendly_translation": row["donor_friendly_translation"] or "",
            "sort_order": row["sort_order"],
            "active": bool(row["active"]),
        }
        for row in rows
    ]
    return [_enrich_planning_category(category) for category in categories]


def client_submitted_this_week(
    client_id: str,
    food_bank_id: str | None = None,
    week_key: str | None = None,
) -> bool:
    fb_id = food_bank_id or get_app_settings()["food_bank_id"]
    wk = week_key or visit_week_key()
    with get_conn() as conn:
        row = conn.execute(
            """SELECT 1 FROM client_requests
               WHERE food_bank_id = ? AND visit_week = ? AND client_id = ?
               LIMIT 1""",
            (fb_id, wk, client_id),
        ).fetchone()
    return row is not None


def add_client_requests(
    client_id: str,
    category_ids: list[str],
    food_bank_id: str | None = None,
    week_key: str | None = None,
) -> int:
    fb_id = food_bank_id or get_app_settings()["food_bank_id"]
    wk = week_key or visit_week_key()
    if client_submitted_this_week(client_id, fb_id, wk):
        raise ValueError("You already submitted requests for this week.")

    allowed = {cat["id"] for cat in get_planning_categories(fb_id, active_only=True)}
    unique_ids = []
    seen: set[str] = set()
    for category_id in category_ids:
        cid = (category_id or "").strip()
        if not cid or cid not in allowed or cid in seen:
            continue
        seen.add(cid)
        unique_ids.append(cid)

    if not unique_ids:
        raise ValueError("Select at least one category.")

    now = _utc_now()
    with get_conn() as conn:
        for category_id in unique_ids:
            conn.execute(
                """INSERT INTO client_requests
                   (id, client_id, food_bank_id, category_id, requested_at, visit_week)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (str(uuid.uuid4()), client_id, fb_id, category_id, now, wk),
            )
        conn.commit()
    return len(unique_ids)


def _category_counts_for_week(food_bank_id: str, week_key: str) -> dict[str, int]:
    with get_conn() as conn:
        total_row = conn.execute(
            """SELECT COUNT(DISTINCT client_id) AS total
               FROM client_requests
               WHERE food_bank_id = ? AND visit_week = ?""",
            (food_bank_id, week_key),
        ).fetchone()
        total_clients = int(total_row["total"] or 0)
        rows = conn.execute(
            """SELECT category_id, COUNT(DISTINCT client_id) AS client_count
               FROM client_requests
               WHERE food_bank_id = ? AND visit_week = ?
               GROUP BY category_id""",
            (food_bank_id, week_key),
        ).fetchall()
    counts = {row["category_id"]: int(row["client_count"]) for row in rows}
    return {"total_clients": total_clients, "counts": counts}


def _metrics_from_counts(
    categories: list[dict],
    total_clients: int,
    counts: dict[str, int],
) -> list[dict]:
    metrics: list[dict] = []
    for category in categories:
        client_count = counts.get(category["id"], 0)
        demand_pct = round(100 * client_count / total_clients, 1) if total_clients else 0.0
        metrics.append(
            {
                "category_id": category["id"],
                "display_name": category["display_name"],
                "client_count": client_count,
                "demand_pct": demand_pct,
            }
        )
    metrics.sort(key=lambda row: row["demand_pct"], reverse=True)
    return metrics


def _snapshot_metrics_map(snapshot: dict | None) -> dict[str, float]:
    if not snapshot:
        return {}
    metrics = snapshot.get("metrics") or json.loads(snapshot.get("metrics_json", "[]"))
    if isinstance(metrics, dict):
        return {k: float(v.get("demand_pct", 0)) for k, v in metrics.items()}
    return {row["category_id"]: float(row.get("demand_pct", 0)) for row in metrics}


def get_trend_snapshot(food_bank_id: str, week_key: str) -> dict | None:
    with get_conn() as conn:
        row = conn.execute(
            """SELECT id, food_bank_id, week_key, computed_at, total_clients, metrics_json
               FROM trend_snapshots
               WHERE food_bank_id = ? AND week_key = ?""",
            (food_bank_id, week_key),
        ).fetchone()
    if row is None:
        return None
    return {
        "id": row["id"],
        "food_bank_id": row["food_bank_id"],
        "week_key": row["week_key"],
        "computed_at": row["computed_at"],
        "total_clients": row["total_clients"],
        "metrics": json.loads(row["metrics_json"]),
    }


def save_trend_snapshot(food_bank_id: str, week_key: str, report: dict) -> dict:
    snapshot = {
        "id": str(uuid.uuid4()),
        "food_bank_id": food_bank_id,
        "week_key": week_key,
        "computed_at": report.get("computed_at", _utc_now()),
        "total_clients": report["total_clients"],
        "metrics_json": json.dumps(report["categories"]),
    }
    with get_conn() as conn:
        conn.execute(
            "DELETE FROM trend_snapshots WHERE food_bank_id = ? AND week_key = ?",
            (food_bank_id, week_key),
        )
        conn.execute(
            """INSERT INTO trend_snapshots
               (id, food_bank_id, week_key, computed_at, total_clients, metrics_json)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                snapshot["id"],
                snapshot["food_bank_id"],
                snapshot["week_key"],
                snapshot["computed_at"],
                snapshot["total_clients"],
                snapshot["metrics_json"],
            ),
        )
        conn.commit()
    return {
        **snapshot,
        "metrics": report["categories"],
    }


def _format_delta(value: float | None) -> str:
    if value is None:
        return "—"
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.1f}%"


def _build_insight(display_name: str, demand_pct: float, vs_prior: float | None, vs_rolling: float | None, rolling_weeks: int) -> str:
    parts = [f"{display_name}: {demand_pct:.0f}% of clients"]
    if vs_prior is not None:
        parts.append(f"({_format_delta(vs_prior)} vs last week)")
    if vs_rolling is not None:
        parts.append(f"({_format_delta(vs_rolling)} vs {rolling_weeks}-week avg)")
    return " ".join(parts)


def compute_weekly_trends(
    food_bank_id: str | None = None,
    week_key: str | None = None,
    *,
    rolling_weeks: int | None = None,
) -> dict:
    settings = get_app_settings()
    fb_id = food_bank_id or settings["food_bank_id"]
    wk = week_key or visit_week_key()
    window = rolling_weeks if rolling_weeks is not None else settings["rolling_weeks"]

    categories = get_planning_categories(fb_id, active_only=True)
    current = _category_counts_for_week(fb_id, wk)
    prior_wk = prior_week_key(wk)
    prior_snapshot = get_trend_snapshot(fb_id, prior_wk)
    if prior_snapshot is None and prior_wk != wk:
        prior_counts = _category_counts_for_week(fb_id, prior_wk)
        prior_metrics = _metrics_from_counts(
            categories,
            prior_counts["total_clients"],
            prior_counts["counts"],
        )
        prior_map = {row["category_id"]: row["demand_pct"] for row in prior_metrics}
    else:
        prior_map = _snapshot_metrics_map(prior_snapshot)

    rolling_keys = rolling_week_keys(wk, window)
    rolling_maps: list[dict[str, float]] = []
    for key in rolling_keys:
        snap = get_trend_snapshot(fb_id, key)
        if snap:
            rolling_maps.append(_snapshot_metrics_map(snap))
        else:
            hist = _category_counts_for_week(fb_id, key)
            if hist["total_clients"] > 0:
                hist_metrics = _metrics_from_counts(categories, hist["total_clients"], hist["counts"])
                rolling_maps.append({row["category_id"]: row["demand_pct"] for row in hist_metrics})

    base_metrics = _metrics_from_counts(categories, current["total_clients"], current["counts"])
    enriched: list[dict] = []
    insights: list[str] = []

    for row in base_metrics:
        prior_pct = prior_map.get(row["category_id"])
        vs_prior = round(row["demand_pct"] - prior_pct, 1) if prior_pct is not None else None

        rolling_values = [m.get(row["category_id"]) for m in rolling_maps if row["category_id"] in m]
        rolling_avg = round(sum(rolling_values) / len(rolling_values), 1) if rolling_values else None
        vs_rolling = round(row["demand_pct"] - rolling_avg, 1) if rolling_avg is not None else None

        insight = _build_insight(row["display_name"], row["demand_pct"], vs_prior, vs_rolling, window)
        enriched_row = {
            **row,
            "vs_prior_week_pct": vs_prior,
            "rolling_avg_pct": rolling_avg,
            "vs_rolling_avg_pct": vs_rolling,
            "insight": insight,
        }
        enriched.append(enriched_row)
        if row["client_count"] > 0:
            insights.append(insight)

    return {
        "food_bank_id": fb_id,
        "week_key": wk,
        "computed_at": _utc_now(),
        "total_clients": current["total_clients"],
        "rolling_weeks": window,
        "categories": enriched,
        "insights": insights[:6],
    }


def get_fll_pallets() -> dict:
    return _read_json(FLL_PALLETS_FILE, {})


def _priority_score(demand_pct: float, supply_urgency: int, vs_rolling_val: float) -> int:
    raw = demand_pct + (supply_urgency * 15) + max(0.0, vs_rolling_val)
    return int(round(raw))


def compute_order_plan(
    food_bank_id: str | None = None,
    week_key: str | None = None,
) -> dict:
    settings = get_app_settings()
    fb_id = food_bank_id or settings["food_bank_id"]
    wk = week_key or visit_week_key()
    max_pallets = settings["max_fll_pallets"]
    high_demand_threshold = settings["high_demand_threshold"]

    trends = compute_weekly_trends(fb_id, wk)
    thresholds = get_staff_thresholds()
    cat_levels = thresholds.get("categories", {})
    storage_levels = thresholds.get("storage", {})
    pallets = get_fll_pallets()
    trend_map = {row["category_id"]: row for row in trends["categories"]}

    categories_out: list[dict] = []
    for cat in get_planning_categories(fb_id, active_only=True):
        cid = cat["id"]
        trend = trend_map.get(cid, {})
        demand_pct = float(trend.get("demand_pct", 0) or 0)
        vs_rolling = trend.get("vs_rolling_avg_pct")
        vs_rolling_val = float(vs_rolling) if vs_rolling is not None else 0.0
        supply_level = cat_levels.get(cid, "ok")
        supply_urgency = CATEGORY_PRIORITY.get(supply_level, 2)
        skipped = supply_level in ("high", "full") and demand_pct <= high_demand_threshold
        priority_score = (
            0
            if skipped
            else _priority_score(demand_pct, supply_urgency, vs_rolling_val)
        )
        storage_type = PLANNING_CATEGORY_STORAGE.get(cid, "shelf")
        categories_out.append(
            {
                "category_id": cid,
                "display_name": cat["display_name"],
                "demand_pct": demand_pct,
                "client_count": int(trend.get("client_count", 0) or 0),
                "vs_rolling_avg_pct": vs_rolling,
                "supply_level": supply_level,
                "supply_label": STAFF_THRESHOLD_LABELS.get(supply_level, supply_level),
                "supply_urgency": supply_urgency,
                "priority_score": priority_score,
                "storage_type": storage_type,
                "storage_level": storage_levels.get(storage_type, "ok"),
                "skipped": skipped,
            }
        )

    categories_out.sort(
        key=lambda row: (row["priority_score"], row["demand_pct"]),
        reverse=True,
    )
    for index, row in enumerate(categories_out, start=1):
        row["priority_rank"] = index

    pallet_scores: list[dict] = []
    for pallet_id, pallet in pallets.items():
        mapped = pallet.get("planning_categories", [])
        scores = [
            c["priority_score"]
            for c in categories_out
            if c["category_id"] in mapped and not c["skipped"]
        ]
        pallet_scores.append(
            {
                "pallet_id": pallet_id,
                "display_name": pallet.get("display_name", pallet_id),
                "storage": pallet.get("storage", "shelf"),
                "planning_categories": mapped,
                "priority_score": max(scores) if scores else 0,
                "default_pallets": max(1, int(pallet.get("default_pallets", 1) or 1)),
            }
        )
    pallet_scores.sort(key=lambda row: row["priority_score"], reverse=True)

    fll_recommendations: list[dict] = []
    total_pallets = 0
    for pallet in pallet_scores:
        if pallet["priority_score"] <= 0 or total_pallets >= max_pallets:
            continue
        suggested = min(pallet["default_pallets"], max_pallets - total_pallets)
        if suggested <= 0:
            continue
        reasons: list[str] = []
        for cat_row in categories_out:
            if cat_row["category_id"] not in pallet["planning_categories"]:
                continue
            if cat_row["priority_score"] <= 0:
                continue
            reasons.append(
                f"{cat_row['display_name']} {cat_row['supply_label'].lower()}; "
                f"{cat_row['demand_pct']:.0f}% client demand"
            )
        fll_recommendations.append(
            {
                "pallet_id": pallet["pallet_id"],
                "display_name": pallet["display_name"],
                "action": "increase",
                "suggested_pallets": suggested,
                "priority_score": pallet["priority_score"],
                "storage": pallet["storage"],
                "reason": "; ".join(reasons[:2]) or "Priority gap",
            }
        )
        total_pallets += suggested

    for index, rec in enumerate(fll_recommendations, start=1):
        rec["priority_rank"] = index

    category_to_pallet: dict[str, str] = {}
    for rec in fll_recommendations:
        for cid in pallets.get(rec["pallet_id"], {}).get("planning_categories", []):
            category_to_pallet[cid] = rec["pallet_id"]
    for cat_row in categories_out:
        pallet_id = category_to_pallet.get(cat_row["category_id"])
        cat_row["fll_pallet_id"] = pallet_id
        cat_row["fll_pallet_name"] = (
            pallets.get(pallet_id, {}).get("display_name") if pallet_id else None
        )

    covered_by_fll = set(category_to_pallet.keys())
    donor_candidates: list[dict] = []
    for cat_row in categories_out:
        if cat_row["supply_level"] not in ("critically_low", "low"):
            continue
        if cat_row["storage_level"] == "full":
            continue
        cid = cat_row["category_id"]
        if cid in covered_by_fll and cat_row["supply_level"] != "critically_low":
            continue
        reason_parts: list[str] = []
        if cat_row["supply_level"] == "critically_low":
            reason_parts.append("Critically low supply")
        elif cat_row["supply_level"] == "low":
            reason_parts.append("Low supply")
        if cat_row["demand_pct"] > 0:
            reason_parts.append(f"{cat_row['demand_pct']:.0f}% client demand")
        if cid in covered_by_fll:
            reason_parts.append("May need donor top-up beyond FLL")
        donor_candidates.append(
            {
                "category_id": cid,
                "display_name": cat_row["display_name"],
                "supply_level": cat_row["supply_level"],
                "supply_label": cat_row["supply_label"],
                "demand_pct": cat_row["demand_pct"],
                "demand_signal": cat_row["demand_pct"] >= high_demand_threshold / 2,
                "reason": "; ".join(reason_parts) or "Staff priority",
            }
        )
    donor_candidates.sort(
        key=lambda row: (CATEGORY_PRIORITY.get(row["supply_level"], 0), row["demand_pct"]),
        reverse=True,
    )

    cooler_count = sum(
        1 for rec in fll_recommendations if rec.get("storage") == "refrigerated"
    )
    storage_warnings: list[str] = []
    if cooler_count >= 3:
        storage_warnings.append(
            f"{cooler_count} refrigerated pallets recommended — check cooler capacity."
        )

    return {
        "food_bank_id": fb_id,
        "week_key": wk,
        "computed_at": _utc_now(),
        "max_fll_pallets": max_pallets,
        "total_suggested_pallets": total_pallets,
        "categories": categories_out,
        "fll_recommendations": fll_recommendations,
        "donor_candidates": donor_candidates,
        "storage_warnings": storage_warnings,
        "capacity_set": capacity_is_set(),
    }


def get_category_donor_board() -> list[dict]:
    plan = compute_order_plan()
    settings = get_app_settings()
    signal_threshold = settings["high_demand_threshold"] / 2
    planning = {cat["id"]: cat for cat in get_planning_categories()}

    board: list[dict] = []
    pledged_ids = {
        p["category_id"]
        for p in get_category_pledges_for_round(statuses=["pledged", "received"])
    }
    for candidate in plan["donor_candidates"]:
        cat = planning.get(candidate["category_id"], {})
        board.append(
            {
                "category_id": candidate["category_id"],
                "display_name": candidate["display_name"],
                "donor_friendly_translation": cat.get("donor_friendly_translation", ""),
                "description": cat.get("description", ""),
                "example_items": cat.get("example_items", []),
                "supply_level": candidate["supply_level"],
                "supply_label": candidate["supply_label"],
                "demand_pct": candidate["demand_pct"],
                "demand_signal": candidate["demand_pct"] >= signal_threshold,
                "reason": candidate["reason"],
                "priority_score": CATEGORY_PRIORITY.get(candidate["supply_level"], 0),
                "pledged": candidate["category_id"] in pledged_ids,
            }
        )
    board.sort(key=lambda row: row["priority_score"], reverse=True)
    return board


def _category_pledge_row_dict(row) -> dict:
    planning = {cat["id"]: cat for cat in get_planning_categories()}
    cat = planning.get(row["category_id"], {})
    return {
        "id": row["id"],
        "created_at": row["created_at"],
        "round_id": row["round_id"],
        "donor_display_name": row["donor_display_name"],
        "category_id": row["category_id"],
        "category_name": cat.get("display_name", row["category_id"]),
        "note": row["note"] or "",
        "status": row["status"],
    }


def get_category_pledges_for_round(
    round_id: str | None = None,
    status: str = "pledged",
    *,
    statuses: list[str] | None = None,
) -> list[dict]:
    rid = round_id if round_id is not None else current_round_id()
    if statuses:
        placeholders = ",".join("?" * len(statuses))
        query = f"""SELECT id, created_at, round_id, category_id, donor_display_name, note, status
                    FROM category_pledges
                    WHERE round_id = ? AND status IN ({placeholders})
                    ORDER BY created_at DESC"""
        params: list = [rid, *statuses]
    else:
        query = """SELECT id, created_at, round_id, category_id, donor_display_name, note, status
                   FROM category_pledges
                   WHERE round_id = ? AND status = ?
                   ORDER BY created_at DESC"""
        params = [rid, status]
    with get_conn() as conn:
        rows = conn.execute(query, params).fetchall()
    return [_category_pledge_row_dict(row) for row in rows]


def get_all_category_pledges_for_round(round_id: str | None = None) -> list[dict]:
    rid = round_id if round_id is not None else current_round_id()
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT id, created_at, round_id, category_id, donor_display_name, note, status
               FROM category_pledges
               WHERE round_id = ?
               ORDER BY created_at DESC""",
            (rid,),
        ).fetchall()
    return [_category_pledge_row_dict(row) for row in rows]


def add_category_pledge(
    donor_display_name: str,
    category_id: str,
    note: str = "",
) -> dict:
    name = (donor_display_name or "").strip()
    if not name:
        name = ANONYMOUS_DONOR_NAME
    if len(name) > 100:
        raise ValueError("Donor name is too long.")

    cid = (category_id or "").strip()
    allowed = {cat["id"] for cat in get_planning_categories(active_only=True)}
    if cid not in allowed:
        raise ValueError("Invalid category.")

    trip = get_trip_settings()
    if not trip.get("community_published"):
        raise ValueError("Community board is not open for pledges yet.")

    needs = get_community_needs(include_unpublished=True)
    if not needs.get("ready"):
        raise ValueError("Supply levels have not been set yet.")

    open_ids = {row["category_id"] for row in needs.get("category_items", [])}
    if cid not in open_ids:
        raise ValueError("This category is not on the needs board.")

    note = (note or "").strip()[:500]
    pledge = {
        "id": str(uuid.uuid4()),
        "created_at": _utc_now(),
        "round_id": current_round_id(),
        "donor_display_name": name,
        "category_id": cid,
        "note": note,
        "status": "pledged",
    }
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO category_pledges
               (id, created_at, round_id, category_id, donor_display_name, note, status)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                pledge["id"],
                pledge["created_at"],
                pledge["round_id"],
                pledge["category_id"],
                pledge["donor_display_name"],
                pledge["note"],
                pledge["status"],
            ),
        )
        conn.commit()
    planning = {cat["id"]: cat for cat in get_planning_categories()}
    return {
        **pledge,
        "category_name": planning.get(cid, {}).get("display_name", cid),
    }


def update_category_pledge_status(pledge_id: str, status: str) -> dict | None:
    if status not in ("pledged", "received", "cancelled"):
        raise ValueError("Invalid pledge status.")
    with get_conn() as conn:
        row = conn.execute(
            """SELECT id, created_at, round_id, category_id, donor_display_name, note, status
               FROM category_pledges WHERE id = ?""",
            (pledge_id,),
        ).fetchone()
        if row is None:
            return None
        conn.execute(
            "UPDATE category_pledges SET status = ? WHERE id = ?",
            (status, pledge_id),
        )
        conn.commit()
    updated = _category_pledge_row_dict(row)
    updated["status"] = status
    return updated

"""Database connections: local SQLite for dev, Turso HTTP for production."""

from __future__ import annotations

import json
import os
import sqlite3
import urllib.error
import urllib.request
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

BASE_DIR = Path(__file__).resolve().parent
LOCAL_DB_PATH = Path(os.environ.get("DATABASE_PATH", str(BASE_DIR / "data" / "food_bank.db")))

TURSO_DATABASE_URL = os.environ.get("TURSO_DATABASE_URL", "").strip()
TURSO_AUTH_TOKEN = os.environ.get("TURSO_AUTH_TOKEN", "").strip()
TURSO_HTTP_URL = os.environ.get("TURSO_HTTP_URL", "").strip()


def uses_turso() -> bool:
    return bool(TURSO_AUTH_TOKEN and (TURSO_DATABASE_URL or TURSO_HTTP_URL))


class RowAdapter:
    """Dict-like row for tuple results."""

    __slots__ = ("_values", "_keys")

    def __init__(self, values: tuple[Any, ...], keys: list[str]) -> None:
        self._values = values
        self._keys = keys

    def __getitem__(self, key: str | int) -> Any:
        if isinstance(key, str):
            return self._values[self._keys.index(key)]
        return self._values[key]

    def keys(self) -> list[str]:
        return list(self._keys)


def _encode_arg(value: Any) -> dict[str, str]:
    if value is None:
        return {"type": "null"}
    if isinstance(value, bool):
        return {"type": "integer", "value": "1" if value else "0"}
    if isinstance(value, int):
        return {"type": "integer", "value": str(value)}
    if isinstance(value, float):
        return {"type": "float", "value": str(value)}
    return {"type": "text", "value": str(value)}


def _decode_cell(cell: Any) -> Any:
    if cell is None:
        return None
    if isinstance(cell, dict):
        cell_type = cell.get("type")
        if cell_type == "null":
            return None
        value = cell.get("value")
        if cell_type == "integer":
            try:
                return int(value)
            except (TypeError, ValueError):
                return 0
        if cell_type == "float":
            try:
                return float(value)
            except (TypeError, ValueError):
                return 0.0
        return value
    return cell


def _turso_pipeline_url() -> str:
    if TURSO_HTTP_URL:
        url = TURSO_HTTP_URL.rstrip("/")
    else:
        url = TURSO_DATABASE_URL.strip()
        if url.startswith("libsql://"):
            url = "https://" + url[len("libsql://") :]
        elif not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        url = url.rstrip("/")
    if not url.endswith("/v2/pipeline"):
        url = url + "/v2/pipeline"
    return url


class _TursoHttpCursor:
    def __init__(self, cols: list[str], rows: list[tuple[Any, ...]]) -> None:
        self.description = [(name, None, None, None, None, None, None) for name in cols]
        self._cols = cols
        self._rows = rows
        self._index = 0

    def fetchone(self) -> Any:
        if self._index >= len(self._rows):
            return None
        row = self._rows[self._index]
        self._index += 1
        if not self._cols:
            return row
        return RowAdapter(row, self._cols)

    def fetchall(self) -> list[Any]:
        rest = self._rows[self._index :]
        self._index = len(self._rows)
        if not self._cols:
            return list(rest)
        return [RowAdapter(row, self._cols) for row in rest]


class _TursoHttpConnection:
    """Turso SQL over HTTP — no native libsql (avoids gunicorn worker deadlocks)."""

    def __init__(self, pipeline_url: str, auth_token: str) -> None:
        self._pipeline_url = pipeline_url
        self._auth_token = auth_token

    def _pipeline(self, requests: list[dict]) -> list[dict]:
        payload = json.dumps({"requests": requests}).encode("utf-8")
        req = urllib.request.Request(
            self._pipeline_url,
            data=payload,
            headers={
                "Authorization": f"Bearer {self._auth_token}",
                "Content-Type": "application/json",
                "User-Agent": "FoodBankOrderApp/1.0",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Turso HTTP {exc.code}: {body[:500]}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Turso connection failed: {exc.reason}") from exc

        results = data.get("results", [])
        for item in results:
            if item.get("type") == "error":
                raise RuntimeError(f"Turso query error: {item.get('error', item)}")
        return results

    @staticmethod
    def _parse_execute_result(result_item: dict) -> tuple[list[str], list[tuple[Any, ...]]]:
        response = result_item.get("response", {})
        payload = response.get("result", {})
        cols = [col.get("name", f"col{i}") for i, col in enumerate(payload.get("cols", []))]
        rows: list[tuple[Any, ...]] = []
        for raw_row in payload.get("rows", []):
            if isinstance(raw_row, list):
                rows.append(tuple(_decode_cell(cell) for cell in raw_row))
            else:
                rows.append((raw_row,))
        return cols, rows

    def execute(self, sql: str, params: tuple[Any, ...] | list[Any] = ()) -> _TursoHttpCursor:
        stmt: dict[str, Any] = {"sql": sql}
        if params:
            stmt["args"] = [_encode_arg(p) for p in params]
        results = self._pipeline(
            [
                {"type": "execute", "stmt": stmt},
                {"type": "close"},
            ]
        )
        cols, rows = self._parse_execute_result(results[0])
        return _TursoHttpCursor(cols, rows)

    def executescript(self, sql: str) -> None:
        statements = [part.strip() for part in sql.split(";") if part.strip()]
        if not statements:
            return
        requests = [{"type": "execute", "stmt": {"sql": stmt}} for stmt in statements]
        requests.append({"type": "close"})
        self._pipeline(requests)

    def commit(self) -> None:
        return None

    def close(self) -> None:
        return None


class _CursorWrapper:
    def __init__(self, cursor: Any, sqlite_native: bool) -> None:
        self._cursor = cursor
        self._sqlite_native = sqlite_native
        self._columns: list[str] | None = None

    def fetchone(self) -> Any:
        return self._wrap(self._cursor.fetchone())

    def fetchall(self) -> list[Any]:
        return [self._wrap(row) for row in self._cursor.fetchall()]

    def _wrap(self, row: Any) -> Any:
        if row is None:
            return None
        if self._sqlite_native:
            return row
        if self._columns is None and getattr(self._cursor, "description", None):
            self._columns = [col[0] for col in self._cursor.description]
        if self._columns and not hasattr(row, "keys"):
            if isinstance(row, dict):
                return row
            return RowAdapter(tuple(row), self._columns)
        return row


class _ConnectionWrapper:
    def __init__(self, conn: Any, sqlite_native: bool) -> None:
        self._conn = conn
        self._sqlite_native = sqlite_native

    def execute(self, sql: str, params: tuple[Any, ...] | list[Any] = ()) -> _CursorWrapper:
        return _CursorWrapper(self._conn.execute(sql, params), self._sqlite_native)

    def executescript(self, sql: str) -> None:
        self._conn.executescript(sql)

    def commit(self) -> None:
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> _ConnectionWrapper:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


@contextmanager
def get_conn() -> Iterator[_ConnectionWrapper]:
    """Yield a DB connection (Turso HTTP when configured, else local SQLite)."""
    if uses_turso():
        raw = _TursoHttpConnection(_turso_pipeline_url(), TURSO_AUTH_TOKEN)
        conn = _ConnectionWrapper(raw, sqlite_native=False)
    else:
        LOCAL_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        raw = sqlite3.connect(LOCAL_DB_PATH)
        raw.row_factory = sqlite3.Row
        conn = _ConnectionWrapper(raw, sqlite_native=True)

    try:
        yield conn
    finally:
        conn.close()


def backend_label() -> str:
    return "turso-http" if uses_turso() else "sqlite"

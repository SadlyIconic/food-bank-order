"""Database connections: local SQLite for dev, Turso (libsql) for production."""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

BASE_DIR = Path(__file__).resolve().parent
LOCAL_DB_PATH = Path(os.environ.get("DATABASE_PATH", str(BASE_DIR / "data" / "food_bank.db")))

TURSO_DATABASE_URL = os.environ.get("TURSO_DATABASE_URL", "").strip()
TURSO_AUTH_TOKEN = os.environ.get("TURSO_AUTH_TOKEN", "").strip()


def uses_turso() -> bool:
    return bool(TURSO_DATABASE_URL and TURSO_AUTH_TOKEN)


class RowAdapter:
    """Dict-like row for Turso/libsql tuple results."""

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
    """Yield a DB connection (Turso remote when configured, else local SQLite)."""
    if uses_turso():
        try:
            import libsql
        except ImportError as exc:
            raise RuntimeError(
                "TURSO_DATABASE_URL and TURSO_AUTH_TOKEN are set but libsql is not installed. "
                "Add libsql to requirements.txt and redeploy."
            ) from exc

        raw = libsql.connect(database=TURSO_DATABASE_URL, auth_token=TURSO_AUTH_TOKEN)
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
    return "turso" if uses_turso() else "sqlite"

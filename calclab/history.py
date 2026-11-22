"""SQLite-backed calculation history."""
import sqlite3
import threading
from datetime import datetime, timezone


class HistoryStore:
    """Stores every successful calculation so the UI can list it and ``ans`` can reuse it."""

    def __init__(self, path):
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS history (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   expression TEXT NOT NULL,
                   display TEXT NOT NULL,
                   value REAL NOT NULL,
                   created_at TEXT NOT NULL
               )"""
        )
        self._conn.commit()

    def add(self, expression, display, value):
        stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with self._lock:
            cur = self._conn.execute(
                "INSERT INTO history (expression, display, value, created_at) VALUES (?, ?, ?, ?)",
                (expression, display, float(value), stamp),
            )
            self._conn.commit()
            return cur.lastrowid

    def recent(self, limit=20):
        with self._lock:
            rows = self._conn.execute(
                "SELECT id, expression, display, value, created_at FROM history ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def last_value(self):
        with self._lock:
            row = self._conn.execute("SELECT value FROM history ORDER BY id DESC LIMIT 1").fetchone()
        return None if row is None else row["value"]

    def variables(self):
        """Variables made available to expressions: ``ans`` is the previous result."""
        last = self.last_value()
        return {} if last is None else {"ans": last}

    def clear(self):
        with self._lock:
            self._conn.execute("DELETE FROM history")
            self._conn.commit()

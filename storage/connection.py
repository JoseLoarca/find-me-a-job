import sqlite3
from contextlib import contextmanager


class Database:
    def __init__(self, path: str):
        self._conn = sqlite3.connect(
            path,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        self._conn.row_factory = sqlite3.Row  # Get dicts instead of tuples
        self._conn.execute("PRAGMA foreign_keys = ON")  # Enforce foreign keys, do I need this?

    @contextmanager
    def cursor(self):
        cur = self._conn.cursor()  # Fresh cursor on every conn
        try:
            yield cur
            self._conn.commit()  # If everything is ok, commit automatically
        except Exception:
            self._conn.rollback()  # Else, rollback
            raise
        finally:
            cur.close()  # Always close the cursor

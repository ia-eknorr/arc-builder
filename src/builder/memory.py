"""SQLite read/write helpers for arc-builder memory."""
from __future__ import annotations

import aiosqlite

DB_PATH = "~/.arc-builder/memory.db"


async def get_db(path: str = DB_PATH) -> aiosqlite.Connection:
    """Open a WAL-mode connection to the memory database."""
    import os

    db = await aiosqlite.connect(os.path.expanduser(path))
    await db.execute("PRAGMA journal_mode=WAL")
    db.row_factory = aiosqlite.Row
    return db

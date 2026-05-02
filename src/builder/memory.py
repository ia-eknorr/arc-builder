"""SQLite read/write helpers for arc-builder memory."""
from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

import aiosqlite

DB_PATH = "~/.arc-builder/memory.db"


def db_path() -> Path:
    """Return the expanded path to the memory database."""
    return Path(os.path.expanduser(DB_PATH))


@asynccontextmanager
async def open_db() -> AsyncIterator[aiosqlite.Connection]:
    """Open a WAL-mode connection to the memory database."""
    db = await aiosqlite.connect(db_path())
    await db.execute("PRAGMA journal_mode=WAL")
    db.row_factory = aiosqlite.Row
    try:
        yield db
    finally:
        await db.close()


async def get_projects() -> list[dict]:
    """Return all projects from the registry."""
    async with open_db() as db:
        async with db.execute("SELECT * FROM projects ORDER BY name") as cur:
            return [dict(row) async for row in cur]


async def get_open_issues() -> list[dict]:
    """Return all issues not in a terminal state."""
    async with open_db() as db:
        async with db.execute(
            "SELECT * FROM issues WHERE status NOT IN ('merged','closed') ORDER BY created_at"
        ) as cur:
            return [dict(row) async for row in cur]


async def get_unread_notifications() -> list[dict]:
    """Return unread worker notifications."""
    async with open_db() as db:
        async with db.execute(
            "SELECT * FROM notifications WHERE read=0 ORDER BY created_at"
        ) as cur:
            return [dict(row) async for row in cur]


async def get_checkpoint(issue_url: str) -> dict | None:
    """Return the checkpoint for a given issue URL, or None."""
    async with open_db() as db:
        async with db.execute(
            "SELECT * FROM checkpoints WHERE issue_url=?", (issue_url,)
        ) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def upsert_checkpoint(issue_url: str, stage: str, **kwargs: str | int | None) -> None:
    """Insert or replace a checkpoint row."""
    fields = {"issue_url": issue_url, "stage": stage, **kwargs}
    cols = ", ".join(fields)
    placeholders = ", ".join("?" * len(fields))
    async with open_db() as db:
        await db.execute(
            f"INSERT OR REPLACE INTO checkpoints ({cols}) VALUES ({placeholders})",
            list(fields.values()),
        )
        await db.commit()


async def update_issue_status(project: str, issue_number: int, status: str, **kwargs: str | int | None) -> None:
    """Update the status (and optional fields) of a tracked issue."""
    fields = {"status": status, "updated_at": "datetime('now')", **kwargs}
    set_clause = ", ".join(f"{k}=?" for k in fields)
    async with open_db() as db:
        await db.execute(
            f"UPDATE issues SET {set_clause} WHERE project=? AND issue_number=?",
            [*fields.values(), project, issue_number],
        )
        await db.commit()


async def write_notification(issue_url: str, project: str, event: str, message: str, pr_number: int | None = None) -> None:
    """Write a worker completion or question notification."""
    async with open_db() as db:
        await db.execute(
            "INSERT INTO notifications (issue_url, project, pr_number, event, message) VALUES (?,?,?,?,?)",
            (issue_url, project, pr_number, event, message),
        )
        await db.commit()


async def get_relevant_decisions(project: str, limit: int = 20) -> list[dict]:
    """Return recent decisions for a project plus global decisions."""
    async with open_db() as db:
        async with db.execute(
            "SELECT * FROM decisions WHERE project=? OR project IS NULL ORDER BY created_at DESC LIMIT ?",
            (project, limit),
        ) as cur:
            return [dict(row) async for row in cur]

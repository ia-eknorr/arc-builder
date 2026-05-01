"""Typed wrappers around the gh CLI."""
from __future__ import annotations


async def get_issue(repo: str, number: int) -> dict:
    """Fetch a GitHub issue as a dict via gh CLI."""
    raise NotImplementedError

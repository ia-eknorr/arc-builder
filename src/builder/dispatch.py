"""Worker dispatch via arc IPC."""
from __future__ import annotations


async def fire(socket_path: str, message: dict) -> None:
    """Dispatch via arc IPC with no_wait=True. Returns after daemon ack."""
    raise NotImplementedError

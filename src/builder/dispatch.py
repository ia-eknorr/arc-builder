"""Worker dispatch via arc IPC."""
from __future__ import annotations

import asyncio
import json
import os
import struct
from pathlib import Path

from builder.github import get_issue
from builder.memory import get_checkpoint, get_relevant_decisions, update_issue_status


def _arc_socket_path() -> str:
    """Return the arc daemon socket path."""
    return os.path.expanduser(os.environ.get("ARC_SOCKET", "~/.arc/arc.sock"))


async def _ipc_request(socket_path: str, message: dict) -> dict:
    """Send a request to the arc daemon and return the response."""
    reader, writer = await asyncio.open_unix_connection(socket_path)
    try:
        data = json.dumps(message).encode()
        writer.write(struct.pack(">I", len(data)) + data)
        await writer.drain()
        length_bytes = await reader.readexactly(4)
        length = struct.unpack(">I", length_bytes)[0]
        body = await reader.readexactly(length)
        return json.loads(body.decode())
    finally:
        writer.close()
        await writer.wait_closed()


def _build_worker_prompt(issue: dict, checkpoint: dict | None, decisions: list[dict]) -> str:
    """Build the full prompt string for a worker dispatch."""
    lines = [
        f"Issue: {issue['url']}",
        f"Repo: {issue['repo']}",
        f"Title: {issue['title']}",
        "",
        issue["body"],
    ]

    if checkpoint and checkpoint["stage"] not in ("complete",):
        lines += [
            "",
            f"Resume from checkpoint: stage={checkpoint['stage']}",
        ]
        if checkpoint.get("worktree"):
            lines.append(f"Worktree: {checkpoint['worktree']}")
        if checkpoint.get("pr_number"):
            lines.append(f"PR: #{checkpoint['pr_number']}")

    if decisions:
        lines += ["", "Relevant past decisions:"]
        for d in decisions:
            scope = d["project"] or "global"
            lines.append(f"- [{scope}] {d['decision']}")
            if d.get("rationale"):
                lines.append(f"  Rationale: {d['rationale']}")

    return "\n".join(lines)


async def fire(issue_url: str) -> None:
    """Dispatch a worker for the given issue URL via arc IPC (non-blocking).

    Fetches issue context and relevant decisions, builds the worker prompt,
    sends a no_wait dispatch to the arc daemon, and marks the issue as dispatched.
    """
    issue = await get_issue(issue_url)
    checkpoint = await get_checkpoint(issue_url)
    decisions = await get_relevant_decisions(issue["project"])
    prompt = _build_worker_prompt(issue, checkpoint, decisions)

    socket_path = _arc_socket_path()
    response = await _ipc_request(socket_path, {
        "prompt": prompt,
        "agent": "worker",
        "source": "cron",
        "no_wait": True,
    })

    if response.get("status") != "ok":
        raise RuntimeError(f"arc IPC error: {response.get('error')}")

    await update_issue_status(issue["project"], issue["number"], "dispatched")

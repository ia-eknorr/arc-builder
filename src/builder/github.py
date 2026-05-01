"""Typed wrappers around the gh CLI."""
from __future__ import annotations

import asyncio
import json
import re


async def _gh(*args: str) -> str:
    """Run a gh CLI command and return stdout."""
    proc = await asyncio.create_subprocess_exec(
        "gh", *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args)} failed: {stderr.decode().strip()}")
    return stdout.decode().strip()


def _parse_repo_from_url(url: str) -> tuple[str, int]:
    """Extract 'owner/repo' and issue number from a GitHub issue URL."""
    match = re.search(r"github\.com/([^/]+/[^/]+)/issues/(\d+)", url)
    if not match:
        raise ValueError(f"Cannot parse GitHub issue URL: {url}")
    return match.group(1), int(match.group(2))


def _repo_to_project(repo: str) -> str:
    """Convert 'owner/repo' to a short project name (the repo part)."""
    return repo.split("/")[-1]


async def get_issue(url: str) -> dict:
    """Fetch a GitHub issue as a normalized dict.

    Returns keys: url, repo, project, number, title, body.
    """
    repo, number = _parse_repo_from_url(url)
    raw = await _gh("issue", "view", str(number), "--repo", repo, "--json",
                    "number,title,body,url")
    data = json.loads(raw)
    return {
        "url": url,
        "repo": repo,
        "project": _repo_to_project(repo),
        "number": data["number"],
        "title": data["title"],
        "body": data.get("body") or "",
    }


async def create_issue(repo: str, title: str, body: str) -> dict:
    """Create a GitHub issue and return its number and URL."""
    raw = await _gh("issue", "create", "--repo", repo,
                    "--title", title, "--body", body,
                    "--json", "number,url")
    return json.loads(raw)


async def get_pr_status(repo: str, pr_number: int) -> str:
    """Return the PR state: open, closed, or merged."""
    raw = await _gh("pr", "view", str(pr_number), "--repo", repo, "--json", "state,merged")
    data = json.loads(raw)
    if data.get("merged"):
        return "merged"
    return data.get("state", "unknown").lower()

"""arc-builder CLI."""
from __future__ import annotations

import typer

app = typer.Typer(name="arc-builder", help="Multi-agent software development system.")


@app.command()
def setup() -> None:
    """Initialize ~/.arc-builder/, create database, register agents."""
    typer.echo("arc-builder setup -- not yet implemented")


@app.command()
def dispatch(issue_url: str = typer.Argument(..., help="GitHub issue URL")) -> None:
    """Dispatch a worker agent for the given issue (non-blocking)."""
    import asyncio
    from builder.dispatch import fire
    asyncio.run(fire(issue_url))
    typer.echo(f"Worker dispatched for {issue_url}")


@app.command()
def status() -> None:
    """Show open issues and worker checkpoint stages."""
    typer.echo("status -- not yet implemented")


@app.command()
def cleanup(issue_url: str = typer.Argument(..., help="GitHub issue URL")) -> None:
    """Manually clean up a worktree for the given issue."""
    typer.echo(f"cleanup {issue_url} -- not yet implemented")


@app.command()
def notify() -> None:
    """Print unread worker notifications and mark them read. Produces no output if none."""
    import asyncio
    from builder.memory import get_unread_notifications, open_db

    async def _run() -> None:
        rows = await get_unread_notifications()
        if not rows:
            return
        lines = []
        for r in rows:
            line = f"[{r['project']}] {r['event']}: {r['message']}"
            if r.get("pr_number"):
                line += f" (PR #{r['pr_number']})"
            lines.append(line)
        typer.echo("\n".join(lines))
        async with open_db() as db:
            ids = [r["id"] for r in rows]
            await db.execute(
                f"UPDATE notifications SET read=1 WHERE id IN ({','.join('?' * len(ids))})",
                ids,
            )
            await db.commit()

    asyncio.run(_run())


memory_app = typer.Typer(help="SQLite memory commands.")
app.add_typer(memory_app, name="memory")


@memory_app.command("show")
def memory_show() -> None:
    """Dump SQLite summary: projects, open issues, recent decisions."""
    typer.echo("memory show -- not yet implemented")


@memory_app.command("add-project")
def memory_add_project() -> None:
    """Interactively add a project to the registry."""
    typer.echo("memory add-project -- not yet implemented")


if __name__ == "__main__":
    app()

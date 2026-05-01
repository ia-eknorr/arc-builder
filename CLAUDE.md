# CLAUDE.md -- arc-builder project

Read `.design/design.md` for the full design document before starting any work.

## What this is

arc-builder is a multi-agent software development system built on top of arc.
A PM agent (Discord) creates GitHub issues from your requests and dispatches
silent background worker agents to implement them. You interact with one thing:
the PM. Workers are invisible.

## Tech

- Python 3.11+, src layout, hatchling build
- typer (CLI), aiosqlite (async SQLite access)
- Depends on arc for dispatch (acpx), Discord bot, cron, and IPC
- pytest, ruff for dev

## Rules

- No em dashes. Not as `--` either. Use a comma, colon, or rewrite.
- No emoji.
- Follow the design doc phases in order. Do not skip ahead.
- Write tests alongside implementation, not after.
- Use async/await throughout.
- Type hints on all function signatures.
- Docstrings on all public functions.

## File structure

```
src/builder/
  __init__.py
  cli.py        # arc-builder CLI (typer)
  dispatch.py   # ipc.request wrapper + worker prompt builder
  memory.py     # SQLite read/write helpers (aiosqlite)
  github.py     # gh CLI wrappers (typed)
agents/
  pm/           # PM agent identity files
  worker/       # Worker agent identity files
  shared/       # STANDARDS.md, PROJECTS.md
memory/
  schema.sql    # canonical schema
scripts/
  setup.sh      # bootstrap ~/.arc-builder/
```

## Testing

- pytest with asyncio mode
- Mock gh CLI with monkeypatched subprocess calls
- Mock SQLite with in-memory databases (`:memory:`)
- Mock arc IPC with mock sockets
- Target 80%+ coverage on core modules (dispatch, memory, github)

# Project registry

One entry per project. Keep in sync with the SQLite projects table.
Workers read this file to understand project conventions before starting work.

## arc

- repo: ia-eknorr/arc
- workspace: /workspace/arc
- language: Python 3.11
- main_branch: main
- ci_tool: github-actions (lint.yml, test.yml)
- conventions: src layout, hatchling, typer CLI, pytest-asyncio, ruff
- notes: Read CLAUDE.md in workspace before touching any code.

---

(Add projects here as they are onboarded via `arc-builder memory add-project`)

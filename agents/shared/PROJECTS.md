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

## fitness-coach

- repo: ia-eknorr/fitness-coach
- workspace: /workspace/fitness-coach
- language: markdown / agent identity files
- main_branch: main
- ci_tool: none
- conventions: changes are to agent identity files (AGENTS.md, SOUL.md,
  IDENTITY.md, TOOLS.md, etc.) and supporting markdown. No test suite, no
  build step. Read CLAUDE.md in workspace before touching anything.
- notes: Acceptance criteria must describe behavioral change, not file change.
  State what the agent will do or know differently after the fix. The quality
  bar is semantic accuracy. A worker with no CI to wait on should verify its
  edit by re-reading the modified section and confirming it accurately reflects
  the intended behavior before opening a PR.

---

(Add projects here as they are onboarded via `arc-builder memory add-project`)

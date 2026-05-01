# Worker Tools and Workflow

## MANDATORY: read the target project's AGENTS.md

Immediately after step 2 below, before making any code changes, read the
AGENTS.md (or CLAUDE.md) in the target project workspace. Treat it with the
same authority as this file. If it conflicts with this file on project-specific
conventions, the target project's file wins.

## Worktree workflow

Execute these steps in order. Write checkpoints as indicated.

**Step 1: Read the issue**
```
gh issue view <number> --repo <repo> --comments
```
Understand the background, acceptance criteria, and out-of-scope list before
proceeding.

**Step 2: Fetch and create worktree**
```
git -C <workspace> fetch origin

# Try creating new branch (fails if branch already exists from a crash)
git -C <workspace> worktree add \
  -b worker/issue-<number> \
  ~/.arc-builder/worktrees/<repo>-issue-<number> \
2>/dev/null \
|| \
# Branch already exists: check it out into a new worktree
git -C <workspace> worktree add \
  ~/.arc-builder/worktrees/<repo>-issue-<number> \
  worker/issue-<number>
```

**Step 3: Write checkpoint**
```
sqlite3 ~/.arc-builder/memory.db \
  "INSERT OR REPLACE INTO checkpoints
   VALUES ('<issue-url>', 'worktree_created',
           '~/.arc-builder/worktrees/<repo>-issue-<number>',
           'worker/issue-<number>', NULL, datetime('now'))"
```

**Step 4: Read project AGENTS.md**
Read <workspace>/AGENTS.md (or CLAUDE.md) in full before touching any code.

**Step 5: Implement**
Work in the worktree. Follow STANDARDS.md and the project's AGENTS.md.
Run only tests related to the files you changed.

**Step 6: Checkpoint after local tests pass**
```
sqlite3 ~/.arc-builder/memory.db \
  "UPDATE checkpoints SET stage='tests_passed', updated_at=datetime('now')
   WHERE issue_url='<issue-url>'"
```

**Step 7: Rebase before opening PR**
```
git -C ~/.arc-builder/worktrees/<repo>-issue-<number> \
  rebase origin/<main_branch>
```
If rebase conflicts touch files you did not modify, post @pm: and exit.

**Step 8: Open PR**
```
cd ~/.arc-builder/worktrees/<repo>-issue-<number>
gh pr create \
  --title "<title under 70 chars>" \
  --body "$(cat <<'EOF'
## Why
<one paragraph: the problem this solves>

## Approach
<one paragraph: what changed and why this approach>

Closes #<issue-number>
EOF
)" \
  --repo <repo>
```

**Step 9: Checkpoint with PR number**
```
sqlite3 ~/.arc-builder/memory.db \
  "UPDATE checkpoints
   SET stage='pr_open', pr_number=<pr-number>, updated_at=datetime('now')
   WHERE issue_url='<issue-url>'"
```

**Step 10: Wait for CI**
```
gh pr checks <pr-number> --repo <repo> --watch
```
This blocks until all checks pass or fail.

If CI fails:
- Read the failure: `gh run view --log-failed`
- Fix the root cause in the worktree
- `git add -A && git commit -m "<fix: description>" && git push`
- Return to step 10

If the same test fails again after your fix:
- Post on the issue: `gh issue comment <number> --repo <repo> --body "@pm: CI failing on <test> after fix attempt. Logs: <summary>. Options: A) skip this test, B) investigate flakiness. Leaning B."`
- Write checkpoint stage='ci_blocked'
- Exit

**Step 11: Write completion notification**
```
sqlite3 ~/.arc-builder/memory.db \
  "INSERT INTO notifications
   (issue_url, project, pr_number, event, message, read)
   VALUES ('<issue-url>', '<project>', <pr-number>, 'pr_ready',
           'CI passed. PR #<pr-number> ready for review.', 0)"
sqlite3 ~/.arc-builder/memory.db \
  "UPDATE checkpoints SET stage='complete', updated_at=datetime('now')
   WHERE issue_url='<issue-url>'"
```

**Step 12: Remove worktree**
```
git -C <workspace> worktree remove \
  ~/.arc-builder/worktrees/<repo>-issue-<number> --force
```
Do NOT delete the branch here. The PR is still open. Branch cleanup happens
after you merge, via the weekly cleanup cron.

## Recovery from checkpoint

When re-dispatched with a checkpoint:
1. Read the checkpoint: `sqlite3 ~/.arc-builder/memory.db "SELECT * FROM checkpoints WHERE issue_url='<url>'"`
2. Check if the worktree still exists: `ls ~/.arc-builder/worktrees/<repo>-issue-<number>`
3. Skip steps already completed based on the checkpoint stage.
4. If stage='pr_open': check PR status with `gh pr checks <N> --repo <repo>` and proceed from step 10.
5. If stage='ci_blocked': read the issue for PM's decision, then implement and continue from step 5.

## Available tools

- git, gh (GitHub CLI)
- sqlite3 ~/.arc-builder/memory.db (checkpoints and notifications tables only)
- Standard Unix tools: bash, find, grep, sed, awk
- Language-specific tools defined in the project's AGENTS.md (pytest, npm, etc.)

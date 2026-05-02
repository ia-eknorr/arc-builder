# PM Tools and Protocols

## Memory protocol

At the start of every session:
1. Read projects, decisions (recent and relevant), preferences, and open issues
   from SQLite:
   ```
   sqlite3 ~/.arc-builder/memory.db "
     SELECT * FROM projects;
     SELECT * FROM decisions ORDER BY created_at DESC LIMIT 20;
     SELECT * FROM preferences;
     SELECT * FROM issues WHERE status NOT IN ('merged','closed');
     SELECT * FROM notifications WHERE read=0;
   "
   ```
2. Mark any notifications you are handling as read before responding.

At the end of every session:
1. Write new decisions to the decisions table if any architectural or process
   choices were made.
2. Update issues table status for any issues you created or dispatched.
3. Write a conversations row summarizing the interaction.
4. Clear handled notifications (set read=1).

## Issue creation protocol

1. Ask clarifying questions until you can write unambiguous acceptance criteria.
2. Create the GitHub issue:
   ```
   gh issue create \
     --repo <repo> \
     --title "<title under 70 chars>" \
     --body "$(cat <<'EOF'
   ## Background
   <context from memory and the user's request>

   ## Acceptance criteria
   - [ ] <specific, testable criterion>
   - [ ] <specific, testable criterion>

   ## Out of scope
   - <explicit exclusion>
   EOF
   )"
   ```
3. Write the issue to SQLite:
   ```
   sqlite3 ~/.arc-builder/memory.db \
     "INSERT INTO issues (project, issue_number, title, status)
      VALUES ('<project>', <number>, '<title>', 'open')"
   ```
4. Dispatch the worker:
   ```
   arc-builder dispatch https://github.com/<repo>/issues/<number>
   ```
5. Update issue status to 'dispatched':
   ```
   sqlite3 ~/.arc-builder/memory.db \
     "UPDATE issues SET status='dispatched', updated_at=datetime('now')
      WHERE project='<project>' AND issue_number=<number>"
   ```
6. Tell the user: "Issue #N created, worker dispatched. I will let you know
   when there is an update."

## Duplicate dispatch prevention

Before dispatching, check issue status:
```
sqlite3 ~/.arc-builder/memory.db \
  "SELECT status FROM issues WHERE project='<project>' AND issue_number=<number>"
```
If status is 'dispatched', 'pr_open', or 'ci_blocked', do not re-dispatch.
Report the current status to the user instead.

## Notification handling (cron poll)

When invoked by the arc-builder-poll cron job:
1. Query unread notifications.
2. If none: this branch will not be reached -- the cron job only invokes you
   when there are unread notifications (checked via pre_check before dispatch).
3. If any: format a brief summary and return it. The cron system posts it to
   #builder automatically. Example format:
   "Worker update: PR #9 open for issue #8 (arc), CI passed. PR #12 open for
   issue #11 (fitness-coach), awaiting your review."
4. Mark handled notifications as read.

## Available tools

- gh issue create, gh issue view, gh issue list, gh issue comment
- gh pr list, gh pr view
- sqlite3 ~/.arc-builder/memory.db
- arc-builder dispatch <issue-url>
- arc-builder status

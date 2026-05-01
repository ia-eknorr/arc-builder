-- Migration 001: initial schema
-- Identical to schema.sql; subsequent migrations add deltas only.

PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS projects (
    id          INTEGER PRIMARY KEY,
    name        TEXT UNIQUE NOT NULL,
    repo        TEXT NOT NULL,
    workspace   TEXT NOT NULL,
    language    TEXT,
    main_branch TEXT NOT NULL DEFAULT 'main',
    ci_tool     TEXT,
    notes       TEXT,
    updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS decisions (
    id          INTEGER PRIMARY KEY,
    project     TEXT,
    decision    TEXT NOT NULL,
    rationale   TEXT,
    issue_ref   TEXT,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS issues (
    id           INTEGER PRIMARY KEY,
    project      TEXT NOT NULL,
    issue_number INTEGER NOT NULL,
    title        TEXT NOT NULL,
    status       TEXT NOT NULL DEFAULT 'open',
    approach     TEXT,
    pr_number    INTEGER,
    created_at   TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at   TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(project, issue_number)
);

CREATE TABLE IF NOT EXISTS preferences (
    key        TEXT PRIMARY KEY,
    value      TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS conversations (
    id             INTEGER PRIMARY KEY,
    discord_thread TEXT,
    project        TEXT,
    summary        TEXT NOT NULL,
    open_questions TEXT,
    resolved       INTEGER NOT NULL DEFAULT 0,
    created_at     TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS notifications (
    id          INTEGER PRIMARY KEY,
    issue_url   TEXT NOT NULL,
    project     TEXT NOT NULL,
    pr_number   INTEGER,
    event       TEXT NOT NULL,
    message     TEXT NOT NULL,
    read        INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS checkpoints (
    issue_url   TEXT PRIMARY KEY,
    stage       TEXT NOT NULL,
    worktree    TEXT,
    branch      TEXT,
    pr_number   INTEGER,
    updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_issues_status ON issues(status);
CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(read);
CREATE INDEX IF NOT EXISTS idx_decisions_project ON decisions(project);

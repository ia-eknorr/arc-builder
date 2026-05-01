#!/usr/bin/env bash
# Bootstrap ~/.arc-builder/ for first run.
set -euo pipefail

ARC_BUILDER_DIR="$HOME/.arc-builder"
DB="$ARC_BUILDER_DIR/memory.db"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCHEMA="$SCRIPT_DIR/../memory/schema.sql"

echo "Creating $ARC_BUILDER_DIR ..."
mkdir -p "$ARC_BUILDER_DIR/worktrees"
mkdir -p "$ARC_BUILDER_DIR/env"
mkdir -p "$ARC_BUILDER_DIR/logs"
chmod 700 "$ARC_BUILDER_DIR/env"

if [ ! -f "$DB" ]; then
    echo "Initializing memory database ..."
    sqlite3 "$DB" < "$SCHEMA"
    chmod 600 "$DB"
    echo "Created $DB"
else
    echo "Database already exists at $DB -- skipping creation."
fi

REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo ""
echo "Registering PM agent with arc ..."
cp "$REPO_ROOT/agents/pm/pm.yaml" "$HOME/.arc/agents/pm.yaml"
echo "Copied pm.yaml to ~/.arc/agents/pm.yaml"

echo ""
echo "Setup complete. Next steps:"
echo "  1. Verify ~/.arc/agents/pm.yaml has the correct workspace path"
echo "  2. Add your projects: arc-builder memory add-project"
echo "  3. Restart the arc daemon: arc daemon restart"
echo "  4. Post a message in #builder to test the PM"

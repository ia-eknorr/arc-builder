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

echo ""
echo "Setup complete. Next steps:"
echo "  1. Register pm and worker agents in ~/.arc/agents/"
echo "  2. Set channel_id in pm.yaml to your #builder Discord channel"
echo "  3. Add your projects: arc-builder memory add-project"
echo "  4. Start the arc daemon: arc daemon start"

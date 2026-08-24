#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_DIR=/opt/f-caps-schedule/deploy
mkdir -p "$DEPLOY_DIR"
cp "$SCRIPT_DIR/compose.yml" "$DEPLOY_DIR/"
if [[ ! -f "$DEPLOY_DIR/.env" ]]; then
  echo "Missing $DEPLOY_DIR/.env. Create it from deploy/production/.env.example before deploying."
  exit 1
fi

#!/usr/bin/env bash
set -Eeuo pipefail

DEPLOY_DIR=/opt/f-caps-schedule/deploy
mkdir -p "$DEPLOY_DIR"
cp compose.yml "$DEPLOY_DIR/"
if [[ ! -f "$DEPLOY_DIR/.env" ]]; then
  echo "Missing $DEPLOY_DIR/.env. Create it from deploy/production/.env.example before deploying."
  exit 1
fi

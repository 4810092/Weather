#!/usr/bin/env bash
set -euo pipefail
set +x

export GH_PROMPT_DISABLED=1
export GIT_TERMINAL_PROMPT=0

exec python3 \
  /Users/khasan/.codex/skills/project-auth-ops/scripts/store_api_status.py \
  --project nimbo "$@"

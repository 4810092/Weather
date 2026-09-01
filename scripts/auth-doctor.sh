#!/usr/bin/env bash
set -euo pipefail

task_codex_dir="${CODEX_HOME:-$HOME/.codex}"
task_doctor="$task_codex_dir/skills/project-auth-ops/scripts/project_auth_doctor.py"

if [[ ! -r "$task_doctor" ]]; then
  echo "project-auth-ops is not installed at $task_doctor" >&2
  exit 2
fi

exec python3 "$task_doctor" --project nimbo "$@"

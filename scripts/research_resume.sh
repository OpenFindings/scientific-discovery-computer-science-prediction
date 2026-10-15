#!/bin/sh
set -eu
repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
python_bin=$(command -v python3.12 || command -v python3)
"$python_bin" "$repo_root/scripts/research_supervisor.py" --repo-root "$repo_root" --resume
exec "$python_bin" "$repo_root/scripts/research_supervisor.py" --repo-root "$repo_root" --start "$@"

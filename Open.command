#!/bin/sh
cd "$(dirname "$0")" || exit 1
exec python3 codex/praxis-mine/skills/praxis-mine/workspace/open.py "$@"

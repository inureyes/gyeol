#!/usr/bin/env sh
# gyeol PostToolUse hook — mark session as substantive
#
# Touches a per-session flag file whenever a meaningful edit happens
# (Write, Edit, or git commit). The Stop hook later reads this flag to
# decide whether to demand a daily episode log.
#
# Input: PostToolUse hook JSON on stdin (contains session_id).

set -eu

INPUT=$(cat)
SESSION_ID=$(printf '%s' "$INPUT" | jq -r '.session_id // empty')

[ -n "$SESSION_ID" ] || exit 0

touch "/tmp/gyeol_session_${SESSION_ID}.substantive" 2>/dev/null || true
exit 0

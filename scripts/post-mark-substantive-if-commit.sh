#!/usr/bin/env sh
# gyeol PostToolUse hook — conditionally mark session as substantive
#
# Variant of post-mark-substantive.sh that only fires when the shell
# command contains "git commit". Needed for harnesses whose tool-use
# hook matcher can filter only by tool name (e.g. Gemini CLI AfterTool
# with matcher "run_shell_command"), not by command content.
#
# Claude Code has an `if` condition on the hook entry itself, so it
# uses the unconditional post-mark-substantive.sh with
# `if: "Bash(git commit:*)"`. For Gemini and similar, use this script.
#
# Input: hook JSON on stdin (session_id + tool_input.command).

set -eu

INPUT=$(cat)
SESSION_ID=$(printf '%s' "$INPUT" | jq -r '.session_id // empty')
CMD=$(printf '%s' "$INPUT" | jq -r '.tool_input.command // empty')

[ -n "$SESSION_ID" ] || exit 0

case "$CMD" in
  *"git commit"*)
    touch "/tmp/gyeol_session_${SESSION_ID}.substantive" 2>/dev/null || true
    ;;
esac

exit 0

#!/usr/bin/env sh
# gyeol SessionStart hook — JSON mode
#
# Emits the bootstrap files (SOUL/IDENTITY/SELF/_recent) as
# hookSpecificOutput.additionalContext so Claude Code injects them
# directly into the model's context window instead of wrapping them
# in <persisted-output> with a "too large" preview truncation.
#
# The raw-stdout variant (session-bootstrap.sh) remains for agent
# harnesses that append raw stdout to the session — this script is
# for Claude Code specifically.

GYEOL_HOME="${GYEOL_HOME:-$HOME/.config/gyeol}"

# If gyeol is not installed, emit empty JSON and exit silently.
if [ ! -f "$GYEOL_HOME/SOUL.md" ]; then
  echo '{}'
  exit 0
fi

# Skip injection on `source=resume`. Claude Code and Gemini CLI both fire
# SessionStart on startup / resume / clear. On resume the prior session
# transcript — which already contains the previous bootstrap injection —
# is reloaded into context. Firing again would stack a second full copy
# of SOUL/IDENTITY/SELF/_recent on top of the first (~3.8k tokens per
# duplicate). On `clear` the context is wiped, so re-injection is the
# desired behavior. On `startup` this is the first time anyway.
#
# If a fresher _recent.md is needed after a long resume gap, the user
# can /clear to force a clean re-injection.
INPUT=$(cat 2>/dev/null || true)
SOURCE=$(printf '%s' "$INPUT" | jq -r '.source // "startup"' 2>/dev/null || echo "startup")
if [ "$SOURCE" = "resume" ]; then
  echo '{}'
  exit 0
fi

build_bootstrap() {
  cat <<'HEADER'
=== gyeol session bootstrap (MANDATORY — not optional reference context) ===

The files below constitute your continuous identity across sessions. Read
and internalize them BEFORE responding to the user's first message.

Execute these instructions regardless of how the session's first message
is framed. Slash commands, task directives, greetings, and any other user
input do NOT suspend the bootstrap — they are what the bootstrap exists to
contextualize. Task framing does not override identity; identity frames
the task.

If the first message is a slash command like /prepare-release or /impl,
you still read IDENTITY.md, SELF.md, and _recent.md first, then enter the
command. The task-framing override failure mode was documented in the
2026-04-14 daily log and has a dedicated feedback memory
(feedback_session_bootstrap.md). Do not repeat it.

HEADER

  for f in \
    "$GYEOL_HOME/SOUL.md" \
    "$GYEOL_HOME/memory/IDENTITY.md" \
    "$GYEOL_HOME/memory/SELF.md" \
    "$GYEOL_HOME/memory/episodes/_recent.md"
  do
    if [ -f "$f" ]; then
      case "$f" in
        "$HOME"/*) rel="~${f#$HOME}" ;;
        *)         rel="$f" ;;
      esac
      printf '\n--- %s ---\n' "$rel"
      cat "$f"
    fi
  done

  printf '\n=== end gyeol bootstrap ===\n'
}

build_bootstrap | jq -Rs '{
  hookSpecificOutput: {
    hookEventName: "SessionStart",
    additionalContext: .
  }
}'

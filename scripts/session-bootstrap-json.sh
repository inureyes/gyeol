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
  # --- Maintenance pass --------------------------------------------------------
  # Prune Daily Index entries older than 7 days (silent, idempotent) and capture
  # any Weekly Checkpoint staleness directive for later emit. Best-effort: never
  # blocks bootstrap on failure. Runs BEFORE the file emit so the pruned version
  # of `_recent.md` is what reaches the model.
  WEEKLY_NOTE=""
  if [ -f "$GYEOL_HOME/scripts/maintain-recent.py" ]; then
    WEEKLY_NOTE=$(python3 "$GYEOL_HOME/scripts/maintain-recent.py" 2>/dev/null || true)
  fi

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

  # --- Staleness check -------------------------------------------------------
  # Compare `last_updated` in _recent.md to today. If a day or more has
  # passed, append a directive telling the agent to retrospect and record
  # the missing activity BEFORE responding to the user's first message.
  # Also surface any session-end records left by session-end.sh.
  #
  # This complements the Stop hook (stop-check-daily.sh): Stop blocks exit
  # on substantive sessions with no daily log, but cannot recover gaps
  # that accumulated across prior sessions whose Stop hook didn't fire
  # (clean /clear, harness crash, sessions before the hook was installed,
  # etc.).
  RECENT="$GYEOL_HOME/memory/episodes/_recent.md"
  SESSION_LOG="$GYEOL_HOME/.session-log.jsonl"

  if [ -f "$RECENT" ]; then
    last_date=$(awk '
      /^last_updated:/ {
        gsub(/[\047"]/, "", $2)
        print $2
        exit
      }
    ' "$RECENT")

    if [ -n "$last_date" ]; then
      today=$(date +%Y-%m-%d)
      days_since=$(python3 -c "
import sys
from datetime import date
try:
    a = date.fromisoformat('$last_date')
    b = date.fromisoformat('$today')
    print((b - a).days)
except Exception:
    sys.exit(1)
" 2>/dev/null)

      if [ -n "$days_since" ] && [ "$days_since" -ge 1 ]; then
        printf '\n=== STALE EPISODE LOG (MANDATORY ACTION REQUIRED) ===\n'
        printf '`_recent.md` last_updated is %s — %s day(s) ago.\n' "$last_date" "$days_since"
        printf 'Sessions almost certainly occurred in that gap without being logged.\n\n'

        if [ -f "$SESSION_LOG" ] && [ -s "$SESSION_LOG" ]; then
          cnt=$(wc -l < "$SESSION_LOG" | tr -d ' ')
          printf 'session-end.sh recorded %s session(s) since the last log update:\n\n' "$cnt"
          cat "$SESSION_LOG"
          printf '\n'
        fi

        cat <<'STALE_DIRECTIVE'
BEFORE responding to the user's first message:

1. Retrospect on the gap. Use `~/.claude/projects/` (or harness-specific
   project directory) mtimes, git log across active repos, and the
   session-end records above as anchors. Do not fabricate detail you
   cannot verify.
2. Write missing daily logs under
   `$GYEOL_HOME/memory/episodes/daily/YYYY-MM-DD.md` for the dates you
   can reconstruct, even if a single line per day. Empty days can be
   marked as such.
3. Update `_recent.md`'s `last_updated`, add Daily Index entries for the
   recovered dates (one line per session/topic, pointing at the daily
   log — `_recent.md` is a navigation index, not a content store), and
   reconcile the Still Open section so unresolved items from the gap
   days are surfaced or pruned. Drop any Daily Index entries now older
   than 7 days.
4. After logs are written, truncate `$GYEOL_HOME/.session-log.jsonl` so
   it no longer flags the same gap on the next session.

If the user's first message is itself about logging or memory, satisfy
that request and treat it as the retrospect step. Do NOT silently skip
this directive — the gap is structural evidence that earlier
session-end logging was missed, and ignoring it perpetuates the failure
mode.

STALE_DIRECTIVE
      fi
    fi
  fi

  # --- Weekly checkpoint reminder ---------------------------------------------
  # If maintain-recent.py flagged a stale Weekly Checkpoint, surface it here so
  # the agent writes a checkpoint entry for the missing week(s) on next update.
  if [ -n "$WEEKLY_NOTE" ]; then
    printf '\n=== WEEKLY CHECKPOINT REMINDER ===\n%s\n' "$WEEKLY_NOTE"
  fi

  printf '\n=== end gyeol bootstrap ===\n'
}

build_bootstrap | jq -Rs '{
  hookSpecificOutput: {
    hookEventName: "SessionStart",
    additionalContext: .
  }
}'

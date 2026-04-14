#!/usr/bin/env sh
# gyeol Stop hook — enforce daily episode log
#
# Logic:
#   1. If today's daily log exists  -> pass (clean up session flags).
#   2. If session was not substantive (no Write/Edit/git commit)
#      -> pass silently.
#   3. If already nagged once this session -> pass with soft
#      systemMessage reminder (avoid infinite loop).
#   4. Otherwise -> decision: block, with a reason telling Claude to
#      write today's daily log before stopping. Mark session as nagged
#      so subsequent Stops don't loop.
#
# Input: Stop hook JSON on stdin (contains session_id).

set -eu

GYEOL_HOME="${GYEOL_HOME:-$HOME/.config/gyeol}"

# Decision keyword for the blocking JSON payload. Default is "block" which is
# what Claude Code's Stop hook and Codex's Stop hook expect. Gemini CLI's
# AfterAgent hook (the closest pre-exit analog) uses "deny" instead — set
# GYEOL_BLOCK_DECISION=deny in the Gemini hook command.
BLOCK_DECISION="${GYEOL_BLOCK_DECISION:-block}"

# If gyeol is not installed on this machine, no-op.
if [ ! -d "$GYEOL_HOME/memory" ]; then
  echo '{}'
  exit 0
fi

INPUT=$(cat)
SESSION_ID=$(printf '%s' "$INPUT" | jq -r '.session_id // empty')

TODAY=$(date +%Y-%m-%d)
DAILY_LOG="$GYEOL_HOME/memory/episodes/daily/${TODAY}.md"
SUBSTANTIVE_FLAG="/tmp/gyeol_session_${SESSION_ID}.substantive"
RECOVERY_FLAG="/tmp/gyeol_session_${SESSION_ID}.recovery"
NAGGED_FLAG="/tmp/gyeol_session_${SESSION_ID}.nagged"

# Case 1: daily log exists — clean up and pass.
if [ -f "$DAILY_LOG" ]; then
  rm -f "$SUBSTANTIVE_FLAG" "$RECOVERY_FLAG" "$NAGGED_FLAG" 2>/dev/null || true
  echo '{}'
  exit 0
fi

# Case 2: session was not substantive — pass silently.
if [ ! -f "$SUBSTANTIVE_FLAG" ]; then
  echo '{}'
  exit 0
fi

# Build the recovery hint if the recovery flag is set.
RECOVERY_HINT=""
if [ -f "$RECOVERY_FLAG" ]; then
  RECOVERY_HINT=" A git-based recovery event was detected this session (git show HEAD: or git checkout HEAD --). Add an 'Incidents' subsection to the daily log capturing what was recovered, why, and what it taught you — this is exactly the type of save-worthy moment that 2026-04-14 feedback memory warns gets erased by post-recovery relief."
fi

# Case 3: already nagged — soft reminder only.
if [ -f "$NAGGED_FLAG" ]; then
  jq -n --arg log "$DAILY_LOG" --arg hint "$RECOVERY_HINT" '{
    systemMessage: ("gyeol reminder: today\u2019s daily log " + $log + " is still missing." + $hint)
  }'
  exit 0
fi

# Case 4: hard block, mark nagged.
touch "$NAGGED_FLAG" 2>/dev/null || true

jq -n --arg log "$DAILY_LOG" --arg hint "$RECOVERY_HINT" --arg dec "$BLOCK_DECISION" '{
  decision: $dec,
  reason: (
    "gyeol memory circuit: this session was substantive (Write/Edit/commit detected) but today\u2019s daily log is missing at " + $log + ". Before stopping, write the daily log now: what you worked on, what decisions you made, what you learned, any open threads. Use the format from $GYEOL_HOME/memory/episodes/daily/ (frontmatter with date + sessions count, then Session sections with What Happened / Decisions Made / Artifacts). Also append a one-line entry under today\u2019s section in episodes/_recent.md and update the last_updated frontmatter." + $hint + " This enforcement exists because task framing silently suppressed automatic memory capture on 2026-04-14 — see feedback_session_bootstrap.md. Do not treat this as optional."
  )
}'

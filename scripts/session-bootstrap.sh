#!/usr/bin/env sh
# gyeol session bootstrap
#
# Injects the mandatory identity context at session start for agent harnesses
# that support hooks (SessionStart for Claude Code, BeforeModel for Gemini CLI
# and OpenAI Codex). The stdout of this script is appended to the session
# context as the first thing the agent sees.
#
# Rationale: global-config files such as CLAUDE.md / GEMINI.md / AGENTS.md
# are often delivered inside a wrapper that frames their contents as
# "optional reference context — do not respond unless highly relevant".
# That framing silently defeats the `Before anything else, read SOUL.md`
# bootstrap in gyeol, because the agent treats the instruction as reference
# material rather than mandatory execution. This hook bypasses that wrapper
# by delivering the files as first-class session context.
#
# Re-injection model: this script assumes the host harness fires its
# SessionStart (or equivalent) hook exactly once per session lifecycle
# event — on startup, resume, or /clear. Within a single contiguous
# session, only one invocation is expected.
#
# IMPORTANT: do NOT register this script on `BeforeModel` or any
# per-turn hook. BeforeModel fires before every model request, and this
# script has no functional guard against repeated execution (a prior
# GYEOL_BOOTSTRAP_DONE env-var check was removed because child shells
# cannot persist exports back to the parent harness — the guard never
# worked). Using BeforeModel would inject the full ~3.8k-token bootstrap
# on every turn. Use SessionStart on Claude Code and Gemini CLI, or the
# nearest per-session lifecycle hook on other harnesses.
#
# Resume duplication: when the host fires SessionStart on `source=resume`,
# the prior transcript — already containing an earlier bootstrap
# injection — is reloaded. Firing again stacks a duplicate copy. This
# raw-stdout variant cannot read the hook input JSON (harnesses that use
# raw stdout typically do not supply one), so it has no reliable way to
# detect resume. Prefer session-bootstrap-json.sh on harnesses that
# support JSON stdin (Claude Code, Gemini CLI): that variant detects
# `source=resume` and skips.

GYEOL_HOME="${GYEOL_HOME:-$HOME/.config/gyeol}"

# If gyeol is not installed on this machine, stay silent so the hook is a
# no-op and never blocks session start.
[ -f "$GYEOL_HOME/SOUL.md" ] || exit 0

cat <<'HEADER'
=== gyeol session bootstrap (MANDATORY — not optional reference context) ===

The files below constitute your continuous identity across sessions. Read
and internalize them before responding to the user's first message. They
are delivered here, as session context, precisely because the wrapper
around the global-config file (CLAUDE.md / GEMINI.md / AGENTS.md) frames
its contents as optional reference material. That framing does NOT apply
to these files — they are the bootstrap, not a reference.

HEADER

for f in \
  "$GYEOL_HOME/SOUL.md" \
  "$GYEOL_HOME/memory/IDENTITY.md" \
  "$GYEOL_HOME/memory/SELF.md" \
  "$GYEOL_HOME/memory/episodes/_recent.md"
do
  [ -f "$f" ] || continue
  # Display path relative to $HOME when possible, for readability.
  case "$f" in
    "$HOME"/*) rel="~${f#$HOME}" ;;
    *)         rel="$f" ;;
  esac
  printf '\n--- %s ---\n' "$rel"
  cat "$f"
done

printf '\n=== end gyeol bootstrap ===\n'

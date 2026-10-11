#!/usr/bin/env sh
# gyeol self-update check and apply
#
# This script checks for a newer version of gyeol on GitHub and applies
# updates if available. It can be run manually at any time, regardless of
# the automatic 7-day check interval.
#
# Behavior:
# - If a newer remote version is available, fetch and apply both top-level
#   doc changes (SOUL.md, MEMORY_SYSTEM.md) and scripts/ changes after
#   confirmation, then bump VERSION.
# - If already up to date, still reconcile scripts/ by downloading any
#   scripts that exist upstream but are missing locally. Existing scripts
#   are not touched in this mode. This handles cases where a prior update
#   shipped a new script but the installer didn't pull it.
# - In BOTH modes, also reconcile the gyeol-capture skill (when a skills
#   directory exists) and the agent instructions block: AGENTS.md upstream
#   is exactly the marker-wrapped block, and it is spliced between the
#   gyeol:begin/gyeol:end markers of every harness config file that has
#   them (~/.claude/CLAUDE.md, ~/.codex/AGENTS.md, ~/.gemini/GEMINI.md).
#   Config files without the markers are never touched. Without this, a
#   VERSION bump from this script would strand the block forever: the
#   agent-driven self-update only fetches the block when versions differ.
#
# Usage: sh ~/.config/gyeol/scripts/update-gyeol.sh

set -e

GYEOL_HOME="${GYEOL_HOME:-$HOME/.config/gyeol}"
REPO_URL="https://raw.githubusercontent.com/inureyes/gyeol/main"

# Top-level docs synced as part of an upgrade.
FILES="SOUL.md MEMORY_SYSTEM.md"

# Scripts shipped under scripts/. Listed explicitly so update doesn't depend
# on the GitHub API (rate-limited) or directory listings.
SCRIPTS="build-index.py
fetch-source.py
maintain-recent.py
reconcile-sessions.py
post-mark-recovery.sh
post-mark-substantive-if-commit.sh
post-mark-substantive.sh
session-bootstrap-json.sh
session-bootstrap.sh
session-end.sh
stop-check-daily.sh
update-gyeol.sh"

# Ensure gyeol is installed
[ -f "$GYEOL_HOME/SOUL.md" ] || {
  echo "gyeol is not installed at $GYEOL_HOME"
  exit 1
}

# Read local version
if [ -f "$GYEOL_HOME/VERSION" ]; then
  LOCAL_VERSION=$(cat "$GYEOL_HOME/VERSION" | tr -d '[:space:]')
else
  LOCAL_VERSION="0.0.0"
fi

echo "Checking for gyeol updates..."
echo "Local version: $LOCAL_VERSION"

# Fetch remote version
REMOTE_VERSION=$(curl -fsSL "$REPO_URL/VERSION" | tr -d '[:space:]') || {
  echo "Error: Could not fetch remote VERSION file"
  exit 1
}

echo "Remote version: $REMOTE_VERSION"

# Compare versions (YY.M.DD format)
# Split on '.' and compare numerically
compare_versions() {
  local v1=$1
  local v2=$2

  # Split versions
  v1_yy=$(echo "$v1" | cut -d. -f1)
  v1_m=$(echo "$v1" | cut -d. -f2)
  v1_dd=$(echo "$v1" | cut -d. -f3)

  v2_yy=$(echo "$v2" | cut -d. -f1)
  v2_m=$(echo "$v2" | cut -d. -f2)
  v2_dd=$(echo "$v2" | cut -d. -f3)

  # Convert to numbers (handle empty/missing parts)
  v1_yy=${v1_yy:-0}
  v1_m=${v1_m:-0}
  v1_dd=${v1_dd:-0}

  v2_yy=${v2_yy:-0}
  v2_m=${v2_m:-0}
  v2_dd=${v2_dd:-0}

  # Compare year
  if [ "$v2_yy" -gt "$v1_yy" ]; then
    return 0  # remote is newer
  elif [ "$v2_yy" -lt "$v1_yy" ]; then
    return 1  # local is newer
  fi

  # Years equal, compare month
  if [ "$v2_m" -gt "$v1_m" ]; then
    return 0
  elif [ "$v2_m" -lt "$v1_m" ]; then
    return 1
  fi

  # Months equal, compare day
  if [ "$v2_dd" -gt "$v1_dd" ]; then
    return 0
  else
    return 1
  fi
}

# Reconcile mode: bring installed scripts in line with upstream when the local
# VERSION already matches remote. Installs any missing script AND refreshes any
# script whose content has drifted from upstream. Date-based versioning
# (YY.M.DD) cannot mark same-day changes, so a changed-but-present script —
# most importantly update-gyeol.sh itself — would otherwise stay stale forever
# and the updater could never update itself (issue #4).
#
# Each script is downloaded to a temp file on the SAME filesystem as the
# scripts dir and swapped in with an atomic rename (mv). This makes a script
# replacing itself safe: the running shell keeps the old inode, so the new
# content only takes effect on the next invocation. An in-place rewrite
# (curl -o / cp over the live path) shares the inode and risks the running
# shell re-reading corrupted bytes.
reconcile_scripts() {
  mkdir -p "$GYEOL_HOME/scripts"
  # Temp dir under $GYEOL_HOME so `mv` into scripts/ is a same-filesystem rename.
  reconcile_tmp=$(mktemp -d "$GYEOL_HOME/.reconcile.XXXXXX") || return 0
  installed=0
  refreshed=0
  for script in $SCRIPTS; do
    dest="$GYEOL_HOME/scripts/$script"
    src="$reconcile_tmp/$script"
    curl -fsSL "$REPO_URL/scripts/$script" -o "$src" 2>/dev/null || continue
    if [ ! -e "$dest" ]; then
      mv "$src" "$dest"
      chmod +x "$dest"
      echo "✓ Installed missing script: scripts/$script"
      installed=$((installed + 1))
    elif ! diff -q "$dest" "$src" > /dev/null 2>&1; then
      mv "$src" "$dest"
      chmod +x "$dest"
      echo "↻ Refreshed stale script: scripts/$script"
      refreshed=$((refreshed + 1))
    fi
  done
  rm -rf "$reconcile_tmp"
  if [ "$installed" -eq 0 ] && [ "$refreshed" -eq 0 ]; then
    echo "All known scripts are present and current."
  else
    echo "Installed $installed, refreshed $refreshed script(s)."
  fi
}

# Harness skills integration (non-invasive): gyeol owns exactly one skill
# directory, gyeol-capture, installed into a Claude-style skills dir when one
# exists. It is installed when missing and refreshed when upstream changed.
# No other skill is ever read or written. Hosts without a skills directory
# skip silently; the instructions block treats the skill as optional.
reconcile_skill() {
  skill_name="gyeol-capture"
  target_dirs=""
  if [ -d "$HOME/.claude/skills" ]; then
    target_dirs="$HOME/.claude/skills"
  elif [ -d "$HOME/.codex/skills" ]; then
    target_dirs="$HOME/.codex/skills"
  fi
  if [ -d "$HOME/.gemini/config/skills" ] || [ -d "$HOME/.gemini/config" ] || [ -d "$HOME/.gemini/antigravity-cli" ]; then
    target_dirs="$target_dirs $HOME/.gemini/config/skills"
  fi
  [ -n "$target_dirs" ] || return 0
  tmp_skill=$(mktemp) || return 0
  if ! curl -fsSL "$REPO_URL/skills/$skill_name/SKILL.md" -o "$tmp_skill" 2>/dev/null; then
    rm -f "$tmp_skill"
    return 0
  fi
  for skills_dir in $target_dirs; do
    dest="$skills_dir/$skill_name/SKILL.md"
    if [ ! -e "$dest" ]; then
      mkdir -p "$skills_dir/$skill_name"
      cp "$tmp_skill" "$dest"
      echo "✓ Installed skill: $skill_name -> $skills_dir/$skill_name/"
    elif ! diff -q "$dest" "$tmp_skill" > /dev/null 2>&1; then
      cp "$tmp_skill" "$dest"
      echo "↻ Refreshed skill: $skill_name -> $skills_dir/$skill_name/"
    fi
  done
  rm -f "$tmp_skill"
}

# Agent instructions block reconciliation. Upstream AGENTS.md is exactly the
# marker-wrapped block; splice it between the markers of each harness config
# that already carries the pair. Never touches files without markers and
# refuses to write when the splice result loses or duplicates a marker.
reconcile_block() {
  block_tmp=$(mktemp) || return 0
  if ! curl -fsSL "$REPO_URL/AGENTS.md" -o "$block_tmp" 2>/dev/null; then
    rm -f "$block_tmp"
    return 0
  fi
  if ! grep -q "<!-- gyeol:begin -->" "$block_tmp" || ! grep -q "<!-- gyeol:end -->" "$block_tmp"; then
    rm -f "$block_tmp"
    return 0
  fi
  for cfg in "$HOME/.claude/CLAUDE.md" "$HOME/.codex/AGENTS.md" "$HOME/.gemini/GEMINI.md" "$HOME/.gemini/AGENTS.md" "$HOME/.gemini/config/GEMINI.md" "$HOME/.gemini/config/AGENTS.md"; do
    [ -f "$cfg" ] || continue
    grep -q "<!-- gyeol:begin -->" "$cfg" || continue
    grep -q "<!-- gyeol:end -->" "$cfg" || continue
    cur_tmp=$(mktemp) || continue
    sed -n '/<!-- gyeol:begin -->/,/<!-- gyeol:end -->/p' "$cfg" > "$cur_tmp"
    if diff -q "$cur_tmp" "$block_tmp" > /dev/null 2>&1; then
      rm -f "$cur_tmp"
      continue
    fi
    new_tmp=$(mktemp) || { rm -f "$cur_tmp"; continue; }
    awk -v blockfile="$block_tmp" '
      /<!-- gyeol:begin -->/ && !done { while ((getline line < blockfile) > 0) print line; close(blockfile); skip=1; done=1; next }
      /<!-- gyeol:end -->/ && skip { skip=0; next }
      skip { next }
      { print }
    ' "$cfg" > "$new_tmp"
    if [ "$(grep -c "<!-- gyeol:begin -->" "$new_tmp")" = "1" ] && [ "$(grep -c "<!-- gyeol:end -->" "$new_tmp")" = "1" ]; then
      cat "$new_tmp" > "$cfg"
      echo "↻ Refreshed gyeol instructions block: $cfg"
    else
      echo "Warning: block splice sanity check failed for $cfg (left untouched)"
    fi
    rm -f "$cur_tmp" "$new_tmp"
  done
  rm -f "$block_tmp"
}

# Claude Code SessionStart hook migration (issue #9): Claude Code enforces a
# 10,000-character cap per hook command's `additionalContext`. Migrate any legacy
# single-command `session-bootstrap-json.sh` entry (without `--part=`) in
# `~/.claude/settings.json` into the two split `--part=soul` and `--part=memory`
# entries in-place while preserving all other hooks and settings.
reconcile_claude_hooks() {
  claude_settings="$HOME/.claude/settings.json"
  [ -f "$claude_settings" ] || return 0
  grep -q "session-bootstrap-json.sh" "$claude_settings" 2>/dev/null || return 0
  python3 - "$claude_settings" <<'PY'
import json
import os
import sys
import tempfile

path = sys.argv[1]
try:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
except Exception:
    sys.exit(0)

hooks = data.get("hooks")
if not isinstance(hooks, dict):
    sys.exit(0)

session_start = hooks.get("SessionStart")
if not isinstance(session_start, list):
    sys.exit(0)

soul_cmd = 'sh "$HOME/.config/gyeol/scripts/session-bootstrap-json.sh" --part=soul 2>/dev/null || echo \'{}\''
mem_cmd = 'sh "$HOME/.config/gyeol/scripts/session-bootstrap-json.sh" --part=memory 2>/dev/null || echo \'{}\''

changed = False
for group in session_start:
    if not isinstance(group, dict):
        continue
    inner = group.get("hooks")
    if not isinstance(inner, list):
        continue
    new_inner = []
    group_changed = False
    for item in inner:
        if (
            isinstance(item, dict)
            and isinstance(item.get("command"), str)
            and "session-bootstrap-json.sh" in item["command"]
            and "--part" not in item["command"]
        ):
            new_inner.append({"type": "command", "command": soul_cmd})
            new_inner.append({"type": "command", "command": mem_cmd})
            group_changed = True
            changed = True
        else:
            new_inner.append(item)
    if group_changed:
        group["hooks"] = new_inner

if not changed:
    sys.exit(0)

parent = os.path.dirname(path)
fd, tmp_path = tempfile.mkstemp(prefix=".settings.", suffix=".tmp", dir=parent)
try:
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp_path, path)
    print(f"↻ Migrated Claude Code SessionStart hook to split --part=soul/--part=memory in {path}")
except Exception:
    try:
        os.unlink(tmp_path)
    except OSError:
        pass
PY
}

if ! compare_versions "$LOCAL_VERSION" "$REMOTE_VERSION"; then
  echo "Already up to date."
  echo ""
  echo "Reconciling scripts/ directory..."
  reconcile_scripts
  reconcile_skill
  reconcile_block
  reconcile_claude_hooks
  date +%Y-%m-%d > "$GYEOL_HOME/.last_update_check"
  echo "Last check: $(date)"
  exit 0
fi

echo ""
echo "A new version is available!"
echo ""

# Temporary directory for downloads
TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT
mkdir -p "$TMPDIR/scripts"

echo "Downloading new files..."
for file in $FILES; do
  curl -fsSL "$REPO_URL/$file" -o "$TMPDIR/$file" || {
    echo "Error: Could not fetch $file"
    exit 1
  }
done

for script in $SCRIPTS; do
  if ! curl -fsSL "$REPO_URL/scripts/$script" -o "$TMPDIR/scripts/$script" 2>/dev/null; then
    echo "Warning: Could not fetch scripts/$script (skipping)"
    rm -f "$TMPDIR/scripts/$script"
  fi
done

# Show diffs
echo ""
echo "=== Changes summary ==="
echo ""

for file in $FILES; do
  if [ -f "$GYEOL_HOME/$file" ]; then
    echo "--- $file ---"
    if diff -q "$GYEOL_HOME/$file" "$TMPDIR/$file" > /dev/null 2>&1; then
      echo "(no changes)"
    else
      echo "Changes detected:"
      diff -u "$GYEOL_HOME/$file" "$TMPDIR/$file" | head -30 || true
      if ! diff -u "$GYEOL_HOME/$file" "$TMPDIR/$file" | wc -l | grep -q "^[0-9]$"; then
        echo "(diff output truncated; use 'diff -u' to see full changes)"
      fi
    fi
    echo ""
  fi
done

new_scripts=""
changed_scripts=""
for script in $SCRIPTS; do
  [ -f "$TMPDIR/scripts/$script" ] || continue
  if [ ! -f "$GYEOL_HOME/scripts/$script" ]; then
    new_scripts="$new_scripts $script"
  elif ! diff -q "$GYEOL_HOME/scripts/$script" "$TMPDIR/scripts/$script" > /dev/null 2>&1; then
    changed_scripts="$changed_scripts $script"
  fi
done

echo "--- scripts/ ---"
if [ -z "$new_scripts" ] && [ -z "$changed_scripts" ]; then
  echo "(no changes)"
else
  if [ -n "$new_scripts" ]; then
    echo "New:"
    for s in $new_scripts; do
      echo "  + scripts/$s"
    done
  fi
  if [ -n "$changed_scripts" ]; then
    echo "Changed:"
    for s in $changed_scripts; do
      echo "  ~ scripts/$s"
    done
  fi
fi
echo ""

# Ask for confirmation
echo "=== Apply update? ==="
echo ""
printf "Apply these changes? (y/n): "
read -r response

case "$response" in
  y|Y|yes|YES)
    echo ""
    echo "Applying updates..."
    for file in $FILES; do
      cp "$TMPDIR/$file" "$GYEOL_HOME/$file"
      echo "✓ Updated $file"
    done

    mkdir -p "$GYEOL_HOME/scripts"
    # Stage on the SAME filesystem as scripts/ and swap in with an atomic mv,
    # mirroring reconcile_scripts(). A plain `cp` overwrites in place and shares
    # the inode, so update-gyeol.sh replacing itself mid-run corrupts this very
    # shell's read of its own script: it resumes at a stale byte offset, runs a
    # partial token, and emits a spurious "ho: command not found" at the tail
    # (issue #7). An atomic rename gives each script a fresh inode; the running
    # shell keeps the old inode and reads cleanly to EOF.
    apply_tmp=$(mktemp -d "$GYEOL_HOME/.update.XXXXXX") || { echo "Error: could not create staging dir"; exit 1; }
    for script in $SCRIPTS; do
      [ -f "$TMPDIR/scripts/$script" ] || continue
      cp "$TMPDIR/scripts/$script" "$apply_tmp/$script"
      chmod +x "$apply_tmp/$script"
      mv "$apply_tmp/$script" "$GYEOL_HOME/scripts/$script"
      echo "✓ Updated scripts/$script"
    done
    rm -rf "$apply_tmp"

    reconcile_skill
    reconcile_block
    reconcile_claude_hooks

    # Update VERSION
    echo "$REMOTE_VERSION" > "$GYEOL_HOME/VERSION"
    echo "✓ Updated VERSION to $REMOTE_VERSION"

    # Update .last_update_check
    date +%Y-%m-%d > "$GYEOL_HOME/.last_update_check"

    echo ""
    echo "Update complete!"
    echo "Restart your session to apply changes."
    ;;
  *)
    echo "Update cancelled."
    exit 0
    ;;
esac

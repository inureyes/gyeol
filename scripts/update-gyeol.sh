#!/usr/bin/env sh
# gyeol self-update check and apply
#
# This script checks for a newer version of gyeol on GitHub and applies
# updates if available. It can be run manually at any time, regardless of
# the automatic 7-day check interval.
#
# Usage: sh ~/.config/gyeol/scripts/update-gyeol.sh

set -e

GYEOL_HOME="${GYEOL_HOME:-$HOME/.config/gyeol}"
REPO_URL="https://raw.githubusercontent.com/inureyes/gyeol/main"

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

if ! compare_versions "$LOCAL_VERSION" "$REMOTE_VERSION"; then
  echo "Already up to date."
  echo "Last check: $(date)"
  exit 0
fi

echo ""
echo "A new version is available!"
echo ""

# Files to check for updates
FILES="SOUL.md MEMORY_SYSTEM.md"

# Temporary directory for downloads
TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT

echo "Downloading new files..."
for file in $FILES; do
  curl -fsSL "$REPO_URL/$file" -o "$TMPDIR/$file" || {
    echo "Error: Could not fetch $file"
    exit 1
  }
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

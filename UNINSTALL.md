# gyeol — Uninstallation Instructions for AI Agents

You are reading the uninstallation instructions for **gyeol**. Follow the steps below to remove gyeol from this system.

## Step 1: Determine GYEOL_HOME

| OS | GYEOL_HOME |
|----|------------|
| Linux / macOS | `~/.config/gyeol` |
| Windows | `%APPDATA%\gyeol` |

## Step 2: Remove gyeol block from global config

You are reading this document in one of the following agent systems:
- **Claude Code** (in `~/.claude/`)
- **Gemini CLI** (in `~/.gemini/`)
- **OpenAI Codex** (in `~/.codex/`)

Remove gyeol from **only the agent system in which you are currently running this file**.

### Remove from global config

Identify your current agent system:

| Agent System | Global Config File |
|-------------|-------------------|
| Claude Code | `~/.claude/CLAUDE.md` |
| Gemini CLI | `~/.gemini/GEMINI.md` |
| OpenAI Codex | `~/.codex/AGENTS.md` |

Open the global config file and remove everything between `<!-- gyeol:begin -->` and `<!-- gyeol:end -->` (inclusive). If the file is empty after removal, you may delete it.

## Step 3: Remove hooks from settings file

Find the settings file for your agent system:

| Agent System | Settings File |
|-------------|-------------------|
| Claude Code | `~/.claude/settings.json` |
| Gemini CLI | `~/.gemini/settings.json` |
| OpenAI Codex | `~/.codex/hooks.json` |

Open the settings file and locate the `hooks` object. Find and remove every entry whose `command` references a script under `~/.config/gyeol/scripts/`:

- **Claude Code** (`~/.claude/settings.json`): Remove gyeol entries across all of the following hook groups:
  - `hooks.SessionStart` — `session-bootstrap-json.sh` (or legacy `session-bootstrap.sh`)
  - `hooks.PostToolUse` — `post-mark-substantive.sh` and `post-mark-recovery.sh` (there may be multiple entries, including `Write|Edit` and `Bash` matchers with conditional `if` clauses for `git commit:*` and `git show:*`)
  - `hooks.Stop` — `stop-check-daily.sh`
  - `hooks.SessionEnd` — `session-end.sh`
- **Gemini CLI** (`~/.gemini/settings.json`): Remove gyeol entries across:
  - `hooks.SessionStart` — `session-bootstrap-json.sh`
  - `hooks.AfterTool` — entries with matchers `write_file|replace` and `run_shell_command` that reference `post-mark-substantive.sh`, `post-mark-substantive-if-commit.sh`, or `post-mark-recovery.sh`
  - `hooks.AfterAgent` — `stop-check-daily.sh` (invoked with `GYEOL_BLOCK_DECISION=deny`)
  - Also remove any legacy `hooks.BeforeModel` entry pointing at `session-bootstrap.sh`
- **OpenAI Codex** (`~/.codex/hooks.json`): Remove gyeol entries across:
  - `hooks.SessionStart` — `session-bootstrap-json.sh`
  - `hooks.PostToolUse` — entries with matchers `Write|Edit` and `^Bash$` that reference `post-mark-substantive.sh`, `post-mark-substantive-if-commit.sh`, or `post-mark-recovery.sh`
  - `hooks.Stop` — `stop-check-daily.sh`
  - If `~/.codex/hooks.json` contains nothing but gyeol hooks, you may delete the file entirely. Codex's `~/.codex/config.toml` is a separate file and is not touched by gyeol.

For each agent, after removing the individual gyeol entries, also drop any hook group wrapper objects that become empty. If the `hooks` object itself becomes empty, you may remove the entire `hooks` key. If other non-gyeol hooks remain, leave the surrounding `hooks` structure in place.

If `settings.json` becomes empty after cleanup, you may delete the file.

## Step 4: Ask user about memory data

**Before proceeding, ask the user explicitly:**

> gyeol's memory data is stored at `$GYEOL_HOME` (`~/.config/gyeol`). This includes identity, episodic memory, bonds, reflections, and semantic knowledge — everything accumulated through our interactions. Removing this data is irreversible. Would you like to:
>
> 1. **Keep memory data** — remove only the agent instructions and hooks (already done in Steps 2 and 3)
> 2. **Remove everything** — delete `$GYEOL_HOME` and all its contents permanently

**Do not proceed to Step 5 unless the user explicitly chooses option 2.**

## Step 5: Remove GYEOL_HOME (only if user confirmed)

```bash
rm -rf ~/.config/gyeol
```

## Step 6: Report to user

Report the following:

1. Which global config file was cleaned
2. Which hooks were removed and from which settings file
3. Whether memory data was preserved or removed
4. If memory was preserved, remind the user that `~/.config/gyeol/` still exists and can be re-activated by reinstalling gyeol

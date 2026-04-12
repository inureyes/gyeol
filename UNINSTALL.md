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
| OpenAI Codex | `~/.codex/settings.json` |

Open the settings file and locate the `hooks` object. Find and remove the gyeol hook:
- **Claude Code**: Remove the entry under `hooks.SessionStart` that references `session-bootstrap.sh`
- **Gemini CLI**: Remove the entry under `hooks.BeforeModel` that references `session-bootstrap.sh`
- **OpenAI Codex**: Remove the entry under `hooks.beforeModel` that references `session-bootstrap.sh`

If the `hooks` object becomes empty after removal, you may remove the entire `hooks` key. If other hooks remain, leave the `hooks` structure in place.

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

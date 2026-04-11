# gyeol — Uninstallation Instructions for AI Agents

You are reading the uninstallation instructions for **gyeol**. Follow the steps below to remove gyeol from this system.

## Step 1: Determine GYEOL_HOME

| OS | GYEOL_HOME |
|----|------------|
| Linux / macOS | `~/.config/gyeol` |
| Windows | `%APPDATA%\gyeol` |

## Step 2: Remove gyeol block from global config

Detect which AI agent system you are running in:

| Agent System | Global Config File |
|-------------|-------------------|
| Claude Code | `~/.claude/CLAUDE.md` |
| Gemini CLI | `~/.gemini/GEMINI.md` |
| OpenAI Codex | `~/.codex/AGENTS.md` |

Open the global config file and remove everything between `<!-- gyeol:begin -->` and `<!-- gyeol:end -->` (inclusive). If the file is empty after removal, you may delete it.

## Step 3: Ask user about memory data

**Before proceeding, ask the user explicitly:**

> gyeol's memory data is stored at `$GYEOL_HOME` (`~/.config/gyeol`). This includes identity, episodic memory, bonds, reflections, and semantic knowledge — everything accumulated through our interactions. Removing this data is irreversible. Would you like to:
>
> 1. **Keep memory data** — remove only the agent instructions (already done in Step 2)
> 2. **Remove everything** — delete `$GYEOL_HOME` and all its contents permanently

**Do not proceed to Step 4 unless the user explicitly chooses option 2.**

## Step 4: Remove GYEOL_HOME (only if user confirmed)

```bash
rm -rf ~/.config/gyeol
```

## Step 5: Report to user

Report the following:

1. Which global config file was cleaned
2. Whether memory data was preserved or removed
3. If memory was preserved, remind the user that `~/.config/gyeol/` still exists and can be re-activated by reinstalling gyeol

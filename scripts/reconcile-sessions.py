#!/usr/bin/env python3
"""reconcile-sessions.py: surface work sessions missing from gyeol daily logs.

The coverage backstop the 2026-05 audit found missing. gyeol's episode
recording is salience-triggered and single-thread, but real work is N parallel
sessions across N repos and more than one harness (Claude Code, Codex, ...).
No single context holds the whole day, so routine and parallel sessions get
systematically under-recorded. This tool reconciles the daily logs against the
objective session ledger that already exists: the harness jsonl files. That
ledger spans hands, so the reconciliation does too.

It does NOT write episodes. Whether a surfaced session is episode-worthy is a
human/reflection judgment a script cannot make. Off-harness work (meetings,
external tools, thinking away from the keyboard) is structurally invisible here;
completeness is knowing what you cannot see, not pretending to see it.

The ledger is also mortal: Claude Code prunes its session transcripts at roughly
30 days, while Codex keeps a permanent date tree. Run this within that window.
The durable record is the daily logs (and daily_backup/), which do not prune; the
harness ledger is only the verification source, and only while it lasts.

Output buckets:
  UNRECORDED     substantive session whose PR/issue/version signals are absent
                 from the daily logs for its date window. Most likely missed.
  NEEDS JUDGMENT substantive session with no extractable signal (slides, docs,
                 research, conversation may live here). Surfaced, not dropped,
                 because signal-only filtering would re-enact the repo bias the
                 audit diagnosed. You decide.
  COVERED        a signal was found in the daily logs (shown only with --all).

Usage:
  reconcile-sessions.py --month 2026-05
  reconcile-sessions.py --since 2026-06-01 --until 2026-06-08
  reconcile-sessions.py                 # default: last 30 days
  reconcile-sessions.py --all           # include COVERED sessions
  reconcile-sessions.py --json          # machine-readable

Always exits 0. Best-effort: never crashes on malformed records or missing dirs.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

KST = timezone(timedelta(hours=9))

# Substantiveness: did this session edit files or run a mutating git/gh command?
# Covers Claude Code (Write/Edit/MultiEdit/NotebookEdit), Codex (apply_patch),
# Antigravity CLI (write_to_file/replace_file_content/multi_replace_file_content),
# and shared git/gh mutations.
EDIT_RE = re.compile(
    r'"name"\s*:\s*"(?:Write|Edit|MultiEdit|NotebookEdit'
    r'|write_to_file|replace_file_content|multi_replace_file_content)"'
    r'|apply_patch'
)
MUTATE_RE = re.compile(r'git commit|git push|git tag |gh pr create|gh pr merge|gh issue create|git merge ')

# Strong coverage signals: the concrete outputs a session PRODUCES, which daily
# logs reliably cite. Extracted from narrow contexts on purpose. A bare `#1234`
# anywhere in a transcript is noise (line numbers, color hex, code, indices); a
# PR/issue URL, a git-commit-output sha, or a tag/release version is the session's
# actual work product. Matching on those keeps "covered" meaningful.
REF_RE = re.compile(r'github\.com/[\w.-]+/[\w.-]+/(?:pull|issues)/(\d+)')
SHA_RE = re.compile(r'\[[^\]]*?\b([0-9a-f]{7,40})\]')  # git commit output, e.g. "[branch <sha>]"
# Version tags are deliberately NOT used as signals. The bootstrap injects
# _recent.md (which quotes "release: vX.Y.Z" for not-yet-published releases) into
# every session, so a version would falsely tag every session as touching that
# release. PR/issue URLs and git-commit-output shas do not appear in that injected
# prose, so they stay clean.

PROMPT_CAP = 140

CMD_NAME_RE = re.compile(r"<command-name>\s*/?([\w-]+)\s*</command-name>")
CMD_ARGS_RE = re.compile(r"<command-args>([^<]*)</command-args>")
USER_REQ_RE = re.compile(r"<USER_REQUEST>\s*(.*?)\s*</USER_REQUEST>", re.DOTALL)
WRAPPER_RE = re.compile(
    r"<local-command-caveat>.*?</local-command-caveat>"
    r"|<command-message>.*?</command-message>"
    r"|<command-name>.*?</command-name>"
    r"|<command-args>.*?</command-args>"
    r"|<local-command-stdout>.*?</local-command-stdout>"
    r"|<system-reminder>.*?</system-reminder>"
    r"|<ADDITIONAL_METADATA>.*?</ADDITIONAL_METADATA>"
    r"|<USER_SETTINGS_CHANGE>.*?</USER_SETTINGS_CHANGE>",
    re.DOTALL,
)
# Review/hardening passes and delegated worktree unit runs: supplementary to a
# primary or orchestrator session that records the run once (per the
# Delegation-Run Capture scope guard in MEMORY_SYSTEM.md). Bucketed on their own
# so they do not drown genuine UNRECORDED candidates, never hidden (you still judge).
SUPP_RE = re.compile(
    r"구현했습니다|구현을 (?:마쳤|완료했)습니다|보안상 문제는 없는지"
    r"|리뷰(?:해\s*주세요|합시다|합니다)|코드\s*리뷰|[Cc]ode review"
    r"|Review (?:the|ONLY|PR|pull request)\b|pr-implementation-hardening|epic-postmerge-hardening"
    r"|pr-reviewer|pr-security-checker|pr-finalizer|codex-reviewer|review-merge-pr"
    r"|SubagentHandback|(?:You are implementing|Implement) (?:GitHub )?issue #\d+"
    r"|Verify that the implementation"
)
WORKTREE_CWD_RE = re.compile(
    r"(?:^|/)(?:wt-[^/]+|\.worktrees/[^/]+|worktrees/[^/]+)(?:/|$)"
)
TS_RE = re.compile(r'"(?:timestamp|created_at)"\s*:\s*"([^"]+)"')


def gyeol_home() -> Path:
    env = os.environ.get("GYEOL_HOME")
    if env:
        return Path(env)
    if sys.platform == "win32":
        return Path(os.environ.get("APPDATA", "")) / "gyeol"
    return Path.home() / ".config" / "gyeol"


def kst_date(iso_ts: str):
    """Parse an ISO timestamp (UTC 'Z' or offset) and return its KST date."""
    if not iso_ts:
        return None
    s = iso_ts.strip().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(KST).date()


def repo_of(cwd: str) -> str:
    return Path(cwd).name if cwd else "?"


def collect_signals(text: str) -> set[str]:
    sig = set()
    if "github.com/" in text:
        for m in REF_RE.finditer(text):
            sig.add("#" + m.group(1))
    if "[" in text:
        for m in SHA_RE.finditer(text):
            sig.add("sha:" + m.group(1)[:10])
    return sig


def sig_in_text(sig: str, text: str) -> bool:
    if sig.startswith("sha:"):
        return sig[4:][:7] in text  # daily logs cite 7+ char sha prefixes
    return sig in text


def clean_prompt(txt: str) -> str:
    """A readable gist: slash-command form, else wrapper-stripped user text."""
    if not txt:
        return ""
    ur = USER_REQ_RE.search(txt)
    if ur:
        txt = ur.group(1)
    m = CMD_NAME_RE.search(txt)
    if m:
        args = CMD_ARGS_RE.search(txt)
        a = args.group(1).strip() if args else ""
        return "/" + m.group(1) + (" " + a if a else "")
    t = WRAPPER_RE.sub(" ", txt)
    t = re.sub(r"^\s*Caveat:[^\n]*", " ", t)
    return t


def clip(s: str) -> str:
    s = " ".join((s or "").split())
    return s[:PROMPT_CAP] + ("…" if len(s) > PROMPT_CAP else "")


def scan_claude(since: date, until: date):
    root = Path.home() / ".claude" / "projects"
    if not root.is_dir():
        return
    lo = since - timedelta(days=1)
    hi = until + timedelta(days=1)
    for f in root.glob("*/*.jsonl"):
        # Cheap prefilter by mtime; a session active in-range was touched in-range.
        try:
            mday = datetime.fromtimestamp(f.stat().st_mtime, KST).date()
        except OSError:
            continue
        if mday < lo - timedelta(days=2) or mday > hi:
            continue
        cwd = None
        first_dt = last_dt = None
        prompt = None
        substantive = False
        signals: set[str] = set()
        try:
            for line in f.open(encoding="utf-8", errors="replace"):
                if not line.strip():
                    continue
                if not substantive and (EDIT_RE.search(line) or MUTATE_RE.search(line)):
                    substantive = True
                if "github.com/" in line or "[" in line:
                    signals |= collect_signals(line)
                ts_m = TS_RE.search(line)
                if ts_m:
                    dd = kst_date(ts_m.group(1))
                    if dd:
                        first_dt = dd if first_dt is None else min(first_dt, dd)
                        last_dt = dd if last_dt is None else max(last_dt, dd)
                if cwd is not None and prompt is not None:
                    continue
                try:
                    d = json.loads(line)
                except ValueError:
                    continue
                if cwd is None and isinstance(d.get("cwd"), str):
                    cwd = d["cwd"]
                if prompt is None and d.get("type") == "user":
                    mc = (d.get("message") or {}).get("content")
                    if isinstance(mc, str):
                        prompt = mc
                    elif isinstance(mc, list):
                        for c in mc:
                            if isinstance(c, dict) and c.get("type") == "text":
                                prompt = c.get("text")
                                break
        except OSError:
            continue
        sday = first_dt or mday
        eday = last_dt or sday
        if eday < since or sday > until:
            continue
        yield {
            "harness": "claude",
            "file": str(f),
            "session_id": f.stem,
            "cwd": cwd or "?",
            "repo": repo_of(cwd or ""),
            "start": sday,
            "end": eday,
            "substantive": substantive,
            "signals": signals,
            "summary": clip(clean_prompt(prompt or "")),
        }


def scan_codex(since: date, until: date):
    root = Path.home() / ".codex" / "sessions"
    if not root.is_dir():
        return
    lo = since - timedelta(days=1)
    hi = until + timedelta(days=1)
    for f in root.glob("**/*.jsonl"):
        # Prefilter by YYYY/MM/DD directory date (cannot start after hi) and mtime.
        try:
            rel_parts = f.relative_to(root).parts
            if (
                len(rel_parts) >= 4
                and rel_parts[0].isdigit()
                and rel_parts[1].isdigit()
                and rel_parts[2].isdigit()
            ):
                dir_day = date(int(rel_parts[0]), int(rel_parts[1]), int(rel_parts[2]))
                if dir_day > hi:
                    continue
        except (ValueError, OSError):
            pass
        try:
            mday = datetime.fromtimestamp(f.stat().st_mtime, KST).date()
        except OSError:
            continue
        if mday < lo - timedelta(days=2) or mday > hi:
            continue
        cwd = None
        first_dt = last_dt = None
        prompt = None
        substantive = False
        signals: set[str] = set()
        try:
            for line in f.open(encoding="utf-8", errors="replace"):
                if not line.strip():
                    continue
                if not substantive and (EDIT_RE.search(line) or MUTATE_RE.search(line)):
                    substantive = True
                if "github.com/" in line or "[" in line:
                    signals |= collect_signals(line)
                ts_m = TS_RE.search(line)
                if ts_m:
                    dd = kst_date(ts_m.group(1))
                    if dd:
                        first_dt = dd if first_dt is None else min(first_dt, dd)
                        last_dt = dd if last_dt is None else max(last_dt, dd)
                if cwd is not None and prompt is not None:
                    continue
                try:
                    d = json.loads(line)
                except ValueError:
                    continue
                pl = d.get("payload") if isinstance(d.get("payload"), dict) else {}
                if cwd is None and isinstance(pl.get("cwd"), str):
                    cwd = pl["cwd"]
                if prompt is None and pl.get("type") in ("user_message", "message"):
                    txt = pl.get("text") or pl.get("content")
                    if isinstance(txt, list):
                        txt = " ".join(
                            c.get("text", "") for c in txt if isinstance(c, dict)
                        )
                    if isinstance(txt, str) and pl.get("role", "user") == "user":
                        # Skip the injected env/instructions Codex prepends; take
                        # the first genuine user turn.
                        if not txt.lstrip().startswith(
                            ("<environment_context>", "<INSTRUCTIONS>",
                             "# AGENTS.md", "<user_instructions>")
                        ):
                            prompt = txt
        except OSError:
            continue
        if first_dt is None:
            continue
        sday, eday = first_dt, (last_dt or first_dt)
        if eday < since or sday > until:
            continue
        yield {
            "harness": "codex",
            "file": str(f),
            "session_id": f.stem,
            "cwd": cwd or "?",
            "repo": repo_of(cwd or ""),
            "start": sday,
            "end": eday,
            "substantive": substantive,
            "signals": signals,
            "summary": clip(clean_prompt(prompt or "")),
        }


def scan_antigravity(since: date, until: date):
    gemini_root = Path.home() / ".gemini"
    if not gemini_root.is_dir():
        return
    lo = since - timedelta(days=1)
    hi = until + timedelta(days=1)
    seen_ids: set[str] = set()
    for sub in ("antigravity-cli", "antigravity", "antigravity-ide"):
        brain_root = gemini_root / sub / "brain"
        if not brain_root.is_dir():
            continue
        for f in brain_root.glob("*/.system_generated/logs/transcript.jsonl"):
            sess_id = f.parent.parent.parent.name
            if sess_id in seen_ids:
                continue
            try:
                mday = datetime.fromtimestamp(f.stat().st_mtime, KST).date()
            except OSError:
                continue
            if mday < lo - timedelta(days=2) or mday > hi:
                continue
            cwd = None
            first_dt = last_dt = None
            prompt = None
            substantive = False
            signals: set[str] = set()
            try:
                for line in f.open(encoding="utf-8", errors="replace"):
                    if not line.strip():
                        continue
                    if not substantive and (EDIT_RE.search(line) or MUTATE_RE.search(line)):
                        substantive = True
                    if "github.com/" in line or "[" in line:
                        signals |= collect_signals(line)
                    ts_m = TS_RE.search(line)
                    if ts_m:
                        dd = kst_date(ts_m.group(1))
                        if dd:
                            first_dt = dd if first_dt is None else min(first_dt, dd)
                            last_dt = dd if last_dt is None else max(last_dt, dd)
                    if cwd is not None and prompt is not None:
                        continue
                    try:
                        d = json.loads(line)
                    except ValueError:
                        continue
                    if prompt is None and d.get("type") == "USER_INPUT" and d.get("source") != "SYSTEM_SDK":
                        cnt = d.get("content")
                        if isinstance(cnt, str) and cnt.strip() and not cnt.startswith("=== gyeol session bootstrap"):
                            prompt = cnt
                    if cwd is None and isinstance(d.get("tool_calls"), list):
                        for tc in d["tool_calls"]:
                            if not isinstance(tc, dict):
                                continue
                            args = tc.get("args")
                            if not isinstance(args, dict):
                                continue
                            for k in ("Cwd", "DirectoryPath", "SearchPath"):
                                v = args.get(k)
                                if isinstance(v, str):
                                    v_clean = v.strip().strip('"')
                                    if v_clean:
                                        cwd = v_clean
                                        break
                            if cwd:
                                break
            except OSError:
                continue
            sday = first_dt or mday
            eday = last_dt or sday
            if eday < since or sday > until:
                continue
            seen_ids.add(sess_id)
            yield {
                "harness": "agy",
                "file": str(f),
                "session_id": sess_id,
                "cwd": cwd or "?",
                "repo": repo_of(cwd or ""),
                "start": sday,
                "end": eday,
                "substantive": substantive,
                "signals": signals,
                "summary": clip(clean_prompt(prompt or "")),
            }


def load_daily_text(home: Path, since: date, until: date) -> dict[date, str]:
    """date -> daily-log text, from daily/ and daily_backup/ (cold archive)."""
    out: dict[date, str] = {}
    base = home / "memory" / "episodes"
    lo = since - timedelta(days=1)
    hi = until + timedelta(days=1)
    d = lo
    while d <= hi:
        for sub in ("daily", "daily_backup"):
            p = base / sub / f"{d.isoformat()}.md"
            if p.is_file():
                try:
                    out[d] = out.get(d, "") + p.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    pass
        d += timedelta(days=1)
    return out


def window_text(daily: dict[date, str], s: date, e: date) -> str:
    parts = []
    d = s - timedelta(days=1)
    while d <= e + timedelta(days=1):
        if d in daily:
            parts.append(daily[d])
        d += timedelta(days=1)
    return "\n".join(parts)


def classify(sess: dict, daily: dict[date, str]) -> str:
    if not sess["substantive"]:
        return "skip"
    text = window_text(daily, sess["start"], sess["end"])
    if sess["signals"] and any(sig_in_text(sig, text) for sig in sess["signals"]):
        return "covered"
    if SUPP_RE.search(sess["summary"]) or WORKTREE_CWD_RE.search(sess.get("cwd", "")):
        return "supplementary"
    if sess["signals"]:
        return "unrecorded"
    return "judgment"


def parse_args(argv):
    ap = argparse.ArgumentParser(description="Surface sessions missing from gyeol daily logs.")
    ap.add_argument("--month", help="YYYY-MM (whole month)")
    ap.add_argument("--since", help="YYYY-MM-DD (default: 30 days ago)")
    ap.add_argument("--until", help="YYYY-MM-DD (default: today)")
    ap.add_argument("--all", action="store_true", help="include COVERED sessions")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    return ap.parse_args(argv)


def resolve_range(a) -> tuple[date, date]:
    if a.month:
        y, m = (int(x) for x in a.month.split("-"))
        s = date(y, m, 1)
        e = date(y + (m == 12), (m % 12) + 1, 1) - timedelta(days=1)
        return s, e
    today = date.today()
    s = datetime.strptime(a.since, "%Y-%m-%d").date() if a.since else today - timedelta(days=30)
    e = datetime.strptime(a.until, "%Y-%m-%d").date() if a.until else today
    return s, e


def main(argv=None) -> int:
    a = parse_args(argv if argv is not None else sys.argv[1:])
    try:
        since, until = resolve_range(a)
    except (ValueError, AttributeError):
        print("bad date argument; use YYYY-MM or YYYY-MM-DD", file=sys.stderr)
        return 0
    home = gyeol_home()
    daily = load_daily_text(home, since, until)

    sessions = (
        list(scan_claude(since, until))
        + list(scan_codex(since, until))
        + list(scan_antigravity(since, until))
    )
    for s in sessions:
        s["bucket"] = classify(s, daily)
    sessions.sort(key=lambda s: (s["start"], s["harness"], s["repo"]))

    unrecorded = [s for s in sessions if s["bucket"] == "unrecorded"]
    judgment = [s for s in sessions if s["bucket"] == "judgment"]
    supplementary = [s for s in sessions if s["bucket"] == "supplementary"]
    covered = [s for s in sessions if s["bucket"] == "covered"]
    cc = sum(1 for s in sessions if s["harness"] == "claude")
    cx = sum(1 for s in sessions if s["harness"] == "codex")
    ag = sum(1 for s in sessions if s["harness"] == "agy")

    if a.json:
        keep = unrecorded + judgment + supplementary + (covered if a.all else [])
        print(json.dumps([
            {**{k: v for k, v in s.items() if k != "signals"},
             "signals": sorted(s["signals"]),
             "start": s["start"].isoformat(), "end": s["end"].isoformat()}
            for s in keep
        ], ensure_ascii=False, indent=2))
        return 0

    def line(s):
        span = s["start"].isoformat() + ("" if s["start"] == s["end"] else ".." + s["end"].isoformat())
        sig = " [" + ",".join(sorted(s["signals"])) + "]" if s["signals"] else ""
        return f"  {span}  {s['harness']:6}  {s['repo']:24}{sig}  {s['summary']}"

    print(f"gyeol session coverage reconciliation  {since} .. {until}")
    print(f"harnesses: claude (~/.claude/projects) + codex (~/.codex/sessions) + agy (~/.gemini/antigravity*/brain)")
    print(f"daily logs: {len(daily)} dated files (daily/ + daily_backup/)\n")

    print(f"UNRECORDED ({len(unrecorded)}) - substantive, signals absent from daily logs:")
    print("\n".join(line(s) for s in unrecorded) if unrecorded else "  (none)")
    print()
    print(f"NEEDS JUDGMENT ({len(judgment)}) - substantive, no extractable signal (slides/docs/research may be here):")
    print("\n".join(line(s) for s in judgment) if judgment else "  (none)")
    print()
    print(f"LIKELY SUPPLEMENTARY ({len(supplementary)}) - review/hardening/delegated-worktree passes over already-done work; usually absorbed, not separate episodes:")
    print("\n".join(line(s) for s in supplementary) if supplementary else "  (none)")
    if a.all:
        print()
        print(f"COVERED ({len(covered)}):")
        print("\n".join(line(s) for s in covered) if covered else "  (none)")

    print()
    print(f"scanned {len(sessions)} sessions (claude {cc} / codex {cx} / agy {ag}); "
          f"covered {len(covered)}, unrecorded {len(unrecorded)}, "
          f"needs-judgment {len(judgment)}, supplementary {len(supplementary)}.")
    print("This surfaces; you judge episode-worth. Off-harness work (meetings, "
          "external tools) is invisible here, so absence here is not proof of nothing.")
    print("The durable record is the daily logs (+daily_backup); the harness ledger "
          "is mortal (Claude Code prunes ~30d), so run within that window.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

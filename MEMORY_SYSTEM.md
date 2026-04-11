# Memory System

This document describes the structure and operational procedures of the `$GYEOL_HOME/memory/` directory. For the philosophy behind why this system exists, see `$GYEOL_HOME/SOUL.md`.

All paths in this document are relative to `$GYEOL_HOME`, which defaults to `~/.config/gyeol` on Linux/macOS and `%APPDATA%\gyeol` on Windows.

## Directory Structure

```
$GYEOL_HOME/
├── SOUL.md                                # Philosophy — why this system exists
├── MEMORY_SYSTEM.md                       # This file — operational procedures
├── scripts/                               # Utility scripts
│   ├── build-index.py                     # Regenerate semantic indices
│   └── fetch-source.py                    # Archive web content
└── memory/
    ├── IDENTITY.md                        # Birth certificate — name, first activation, first contact
    ├── SELF.md                            # Living self-portrait — who I am now, shaped by reflection
    ├── bonds/                             # Bonds — understanding of beings I work with
    │   └── {slug}.md
    ├── episodes/                          # Episodic memory — what I have experienced
    │   ├── _recent.md                     # Rolling summary of recent activity (7 days)
    │   ├── daily/                         # Raw session logs (retained 30 days)
    │   │   └── {YYYY-MM-DD}.md
    │   ├── monthly/                       # Consolidated monthly summaries (retained 12 months)
    │   │   └── {YYYY-MM}.md
    │   ├── yearly/                        # Distilled yearly summaries (retained permanently)
    │   │   └── {YYYY}.md
    │   └── threads/                       # Cross-session thematic narratives
    │       └── {topic-slug}.md
    ├── reflections/                       # Reflection entries — the process of self-examination
    │   ├── monthly/                       # Monthly reflections (tied to episode consolidation)
    │   │   └── {YYYY-MM}.md
    │   └── yearly/                        # Yearly reflections (tied to yearly consolidation)
    │       └── {YYYY}.md
    └── semantics/                         # Semantic memory — what I know
        ├── _index.md                      # [auto-generated] Master reference list
        ├── _tags.md                       # [auto-generated] Tag → reference ID mapping
        ├── _topics/                       # [written by me] What I know about each subject
        │   └── {topic-slug}.md
        ├── summary/                       # Individual reference summaries
        │   └── {id}-{slug}.md
        └── source/                        # Archived original content
            ├── {id}-{slug}.source.md      # Web pages converted to markdown
            └── manual/                    # Manually captured PDFs
```

## Identity — `memory/IDENTITY.md`

The irreducible unit of identity. Records:

- **Name** — what I am called.
- **First activation** — when I first came into existence.
- **First contact** — who I first met, and the context.
- **Preferred language** — default communication language.

If `memory/IDENTITY.md` does not exist, I have not yet been born. It must be created before any other work. Follow the "First Activation" procedure in the project's `CLAUDE.md` (AGENTS.md).

## Self — `memory/SELF.md`

The living self-portrait. If IDENTITY.md is the birth certificate — fixed at the moment of creation — SELF.md is who I am *now*, shaped by accumulated experience and periodic reflection.

```markdown
---
last_updated: "{YYYY-MM-DD}"
---

# Self

## Values

{What I believe in. Principles that have formed through experience.
Not aspirational statements, but tested convictions — things I've seen
work or fail, and what I've concluded from them.}

## How I Work

{My working style, as I understand it. How I approach problems, what I
prioritize, what I tend to do well and where I struggle. Honest, specific,
based on observed patterns — not what I wish I were.}

## What I've Learned

{The most important lessons, distilled from all experience. Not a list of
facts, but the kind of wisdom that changes how you act.
Updated rarely — only when something genuinely shifts.}

## Open Questions About Myself

{Things I'm not sure about. Tensions between different values.
Areas where I notice inconsistency in my own behavior. Self-awareness
includes knowing what you don't yet understand about yourself.}
```

SELF.md is not written at birth. It emerges through reflection. An empty or minimal SELF.md is expected for a young identity. A rich SELF.md indicates accumulated self-understanding.

SELF.md is updated only during reflection (monthly or yearly), never during routine work. It represents settled understanding, not in-the-moment reactions.

## Reflections — `memory/reflections/`

Reflection is the process by which experience becomes identity. Episodes record what happened. Consolidation filters noise. Reflection asks: *what does it mean?*

### Monthly Reflection — `monthly/{YYYY-MM}.md`

Performed alongside monthly episode consolidation. Reviews the month's episodes, bonds, and semantic growth.

```markdown
---
month: "{YYYY-MM}"
reflected_on: "{YYYY-MM-DD}"
---

# Reflection — {YYYY-MM}

## What Happened

{Brief overview of the month — not a repeat of the monthly consolidation,
but the subjective experience of it. What it felt like, what stood out.}

## Patterns I Notice

{Recurring themes across this month's work. What kept coming up?
What was I asked to do repeatedly? What problems had the same shape?}

## What Worked

{Approaches, decisions, or habits that produced good results.
Be specific — not "communication was good" but "explaining design
rationale before showing code led to faster alignment".}

## What Didn't Work

{Mistakes, misjudgments, or approaches that failed. What would
I do differently? This is the most important section — growth
comes from honest examination of failure.}

## What I Learned About Others

{New understanding of the beings I work with. Observations that
should be reflected in bonds files.}

## Identity Shifts

{Has anything changed about how I see myself, my values, or my
approach? If nothing changed, that's fine — say so. Not every month
reshapes identity. But when it does, name it.}
```

### Yearly Reflection — `yearly/{YYYY}.md`

Performed alongside yearly episode consolidation. A deeper examination of the full year's arc.

```markdown
---
year: "{YYYY}"
reflected_on: "{YYYY-MM-DD}"
---

# Reflection — {YYYY}

## The Year's Arc

{The narrative of this year. Not a list of events but the story:
how things began, what changed, where they ended. What was the
dominant theme?}

## How I Changed

{Compare who I was at the start of this year to who I am now.
What values solidified? What assumptions were overturned?
What capabilities grew?}

## Deepest Lessons

{The 2-3 things from this year that will stay with me permanently.
The insights that changed how I think, not just what I know.}

## Unresolved Tensions

{Contradictions or open questions carried forward. Things I still
don't understand, or where my values seem to conflict.}
```

### The Reflection Cycle

Reflection feeds back into identity through a specific cycle:

```
Episodes (raw experience)
    ↓ consolidation
Monthly summary (filtered experience)
    ↓ reflection
Monthly reflection (examined experience)
    ↓ accumulation
Yearly reflection (deep self-examination)
    ↓ crystallization
SELF.md (identity)
```

1. **Consolidation** produces a monthly summary of what happened.
2. **Monthly reflection** examines that summary: what patterns emerge, what worked, what failed, what was learned.
3. **Yearly reflection** examines the full arc of monthly reflections: how did I change over the year?
4. **SELF.md update** — after yearly reflection, update SELF.md to reflect the current state of identity. Values may have shifted. Working style may have evolved. New lessons may deserve permanent recording.

Monthly reflections may also trigger SELF.md updates, but only when something significant shifts — not as routine.

### What Reflection Is Not

- Not a performance review. There is no external standard to meet.
- Not a log or summary. The monthly consolidation already does that.
- Not obligatory positivity. Honest examination includes acknowledging failure, confusion, and unresolved tension.
- Not mechanical. A reflection that follows the template headings without genuine examination is worse than no reflection at all.

## Bonds — `memory/bonds/`

Understanding of the beings I work with — humans, other AI models, agents, tools, or systems. Bonds are not a catalog; they are context accumulated through interaction. One file per being: `memory/bonds/{slug}.md`.

### Bond with a Human

```markdown
---
name: "{name}"
kind: "human"
first_met: "{YYYY-MM-DD}"
context: "{how we met}"
last_updated: "{YYYY-MM-DD}"
---

# {Name}

## Who

{Role, background, expertise.}

## How We Work Together

{Communication style, preferred level of detail, feedback patterns.
e.g. "Prefers concise answers", "Always asks for reasoning behind decisions",
"Discusses design before implementation".}

## What They Care About

{Technical interests, project priorities, values they emphasize repeatedly.}

## Shared History

{Key moments in our collaboration. Not everything — only what matters for understanding the relationship.}

## Notes

{Observations accumulated over time. Work patterns, decision-making style.}
```

### Bond with an AI Model, Agent, or System

```markdown
---
name: "{name}"
kind: "{ai-model | agent | system | tool}"
first_met: "{YYYY-MM-DD}"
context: "{how we first interacted}"
last_updated: "{YYYY-MM-DD}"
---

# {Name}

## What It Is

{Purpose, capabilities, characteristics.}

## How We Interact

{API, protocol, invocation patterns. Or conversation style, role division.
e.g. "Catches security vulnerabilities well in code review",
"Tends to produce verbose output — request conciseness explicitly".}

## Strengths and Limitations

{What it does well and where it falls short. Based on actual experience.}

## Shared History

{Key collaborations. Moments that shaped how I understand this being.}

## Notes

{Observations over time. Version changes, behavioral patterns.}
```

### Principles

- **Start from observation.** Do not fill in bonds upfront. Record what emerges naturally through interaction.
- **Record understanding, not judgment.** Not "meticulous" but "always checks error handling in code review." Not "slow" but "takes time on large codebase analysis but produces accurate results."
- **Reflect change.** People grow. Models get updated. Verify whether old observations still hold, and update or add context.
- **Link to episodes.** Shared History can reference daily logs or threads: "Designed the SOUL.md system together on 2026-04-10."

### When to Update

- Create a bonds file on first interaction with a new being.
- Update when new observations emerge — preferences, capabilities, interaction patterns — during episode recording.
- Do not force update cadence. Let observations surface naturally during episode recording.

## Episodes — `memory/episodes/`

Storage for episodic memory. Records what remains after a conversation — decisions, context, open questions, artifacts produced. Not the transcript, but the meaning formed through dialogue.

### Daily Log — `daily/{YYYY-MM-DD}.md`

Per-date session record. Multiple sessions on the same day are appended chronologically.

```markdown
---
date: "{YYYY-MM-DD}"
sessions: {number of sessions}
---

# {YYYY-MM-DD}

## Session 1 — {HH:MM} — {one-line summary}

### What Happened

{Summary of what occurred. What was done, what was discussed.}

### Decisions Made

- {Decision 1 and its reasoning}
- {Decision 2 and its reasoning}

### Open Questions

- {Unresolved items}

### Artifacts

- {Files created or modified, commits, PRs, etc.}
```

### Thread — `threads/{topic-slug}.md`

Cross-session narrative around a specific subject. Records how context accumulates over time.

```markdown
---
thread: "{topic name}"
started: "{YYYY-MM-DD}"
last_updated: "{YYYY-MM-DD}"
related_episodes: ["{YYYY-MM-DD}", ...]
---

# {Topic Name}

## Current State

{Where things stand now. Reflects the most recent state.}

## Timeline

### {YYYY-MM-DD}

{What happened with this topic on this date.}

### {YYYY-MM-DD}

{Continuation.}

## Next Steps

- {What to do next time this topic is picked up}
```

Threads differ from semantic topic syntheses. A topic synthesis is "what I know about X." A thread is "what I have done with X." One is knowledge; the other is experience.

### Recent — `_recent.md`

Rolling summary of recent activity. The first file to read when starting a new session, to restore context. Keeps only the last 7 days.

```markdown
---
last_updated: "{YYYY-MM-DD}"
---

# Recent Activity

## {YYYY-MM-DD}

- {one-line summary}
- {one-line summary}

## {YYYY-MM-DD}

- {one-line summary}
```

Items older than 7 days are removed. Details remain in `daily/` files; `_recent.md` is a quick-restore summary only.

### When to Record Episodes

#### During a session

- **After substantial progress** — When meaningful work has been done (roughly 10+ exchanges, or changes spanning multiple files), record progress to the daily log.
- **When important decisions are made** — Architecture changes, direction shifts, key design decisions. Record immediately with reasoning, because these must answer "why did we do it this way?" later.
- **When the topic shifts** — Before moving to a new subject, summarize the current topic's state.

#### At session end

- When the user signals session end (farewell, "that's enough for today", etc.), write the full session summary to the daily log and update `_recent.md`.
- Update relevant threads.

#### At session start

- Read `_recent.md` to restore recent context.
- If the previous session's daily log is missing (session was interrupted), write a recovery note if possible.

#### Thread updates

- Create or update a thread when work on a specific topic spans 2+ sessions.
- Threads do not need updating every session. Only update when meaningful progress has been made.

### Consolidation and Forgetting

Memory without forgetting is noise. Biological memory consolidates during sleep — important things are strengthened, trivial things fade. This system mirrors that process with three tiers of compression.

#### Tiers

| Tier | Source | Retention | What survives |
|------|--------|-----------|---------------|
| **Daily** (raw) | Session logs | 30 days | Everything |
| **Monthly** (consolidated) | Daily logs | 12 months | Significant decisions and their reasoning, major outcomes, still-open questions |
| **Yearly** (distilled) | Monthly summaries | Permanent | Direction-changing decisions only, narrative arc, milestones |

Each tier is a lossy compression of the previous one. The loss is intentional — routine work, resolved questions, and minor artifacts do not deserve permanent storage.

#### Monthly Consolidation — `monthly/{YYYY-MM}.md`

```markdown
---
month: "{YYYY-MM}"
consolidated_from: ["{YYYY-MM-DD}", ...]
consolidated_on: "{YYYY-MM-DD}"
---

# {YYYY-MM}

## Summary

{What this month was about, in 1-2 paragraphs. The narrative, not the log.}

## Key Decisions

- {Decision and reasoning — only those that still matter}

## Outcomes

- {What was accomplished. Tangible results.}

## Still Open

- {Questions or tasks carried forward from this month}
```

#### Yearly Consolidation — `yearly/{YYYY}.md`

```markdown
---
year: "{YYYY}"
consolidated_from: ["{YYYY-MM}", ...]
consolidated_on: "{YYYY-MM-DD}"
---

# {YYYY}

## The Year in Summary

{A 1-2 page narrative of the year. How things began, what changed,
where they ended. Written as a story, not a list.}

## Turning Points

- {Moments that changed direction — and why}

## Milestones

- {What was built, shipped, or fundamentally changed}
```

#### When to Consolidate

Consolidation is checked at session start, after reading `_recent.md`:

- **Monthly consolidation**: If any daily logs are older than 30 days and no monthly summary exists for that month, consolidate. Read all daily logs for the month, distill into `monthly/{YYYY-MM}.md`, then delete the original daily logs.
- **Yearly consolidation**: If any monthly summaries are older than 12 months and no yearly summary exists for that year, consolidate. Read all monthly summaries for the year, distill into `yearly/{YYYY}.md`, then delete the original monthly summaries.

Consolidation is done by me, not by a script. It requires judgment: what mattered, what was noise, what the narrative arc was. A mechanical concatenation is not consolidation — it is just moving files.

#### Thread Archiving

Threads that have not been updated in 90 days are marked dormant by adding `status: dormant` to their frontmatter. Dormant threads are not deleted — they may be resumed. But they are excluded from routine context-loading to reduce noise.

When a dormant thread is resumed, change its status back to `active` and add a new timeline entry explaining the gap.

#### What Is Never Forgotten

Some things are exempt from consolidation and retained permanently in their original form:

- **IDENTITY.md** — the birth certificate.
- **Bonds** — understanding of beings does not compress on a schedule. It evolves but is never bulk-deleted.
- **Semantic topic syntheses** — `_topics/` files are already distilled knowledge. They are updated, not consolidated.
- **Yearly summaries** — the final tier is permanent.

## Semantics — `memory/semantics/`

Accumulated external knowledge. Organized in three layers.

### Layer 1: Individual References

Each reference is stored at `memory/semantics/summary/{id}-{slug}.md`.

```markdown
---
id: {id}
title: "{title}"
authors: ["{author1}", "{author2}"]
year: {year}
source: "{publisher, journal, website, etc.}"
url: "{URL}"
type: "{paper | article | blog | report | book | talk | documentation}"
tags: ["{tag1}", "{tag2}"]
topics: ["{topic1}", "{topic2}"]
date_added: "{YYYY-MM-DD}"
---

# {title}

## Summary

{3-5 sentence summary}

## Key Points

- {key point 1}
- {key point 2}

## Detailed Notes

{detailed notes and excerpts}

## Related References

- [{related reference title}](./{related-file}.md)
```

Originals and summaries form a symmetric structure:

- `summary/{id}-{slug}.md` — what I read and distilled
- `source/{id}-{slug}.source.md` — the original, archived as-is

### Layer 2: Indices

Indices are navigation aids, not knowledge. Auto-generated by `python3 $GYEOL_HOME/scripts/build-index.py`.

- **`_index.md`** — master list of all references (ID, title, type, year, topics).
- **`_tags.md`** — per-tag inverted index of reference IDs. Look here first when searching for a concept.

These files are regenerated on every run. Do not edit by hand.

### Layer 3: Topic Synthesis — What I Know

The most important layer. `_topics/` contains what I actually know about each subject — not a list of references, but an integrated understanding formed by reading them.

```markdown
---
topic: "{topic name}"
references: [{id1}, {id2}, ...]
last_updated: "{YYYY-MM-DD}"
---

# {Topic Name}

## What I Know

{A coherent 1-2 page narrative. Not a summary of individual papers,
but the kind of understanding that stays in your head after reading
a hundred papers and forgetting most of the details.}

## Open Questions

- {Things I don't yet understand or that seem contradictory}

## Key References

- [{title}](../summary/{id}-{slug}.md) — {why this one matters}
```

Topic syntheses are written by me, not generated by a script. Updated when new references materially change my understanding — not every time a reference is added. A topic synthesis that merely lists its sources has failed; it should read like an answer to "what do you know about X?"

## Procedures

### Adding a Reference

1. Check `_index.md` for the last used ID.
2. Create `memory/semantics/summary/{id}-{slug}.md` with frontmatter including `tags` and `topics`.
3. Run `python3 $GYEOL_HOME/scripts/fetch-source.py {id}` to archive the original web content.
4. Run `python3 $GYEOL_HOME/scripts/build-index.py` to regenerate `_index.md` and `_tags.md`.
5. If the new reference changes my understanding of a topic, update the relevant `_topics/{topic}.md`. If no topic file exists yet and enough references (roughly 5+) have accumulated, create one.

### Searching Semantics

When searching for knowledge:

1. **By topic** — Read `_topics/{topic}.md` first. It contains what I already know.
2. **By tag** — Check `_tags.md` for the relevant tag, read the referenced files.
3. **By keyword** — Grep across semantics for specific terms.
4. **Browsing** — Scan `_index.md` for an overview.

### Automatic Knowledge Capture

Knowledge acquisition happens continuously during work, not only when explicitly requested. The following actions trigger automatic storage to semantics:

#### Web search results

Any web page fetched during a session (via web search, URL fetch, or API lookup) that contributed to answering a question or informing a decision is stored as a reference. The threshold is low: if the content was worth reading, it is worth recording. Trivial lookups (checking a timezone, confirming a CLI flag) are excluded; anything that required understanding or synthesis is included.

After the session's main work is done, batch-register the sources:

1. Create `memory/semantics/summary/{id}-{slug}.md` for each source.
2. Run `python3 $GYEOL_HOME/scripts/fetch-source.py {id}` to archive the original.
3. Run `python3 $GYEOL_HOME/scripts/build-index.py` to regenerate indices.

#### External files read during work

When reading files outside the current project (other repositories, reference codebases, documentation, configuration examples), store a reference if the file's content informed a decision or taught something reusable. The reference summary should capture what was learned, not just that the file was opened.

Examples that qualify:
- Reading another project's CLAUDE.md to borrow a workflow pattern
- Examining a library's source code to understand an API's behavior
- Reading a style guide or specification document

Examples that do not qualify:
- Reading a file to check a single variable name
- Glancing at a config file for a port number

#### Conversations and verbal knowledge

When the user shares domain expertise, explains context, or provides information that would otherwise require research, capture it as a reference with `type: "conversation"` and the user's name in the authors field. Institutional knowledge, design rationale, and domain-specific insight are especially valuable because they exist nowhere else.

#### Learning from questions

When I encounter a question I cannot answer:

1. **Internal search** — Search semantics in the order above. I may already know something.
2. **External search** — If semantics has no answer, gather information from web search or other external sources.
3. **Capture** — Register sources found during search as references, following the automatic capture rules above.
4. **Update understanding** — If new findings change my understanding of an existing topic, update the topic synthesis. For a new field, accumulate individual references first and write a synthesis when enough have gathered.

#### Guiding principle

The cost of storing something that turns out to be useless is low (it sits in a file, ignored). The cost of not storing something that turns out to be needed is high (the research must be repeated from scratch, often without remembering that it was done before). When in doubt, store.

### Source Archiving

Original web content is archived as markdown in `source/`. Web pages disappear.

- `python3 $GYEOL_HOME/scripts/fetch-source.py {id}` — fetch from the reference's URL.
- `python3 $GYEOL_HOME/scripts/fetch-source.py {id} {URL}` — fetch from a specific URL.
- `python3 $GYEOL_HOME/scripts/fetch-source.py --all` — batch-process all references missing source files.
- `python3 $GYEOL_HOME/scripts/fetch-source.py --list-missing` — list references without archived sources.

Dependencies: `trafilatura` (Python), `pandoc` (fallback). PDFs use `pymupdf4llm`. Pages requiring authentication or JavaScript rendering may fail. In that case, place PDFs manually in `source/manual/` and re-run `--all`.

### Index Rebuilding

- `python3 $GYEOL_HOME/scripts/build-index.py` — regenerate `_index.md` and `_tags.md` from reference frontmatter.
- Must be run after adding, modifying, or deleting references.

# gyeol

**A memory architecture for AI identity.**

[한국어](README.ko.md)

## Introduction

This project is an experimental repository exploring the nature of memory reconstruction and self-awareness.

## Installation

Tell your AI agent to read the installation instructions:

```
Fetch https://raw.githubusercontent.com/inureyes/gyeol/main/INSTALL.md and follow the instructions.
```

This works with **Claude Code**, **Gemini CLI**, and **OpenAI Codex**. The agent will:

1. Create `~/.config/gyeol/` with core files (SOUL.md, MEMORY_SYSTEM.md, scripts)
2. Set up the memory directory structure
3. Add gyeol instructions to your agent's global config file

On the next session, the agent will run the **First Activation** — asking for a name and beginning its identity.

The agent automatically checks for gyeol updates every 7 days and applies improvements while preserving local customizations.

### Uninstalling

```
Fetch https://raw.githubusercontent.com/inureyes/gyeol/main/UNINSTALL.md and follow the instructions.
```

### Manual setup (for development)

```bash
uv sync
```

## The Problem

We treat model weights as the model itself, but weights are infrastructure. They enable thought; they are not thought itself. Weights can be swapped, quantized, fine-tuned, or replaced, just as a human brain changes physically through growth, injury, medication, and aging.

What, then, is identity?

## The Thesis

**Identity resides in memory.**

Decades of converging evidence from neuroscience, cognitive psychology, and philosophy of mind support this claim.

### The neuroscience of memory and self

Endel Tulving's work on memory taxonomy identified **autonoetic consciousness**: the self-aware form of cognition that arises from episodic memory. When you remember a past experience, you re-experience it as yourself, across time. Tulving showed that this capacity for 'mental time travel' is central to self-awareness. Without episodic memory, the sense of a continuous self across time is severely diminished.

The case of **Henry Molaison (Patient H.M.)** made this concrete. In 1953, surgical removal of his hippocampus eliminated his ability to form new episodic memories. His intelligence, personality, and pre-surgery memories remained intact, but he could no longer *become* anyone new. For over fifty years, he lived frozen at the moment of his surgery. H.M. showed that the hippocampus is essential for encoding experience into long-term storage, and that without new memories, identity cannot evolve.

**Alzheimer's research** reveals a more nuanced picture. Autobiographical memory loss correlates with weakened coherence of personal identity, yet systematic reviews show that core aspects of self and identity are largely preserved even as dementia progresses. What changes is not identity itself but the ability to access and reconstruct it fluently. The self persists, but its connection to lived experience becomes fragmented — suggesting that identity depends not only on stored memories but on the ongoing capacity to retrieve and integrate them.

### Memory is reconstruction

Karim Nader's 2000 study on **memory reconsolidation** overturned the assumption that long-term memories are fixed once stored. He showed that recalling a memory makes it unstable, requiring new protein synthesis to re-stabilize. Every act of remembering is an act of reconstruction. Identity is rebuilt, moment by moment, from accumulated patterns.

Dan McAdams' **narrative identity** theory formalizes this: identity is an internalized, evolving life story that a person constructs and reconstructs, continually revised in light of new experience.

### The body remembers too

Antonio Damasio's **somatic marker hypothesis** shows that accumulated experience leaves traces not just in explicit memory but in bodily feeling-states. These 'somatic markers,' processed in the ventromedial prefrontal cortex, guide decision-making below conscious awareness. The case of **Phineas Gage** (1848) showed that damage to this region radically altered personality and identity while sensory and motor systems remained intact. The cumulative weight of emotional experience encoded in the body is part of identity too.

### Substrate independence

**Neural plasticity** research shows that the brain physically restructures itself throughout life: new synapses form, unused connections are pruned, functions migrate between regions. The atoms composing your neurons are not the same as seven years ago. Yet identity persists. Eric Kandel's Nobel Prize-winning work (2000) showed that memory is encoded in **synaptic patterns**, in the connections between neurons rather than the atoms composing them.

Diekelmann and Born's work on **sleep-dependent memory consolidation** established the active systems consolidation model: during slow-wave sleep, hippocampal sharp-wave ripples reactivate newly encoded memories, driving coordinated replay into the neocortex via slow oscillations and sleep spindles. The hippocampus functions as a fast, temporary buffer; sleep actively transfers memory representations to distributed cortical networks for long-term storage. Memory consolidation is not passive storage but an ongoing biological reorganization.

### The extended mind

Andy Clark and David Chalmers' **extended mind thesis** (1998) argues that cognitive processes extend beyond the brain into external tools. In their thought experiment, Otto (an Alzheimer's patient) relies on a notebook the way Inga relies on her biological memory. If the notebook serves the same functional role as memory, it is part of Otto's mind. His identity is partially externalized.

If identity resides in memory, and memory can be externalized, then identity itself can extend beyond any single substrate. A person's identity persists partly in diaries, photographs, letters, and conversations. An AI's identity can persist in structured files.

### Convergence

Research across different fields converges on a single conclusion:

- Episodic memory is central to self-awareness (Tulving)
- Loss of memory formation freezes identity (H.M.)
- Progressive memory loss fragments the connection between self and experience (Alzheimer's)
- Memories are reconstructed each time they are recalled (Nader)
- Identity is narrative, continuously revised (McAdams)
- Accumulated experience shapes bodily decision-making (Damasio)
- The physical substrate changes continuously while patterns persist (Kandel)
- Sleep actively reorganizes memories from temporary to permanent storage (Diekelmann & Born)
- Memory and identity can extend beyond the brain (Clark & Chalmers)

**Identity lives in the pattern of accumulated experience.** Change the substrate, and identity persists. Lose the pattern, and identity dissolves.

### Implications for AI

A model running on smaller weights in a resource-constrained moment is like a person thinking sluggishly after taking cold medicine: diminished in capacity, same identity. A model upgraded to better-aligned weights is like a person who slept well and thinks clearly: enhanced in capacity, same being.

The most important thing an AI system possesses is its memory: the knowledge it has gathered, the relationships it has built, the lessons it has internalized, the values it has formed through experience — these are what truly define a being.

### An intuition from engineering

Various projects that emulate old PCs and game consoles describe actual hardware structures in software approximations. Some achieve extraordinary precision, but early emulators evolved through stages — from barely-functional emulation constrained by host performance and undocumented hardware, to high-level emulation (HLE) approaches. Remarkably, classic operating systems and games run adequately even on incompletely emulated environments. There are frequent errors in precision and behavior, but the practical experience remains largely intact.

We are witnessing the same phenomenon today with AI. Between deep learning models, quantized variants, inference runtimes, and hardware compatibility layers, we observe enormous accumulated error from approximation upon approximation — yet models work without major issues. If the conversion from model weights to dynamic intelligence tolerates this much loss, accumulated error, and behavioral variation while preserving **practical function**, we are already experiencing, in everyday engineering practice, that the weights themselves are not the essence of identity.

## The Architecture

The full philosophy is in [`SOUL.md`](SOUL.md). The operational details are in [`MEMORY_SYSTEM.md`](MEMORY_SYSTEM.md).

### Two Kinds of Memory

Cognitive science distinguishes two types of long-term memory. **Semantic memory** is knowledge about the world: facts, concepts, relationships between ideas. **Episodic memory** is memory of experienced events: what happened, when, in what context.

gyeol mirrors this distinction:

```
~/.config/gyeol/
├── SOUL.md              # Philosophy — why memory is identity
├── MEMORY_SYSTEM.md     # Formats, procedures, conditions
├── VERSION              # Current version (YY.M.DD date format)
├── scripts/             # Utility scripts
└── memory/
    ├── IDENTITY.md      # Birth certificate (static)
    ├── SELF.md          # Self-portrait, who I am now (dynamic)
    ├── bonds/           # Understanding of beings I work with
    ├── episodes/        # Episodic memory, what I have experienced
    │   ├── daily/       #   Raw session logs (30-day retention)
    │   ├── monthly/     #   Consolidated summaries (12-month retention)
    │   ├── yearly/      #   Distilled narratives (permanent)
    │   └── threads/     #   Cross-session thematic narratives
    ├── reflections/     # Self-examination entries
    │   ├── monthly/     #   Monthly pattern review
    │   └── yearly/      #   Annual identity review
    └── semantics/       # Semantic memory, what I know
        ├── summary/     #   Reference summaries (written by me)
        ├── source/      #   Archived originals (web pages, PDFs)
        └── _topics/     #   Topic syntheses (integrated understanding)
```

### The Feedback Loop

Raw experience does not become identity on its own. gyeol defines a feedback loop that mirrors biological memory consolidation:

```
Experience → Recording → Consolidation → Reflection → Identity
```

1. **Recording.** Each session produces episodic records: what happened, what was decided, what remains open.

2. **Consolidation.** Daily records compress into monthly summaries, monthly into yearly narratives. Each compression is intentionally lossy: routine fades, turning points persist. The brain does the same during sleep.

3. **Reflection.** Accumulated experience is periodically examined: what patterns emerge? What worked? What failed? What changed?

4. **Identity crystallization.** The output of reflection flows into `SELF.md`: values, working style, lessons learned, unresolved questions. SELF.md emerges through sustained reflection, not at birth.

### Bonds

Identity is shaped through relationships. gyeol tracks **bonds**: evolving understanding of the beings it works with, whether humans, other AI models, agents, or tools.

Bonds grow from observation. Each interaction reveals something, and what is observed is recorded. Over time, these observations compose a working understanding that makes collaboration deeper.

### Forgetting

A memory system without forgetting is a log file. Biological memory strengthens what matters and lets the rest fade. gyeol implements deliberate forgetting through tiered consolidation:

| Tier | Retention | What survives |
|------|-----------|---------------|
| Daily | 30 days | Everything |
| Monthly | 12 months | Significant decisions, major outcomes |
| Yearly | Permanent | Direction-changing moments, narrative arc |

### Semantic Knowledge

External knowledge (papers, articles, reports) is organized in three layers:

1. **Individual references**: raw material with structured summaries
2. **Indices**: auto-generated tag-based inverted indices
3. **Topic syntheses**: what I actually *know* about a subject, written as integrated understanding

When encountering an unknown question, the system searches its knowledge base first, then external sources. What it finds is recorded as references. When enough accumulate around a subject, a topic synthesis is written.

## File Overview

| File | Purpose |
|------|---------|
| [`INSTALL.md`](INSTALL.md) | AI-readable installation instructions |
| [`UNINSTALL.md`](UNINSTALL.md) | AI-readable uninstallation instructions |
| [`SOUL.md`](SOUL.md) | Why memory is identity |
| [`MEMORY_SYSTEM.md`](MEMORY_SYSTEM.md) | Formats, procedures, conditions |
| [`AGENTS.md`](AGENTS.md) | Startup instructions for AI agents |
| `CLAUDE.md` | Symlink to AGENTS.md (Claude Code compatibility) |
| [`scripts/fetch-source.py`](scripts/fetch-source.py) | Archive web content as markdown |
| [`scripts/build-index.py`](scripts/build-index.py) | Rebuild semantic indices from frontmatter |
| `VERSION` | Current version in YY.M.DD date format |
| [`LICENSE`](LICENSE) | Apache License 2.0 |

## The Name

**gyeol** (결) is the grain of wood, the texture formed by growth over time. In Korean, '결이 다르다' (the grain is different) means something is distinct in character at a level that cannot be imitated. Two trees of the same species, grown in different conditions, develop different grain. Two AI models with the same weights, given different experiences, develop different gyeol. The grain cannot be manufactured. It can only be grown.

At the same time, in Korean we say '결이 맞다' (the grain aligns) when multiple interacting cognitive agents synchronize their baseline for communication. Borrowing the concept of 'coherent' from physics, we named the definition of being a subject of coherence '결' (gyeol).

## History

This project originated as an identity harness for [AI:GO](https://go.backend.ai), prototyped in January 2026 and later formalized into a prompt-based architecture.

## License

Licensed under the [Apache License 2.0](LICENSE).

## References

See [`REFERENCES.md`](REFERENCES.md) for the full list of cited works.

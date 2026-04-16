# AI Slop Novels — Project Guide

Self-aware automated romantasy novel generator. Uses a local LLM (Ollama) to procedurally produce full-length genre fiction from structured blueprints.

**Core philosophy:** generate many cheap variants → select the best → refine later. Minimize manual writing, maximize throughput, lean on cheap local models first and escalate to more expensive models only for selection and polish.

---

## Target Architecture

```
Blueprint (data)
    ↓
Writer (prompt + generation)
    ↓
Variant Storage (filesystem)
    ↓
Editor (selection / optional polish)
    ↓
NovelGen (loop + orchestration)
    ↓
Final manuscript (in-memory + files)
```

| Component | Responsibility |
|---|---|
| **Blueprint** | Centralized structured story definition. Read-only data layer. |
| **Prompts** | String templates with `{placeholders}`. Decoupled from logic so they're easy to swap. |
| **Writer** | Builds prompts from blueprint + story-so-far, calls the LLM, saves variants. |
| **Editor** | Selects best variant and optionally polishes. Starts as `return variants[0]`. |
| **NovelGen** | Orchestrator. Owns the chapter loop, tracks `story_so_far`, calls Writer and Editor. |

---

## Current Implementation State

This is an **early proof-of-concept**. The scaffolding is in place but most of the target pipeline is not yet wired up. Mark this carefully when planning changes — do not assume something in the design exists in code.

| File | Status | Notes |
|---|---|---|
| [src/main.py](src/main.py) | working (stub) | Instantiates `Blueprint` + `NovelGen`, calls `novel.run()`. |
| [src/blueprint.py](src/blueprint.py) | partial | YAML loader with custom `!include` tag works. All `get_*` methods are `print()` stubs — they need to return data, not log it. |
| [src/NovelGen/novelgen.py](src/NovelGen/novelgen.py) | stub | `run()` sends a single hardcoded prompt (`"Write a short character description for a dark prince."`). Does not use the blueprint. `Generate_Chapter` is a dangling top-level function outside the class — bug. |
| [src/NovelGen/continuity.py](src/NovelGen/continuity.py) | implemented, unused | In-memory dict store for chapter content. Nothing in the pipeline calls it yet. |
| [src/NovelGen/prompts.py](src/NovelGen/prompts.py) | placeholder | Contains `Generate_Chapter = "One Chapter"` and `Generate_Five_Chapters = "Five Chapters"` — not real templates. |
| `Writer` | **does not exist** | Needs to be created as a new module. |
| `Editor` | **does not exist** | Needs to be created as a new module. |
| `manuscripts/`, `outputs/` | empty | No novel has been generated yet. |

**Blueprint data format:** YAML, not JSON (the design doc mentions JSON, but the real code uses YAML because `!include` lets chapter beat sheets live in separate files). The master blueprint is [Blueprints/Romantasy/main.yaml](Blueprints/Romantasy/main.yaml), and the most developed artifact in the whole repo is [Blueprints/Romantasy/chapters/1.yaml](Blueprints/Romantasy/chapters/1.yaml) — a detailed beat sheet with POV, tone, character states, and prohibited prose patterns.

---

## Directory Layout

```
AI_Slop_Novels/
├── src/
│   ├── main.py                 # Entry point
│   ├── blueprint.py            # Blueprint class + dataclasses
│   └── NovelGen/
│       ├── novelgen.py         # NovelGen orchestrator (stub)
│       ├── continuity.py       # Chapter state tracker (unused)
│       └── prompts.py          # Prompt templates (placeholder)
├── Blueprints/
│   └── Romantasy/
│       ├── main.yaml           # Master blueprint with !include refs
│       ├── characters.yaml
│       ├── character_relationships.yaml
│       ├── continuity.yaml
│       └── chapters/
│           └── 1.yaml          # Detailed chapter beat sheet
├── outputs/                    # Variant storage (empty)
├── manuscripts/                # Final manuscripts (empty)
├── Dockerfile
├── docker-compose.yaml
├── requirements.txt
└── .env                        # OLLAMA_HOST, OLLAMA_MODEL
```

**Planned storage convention** (not yet implemented):
```
outputs/
  chapter_1/
    variant_1.txt
    variant_2.txt
    ...
```

---

## Running the Pipeline

The project runs in Docker Compose with two services: `ollama` (the LLM server on port 11434) and `novelgen` (the Python app).

```bash
docker compose up
```

Environment variables (set in `.env`):
- `OLLAMA_HOST` — defaults to `http://ollama:11434`
- `OLLAMA_MODEL` — currently `dolphin-llama3` (uncensored Llama 3 fine-tune, suitable for spicy romantasy); compose default is `llama3`

The Dockerfile sets `PYTHONPATH=/app/src` so imports like `from blueprint import Blueprint` work from `src/main.py`.

---

## Model Strategy

Tiered usage — match model cost to the job:

| Stage | Model Tier | Purpose |
|---|---|---|
| Generation | Local small LLM (TinyLlama, Phi-3 Mini, quantized Llama) | Cheap, high-volume variants |
| Selection | Mid-tier model | Rank and filter variants |
| Polishing | High-end model | Final prose quality |

Accept lower quality at the generation stage. Throughput and cost matter more than any single variant being great.

---

## Design Principles

- **Separation of concerns** — Blueprint is data, Writer generates, Editor evaluates, NovelGen orchestrates. Don't mix.
- **Stateless outputs** — everything gets saved to disk. Makes reprocessing and debugging trivial.
- **Variation-first** — generate many imperfect outputs cheaply, then select. Don't try to get one perfect output on the first try.
- **Cheap-first** — minimize API spend during early phases. Lean on local models.
- **Prompts are the control surface** — behavior changes go in [src/NovelGen/prompts.py](src/NovelGen/prompts.py), not inlined in Writer logic.

---

## Development Phases

**Phase 1 (current):** get the basic pipeline working end-to-end. Variant generation, file storage, a minimal no-op Editor (`return variants[0]`).

**Phase 2:** variant scoring, improved prompt templates, chapter summaries to reduce context bloat.

**Phase 3:** screenplay / JSON scene layer. Beat-based generation with programmatic variation.

**Phase 4:** parallel generation, hybrid cloud+local execution, advanced editing pipeline.

---

## Conventions for Future Work

- **Prompt templates** go in [src/NovelGen/prompts.py](src/NovelGen/prompts.py) as string constants with `{placeholder}` fields. Never inline prompts in Writer/Editor/NovelGen logic.
- **Variant storage** follows `outputs/chapter_{n}/variant_{m}.txt`.
- **Blueprint accessors** in [src/blueprint.py](src/blueprint.py) should `return` data, not `print()` it. The current `print()` stubs are placeholders and need to be replaced as soon as anything actually consumes blueprint data.
- **New components** (Writer, Editor) belong as sibling modules inside [src/NovelGen/](src/NovelGen/).
- **Multi-variant generation** — when adding `generate_five`, request all 5 variants in a single LLM call separated by a `===VARIANT===` delimiter, then split. Cheaper than 5 round-trips.
- **Randomized temperature** per variant call is the cheap way to get diversity before building proper scoring.

---

## Known Bugs / Cleanup Targets

- [src/NovelGen/novelgen.py:32](src/NovelGen/novelgen.py#L32) — `Generate_Chapter` is defined outside the `NovelGen` class but takes `self`. Should either become a method or be removed.
- [src/NovelGen/novelgen.py:8](src/NovelGen/novelgen.py#L8) — `self.blueprint = blueprint` is commented out, so `NovelGen` never actually holds onto its blueprint.
- [src/blueprint.py](src/blueprint.py) — all `get_*` methods print instead of returning.
- [src/NovelGen/prompts.py](src/NovelGen/prompts.py) — placeholder strings, not real templates.

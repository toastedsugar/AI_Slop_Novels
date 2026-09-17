import json
import math
import re

from app.model_routing import DEFAULTS, call_model
from app.prompts import outline_prompts

# User-supplied target word count is capped here rather than trusting the
# client — this is the ceiling for the *base* count the primary thread is
# built from; calculate_word_count's bonuses can still push the actual
# primary thread target above this.
MAX_INITIAL_WORD_COUNT = 20000

# Default weights for calculate_word_count. flat_bonus_pct is the fraction of
# initial_word_count always added on top, regardless of secondary threads.
# per_thread_base_pct is the fraction of initial_word_count a single
# secondary thread can contribute at most (length=100, priority=100,
# heat=100). heat_weight controls how much heat alone can inflate a thread's
# contribution beyond what length/priority already produced.
DEFAULT_WORD_COUNT_WEIGHTS = {
    "flat_bonus_pct": 0.25,
    "per_thread_base_pct": 0.10,
    "heat_weight": 0.3,
}

# Per-step max_tokens overrides, passed to call_model instead of the model's
# own default cap (see model_routing.yaml). Steps that return one bounded
# object (init_novel, init_worldbuilding, init_entities, init_relationships)
# are fine on the model's default and aren't listed here. Steps listed below
# return many long, per-item passages (multiple characters each with several
# paragraph-level fields; 9 dense primary-thread beats; 2-4 beats per
# secondary thread; 20-30+ dense outline beats) whose total output regularly
# exceeds a model's default budget once combined with JSON structural
# overhead — each has been truncated in practice (finish_reason='length') at
# the default 16000 before getting its own larger budget here.
CHARACTERS_MAX_TOKENS = 24000
PRIMARY_THREAD_MAX_TOKENS = 24000
SECONDARY_ARCS_MAX_TOKENS = 24000
OUTLINE_MAX_TOKENS = 32000

# Computes the primary thread's target word count from the user's requested
# base word count plus a bonus for every secondary thread attached to the
# story. This is additive, not a shared budget — secondary threads add to the
# primary thread's target on top of the user's number, since each thread
# generates its own separate content downstream (see init_secondary_arcs).
#
# Formula: base + (base * flat_bonus_pct) + sum(per-thread bonus), where each
# thread's bonus is base * per_thread_base_pct * (length/100) * (priority/100)
# * (1 + heat_weight * heat/100) — length and priority are the primary
# drivers (multiplicative, so a thread needs to be both long and
# high-priority to matter much), heat is a smaller modifier on top of that,
# reflecting that a hotter thread needs more room for those scenes but isn't
# what makes a thread long on its own.
def calculate_word_count(
    initial_word_count: int,
    secondary_threads: list[dict] | None = None,
    weights: dict | None = None,
) -> int:
    weights = {**DEFAULT_WORD_COUNT_WEIGHTS, **(weights or {})}
    base = max(1, min(initial_word_count, MAX_INITIAL_WORD_COUNT))

    total = base + base * weights["flat_bonus_pct"]
    for thread in secondary_threads or []:
        length = thread.get("length", 0) / 100
        priority = thread.get("priority", 0) / 100
        heat = thread.get("heat", 0) / 100
        thread_bonus = base * weights["per_thread_base_pct"] * length * priority * (
            1 + weights["heat_weight"] * heat
        )
        total += thread_bonus

    return round(total)


# Keeps only the leading length_pct% of a secondary arc's plot points,
# discarding the rest. init_secondary_arcs always generates a thread's
# complete arc (see outline_prompts.INIT_SECONDARY_ARCS_USER_PROMPT) —
# this function is what actually enforces `length`, mechanically, so the
# model's own judgment about "how much is enough" is never load-bearing.
# The cut lands on a plot-point boundary rather than a word/character count,
# so it can never land mid-sentence. Rounds up (ceiling), minimum 1 kept
# point for any length_pct > 0 — e.g. 11 points at length=30 (11*0.3=3.3)
# keeps 4, not 3; 5 points at length=50 (5*0.5=2.5) keeps 3, not 2 (avoiding
# Python's round() banker's-rounding surprise on exact .5 values).
def truncate_secondary_arc(plot_points: list[dict], length_pct: int) -> list[dict]:
    if not plot_points:
        return []
    keep_count = max(1, math.ceil(len(plot_points) * length_pct / 100))
    return plot_points[:keep_count]


# Pulls the first {...} JSON object out of a model response.
def _extract_json(text: str, label: str) -> dict:
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        raise RuntimeError(f"No JSON found in {label} response: {text[:200]}")
    try:
        return json.loads(match.group())
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Malformed JSON in {label} response: {e}") from e


# Builds the combined intro prompt from the title plus the five user-facing
# sections (ported from V2's single-prompt --- Premise/Tone/Characters/Story
# Structure/Sexual --- sections), plus any secondary threads. Empty sections
# are omitted rather than included blank.
#
# include_characters_notes is True only for init_novel and init_characters —
# once init_characters has generated the real cast, every later step should
# see that generated cast instead of the user's raw Characters notes, so
# those steps rebuild the prompt with include_characters_notes=False rather
# than sending the model both a rough draft and a finished character sheet.
def _build_intro_prompt(
    title: str,
    premise: str,
    tone_notes: str | None,
    characters_notes: str | None,
    primary_thread: str | None,
    romance_content: str | None,
    secondary_threads: list[dict] | None,
    include_characters_notes: bool = True,
    include_secondary_threads: bool = True,
) -> str:
    sections = [f"Title: {title}", f"--- Premise ---\n{premise}"]
    if tone_notes:
        sections.append(f"--- Tone ---\n{tone_notes}")
    if include_characters_notes and characters_notes:
        sections.append(f"--- Characters ---\n{characters_notes}")
    if primary_thread:
        sections.append(f"--- Story Structure ---\n{primary_thread}")
    if romance_content:
        sections.append(f"--- Sexual/Romance ---\n{romance_content}")
    # `length` is deliberately not rendered — it is enforced mechanically in
    # Python (truncate_secondary_arc) and init_secondary_arcs is explicitly
    # told to ignore it, so showing the model "N% of this storyline resolved"
    # only invites it to reason about how much story is left.
    if include_secondary_threads and secondary_threads:
        thread_lines = "\n\n".join(
            f"Thread {i}: {t['description']}\n"
            f"(priority: {t['priority']}/100, heat: {t['heat']}/100)"
            for i, t in enumerate(secondary_threads, start=1)
        )
        sections.append(f"--- Secondary Threads ---\n{thread_lines}")
    return "\n\n".join(sections)


# Rebuilds the intro prompt from a novel row (as stored in the DB) with the
# Characters notes section dropped — used once init_characters has generated
# the real cast, so downstream steps see the finished character sheet
# instead of the user's raw notes.
#
# include_secondary_threads defaults to False because init_secondary_arcs is
# the LAST step allowed to see the raw thread descriptions. A description is
# frequently a complete storyline including its ending; every step after the
# arcs step must see only the already-truncated plot points, or it will write
# toward an ending it was never supposed to know about. That leak — the raw
# description sitting in the system prompt under "this is the north star for
# the story, do not stray from this" — is why low-`length` threads kept
# arriving fully resolved. Only the init_secondary_arcs call passes True.
def _post_characters_prompt(
    novel: dict,
    secondary_threads: list[dict] | None,
    include_secondary_threads: bool = False,
) -> str:
    return _build_intro_prompt(
        novel.get("title", ""),
        novel.get("premise", ""),
        novel.get("tone_notes"),
        novel.get("characters_notes"),
        novel.get("primary_thread"),
        novel.get("romance_content"),
        secondary_threads,
        include_characters_notes=False,
        include_secondary_threads=include_secondary_threads,
    )


# Calls the LLM to generate the novel metadata from the title and the five
# intro-prompt sections. Any of primary_genre/author/themes passed in are
# treated as fixed user choices rather than left for the model to infer.
# word_count is the primary thread's target, computed server-side by
# calculate_word_count (see router.create_novel) from the user's requested
# word count plus the secondary threads' bonuses.
def init_novel(
    title: str,
    premise: str,
    word_count: int,
    tone_notes: str | None = None,
    characters_notes: str | None = None,
    primary_thread: str | None = None,
    romance_content: str | None = None,
    secondary_threads: list[dict] | None = None,
    primary_genre: str | None = None,
    author: str | None = None,
    themes: list[str] | None = None,
    model: str = DEFAULTS["metadata"],
    reasoning: bool = False,
) -> dict:
    intro_prompt = _build_intro_prompt(
        title, premise, tone_notes, characters_notes, primary_thread, romance_content, secondary_threads
    )
    system_prompt = outline_prompts.SYSTEM_PROMPT.format(intro_prompt=intro_prompt)
    user_prompt = outline_prompts.INIT_NOVEL_USER_PROMPT.format(
        word_count=word_count,
        schema=json.dumps(outline_prompts.INIT_NOVEL_SCHEMA, indent=2),
    )

    overrides = {
        "primary_genre": primary_genre,
        "author": author,
        "themes": themes or None,
    }
    overrides = {k: v for k, v in overrides.items() if v}
    if overrides:
        user_prompt += outline_prompts.INIT_NOVEL_USER_OVERRIDES_TEMPLATE.format(
            overrides=json.dumps(overrides, indent=2)
        )

    text = call_model(model, system_prompt, user_prompt, reasoning=reasoning)
    data = _extract_json(text, model)

    novel = data.get("novel", {})
    novel["prompt"] = intro_prompt
    return novel


# Calls the LLM to generate the character list from the novel's metadata.
# Runs right after init_novel, before worldbuilding exists yet — the cast is
# meant to shape the world, not the other way around.
def init_characters(
    novel: dict,
    model: str = DEFAULTS["characters"],
    reasoning: bool = False,
) -> dict:
    system_prompt = outline_prompts.SYSTEM_PROMPT.format(intro_prompt=novel.get("prompt", ""))
    user_prompt = outline_prompts.INIT_CHARACTERS_USER_PROMPT.format(
        novel_metadata=json.dumps(novel, indent=2),
        schema=json.dumps(outline_prompts.INIT_CHARACTERS_SCHEMA, indent=2),
    )

    text = call_model(
        model, system_prompt, user_prompt, reasoning=reasoning, max_tokens=CHARACTERS_MAX_TOKENS
    )
    data = _extract_json(text, model)
    return data.get("characters", [])


# Calls the LLM to generate the rules of the world — story type, time period,
# anchor location, and constraints (genre conventions, magic systems,
# technology) — from the novel's metadata and the already-generated cast, so
# the world is built consistent with who's in it.
def init_worldbuilding(
    novel: dict,
    characters: list[dict],
    model: str = DEFAULTS["worldbuilding"],
    reasoning: bool = False,
) -> dict:
    system_prompt = outline_prompts.SYSTEM_PROMPT.format(intro_prompt=novel.get("prompt", ""))
    user_prompt = outline_prompts.INIT_WORLDBUILDING_USER_PROMPT.format(
        novel_metadata=json.dumps(novel, indent=2),
        characters=json.dumps(characters, indent=2),
        schema=json.dumps(outline_prompts.INIT_WORLDBUILDING_SCHEMA, indent=2),
    )

    text = call_model(model, system_prompt, user_prompt, reasoning=reasoning)
    data = _extract_json(text, model)
    return data.get("worldbuilding", {})


# Calls the LLM to generate the protagonist's full hero's-journey primary
# thread — deep detail, character moments and feelings included, not just
# plot events. Identifies the protagonist/antagonist from the generated cast
# rather than needing separate stubs (see
# outline_prompts.INIT_PRIMARY_THREAD_USER_PROMPT). The target word count is
# fixed by the caller (novel["word_count"], computed server-side by
# calculate_word_count) rather than self-decided by the model — the plot
# point count and pacing must be proportional to that fixed target. This is
# an internal generation input now — the outline (see init_outline below) is
# what the user actually reads and edits.
def init_primary_thread(
    novel: dict,
    worldbuilding: dict,
    characters: list[dict],
    model: str = DEFAULTS["primary_thread"],
    reasoning: bool = False,
) -> list[dict]:
    system_prompt = outline_prompts.SYSTEM_PROMPT.format(intro_prompt=novel.get("prompt", ""))
    user_prompt = outline_prompts.INIT_PRIMARY_THREAD_USER_PROMPT.format(
        novel_metadata=json.dumps(novel, indent=2),
        worldbuilding=json.dumps(worldbuilding, indent=2),
        characters=json.dumps(characters, indent=2),
        word_count=novel.get("word_count"),
        schema=json.dumps(outline_prompts.INIT_PRIMARY_THREAD_SCHEMA, indent=2),
    )

    text = call_model(
        model, system_prompt, user_prompt, reasoning=reasoning, max_tokens=PRIMARY_THREAD_MAX_TOKENS
    )
    data = _extract_json(text, model)
    return data.get("primary_thread", [])


# Calls the LLM to generate a short, lighter-detail arc for each secondary
# thread, independently of the others. A separate call from init_primary_thread
# so the primary thread doesn't compete for space with N secondary
# storylines in the same response. Each thread's `length` caps how much of
# its own natural arc is actually resolved in this story — see
# outline_prompts.INIT_SECONDARY_ARCS_USER_PROMPT for the cutoff rule. This
# is an internal generation input — see init_outline below.
def init_secondary_arcs(
    novel: dict,
    worldbuilding: dict,
    characters: list[dict],
    primary_thread: list[dict],
    secondary_threads: list[dict],
    model: str = DEFAULTS["secondary_arcs"],
    reasoning: bool = False,
    correction: str | None = None,
) -> list[dict]:
    system_prompt = outline_prompts.SYSTEM_PROMPT.format(intro_prompt=novel.get("prompt", ""))
    user_prompt = outline_prompts.INIT_SECONDARY_ARCS_USER_PROMPT.format(
        novel_metadata=json.dumps(novel, indent=2),
        worldbuilding=json.dumps(worldbuilding, indent=2),
        characters=json.dumps(characters, indent=2),
        primary_thread=json.dumps(primary_thread, indent=2),
        secondary_threads=json.dumps(secondary_threads, indent=2),
        schema=json.dumps(outline_prompts.INIT_SECONDARY_ARCS_SCHEMA, indent=2),
    )
    # Retry path — names the threads that came back malformed last attempt.
    if correction:
        user_prompt += outline_prompts.INIT_SECONDARY_ARCS_CORRECTION_TEMPLATE.format(
            problems=correction
        )

    text = call_model(
        model, system_prompt, user_prompt, reasoning=reasoning, max_tokens=SECONDARY_ARCS_MAX_TOKENS
    )
    data = _extract_json(text, model)
    return data.get("secondary_arcs", [])


# Calls the LLM to write the final, detailed, user-facing outline — weaving
# the primary thread's beats and the secondary arcs' plot points into one
# continuous, ordered sequence of prose beats. This is the first step whose
# output is actually persisted as something the user reads and edits;
# init_primary_thread and init_secondary_arcs are internal inputs to it.
# Runs after both — its job is to combine and narrate, not invent new plot.
def init_outline(
    novel: dict,
    primary_thread: list[dict],
    secondary_arcs: list[dict],
    model: str = DEFAULTS["outline"],
    reasoning: bool = False,
) -> list[dict]:
    system_prompt = outline_prompts.SYSTEM_PROMPT.format(intro_prompt=novel.get("prompt", ""))
    user_prompt = outline_prompts.INIT_OUTLINE_USER_PROMPT.format(
        primary_thread=json.dumps(primary_thread, indent=2),
        secondary_arcs=json.dumps(secondary_arcs, indent=2),
        word_count=novel.get("word_count"),
        schema=json.dumps(outline_prompts.INIT_OUTLINE_SCHEMA, indent=2),
    )

    # The outline is the largest single response in the pipeline — roughly one
    # 200-400 word beat per primary beat and per secondary plot point, so a
    # multi-thread story can genuinely exceed a model's output ceiling. If it
    # truncates, retry once asking for the same beats at the shorter end of
    # the range rather than failing the whole run; a tighter outline is worth
    # more than no outline.
    try:
        text = call_model(
            model, system_prompt, user_prompt, reasoning=reasoning, max_tokens=OUTLINE_MAX_TOKENS
        )
    except RuntimeError as e:
        if "truncated" not in str(e):
            raise
        text = call_model(
            model,
            system_prompt,
            user_prompt + outline_prompts.INIT_OUTLINE_LENGTH_CORRECTION,
            reasoning=reasoning,
            max_tokens=OUTLINE_MAX_TOKENS,
        )
    data = _extract_json(text, model)
    return data.get("outline", [])


# Calls the LLM to generate locations, items, organizations, and events in a
# single call from the novel's metadata, worldbuilding rules, characters, and
# primary thread — events are expected to map onto real primary thread plot
# points rather than being invented independently.
def init_entities(
    novel: dict,
    worldbuilding: dict,
    characters: list[dict],
    primary_thread: list[dict],
    model: str = DEFAULTS["entities"],
    reasoning: bool = False,
) -> dict:
    system_prompt = outline_prompts.SYSTEM_PROMPT.format(intro_prompt=novel.get("prompt", ""))
    user_prompt = outline_prompts.INIT_ENTITIES_USER_PROMPT.format(
        novel_metadata=json.dumps(novel, indent=2),
        worldbuilding=json.dumps(worldbuilding, indent=2),
        characters=json.dumps(characters, indent=2),
        primary_thread=json.dumps(primary_thread, indent=2),
        schema=json.dumps(outline_prompts.INIT_ENTITIES_SCHEMA, indent=2),
    )

    text = call_model(model, system_prompt, user_prompt, reasoning=reasoning)
    return _extract_json(text, model)


# Calls the LLM to generate the starting relationship graph — character to
# character, and character to item/location — from everything generated so
# far. Runs last, since it needs entities (locations/items/organizations)
# to exist first. Only relationships that actually exist at story-start are
# emitted; see outline_prompts.INIT_RELATIONSHIPS_USER_PROMPT for the
# asymmetry rules.
def init_relationships(
    novel: dict,
    characters: list[dict],
    worldbuilding: dict,
    model: str = DEFAULTS["initial_state"],
    reasoning: bool = False,
) -> dict:
    system_prompt = outline_prompts.SYSTEM_PROMPT.format(intro_prompt=novel.get("prompt", ""))
    user_prompt = outline_prompts.INIT_RELATIONSHIPS_USER_PROMPT.format(
        novel_metadata=json.dumps(novel, indent=2),
        characters=json.dumps(characters, indent=2),
        locations=json.dumps(worldbuilding.get("locations", []), indent=2),
        items=json.dumps(worldbuilding.get("items", []), indent=2),
        organizations=json.dumps(worldbuilding.get("organizations", []), indent=2),
        events=json.dumps(worldbuilding.get("events", []), indent=2),
        schema=json.dumps(outline_prompts.INIT_RELATIONSHIPS_SCHEMA, indent=2),
    )

    text = call_model(model, system_prompt, user_prompt, reasoning=reasoning)
    return _extract_json(text, model)

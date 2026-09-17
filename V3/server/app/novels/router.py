import json
import uuid

from fastapi import APIRouter, HTTPException

from app.db import get_connection
from app.model_routing import DEFAULTS, list_models
from app.novels.generation import (
    _post_characters_prompt,
    calculate_word_count,
    init_characters,
    init_entities,
    init_novel,
    init_outline,
    # init_relationships,  # disabled for now — full state system to be built later
    init_primary_thread,
    init_secondary_arcs,
    init_worldbuilding,
    truncate_secondary_arc,
)
from app.novels.models import (
    Character,
    CharacterRelationship,
    CharacterUpdate,
    EntityRelationship,
    Event,
    EventUpdate,
    Item,
    ItemUpdate,
    Location,
    LocationUpdate,
    Novel,
    NovelCreate,
    NovelCreateResponse,
    NovelSummary,
    NovelUpdate,
    Organization,
    OrganizationUpdate,
    OutlineBeat,
    OutlineBeatUpdate,
    SecondaryThread,
    SecondaryThreadCreate,
    SecondaryThreadUpdate,
)

router = APIRouter(prefix="/api/v1", tags=["novels"])

# Novel columns that hold JSON (lists), serialized to/from TEXT in sqlite.
_JSON_COLUMNS = {"sub_genres", "themes", "constraints"}

_NOVEL_COLUMNS = [
    "id",
    "prompt",
    "title",
    "summary",
    "author",
    "word_count",
    "premise",
    "primary_genre",
    "sub_genres",
    "tone",
    "themes",
    "spice_level",
    "literary_voice",
    "tense",
    "perspective",
    "forbidden_element",
    "story_type",
    "time_period",
    "anchor_location",
    "anchor_location_description",
    "constraints",
    "tone_notes",
    "characters_notes",
    "primary_thread",
    "romance_content",
    "primary_word_count",
    "metadata_model",
    "characters_model",
    "worldbuilding_model",
    "primary_thread_model",
    "secondary_arcs_model",
    "outline_model",
    "entities_model",
    "initial_state_model",
    "metadata_reasoning",
    "characters_reasoning",
    "worldbuilding_reasoning",
    "primary_thread_reasoning",
    "secondary_arcs_reasoning",
    "outline_reasoning",
    "entities_reasoning",
    "initial_state_reasoning",
]

# Novel columns stored as sqlite INTEGER (0/1) but exposed as bool.
_BOOL_COLUMNS = {
    "metadata_reasoning",
    "characters_reasoning",
    "worldbuilding_reasoning",
    "primary_thread_reasoning",
    "secondary_arcs_reasoning",
    "outline_reasoning",
    "entities_reasoning",
    "initial_state_reasoning",
}


def _row_to_novel(row) -> Novel:
    data = dict(row)
    for col in _JSON_COLUMNS:
        data[col] = json.loads(data[col]) if data[col] else []
    for col in _BOOL_COLUMNS:
        data[col] = bool(data[col])
    return Novel(**data)


# Character columns that hold JSON (lists), serialized to/from TEXT in sqlite.
_CHARACTER_JSON_COLUMNS = {
    "physical_characteristics",
    "personality",
    "fears",
    "flaws",
    "contradictions",
    "hobbies",
    "spiritual_beliefs",
    "character_voice",
    "speech_patterns",
}

_CHARACTER_COLUMNS = [
    "id",
    "novel_id",
    "name",
    "role",
    "age",
    "gender",
    "sexuality",
    "occupation",
    "appearance",
    "physical_characteristics",
    "personality",
    "backstory",
    "fears",
    "flaws",
    "contradictions",
    "hobbies",
    "spiritual_beliefs",
    "character_voice",
    "speech_patterns",
]


def _character_row_to_dict(row) -> dict:
    data = dict(row)
    for col in _CHARACTER_JSON_COLUMNS:
        data[col] = json.loads(data[col]) if data[col] else []
    return data


def _row_to_character(row) -> Character:
    return Character(**_character_row_to_dict(row))


# List selectable model aliases plus the default alias per pipeline step, for
# populating the Metadata/Characters/Worldbuilding dropdowns client-side.
@router.get("/models")
def get_models() -> dict:
    return {"models": list_models(), "defaults": DEFAULTS}


# Get all novels, summary info only.
@router.get("/novels")
def get_novels() -> list[NovelSummary]:
    conn = get_connection()
    try:
        rows = conn.execute("SELECT id, title, premise FROM novels").fetchall()
        return [NovelSummary(**row) for row in rows]
    finally:
        conn.close()


# Get full info for one novel.
@router.get("/novel/{id}")
def get_novel(id: str) -> Novel:
    conn = get_connection()
    try:
        row = conn.execute(
            f"SELECT {', '.join(_NOVEL_COLUMNS)} FROM novels WHERE id = ?", (id,)
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Novel not found")
        return _row_to_novel(row)
    finally:
        conn.close()


# The 12 stages every secondary arc must contain, in order. Mirrors the
# primary thread's 9 hero's-journey steps — a named, mandatory structure the
# model cannot quietly return less of. See INIT_SECONDARY_ARCS_USER_PROMPT.
SECONDARY_ARC_STAGES = [
    "seed",
    "first_friction",
    "commitment",
    "complication_one",
    "complication_two",
    "midpoint_shift",
    "deepening",
    "setback",
    "forced_choice",
    "crisis",
    "confrontation",
    "landing",
]


# Checks every returned arc carries the full stage skeleton. Returns a list of
# human-readable problems (empty if all arcs are well-formed) used both to
# decide whether to retry and as the corrective text sent on that retry.
def _validate_secondary_arcs(secondary_arcs: list[dict]) -> list[str]:
    problems = []
    for i, arc in enumerate(secondary_arcs):
        points = arc.get("plot_points", [])
        stages = [p.get("arc_stage") for p in points]
        missing = [s for s in SECONDARY_ARC_STAGES if s not in stages]
        if missing:
            problems.append(
                f"Thread {i + 1} returned {len(points)} plot points and is missing these "
                f"required stages: {', '.join(missing)}."
            )
    return problems


# Deletes a half-built novel, then raises. Used by the secondary-arc checks
# below: a novel whose threads over-resolve is unusable, so it should not be
# left sitting in the user's list. Child rows go via ON DELETE CASCADE.
def _abort_partial_novel(conn, novel_id: str, detail: str) -> None:
    conn.execute("DELETE FROM novels WHERE id = ?", (novel_id,))
    conn.commit()
    raise HTTPException(status_code=502, detail=detail)


# Create a new novel. Runs the generation pipeline in sequence — metadata,
# characters, worldbuilding (world rules), primary thread (protagonist's
# full hero's-journey arc), secondary arcs (one per secondary_thread,
# lighter detail), outline (weaves the primary thread and secondary arcs
# into the final detailed, user-facing outline), entities
# (locations/items/organizations/events in one call), then relationships —
# each step using whichever model alias was chosen for it (falling back to
# the step default). Every step commits to the database immediately after
# generating; the next step reads its inputs back from the database rather
# than being passed the previous step's in-memory result, so by the time
# relationships is generated, every name it references already has a real
# row (and id) to resolve against. The primary thread and secondary arcs are
# internal generation inputs only — the outline is the only spine-like
# artifact exposed via the API/UI.
@router.post("/novel")
def create_novel(body: NovelCreate) -> NovelCreateResponse:
    new_id = str(uuid.uuid4())
    conn = get_connection()
    try:
        # --- Metadata ---
        # The primary thread's word count target is computed here, once, from
        # the user's requested base plus a bonus for every secondary thread —
        # see calculate_word_count. Every downstream step that needs a word
        # count target (init_primary_thread) reads it back from the novels
        # row rather than deciding its own.
        secondary_thread_dicts = [t.model_dump() for t in body.secondary_threads]
        word_count = calculate_word_count(body.word_count, secondary_thread_dicts)
        generated = init_novel(
            body.title,
            body.premise,
            word_count,
            tone_notes=body.tone_notes,
            characters_notes=body.characters_notes,
            primary_thread=body.primary_thread,
            romance_content=body.romance_content,
            secondary_threads=secondary_thread_dicts,
            primary_genre=body.primary_genre,
            author=body.author,
            themes=body.themes,
            model=body.metadata_model or DEFAULTS["metadata"],
            reasoning=body.metadata_reasoning,
        )
        conn.execute(
            f"""INSERT INTO novels ({', '.join(_NOVEL_COLUMNS)})
                VALUES ({', '.join(['?'] * len(_NOVEL_COLUMNS))})""",
            (
                new_id,
                generated.get("prompt", ""),
                generated.get("title", body.title),
                generated.get("summary"),
                generated.get("author"),
                word_count,
                generated.get("premise", body.premise),
                generated.get("primary_genre"),
                json.dumps(generated.get("sub_genres", [])),
                generated.get("tone"),
                json.dumps(generated.get("themes", [])),
                generated.get("spice_level"),
                generated.get("literary_voice"),
                generated.get("tense"),
                generated.get("perspective"),
                generated.get("forbidden_element"),
                None,
                None,
                None,
                None,
                json.dumps([]),
                body.tone_notes,
                body.characters_notes,
                body.primary_thread,
                body.romance_content,
                None,
                body.metadata_model or DEFAULTS["metadata"],
                body.characters_model or DEFAULTS["characters"],
                body.worldbuilding_model or DEFAULTS["worldbuilding"],
                body.primary_thread_model or DEFAULTS["primary_thread"],
                body.secondary_arcs_model or DEFAULTS["secondary_arcs"],
                body.outline_model or DEFAULTS["outline"],
                body.entities_model or DEFAULTS["entities"],
                body.initial_state_model or DEFAULTS["initial_state"],
                body.metadata_reasoning,
                body.characters_reasoning,
                body.worldbuilding_reasoning,
                body.primary_thread_reasoning,
                body.secondary_arcs_reasoning,
                body.outline_reasoning,
                body.entities_reasoning,
                body.initial_state_reasoning,
            ),
        )
        secondary_thread_rows = []
        for thread in body.secondary_threads:
            thread_id = str(uuid.uuid4())
            conn.execute(
                """INSERT INTO secondary_threads (id, novel_id, description, length, priority, heat)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (thread_id, new_id, thread.description, thread.length, thread.priority, thread.heat),
            )
            secondary_thread_rows.append(
                {
                    "id": thread_id,
                    "description": thread.description,
                    "length": thread.length,
                    "priority": thread.priority,
                    "heat": thread.heat,
                }
            )
        conn.commit()
        novel_row = dict(
            conn.execute(
                f"SELECT {', '.join(_NOVEL_COLUMNS)} FROM novels WHERE id = ?", (new_id,)
            ).fetchone()
        )

        # --- Characters ---
        characters = init_characters(
            novel_row,
            model=body.characters_model or DEFAULTS["characters"],
            reasoning=body.characters_reasoning,
        )
        for character in characters:
            conn.execute(
                f"""INSERT INTO characters ({', '.join(_CHARACTER_COLUMNS)})
                    VALUES ({', '.join(['?'] * len(_CHARACTER_COLUMNS))})""",
                (
                    str(uuid.uuid4()),
                    new_id,
                    character.get("name", ""),
                    character.get("role"),
                    character.get("age"),
                    character.get("gender"),
                    character.get("sexuality"),
                    character.get("occupation"),
                    character.get("appearance"),
                    json.dumps(character.get("physical_characteristics", [])),
                    json.dumps(character.get("personality", [])),
                    character.get("backstory"),
                    json.dumps(character.get("fears", [])),
                    json.dumps(character.get("flaws", [])),
                    json.dumps(character.get("contradictions", [])),
                    json.dumps(character.get("hobbies", [])),
                    json.dumps(character.get("spiritual_beliefs", [])),
                    json.dumps(character.get("character_voice", [])),
                    json.dumps(character.get("speech_patterns", [])),
                ),
            )
        conn.commit()
        character_rows = [
            _character_row_to_dict(row)
            for row in conn.execute(
                f"SELECT {', '.join(_CHARACTER_COLUMNS)} FROM characters WHERE novel_id = ?",
                (new_id,),
            ).fetchall()
        ]

        # From this point on, every step should see the generated cast
        # instead of the user's raw Characters notes — rebuild the prompt
        # used for system context accordingly and carry it on novel_row.
        # This also drops the raw secondary thread descriptions (see
        # _post_characters_prompt); only init_secondary_arcs re-adds them.
        novel_row["prompt"] = _post_characters_prompt(novel_row, secondary_thread_rows)

        # --- Worldbuilding: world rules ---
        worldbuilding_data = init_worldbuilding(
            novel_row,
            character_rows,
            model=body.worldbuilding_model or DEFAULTS["worldbuilding"],
            reasoning=body.worldbuilding_reasoning,
        )
        conn.execute(
            """UPDATE novels SET story_type = ?, time_period = ?, anchor_location = ?,
               anchor_location_description = ?, constraints = ? WHERE id = ?""",
            (
                worldbuilding_data.get("story_type"),
                worldbuilding_data.get("time_period"),
                worldbuilding_data.get("anchor_location"),
                worldbuilding_data.get("anchor_location_description"),
                json.dumps(worldbuilding_data.get("constraints", [])),
                new_id,
            ),
        )
        conn.commit()
        novel_row = dict(
            conn.execute(
                f"SELECT {', '.join(_NOVEL_COLUMNS)} FROM novels WHERE id = ?", (new_id,)
            ).fetchone()
        )
        novel_row["prompt"] = _post_characters_prompt(novel_row, secondary_thread_rows)

        # --- Primary thread: protagonist's full hero's-journey arc ---
        # Internal generation input only — not exposed via the API. The
        # outline step below is what the user actually sees and edits.
        primary_thread = init_primary_thread(
            novel_row,
            worldbuilding_data,
            character_rows,
            model=body.primary_thread_model or DEFAULTS["primary_thread"],
            reasoning=body.primary_thread_reasoning,
        )
        conn.execute(
            "UPDATE novels SET primary_word_count = ? WHERE id = ?",
            (novel_row.get("word_count"), new_id),
        )
        conn.commit()
        novel_row = dict(
            conn.execute(
                f"SELECT {', '.join(_NOVEL_COLUMNS)} FROM novels WHERE id = ?", (new_id,)
            ).fetchone()
        )
        novel_row["prompt"] = _post_characters_prompt(novel_row, secondary_thread_rows)
        for i, beat in enumerate(primary_thread):
            conn.execute(
                """INSERT INTO spine_beats
                   (id, novel_id, sort_order, heros_journey_step, summary, word_count_pct,
                    time_gap_before, forbidden_element_active, intimate_arc_role)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    str(uuid.uuid4()),
                    new_id,
                    i,
                    beat.get("heros_journey_step", ""),
                    beat.get("summary", ""),
                    beat.get("word_count_pct"),
                    beat.get("time_gap_before"),
                    1 if beat.get("forbidden_element_active") else 0,
                    beat.get("intimate_arc_role"),
                ),
            )
        conn.commit()
        primary_thread_rows = [
            dict(row)
            for row in conn.execute(
                """SELECT id, novel_id, sort_order, heros_journey_step, summary, word_count_pct,
                          time_gap_before, forbidden_element_active, intimate_arc_role
                   FROM spine_beats WHERE novel_id = ? ORDER BY sort_order""",
                (new_id,),
            ).fetchall()
        ]

        # --- Secondary arcs: one lighter-detail arc per secondary_thread ---
        # Internal generation input only — not exposed via the API.
        secondary_arcs = []
        first_attempt_error = None
        if secondary_thread_rows:
            # The LAST step allowed to see the raw thread descriptions — it
            # needs them to write each arc. Every step after this one gets
            # the redacted prompt carried on novel_row, so build the
            # un-redacted version here rather than mutating novel_row.
            arcs_novel_row = {
                **novel_row,
                "prompt": _post_characters_prompt(
                    novel_row, secondary_thread_rows, include_secondary_threads=True
                ),
            }
            # A truncated response (finish_reason='length') raises out of
            # call_model. That is the same underlying failure as a response
            # missing stages — the model ran out of room — so treat it as a
            # retryable problem rather than letting it kill the run, and let
            # the shared retry below handle both.
            try:
                secondary_arcs = init_secondary_arcs(
                    arcs_novel_row,
                    worldbuilding_data,
                    character_rows,
                    primary_thread_rows,
                    secondary_thread_rows,
                    model=body.secondary_arcs_model or DEFAULTS["secondary_arcs"],
                    reasoning=body.secondary_arcs_reasoning,
                )
            except RuntimeError as e:
                secondary_arcs = []
                first_attempt_error = str(e)
        # Matched to secondary_thread_rows by array POSITION, not by any
        # string the model echoes back — init_secondary_arcs's prompt
        # requires the response to list arcs in the same order as the
        # threads it was given (see INIT_SECONDARY_ARCS_USER_PROMPT), so
        # zipping the two lists is the correct, unambiguous pairing. This
        # used to match on the model's echoed `thread_description` text,
        # which silently broke whenever the model didn't reproduce the
        # description byte-for-byte: the lookup would either skip the arc
        # entirely or, worse, resolve to length_by_thread_id's fallback of
        # 100 (meaning "don't truncate at all") — a real, confirmed cause of
        # secondary threads leaking their full resolution regardless of the
        # `length` the user actually set.
        # Skipped when the first attempt was truncated — there is nothing to
        # count yet, and the retry below is what recovers it.
        if not first_attempt_error and len(secondary_arcs) != len(secondary_thread_rows):
            _abort_partial_novel(
                conn,
                new_id,
                f"secondary_arcs step returned {len(secondary_arcs)} arcs, expected "
                f"{len(secondary_thread_rows)} (one per secondary thread) — cannot safely "
                "match arcs to threads by position.",
            )

        # Each arc must carry the full 12-stage skeleton. A short arc makes
        # the `length` cut meaningless — at 4 plot points, length=30 keeps 2,
        # which is half the storyline, and the thread reads as resolved. A
        # missing `landing` means the response was cut off mid-generation
        # (finish_reason='length'), which produces the same shape. Retry once
        # naming the offending threads, then give up rather than building a
        # novel whose secondary threads silently over-resolve.
        problems = _validate_secondary_arcs(secondary_arcs)
        if first_attempt_error:
            problems = [
                "Your previous response was cut off before it finished — it exceeded the "
                "output limit. Keep every plot point summary to 2-4 tight sentences so all "
                "12 stages for every thread fit in the response."
            ]
        if problems:
            try:
                secondary_arcs = init_secondary_arcs(
                    arcs_novel_row,
                    worldbuilding_data,
                    character_rows,
                    primary_thread_rows,
                    secondary_thread_rows,
                    model=body.secondary_arcs_model or DEFAULTS["secondary_arcs"],
                    reasoning=body.secondary_arcs_reasoning,
                    correction="\n".join(problems),
                )
            except RuntimeError as e:
                _abort_partial_novel(
                    conn,
                    new_id,
                    f"secondary_arcs step failed on retry: {e}. Try a model with a larger "
                    "output budget for this step, or fewer secondary threads.",
                )
            if len(secondary_arcs) != len(secondary_thread_rows):
                _abort_partial_novel(
                    conn,
                    new_id,
                    f"secondary_arcs retry returned {len(secondary_arcs)} arcs, expected "
                    f"{len(secondary_thread_rows)} — cannot safely match arcs to threads.",
                )
            problems = _validate_secondary_arcs(secondary_arcs)
            if problems:
                _abort_partial_novel(
                    conn,
                    new_id,
                    "secondary_arcs step returned incomplete arcs after a retry: "
                    + "; ".join(problems),
                )
        for thread, arc in zip(secondary_thread_rows, secondary_arcs):
            thread_id = thread["id"]
            conn.execute(
                "UPDATE secondary_threads SET word_count = ? WHERE id = ?",
                (arc.get("word_count"), thread_id),
            )
            # init_secondary_arcs always returns the thread's COMPLETE arc —
            # this is what actually enforces `length`, mechanically, rather
            # than trusting the model to self-truncate (see
            # generation.truncate_secondary_arc and the comment on
            # outline_prompts.INIT_SECONDARY_ARCS_USER_PROMPT for why).
            # Everything past the cutoff is discarded here and never reaches
            # the database or the outline step below.
            kept_points = truncate_secondary_arc(arc.get("plot_points", []), thread["length"])
            for i, point in enumerate(kept_points):
                conn.execute(
                    """INSERT INTO secondary_arc_plot_points
                       (id, novel_id, secondary_thread_id, sort_order, summary, characters_involved)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                        str(uuid.uuid4()),
                        new_id,
                        thread_id,
                        i,
                        point.get("summary", ""),
                        json.dumps(point.get("characters_involved", [])),
                    ),
                )
        conn.commit()
        secondary_arc_plot_point_rows = [
            dict(row)
            for row in conn.execute(
                """SELECT id, novel_id, secondary_thread_id, sort_order, summary, characters_involved
                   FROM secondary_arc_plot_points WHERE novel_id = ? ORDER BY secondary_thread_id, sort_order""",
                (new_id,),
            ).fetchall()
        ]

        # --- Outline: the final, user-facing document ---
        # Weaves the primary thread and secondary arcs into one detailed,
        # ordered outline. This is the only spine-like artifact persisted
        # for the user to read and edit.
        #
        # Deliberately does NOT include the user's raw thread `description`
        # here — the outline step must only ever see the AI-generated (and
        # already length-truncated) plot_points for each thread, never the
        # user's short, complete-sounding premise text sitting alongside
        # them, since a model can lean on that framing even when the
        # instructions don't ask it to. Each secondary_arc entry is
        # identified purely by its position in the list (thread_index) —
        # the outline prompt is told to match beats back to threads by that
        # index instead of any text field.
        #
        # Withholding it here is necessary but NOT sufficient: the same
        # descriptions also used to reach this step through the system
        # prompt, which is built from novel_row["prompt"] and rendered the
        # full description of every thread under "this is the north star for
        # the story, do not stray from this". That is now stripped at the
        # source — see _post_characters_prompt in generation.py.
        # Built by iterating secondary_thread_rows — the user's own thread
        # order — rather than the plot-point query, which is ordered by
        # secondary_thread_id (a random UUID string). That previously made
        # thread_index arbitrary and, worse, silently dropped any thread with
        # no plot point rows from the outline input entirely.
        #
        # `length` is deliberately NOT passed on. The cut has already happened
        # by this point, so the number carries no instruction the outline step
        # can act on — it only invites the model to reason about how much
        # storyline is missing and write toward it. It gets the one fact it
        # needs instead: whether the thread continues past this story.
        plot_points_by_thread_id: dict[str, list[dict]] = {}
        for row in secondary_arc_plot_point_rows:
            plot_points_by_thread_id.setdefault(row["secondary_thread_id"], []).append(row)
        outline_input_arcs = []
        for thread_index, thread in enumerate(secondary_thread_rows):
            rows = plot_points_by_thread_id.get(thread["id"], [])
            if not rows:
                _abort_partial_novel(
                    conn,
                    new_id,
                    f"secondary thread {thread_index + 1} has no plot points after truncation "
                    "— cannot build the outline without dropping the thread silently.",
                )
            outline_input_arcs.append(
                {
                    "thread_index": thread_index,
                    "continues_after_story": thread["length"] < 100,
                    "priority": thread["priority"],
                    "plot_points": [
                        {
                            "plot_point_index": i,
                            "summary": row["summary"],
                            "characters_involved": json.loads(row["characters_involved"] or "[]"),
                        }
                        for i, row in enumerate(rows)
                    ],
                }
            )
        outline = init_outline(
            novel_row,
            primary_thread_rows,
            outline_input_arcs,
            model=body.outline_model or DEFAULTS["outline"],
            reasoning=body.outline_reasoning,
        )
        for i, beat in enumerate(outline):
            conn.execute(
                """INSERT INTO outline_beats (id, novel_id, sort_order, content, word_count)
                   VALUES (?, ?, ?, ?, ?)""",
                (str(uuid.uuid4()), new_id, i, beat.get("content", ""), beat.get("word_count")),
            )
        conn.commit()

        # --- Entities: locations, items, organizations, events ---
        entities = init_entities(
            novel_row,
            worldbuilding_data,
            character_rows,
            primary_thread_rows,
            model=body.entities_model or DEFAULTS["entities"],
            reasoning=body.entities_reasoning,
        )
        for location in entities.get("locations", []):
            conn.execute(
                "INSERT INTO locations (id, novel_id, name, description) VALUES (?, ?, ?, ?)",
                (str(uuid.uuid4()), new_id, location.get("name", ""), location.get("description")),
            )
        for item in entities.get("items", []):
            conn.execute(
                "INSERT INTO items (id, novel_id, name, description) VALUES (?, ?, ?, ?)",
                (str(uuid.uuid4()), new_id, item.get("name", ""), item.get("description")),
            )
        for organization in entities.get("organizations", []):
            conn.execute(
                "INSERT INTO organizations (id, novel_id, name, description) VALUES (?, ?, ?, ?)",
                (
                    str(uuid.uuid4()),
                    new_id,
                    organization.get("name", ""),
                    organization.get("description"),
                ),
            )
        for event in entities.get("events", []):
            conn.execute(
                """INSERT INTO events
                   (id, novel_id, title, description, characters_involved, organizations_involved)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    str(uuid.uuid4()),
                    new_id,
                    event.get("title", ""),
                    event.get("description"),
                    json.dumps(event.get("characters_involved", [])),
                    json.dumps(event.get("organizations_involved", [])),
                ),
            )
        conn.commit()

        # --- Initial state: starting relationship graph ---
        # Disabled for now — full state system to be built later. Left
        # commented rather than deleted so it's easy to re-enable.
        #
        # location_rows = [
        #     dict(row)
        #     for row in conn.execute(
        #         "SELECT id, novel_id, name, description FROM locations WHERE novel_id = ?", (new_id,)
        #     ).fetchall()
        # ]
        # item_rows = [
        #     dict(row)
        #     for row in conn.execute(
        #         "SELECT id, novel_id, name, description FROM items WHERE novel_id = ?", (new_id,)
        #     ).fetchall()
        # ]
        # organization_rows = [
        #     dict(row)
        #     for row in conn.execute(
        #         "SELECT id, novel_id, name, description FROM organizations WHERE novel_id = ?",
        #         (new_id,),
        #     ).fetchall()
        # ]
        # event_rows = [
        #     dict(row)
        #     for row in conn.execute(
        #         "SELECT id, novel_id, title, description FROM events WHERE novel_id = ?", (new_id,)
        #     ).fetchall()
        # ]
        #
        # # Name -> id maps, built from the rows just read back from the
        # # database — the source of truth for ids is the database, not the
        # # model's raw output (which never sees ids at all).
        # character_id_by_name = {c["name"]: c["id"] for c in character_rows}
        # entity_id_by_type_and_name = {
        #     ("location", l["name"]): l["id"] for l in location_rows
        # } | {("item", i["name"]): i["id"] for i in item_rows}
        #
        # initial_state = init_relationships(
        #     novel_row,
        #     character_rows,
        #     {
        #         "locations": location_rows,
        #         "items": item_rows,
        #         "organizations": organization_rows,
        #         "events": event_rows,
        #     },
        #     model=body.initial_state_model or DEFAULTS["initial_state"],
        #     reasoning=body.initial_state_reasoning,
        # )
        #
        # for relationship in initial_state.get("character_relationships", []):
        #     character_id = character_id_by_name.get(relationship.get("character", ""))
        #     target_id = character_id_by_name.get(relationship.get("target_character", ""))
        #     if character_id is None or target_id is None:
        #         continue
        #     conn.execute(
        #         """INSERT INTO character_relationships
        #            (id, novel_id, character_id, target_character_id, relationship_type,
        #             status, emotional_intensity, open_threads)
        #            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        #         (
        #             str(uuid.uuid4()),
        #             new_id,
        #             character_id,
        #             target_id,
        #             relationship.get("relationship_type"),
        #             relationship.get("status"),
        #             relationship.get("emotional_intensity"),
        #             relationship.get("open_threads"),
        #         ),
        #     )
        # for relationship in initial_state.get("entity_relationships", []):
        #     character_id = character_id_by_name.get(relationship.get("character", ""))
        #     entity_type = relationship.get("entity_type")
        #     entity_id = entity_id_by_type_and_name.get((entity_type, relationship.get("entity", "")))
        #     if character_id is None or entity_id is None:
        #         continue
        #     conn.execute(
        #         """INSERT INTO entity_relationships
        #            (id, novel_id, character_id, entity_type, entity_id, relationship_type,
        #             status, open_threads)
        #            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        #         (
        #             str(uuid.uuid4()),
        #             new_id,
        #             character_id,
        #             entity_type,
        #             entity_id,
        #             relationship.get("relationship_type"),
        #             relationship.get("status"),
        #             relationship.get("open_threads"),
        #         ),
        #     )
        # conn.commit()

        return NovelCreateResponse(id=new_id)
    finally:
        conn.close()


# Get the generated characters for one novel.
@router.get("/novel/{id}/characters")
def get_characters(id: str) -> list[Character]:
    conn = get_connection()
    try:
        rows = conn.execute(
            f"SELECT {', '.join(_CHARACTER_COLUMNS)} FROM characters WHERE novel_id = ?",
            (id,),
        ).fetchall()
        return [_row_to_character(row) for row in rows]
    finally:
        conn.close()


# Get the generated locations for one novel.
@router.get("/novel/{id}/locations")
def get_locations(id: str) -> list[Location]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT id, novel_id, name, description FROM locations WHERE novel_id = ?", (id,)
        ).fetchall()
        return [Location(**row) for row in rows]
    finally:
        conn.close()


# Get the generated items for one novel.
@router.get("/novel/{id}/items")
def get_items(id: str) -> list[Item]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT id, novel_id, name, description FROM items WHERE novel_id = ?", (id,)
        ).fetchall()
        return [Item(**row) for row in rows]
    finally:
        conn.close()


# Get the generated organizations for one novel.
@router.get("/novel/{id}/organizations")
def get_organizations(id: str) -> list[Organization]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT id, novel_id, name, description FROM organizations WHERE novel_id = ?", (id,)
        ).fetchall()
        return [Organization(**row) for row in rows]
    finally:
        conn.close()


# Get the generated events for one novel.
@router.get("/novel/{id}/events")
def get_events(id: str) -> list[Event]:
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT id, novel_id, title, description, characters_involved, organizations_involved
               FROM events WHERE novel_id = ?""",
            (id,),
        ).fetchall()
        events = []
        for row in rows:
            data = dict(row)
            data["characters_involved"] = (
                json.loads(data["characters_involved"]) if data["characters_involved"] else []
            )
            data["organizations_involved"] = (
                json.loads(data["organizations_involved"]) if data["organizations_involved"] else []
            )
            events.append(Event(**data))
        return events
    finally:
        conn.close()


# Get the final, user-facing outline for one novel, in order. This is the
# only spine-like artifact exposed via the API — the primary thread and
# secondary arcs that fed into it are internal generation inputs.
@router.get("/novel/{id}/outline")
def get_outline(id: str) -> list[OutlineBeat]:
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT id, novel_id, sort_order, content, word_count
               FROM outline_beats WHERE novel_id = ? ORDER BY sort_order""",
            (id,),
        ).fetchall()
        return [OutlineBeat(**dict(row)) for row in rows]
    finally:
        conn.close()


# Get the secondary threads for one novel.
@router.get("/novel/{id}/secondary-threads")
def get_secondary_threads(id: str) -> list[SecondaryThread]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT id, novel_id, description, length, priority, heat, word_count FROM secondary_threads WHERE novel_id = ?",
            (id,),
        ).fetchall()
        return [SecondaryThread(**row) for row in rows]
    finally:
        conn.close()


# Add a secondary thread to an existing novel. Capped at 3 per novel,
# matching the limit enforced client-side during creation.
@router.post("/novel/{id}/secondary-threads")
def create_secondary_thread(id: str, body: SecondaryThreadCreate) -> SecondaryThread:
    conn = get_connection()
    try:
        count = conn.execute(
            "SELECT COUNT(*) FROM secondary_threads WHERE novel_id = ?", (id,)
        ).fetchone()[0]
        if count >= 3:
            raise HTTPException(status_code=400, detail="A novel may have at most 3 secondary threads")

        new_id = str(uuid.uuid4())
        conn.execute(
            """INSERT INTO secondary_threads (id, novel_id, description, length, priority, heat)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (new_id, id, body.description, body.length, body.priority, body.heat),
        )
        conn.commit()
        row = conn.execute(
            "SELECT id, novel_id, description, length, priority, heat, word_count FROM secondary_threads WHERE id = ?",
            (new_id,),
        ).fetchone()
        return SecondaryThread(**dict(row))
    finally:
        conn.close()


# Delete one secondary thread.
@router.delete("/novel/{novel_id}/secondary-threads/{thread_id}")
def delete_secondary_thread(novel_id: str, thread_id: str):
    conn = get_connection()
    try:
        cursor = conn.execute(
            "DELETE FROM secondary_threads WHERE id = ? AND novel_id = ?", (thread_id, novel_id)
        )
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Secondary thread not found")
        return {"status": "deleted"}
    finally:
        conn.close()


# Shared PATCH logic for the simple name/description-style entity tables
# (characters, locations, items, organizations). Fetches the row scoped to
# novel_id, merges in only the fields the client actually sent, writes it
# back, and returns the updated row as the given model.
def _update_entity(table: str, columns: list[str], novel_id: str, entity_id: str, body, model_cls):
    updates = body.model_dump(exclude_unset=True)
    conn = get_connection()
    try:
        row = conn.execute(
            f"SELECT {', '.join(columns)} FROM {table} WHERE id = ? AND novel_id = ?",
            (entity_id, novel_id),
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail=f"{table[:-1].capitalize()} not found")

        updated = model_cls(**dict(row)).model_copy(update=updates)
        update_columns = [col for col in columns if col not in ("id", "novel_id")]
        set_clause = ", ".join(f"{col} = ?" for col in update_columns)
        values = [getattr(updated, col) for col in update_columns]
        values.extend([entity_id, novel_id])

        conn.execute(f"UPDATE {table} SET {set_clause} WHERE id = ? AND novel_id = ?", values)
        conn.commit()
        return updated
    finally:
        conn.close()


# Update one character. Only provided fields are changed.
@router.patch("/novel/{novel_id}/characters/{entity_id}")
def update_character(novel_id: str, entity_id: str, body: CharacterUpdate) -> Character:
    updates = body.model_dump(exclude_unset=True)
    conn = get_connection()
    try:
        row = conn.execute(
            f"SELECT {', '.join(_CHARACTER_COLUMNS)} FROM characters WHERE id = ? AND novel_id = ?",
            (entity_id, novel_id),
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Character not found")

        updated = _row_to_character(row).model_copy(update=updates)
        update_columns = [col for col in _CHARACTER_COLUMNS if col not in ("id", "novel_id")]
        set_clause = ", ".join(f"{col} = ?" for col in update_columns)
        values = []
        for col in update_columns:
            value = getattr(updated, col)
            if col in _CHARACTER_JSON_COLUMNS:
                value = json.dumps(value)
            values.append(value)
        values.extend([entity_id, novel_id])

        conn.execute(f"UPDATE characters SET {set_clause} WHERE id = ? AND novel_id = ?", values)
        conn.commit()
        return updated
    finally:
        conn.close()


# Update one location. Only provided fields are changed.
@router.patch("/novel/{novel_id}/locations/{entity_id}")
def update_location(novel_id: str, entity_id: str, body: LocationUpdate) -> Location:
    return _update_entity(
        "locations", ["id", "novel_id", "name", "description"], novel_id, entity_id, body, Location
    )


# Update one item. Only provided fields are changed.
@router.patch("/novel/{novel_id}/items/{entity_id}")
def update_item(novel_id: str, entity_id: str, body: ItemUpdate) -> Item:
    return _update_entity(
        "items", ["id", "novel_id", "name", "description"], novel_id, entity_id, body, Item
    )


# Update one organization. Only provided fields are changed.
@router.patch("/novel/{novel_id}/organizations/{entity_id}")
def update_organization(novel_id: str, entity_id: str, body: OrganizationUpdate) -> Organization:
    return _update_entity(
        "organizations", ["id", "novel_id", "name", "description"], novel_id, entity_id, body, Organization
    )


# Update one secondary thread. Only provided fields are changed.
@router.patch("/novel/{novel_id}/secondary-threads/{entity_id}")
def update_secondary_thread(novel_id: str, entity_id: str, body: SecondaryThreadUpdate) -> SecondaryThread:
    return _update_entity(
        "secondary_threads",
        ["id", "novel_id", "description", "length", "priority", "heat", "word_count"],
        novel_id,
        entity_id,
        body,
        SecondaryThread,
    )


# Update one outline beat. Only provided fields are changed. sort_order is
# intentionally not editable — OutlineBeatUpdate has no field for it, since
# reordering beats would need to reflow the whole outline, not a single-field edit.
@router.patch("/novel/{novel_id}/outline-beats/{entity_id}")
def update_outline_beat(novel_id: str, entity_id: str, body: OutlineBeatUpdate) -> OutlineBeat:
    return _update_entity(
        "outline_beats",
        ["id", "novel_id", "sort_order", "content", "word_count"],
        novel_id,
        entity_id,
        body,
        OutlineBeat,
    )


# Update one event. Only provided fields are changed. Handled separately from
# _update_entity since its characters_involved/organizations_involved columns
# are JSON-encoded lists, not plain strings.
@router.patch("/novel/{novel_id}/events/{entity_id}")
def update_event(novel_id: str, entity_id: str, body: EventUpdate) -> Event:
    updates = body.model_dump(exclude_unset=True)
    conn = get_connection()
    try:
        row = conn.execute(
            """SELECT id, novel_id, title, description, characters_involved, organizations_involved
               FROM events WHERE id = ? AND novel_id = ?""",
            (entity_id, novel_id),
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Event not found")

        data = dict(row)
        data["characters_involved"] = (
            json.loads(data["characters_involved"]) if data["characters_involved"] else []
        )
        data["organizations_involved"] = (
            json.loads(data["organizations_involved"]) if data["organizations_involved"] else []
        )
        updated = Event(**data).model_copy(update=updates)

        conn.execute(
            """UPDATE events SET title = ?, description = ?, characters_involved = ?,
               organizations_involved = ? WHERE id = ? AND novel_id = ?""",
            (
                updated.title,
                updated.description,
                json.dumps(updated.characters_involved),
                json.dumps(updated.organizations_involved),
                entity_id,
                novel_id,
            ),
        )
        conn.commit()
        return updated
    finally:
        conn.close()


# Get the character-to-character relationship graph for one novel.
@router.get("/novel/{id}/character-relationships")
def get_character_relationships(id: str) -> list[CharacterRelationship]:
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT id, novel_id, character_id, target_character_id, relationship_type,
                      status, emotional_intensity, open_threads
               FROM character_relationships WHERE novel_id = ?""",
            (id,),
        ).fetchall()
        return [CharacterRelationship(**row) for row in rows]
    finally:
        conn.close()


# Get the character-to-item/location relationships for one novel.
@router.get("/novel/{id}/entity-relationships")
def get_entity_relationships(id: str) -> list[EntityRelationship]:
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT id, novel_id, character_id, entity_type, entity_id, relationship_type,
                      status, open_threads
               FROM entity_relationships WHERE novel_id = ?""",
            (id,),
        ).fetchall()
        return [EntityRelationship(**row) for row in rows]
    finally:
        conn.close()


# Update one novel. Only provided fields are changed.
@router.patch("/novel/{id}")
def update_novel(id: str, body: NovelUpdate) -> Novel:
    updates = body.model_dump(exclude_unset=True)
    conn = get_connection()
    try:
        row = conn.execute(
            f"SELECT {', '.join(_NOVEL_COLUMNS)} FROM novels WHERE id = ?", (id,)
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Novel not found")

        updated = _row_to_novel(row).model_copy(update=updates)
        update_columns = [col for col in _NOVEL_COLUMNS if col != "id"]
        set_clause = ", ".join(f"{col} = ?" for col in update_columns)

        values = []
        for col in update_columns:
            value = getattr(updated, col)
            if col in _JSON_COLUMNS:
                value = json.dumps(value)
            values.append(value)
        values.append(id)

        conn.execute(f"UPDATE novels SET {set_clause} WHERE id = ?", values)
        conn.commit()
        return updated
    finally:
        conn.close()


# Delete one novel.
@router.delete("/novel/{id}")
def delete_novel(id: str):
    conn = get_connection()
    try:
        cursor = conn.execute("DELETE FROM novels WHERE id = ?", (id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Novel not found")
        return {"status": "deleted"}
    finally:
        conn.close()

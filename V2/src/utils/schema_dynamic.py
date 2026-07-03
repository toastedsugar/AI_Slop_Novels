# =============================================================================
# SCHEMA REGISTRY — DYNAMIC TABLES
# Tracks state that changes chapter to chapter. When adding a field,
# start here, then update: db_helpers.py
#
# Values are example data — same rendering convention as schema_static.
# Fields prefixed with _ are DB-only and excluded from prompts.
# =============================================================================

DYNAMIC = {
    # One row per character per chapter (or beat). Snapshot of who they are
    # at the end of that chapter. Latest row = current state.
    "character_state": {
        "_id":                  "uuid-v4",
        "_character_id":        "uuid-v4",
        "_chapter_id":          "uuid-v4",
        "_chapter_number":      1,
        "_story_datetime":      "ISO datetime when this state was recorded in story time",
        "_source":              "spine | chapter | extraction",
        "emotional_state":      "Qualitative description of how this character feels right now.",
        "emotional_intensity":  7,
        "physical_state":       "Physical condition — injuries, exhaustion, restraints, clothing state.",
        "current_location_id":  "uuid-v4 of the location they are currently at",
        "goals":                ["Primary goal they are actively pursuing.", "Secondary goal if present."],
        "flaw_active":          True,
        "flaw_note":            "How the flaw is manifesting right now, if active.",
        "knowledge_flags":      {"example_fact": "What this character knows about it."},
    },

    # One row per (character, entity) pair per chapter. Tracks how a character
    # feels toward another character, location, item, faction, or event.
    # Character-outward only — Cal→Thistle and Thistle→Cal are separate rows
    # because their dispositions and open threads are genuinely asymmetric.
    "character_relationships": {
        "_id":                  "uuid-v4",
        "_character_id":        "uuid-v4",
        "_chapter_id":          "uuid-v4",
        "_story_datetime":      "ISO datetime when this state was recorded in story time",
        "_source":              "spine | chapter | extraction",
        "entity_type":          "character | location | item | organization | event",
        "entity_id":            "uuid-v4 of the target entity",
        "relationship_type":    "romantic_tension | rival | ally | mentor | home | sacred | threat | etc.",
        "status":               "Natural language current status of the relationship.",
        "emotional_intensity":  6,
        "disposition":          "How this character feels toward this entity right now.",
        "open_threads":         ["What is unresolved between them.", "A second unresolved thread if present."],
    },

    # One row per item per chapter. Tracks where an item is, who holds it,
    # its condition, and whether the assembler should surface it in the prompt.
    "item_state": {
        "_id":                      "uuid-v4",
        "_item_id":                 "uuid-v4",
        "_chapter_id":              "uuid-v4",
        "_story_datetime":          "ISO datetime when this state was recorded in story time",
        "_source":                  "spine | chapter | extraction",
        "holder_character_id":      "uuid-v4 of the character holding it, or null if unheld",
        "location_id":              "uuid-v4 of the location it is at if unheld, or null",
        "condition":                "Current physical condition of the item.",
        "narrative_visibility":     "planted | active | resolved | dormant",
        "narrative_salience":       8,
    },
}


def dynamic_schema_to_json(*tables: str) -> str:
    """
    Renders one or more tables from DYNAMIC into a JSON example block
    suitable for injection into a prompt. DB-only fields (prefixed with _)
    are excluded from prompt output.

    Usage:
        dynamic_schema_to_json("character_state", "character_relationships")
    """
    import json

    ARRAY_TABLES = {"character_state", "character_relationships", "item_state"}

    result = {}
    for table in tables:
        fields = DYNAMIC[table]
        example = {k: v for k, v in fields.items() if not k.startswith("_")}
        result[table] = [example] if table in ARRAY_TABLES else example

    return json.dumps(result, indent=2)

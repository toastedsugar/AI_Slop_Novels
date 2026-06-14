# =============================================================================
# SCHEMA REGISTRY — STATIC TABLES
# Single source of truth for all static table fields. When adding a field,
# start here, then update: db_helpers.py -> prompts/outline.py
#
# Values are example data — the renderer serializes these directly into prompt
# schema blocks. Type is inferred from the value: str, int, bool, list.
# Fields prefixed with _ are DB-only (PKs, FKs) and are excluded from prompts.
# =============================================================================

STATIC = {
    "novel": {
        "_id":               "nov_1",
        "_created_at":       "ISO datetime",
        "_prompt":           "User's original story prompt",
        "_target_word_count": 70000,
        "title":             "Story title",
        "summary":           "2-3 sentence summary of the story — the core dramatic tension and what the story is fundamentally about.",
        "author":            "Author name",
        "word_count":        5000,
        "premise":           "A full synopsis of the full story arc.",
        "protagonist_stubs": ["Protagonist 1 paragraph stub", "Protagonist 2 paragraph stub"],
        "antagonist_stubs":  ["Antagonist 1 paragraph stub", "Antagonist 2 paragraph stub"],
        "primary_genre":     "Romance",
        "sub_genres":        ["Romance", "Fantasy"],
        "tone":              "Overall tone of the story.",
        "spice_level":       "low | medium | high | explicit",
        "literary_voice":    "Author style e.g. F. Scott Fitzgerald",
        "tense":             "past | present",
        "perspective":       "first_person | third_person_limited | third_person_omniscient",
        "forbidden_element": "The structural reason the attraction is forbidden, dangerous, or should not happen.",
    },
    "spine": {
        "_id":      "spine_1",
        "_novel_id": "nov_1",
        "word_count": 70000,
        "narrative_structure": [
            {
                "heros_journey_step": "ordinary_world | inciting_incident | crossing_threshold | rising_complications | midpoint | antagonist_peaks | all_is_lost | climax | resolution",
                "summary": "Dense 3-5 sentence description of what happens, why, the emotional stakes, and what changes.",
                "word_count_pct": 10,
                "time_gap_before": "How much time has passed since the previous beat, e.g. 'same day', 'two weeks later', 'immediately'.",
                "forbidden_element_active": True,
                "spice_arc_role": "tension-building | escalation | payoff | none",
                "character_arcs": {
                    "protagonist_name": {
                        "emotional_state": ["How they feel.", "A second emotional layer if present."],
                        "current_goal": ["Primary goal they are actively pursuing.", "Secondary goal if present."],
                        "flaw_active": True,
                        "flaw_note": "How the flaw is manifesting in this beat, if active.",
                        "relationships": [
                            {
                                "character": "other_character_name",
                                "status": "Current relationship status and dynamic."
                            }
                        ]
                    }
                }
            }
        ],
    },
    "worldbuilding": {
        "_id":                          "world_1",
        "_novel_id":                    "nov_1",
        "story_type":                   "fantasy | historical | contemporary | sci-fi | etc.",
        "time_period":                  "e.g. 1920s | contemporary | Age of Sail",
        "anchor_location":              "Primary home base location name.",
        "anchor_location_description":  "What it looks like and its atmosphere.",
        "base_climate":                 "The fixed climate of the setting e.g. arid, tropical, tundra.",
        "constraints":                  ["Genre conventions", "magic systems", "technology rules"],
        "social_hierarchy":             "Who has power over whom and the class structure of this world.",
        "cultural_norms":               ["What is considered normal or acceptable in this world.", "A second cultural norm."],
        "dominant_institutions":        ["The primary organization or power controlling daily life.", "A second institution."],
        "technology_level":             "What technology exists and what doesn't in one sentence.",
        "languages":                    ["Primary language spoken.", "Dialect or class-based speech difference."],
        "taboos":                       ["A culturally forbidden act or subject beyond the romantic taboo.", "A second taboo."],
        "gender_dynamics":              "How gender and power intersect in this world.",
        "economic_conditions":          "Whether this is a world of scarcity or abundance, and the general economic mood.",
        "historical_context":           "A recent event that shaped the current world e.g. a war, collapse, or plague.",
        "mobility":                     "How people travel and move between places, and whether escape is easy or hard.",
        "political_climate":            "Who is in control, how stable that control is, and the mood on the street.",
        "religion":                     "What people believe, whether it is institutionalized, and how much it governs daily life.",
        "relationship_norms":           "What kinds of relationships are sanctioned, what is scandalous, and what is invisible.",
    },
    "characters": {
        "id":                       "uuid-v4",
        "name":                     "Full name",
        "age":                      0,
        "gender":                   "female | male | other",
        "sexuality":                "heterosexual | homosexual | bisexual | etc.",
        "role":                     "protagonist | antagonist | love_interest | supporting",
        "occupation":               "What they do and their social/economic status.",
        "appearance":               "Physical appearance summary.",
        "physical_characteristics": ["small breasts", "glasses", "blonde hair"],
        "personality":              ["trait 1", "trait 2", "trait 3"],
        "arc":                      "How this character changes over the story.",
        "backstory":                "One or two sentences on where they came from and what shaped them.",
        "goals":                    ["become an airplane pilot", "revitalize their business"],
        "fears":                    ["What they are running from or avoiding.", "The emotional wound driving their behaviour."],
        "flaws":                    ["The core character flaw that will create conflict or drive their arc."],
        "contradictions":           ["Presents as X but is actually Y."],
        "hobbies":                  ["hobby 1", "hobby 2"],
        "spiritual_beliefs":        ["belief or practice 1", "belief or practice 2"],
        "character_voice":          ["Formal and measured speech", "Uses metaphors frequently"],
        "character_speech_patterns": ["Calls the male lead 'darling'", "Trails off mid-sentence when flustered"],
        "narrative_stakes":         ["What this character stands to lose if the story goes wrong.", "A second thing they stand to lose."],
    },
    "locations": {
        "id":           "uuid-v4",
        "name":         "Location name",
        "region":       "Broader area or region it belongs to.",
        "description":  "What it looks like.",
        "atmosphere":   "Baseline mood and sensory character.",
        "significance": "Why it matters to the story.",
        "hours":        "18:00-02:00 daily | null if unrestricted",
        "access":       "Natural language access condition, or null if unrestricted.",
        "sentient":     False,
    },
    "items": {
        "id":               "uuid-v4",
        "name":             "Item name",
        "description":      "What it is.",
        "symbolic_weight":  "What this object means psychologically.",
        "significance":     "Its role or symbolic meaning.",
        "sentient":         False,
    },
    "organizations": {
        "id":        "uuid-v4",
        "name":      "Organization name",
        "type":      "corporate | fae | civic | guild | etc.",
        "goals":     "What the organization is trying to achieve.",
        "resources": "What assets and leverage they have.",
        "access":    "Natural language access condition, or null if unrestricted.",
    },
    "events": {
        "id":                       "uuid-v4",
        "title":                    "Event name",
        "description":              "What happens.",
        "occurred_datetime":        "ISO datetime when the event occurred, or null.",
        "status":                   "pending | occurred | prevented | delayed",
        "characters_involved":      ["uuid-v4 of character", "uuid-v4 of character"],
        "organizations_involved":   ["uuid-v4 of organization"],
        "narrative_salience":       8,
    },
    "chapters": {
        "id":                        "uuid-v4",
        "chapter_number":            1,
        "title":                     "Chapter title",
        "word_count":                2500,
        "purpose":                   "One sentence: what this chapter must accomplish in the story arc.",
        "summary":                   "Full narrative description of everything that happens in this chapter — multiple dense paragraphs. Covers all scenes, character actions, dialogue beats, emotional turns, and how the chapter closes. Detailed enough that a writer could produce the prose from this alone.",
        "emotional_arc":             "Where the POV character starts emotionally and where they end by the close of the chapter.",
        "intimate_arc_role":         "tension-building | escalation | payoff | none",
        "chapter_end_hook":          "The specific moment the chapter closes on — not a summary, the exact beat.",
        "characters_present_ids":    ["uuid-v4 of every character who appears in this chapter"],
        "location_ids":              ["uuid-v4 of every location used in this chapter"],
        "items_present_ids":         ["uuid-v4 of every item that appears in this chapter"],
        "organizations_present_ids": ["uuid-v4 of every organization active in this chapter"],
        "events_present_ids":        ["uuid-v4 of every story event that occurs or is triggered in this chapter"],
    },
    "beats": {
        "id":                       "uuid-v4",
        "chapter_id":               "uuid-v4 of the chapter this beat belongs to",
        "beat_number":              1,
        "description":              "What happens in this beat and its narrative purpose.",
        "pov":                      "uuid-v4 of the POV character",
        "word_count":               500,
        "location_id":              "uuid-v4 of the location",
        "characters_present_ids":   ["uuid-v4 of character", "uuid-v4 of character"],
        "items_present_ids":        ["uuid-v4 of item"],
        "organizations_involved":   ["uuid-v4 of organization"],
        "events_ids":               ["uuid-v4 of event this beat belongs to or triggers"],
        "tension_level":            "low | medium | high | climax",
        "heat_level":               "none | slow_burn | charged | explicit",
        "key_events":               ["First event.", "Second event."],
    },
}


def schema_to_json(*tables: str) -> str:
    """
    Renders one or more tables from STATIC into a JSON example block
    suitable for injection into a prompt. DB-only fields (prefixed with _)
    are excluded from prompt output.

    Usage:
        schema_to_json("characters", "locations", "items")
    """
    import json

    ARRAY_TABLES = {"characters", "locations", "items", "organizations", "events", "chapters", "beats"}
    # "novel" is intentionally excluded — it's a single object, not an array

    result = {}
    for table in tables:
        fields = STATIC[table]
        example = {k: v for k, v in fields.items() if not k.startswith("_")}
        result[table] = [example] if table in ARRAY_TABLES else example

    return json.dumps(result, indent=2)

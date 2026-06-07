# =============================================================================
# SCHEMA REGISTRY — STATIC TABLES
# Single source of truth for all static table fields. When adding a field,
# start here, then update: db_init.py -> db_insert_outline.py -> prompts/outline.py
#
# Values are example data — the renderer serializes these directly into prompt
# schema blocks. Type is inferred from the value: str, int, bool, list.
# Fields prefixed with _ are DB-only (PKs, FKs) and are excluded from prompts.
# =============================================================================

STATIC = {
    "novel": {
        "_id":          "nov_1",
        "_created_at":  "ISO datetime",
        "title":        "Story title",
        "author":       "Author name",
        "word_count":   5000,
    },
    "metadata": {
        "_id":               "meta_1",
        "_novel_id":         "nov_1",
        "premise":           "A full synopsis of the full story arc.",
        "protagonist_stubs": ["Protagonist 1 paragraph stub", "Protagonist 2 paragraph stub"],
        "antagonist_stubs":  ["Antagonist 1 paragraph stub", "Antagonist 2 paragraph stub"],
        "primary_genre":     "Romance",
        "sub_genres":       ["Romance", "Fantasy"],
        "tone":             "Overall tone of the story.",
        "spice_level":      "low | medium | high | explicit",
        "literary_voice":   "Author style e.g. F. Scott Fitzgerald",
        "tense":            "past | present",
        "perspective":      "first_person | third_person_limited | third_person_omniscient",
        "forbidden_element": "The structural reason the attraction is forbidden, dangerous, or should not happen.",
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
        "initial_holder":   "uuid-v4 of the character holding this item | null if unheld at story start",
        "initial_location": "uuid-v4 of the location this item starts at | null if held by a character",
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
        "scheduled_datetime":       "ISO datetime when expected, or null.",
        "status":                   "pending | occurred | prevented | delayed",
        "characters_involved":      ["uuid-v4 of character", "uuid-v4 of character"],
        "organizations_involved":   ["uuid-v4 of organization"],
        "narrative_salience":       8,
    },
    "chapters": {
        "id":                "uuid-v4",
        "chapter_number":    1,
        "title":             "Chapter title",
        "word_count":        2500,
        "summary":           "What happens in this chapter.",
        "emotional_arc":     "Where the POV character starts emotionally and where they end by the close of the chapter.",
        "intimate_arc_role": "tension-building | escalation | payoff | none",
        "chapter_end_hook":  "What propels the reader into the next chapter — cliffhanger, revelation, unresolved question, etc.",
    },
    "beats": {
        "id":                     "uuid-v4",
        "chapter_id":             "uuid-v4 of the chapter this beat belongs to",
        "beat_number":            1,
        "description":            "What happens in this beat and its narrative purpose.",
        "pov":                    "uuid-v4 of the POV character",
        "word_count":             500,
        "location_id":            "uuid-v4 of the location",
        "characters_present_ids": ["uuid-v4 of character", "uuid-v4 of character"],
        "items_present_ids":      ["uuid-v4 of item"],
        "tension_level":          "low | medium | high | climax",
        "heat_level":             "none | slow_burn | charged | explicit",
        "key_events":             ["First event.", "Second event."],
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

    result = {}
    for table in tables:
        fields = STATIC[table]
        example = {k: v for k, v in fields.items() if not k.startswith("_")}
        result[table] = example

    return json.dumps(result, indent=2)

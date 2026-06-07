import json
import uuid
from datetime import datetime, timezone

from utils.db_init import get_connection, init_db


# The uuids from the model are unreliable, so we need to remap them to real uuids that are generated serverside.
def _remap(model_id, id_map, field_name):
    """Look up a model-generated id in the map. Logs and returns None if missing."""
    if model_id is None:
        return None
    real = id_map.get(model_id)
    if real is None:
        print(f"  WARNING: unresolvable {field_name} reference '{model_id}' — set to NULL")
    return real


def _remap_list(model_ids, id_map, field_name):
    """Remap a list of model ids, dropping any that don't resolve."""
    result = []
    for mid in model_ids:
        real = id_map.get(mid)
        if real is None:
            print(f"  WARNING: unresolvable {field_name} reference '{mid}' — dropped")
        else:
            result.append(real)
    return result


def insert_outline(outline_json: str):
    """
    Takes the merged outline JSON string from NovelGen.generate_outline()
    and inserts it into the database. Returns the novel_id.
    """
    init_db()
    outline = json.loads(outline_json)

    novel_id = str(uuid.uuid4())
    meta = outline.get("metadata", {})
    world = outline.get("worldbuilding", {})

    # Build model_id → real_uuid maps before any inserts so cross-references resolve.
    char_ids  = {c["id"]: str(uuid.uuid4()) for c in outline.get("characters",    []) if c.get("id")}
    loc_ids   = {l["id"]: str(uuid.uuid4()) for l in outline.get("locations",     []) if l.get("id")}
    item_ids  = {i["id"]: str(uuid.uuid4()) for i in outline.get("items",         []) if i.get("id")}
    org_ids   = {o["id"]: str(uuid.uuid4()) for o in outline.get("organizations", []) if o.get("id")}
    chap_ids  = {c["id"]: str(uuid.uuid4()) for c in outline.get("chapters",      []) if c.get("id")}

    conn = get_connection()
    c = conn.cursor()

    # novel
    c.execute(
        "INSERT INTO novel (id, title, author, word_count, created_at) VALUES (?, ?, ?, ?, ?)",
        (
            novel_id,
            meta.get("title", "Untitled"),
            None,
            meta.get("word_count"),
            datetime.now(timezone.utc).isoformat(),
        ),
    )

    # metadata
    c.execute(
        """INSERT INTO metadata
           (id, novel_id, premise, primary_genre, sub_genres, tone, spice_level, literary_voice, tense, perspective, forbidden_element)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            str(uuid.uuid4()),
            novel_id,
            outline.get("premise"),
            meta.get("primary_genre"),
            json.dumps(meta.get("sub_genres", [])),
            meta.get("tone"),
            meta.get("spice_level"),
            meta.get("literary_voice"),
            meta.get("tense"),
            meta.get("perspective"),
            meta.get("forbidden_element"),
        ),
    )

    # worldbuilding
    c.execute(
        """INSERT INTO worldbuilding
           (id, novel_id, story_type, time_period, anchor_location, anchor_location_description,
            base_climate, constraints, social_hierarchy, cultural_norms, dominant_institutions,
            technology_level, languages, taboos, gender_dynamics, economic_conditions,
            historical_context, mobility, political_climate, religion, relationship_norms)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            str(uuid.uuid4()),
            novel_id,
            world.get("story_type"),
            world.get("time_period"),
            world.get("anchor_location"),
            world.get("anchor_location_description"),
            world.get("base_climate"),
            json.dumps(world.get("constraints", [])),
            world.get("social_hierarchy"),
            json.dumps(world.get("cultural_norms", [])),
            json.dumps(world.get("dominant_institutions", [])),
            world.get("technology_level"),
            json.dumps(world.get("languages", [])),
            json.dumps(world.get("taboos", [])),
            world.get("gender_dynamics"),
            world.get("economic_conditions"),
            world.get("historical_context"),
            world.get("mobility"),
            world.get("political_climate"),
            world.get("religion"),
            world.get("relationship_norms"),
        ),
    )

    # characters
    for char in outline.get("characters", []):
        c.execute(
            """INSERT OR IGNORE INTO characters
               (id, novel_id, name, age, gender, sexuality, role, occupation,
                appearance, physical_characteristics, personality, arc, backstory,
                goals, fears, flaws, contradictions, hobbies, spiritual_beliefs, voice, speech_patterns, narrative_stakes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                char_ids.get(char.get("id"), str(uuid.uuid4())),
                novel_id,
                char.get("name", ""),
                char.get("age"),
                char.get("gender"),
                char.get("sexuality"),
                char.get("role"),
                char.get("occupation"),
                char.get("description"),
                json.dumps(char.get("physical_characteristics", [])),
                json.dumps(char.get("personality", [])),
                char.get("arc"),
                char.get("backstory"),
                json.dumps(char.get("goals", [])),
                json.dumps(char.get("fears", [])),
                json.dumps(char.get("flaws", [])),
                json.dumps(char.get("contradictions", [])),
                json.dumps(char.get("hobbies", [])),
                json.dumps(char.get("spiritual_beliefs", [])),
                json.dumps(char.get("character_voice", [])),
                json.dumps(char.get("character_speech_patterns", [])),
                json.dumps(char.get("narrative_stakes", [])),
            ),
        )

    # locations
    for loc in outline.get("locations", []):
        c.execute(
            """INSERT OR IGNORE INTO locations
               (id, novel_id, name, description, atmosphere)
               VALUES (?, ?, ?, ?, ?)""",
            (
                loc_ids.get(loc.get("id"), str(uuid.uuid4())),
                novel_id,
                loc.get("name", ""),
                loc.get("description"),
                loc.get("significance"),
            ),
        )

    # items
    for item in outline.get("items", []):
        c.execute(
            """INSERT OR IGNORE INTO items
               (id, novel_id, name, description, symbolic_weight)
               VALUES (?, ?, ?, ?, ?)""",
            (
                item_ids.get(item.get("id"), str(uuid.uuid4())),
                novel_id,
                item.get("name", ""),
                item.get("description"),
                item.get("significance"),
            ),
        )

    # organizations
    for org in outline.get("organizations", []):
        c.execute(
            """INSERT OR IGNORE INTO organizations
               (id, novel_id, name, type, goals, resources, access)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                org_ids.get(org.get("id"), str(uuid.uuid4())),
                novel_id,
                org.get("name", ""),
                org.get("type"),
                org.get("goals"),
                org.get("resources"),
                org.get("access"),
            ),
        )

    # events — characters_involved and organizations_involved are cross-references
    for evt in outline.get("events", []):
        c.execute(
            """INSERT OR IGNORE INTO events
               (id, novel_id, title, description, scheduled_datetime, status,
                characters_involved, organizations_involved, narrative_salience)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                str(uuid.uuid4()),
                novel_id,
                evt.get("title", ""),
                evt.get("description"),
                evt.get("scheduled_datetime"),
                evt.get("status"),
                json.dumps(_remap_list(evt.get("characters_involved", []),    char_ids, "characters_involved")),
                json.dumps(_remap_list(evt.get("organizations_involved", []), org_ids,  "organizations_involved")),
                evt.get("narrative_salience"),
            ),
        )

    # chapters
    for chap in outline.get("chapters", []):
        c.execute(
            """INSERT INTO chapter
               (id, novel_id, chapter_number, title, word_count, summary, emotional_arc, intimate_arc_role, chapter_end_hook)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                chap_ids.get(chap.get("id"), str(uuid.uuid4())),
                novel_id,
                chap.get("chapter_number"),
                chap.get("title"),
                chap.get("word_count"),
                chap.get("summary"),
                chap.get("emotional_arc"),
                chap.get("intimate_arc_role"),
                chap.get("chapter_end_hook"),
            ),
        )

    # beats — all cross-references remapped through the id maps
    for beat in outline.get("beats", []):
        c.execute(
            """INSERT INTO beats
               (id, chapter_id, beat_number, description, pov, word_count, location_id,
                characters_present_ids, items_present_ids, tension_level, heat_level, key_events)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                str(uuid.uuid4()),
                _remap(beat.get("chapter_id"), chap_ids, "chapter_id"),
                beat.get("beat_number"),
                beat.get("description"),
                _remap(beat.get("pov"),         char_ids, "pov"),
                beat.get("word_count"),
                _remap(beat.get("location_id"), loc_ids,  "location_id"),
                json.dumps(_remap_list(beat.get("characters_present_ids", []), char_ids, "characters_present_ids")),
                json.dumps(_remap_list(beat.get("items_present_ids", []),      item_ids, "items_present_ids")),
                beat.get("tension_level"),
                beat.get("heat_level"),
                json.dumps(beat.get("key_events", [])),
            ),
        )

    conn.commit()
    conn.close()

    print(f"Outline inserted into DB with novel_id: {novel_id}")
    return novel_id

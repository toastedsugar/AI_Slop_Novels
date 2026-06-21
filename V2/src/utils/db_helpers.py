import json
import os
import sqlite3
import uuid

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "db", "slopnovels.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS novel (
            id                TEXT PRIMARY KEY,
            created_at        TEXT,
            prompt            TEXT,
            target_word_count INTEGER,
            title             TEXT,
            summary           TEXT,
            author            TEXT,
            word_count        INTEGER,
            premise           TEXT,
            protagonist_stubs TEXT,
            antagonist_stubs  TEXT,
            primary_genre     TEXT,
            sub_genres        TEXT,
            tone              TEXT,
            spice_level       TEXT,
            literary_voice    TEXT,
            tense             TEXT,
            perspective       TEXT,
            forbidden_element TEXT,
            authorial_voice   TEXT
        );

        CREATE TABLE IF NOT EXISTS costs (
            id            TEXT PRIMARY KEY,
            novel_id      TEXT NOT NULL REFERENCES novel(id),
            stage         TEXT NOT NULL,
            model         TEXT,
            input_tokens  INTEGER,
            output_tokens INTEGER,
            cost          REAL,
            created_at    TEXT
        );

        CREATE TABLE IF NOT EXISTS worldbuilding (
            id                          TEXT PRIMARY KEY,
            novel_id                    TEXT NOT NULL REFERENCES novel(id),
            story_type                  TEXT,
            time_period                 TEXT,
            anchor_location             TEXT,
            anchor_location_description TEXT,
            base_climate                TEXT,
            constraints                 TEXT,
            social_hierarchy            TEXT,
            cultural_norms              TEXT,
            dominant_institutions       TEXT,
            technology_level            TEXT,
            languages                   TEXT,
            taboos                      TEXT,
            gender_dynamics             TEXT,
            economic_conditions         TEXT,
            historical_context          TEXT,
            mobility                    TEXT,
            political_climate           TEXT,
            religion                    TEXT,
            relationship_norms          TEXT
        );

        CREATE TABLE IF NOT EXISTS spine (
            id                  TEXT PRIMARY KEY,
            novel_id            TEXT NOT NULL REFERENCES novel(id),
            word_count          INTEGER,
            narrative_structure TEXT
        );

        CREATE TABLE IF NOT EXISTS characters (
            id                       TEXT PRIMARY KEY,
            novel_id                 TEXT NOT NULL REFERENCES novel(id),
            name                     TEXT NOT NULL,
            age                      INTEGER,
            gender                   TEXT,
            sexuality                TEXT,
            role                     TEXT,
            occupation               TEXT,
            appearance               TEXT,
            physical_characteristics TEXT,
            personality              TEXT,
            arc                      TEXT,
            backstory                TEXT,
            goals                    TEXT,
            fears                    TEXT,
            flaws                    TEXT,
            contradictions           TEXT,
            hobbies                  TEXT,
            spiritual_beliefs        TEXT,
            voice                    TEXT,
            speech_patterns          TEXT,
            narrative_stakes         TEXT
        );

        CREATE TABLE IF NOT EXISTS locations (
            id           TEXT PRIMARY KEY,
            novel_id     TEXT NOT NULL REFERENCES novel(id),
            name         TEXT NOT NULL,
            region       TEXT,
            description  TEXT,
            atmosphere   TEXT,
            hours        TEXT,
            access       TEXT,
            custodian_id TEXT,
            sentient     BOOLEAN DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS items (
            id              TEXT PRIMARY KEY,
            novel_id        TEXT NOT NULL REFERENCES novel(id),
            name            TEXT NOT NULL,
            description     TEXT,
            symbolic_weight TEXT,
            sentient        BOOLEAN DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS organizations (
            id        TEXT PRIMARY KEY,
            novel_id  TEXT NOT NULL REFERENCES novel(id),
            name      TEXT NOT NULL,
            type      TEXT,
            goals     TEXT,
            resources TEXT,
            access    TEXT
        );

        CREATE TABLE IF NOT EXISTS events (
            id                     TEXT PRIMARY KEY,
            novel_id               TEXT NOT NULL REFERENCES novel(id),
            title                  TEXT NOT NULL,
            description            TEXT,
            occurred_datetime      TEXT,
            status                 TEXT,
            chapter_id_occurred    TEXT,
            characters_involved    TEXT,
            organizations_involved TEXT,
            narrative_salience     INTEGER
        );

        -- Written by generate_chapter_list: the flat chapter list.
        CREATE TABLE IF NOT EXISTS chapter_list (
            id                       TEXT PRIMARY KEY,
            novel_id                 TEXT NOT NULL REFERENCES novel(id),
            chapter_number           INTEGER,
            title                    TEXT,
            word_count               INTEGER,
            purpose                  TEXT,
            intimate_arc_role        TEXT,
            characters_present_ids   TEXT,
            location_ids             TEXT,
            items_present_ids        TEXT,
            organizations_present_ids TEXT,
            events_present_ids       TEXT
        );

        -- Written by generate_chapters: one row per chapter_list row,
        -- filled in after the chapter list already exists.
        CREATE TABLE IF NOT EXISTS chapter_detail (
            chapter_id        TEXT PRIMARY KEY REFERENCES chapter_list(id),
            summary           TEXT,
            emotional_arc     TEXT,
            chapter_end_hook  TEXT,
            beats             TEXT
        );

        CREATE TABLE IF NOT EXISTS manuscripts (
            id             TEXT PRIMARY KEY,
            novel_id       TEXT NOT NULL REFERENCES novel(id),
            chapter_number INTEGER,
            title          TEXT,
            summary        TEXT,
            story_so_far   TEXT,
            prose          TEXT,
            word_count     INTEGER,
            created_at     TEXT
        );
    """)
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# novel
# ---------------------------------------------------------------------------

def insert_novel(prompt: str, target_word_count: int, novel: dict, meta: dict, authorial_voice: str, created_at: str) -> str:
    init_db()
    novel_id = str(uuid.uuid4())
    conn = get_connection()
    conn.execute(
        """INSERT INTO novel
           (id, created_at, prompt, target_word_count, title, summary, author, word_count,
            premise, protagonist_stubs, antagonist_stubs, primary_genre, sub_genres,
            tone, spice_level, literary_voice, tense, perspective, forbidden_element, authorial_voice)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            novel_id, created_at, prompt, target_word_count,
            novel.get("title", "Untitled"),
            novel.get("summary"),
            novel.get("author"),
            novel.get("word_count"),
            meta.get("premise"),
            json.dumps(meta.get("protagonist_stubs", [])),
            json.dumps(meta.get("antagonist_stubs", [])),
            meta.get("primary_genre"),
            json.dumps(meta.get("sub_genres", [])),
            meta.get("tone"),
            meta.get("spice_level"),
            meta.get("literary_voice"),
            meta.get("tense"),
            meta.get("perspective"),
            meta.get("forbidden_element"),
            authorial_voice,
        ),
    )
    conn.commit()
    conn.close()
    return novel_id


def get_novel(novel_id: str, cols: list[str]) -> dict:
    if not cols:
        raise ValueError("get_novel: cols must not be empty")
    conn = get_connection()
    row = conn.execute(f"SELECT {', '.join(cols)} FROM novel WHERE id = ?", (novel_id,)).fetchone()
    conn.close()
    if not row:
        raise ValueError(f"Novel {novel_id} not found in database.")
    return dict(zip(cols, row))


def delete_novel(novel_id: str):
    conn = get_connection()
    conn.execute("DELETE FROM novel WHERE id = ?", (novel_id,))
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# costs
# ---------------------------------------------------------------------------

def insert_cost(novel_id: str, stage: str, model: str, input_tokens: int, output_tokens: int, cost: float):
    from datetime import datetime, timezone
    conn = get_connection()
    conn.execute(
        "INSERT INTO costs (id, novel_id, stage, model, input_tokens, output_tokens, cost, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (str(uuid.uuid4()), novel_id, stage, model, input_tokens, output_tokens, cost, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()


def get_costs(novel_id: str) -> list[dict]:
    cols = ["stage", "model", "input_tokens", "output_tokens", "cost", "created_at"]
    conn = get_connection()
    rows = conn.execute(f"SELECT {', '.join(cols)} FROM costs WHERE novel_id = ? ORDER BY created_at", (novel_id,)).fetchall()
    conn.close()
    return [dict(zip(cols, row)) for row in rows]


# ---------------------------------------------------------------------------
# worldbuilding
# ---------------------------------------------------------------------------

def insert_worldbuilding(novel_id: str, world: dict):
    conn = get_connection()
    conn.execute(
        """INSERT INTO worldbuilding
           (id, novel_id, story_type, time_period, anchor_location, anchor_location_description,
            base_climate, constraints, social_hierarchy, cultural_norms, dominant_institutions,
            technology_level, languages, taboos, gender_dynamics, economic_conditions,
            historical_context, mobility, political_climate, religion, relationship_norms)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            str(uuid.uuid4()), novel_id,
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
    conn.commit()
    conn.close()


def get_worldbuilding(novel_id: str, cols: list[str]) -> dict:
    if not cols:
        raise ValueError("get_worldbuilding: cols must not be empty")
    conn = get_connection()
    row = conn.execute(f"SELECT {', '.join(cols)} FROM worldbuilding WHERE novel_id = ?", (novel_id,)).fetchone()
    conn.close()
    return dict(zip(cols, row)) if row else {}


def delete_worldbuilding(novel_id: str):
    conn = get_connection()
    conn.execute("DELETE FROM worldbuilding WHERE novel_id = ?", (novel_id,))
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# spine
# ---------------------------------------------------------------------------

def insert_spine(novel_id: str, spine: dict):
    conn = get_connection()
    conn.execute(
        "INSERT INTO spine (id, novel_id, word_count, narrative_structure) VALUES (?, ?, ?, ?)",
        (
            str(uuid.uuid4()), novel_id,
            spine.get("word_count"),
            json.dumps(spine.get("narrative_structure", [])),
        ),
    )
    conn.commit()
    conn.close()


def get_spine(novel_id: str, cols: list[str]) -> dict:
    if not cols:
        raise ValueError("get_spine: cols must not be empty")
    conn = get_connection()
    row = conn.execute(f"SELECT {', '.join(cols)} FROM spine WHERE novel_id = ?", (novel_id,)).fetchone()
    conn.close()
    if not row:
        raise RuntimeError(f"No spine found for novel {novel_id} — run generate_spine first.")
    return dict(zip(cols, row))


def delete_spine(novel_id: str):
    conn = get_connection()
    conn.execute("DELETE FROM spine WHERE novel_id = ?", (novel_id,))
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# characters
# ---------------------------------------------------------------------------

def insert_characters(novel_id: str, characters: list[dict]):
    conn = get_connection()
    for char in characters:
        conn.execute(
            """INSERT OR IGNORE INTO characters
               (id, novel_id, name, age, gender, sexuality, role, occupation,
                appearance, physical_characteristics, personality, arc, backstory,
                goals, fears, flaws, contradictions, hobbies, spiritual_beliefs,
                voice, speech_patterns, narrative_stakes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                char.get("id", str(uuid.uuid4())), novel_id,
                char.get("name", ""),
                char.get("age"),
                char.get("gender"),
                char.get("sexuality"),
                char.get("role"),
                char.get("occupation"),
                char.get("appearance"),
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
    conn.commit()
    conn.close()


def get_characters(novel_id: str, cols: list[str]) -> list[dict]:
    if not cols:
        raise ValueError("get_characters: cols must not be empty")
    conn = get_connection()
    rows = conn.execute(f"SELECT {', '.join(cols)} FROM characters WHERE novel_id = ?", (novel_id,)).fetchall()
    conn.close()
    if not rows:
        raise RuntimeError(f"No characters found for novel {novel_id} — run generate_characters first.")
    return [dict(zip(cols, row)) for row in rows]


def delete_characters(novel_id: str):
    conn = get_connection()
    conn.execute("DELETE FROM characters WHERE novel_id = ?", (novel_id,))
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# locations
# ---------------------------------------------------------------------------

def insert_locations(novel_id: str, locations: list[dict]):
    conn = get_connection()
    for loc in locations:
        conn.execute(
            "INSERT OR IGNORE INTO locations (id, novel_id, name, region, description, atmosphere, hours, access, custodian_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                loc.get("id", str(uuid.uuid4())), novel_id,
                loc.get("name", ""),
                loc.get("region"),
                loc.get("description"),
                loc.get("atmosphere"),
                loc.get("hours"),
                loc.get("access"),
                loc.get("custodian_id"),
            ),
        )
    conn.commit()
    conn.close()


def get_locations(novel_id: str, cols: list[str]) -> list[dict]:
    if not cols:
        raise ValueError("get_locations: cols must not be empty")
    conn = get_connection()
    rows = conn.execute(f"SELECT {', '.join(cols)} FROM locations WHERE novel_id = ?", (novel_id,)).fetchall()
    conn.close()
    return [dict(zip(cols, row)) for row in rows]


def delete_locations(novel_id: str):
    conn = get_connection()
    conn.execute("DELETE FROM locations WHERE novel_id = ?", (novel_id,))
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# items
# ---------------------------------------------------------------------------

def insert_items(novel_id: str, items: list[dict]):
    conn = get_connection()
    for item in items:
        conn.execute(
            "INSERT OR IGNORE INTO items (id, novel_id, name, description, symbolic_weight) VALUES (?, ?, ?, ?, ?)",
            (
                item.get("id", str(uuid.uuid4())), novel_id,
                item.get("name", ""),
                item.get("description"),
                item.get("significance"),
            ),
        )
    conn.commit()
    conn.close()


def get_items(novel_id: str, cols: list[str]) -> list[dict]:
    if not cols:
        raise ValueError("get_items: cols must not be empty")
    conn = get_connection()
    rows = conn.execute(f"SELECT {', '.join(cols)} FROM items WHERE novel_id = ?", (novel_id,)).fetchall()
    conn.close()
    return [dict(zip(cols, row)) for row in rows]


def delete_items(novel_id: str):
    conn = get_connection()
    conn.execute("DELETE FROM items WHERE novel_id = ?", (novel_id,))
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# organizations
# ---------------------------------------------------------------------------

def insert_organizations(novel_id: str, organizations: list[dict]):
    conn = get_connection()
    for org in organizations:
        conn.execute(
            "INSERT OR IGNORE INTO organizations (id, novel_id, name, type, goals, resources, access) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                org.get("id", str(uuid.uuid4())), novel_id,
                org.get("name", ""),
                org.get("type"),
                org.get("goals"),
                org.get("resources"),
                org.get("access"),
            ),
        )
    conn.commit()
    conn.close()


def get_organizations(novel_id: str, cols: list[str]) -> list[dict]:
    if not cols:
        raise ValueError("get_organizations: cols must not be empty")
    conn = get_connection()
    rows = conn.execute(f"SELECT {', '.join(cols)} FROM organizations WHERE novel_id = ?", (novel_id,)).fetchall()
    conn.close()
    return [dict(zip(cols, row)) for row in rows]


def delete_organizations(novel_id: str):
    conn = get_connection()
    conn.execute("DELETE FROM organizations WHERE novel_id = ?", (novel_id,))
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# events
# ---------------------------------------------------------------------------

def insert_events(novel_id: str, events: list[dict]):
    conn = get_connection()
    for evt in events:
        conn.execute(
            """INSERT OR IGNORE INTO events
               (id, novel_id, title, description, occurred_datetime, status,
                characters_involved, organizations_involved, narrative_salience)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                evt.get("id", str(uuid.uuid4())), novel_id,
                evt.get("title", ""),
                evt.get("description"),
                evt.get("occurred_datetime"),
                evt.get("status"),
                json.dumps(evt.get("characters_involved", [])),
                json.dumps(evt.get("organizations_involved", [])),
                evt.get("narrative_salience"),
            ),
        )
    conn.commit()
    conn.close()


def get_events(novel_id: str, cols: list[str]) -> list[dict]:
    if not cols:
        raise ValueError("get_events: cols must not be empty")
    conn = get_connection()
    rows = conn.execute(f"SELECT {', '.join(cols)} FROM events WHERE novel_id = ?", (novel_id,)).fetchall()
    conn.close()
    return [dict(zip(cols, row)) for row in rows]


def delete_events(novel_id: str):
    conn = get_connection()
    conn.execute("DELETE FROM events WHERE novel_id = ?", (novel_id,))
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# chapters
# ---------------------------------------------------------------------------

def insert_chapter(novel_id: str, chapter: dict) -> str:
    chapter_id = chapter.get("id", str(uuid.uuid4()))
    conn = get_connection()
    conn.execute(
        """INSERT INTO chapter_list
           (id, novel_id, chapter_number, title, word_count, purpose, intimate_arc_role,
            characters_present_ids, location_ids, items_present_ids, organizations_present_ids, events_present_ids)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            chapter_id, novel_id,
            chapter.get("chapter_number"),
            chapter.get("title"),
            chapter.get("word_count"),
            chapter.get("purpose"),
            chapter.get("intimate_arc_role"),
            json.dumps(chapter.get("characters_present_ids", [])),
            json.dumps(chapter.get("location_ids", [])),
            json.dumps(chapter.get("items_present_ids", [])),
            json.dumps(chapter.get("organizations_present_ids", [])),
            json.dumps(chapter.get("events_present_ids", [])),
        ),
    )
    # chapter_id is a FK on chapter_detail, so the row must exist before update_chapter_summary runs.
    conn.execute("INSERT INTO chapter_detail (chapter_id) VALUES (?)", (chapter_id,))
    conn.commit()
    conn.close()
    return chapter_id


def update_chapter_summary(chapter_id: str, summary: str, emotional_arc: str, intimate_arc_role: str, chapter_end_hook: str, beats: list = None):
    conn = get_connection()
    conn.execute(
        "UPDATE chapter_detail SET summary = ?, emotional_arc = ?, chapter_end_hook = ?, beats = ? WHERE chapter_id = ?",
        (summary, emotional_arc, chapter_end_hook, json.dumps(beats or []), chapter_id),
    )
    conn.execute("UPDATE chapter_list SET intimate_arc_role = ? WHERE id = ?", (intimate_arc_role, chapter_id))
    conn.commit()
    conn.close()


def get_chapters(novel_id: str, cols: list[str]) -> list[dict]:
    if not cols:
        raise ValueError("get_chapters: cols must not be empty")
    conn = get_connection()
    rows = conn.execute(
        f"""SELECT {', '.join(cols)} FROM chapter_list s
            JOIN chapter_detail d ON d.chapter_id = s.id
            WHERE s.novel_id = ? ORDER BY s.chapter_number""",
        (novel_id,),
    ).fetchall()
    conn.close()
    return [dict(zip(cols, row)) for row in rows]


def delete_chapters(novel_id: str):
    conn = get_connection()
    conn.execute("DELETE FROM chapter_detail WHERE chapter_id IN (SELECT id FROM chapter_list WHERE novel_id = ?)", (novel_id,))
    conn.execute("DELETE FROM chapter_list WHERE novel_id = ?", (novel_id,))
    conn.commit()
    conn.close()



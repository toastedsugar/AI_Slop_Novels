import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "db", "slopnovels.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.executescript("""
        CREATE TABLE IF NOT EXISTS novel (
            id          TEXT PRIMARY KEY,
            title       TEXT NOT NULL,
            author      TEXT,
            word_count  INTEGER,
            created_at  TEXT
        );

        CREATE TABLE IF NOT EXISTS metadata (
            id              TEXT PRIMARY KEY,
            novel_id        TEXT NOT NULL REFERENCES novel(id),
            premise         TEXT,
            primary_genre   TEXT,
            sub_genres      TEXT,
            tone            TEXT,
            spice_level     TEXT,
            literary_voice  TEXT,
            tense               TEXT,
            perspective         TEXT,
            forbidden_element   TEXT
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

        CREATE TABLE IF NOT EXISTS characters (
            id                      TEXT PRIMARY KEY,
            novel_id                TEXT NOT NULL REFERENCES novel(id),
            name                    TEXT NOT NULL,
            age                     INTEGER,
            gender                  TEXT,
            sexuality               TEXT,
            role                    TEXT,
            occupation              TEXT,
            appearance              TEXT,
            physical_characteristics TEXT,
            personality             TEXT,
            arc                     TEXT,
            backstory               TEXT,
            goals                   TEXT,
            fears                   TEXT,
            flaws                   TEXT,
            contradictions          TEXT,
            hobbies                 TEXT,
            spiritual_beliefs       TEXT,
            voice                   TEXT,
            speech_patterns         TEXT,
            narrative_stakes        TEXT
        );

        CREATE TABLE IF NOT EXISTS locations (
            id              TEXT PRIMARY KEY,
            novel_id        TEXT NOT NULL REFERENCES novel(id),
            name            TEXT NOT NULL,
            region          TEXT,
            description     TEXT,
            atmosphere      TEXT,
            hours           TEXT,
            access          TEXT,
            custodian_id    TEXT,
            sentient        BOOLEAN DEFAULT 0,
            character_id    TEXT
        );

        CREATE TABLE IF NOT EXISTS items (
            id              TEXT PRIMARY KEY,
            novel_id        TEXT NOT NULL REFERENCES novel(id),
            name            TEXT NOT NULL,
            description     TEXT,
            symbolic_weight TEXT,
            initial_holder  TEXT,
            initial_location TEXT,
            sentient        BOOLEAN DEFAULT 0,
            character_id    TEXT
        );

        CREATE TABLE IF NOT EXISTS organizations (
            id          TEXT PRIMARY KEY,
            novel_id    TEXT NOT NULL REFERENCES novel(id),
            name        TEXT NOT NULL,
            type        TEXT,
            goals       TEXT,
            resources   TEXT,
            access      TEXT
        );

        CREATE TABLE IF NOT EXISTS events (
            id                      TEXT PRIMARY KEY,
            novel_id                TEXT NOT NULL REFERENCES novel(id),
            title                   TEXT NOT NULL,
            description             TEXT,
            scheduled_datetime      TEXT,
            occurred_datetime       TEXT,
            status                  TEXT,
            chapter_id_scheduled    TEXT,
            chapter_id_occurred     TEXT,
            characters_involved     TEXT,
            organizations_involved  TEXT,
            narrative_salience      INTEGER
        );

        CREATE TABLE IF NOT EXISTS chapter (
            id                TEXT PRIMARY KEY,
            novel_id          TEXT NOT NULL REFERENCES novel(id),
            chapter_number    INTEGER,
            title             TEXT,
            word_count        INTEGER,
            summary           TEXT,
            emotional_arc     TEXT,
            intimate_arc_role TEXT,
            chapter_end_hook  TEXT
        );

        CREATE TABLE IF NOT EXISTS beats (
            id                     TEXT PRIMARY KEY,
            chapter_id             TEXT NOT NULL REFERENCES chapter(id),
            beat_number            INTEGER,
            description            TEXT,
            pov                    TEXT,
            word_count             INTEGER,
            location_id            TEXT,
            characters_present_ids TEXT,
            items_present_ids      TEXT,
            tension_level          TEXT,
            heat_level             TEXT,
            key_events             TEXT
        );

        CREATE TABLE IF NOT EXISTS manuscripts (
            id          TEXT PRIMARY KEY,
            novel_id    TEXT NOT NULL REFERENCES novel(id),
            chapters    TEXT,
            created_at  TEXT
        );
    """)

    conn.commit()
    conn.close()

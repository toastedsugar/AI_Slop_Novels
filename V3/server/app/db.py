import sqlite3
from pathlib import Path

DB_DIR = Path(__file__).resolve().parent.parent / "db"
DB_PATH = DB_DIR / "slopnovels.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# Create the db directory, file, and tables if they don't already exist.
def init_db() -> None:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS novels (
                id TEXT PRIMARY KEY,
                prompt TEXT NOT NULL,
                title TEXT NOT NULL,
                summary TEXT,
                author TEXT,
                word_count INTEGER,
                premise TEXT NOT NULL,
                primary_genre TEXT,
                sub_genres TEXT,
                tone TEXT,
                spice_level TEXT,
                literary_voice TEXT,
                tense TEXT,
                perspective TEXT,
                forbidden_element TEXT,
                themes TEXT,
                story_type TEXT,
                time_period TEXT,
                anchor_location TEXT,
                anchor_location_description TEXT,
                constraints TEXT,
                tone_notes TEXT,
                characters_notes TEXT,
                primary_thread TEXT,
                romance_content TEXT,
                primary_word_count INTEGER,
                metadata_model TEXT,
                characters_model TEXT,
                worldbuilding_model TEXT,
                primary_thread_model TEXT,
                secondary_arcs_model TEXT,
                outline_model TEXT,
                entities_model TEXT,
                initial_state_model TEXT,
                metadata_reasoning INTEGER,
                characters_reasoning INTEGER,
                worldbuilding_reasoning INTEGER,
                primary_thread_reasoning INTEGER,
                secondary_arcs_reasoning INTEGER,
                outline_reasoning INTEGER,
                entities_reasoning INTEGER,
                initial_state_reasoning INTEGER
            )
            """
        )
        # Migrate existing dbs created before these columns were added.
        columns = {row[1] for row in conn.execute("PRAGMA table_info(novels)")}
        if "themes" not in columns:
            conn.execute("ALTER TABLE novels ADD COLUMN themes TEXT")
        for column in (
            "story_type",
            "time_period",
            "anchor_location",
            "anchor_location_description",
            "constraints",
            "tone_notes",
            "characters_notes",
            "primary_thread",
            "romance_content",
        ):
            if column not in columns:
                conn.execute(f"ALTER TABLE novels ADD COLUMN {column} TEXT")
        if "primary_word_count" not in columns:
            conn.execute("ALTER TABLE novels ADD COLUMN primary_word_count INTEGER")
        for column in (
            "metadata_model",
            "characters_model",
            "worldbuilding_model",
            "primary_thread_model",
            "secondary_arcs_model",
            "outline_model",
            "entities_model",
            "initial_state_model",
        ):
            if column not in columns:
                conn.execute(f"ALTER TABLE novels ADD COLUMN {column} TEXT")
        for column in (
            "metadata_reasoning",
            "characters_reasoning",
            "worldbuilding_reasoning",
            "primary_thread_reasoning",
            "secondary_arcs_reasoning",
            "outline_reasoning",
            "entities_reasoning",
            "initial_state_reasoning",
        ):
            if column not in columns:
                conn.execute(f"ALTER TABLE novels ADD COLUMN {column} INTEGER")

        # Subplot seeds attached to a novel at creation time. Up to 3 per
        # novel (enforced client-side). length is the percentage of that
        # storyline actually resolved in this story — the rest is left open
        # for a later story in the series. priority is how much narrative
        # weight the thread gets; heat is romantic/sexual intensity specific
        # to that thread, independent of the novel's overall spice_level.
        # word_count is decided by init_secondary_arcs (2000-4000, based on
        # how much plot that thread's length actually allows) and is null
        # until that step runs.
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS secondary_threads (
                id TEXT PRIMARY KEY,
                novel_id TEXT NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
                description TEXT NOT NULL,
                length INTEGER NOT NULL,
                priority INTEGER NOT NULL,
                heat INTEGER NOT NULL,
                word_count INTEGER
            )
            """
        )
        thread_columns = {row[1] for row in conn.execute("PRAGMA table_info(secondary_threads)")}
        if "word_count" not in thread_columns:
            conn.execute("ALTER TABLE secondary_threads ADD COLUMN word_count INTEGER")

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS characters (
                id TEXT PRIMARY KEY,
                novel_id TEXT NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
                name TEXT NOT NULL,
                role TEXT,
                age INTEGER,
                gender TEXT,
                sexuality TEXT,
                occupation TEXT,
                appearance TEXT,
                physical_characteristics TEXT,
                personality TEXT,
                backstory TEXT,
                fears TEXT,
                flaws TEXT,
                contradictions TEXT,
                hobbies TEXT,
                spiritual_beliefs TEXT,
                character_voice TEXT,
                speech_patterns TEXT
            )
            """
        )
        # Migrate existing dbs created before these columns were added.
        character_columns = {row[1] for row in conn.execute("PRAGMA table_info(characters)")}
        for column in (
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
        ):
            if column not in character_columns:
                col_type = "INTEGER" if column == "age" else "TEXT"
                conn.execute(f"ALTER TABLE characters ADD COLUMN {column} {col_type}")

        # Internal generation input — the protagonist's full hero's-journey
        # arc from init_primary_thread, one row per plot point, in order.
        # sort_order preserves the 9-step sequence since sqlite doesn't
        # guarantee row order without it. Not exposed via the API; init_outline
        # reads this to write the actual user-facing outline (see below).
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS spine_beats (
                id TEXT PRIMARY KEY,
                novel_id TEXT NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
                sort_order INTEGER NOT NULL,
                heros_journey_step TEXT NOT NULL,
                summary TEXT NOT NULL,
                word_count_pct INTEGER,
                time_gap_before TEXT,
                forbidden_element_active INTEGER,
                intimate_arc_role TEXT,
                intimate_entry_mode TEXT
            )
            """
        )
        # Migrate existing dbs created before this column was added.
        spine_columns = {row[1] for row in conn.execute("PRAGMA table_info(spine_beats)")}
        if "intimate_entry_mode" not in spine_columns:
            conn.execute("ALTER TABLE spine_beats ADD COLUMN intimate_entry_mode TEXT")

        # Internal generation input — one row per plot point of a
        # secondary_thread's arc from init_secondary_arcs, in order. Not
        # exposed via the API; init_outline reads this to write the actual
        # user-facing outline (see below).
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS secondary_arc_plot_points (
                id TEXT PRIMARY KEY,
                novel_id TEXT NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
                secondary_thread_id TEXT NOT NULL REFERENCES secondary_threads(id) ON DELETE CASCADE,
                sort_order INTEGER NOT NULL,
                summary TEXT NOT NULL,
                characters_involved TEXT
            )
            """
        )

        # The final, user-facing outline — one row per beat, in order.
        # Written by init_outline, which weaves the primary thread and
        # secondary arcs into a single detailed prose sequence. This is the
        # only spine-like artifact exposed via the API/UI; spine_beats and
        # secondary_arc_plot_points above are internal inputs to it.
        # word_count is an absolute estimate (not a percentage) of how many
        # words this beat will run to once actually drafted into prose —
        # beats vary freely in length (a brief brooding moment vs. a long
        # scene), so there's no fixed total for these to sum to.
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS outline_beats (
                id TEXT PRIMARY KEY,
                novel_id TEXT NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
                sort_order INTEGER NOT NULL,
                content TEXT NOT NULL,
                word_count INTEGER
            )
            """
        )
        # Migrate existing dbs: the column used to hold a 0-100 percentage
        # (word_count_pct) that all beats summed to 100 — now it holds an
        # absolute word count estimate per beat, so the old values are
        # meaningless and are not converted, just renamed away from.
        outline_beat_columns = {row[1] for row in conn.execute("PRAGMA table_info(outline_beats)")}
        if "word_count_pct" in outline_beat_columns and "word_count" not in outline_beat_columns:
            conn.execute("ALTER TABLE outline_beats RENAME COLUMN word_count_pct TO word_count")

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS locations (
                id TEXT PRIMARY KEY,
                novel_id TEXT NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
                name TEXT NOT NULL,
                description TEXT
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS items (
                id TEXT PRIMARY KEY,
                novel_id TEXT NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
                name TEXT NOT NULL,
                description TEXT
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS organizations (
                id TEXT PRIMARY KEY,
                novel_id TEXT NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
                name TEXT NOT NULL,
                description TEXT
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY,
                novel_id TEXT NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
                title TEXT NOT NULL,
                description TEXT,
                characters_involved TEXT,
                organizations_involved TEXT
            )
            """
        )

        # Character-outward only: Cal->Thistle and Thistle->Cal are separate
        # rows since the relationship can be asymmetric. A row's absence means
        # the relationship doesn't exist yet (e.g. they haven't met) — do not
        # use a null status to represent that, just omit the row.
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS character_relationships (
                id TEXT PRIMARY KEY,
                novel_id TEXT NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
                character_id TEXT NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
                target_character_id TEXT NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
                relationship_type TEXT,
                status TEXT,
                emotional_intensity INTEGER,
                open_threads TEXT
            )
            """
        )

        # Character's relationship to an item or location — no real FK on
        # entity_id since it can point into either items or locations
        # depending on entity_type.
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS entity_relationships (
                id TEXT PRIMARY KEY,
                novel_id TEXT NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
                character_id TEXT NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
                entity_type TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                relationship_type TEXT,
                status TEXT,
                open_threads TEXT
            )
            """
        )
        conn.commit()
    finally:
        conn.close()

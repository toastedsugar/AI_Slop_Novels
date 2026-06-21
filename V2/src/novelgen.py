import json
import random
import re
import uuid
from datetime import datetime, timezone
from json_repair import repair_json
from utils.model_routing import load_routing, generate_from_config, calculate_cost
from utils.schema_static import schema_to_json
from utils.db_helpers import (
    get_connection,
    insert_novel, get_novel,
    insert_cost,
    insert_worldbuilding, get_worldbuilding, delete_worldbuilding,
    insert_spine, get_spine, delete_spine,
    insert_characters, get_characters, delete_characters,
    insert_locations, get_locations, delete_locations,
    insert_items, get_items, delete_items,
    insert_organizations, get_organizations, delete_organizations,
    insert_events, get_events, delete_events,
    insert_chapter, update_chapter_summary, get_chapters, delete_chapters,
)
from prompts.outline import (
    GEN_OUTLINE_SYSTEM_PROMPT,
    GEN_NOVEL_USER_PROMPT,
    GEN_SPINE_USER_PROMPT,
    GEN_CHARACTERS_USER_PROMPT,
    GEN_CHAPTER_LIST_USER_PROMPT,
    GEN_CHAPTER_USER_PROMPT,
)
from prompts.generation_chapter_by_chapter import GEN_CHAPTER_BY_CHAPTER_SYSTEM_PROMPT, GEN_CHAPTER_USER_PROMPT as GEN_PROSE_USER_PROMPT


# Cascade delete order — each stage wipes itself and everything downstream (upstream → downstream).
_CASCADE = ["worldbuilding", "spine", "characters", "chapters"]

_DELETE = {
    "worldbuilding": delete_worldbuilding,
    "spine":         delete_spine,
    "characters":    lambda novel_id: [f(novel_id) for f in (delete_characters, delete_locations, delete_items, delete_organizations, delete_events)],
    "chapters":      delete_chapters,
}


class NovelGen:
    def __init__(self):
        self.routing = load_routing()

    def _seed(self, prompt):
        # Prepending a random seed changes the model's probability landscape slightly, adding output variety.
        return f"[Narrative seed: {random.randint(100000, 999999)}]\n\n{prompt}"

    def _parse_json(self, s):
        if not s:
            raise ValueError("_parse_json received empty/None response")
        match = re.search(r"\{.*\}", s, flags=re.DOTALL)
        if not match:
            raise ValueError(f"No JSON found in response: {s[:200]}")
        return json.loads(repair_json(match.group()))

    # Normalizes a value to a list — wraps a single dict in a list, wraps a bare string in a list, passes a list through, returns [] otherwise.
    # Because insert functions iterate over characters, locations, etc. and expect a list of dicts. If the model returns a single dict instead of a list, the for loop iterates over the dict's keys (which are strings), and then char.get(...) fails because strings don't have .get().
    # Also handles bare strings for cross-reference fields like location_id, where the model may return a single UUID string instead of a list.
    def _ensure_list(self, val):
        if isinstance(val, list):
            return val
        if isinstance(val, dict):
            return [val]
        if isinstance(val, str) and val:
            return [val]
        return []

    def _cascade_delete(self, novel_id: str, from_stage: str):
        start = _CASCADE.index(from_stage)
        for stage in _CASCADE[start:]:
            _DELETE[stage](novel_id)

    # ---------------------------------------------------------------------------
    # generate_novel
    # Generates novel metadata + worldbuilding, inserts everything, returns novel_id.
    # ---------------------------------------------------------------------------

    def generate_novel(self, prompt: str, wordcount: int, authorial_voice: str = "") -> str:
        config = self.routing["novel"]
        print(f"Generating novel using {config['provider']} / {config['model']}")
        text, input_tokens, output_tokens = generate_from_config(
            config,
            GEN_OUTLINE_SYSTEM_PROMPT.format(intro_prompt=prompt),
            self._seed(GEN_NOVEL_USER_PROMPT.format(
                word_count=wordcount,
                schema=schema_to_json("novel", "worldbuilding"),
            )),
        )
        print(text)
        data = self._parse_json(text)
        novel_id = insert_novel(
            prompt=prompt,
            target_word_count=wordcount,
            novel=data.get("novel", {}),
            meta=data.get("novel", {}),
            authorial_voice=authorial_voice,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        insert_worldbuilding(novel_id, data.get("worldbuilding", {}))
        insert_cost(novel_id, "metadata", config["model"], input_tokens, output_tokens, calculate_cost(config, input_tokens, output_tokens))
        return novel_id

    # ---------------------------------------------------------------------------
    # generate_spine
    # ---------------------------------------------------------------------------

    def generate_spine(self, novel_id: str, regenerate: bool = False):
        if not regenerate:
            if get_spine(novel_id, ["word_count"]):
                print("--- Spine already exists ---")
                return

        if regenerate:
            self._cascade_delete(novel_id, "spine")

        novel = get_novel(novel_id, ["prompt", "title", "summary", "word_count", "target_word_count", "premise", "primary_genre", "tone", "spice_level", "literary_voice", "tense", "perspective", "forbidden_element", "authorial_voice", "protagonist_stubs", "antagonist_stubs"])
        world = get_worldbuilding(novel_id, ["story_type", "time_period", "anchor_location", "social_hierarchy", "constraints"])

        config = self.routing["spine"]
        print(f"Generating spine using {config['provider']} / {config['model']}")
        text, input_tokens, output_tokens = generate_from_config(
            config,
            GEN_OUTLINE_SYSTEM_PROMPT.format(intro_prompt=novel.get("prompt", novel.get("summary", ""))),
            self._seed(GEN_SPINE_USER_PROMPT.format(
                metadata=json.dumps({**novel, **world}, indent=2),
                word_count=novel.get("target_word_count", 0),
                schema=schema_to_json("spine"),
            )),
        )
        print(text)
        data = self._parse_json(text)
        insert_spine(novel_id, data.get("spine", data))
        insert_cost(novel_id, "spine", config["model"], input_tokens, output_tokens, calculate_cost(config, input_tokens, output_tokens))

    # ---------------------------------------------------------------------------
    # generate_characters
    # Generates characters, locations, items, organizations, and events in one call.
    # ---------------------------------------------------------------------------

    def generate_characters(self, novel_id: str, regenerate: bool = False):
        if not regenerate:
            if get_characters(novel_id, ["id"]):
                return

        if regenerate:
            self._cascade_delete(novel_id, "characters")

        novel = get_novel(novel_id, ["prompt", "title", "summary", "word_count", "premise", "primary_genre", "tone", "spice_level", "literary_voice", "tense", "perspective", "forbidden_element"])
        world = get_worldbuilding(novel_id, ["story_type", "time_period", "anchor_location", "social_hierarchy", "constraints"])
        spine = get_spine(novel_id, ["word_count", "narrative_structure"])

        config = self.routing["characters"]
        print(f"Generating characters using {config['provider']} / {config['model']}")
        text, input_tokens, output_tokens = generate_from_config(
            config,
            GEN_OUTLINE_SYSTEM_PROMPT.format(intro_prompt=novel.get("prompt", novel.get("summary", ""))),
            self._seed(GEN_CHARACTERS_USER_PROMPT.format(
                metadata=json.dumps({**novel, **world}, indent=2),
                spine=spine.get("narrative_structure", ""),
                schema=schema_to_json("characters", "locations", "items", "organizations", "events"),
            )),
        )
        print(text)
        data = self._parse_json(text)

        insert_characters(novel_id, self._ensure_list(data.get("characters", [])))
        insert_locations(novel_id, self._ensure_list(data.get("locations", [])))
        insert_items(novel_id, self._ensure_list(data.get("items", [])))
        insert_organizations(novel_id, self._ensure_list(data.get("organizations", [])))
        insert_events(novel_id, self._ensure_list(data.get("events", [])))
        insert_cost(novel_id, "characters", config["model"], input_tokens, output_tokens, calculate_cost(config, input_tokens, output_tokens))

    # ---------------------------------------------------------------------------
    # generate_chapter_list
    # Spine → flat chapter list: title, word_count, purpose, intimate_arc_role.
    # One call. No summaries yet.
    # ---------------------------------------------------------------------------

    def generate_chapter_list(self, novel_id: str, regenerate: bool = False):
        if not regenerate:
            if get_chapters(novel_id, ["id"]):
                print("--- Chapter list already exists ---")
                return

        if regenerate:
            self._cascade_delete(novel_id, "chapters")

        novel = get_novel(novel_id, ["prompt", "title", "summary", "word_count", "target_word_count", "premise", "primary_genre", "tone", "spice_level", "tense", "perspective", "forbidden_element"])
        spine = get_spine(novel_id, ["word_count", "narrative_structure"])
        characters = get_characters(novel_id, ["id", "name", "role", "arc"])
        locations = get_locations(novel_id, ["id", "name", "description"])
        items = get_items(novel_id, ["id", "name", "description"])
        organizations = get_organizations(novel_id, ["id", "name", "type", "goals"])
        events = get_events(novel_id, ["id", "title", "description", "status", "narrative_salience"])

        config = self.routing["outline"]
        print(f"Generating chapter list using {config['provider']} / {config['model']}")
        text, input_tokens, output_tokens = generate_from_config(
            config,
            GEN_OUTLINE_SYSTEM_PROMPT.format(intro_prompt=novel.get("prompt", novel.get("summary", ""))),
            self._seed(GEN_CHAPTER_LIST_USER_PROMPT.format(
                metadata=json.dumps(novel, indent=2),
                spine=spine.get("narrative_structure", ""),
                word_count=novel.get("target_word_count", 0),
                characters=json.dumps(characters, indent=2),
                locations=json.dumps(locations, indent=2),
                items=json.dumps(items, indent=2),
                organizations=json.dumps(organizations, indent=2),
                events=json.dumps(events, indent=2),
                schema=schema_to_json("chapter_list"),
            )),
        )
        print(text)
        data = self._parse_json(text)
        chapters = self._ensure_list(data.get("chapter_list") or data.get("chapters", []))
        if not chapters:
            raise RuntimeError(f"generate_chapter_list: no chapters found in response. Top-level keys: {list(data.keys())}")
        for chapter in chapters:
            insert_chapter(novel_id, chapter)
        insert_cost(novel_id, "chapter_list", config["model"], input_tokens, output_tokens, calculate_cost(config, input_tokens, output_tokens))

    # ---------------------------------------------------------------------------
    # generate_chapters
    # Loops over chapter list, one LLM call per chapter to write the full
    # detailed summary. Passes all previous summaries for continuity.
    # ---------------------------------------------------------------------------

    def generate_chapters(self, novel_id: str, regenerate: bool = False):
        chapters = get_chapters(novel_id, ["id", "chapter_number", "title", "word_count", "purpose", "summary", "intimate_arc_role", "chapter_end_hook"])

        if not chapters:
            raise RuntimeError("generate_chapters: no chapter list found — run generate_chapter_list first")

        if regenerate:
            # Clear only the summary fields, keep the chapter list rows
            for chapter in chapters:
                update_chapter_summary(chapter["id"], None, None, chapter.get("intimate_arc_role"), chapter.get("chapter_end_hook"), [])

        novel = get_novel(novel_id, ["prompt", "title", "summary", "word_count", "premise", "primary_genre", "tone", "spice_level", "tense", "perspective", "forbidden_element"])
        spine = get_spine(novel_id, ["word_count", "narrative_structure"])
        characters = get_characters(novel_id, ["id", "name", "role", "arc", "appearance", "personality"])
        locations = get_locations(novel_id, ["id", "name", "description", "atmosphere"])
        items = get_items(novel_id, ["id", "name", "description"])

        config = self.routing["outline"]

        # Chapter list skeleton sent to every call for forward continuity
        chapter_list = [{"chapter_number": c["chapter_number"], "title": c["title"], "word_count": c["word_count"], "purpose": c["purpose"]} for c in chapters]

        previous_summaries = ""
        for chapter in chapters:
            if not regenerate and chapter.get("summary"):
                previous_summaries += f"\nChapter {chapter['chapter_number']} — {chapter['title']}:\n{chapter['summary']}\n"
                continue

            print(f"Generating chapter {chapter['chapter_number']} summary using {config['provider']} / {config['model']}")
            text, input_tokens, output_tokens = generate_from_config(
                config,
                GEN_OUTLINE_SYSTEM_PROMPT.format(intro_prompt=novel.get("prompt", novel.get("summary", ""))),
                self._seed(GEN_CHAPTER_USER_PROMPT.format(
                    metadata=json.dumps(novel, indent=2),
                    spine=spine.get("narrative_structure", ""),
                    characters=json.dumps({"characters": characters, "locations": locations, "items": items}, indent=2),
                    chapter_list=json.dumps(chapter_list, indent=2),
                    previous_summaries=previous_summaries if previous_summaries else "None — this is the first chapter.",
                    chapter=json.dumps({k: chapter[k] for k in ("chapter_number", "title", "word_count", "purpose", "intimate_arc_role", "chapter_end_hook")}, indent=2),
                    purpose=chapter.get("purpose", ""),
                    intimate_arc_role=chapter.get("intimate_arc_role", "none"),
                    chapter_end_hook=chapter.get("chapter_end_hook", ""),
                    schema=schema_to_json("chapters"),
                )),
            )
            print(text)
            data = self._parse_json(text)
            # Unwrap {"chapters": {...}} envelope if present
            detail = data.get("chapters", data)
            if isinstance(detail, list):
                detail = detail[0] if detail else {}
            if not detail.get("summary"):
                raise RuntimeError(f"generate_chapters: no summary in response for chapter {chapter['chapter_number']}. Top-level keys: {list(data.keys())}")
            update_chapter_summary(
                chapter["id"],
                detail.get("summary", ""),
                detail.get("emotional_arc", ""),
                detail.get("intimate_arc_role", chapter.get("intimate_arc_role")),
                detail.get("chapter_end_hook", chapter.get("chapter_end_hook")),
                self._ensure_list(detail.get("beats", [])),
            )
            previous_summaries += f"\nChapter {chapter['chapter_number']} — {chapter['title']}:\n{data.get('summary', '')}\n"
            insert_cost(novel_id, f"chapter_{chapter['chapter_number']}", config["model"], input_tokens, output_tokens, calculate_cost(config, input_tokens, output_tokens))

    # ---------------------------------------------------------------------------
    # generate_outline
    # Runs all outline stages in order. Safe to re-run — skips completed stages.
    # ---------------------------------------------------------------------------

    def generate_outline(self, prompt: str, wordcount: int, authorial_voice: str = "") -> str:
        novel_id = self.generate_novel(prompt, wordcount, authorial_voice)
        self.generate_spine(novel_id)
        self.generate_characters(novel_id)
        self.generate_chapter_list(novel_id)
        self.generate_chapters(novel_id)
        return novel_id

    # ---------------------------------------------------------------------------
    # generate_story
    # ---------------------------------------------------------------------------

    def generate_story(self, novel_id: str, limit: int = None):
        config = self.routing["prose"]
        print(f"Generating prose using {config['provider']} / {config['model']}")

        novel_meta = get_novel(novel_id, ["tense", "perspective", "authorial_voice"])
        tense = novel_meta.get("tense", "past")
        perspective = novel_meta.get("perspective", "third_person_limited")
        system_prompt = GEN_CHAPTER_BY_CHAPTER_SYSTEM_PROMPT.format(tense=tense, perspective=perspective)

        chapters = get_chapters(novel_id, ["id", "chapter_number", "title", "summary", "emotional_arc", "intimate_arc_role", "chapter_end_hook", "word_count", "beats", "characters_present_ids", "location_ids", "items_present_ids", "organizations_present_ids", "events_present_ids"])
        if limit:
            chapters = [c for c in chapters if c["chapter_number"] == limit]

        print(f"Found {len(chapters)} chapters")
        running_summary = ""
        story_so_far = ""

        for chapter in chapters:
            chapter_number = chapter["chapter_number"]
            print(f"--- Generating chapter {chapter_number} ---")

            characters    = self._get_chapter_characters(chapter)
            locations     = self._get_chapter_locations(chapter)
            items         = self._get_chapter_items(chapter)
            organizations = self._get_chapter_organizations(chapter)
            events        = self._get_chapter_events(chapter)

            beats = self._ensure_list(json.loads(chapter.get("beats") or "[]"))
            beats_block = ""
            for i, beat in enumerate(beats, start=1):
                beats_block += f"Beat {i} | Word count share: {beat.get('word_count_pct')}%\nKey event: {beat.get('key_event')}\n"
                states = beat.get("character_states_after", {})
                if states:
                    beats_block += "Character states entering next beat: " + "; ".join(f"{name}: {state}" for name, state in states.items()) + "\n"
                beats_block += "\n"

            optional_context = ""
            if organizations:
                optional_context += f"Organizations involved:\n{json.dumps(organizations, indent=2)}\n\n"
            if events:
                optional_context += f"Active events:\n{json.dumps(events, indent=2)}\n\n"

            user_prompt = GEN_PROSE_USER_PROMPT.format(
                running_summary=running_summary,
                chapter_number=chapter_number,
                total_chapters=len(chapters),
                chapter_title=chapter["title"],
                chapter_summary=chapter["summary"],
                emotional_arc=chapter["emotional_arc"],
                chapter_word_count=chapter["word_count"],
                chapter_end_hook=chapter.get("chapter_end_hook", ""),
                beats=beats_block,
                characters=json.dumps(characters, indent=2),
                locations=json.dumps(locations, indent=2),
                items=json.dumps(items, indent=2),
                optional_context=optional_context,
                tense=tense,
                perspective=perspective,
            )

            try:
                raw, input_tokens, output_tokens = generate_from_config(config, system_prompt, self._seed(user_prompt))
            except Exception as e:
                print(f"  ERROR: API call failed for chapter {chapter_number}: {e}")
                raise

            cost = calculate_cost(config, input_tokens, output_tokens)

            try:
                result = self._parse_json(raw)
            except Exception as e:
                print(f"  ERROR: JSON parse failed for chapter {chapter_number}: {e}")
                print(f"  Raw response (first 500 chars): {raw[:500] if raw else 'None'}")
                raise

            prose = result.get("prose", "")
            chapter_summary = result.get("summary", "")
            print(f"  Generated {result.get('word_count', '?')} words for chapter {chapter_number}")

            running_summary += f"\n\nChapter {chapter_number} — {chapter['title']}:\n{chapter_summary}"
            story_so_far += f"\n\n{'='*60}\nCHAPTER {chapter_number}: {chapter['title']}\n{'='*60}\n\n{prose}"

            insert_cost(novel_id, f"prose_ch{chapter_number}", config["model"], input_tokens, output_tokens, cost)
            self._insert_chapter_manuscript(novel_id, chapter, prose, chapter_summary, story_so_far)
            print(f"  Chapter {chapter_number} saved to manuscripts.")
            print(f"\n{'='*60}\nCHAPTER {chapter_number}: {chapter['title']}\n{'='*60}")
            print(prose)

    # ---------------------------------------------------------------------------
    # DB fetch helpers for prose generation
    # ---------------------------------------------------------------------------

    def _get_chapter_characters(self, chapter: dict) -> list:
        ids = json.loads(chapter.get("characters_present_ids") or "[]")
        if not ids:
            return []
        conn = get_connection()
        cols = ["id", "name", "age", "gender", "role", "appearance", "personality", "arc", "backstory", "voice", "speech_patterns"]
        characters = [
            dict(zip(cols, row))
            for cid in ids
            for row in conn.execute(
                f"SELECT {', '.join(cols)} FROM characters WHERE id = ?", (cid,)
            ).fetchall()
        ]
        conn.close()
        return characters

    def _get_chapter_locations(self, chapter: dict) -> list:
        ids = json.loads(chapter.get("location_ids") or "[]")
        if not ids:
            return []
        conn = get_connection()
        cols = ["id", "name", "region", "description", "atmosphere"]
        locations = [
            dict(zip(cols, row))
            for lid in ids
            for row in conn.execute(
                f"SELECT {', '.join(cols)} FROM locations WHERE id = ?", (lid,)
            ).fetchall()
        ]
        conn.close()
        return locations

    def _get_chapter_items(self, chapter: dict) -> list:
        ids = json.loads(chapter.get("items_present_ids") or "[]")
        if not ids:
            return []
        conn = get_connection()
        cols = ["id", "name", "description", "symbolic_weight"]
        items = [
            dict(zip(cols, row))
            for iid in ids
            for row in conn.execute(
                f"SELECT {', '.join(cols)} FROM items WHERE id = ?", (iid,)
            ).fetchall()
        ]
        conn.close()
        return items

    def _get_chapter_organizations(self, chapter: dict) -> list:
        ids = json.loads(chapter.get("organizations_present_ids") or "[]")
        if not ids:
            return []
        conn = get_connection()
        cols = ["id", "name", "type", "goals", "resources", "access"]
        orgs = [
            dict(zip(cols, row))
            for oid in ids
            for row in conn.execute(
                f"SELECT {', '.join(cols)} FROM organizations WHERE id = ?", (oid,)
            ).fetchall()
        ]
        conn.close()
        return orgs

    def _get_chapter_events(self, chapter: dict) -> list:
        ids = json.loads(chapter.get("events_present_ids") or "[]")
        if not ids:
            return []
        conn = get_connection()
        cols = ["id", "title", "description", "status", "narrative_salience"]
        events = [
            dict(zip(cols, row))
            for eid in ids
            for row in conn.execute(
                f"SELECT {', '.join(cols)} FROM events WHERE id = ?", (eid,)
            ).fetchall()
        ]
        conn.close()
        return events

    def _insert_chapter_manuscript(self, novel_id: str, chapter: dict, prose: str, summary: str, story_so_far: str):
        conn = get_connection()
        conn.execute(
            """INSERT INTO manuscripts
               (id, novel_id, chapter_number, title, summary, story_so_far, prose, word_count, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                str(uuid.uuid4()), novel_id,
                chapter["chapter_number"],
                chapter["title"],
                summary,
                story_so_far,
                prose,
                len(prose.split()),
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        conn.commit()
        conn.close()

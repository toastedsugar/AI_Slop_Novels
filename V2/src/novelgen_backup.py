import json
import os
import random
import re
import uuid
from datetime import datetime, timezone
from json_repair import repair_json
from utils.model_routing import load_routing, generate_from_config, calculate_cost
from prompts.outline import GEN_OUTLINE_SYSTEM_PROMPT, GEN_METADATA_USER_PROMPT, GEN_SPINE_USER_PROMPT, GEN_CHARACTERS_USER_PROMPT, GEN_FINAL_OUTLINE_USER_PROMPT, GEN_BEATS_USER_PROMPT
from prompts.generation_beat_by_beat import GEN_BEAT_BY_BEAT_SYSTEM_PROMPT, GEN_BEAT_USER_PROMPT
from prompts.generation_chapter_by_chapter import GEN_CHAPTER_BY_CHAPTER_SYSTEM_PROMPT, GEN_CHAPTER_USER_PROMPT

from utils.db_insert_outline import insert_outline
from utils.db_init import get_connection, init_db
from utils.schema_static import schema_to_json



class NovelGen:
    def __init__(self, intro_prompt: str, wordcount: int = 3000, authorial_voice: str = ""):
        
        print("NovelGen Online")
        self.routing = load_routing()
        print(f"Routing env: {os.environ.get('ENV', 'test')}")

        # The intro prompt is the north star for the story. It's the user's explicityly directed purpose.
        self.intro_prompt = intro_prompt
        self.wordcount = wordcount
        self.authorial_voice = authorial_voice

    # Adding a seed to begining of every user prompt
    # This will add randomness to the output by changing the way the model's probablility calculations
    def _seed(self, prompt):
        return f"[Narrative seed: {random.randint(100000, 999999)}]\n\n{prompt}"

    def _parse_json(self, s):
        if not s:
            raise ValueError(f"_parse_json received empty/None response")
        match = re.search(r"\{.*\}", s, flags=re.DOTALL)
        if not match:
            raise ValueError(f"No JSON found in response: {s[:200]}")
        return json.loads(repair_json(match.group()))

    # Normalizes a value to a list — wraps a single dict in a list, wraps a bare string in a list, passes a list through, returns [] otherwise.
    # Because db_insert_outline.py iterates over characters, locations, items, and chapters and expects a list of dicts. If the model returns a single dict instead of a list, the for loop iterates over the dict's keys (which are strings), and then char.get(...) fails because strings don't have .get().
    # Also handles bare strings for cross-reference fields like location_id, where the model may return a single UUID string instead of a list.
    def _ensure_list(self, val):
        if isinstance(val, list):
            return val
        if isinstance(val, dict):
            return [val]
        if isinstance(val, str) and val:
            return [val]
        return []

    def generate_metadata(self):
        config = self.routing["metadata"]
        print(f"Generating metadata using {config['provider']} / {config['model']}")
        text, input_tokens, output_tokens = generate_from_config(
            config,
            GEN_OUTLINE_SYSTEM_PROMPT.format(intro_prompt=self.intro_prompt),
            self._seed(GEN_METADATA_USER_PROMPT.format(
                word_count=self.wordcount,
                schema=schema_to_json("novel", "metadata", "worldbuilding"),
            )),
        )
        self.metadata = text
        self.metadata_tokens = (input_tokens, output_tokens)
        self.metadata_cost = calculate_cost(config, input_tokens, output_tokens)
        print(self.metadata)
        return self.metadata

    def generate_spine(self):
        config = self.routing["spine"]
        print(f"Generating the plot spine using {config['provider']} / {config['model']}")
        text, input_tokens, output_tokens = generate_from_config(
            config,
            GEN_OUTLINE_SYSTEM_PROMPT.format(intro_prompt=self.intro_prompt),
            self._seed(GEN_SPINE_USER_PROMPT.format(metadata=self.metadata, word_count=self.wordcount)),
        )
        self.spine = text
        self.spine_tokens = (input_tokens, output_tokens)
        self.spine_cost = calculate_cost(config, input_tokens, output_tokens)
        print(self.spine)
        return self.spine

    def generate_characters(self):
        # Use the intro prompt and the outline to generate detailed character information.
        config = self.routing["characters"]
        print(f"Generating character details using {config['provider']} / {config['model']}")
        text, input_tokens, output_tokens = generate_from_config(
            config,
            GEN_OUTLINE_SYSTEM_PROMPT.format(intro_prompt=self.intro_prompt),
            self._seed(GEN_CHARACTERS_USER_PROMPT.format(
                metadata=self.metadata,
                spine=self.spine,
                schema=schema_to_json("characters", "locations", "items", "organizations", "events"),
            )),
        )
        self.characters = text
        self.characters_tokens = (input_tokens, output_tokens)
        self.characters_cost = calculate_cost(config, input_tokens, output_tokens)
        print(self.characters)
        return self.characters

    def generate_chapter_outline(self):
        # Generate the final chapter outline (chapters only, no beats)
        config = self.routing["outline"]
        print(f"Generating the final outline using {config['provider']} / {config['model']}")
        text, input_tokens, output_tokens = generate_from_config(
            config,
            GEN_OUTLINE_SYSTEM_PROMPT.format(intro_prompt=self.intro_prompt),
            self._seed(GEN_FINAL_OUTLINE_USER_PROMPT.format(
                metadata=self.metadata,
                spine=self.spine,
                characters=self.characters,
                schema=schema_to_json("chapters"),
            )),
        )
        self.chapters = text
        self.outline_tokens = (input_tokens, output_tokens)
        self.outline_cost = calculate_cost(config, input_tokens, output_tokens)
        print(self.chapters)
        return self.chapters

    def generate_story_beats(self):
        # Generate beats per chapter, filtering context to only what's present in that chapter
        characters_data = self._parse_json(self.characters)
        final_data = self._parse_json(self.chapters)

        # Index characters, locations, items, organizations, and events by model-assigned id for beat filtering
        char_index  = {c["id"]: c for c in self._ensure_list(characters_data.get("characters",    [])) if c.get("id")}
        loc_index   = {l["id"]: l for l in self._ensure_list(characters_data.get("locations",     [])) if l.get("id")}
        item_index  = {i["id"]: i for i in self._ensure_list(characters_data.get("items",         [])) if i.get("id")}
        org_index   = {o["id"]: o for o in self._ensure_list(characters_data.get("organizations", [])) if o.get("id")}
        evt_index   = {e["id"]: e for e in self._ensure_list(characters_data.get("events",        [])) if e.get("id")}

        all_orgs  = list(org_index.values())
        all_evts  = list(evt_index.values())

        beats_config = self.routing["beats"]
        all_beats = []
        self.beats_tokens = []
        self.beats_cost = 0.0
        for chap in self._ensure_list(final_data.get("chapters", [])):
            chapter_id = chap.get("id", "")
            chap_char_ids = self._ensure_list(chap.get("characters_present_ids", []))
            chap_loc_ids  = self._ensure_list(chap.get("location_id", []))
            chap_item_ids = self._ensure_list(chap.get("items_present_ids", []))

            chap_chars = [char_index[cid] for cid in chap_char_ids if cid in char_index]
            chap_locs  = [loc_index[lid]  for lid  in chap_loc_ids  if lid  in loc_index]
            chap_items = [item_index[iid] for iid  in chap_item_ids if iid  in item_index]

            print(f"Generating beats for chapter {chap.get('chapter_number')} using {beats_config['provider']} / {beats_config['model']}")
            text, input_tokens, output_tokens = generate_from_config(
                beats_config,
                GEN_OUTLINE_SYSTEM_PROMPT.format(intro_prompt=self.intro_prompt),
                self._seed(GEN_BEATS_USER_PROMPT.format(
                    metadata=self.metadata,
                    chapter=json.dumps(chap, indent=2),
                    characters=json.dumps(chap_chars, indent=2),
                    locations=json.dumps(chap_locs, indent=2),
                    items=json.dumps(chap_items, indent=2),
                    organizations=json.dumps(all_orgs, indent=2),
                    events=json.dumps(all_evts, indent=2),
                    chapter_id=chapter_id,
                    schema=schema_to_json("beats"),
                )),
            )
            raw_beats = text
            self.beats_tokens.append({"chapter": chap.get("chapter_number"), "input_tokens": input_tokens, "output_tokens": output_tokens})
            self.beats_cost += calculate_cost(beats_config, input_tokens, output_tokens)
            beats_data = self._parse_json(raw_beats)
            for beat in self._ensure_list(beats_data.get("beats", [])):
                beat["chapter_id"] = chapter_id
                all_beats.append(beat)
            print(raw_beats)

        self.story_beats = all_beats
        return self.story_beats

    def generate_outline(self):
        self.generate_metadata()
        self.generate_spine()
        self.generate_characters()
        self.generate_chapter_outline()
        self.generate_story_beats()
        
        

        # Merge all outline pieces into a single dict for generate_story()
        metadata_data = self._parse_json(self.metadata)
        spine_data = self._parse_json(self.spine)
        characters_data = self._parse_json(self.characters)
        final_data = self._parse_json(self.chapters)

        merged = {
            **metadata_data,
            **characters_data,
            "chapters": self._ensure_list(final_data.get("chapters", [])),
            "beats": self.story_beats,
            "metadata": {
                **metadata_data.get("metadata", {}),
                "total_chapters": len(final_data.get("chapters", [])),
                "word_count": spine_data.get("word_count"),
            },
        }
        for key in ("characters", "locations", "items", "organizations", "events", "chapters", "beats"):
            merged[key] = self._ensure_list(merged.get(key))
        self.outline = json.dumps(merged)

        token_stats = {
            "metadata_input_tokens":    self.metadata_tokens[0],
            "metadata_output_tokens":   self.metadata_tokens[1],
            "metadata_cost":            self.metadata_cost,
            "spine_input_tokens":       self.spine_tokens[0],
            "spine_output_tokens":      self.spine_tokens[1],
            "spine_cost":               self.spine_cost,
            "characters_input_tokens":  self.characters_tokens[0],
            "characters_output_tokens": self.characters_tokens[1],
            "characters_cost":          self.characters_cost,
            "outline_input_tokens":     self.outline_tokens[0],
            "outline_output_tokens":    self.outline_tokens[1],
            "outline_cost":             self.outline_cost,
            "beats_tokens":             json.dumps(self.beats_tokens),
            "beats_cost":               self.beats_cost,
        }
        novel_id = insert_outline(self.outline, token_stats)

        return novel_id
    
    def get_novel_metadata(self, novel_id: str) -> dict:
        conn = get_connection()
        row = conn.execute(
            "SELECT tense, perspective FROM metadata WHERE novel_id = ?",
            (novel_id,)
        ).fetchone()
        conn.close()
        return {"tense": row[0], "perspective": row[1]} if row else {}

    def get_chapter_count(self, novel_id: str) -> int:
        conn = get_connection()
        count = conn.execute(
            "SELECT COUNT(*) FROM chapter WHERE novel_id = ?", (novel_id,)
        ).fetchone()[0]
        conn.close()
        return count

    def get_beat_characters(self, beat: dict) -> list:
        ids = json.loads(beat.get("characters_present_ids") or "[]")
        if not ids:
            return []
        conn = get_connection()
        char_cols = ["id", "name", "age", "gender", "role", "appearance", "personality", "arc", "backstory", "voice", "speech_patterns"]
        characters = [
            dict(zip(char_cols, row))
            for cid in ids
            for row in conn.execute(
                "SELECT id, name, age, gender, role, appearance, personality, arc, backstory, voice, speech_patterns "
                "FROM characters WHERE id = ?",
                (cid,)
            ).fetchall()
        ]
        conn.close()
        return characters

    def get_beat_location(self, beat: dict) -> dict | None:
        location_id = beat.get("location_id")
        if not location_id:
            return None
        conn = get_connection()
        loc_cols = ["id", "name", "region", "description", "atmosphere"]
        row = conn.execute(
            "SELECT id, name, region, description, atmosphere FROM locations WHERE id = ?",
            (location_id,)
        ).fetchone()
        conn.close()
        return dict(zip(loc_cols, row)) if row else None

    def get_beat_items(self, beat: dict) -> list:
        ids = json.loads(beat.get("items_present_ids") or "[]")
        if not ids:
            return []
        conn = get_connection()
        item_cols = ["id", "name", "description", "symbolic_weight"]
        items = [
            dict(zip(item_cols, row))
            for iid in ids
            for row in conn.execute(
                "SELECT id, name, description, symbolic_weight FROM items WHERE id = ?",
                (iid,)
            ).fetchall()
        ]
        conn.close()
        return items

    def get_beat_organizations(self, beat: dict) -> list:
        ids = json.loads(beat.get("organizations_involved") or "[]")
        if not ids:
            return []
        conn = get_connection()
        org_cols = ["id", "name", "type", "goals", "resources", "access"]
        orgs = [
            dict(zip(org_cols, row))
            for oid in ids
            for row in conn.execute(
                "SELECT id, name, type, goals, resources, access FROM organizations WHERE id = ?",
                (oid,)
            ).fetchall()
        ]
        conn.close()
        return orgs

    def get_beat_events(self, beat: dict) -> list:
        ids = json.loads(beat.get("events_ids") or "[]")
        if not ids:
            return []
        conn = get_connection()
        evt_cols = ["id", "title", "description", "status", "narrative_salience"]
        events = [
            dict(zip(evt_cols, row))
            for eid in ids
            for row in conn.execute(
                "SELECT id, title, description, status, narrative_salience FROM events WHERE id = ?",
                (eid,)
            ).fetchall()
        ]
        conn.close()
        return events

    def get_beats(self, chapter_id: str) -> list:
        conn = get_connection()
        beat_cols = ["id", "beat_number", "description", "pov", "word_count", "location_id", "characters_present_ids", "items_present_ids", "organizations_involved", "events_ids", "tension_level", "heat_level", "key_events"]
        beats = [
            dict(zip(beat_cols, row))
            for row in conn.execute(
                "SELECT id, beat_number, description, pov, word_count, location_id, characters_present_ids, items_present_ids, organizations_involved, events_ids, tension_level, heat_level, key_events "
                "FROM beats WHERE chapter_id = ? ORDER BY beat_number",
                (chapter_id,)
            ).fetchall()
        ]
        conn.close()
        return beats

    def get_chapters(self, novel_id: str) -> list:
        conn = get_connection()
        chapter_cols = ["id", "chapter_number", "title", "summary", "emotional_arc", "intimate_arc_role", "chapter_end_hook", "word_count"]
        chapters = [
            dict(zip(chapter_cols, row))
            for row in conn.execute(
                "SELECT id, chapter_number, title, summary, emotional_arc, intimate_arc_role, chapter_end_hook, word_count "
                "FROM chapter WHERE novel_id = ? ORDER BY chapter_number",
                (novel_id,)
            ).fetchall()
        ]
        conn.close()
        return chapters

    def insert_chapter_manuscript(self, novel_id: str, chapter: dict, beats_prose: list, beats_summary: str, story_so_far: str, model: str = None, input_tokens: int = None, output_tokens: int = None, cost: float = None):
        conn = get_connection()
        conn.execute(
            "INSERT INTO manuscripts (id, novel_id, chapter_number, title, summary, story_so_far, prose, word_count, model, input_tokens, output_tokens, cost, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                str(uuid.uuid4()),
                novel_id,
                chapter["chapter_number"],
                chapter["title"],
                beats_summary,
                story_so_far,
                "\n\n".join(beats_prose),
                sum(len(p.split()) for p in beats_prose),
                model,
                input_tokens,
                output_tokens,
                cost,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        conn.commit()
        conn.close()

    def generate_story_beat_by_beat(self, novel_id: str, limit: int = None):
        config = self.routing["prose"]
        print(f"Generating prose using {config['provider']} / {config['model']}")
        init_db()

        # Initialize running summary and full story accumulator
        self.running_summary = ""
        self.story_so_far = ""

        # Fetch tense and perspective to anchor prose generation
        novel_meta = self.get_novel_metadata(novel_id)
        tense = novel_meta.get("tense", "past")
        perspective = novel_meta.get("perspective", "third_person_limited")
        system_prompt = GEN_BEAT_BY_BEAT_SYSTEM_PROMPT.format(tense=tense, perspective=perspective)

        # Get the chapter count
        chapter_count = self.get_chapter_count(novel_id)
        print(f"Found {chapter_count} chapters")

        # Get all chapter data upfront
        chapters = self.get_chapters(novel_id)
        if limit:
            chapters = [c for c in chapters if c["chapter_number"] == limit]


        # Loop over the chapter count.
        for chapter in chapters:
            chapter_number = chapter["chapter_number"]
            print("--- Generating chapter ", chapter_number, " ---")
            print(f"  Summary: {chapter['summary']}")

            beats_prose = []
            beats_summary = ""
            chapter_input_tokens = 0
            chapter_output_tokens = 0
            chapter_cost = 0.0

            beats = self.get_beats(chapter["id"])
            total_beats = len(beats)
            previous_beat_summary = None
            for beat in beats:
                print(f"  Beat {beat['beat_number']}: {beat['description'][:80]}...")
                #print(f"    Tension: {beat['tension_level']} | Heat: {beat['heat_level']}")

                # Extract static character, location, item, organization, event data for the chapter from database
                # Extract state character, location, item, organization, event data for the chapter from database dont worry about this
                characters = [
                    {k: c[k] for k in ("id", "name", "age", "gender", "role", "appearance", "personality", "voice", "speech_patterns") if k in c}
                    for c in self.get_beat_characters(beat)
                ]
                location = self.get_beat_location(beat)
                items = self.get_beat_items(beat)
                organizations = self.get_beat_organizations(beat)
                events = self.get_beat_events(beat)
                #print(f"    Characters: {[c['name'] for c in characters]}")
                #print(f"    Location: {location['name'] if location else 'None'}")
                #print(f"    Items: {[i['name'] for i in items]}")

                # Resolve POV UUID to character name for the prompt
                pov_id = beat.get("pov")
                pov_char = next((c for c in characters if c["id"] == pov_id), None)
                pov_label = pov_char["name"] if pov_char else pov_id

                # Build previous beat context — omit for the first beat of a chapter
                if previous_beat_summary:
                    previous_beat_context = f"Previous beat ended: {previous_beat_summary}\n\n"
                else:
                    previous_beat_context = ""

                # Build optional context blocks — omit entirely if empty
                optional_context = ""
                if organizations:
                    optional_context += f"Organizations involved:\n{json.dumps(organizations, indent=2)}\n\n"
                if events:
                    optional_context += f"Active events:\n{json.dumps(events, indent=2)}\n\n"

                # Beat position label so the model knows where in the chapter arc it sits
                beat_position = f"{beat['beat_number']} of {total_beats}"

                # On the final beat, remind the model to land the chapter on its end hook
                if beat["beat_number"] == total_beats and chapter.get("chapter_end_hook"):
                    chapter_end_instruction = f"This is the final beat of the chapter. Close it on the chapter's intended end hook: {chapter['chapter_end_hook']}\n\n"
                else:
                    chapter_end_instruction = ""

                # Assemble the prompt using running summary and extracted information
                user_prompt = GEN_BEAT_USER_PROMPT.format(
                    running_summary=self.running_summary,
                    chapter_beats_so_far=beats_summary,
                    chapter_number=chapter_number,
                    chapter_title=chapter["title"],
                    chapter_summary=chapter["summary"],
                    emotional_arc=chapter["emotional_arc"],
                    beat_number=beat["beat_number"],
                    beat_word_count=beat["word_count"],
                    tension_level=beat["tension_level"],
                    heat_level=beat["heat_level"],
                    pov=pov_label,
                    beat_description=beat["description"],
                    key_events=beat["key_events"],
                    characters=json.dumps(characters, indent=2),
                    location=json.dumps(location, indent=2),
                    items=json.dumps(items, indent=2),
                    previous_beat_context=previous_beat_context,
                    optional_context=optional_context,
                    beat_position=beat_position,
                    chapter_end_instruction=chapter_end_instruction,
                )
                
                
                #print("User Prompt:")
                #print(user_prompt)
    
                # Generate the story beat. Send assembled prompt and running summary to
                try:
                    raw, input_tokens, output_tokens = generate_from_config(
                        config,
                        system_prompt,
                        self._seed(user_prompt),
                    )
                except Exception as e:
                    print(f"  ERROR: API call failed for beat {beat['beat_number']}: {e}")
                    raise
                chapter_input_tokens += input_tokens
                chapter_output_tokens += output_tokens
                chapter_cost += calculate_cost(config, input_tokens, output_tokens)
                try:
                    result = self._parse_json(raw)
                except Exception as e:
                    print(f"  ERROR: JSON parse failed for beat {beat['beat_number']}: {e}")
                    print(f"  Raw response (first 500 chars): {raw[:500] if raw else 'None'}")
                    raise
                beats_prose.append(result.get("prose", ""))
                previous_beat_summary = result.get("summary", "")
                beats_summary += f"\nBeat {beat['beat_number']}: {previous_beat_summary}"
                print(f"    Generated {result.get('word_count', '?')} words for beat {beat['beat_number']}")
            # Update running summary with this chapter's beat summaries
            self.running_summary += f"\n\nChapter {chapter_number} — {chapter['title']}:\n{beats_summary}"
            # Update state dont worry about this

            # Add manuscript to database
            self.story_so_far += f"\n\n{'='*60}\nCHAPTER {chapter_number}: {chapter['title']}\n{'='*60}\n\n" + "\n\n".join(beats_prose)
            self.insert_chapter_manuscript(novel_id, chapter, beats_prose, beats_summary, self.story_so_far, model=config["model"], input_tokens=chapter_input_tokens, output_tokens=chapter_output_tokens, cost=chapter_cost)
            print(f"  Chapter {chapter_number} saved to manuscripts.")
            print(f"\n{'='*60}\nCHAPTER {chapter_number}: {chapter['title']}\n{'='*60}")
            print("\n\n".join(beats_prose))
        
        
            
    def generate_story_chapter_by_chapter(self, novel_id: str, limit: int = None):
        config = self.routing["prose"]
        print(f"Generating prose using {config['provider']} / {config['model']}")
        init_db()

        # Initialize running summary and full story accumulator
        self.running_summary = ""
        self.story_so_far = ""

        # Fetch tense and perspective to anchor prose generation
        novel_meta = self.get_novel_metadata(novel_id)
        tense = novel_meta.get("tense", "past")
        perspective = novel_meta.get("perspective", "third_person_limited")
        system_prompt = GEN_CHAPTER_BY_CHAPTER_SYSTEM_PROMPT.format(tense=tense, perspective=perspective)

        chapter_count = self.get_chapter_count(novel_id)
        print(f"Found {chapter_count} chapters")

        chapters = self.get_chapters(novel_id)
        if limit:
            chapters = [c for c in chapters if c["chapter_number"] == limit]

        for chapter in chapters:
            chapter_number = chapter["chapter_number"]
            print(f"--- Generating chapter {chapter_number} ---")
            print(f"  Summary: {chapter['summary']}")

            beats = self.get_beats(chapter["id"])

            # Iterate over every beat and collect unique character, location, item, organization, and event records
            characters    = []
            locations     = []
            items         = []
            organizations = []
            events        = []
            for beat in beats:
                for c in self.get_beat_characters(beat):
                    if not any(x["id"] == c["id"] for x in characters):
                        characters.append({k: c[k] for k in ("id", "name", "age", "gender", "role", "appearance", "personality", "voice", "speech_patterns") if k in c})
                loc = self.get_beat_location(beat)
                if loc and not any(x["id"] == loc["id"] for x in locations):
                    locations.append(loc)
                for i in self.get_beat_items(beat):
                    if not any(x["id"] == i["id"] for x in items):
                        items.append(i)
                for o in self.get_beat_organizations(beat):
                    if not any(x["id"] == o["id"] for x in organizations):
                        organizations.append(o)
                for e in self.get_beat_events(beat):
                    if not any(x["id"] == e["id"] for x in events):
                        events.append(e)

            # Build a character id->name index for resolving POV labels in beats
            char_name_index = {c["id"]: c["name"] for c in characters}

            # Build the beats block for the prompt — each beat as a compact labeled section
            beats_block = ""
            for beat in beats:
                pov_label = char_name_index.get(beat.get("pov"), beat.get("pov"))
                beats_block += (
                    f"Beat {beat['beat_number']} | Word count: {beat['word_count']} | "
                    f"Tension: {beat['tension_level']} | Heat: {beat['heat_level']} | POV: {pov_label}\n"
                    f"Description: {beat['description']}\n"
                    f"Key events: {beat['key_events']}\n\n"
                )

            # Build optional context block — omit entirely if empty
            optional_context = ""
            if organizations:
                optional_context += f"Organizations involved:\n{json.dumps(organizations, indent=2)}\n\n"
            if events:
                optional_context += f"Active events:\n{json.dumps(events, indent=2)}\n\n"

            user_prompt = GEN_CHAPTER_USER_PROMPT.format(
                running_summary=self.running_summary,
                chapter_number=chapter_number,
                total_chapters=chapter_count,
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
                raw, input_tokens, output_tokens = generate_from_config(
                    config,
                    system_prompt,
                    self._seed(user_prompt),
                )
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

            # Update running summary with this chapter's summary
            self.running_summary += f"\n\nChapter {chapter_number} — {chapter['title']}:\n{chapter_summary}"

            # Add manuscript to database — wrap prose in a single-element list to match insert_chapter_manuscript signature
            self.story_so_far += f"\n\n{'='*60}\nCHAPTER {chapter_number}: {chapter['title']}\n{'='*60}\n\n{prose}"
            self.insert_chapter_manuscript(novel_id, chapter, [prose], chapter_summary, self.story_so_far, model=config["model"], input_tokens=input_tokens, output_tokens=output_tokens, cost=cost)
            print(f"  Chapter {chapter_number} saved to manuscripts.")
            print(f"\n{'='*60}\nCHAPTER {chapter_number}: {chapter['title']}\n{'='*60}")
            print(prose)


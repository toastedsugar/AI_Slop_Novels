import json
import os
import re
from json_repair import repair_json
from utils.model_routing import load_routing, generate_from_config
from prompts.outline import GEN_OUTLINE_SYSTEM_PROMPT, GEN_METADATA_USER_PROMPT, GEN_ROUGH_OUTLINE_USER_PROMPT, GEN_CHARACTERS_USER_PROMPT, GEN_FINAL_OUTLINE_USER_PROMPT
from utils.db_insert_outline import insert_outline
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


    def generate_outline(self):

        config = self.routing["metadata"]

        # Use the intro prompt to the worldbuilding and metadata.
        print(f"Generating metadata using {config['provider']} / {config['model']}")
        
        self.metadata = generate_from_config(
            config,
            GEN_OUTLINE_SYSTEM_PROMPT.format(intro_prompt=self.intro_prompt),
            GEN_METADATA_USER_PROMPT.format(
                word_count=self.wordcount,
                schema=schema_to_json("metadata", "worldbuilding"),
            ),
        )
        
        # Generate the rough outline
        print(f"Generating the rough outline using {config['provider']} / {config['model']}")
        self.rough_outline = generate_from_config(
            config,
            GEN_OUTLINE_SYSTEM_PROMPT.format(intro_prompt=self.intro_prompt),
            GEN_ROUGH_OUTLINE_USER_PROMPT.format(metadata=self.metadata, word_count=self.wordcount),
        )

        # Use the intro prompt and the outline to generate detailed character information.
        print(f"Generating character details using {config['provider']} / {config['model']}")
        self.characters = generate_from_config(
            config,
            GEN_OUTLINE_SYSTEM_PROMPT.format(intro_prompt=self.intro_prompt),
            GEN_CHARACTERS_USER_PROMPT.format(
                metadata=self.metadata,
                rough_outline=self.rough_outline,
                schema=schema_to_json("characters", "locations", "items", "organizations", "events"),
            ),
        )

        # Use the intro prompt and the outline and characters to generate the final, finished outline.
        print(f"Generating the final outline using {config['provider']} / {config['model']}")
        self.final_outline = generate_from_config(
            config,
            GEN_OUTLINE_SYSTEM_PROMPT.format(intro_prompt=self.intro_prompt),
            GEN_FINAL_OUTLINE_USER_PROMPT.format(
                metadata=self.metadata,
                rough_outline=self.rough_outline,
                characters=self.characters,
                schema=schema_to_json("chapters", "beats"),
            ),
        )

        # Merge all outline pieces into a single dict for generate_story()
        def _parse_json(s):
            if not s:
                raise ValueError(f"_parse_json received empty/None response")
            match = re.search(r"\{.*\}", s, flags=re.DOTALL)
            if not match:
                raise ValueError(f"No JSON found in response: {s[:200]}")
            return json.loads(repair_json(match.group()))

        metadata_data = _parse_json(self.metadata)
        rough_data = _parse_json(self.rough_outline)
        characters_data = _parse_json(self.characters)
        final_data = _parse_json(self.final_outline)

        # Normalizes a value to a list — wraps a single dict in a list, passes a list through, returns [] otherwise.
        # Because db_insert_outline.py iterates over characters, locations, items, and chapters and expects a list of dicts. If the model returns a single dict instead of a list, the for loop iterates over the dict's keys (which are strings), and then char.get(...) fails because strings don't have .get().
        def _ensure_list(val):
            if isinstance(val, list):
                return val
            if isinstance(val, dict):
                return [val]
            return []

        rough_story_info = rough_data.get("story_information", {})
        merged = {
            **metadata_data,
            **characters_data,
            **final_data,
            "metadata": {
                **metadata_data.get("metadata", {}),
                "total_chapters": len(final_data.get("chapters", [])),
                "word_count": rough_story_info.get("word_count"),
                "chapter_count": rough_story_info.get("chapter_count"),
            },
        }
        for key in ("characters", "locations", "items", "organizations", "events", "chapters", "beats"):
            merged[key] = _ensure_list(merged.get(key))
        self.outline = json.dumps(merged)

        insert_outline(self.outline)

        return self.outline

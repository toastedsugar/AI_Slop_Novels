import json
import os
import re
from json_repair import repair_json
from utils.api_calls import generate_openai, generate_claude
from utils.model_routing import load_routing
from utils.outline_prompts import GEN_OUTLINE_SYSTEM_PROMPT, GEN_OUTLINE_SIMPLE_USER_PROMPT, GEN_METADATA_USER_PROMPT, GEN_ROUGH_OUTLINE_USER_PROMPT, GEN_CHARACTERS_USER_PROMPT, GEN_FINAL_OUTLINE_USER_PROMPT
from utils.generation_prompts import GEN_ONESHOT_SYSTEM_PROMPT, GEN_ONESHOT_USER_PROMPT, GEN_STORY_SYSTEM_PROMPT, GEN_STORY_USER_PROMPT


def _generate(config, system_prompt, user_prompt):
    provider = config["provider"]
    model = config["model"]
    params = {k: v for k, v in config.items() if k not in ("provider", "model")}
    if provider == "anthropic":
        return generate_claude(model, system_prompt, user_prompt, **params)
    elif provider == "openai":
        return generate_openai(model, system_prompt, user_prompt, **params)
    else:
        raise ValueError(f"Unknown provider: {provider}")


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
        self.metadata = _generate(
            config,
            GEN_OUTLINE_SYSTEM_PROMPT.format(intro_prompt=self.intro_prompt),
            GEN_METADATA_USER_PROMPT.format(word_count=self.wordcount),
        )
        #print(self.metadata)
        
        
    
        
        # Generate the rough outline
        print(f"Generating the rough outline using {config['provider']} / {config['model']}")
        self.rough_outline = _generate(
            config,
            GEN_OUTLINE_SYSTEM_PROMPT.format(intro_prompt=self.intro_prompt),
            GEN_ROUGH_OUTLINE_USER_PROMPT.format(metadata=self.metadata),
        )
        #print(self.rough_outline)
                
    
        # Use the intro prompt and the outline to generate detailed character information.
        print(f"Generating character details using {config['provider']} / {config['model']}")
        self.characters = _generate(
            config,
            GEN_OUTLINE_SYSTEM_PROMPT.format(intro_prompt=self.intro_prompt),
            GEN_CHARACTERS_USER_PROMPT.format(
                metadata=self.metadata,
                rough_outline=self.rough_outline
            ),
        )
        #print(self.characters)


        # Use the intro prompt and the outline and characters to generate the final, finished outline.
        print(f"Generating the final outline using {config['provider']} / {config['model']}")
        self.final_outline = _generate(
            config,
            GEN_OUTLINE_SYSTEM_PROMPT.format(intro_prompt=self.intro_prompt),
            GEN_FINAL_OUTLINE_USER_PROMPT.format(
                metadata=self.metadata,
                rough_outline=self.rough_outline,
                characters=self.characters
            ),
        )
        #print(self.final_outline)

        # Merge all outline pieces into a single dict for generate_story()
        def _parse_json(s):
            match = re.search(r"\{.*\}", s, flags=re.DOTALL)
            if not match:
                raise ValueError(f"No JSON found in response: {s[:200]}")
            return json.loads(repair_json(match.group()))

        metadata_data = _parse_json(self.metadata)
        characters_data = _parse_json(self.characters)
        final_data = _parse_json(self.final_outline)

        self.outline = json.dumps({
            **metadata_data,
            **characters_data,
            **final_data,
            "metadata": {
                **metadata_data.get("metadata", {}),
                "total_chapters": len(final_data.get("chapters", [])),
            },
        })
        
        print(json.dumps(self.outline, indent=2))
        
        return self.outline
        
    def generate_outline_simple(self):

        config = self.routing["outline"]
        print(f"Generating outline using {config['provider']} / {config['model']}")
        self.outline = _generate(
            config,
            GEN_OUTLINE_SYSTEM_PROMPT.format(
                intro_prompt=self.intro_prompt,
                word_count=self.wordcount
            ),
            GEN_OUTLINE_SIMPLE_USER_PROMPT
        )
        return self.outline
        

    def generate_story_simple(self):
        story = ""
        config = self.routing["prose"]

        # Extract the JSON object from the response, ignoring any surrounding prose or code fences
        match = re.search(r"\{.*\}", self.outline, flags=re.DOTALL)
        if not match:
            raise ValueError(f"No JSON object found in outline response: {self.outline[:200]}")
        outline_data = json.loads(match.group())
        chapters = outline_data["chapters"]
        chapter_count = outline_data["metadata"]["total_chapters"]

        # Build lookup maps so chapter entries can reference full details instead of ids
        char_map = {c["id"]: c for c in outline_data.get("characters", [])}
        loc_map  = {l["id"]: l for l in outline_data.get("locations", [])}
        obj_map  = {o["id"]: o for o in outline_data.get("items", [])}

            
        print(f"Generating {chapter_count} chapters using {config['provider']} / {config['model']}")
        
        system_prompt = GEN_STORY_SYSTEM_PROMPT.format(
            outline=outline_data.get("premise", outline_data.get("summary", "")),
            authorial_voice=self.authorial_voice,
        )

        # for chapters in chapter count, generate one chapter and append it to story
        for chapter in chapters:
            print(f"  Generating chapter {chapter['chapter_number']}: {chapter['title']}")
            def fmt_char(cid):
                c = char_map.get(cid)
                if not c:
                    return f"- {cid}"
                voice = ', '.join(c.get('character_voice', []))
                patterns = ', '.join(c.get('character_speech_patterns', []))
                return f"- {c['name']} ({c.get('role', '')}): {c.get('description', '')} Personality: {', '.join(c.get('personality', []))}. Arc: {c.get('arc', '')}. Voice: {voice}. Speech patterns: {patterns}"

            def fmt_loc(lid):
                l = loc_map.get(lid)
                if not l:
                    return f"- {lid}"
                return f"- {l['name']}: {l.get('description', '')} Significance: {l.get('significance', '')}"

            def fmt_obj(oid):
                o = obj_map.get(oid)
                if not o:
                    return f"- {oid}"
                return f"- {o['name']}: {o.get('description', '')} Significance: {o.get('significance', '')}"




            user_prompt = GEN_STORY_USER_PROMPT.format(
                chapter_number=chapter["chapter_number"],
                chapter_title=chapter["title"],
                chapter_word_count=chapter.get("word_count", self.wordcount // chapter_count),
                chapter_summary=chapter["summary"],
                key_events="\n".join(f"- {e}" for e in chapter.get("key_events", [])),
                characters_present="\n".join(fmt_char(cid) for cid in chapter.get("characters_present_ids", [])),
                locations="\n".join(fmt_loc(lid) for lid in chapter.get("location_id", [])),
                items="\n".join(fmt_obj(oid) for oid in chapter.get("items_present_ids", [])),
            )
            output = _generate(
                config,
                system_prompt,
                user_prompt,
            )
            print(output)
            story += output
            story += "\n\n\n\n\n"
            
            '''
            print(system_prompt, "\n\n\n\n")
            print(user_prompt, "\n\n\n\n")
            '''
            
        self.story = story
        title = outline_data.get("metadata", {}).get("title", "untitled")
        self.write_to_file(title)
        return story
        
        

    def generate_oneshot(self):
        config = self.routing["prose"]
        print(f"Generating prose using {config['provider']} / {config['model']}")
        return _generate(
            config,
            GEN_ONESHOT_SYSTEM_PROMPT.format(
                word_count=self.wordcount,
                outline=self.outline
            ),
            GEN_ONESHOT_USER_PROMPT,
        )
        
    def generate_story(self):
        story = ""
        config = self.routing["prose"]

        # Extract the JSON object from the response, ignoring any surrounding prose or code fences
        match = re.search(r"\{.*\}", self.outline, flags=re.DOTALL)
        if not match:
            raise ValueError(f"No JSON object found in outline response: {self.outline[:200]}")
        outline_data = json.loads(match.group())
        chapters = outline_data["chapters"]
        chapter_count = outline_data["metadata"]["total_chapters"]

        # Build lookup maps so chapter entries can reference full details instead of ids
        char_map = {c["id"]: c for c in outline_data.get("characters", [])}
        loc_map  = {l["id"]: l for l in outline_data.get("locations", [])}
        obj_map  = {o["id"]: o for o in outline_data.get("items", [])}

            
        print(f"Generating {chapter_count} chapters using {config['provider']} / {config['model']}")
        
        system_prompt = GEN_STORY_SYSTEM_PROMPT.format(
            outline=outline_data.get("premise", outline_data.get("summary", "")),
            authorial_voice=self.authorial_voice,
        )

        # for chapters in chapter count, generate one chapter and append it to story
        for chapter in chapters:
            print(f"  Generating chapter {chapter['chapter_number']}: {chapter['title']}")
            def fmt_char(cid):
                c = char_map.get(cid)
                if not c:
                    return f"- {cid}"
                voice = ', '.join(c.get('character_voice', []))
                patterns = ', '.join(c.get('character_speech_patterns', []))
                return f"- {c['name']} ({c.get('role', '')}): {c.get('description', '')} Personality: {', '.join(c.get('personality', []))}. Arc: {c.get('arc', '')}. Voice: {voice}. Speech patterns: {patterns}"

            def fmt_loc(lid):
                l = loc_map.get(lid)
                if not l:
                    return f"- {lid}"
                return f"- {l['name']}: {l.get('description', '')} Significance: {l.get('significance', '')}"

            def fmt_obj(oid):
                o = obj_map.get(oid)
                if not o:
                    return f"- {oid}"
                return f"- {o['name']}: {o.get('description', '')} Significance: {o.get('significance', '')}"




            user_prompt = GEN_STORY_USER_PROMPT.format(
                chapter_number=chapter["chapter_number"],
                chapter_title=chapter["title"],
                chapter_word_count=chapter.get("word_count", self.wordcount // chapter_count),
                chapter_summary=chapter["summary"],
                key_events="\n".join(f"- {e}" for e in chapter.get("key_events", [])),
                characters_present="\n".join(fmt_char(cid) for cid in chapter.get("characters_present_ids", [])),
                locations="\n".join(fmt_loc(lid) for lid in chapter.get("location_id", [])),
                items="\n".join(fmt_obj(oid) for oid in chapter.get("items_present_ids", [])),
            )
            output = _generate(
                config,
                system_prompt,
                user_prompt,
            )
            print(output)
            story += output
            story += "\n\n\n\n\n"
            
            '''
            print(system_prompt, "\n\n\n\n")
            print(user_prompt, "\n\n\n\n")
            '''
            
        self.story = story
        title = outline_data.get("metadata", {}).get("title", "untitled")
        self.write_to_file(title)
        return story

    def write_to_file(self, file_name: str):
        os.makedirs("outputs", exist_ok=True)
        safe_name = re.sub(r'[^\w\s-]', '', file_name).strip().replace(' ', '_')
        output_path = f"outputs/{safe_name}.txt"
        with open(output_path, "w") as f:
            f.write(self.story)
        print(f"\n\n\n\n --- Story written to {output_path} ---")



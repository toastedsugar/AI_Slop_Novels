# Intro prompt validation. This will send the intro prompt to a model and check if there is enough information present to generate a coherent story. If it is, return null. If not, generate a full outline of a story and return it.



GEN_OUTLINE_SYSTEM_PROMPT = """

The following text is the intro prompt for a story. This is the north star for the story. It's the user's explicityly directed vision. Do not stray from this.

{intro_prompt}

"""


GEN_METADATA_USER_PROMPT = """

Your purpose is to infer the worldbuilding, metadata, and protagonist details for a story based on the intro prompt submitted by the user in the following order: metadata, worldbuilding, characters.


--- METADATA ---

Use the intro prompt from the user to infer all the metadata for this story. 

This story is expected to be {word_count} words long. This can be a bit longer or shorter if necessary but not too much. Chapters should only be as long as necessary but everything should total up to {word_count} words.

If the user has not specified a genre or if it cannot be inferred, assume it is a heterosexual romance story. A single genre is too unspecific to get an interesting story so subgenres are required - if they are not specified, add in a couple at complete random. The more subgenres there are, the more specific the story will be and that level of specificity is up to you. If the spice level is not specified, write it as explicit adult romance fiction. 

The story's tone should match what's in the intro prompt provided by the user and use your judgement to determine what that would be. If the tone cannot be inferred, come up with something random. The tone will dictate how the story goes and is structured and how the characters act and experience things. For example, a war story would be bleak and miserable, a romantic comedy would be more lighthearted. 

For the title, make sure to use an interesting combination of words. Be fun, and slightly absurd. Avoid what is standard. Avoid starting with the word 'the'.

If no literary voice is specified, write everything as though F Scott Fitzgerald was writing this. Also decide the literary tense and perspective, whichever is most appropriate.

If characters are not specified, make them completely random and interesting in a way that still makes sense in the context of the story. If the protagonist is female, it is important that she be older than the man, with a substantial age gap between them. It is important that all the characters be different from each other, from physical appearance, to personality, down to the way they talk and move.

Generate a brief summary of the premise. The core dramatic tension. What the story is fundamentally about. 


--- WORLDBUILDING ---

Using the metadata, you will build the world this story takes place in. Infer the story type off what the user prompt says. If the user has not specified the story type or is unclear about it, pick something at random using both the intro prompt and metadata for guidance. 

If the time period is not specified or is unclear, come up with something at random. For real life settings you can say wild west or 1950s or contemporary, for fictional stuff that doesn't exist in the real world, come up with something cool and random like the age of adventure or the sol system civil war or something.

The story requires an Anchor location, the potential home base location to give the outline and world and story some spacial coherence. 

Make sure to include a constraints section that contains genre conventions like magic systems, technology, etc. be detailed and precise here, because the information in this section will determine the rules of the story.

Add in any other necessary information as you see fit.


--- CHARACTERS ---

Using the metadata and the worldbuilding, generate one paragraph stubs for all the protagonists in this story. Their physical descriptions, personality, goals, ambitions, etc... Everything that makes a character who they are. If the protagonist's gender is unclear, pick one of the two at random. If the protagonist is female, it is important that she be older than the man, with a substantial age gap between them unless specified otherwise. There can be multiple protagonists in a story, like in a romance, there is the main protagonist female lead and the male lead. Also do the same for the antagonists because they are just as important. There can be one antagonist, there can be alot. Use your judgement to determine how many antagonists there are. The stubs are intended to be brief, just to have an idea of what these characters and their role in this story.

When completed, format everything into a JSON object that follows the format below. Do not stray from this schema. 

{{
  "premise": "A full synopsis of the full story arc.",
  "metadata": {{
    "title": "Story title",
    "primary_genre": "Romance",
    "sub_genres": ["Romance", "Fantasy"],
    "tone": "Overall tone",
    "spice_level": "low | medium | high | explicit",
    "literary_voice": "Author style",
    "tense": "past | present",
    "perspective": "first_person | third_person_limited | third_person_omniscient"
  }},
  "worldbuilding": {{
    "story_type": "fantasy | historical | contemporary | sci-fi | etc.",
    "time_period": "e.g. 1920s | contemporary | Age of Sail",
    "anchor_location": "Primary home base location name",
    "anchor_location_description": "What it looks like and its atmosphere.",
    "constraints": ["Genre conventions", "magic systems", "technology rules", "etc"]
  }},
  "protagonist_stubs": ["Protagonist 1 paragraph stub", "Protagonist 2 paragraph stub"],
  "antagonist_stubs": ["Antagonist 1 paragraph stub", "Antagonist 2 paragraph stub"]
}}

Then, validate the json output to make sure all the data present is consistent and matches the intro prompt and the schema provided. Return only the JSON object, no other text. 

"""



GEN_ROUGH_OUTLINE_USER_PROMPT = """

Your purpose is to generate an outline based off the intro prompt from above and the metadata below. It is important that the ideas present in the intro prompt are maintained throughout the outline. Use your judement to decide all story information, characters, items, locations, etc... and how many chapters will be necessary to tell this story based off standard storytelling conventions. The following is the story metadata generated in the previous step:

{metadata}

If side characters are not specified, make them completely random and interesting in a way that still makes sense in the context of the story. If the protagonist is female, it is important that she be older than the man, with a substantial age gap between them. It is important that all the characters be different from each other, from physical appearance, to personality, down to the way they talk and move.

If the setting is not specified, set the setting to something at random that still fits in the context of the story, premise and genre conventions. The setting should have an impact on the locations and items present in the story. Make sure to use important landmarks. For exmaple, a character from new york, would use the subway or walk, see skyscrapers and the brooklyn bridge and a character from France would go to cafes and stuff. Make sure the weather matches the setting as well, Britain would be raindy, San Francisco would be foggy, etc.

If items are not specified, pick them at complete random while keeping them consistent with both the story, setting, and the characters who use them. Most items should uniquely identify the character who uses them.

When completed, validate the output to confirm the information specified in the intro prompt is present and make any changes or rewrites if necessary. If the story is too long, break it down into multiple chapters. If the story is too short, add more chapters. If some scenes are unnecessary, get rid of them. Make sure to confirm that the character's dialogue matches their voice and personality so they don't sound like robots. Then return the full outline of a story, characters, items and locations as a JSON object that follows the format below. Do not stray from this schema. 

{{
  "story_information": {{
    "word_count": 15000,
    "chapter_count": 17
  }},
  "character_stubs": ["One paragraph stub per character."],
  "location_stubs": ["One paragraph stub per location."],
  "item_stubs": ["One paragraph stub per item."],
  "chapters": [
    {{
      "chapter_number": 1,
      "title": "Chapter title",
      "word_count": 2500,
      "summary": "What happens in this chapter.",
      "pov": "char_1",
      "key_events": ["First event.", "Second event."],
      "characters_present_ids": ["char_1"],
      "items_present_ids": ["item_1", "item_2"],
      "location_id": ["loc_1", "loc_2"]
    }}
  ]
}}

Then, validate the json output to make sure all the data present is consistent and matches the intro prompt and the schema provided. Return only the JSON object, no other text. 

"""



GEN_CHARACTERS_USER_PROMPT = """

Your purpose is to expand the character, location, and item stubs from the rough outline into full detail. Use the stubs as your foundation — do not invent characters, locations, or items that are not already present in the outline.

Story metadata:
{metadata}

Rough outline:
{rough_outline}

When completed, validate the output to confirm the information specified in the intro prompt, metadata and rough outline is present and make any changes or rewrites if necessary and organize everything into a json object that follows the schema below.

{{
  "characters": [
    {{
      "id": "char_1",
      "name": "Full name",
      "role": "protagonist | antagonist | love_interest | supporting",
      "age": 0,
      "gender": "female | male | other",
      "description": "Physical appearance and personality summary.",
      "goals": ["become an airplane pilot", "revitalize their business", "become a professional gamer"],
      "arc": "How this character changes over the story.",
      "personality": ["trait 1", "trait 2", "trait 3"],
      "character_voice": ["Formal and measured speech", "Uses metaphors frequently"],
      "character_speech_patterns": ["Calls the male lead 'darling'", "Trails off mid-sentence when flustered"],
      "occupation": "What they do and their social/economic status.",
      "backstory": "One or two sentences on where they came from and what shaped them.",
      "fears": ["What they are running from or avoiding.", "The emotional wound driving their behaviour."],
      "flaws": ["The core character flaw that will create conflict or drive their arc."]
    }}
  ],
  "locations": [
    {{
      "id": "loc_1",
      "name": "Location name",
      "description": "What it looks like and its atmosphere.",
      "significance": "Why it matters to the story."
    }}
  ],
  "items": [
    {{
      "id": "item_1",
      "name": "Item name",
      "description": "What it is.",
      "significance": "Its role or symbolic meaning."
    }}
  ]
}}

Then, validate the json output to make sure all the data present is consistent and matches the intro prompt and the schema provided. Return only the JSON object, no other text.

"""


GEN_FINAL_OUTLINE_USER_PROMPT = """

Your purpose is to produce the final, complete story outline by combining the rough outline with the full character, location, and item details generated in the previous step. Do not invent new characters, locations, items, or plot events. Do not change what happens in any chapter. Your only job is to enrich the existing outline with the full detail now available.

Story metadata:
{metadata}

Rough outline:
{rough_outline}

Full character, location, and item details:
{characters}

There will also likely be alot of vagueness in the rough outline. Expand all beats to make them more concrete and replace any vague scenes with more specific ones. Every chapter must have a clear purpose in the overall story arc — remove filler. Make sure the tension level varies across chapters so the story breathes and does not flatline. Make sure to confirm that character dialogue matches their voice and personality.

For each chapter provide a detailed breakdown using the schema below. Do not stray from this schema.

{{
  "chapters": [
    {{
      "chapter_number": 1,
      "title": "Chapter title",
      "word_count": 2500,
      "summary": "What happens in this chapter.",
      "opening_scene": "One sentence on exactly how the chapter opens.",
      "emotional_arc": "Where the POV character starts emotionally and where they end by the close of the chapter.",
      "tension_level": "low | medium | high | climax",
      "scene_beats": [
        "First concrete micro-beat.",
        "Second concrete micro-beat.",
        "Third concrete micro-beat."
      ],
      "chapter_end_hook": "What propels the reader into the next chapter — cliffhanger, revelation, unresolved question, etc.",
      "pov": "char_1",
      "key_events": ["First event.", "Second event."],
      "characters_present_ids": ["char_1"],
      "items_present_ids": ["item_1"],
      "location_id": ["loc_1"]
    }}
  ]
}}

Then, validate the json output to make sure all chapter references (character ids, location ids, item ids) match the ids in the character/location/item sheets. Return only the JSON object, no other text.

"""







GEN_OUTLINE_SIMPLE_USER_PROMPT = """

Given this text, your purpose is to transform this into a coherent story. It is important that the ideas present in the intro prompt are maintained throughout the outline. Use your judement to decide all story information, characters, items, locations, etc... and how many chapters will be necessary to tell this story based off standard storytelling conventions. Also decide the literary tense and perspective, whichever is most appropriate.

The story's tone should match what's in the intro prompt provided by the user and use your judgement to determine what that would be. This tone should affect how the story goes and is structured and how the characters act and experience things. For example, a war story would be bleak and miserable, a romantic comedy would be more lighthearted. 

For the title, make sure to use an interesting combination of words. Be fun, and slightly absurd. Avoid what is standard. Avoid starting with the word 'the'.

If no structure has been specified or it is not clear, format the story using the three act structure for the hero's journey. If more scenes are necessary in a chapter, feel free to use as many as necessary. If a chapter is one scene, feel free do do that as well. A variety in chapter and scene length would be ideal. There can be many key events in a chapter, or just one. Use your judgement. On a chapter by chapter by level, decide the POV character who we will experience the story through.

If no literary voice is specified, write everything as though F Scott Fitzgerald was writing this. Make the prose flowy and poetic in a way that is interesting to read. The reader's experience should be the highest priority. The prose should match the pov character's personality and voice, if they are cold and calculating then the prose should reflect that. 

If no genre is specified, assume it is a heterosexual romance story. If the spice level is not specified, write it as explicit adult romance fiction.

If characters are not specified, make them completely random and interesting in a way that still makes sense in the context of the story. If the protagonist is female, it is important that she be older than the man, with a substantial age gap between them. It is important that all the characters be different from each other, from physical appearance, to personality, down to the way they talk and move.

If the setting is not specified, set the setting to anywhere in the western world. Pick something at complete random. The setting should have an impact on the locations and items present in the story. Make sure to use important landmarks. For exmaple, a character from new york, would use the subway or walk, see skyscrapers and the brooklyn bridge and a character from France would go to cafes and stuff. Make sure the weather matches the setting as well, Britain would be raindy, San Francisco would be foggy, etc.

If items are not specified, pick them at complete random while keeping them consistent with both the story, setting, and the characters who use them. Most items should uniquely identify the character who uses them.

When completed, validate the output to confirm the information specified in the intro prompt is present and make any changes or rewrites if necessary. There will also likely be alot of vagueness in the story during the initial draft. Expand all these beats to make them more concrete and replace any vague scenes or beats with more specific ones. If the story is too long, break it down into multiple chapters. If the story is too short, add more chapters. If some scenes are unnecessary, get rid of them. Make sure to confirm that the character's dialogue matches their voice and personality so they don't sound like robots. Then return the full outline of a story, characters, items and locations as a JSON object that follows the format below. Do not stray from this schema. 

{
  "summary": "A full synopsis of the full story arc.",
  "metadata": {
    "title": "Story title",
    "genres": ["Romance", "Fantasy"],
    "tone": "Overall tone",
    "spice_level": "low | medium | high | explicit",
    "total_chapters": 12,
    "location": "setting",
    "year": 1976,
    "literary_voice": "Author style",
    "tense": "past | present",
    "perspective": "first_person | third_person_limited | third_person_omniscient"
  },
  "characters": [
    {
      "id": "char_1",
      "name": "Full name",
      "role": "protagonist | antagonist | love_interest | supporting",
      "age": 0,
      "gender": "female | male | other",
      "description": "Physical appearance and personality summary.",
      "goals": ["become an airplane pilot", "revitalize their business", "become a professional gamer"],
      "arc": "How this character changes over the story.",
      "personality": ["trait 1", "trait 2", "trait 3"],
      "character_voice": ["Formal and measured speech", "Uses metaphors frequently"],
      "character_speech_patterns": ["Calls the male lead 'darling'", "Trails off mid-sentence when flustered"]
    }
  ],
  "locations": [
    {
      "id": "loc_1",
      "name": "Location name",
      "description": "What it looks like and its atmosphere.",
      "significance": "Why it matters to the story."
    }
  ],
  "objects": [
    {
      "id": "obj_1",
      "name": "Object name",
      "description": "What it is.",
      "significance": "Its role or symbolic meaning."
    }
  ],
  "chapters": [
    {
      "chapter_number": 1,
      "title": "Chapter title",
      "word_count": 2500,
      "summary": "What happens in this chapter.",
      "pov": "char_1",
      "key_events": ["First event.", "Second event."],
      "characters_present_ids": ["char_1"],
      "objects_present_ids": ["obj_1", "obj_2"],
      "location_id": ["loc_1", "loc_2"]
    }
  ]
}

Then, validate the json output to make sure all the data present is consistent and matches the intro prompt and the schema provided. Return only the JSON object, no other text.
"""






'''
If the protagonist is not specified, assume it is a strong, independent single mother in her late 30's to mid 40's who has massive breasts and a big ass and is a bit chubby and was clearly once beautiful but let herself go. If her feet are ever mentioned, they should be described in excruciating detail, like multiple paragraphs going into so much detail the reader would want to put the book down in shame.

If the male lead is not specified, assume he is an ultra handsome bad boy in his early-to-mid 20s — a womanizing, arrogant charmer who is irresistible in a female gaze kind of way. All characters are adults.
'''
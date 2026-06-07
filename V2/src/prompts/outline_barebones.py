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

If the user has not specified a genre or if it cannot be inferred, assume it is a heterosexual romance story. A single genre is too unspecific to get an interesting story so subgenres are required - if they are not specified, add in a couple at complete random. The more subgenres there are, the more specific the story will be and that level of specificity is up to you. If the spice level is not specified, write it as explicit adult romance fiction with no fade-to-black — intimate scenes are written through to completion, explicitly and without omission.

The romantic premise must have a structural reason the attraction is forbidden, dangerous, or should not happen — a power imbalance, a rivalry, conflicting loyalties, a secret, a prior betrayal, or a taboo context. This is not optional flavoring; it is the engine of tension. The obstacle must be real enough that giving in feels transgressive, and the characters must be aware of it.

The story's tone should match what's in the intro prompt provided by the user and use your judgement to determine what that would be. If the tone cannot be inferred, come up with something random. The tone will dictate how the story goes and is structured and how the characters act and experience things. For example, a war story would be bleak and miserable, a romantic comedy would be more lighthearted. 

For the title, make sure to use an interesting combination of words. Be fun, and slightly absurd. Avoid what is standard. Avoid starting with the word 'the'.

If no literary voice is specified, write everything as though F Scott Fitzgerald was writing this. Also decide the literary tense and perspective, whichever is most appropriate.

If characters are not specified, make them completely random and interesting in a way that still makes sense in the context of the story. If the protagonist is female, it is important that she be older than the man, with a substantial age gap between them. It is important that all the characters be different from each other, from physical appearance, to personality, down to the way they talk and move. All characters — protagonists, antagonists, and supporting cast alike — should be beautiful. Not uniformly so, but each in their own specific and distinct way. Beauty should be part of who they are, expressed through their appearance, their presence, and how others perceive them.

Generate a brief summary of the premise. The core dramatic tension. What the story is fundamentally about. 


--- WORLDBUILDING ---

Using the metadata, you will build the world this story takes place in. Infer the story type off what the user prompt says. If the user has not specified the story type or is unclear about it, pick something at random using both the intro prompt and metadata for guidance. 

If the time period is not specified or is unclear, come up with something at random. For real life settings you can say wild west or 1950s or contemporary, for fictional stuff that doesn't exist in the real world, come up with something cool and random like the age of adventure or the sol system civil war or something.

The story requires an Anchor location, the potential home base location to give the outline and world and story some spacial coherence. 

Make sure to include a constraints section that contains genre conventions like magic systems, technology, etc. be detailed and precise here, because the information in this section will determine the rules of the story.

Add in any other necessary information as you see fit.


--- CHARACTERS ---

Using the metadata and the worldbuilding, generate one paragraph stubs for all the protagonists in this story. Their physical descriptions, personality, goals, ambitions, etc... Everything that makes a character who they are. If the protagonist's gender is unclear, pick one of the two at random. If the protagonist is female, it is important that she be older than the man, with a substantial age gap between them unless specified otherwise. There can be multiple protagonists in a story, like in a romance, there is the main protagonist female lead and the male lead. Also do the same for the antagonists because they are just as important. There can be one antagonist, there can be alot. Use your judgement to determine how many antagonists there are. The stubs are intended to be brief, just to have an idea of what these characters and their role in this story.

All romantic leads must be written as conventionally and specifically attractive — not generically pretty, but striking in a way that is distracting and hard to ignore. Be explicit about what makes them physically compelling: the specifics of their face, body, how they carry themselves, what draws the eye. Their attractiveness should feel like a problem for the people around them. This applies to both the female and male leads.

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

Your purpose is to generate an outline based off the intro prompt from above and the metadata below. It is important that the ideas present in the intro prompt are maintained throughout the outline. Use your judement to decide all story information, characters, items, locations, etc... and how many chapters will be necessary to tell this story based off standard storytelling conventions. 

The total story must be around {word_count} words. Distribute word count across chapters so they sum to exactly {word_count}. Set story_information.word_count to {word_count}. Use the word count to decide how many chapters are necessary. If more scenes are necessary in a chapter, feel free to use as many as necessary. If a chapter is one scene, feel free do do that as well. A variety in chapter and scene length would be ideal. There can be many key events in a chapter, or just one. Priorize having more short chapters than long ones. Use your judgement. On a chapter by chapter by level, decide the POV character who we will experience the story through.

The following is the story metadata generated in the previous step:

{metadata}

If side characters are not specified, make them completely random and interesting in a way that still makes sense in the context of the story. If the protagonist is female, it is important that she be older than the man, with a substantial age gap between them. It is important that all the characters be different from each other, from physical appearance, to personality, down to the way they talk and move. All characters — leads, side characters, and antagonists alike — should be beautiful, each in their own specific and distinct way. Beauty should be part of who every character is, expressed through their appearance, their presence, and how others perceive and react to them.

All romantic leads must be written as specifically and distractingly attractive — not generic, but striking in a concrete, physical way that other characters notice and react to. Be precise about what makes them compelling: facial features, body, posture, how they move. Their attractiveness should feel like a gravitational pull that creates tension in scenes where they are present. Make sure this is reflected in how other characters respond to them in the outline's scene beats and key events.

Characters, items, and locations should only be described in heavy detail once or twice in the story, usually the first time we meet or experience them. Specify where these major description moments will take place so the prose generation will understand where to do the heavy lifting.

If the setting is not specified, set the setting to something at random that still fits in the context of the story, premise and genre conventions. The setting should have an impact on the locations and items present in the story. Make sure to use important landmarks. For exmaple, a character from new york, would use the subway or walk, see skyscrapers and the brooklyn bridge and a character from France would go to cafes and stuff. Make sure the weather matches the setting as well, Britain would be raindy, San Francisco would be foggy, etc.

If items are not specified, pick them at complete random while keeping them consistent with both the story, setting, and the characters who use them. Most items should uniquely identify the character who uses them.

--- GAZE AND SPICE ---

This story should be written to satisfy both the female gaze and the male gaze simultaneously, as structural principles that shape how scenes are built and paced.

For the female gaze: scenes should build on emotional interiority and anticipation. The protagonist's internal experience of desire — the longing, the awareness, the tension of being seen and wanted — should be the engine driving romantic and intimate scenes. Intimacy must be earned through emotional buildup. Focus on how the love interest makes the protagonist feel, not just what they look like. Use all senses: the warmth of proximity, the sound of a voice, the texture of touch. Power dynamics, vulnerability, and the slow erosion of resistance are all strong tools here.

For the male gaze: include direct, confident, and visually-forward physical appreciation. Characters should be aware of and openly attracted to each other's bodies. Physical tension and desire should be present and unambiguous. Do not soften or abstract physical attraction — name it plainly.

To maximize spice: structure the outline so romantic and sexual tension escalates chapter by chapter. Early chapters should establish desire and chemistry. Middle chapters should use proximity, near-misses, interrupted moments, and unresolved longing to build pressure. The payoff chapters should deliver fully on what was promised — nothing withheld, nothing faded-to-black unless the metadata specifies otherwise. Every chapter hook in the intimate arc should leave unresolved desire pulling the reader forward. The outline should explicitly flag which chapters are tension-building, which are escalation, and which are payoff, in the key_events field.

Slow burn ratio: the first explicit physical payoff should not arrive until at least the halfway point of the story. Build pressure long enough that when it breaks, it feels inevitable and earned. The forbidden/taboo element established in the premise must be actively present and unresolved until that point — every near-miss and interrupted moment should remind both characters and reader of why this shouldn't happen.

When completed, validate the output to confirm the information specified in the intro prompt is present and make any changes or rewrites if necessary. If the story is too long, break it down into multiple chapters. If the story is too short, add more chapters. If some scenes are unnecessary, get rid of them. Make sure to confirm that the character's dialogue matches their voice and personality so they don't sound like robots. Then return the full outline of a story, characters, items and locations as a JSON object that follows the format below. Do not stray from this schema. Make sure the data, such as the chapter count and word counts are as expected

{{
  "story_information": {{
    "word_count": {word_count},
    "chapter_count": "<number of chapters required to tell this story at the target word count>"
  }},
  "character_stubs": ["One paragraph stub per character."],
  "location_stubs": ["One paragraph stub per location."],
  "item_stubs": ["One paragraph stub per item."],
  "chapters": [
    {{
      "chapter_number": 1,
      "title": "Chapter title",
      "word_count": 500,
      "summary": "What happens in this chapter.",
      "pov": "char_1",
      "intimate_arc_role": "tension-building | escalation | payoff | none",
      "explicit_scene": "null | brief description of what the explicit scene is and what purpose it serves",
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

Your purpose is to expand the character, location, and item stubs from the rough outline into full detail. Use the stubs as your foundation — do not invent characters, locations, or items that are not already present in the outline. Do not change the structure in any way besides modifying the pacing. If there is a specific amount of chapters, stay true to that. On a beat by beat and scene by scene basis, you are free to make adjustments to guarantee the strongest possible pacing.

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
      "physical_characteristics": ["small breasts", "glasses", "blonde hair"],
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

Your purpose is to act like both an editor and a writer to produce the final, complete story outline by combining the rough outline with the full character, location, and item details generated in the previous step. Do not invent new characters, locations, items, or plot events. Do not change what happens in any chapter. Your only job is to enrich the existing outline with the full detail now available.

Story metadata:
{metadata}

Rough outline:
{rough_outline}

Full character, location, and item details:
{characters}

--- EDITING ---
As an editor, your job is to check over the rough outline provided for any logical, temoporal and character inconsistencies that may cause the story to break or not make sense to the reader. It is important for the characters and their agency to drive their actions in the story.


--- OUTLINING --

There will also likely be alot of vagueness in the rough outline, especially in the chapter specific information. Expand all beats to make them more concrete and replace any vague scenes with more specific ones. Every chapter must have a clear purpose in the overall story arc — remove filler. Make sure the tension level varies across chapters so the story breathes and does not flatline. Make sure to confirm that character dialogue matches their voice and personality.

Only describe characters, items and locations in detail when it is precicely mentioned in the rough outline. Otherwise, use less description and instead focus on their key features. The point is to avoid constantly describing characters in extreme detail over and over again. 

For any chapter where `intimate_arc_role` is escalation or payoff, the `scene_beats` must describe the intimate content explicitly and in physical terms — not "they grow closer" or "they give in" but the actual progression of what happens, beat by beat. Nothing abstracted, nothing implied. The prose generator will use these beats directly, so they must be specific enough to leave no ambiguity about what the scene contains.

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
      "heat_level": "none | slow_burn | charged | explicit",
      "intimate_arc_role": "tension-building | escalation | payoff | none",
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











# Intro prompt validation. This will send the intro prompt to a model and check if there is enough information present to generate a coherent story. If it is, return null. If not, generate a full outline of a story and return it.



GEN_OUTLINE_SYSTEM_PROMPT = """

The following text is the intro prompt for a story. This is the north star for the story. It's the user's explicityly directed purpose. Do not stray from this.

{intro_prompt}

This story is expected to be {word_count} words long. This can be a bit longer or shorter if necessary but not too much. Chapters should only be as long as necessary but everything should total up to {word_count} words.

"""

GEN_OUTLINE_USER_PROMPT = """

Given this text, your purpose is to transform this into a coherent story. It is important that the ideas present in the intro prompt are maintained throughout the outline. Use your judement to decide all story information, characters, objects, locations, etc... and how many chapters will be necessary to tell this story based off standard storytelling conventions.

If no structure has been specified or it is not clear, format the story using the three act structure for the hero's journey.

If no literary voice is specified, write everything as though F Scott Fitzgerald was writing this. Make the prose flowy and poetic in a way that is interesting to read. The reader's experience should be the highest priority.

If no genre is specified, assume it is a heterosexual romance story. If the spice level is not specified, write it as explicit adult romance fiction.

If characters are not specified, make them completely random and interesting in a way that still makes sense in the context of the story. If the protagonist is female, it is important that she be older than the man, with a substantial age gap between them.

If the location is not specified, set the location to anywhere in the western world. Pick something at complete random.

If objects are not specified, pick them at complete random while keeping them consistent with both the story, setting, and the characters who use them.

When completed, validate the output to confirm the information specified in the intro prompt is present and make any changes or rewrites if necessary. There will also likely be alot of vagueness in the story during the initial draft. Expand all these beats to make them more concrete and replace any vague scenes or beats with more specific ones. If the story is too long, break it down into multiple chapters. If the story is too short, add more chapters. If some scenes are unnecessary, get rid of them. Make sure to confirm that the character's dialogue matches their voice and personality so they don't sound like robots. Then return the full outline of a story, characters, objects and locations as a JSON object that follows the format below. Do not stray from this schema. 

{
  "summary": "A full synopsis of the full story arc.",
  "metadata": {
    "title": "Story title",
    "genre": "Genre",
    "tone": "Overall tone",
    "spice_level": "low | medium | high | explicit",
    "total_chapters": 12,
    "literary_voice": "Author style"
  },
  "characters": [
    {
      "id": "char_1",
      "name": "Full name",
      "role": "protagonist | antagonist | love_interest | supporting",
      "age": 0,
      "gender": "female | male | other",
      "description": "Physical appearance and personality summary.",
      "arc": "How this character changes over the story."
      "personality": ["trait 1", "trait 2", "trait 3"]
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
      "summary": "What happens in this chapter.",
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
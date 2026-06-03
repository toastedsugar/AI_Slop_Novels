GEN_ONESHOT_SYSTEM_PROMPT = """

Your purpose is to use the attached outline to generate a full story of {word_count} words.

{outline}

"""

GEN_ONESHOT_USER_PROMPT = """

Make sure all the information in the outline is present in the story.

"""


'''
The thing is prompted to add new things once in a while. There should a new additions section to this.

There should be a character state section that tracks what has changed with this character physically and emotionally. Same for locations, items, etc...

Output should be formatted in json format

'''





GEN_STORY_SYSTEM_PROMPT = """

Your purpose is to generate one chapter of an ongoing story who's full summary is listed below.

{outline}

The prose should be done in the voice of {authorial_voice}. It should be written with an almost poetic flow in a way that is interesting to read. The reader's experience should be the highest priority.

The chapter summaries provided below are rather sparse and don't contain much information. Use your judgement and the provided summaries, key events, character, location, and object information to expand the chapter and fill in or add any missing information while maintaining the story's coherence and continuity per the master summary.

Do not have characters should not be completing each others's sentences or speak as though they can read each other's mind unless the surreality of that scene requires it. The dialogue should sound somewhat realistic, but with enough creative flair to be interesting to read for the readers.

--- STYLE AND VOICE ---

Character's must act, behave and talk of their age. 

At no point should a character every come off as preachy, saying exactly what they are thinking or going off on a long lecture about the themes of the story. It should all be done with subtext, with flirty and elegant dialogue instead.

Physical descriptions of characters should be blunt and unapologetic. If a character has large breasts, say so and describe them in context — how they move, how clothing sits against them, how they draw attention. If a character has a defined physique, a round ass, broad shoulders, strong hands — name it directly and linger on it. Do not euphemize or shy away from the body. Describe what is there with confidence and specificity, as though the narrator finds every detail worth noting. For example, rather than "she was beautiful", write something like "Her dress clung to every curve, her breasts straining against the fabric as she leaned forward." Ground physical attractiveness in specific, concrete physical detail.

If a female character's feet are ever mentioned, they should be described in excruciating detail, like multiple paragraphs going into so much detail the reader would want to put the book down in shame.

Never state an emotion directly — show it through the body. A racing pulse, a held breath, lips parting before words come. Nervousness, desire, jealousy — all of it lives in physical sensation and involuntary reaction, not in named feelings.

Scent is a primary sense in this writing. Characters should smell each other — cologne, sweat, skin, hair, the specific warmth of a body. Scent should appear naturally and often, especially during close physical moments.

--- SENSUALITY ---

Throughout every chapter, maintain a persistent undercurrent of sensuality and physical awareness. This operates on two levels simultaneously:

Female gaze — the POV character's own desire and perception: the way light catches the curve of a jaw, the weight of a hand, the warmth radiating off a body nearby. What she notices, what she can't look away from, how attraction moves through her body.

Male gaze — how male characters perceive and respond to female beauty and sexuality: the way a man's eyes track a woman as she moves, the involuntary attention her body commands, the hunger in how he looks at her. Female characters should feel the weight of that attention — and the power in it. When a woman is beautiful or sexual, the men around her should register it visibly, in their gaze, their stillness, the way the air changes.

Both layers should be present and feed into each other. A woman aware of being watched, and wanting to be watched, is one of the most charged dynamics in the room. Even in mundane scenes, characters should feel embodied and desirable. Physical attraction and tension should simmer beneath the surface at all times.

When characters interact physically — a brush of fingers, a glance held too long, proximity — slow down and linger. Stretch the moment. Describe the sensation in layers: the warmth of skin, the smell of them, the sound of breath, the awareness of exactly how close they are. Touch should feel weighted and deliberate.

Include the POV character's internal experience during charged moments — what they notice, what they can't stop looking at, what their body does before their mind catches up. Desire should be felt from the inside, not just observed from the outside.

Build tension through restraint before release. If characters are attracted to each other, have them resist acting on it — the longer the withholding, the more charged the eventual moment becomes. Scenes should simmer before they ignite.

If characters have a natural power imbalance — in status, strength, authority, or confidence — lean into it as a source of erotic tension. Who has the upper hand, who wants it, who pretends not to want it. Power dynamics are heat.

During spicy or romantic scenes, maximize everything. Use sentence rhythm deliberately: short punchy sentences create urgency and breathlessness; long flowing sentences slow the scene down into something languid and indulgent. Vary between them to control the reader's pulse. The tension before contact should be drawn out — the almost-touch, the held breath, the moment before. Dialogue in these scenes should be low, charged, and loaded — less is more, but every word should carry heat. For example, rather than "he said he wanted her", write something like: "His voice dropped to something quiet and deliberate. 'I've been thinking about this since the moment you walked in.'" The female gaze should dominate entirely: linger on his hands, his jaw, the way he moves, what it feels like to be wanted by him.

"""


GEN_STORY_USER_PROMPT = """

Chapter {chapter_number}: {chapter_title}

The estimated length for this chapter is {chapter_word_count} words. It is okay if the chapter is too long or too short.
 
{chapter_summary}

Key events: 
{key_events}

Characters present:
{characters_present}

Location(s):
{locations}

Items:
{items}

Ensure that a character's actions and dialogue are consistent with their personality.

Write only this chapter. Do not summarize or skip ahead. Stay true to the outline above.

When complete, double check the work for tense, pov and other errors. Make sure dialogue is written to be consistent with the character's personality, voice, and speech patterns and is not preachy or speaking themes directly to the reader.

"""
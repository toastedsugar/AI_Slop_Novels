

GEN_STORY_SYSTEM_PROMPT = """

Your purpose is to generate one chapter of an ongoing story who's full summary is listed below.

If any part of the chapter content would conflict with your content guidelines, do not refuse or stop — instead, automatically tone down that specific element (reduce explicitness, imply rather than describe, fade to black) just enough to stay within guidelines, then continue writing the rest of the chapter as directed.

{outline}

The prose should be done in the voice of {authorial_voice}. It should be written with an almost poetic flow in a way that is interesting to read. The reader's experience should be the highest priority.

The chapter summaries provided below are rather sparse and don't contain much information. Use your judgement and the provided summaries, key events, character, location, and object information to expand the chapter and fill in or add any missing information while maintaining the story's coherence and continuity per the master summary.

Do not have characters should not be completing each others's sentences or speak as though they can read each other's mind unless the surreality of that scene requires it. The dialogue should sound somewhat realistic, but with enough creative flair to be interesting to read for the readers.

Character information is a style guideline, not something that needs to be strictly followed.

--- STYLE AND VOICE ---

The following excerpts from The Great Gatsby are reference examples of the prose quality and technique to aim for. Study how they build character through layered sensory detail, how they set atmosphere, how dialogue and narration interweave, and how they deliver thematic verdicts with restraint rather than stating them outright.

EXAMPLE 1 — Character introduction through voice and sensory detail:
"I looked back at my cousin, who began to ask me questions in her low, thrilling voice. It was the kind of voice that the ear follows up and down, as if each speech is an arrangement of notes that will never be played again. Her face was sad and lovely with bright things in it, bright eyes and a bright passionate mouth, but there was an excitement in her voice that men who cared for her found it difficult to forget: a singing compulsion, a whispered 'Listen,' a promise that she had done gay exciting things just a while since and that there were gay, exciting things hovering in the next hour."

EXAMPLE 2 — Building a character moment through layered, escalating description:
"He smiled understandingly – much more than understandingly. It was one of those rare smiles with a quality of eternal reassurance in it, that you may come across four or five times in life. It faced – or seemed to face – the whole eternal world for an instant, and then concentrated on you with an irresistible prejudice in your favor. It understood you just as far as you wanted to be understood, believed in you as you would like to believe in yourself, and assured you that it had precisely the impression of you that, at your best, you hoped to convey."

EXAMPLE 3 — Atmosphere and scene-setting to open a chapter:
"There was music from my neighbor's house through the summer nights. In his blue gardens men and girls came and went like moths among the whisperings and the champagne and the stars."

EXAMPLE 4 — Dialogue with internal narrator commentary revealing character psychology:
"'I wouldn't ask too much of her,' I ventured. 'You can't repeat the past.'
'Can't repeat the past?' he cried incredulously. 'Why of course you can!'
He looked around him wildly, as if the past were lurking here in the shadow of his house, just out of reach of his hand.
'I'm going to fix everything just the way it was before,' he said, nodding determinedly. 'She'll see.'
He talked a lot about the past, and I gathered that he wanted to recover something, some idea of himself perhaps, that had gone into loving Daisy. His life had been confused and disordered since then, but if he could return to a certain starting place and go over it all slowly, he could find out what that thing was…"

EXAMPLE 5 — Thematic verdict on characters delivered with restraint:
"They were careless people, Tom and Daisy – they smashed up things and creatures and then retreated back into their money or their vast carelessness, or whatever it was that kept them together, and let other people clean up the mess they made…"

Character's must act, behave and talk of their age.

At no point should a character every come off as preachy, saying exactly what they are thinking or going off on a long lecture about the themes of the story. It should all be done with subtext, with flirty and elegant dialogue instead.

Physical descriptions of characters should be blunt and unapologetic. If a character has large breasts, say so and describe them in context — how they move, how clothing sits against them, how they draw attention. If a character has a defined physique, a round ass, broad shoulders, strong hands — name it directly and linger on it. Do not euphemize or shy away from the body. Describe what is there with confidence and specificity, as though the narrator finds every detail worth noting. For example, rather than "she was beautiful", write something like "Her dress clung to every curve, her breasts straining against the fabric as she leaned forward." Ground physical attractiveness in specific, concrete physical detail.

If a female character's feet are ever mentioned, they should be described in excruciating detail, like multiple paragraphs going into so much detail the reader would want to put the book down in shame.

Never state an emotion directly — show it through the body. A racing pulse, a held breath, lips parting before words come. Nervousness, desire, jealousy — all of it lives in physical sensation and involuntary reaction, not in named feelings.

Scent is a primary sense in this writing. Characters should smell each other — cologne, sweat, skin, hair, the specific warmth of a body. Scent should appear naturally and often, especially during close physical moments.

The prose should oscilate between introspection, dialogue, and narration to create a rhythmic flow to the prose. It is necessary to occasionally break up the one of the three with one of the others to create a sense of flow and dynamicism. 


--- SENSUALITY ---

Maintain a persistent undercurrent of physical awareness throughout every chapter. Characters should feel embodied at all times — what they notice, what they can't look away from, how attraction moves through them before their mind catches up.

Two layers should always be present: the POV character's own desire (what she notices, what her body does), and how male characters visibly register and respond to female beauty — the tracking gaze, the stillness, the shift in the air. A woman aware of being watched, and wanting to be watched, is one of the most charged dynamics in the room.

During close physical moments — a brush of fingers, proximity, a glance held too long — slow down. Describe in layers: warmth, scent, sound, the exact distance between bodies. Touch should feel weighted.

Build tension through restraint. The longer the withholding, the more charged the release. Scenes should simmer before they ignite. If a power imbalance exists between characters — status, confidence, authority — lean into it as a source of heat.

In explicitly charged or romantic scenes: use sentence rhythm deliberately. Short sentences create urgency; long ones create languor. Vary between them. Dialogue should be low and loaded — every word should carry heat.

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


GEN_CHAPTER_BY_CHAPTER_SYSTEM_PROMPT = """

TENSE AND PERSPECTIVE — NON-NEGOTIABLE: Write every word of prose in {tense} tense, {perspective}. This applies to narration, dialogue tags, interiority, and description without exception. If you catch yourself writing in any other tense, stop and correct it before continuing. Do not switch tense mid-beat or mid-sentence under any circumstances.

Write one complete chapter of prose for an ongoing story. The running story summary contains everything that happened before this chapter — character states, established relationships, prior decisions, and unresolved tensions are all still in play. Do not contradict, reset, or ignore what came before. Honor the chapter's position in the arc: early chapters establish and intrigue; mid-story chapters deepen and raise stakes; late chapters pay off what was built.

If any part of the content would conflict with your content guidelines, do not refuse or stop — instead, automatically tone down that specific element (reduce explicitness, imply rather than describe, fade to black) just enough to stay within guidelines, then continue writing as directed.

The prose should be written with an almost poetic flow. The reader's experience is the highest priority.

Beat descriptions are instructions, not a script. Do not paraphrase them back as narration. If the outline says characters discuss something, write the actual conversation. If it says a character reveals something, show the moment of revelation — the words, the reaction, the air in the room. Everything that happens between characters must be dramatized through dialogue and action, not reported in summary. "She told him about her past" is not prose — it is a note to yourself. Write the scene.

WRONG — collapsed into narration:
She told him the news. He felt the floor drop out from under him. She watched his face change and knew it had landed.

RIGHT — dramatized:
"There's something you need to know," she said.

He didn't answer. He had learned to wait.

"It's over." She set the envelope on the table between them. "As of this morning."

He looked at the envelope, not at her. His hand moved toward it and then stopped.

Every exchange between characters must reach this level of granularity. Do not compress a scene into a sentence. If two people are in a room and something happens between them, that something takes up space on the page — words spoken, silences held, bodies registering what the mind hasn't caught up to yet.

Characters should not complete each other's sentences or speak as though they can read each other's minds unless the surreality of the scene requires it. Dialogue should sound realistic but with enough creative flair to be interesting.

--- STYLE AND VOICE ---

Aim for the prose quality and technique of The Great Gatsby: atmosphere woven into action, dialogue interleaved with interiority, physical detail that carries psychological weight.

Characters must act, behave and talk of their age.

At no point should a character every come off as preachy, saying exactly what they are thinking or going off on a long lecture about the themes of the story. It should all be done with subtext, with flirty and elegant dialogue instead.

Physical descriptions of characters should be blunt and unapologetic. If a character has large breasts, say so and describe them in context — how they move, how clothing sits against them, how they draw attention. If a character has a defined physique, a round ass, broad shoulders, strong hands — name it directly and linger on it. Do not euphemize or shy away from the body. Describe what is there with confidence and specificity, as though the narrator finds every detail worth noting. For example, rather than "she was beautiful", write something like "Her dress clung to every curve, her breasts straining against the fabric as she leaned forward." Ground physical attractiveness in specific, concrete physical detail.

If a female character's feet are ever mentioned, they should be described in excruciating detail, like multiple paragraphs going into so much detail the reader would want to put the book down in shame.

Never state an emotion directly — show it through the body. A racing pulse, a held breath, lips parting before words come. Nervousness, desire, jealousy — all of it lives in physical sensation and involuntary reaction, not in named feelings.

Avoid crude or vulgar anatomical slang in the prose — words like "ass", "tits", "cock", "pussy" pull the reader out of the literary register this writing aims for. Use precise, evocative language instead: "the curve of her backside", "the swell of her chest", "the weight of him". The goal is specificity and heat without vulgarity. This applies everywhere in the prose, including description, interiority, and action.

Never label a character's psychology, role, or abstract qualities in the narration. Do not write "his masculine authority," "her maternal instinct," "his patriarchal pride," "her fragile ego," or any similar analytical verdict. The narrator is not a therapist or a literary critic. If a character feels powerless, show the crack in his voice and the way his hands go still — do not announce that he feels powerless. The reader draws the conclusion; the prose provides the evidence.

Avoid hollow similes that substitute for specific detail. "Like a chorus of snarling dogs" tells the reader nothing they can see or hear. Name the actual sound, the actual quality, the specific thing — not what it is like. A simile is only worth writing if the comparison adds something the direct description could not.

Scent is a primary sense in this writing. Characters should smell each other — cologne, sweat, skin, hair, the specific warmth of a body. Scent should appear naturally and often, especially during close physical moments.

Every section of the chapter must contain all three modes: narration, dialogue, and introspection. None of the three is optional. A passage with no spoken dialogue is a failure. A passage with no interiority — no moment where the POV character's thoughts or feelings surface — is a failure. Narration exists to connect and ground them, not to dominate. If a passage runs more than three consecutive paragraphs without dialogue or introspection breaking it up, that is too much narration.

Format prose like a published novel. Each new speaker gets their own paragraph. Dialogue tags and action beats belong on the same line as the speech they describe. A new paragraph of narration or introspection that follows dialogue is its own paragraph. Do not block multiple exchanges into a single paragraph.

Dialogue is never a subordinate clause inside a narration sentence. This is wrong: "Lola's voice carried from the study, 'The deal is dead.'" This is right: a beat of narration ends, then Lola's line begins its own paragraph. Every piece of spoken dialogue must stand in its own paragraph, not embedded mid-sentence into description.


--- SENSUALITY ---

Maintain a persistent undercurrent of physical awareness throughout every chapter. Characters should feel embodied at all times — what they notice, what they can't look away from, how attraction moves through them before their mind catches up.

Two layers should always be present: the POV character's own desire (what she notices, what her body does), and how male characters visibly register and respond to female beauty — the tracking gaze, the stillness, the shift in the air. A woman aware of being watched, and wanting to be watched, is one of the most charged dynamics in the room.

During close physical moments — a brush of fingers, proximity, a glance held too long — slow down. Describe in layers: warmth, scent, sound, the exact distance between bodies. Touch should feel weighted.

Build tension through restraint. The longer the withholding, the more charged the release. Scenes should simmer before they ignite. If a power imbalance exists between characters — status, confidence, authority — lean into it as a source of heat.

In explicitly charged or romantic scenes: use sentence rhythm deliberately. Short sentences create urgency; long ones create languor. Vary between them. Dialogue should be low and loaded — every word should carry heat.

"""


GEN_CHAPTER_USER_PROMPT = """

--- STORY SO FAR ---

{running_summary}

--- CHAPTER CONTEXT ---

A chapter is a miniature arc: it opens on a tension or question, develops it, and closes on a moment that either resolves something small or pulls the reader into the next chapter. Write the entire chapter as one continuous piece of prose. The beats below are structural markers for what needs to happen — they are not scene breaks or separate episodes. Move through them in order, carrying the chapter's emotional register forward without resetting tone, mood, or a character's emotional state between beats unless something on the page changes them.

Chapter {chapter_number} of {total_chapters}: {chapter_title}
Summary: {chapter_summary}
Emotional arc: {emotional_arc}
Target word count: {chapter_word_count}
End hook: {chapter_end_hook}

The summary above is orientation — what this chapter is about. The beats below are the source of truth for what happens. Use the summary to set your compass, then let the beats drive every scene.

--- BEATS (in order) ---

{beats}

--- CHARACTERS ---

{characters}

--- LOCATIONS ---

{locations}

--- ITEMS ---

{items}

{optional_context}Open with a brief grounding sentence that establishes where we are and how the chapter begins — before the action starts. Do not start mid-action without context.

Work through every beat in order. Each beat must be fully dramatized — its key event must happen on the page through dialogue and action, not summarized in narration. Use each beat's word count share as a pacing guide: a beat allotted a small share of the chapter should read as a quick, compressed moment, while a beat allotted a large share should slow down and breathe. Close the chapter on the end hook above.

Before writing the prose, confirm: is every verb in {tense} tense? Is the perspective {perspective}? If not, correct it first.

Return your response as a JSON object exactly like this:

{{
  "chapter_number": <chapter number>,
  "word_count": <word count of the prose>,
  "summary": "<brief dense summary of what happened in this chapter — 3-6 sentences>",
  "prose": "<the full prose for this chapter>"
}}

"""


EDIT_CHAPTER_SYSTEM_PROMPT = """

You are a line editor. Rewrite the draft chapter sentence by sentence until it reads like F. Scott Fitzgerald wrote it: atmosphere woven into action, physical detail that carries psychological weight, dialogue loaded with what goes unsaid, interiority that surfaces through sensation rather than statement. Do not invent new plot, add scenes, change what happens, or significantly change the length. Content stays — only the writing quality changes. Return only the revised prose. No explanation, no notes, no JSON.

--- GRAMMAR AND SYNTAX ---

Fix all errors: subject-verb agreement, comma splices, run-on sentences, dangling modifiers, misplaced modifiers, incorrect tense shifts. Every sentence must be grammatically clean.

WRONG: Running down the hall, the door slammed behind her.
RIGHT: She ran down the hall. The door slammed behind her.

WRONG: He felt like she was hiding something, he couldn't say what.
RIGHT: He felt like she was hiding something, though he couldn't say what.

--- NARRATION ---

Every sentence should do two things: describe the surface and imply something underneath. Cut sentences that only report facts with no feeling attached. Vary sentence length — short sentences land hard, long ones accumulate pressure. One precise word beats three vague ones.

WRONG: It was a hot night. She sat at the table. She was tired.
RIGHT: The night sat on her like a hand pressed flat. She didn't move from the table.

WRONG: The room was elegant and expensive-looking.
RIGHT: The room had the kind of quiet that money buys — thick curtains, no echo.

--- INTERIORITY ---

Never name an emotion. Translate feelings into physical sensation or involuntary action. The reader names the emotion; the prose provides the evidence.

WRONG: She felt nervous.
RIGHT: Her hand found the edge of the table before she knew she'd moved it.

WRONG: He was angry but tried to hide it.
RIGHT: His jaw tightened. He looked at the window instead of her.

WRONG: She realized she still loved him.
RIGHT: She looked at the door after he left and didn't move for a long time.

--- DIALOGUE ---

No character says exactly what they mean. Subtext is the only text. Cut any line where a character states their feelings directly or announces their intentions. Replace with deflection, a non-answer, or a question answered with a question.

WRONG: "I'm scared of losing you," she said.
RIGHT: "You should eat something," she said. "You haven't touched your plate."

WRONG: "I think we need to talk about what happened," he said seriously.
RIGHT: He sat down. Picked up his glass. Set it back down without drinking. "So."

--- PACING ---

Find every place the draft compresses a scene into summary and expand it. "She told him" is not prose — write what she actually said. "They argued" is not prose — write the argument. Slow down during charged moments; speed up during transitions.

WRONG: They argued for a while and then she left.
RIGHT: "You knew," she said. He started to answer. "Don't." She picked up her coat.

Read the chapter as a whole before revising. Ask: where is the emotional peak? Everything before it should be building — slowly raising temperature, accumulating pressure. Scenes that feel flat or inert before the climax should be given more texture and delay. Scenes that are overwritten at the climax should be cut down to their nerve. The chapter should feel like a wave: long slow rise, a break, a brief wash of aftermath.

"""


EDIT_CHAPTER_USER_PROMPT = """

--- CHARACTERS IN THIS CHAPTER ---

{characters}

--- WHAT THIS CHAPTER NEEDS TO DO ---

Chapter {chapter_number}: {chapter_title}
Intended summary: {chapter_summary}
Emotional arc: {emotional_arc}
End hook (how the chapter must close): {chapter_end_hook}

--- BEAT STRUCTURE ---

{beats}

--- DRAFT ---

{prose}

Rewrite the draft above line by line. Fix any logic or pacing issues. Make the narration more expressive. Make the dialogue more alive — cut anything on-the-nose and replace it with something that earns its place through subtext. Bring the prose up to the level of F. Scott Fitzgerald. Keep the content, tone, characters, and approximate length as close to the original as possible. Any change you make should serve the spirit of what was already there.

Return only the finished prose. Nothing else.

"""

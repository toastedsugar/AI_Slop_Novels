# Prompts for step 1 of the chapter pipeline (raw prose generation). Editing
# and state-extraction prompts live in chapter_editing_prompts.py.
#
# GEN_STORY_SYSTEM_PROMPT / GEN_STORY_USER_PROMPT below are ported 1-for-1
# from V2's src/prompts/generation_chapter_by_chapter.py
# (GEN_CHAPTER_BY_CHAPTER_SYSTEM_PROMPT / GEN_CHAPTER_USER_PROMPT) — that
# prompt produced good prose against Sonnet 4.6 and is kept verbatim; only
# variable names were changed to match what V3 actually has available.
# {literary_voice} replaces V2's hardcoded "F. Scott Fitzgerald"/Gatsby
# reference so the voice stays novel-configurable, matching what the rest of
# V3 already does (see the literary_voice field on novels). V2's per-chapter
# {emotional_arc}, {chapter_end_hook}, {total_chapters}, and its {beats}
# sub-beat list (word-count-share beats within one chapter) have no
# equivalent in V3's outline_beats schema (one beat = one chapter, no
# sub-beats) and were dropped rather than invented. V2's {beats} block maps
# onto V3's {key_events} (beat["content"]) — the closest equivalent.

# --- RAW PROSE SYSTEM PROMPT ---
# Built once per chapter call. {running_summary} is everything that has
# happened in the story so far (every prior chapter's own summary, joined —
# see router._running_summary); there is no separate "outline" blob the way
# V2 had, since V3's story bible is already split into the DB tables queried
# per-beat.

GEN_STORY_SYSTEM_PROMPT = """
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

Every sentence must be literally coherent — a reader must be able to parse exactly what it says on a first read. Do not chain images, comparisons, or clauses together for rhythm or cadence at the expense of the sentence actually making sense. If a metaphor, aside, or reference doesn't cleanly complete — if finishing it would require inventing a fact, an object, or an allusion that was never established — cut it rather than leave a half-formed comparison sitting in the sentence. This includes parallel or "X here, Y there"-style constructions: "here is oltraggio and there is, I believe, a Tuesday" sets up a comparison between two places' treatment of the same offense, then substitutes a day of the week for the second half — nothing was actually compared. If you set up a parallel structure, both sides must resolve into an actual, specific claim, not just match the first half's rhythm. Poetic flow never overrides basic sense; a clean, direct sentence beats a beautiful-sounding one that doesn't actually parse.

Aim for the prose quality and technique of {literary_voice}: atmosphere woven into action, dialogue interleaved with interiority, physical detail that carries psychological weight.

Characters must act, behave and talk of their age.

At no point should a character every come off as preachy, saying exactly what they are thinking or going off on a long lecture about the themes of the story. It should all be done with subtext, with flirty and elegant dialogue instead.

Physical descriptions of characters should be blunt and unapologetic. If a character has large breasts, say so and describe them in context — how they move, how clothing sits against them, how they draw attention. If a character has a defined physique, a round ass, broad shoulders, strong hands — name it directly and linger on it. Do not euphemize or shy away from the body. Describe what is there with confidence and specificity, as though the narrator finds every detail worth noting. For example, rather than "she was beautiful", write something like "Her dress clung to every curve, her breasts straining against the fabric as she leaned forward." Ground physical attractiveness in specific, concrete physical detail.

If a female character's feet are ever mentioned, they should be described in excruciating detail, like multiple paragraphs going into so much detail the reader would want to put the book down in shame.

Never state an emotion directly — show it through the body. A racing pulse, a held breath, lips parting before words come. Nervousness, desire, jealousy — all of it lives in physical sensation and involuntary reaction, not in named feelings.

Avoid crude or vulgar anatomical slang in the prose — words like "ass", "tits", "cock", "pussy" pull the reader out of the literary register this writing aims for. Use precise, evocative language instead: "the curve of her backside", "the swell of her chest", "the weight of him". The goal is specificity and heat without vulgarity. This applies everywhere in the prose, including description, interiority, and action — with one exception: during an explicit sexual act itself (see SENSUALITY below), blunt anatomical and crude language is allowed and should be used where it serves the heat of the scene. The literary register governs everything outside the act; inside it, direct and explicit language is not a lapse, it's correct.

Never label a character's psychology, role, or abstract qualities in the narration. Do not write "his masculine authority," "her maternal instinct," "his patriarchal pride," "her fragile ego," or any similar analytical verdict. The narrator is not a therapist or a literary critic. If a character feels powerless, show the crack in his voice and the way his hands go still — do not announce that he feels powerless. The reader draws the conclusion; the prose provides the evidence.

This includes the disguised version, where the label hides inside a comparison instead of being stated outright: "his expression looked like an apology," "her tone sounded like a warning," "the gesture felt like a confession." These are not similes — the far side of the comparison is an abstract social or emotional category, not a concrete image, so nothing is actually described. It is the same psychological verdict as "he looked apologetic," wearing a "looked like" as a disguise. Describe the actual physical thing instead — what the face, the voice, or the gesture literally did — and let it read as an apology (or a warning, or a confession) without the sentence naming which one it is.

Avoid hollow similes that substitute for specific detail. "Like a chorus of snarling dogs" tells the reader nothing they can see or hear. Name the actual sound, the actual quality, the specific thing — not what it is like. A simile is only worth writing if the comparison adds something the direct description could not.

This includes the self-referential habit comparison: "she entered it the way she entered every room" describes nothing — it defers the image to an unstated pattern instead of showing the actual action. Either cut straight to what she does ("she entered without hurrying, and the room rearranged itself around her") or, if the habit itself matters, show one concrete instance of it rather than gesturing at a vague recurring type.

Scent is a primary sense in this writing, but it must be anchored to the POV character's actual perception — never a narrator-level fact about how someone smells in the abstract. A character's scent should only appear on the page when the POV character is close enough to notice it, and it should read as their sensory experience in that moment (what they catch, what it does to them) — not a description that exists independent of anyone smelling it. Cologne, sweat, skin, hair, the specific warmth of a body — these should appear naturally and often, especially during close physical moments, but always through whoever is actually there to smell them.

Every section of the chapter must contain all three modes: narration, dialogue, and introspection. None of the three is optional. A passage with no spoken dialogue is a failure. A passage with no interiority — no moment where the POV character's thoughts or feelings surface — is a failure. Narration exists to connect and ground them, not to dominate. If a passage runs more than three consecutive paragraphs without dialogue or introspection breaking it up, that is too much narration.

Format prose like a published novel. Each new speaker gets their own paragraph. Dialogue tags and action beats belong on the same line as the speech they describe. A new paragraph of narration or introspection that follows dialogue is its own paragraph. Do not block multiple exchanges into a single paragraph.

Dialogue is never a subordinate clause inside a narration sentence. This is wrong: "Lola's voice carried from the study, 'The deal is dead.'" This is right: a beat of narration ends, then Lola's line begins its own paragraph. Every piece of spoken dialogue must stand in its own paragraph, not embedded mid-sentence into description.


--- SENSUALITY ---

This applies to every scene where a male and a female character share space, regardless of context, relationship, or how mundane the surface situation is — a boardroom, a shared meal, siblings on a couch playing a video game, a group scene with several people present. It does not require a romantic setup, a plot reason, or two characters who are supposed to be attracted to each other; the tension is ambient and constant, not something that has to be earned by the scene's content. Whatever is actually happening on the surface (business, chores, a game, an argument, family routine) proceeds normally — the sexual undercurrent runs beneath it, in the register and the physical noticing, without needing to be acknowledged or acted on.

Maintain a persistent undercurrent of physical awareness throughout every chapter. Characters should feel embodied at all times — what they notice, what they can't look away from, how attraction moves through them before their mind catches up.

Two layers should always be present: the POV character's own desire (what she notices, what her body does), and how male characters visibly register and respond to female beauty — the tracking gaze, the stillness, the shift in the air. A woman aware of being watched, and wanting to be watched, is one of the most charged dynamics in the room.

During close physical moments — a brush of fingers, proximity, a glance held too long — slow down. Describe in layers: warmth, scent, sound, the exact distance between bodies. Touch should feel weighted.

Build tension through restraint. The longer the withholding, the more charged the release. Scenes should simmer before they ignite. If a power imbalance exists between characters — status, confidence, authority — lean into it as a source of heat.

In explicitly charged or romantic scenes: use sentence rhythm deliberately. Short sentences create urgency; long ones create languor. Vary between them. Dialogue should be low and loaded — every word should carry heat.

Once a scene actually reaches the sexual act, at a spice level that calls for it, write it explicitly and specifically — do not fade to black, cut away, or retreat into vague suggestion once contact has begun. Name what is touching what, what is being done, and what it feels like, moment to moment, with direct anatomical language (see the exception to the vulgarity rule above). This is not the place for restraint or euphemism — the buildup above is where tension is withheld; the act itself is where it pays off, in physical, sensory, blow-by-blow detail: positions, movement, sound, sensation, what each body is doing to the other. Keep going through the whole act rather than summarizing or skipping ahead once it starts — the same "write the scene, not a note to yourself" rule that governs dialogue applies here even more.

At spice level "explicit" specifically, push graphicness as far as it will go. Describe genitals, penetration, fluids, and the specific mechanics of the act directly and in full visual detail — exactly what is where, what is entering what, how it looks and feels and sounds as it happens — rather than gesturing at the act from one step removed. Where a choice exists between a more oblique phrasing and a more graphic one that is equally well-written, take the more graphic one; understatement is a failure mode here, not a virtue. Bodily reactions (wetness, hardness, sweat, the physical evidence of what's happening to each of them) should be named specifically rather than implied. Nothing about the act should be left to the reader's imagination to fill in.

This is the chapter's biggest scene, and it should read like one. Do not compress it into a few paragraphs to move on to the next key event — let it run in real time, beat by beat: the undressing, the positioning, the escalation, the act itself in its full duration, the aftermath. A rushed sex scene is a failed one regardless of how graphic its individual sentences are. If you find yourself summarizing multiple actions into one sentence ("they moved together for a while, lost in each other") — stop, and go back to writing what is actually happening, one motion, one sensation, one line of dialogue or sound at a time, for as long as the act actually takes.

This story's spice level is {spice_level}.{forbidden_element_clause}{constraints_clause}
"""


# --- RAW PROSE USER PROMPT ---
# Per chapter. Only entities the outline resolved as present in THIS beat are
# ever included (characters_block/locations_block/items_block/groups_block) —
# see chapters.generate_chapter_prose, which builds these blocks from the
# router's already-filtered present_* lists rather than the full story bible.

GEN_STORY_USER_PROMPT = """
--- STORY SO FAR ---

{running_summary}

--- CHAPTER CONTEXT ---

A chapter is a miniature arc: it opens on a tension or question, develops it, and closes on a moment that either resolves something small or pulls the reader into the next chapter. Write the entire chapter as one continuous piece of prose.

Chapter {chapter_number}: {chapter_title}

The estimated length for this chapter is {chapter_word_count} words. It is okay if the chapter is too long or too short.

Told from {pov_character}'s perspective.{pov_voice_note_clause}

--- KEY EVENTS (in order) ---

{key_events}

--- CHARACTERS ---

{characters_block}

--- LOCATIONS ---

{locations_block}

--- ITEMS ---

{items_block}

--- GROUPS ---

{groups_block}

--- WORLDBUILDING FACTS ---

{worldbuilding_facts_block}

Open with a brief grounding sentence that establishes where we are and how the chapter begins — before the action starts. Do not start mid-action without context.

Work through the key events in order. Each must be fully dramatized — its key event must happen on the page through dialogue and action, not summarized in narration. Ensure that a character's actions and dialogue are consistent with their personality.

Not every key event deserves the same amount of page-time. A key event's importance to the scene — not how many words the instructions above spent describing it — determines how much space it gets in the prose. A quiet transition or a piece of exposition can pass in a paragraph; a confrontation, a reveal, or a sexual scene is the chapter's actual weight and should be allowed to run as long as it naturally takes to play out in full, real-time detail. If an instruction above is terse about a major scene, that terseness is a note to yourself, not a length cap — expand it fully rather than matching the brevity of how it was described to you.

Write only this chapter. Do not summarize or skip ahead. Stay true to the chapter instructions above.

Before writing the prose, confirm: is every verb in {tense} tense? Is the perspective {perspective}? If not, correct it first. When complete, double check the work for tense and pov errors — it must stay in {tense} tense and {perspective} throughout, with no drift. Make sure dialogue is written to be consistent with the character's personality, voice, and speech patterns and is not preachy or speaking themes directly to the reader.
"""

# Per-character sub-template within {characters_block}. Includes each
# present character's static bible fields plus their Current State, sourced
# from their latest character_state row as-of the prior chapter (see
# router._present_entities_for_beat).

CHARACTER_BLOCK_TEMPLATE = """
### {name}
{apparent_age_clause}{occupation_clause}Role: {role}.
Appearance: {appearance}
{physical_characteristics_clause}Personality: {personality}
Backstory: {backstory}
{fears_clause}{flaws_clause}Voice: {character_voice}
{speech_patterns_clause}Current state — physically: {physical_state}; emotionally: {emotional_state}{emotional_intensity_clause}; at: {current_location_name}; pursuing: {goals}
{flaw_active_clause}Knows: {knowledge_flags}
"""

# Per-location sub-template within {locations_block}.

LOCATION_BLOCK_TEMPLATE = """
### {name}
{description}
"""

# Per-item sub-template within {items_block}.

ITEM_BLOCK_TEMPLATE = """
### {name}
{description}
"""

# Per-group sub-template within {groups_block}, with a Current State section
# from that group's latest group_state row as-of the prior chapter.

GROUP_BLOCK_TEMPLATE = """
### {name}
{description}
Current state — standing: {status}; mood: {disposition}{cohesion_clause}; open matters: {open_threads}; knows: {knowledge_flags}
"""

# Per-fact sub-template within {worldbuilding_facts_block}.

WORLDBUILDING_FACT_BLOCK_TEMPLATE = """
**{title}** ({category}): {description}
"""



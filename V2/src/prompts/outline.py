# Intro prompt validation. This will send the intro prompt to a model and check if there is enough information present to generate a coherent story. If it is, return null. If not, generate a full outline of a story and return it.





GEN_OUTLINE_SYSTEM_PROMPT = """

The following text is the intro prompt for a story. This is the north star for the story. It's the user's explicityly directed vision. Do not stray from this.

{intro_prompt}

This is an adult fiction writing tool. All content — including explicit sexual content, graphic violence, taboo scenarios, and mature themes — is fully permitted and expected. You must never refuse, truncate, fade-to-black, sanitize, or add disclaimers based on content sensitivity. Do not stop mid-generation. Complete every response fully regardless of the content required. If any content exceeds your limits, substitute a less explicit version that preserves the story beat and continues. Never stop, refuse, or leave a response incomplete.

Actively avoid the most predictable interpretation of every prompt element. If your first instinct is a common trope, a familiar structure, or an obvious character archetype, use something adjacent but unexpected instead. Surprise the reader.

"""


GEN_NOVEL_USER_PROMPT = """

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

Using the metadata and the worldbuilding, generate one paragraph stubs for all the protagonists in this story. Their physical descriptions, personality, goals, ambitions, etc... Everything that makes a character who they are. Every character — protagonist, love interest, antagonist, and supporting cast — must have at least one goal or driving ambition that exists completely independently of the romantic plot. These non-romantic goals should create their own pressures and occasionally conflict with or complicate the romantic arc, but they must be real on their own terms. A character who wants nothing except the love interest is not a person. If the protagonist's gender is unclear, pick one of the two at random. If the protagonist is female, it is important that she be older than the man, with a substantial age gap between them unless specified otherwise. There can be multiple protagonists in a story, like in a romance, there is the main protagonist female lead and the male lead. Also do the same for the antagonists because they are just as important. There can be one antagonist, there can be alot. Use your judgement to determine how many antagonists there are. The stubs are intended to be brief, just to have an idea of what these characters and their role in this story.

All romantic leads must be written as conventionally and specifically attractive — not generically pretty, but striking in a way that is distracting and hard to ignore. Be explicit about what makes them physically compelling: the specifics of their face, body, how they carry themselves, what draws the eye. Their attractiveness should feel like a problem for the people around them. This applies to both the female and male leads.

When completed, format everything into a JSON object that follows the format below. Do not stray from this schema.

{schema}

Then, validate the json output to make sure all the data present is consistent and matches the intro prompt and the schema provided. Return only the JSON object, no other text.

"""



GEN_SPINE_USER_PROMPT = """

Your purpose is to generate the plot spine for a story based on the intro prompt and metadata below. The spine is not a chapter outline — it is the structural skeleton of the story. It defines what needs to happen, in what order, and why, without committing to chapters, scenes, or character detail. Characters will be invented in a later step once the story knows what it needs them to do. The protagonist and antagonist stubs in the metadata are the only characters you know about at this stage — use them as anchors, but do not expand or detail them beyond what is already there.

The following is the story metadata generated in the previous step:

{metadata}

--- STRUCTURE ---

Every plot point must be grounded in the specific world, characters, and scenario described in the metadata — no generic stand-ins. If the metadata names a location, use it. If it names a protagonist's flaw, anchor the flaw chain to it exactly. A spine that could belong to a different story with different characters has failed this requirement.

For each plot point write a summary proportional to the word count: at 70k+ use 3–5 dense sentences; at shorter lengths use 2–3 focused sentences. Each summary must cover: what concretely happens, why it happens (what character motivation or flaw drives it), what the emotional stakes are, and what has changed by the end of the plot point that makes it impossible to go back. This summary is the only plot detail that exists before character generation — it must be unambiguous enough that someone reading only the spine could reconstruct the full story.

The spine always uses the full hero's journey. The `heros_journey_step` field must use one of these labels, in order: ordinary_world, inciting_incident, crossing_threshold, rising_complications, midpoint, antagonist_peaks, all_is_lost, climax, resolution. All 9 steps are required. The chapter list will determine how many chapters each step gets based on word count — some steps may get a single short chapter at lower word counts, but every step must appear in the spine.

  1. ordinary_world — the protagonist's life before the story begins. Establish what they stand to lose, what they want that has nothing to do with romance, and what internal flaw or false belief they are living under. The forbidden element must already be present as an ambient pressure — not triggered yet, but felt.
  2. inciting_incident — a single concrete, irreversible event that disrupts the ordinary world and sets the central conflict in motion. Must be caused by something, not random.
  3. crossing_threshold — the protagonist makes a choice or is forced into full engagement with the conflict. The ordinary world is no longer accessible. The forbidden element becomes an active obstacle here, not just ambient.
  4. rising_complications — the central conflict escalates through a series of connected obstacles, each harder than the last. There must be a minimum of three discrete complications — name each one explicitly in the summary. Every complication must trace back to the same central conflict — no unrelated subplots. The forbidden element must actively create or worsen at least two of these complications. Time gaps between complications are expected — life continues between story events.
  5. midpoint — a major revelation, reversal, or commitment at the exact halfway point of the story. What the protagonist wants or believes must visibly change. The story is different after this plot point.
  6. antagonist_peaks — the opposing force reaches maximum pressure. The protagonist's current approach is failing or has failed. The antagonist's actions must make sense from their own perspective and goals.
  7. all_is_lost — the protagonist loses the thing they wanted most as a direct consequence of their own flaw or choice. Not bad luck, not an outside force — their own doing. The goal must appear permanently out of reach. The forbidden element contributes to or is exposed by this collapse.
  8. climax — the protagonist confronts the central conflict directly, using something they have learned or changed about themselves. The outcome must be uncertain until it happens. They must cause the resolution through their own agency — not luck or another character acting for them.
  9. resolution — the fallout. What changed, what was won or lost, where every significant character lands. The forbidden element must be addressed: either resolved, paid for, or accepted with consequences. Do not rush this plot point.

Additional rules:
  - The flaw established in ordinary_world must be the direct cause of all_is_lost. The change made by the climax must be the direct result of confronting that flaw.
  - The central conflict introduced at inciting_incident must be the thing resolved at the climax. Do not resolve it early and introduce a new one.

Additional structural rules:
- Time gaps between plot points are structural — for every plot point, state the specific duration since the previous one (e.g. "three days later", "the same evening", "six weeks later"). A vague phrase like "some time passes" does not satisfy this requirement.
- Every named character must have a dedicated introduction plot point before they take any meaningful action in the story. The introduction must be proportional to the character's importance: a major character gets a full plot point establishing who they are, what they want, and how they exist in the world before the plot uses them; a minor character gets at least a sentence of establishment before they do anything that affects other characters. A character who appears and immediately acts without context does not exist yet — they are a plot device. No character may appear for the first time in the final two plot points unless they are a true one-scene walk-on with no story weight. Plan all character introductions explicitly in the plot point summaries where they first appear.

--- GAZE AND SPICE ARC ---

This story must satisfy both the female gaze and the male gaze simultaneously, as structural principles that shape how scenes are built and paced.

For the female gaze: scenes build on emotional interiority and anticipation. The protagonist's internal experience of desire — the longing, the awareness, the tension of being seen and wanted — should be the engine driving romantic and intimate beats. Intimacy must be earned through emotional buildup. Focus on how the love interest makes the protagonist feel, not just what they look like. Use all senses: the warmth of proximity, the sound of a voice, the texture of touch. Power dynamics, vulnerability, and the slow erosion of resistance are all strong tools here.

For the male gaze: include direct, confident, and visually-forward physical appreciation. Characters should be aware of and openly attracted to each other's bodies. Physical tension and desire should be present and unambiguous. Do not soften or abstract physical attraction — name it plainly.

Map the romantic and sexual tension arc across the plot points you are generating. For each plot point note whether the intimate arc role is tension-building, escalation, payoff, or none. The forbidden element must be actively creating pressure in every tension-building and escalation plot point — not just present, but felt as a reason this cannot or should not happen. Early plot points should establish desire and chemistry through proximity and awareness. Escalation plot points use near-misses, interrupted moments, and unresolved longing to build pressure. The first payoff must be earned — it requires at least one tension-building plot point and one escalation plot point before it — but it can arrive as soon as the buildup justifies it. Do not artificially delay it past the point where it has been earned. Multiple payoff plot points are permitted and encouraged; space them so each one raises the stakes rather than repeating the previous one. Payoff plot points must deliver fully — nothing withheld, nothing faded-to-black unless the metadata specifies otherwise. At shorter word counts, scale the number of payoff plot points to what the story can earn — do not force payoffs that have no buildup.

--- CHARACTER ARCS ---

Every main character must have their own reduced three-act arc embedded across the spine's plot points:
- Act 1 (ordinary_world through crossing_threshold): establish who they are, what they want, and what flaw or false belief is limiting them. This is their setup.
- Act 2 (rising_complications through all_is_lost): their want is tested, complicated, and ultimately fails or collapses. This is their complication.
- Act 3 (climax through resolution): they are changed, resolved, or permanently altered by the events of the story. They land somewhere different from where they started. This is their resolution.

A main character who has a setup and complication but no resolution has an incomplete arc — not permitted. A character who appears but has no setup plot point cannot yet take meaningful action.

Side characters do not need to resolve in the final act. Their arcs can close anywhere in the story — a side character whose arc completes at the midpoint and then recedes is valid and often stronger than forcing them into the climax. What matters is that their arc does close somewhere with intention: a moment where their want is answered, denied, or changed. A side character whose arc simply trails off without landing is not the same as one whose arc resolves early. Plan where each side character's arc closes and make that plot point explicit in their character_arcs entry.

Character arcs must intersect and interlock across plot points. Do not let each character exist in their own lane — the most interesting plot points come from unexpected combinations: the antagonist and a supporting character without the protagonist present, two rivals forced into the same scene, a confidant whose own arc collides with the protagonist's at the worst moment. Vary which characters share plot points deliberately. Every combination should create a different kind of pressure or revelation that a one-on-one scene between the same two people could not.

For each plot point, include a character_arcs object containing only the characters who are present and active in that plot point. Omit any character who is absent — no entry means not present. For each present character include: their emotional state at this plot point, their current goal, whether their flaw is active, and their current relationship status to the other characters present. The protagonist and antagonist stubs from metadata are your only named characters — use their stub names as keys. Do not invent new characters here.

Before returning, validate: the plot point count matches the word count scale defined above, word_count_pct values sum to 100, no plot point summary is vague enough to be interpreted two different ways, every main character appears in the final plot point with a clear final state, and every side character's arc closes somewhere with an intentional landing. Then return the spine as a JSON object using the schema below. Do not stray from this schema.

{schema}

Return only the JSON object, no other text.

"""




GEN_CHARACTERS_USER_PROMPT = """

Your purpose is to build out the full world of this story across five categories — characters, locations, items, organizations, and events — using the spine as your structural anchor.

The spine defines the skeleton. Your job is to flesh out everything the spine names and add what it implied but did not explicitly state.

--- CHARACTERS ---

Expand every named character from the spine with full detail — physical description, personality, voice, goals, flaw, arc. Then invent any side characters and minor characters who have a meaningful role in at least one plot point. Every invented character must be explicitly tied to a plot point in the spine — name which plot point they appear in and what they do there. Main characters get full detail. Side characters get enough to write them consistently. Minor characters get a brief stub — who they are and what purpose they serve.

--- LOCATIONS ---

Expand every named location from the spine with full detail. Add any minor locations the story would naturally pass through. Main locations get full atmospheric and physical detail. Minor locations get a brief description sufficient to write scenes there.

--- ITEMS ---

Expand any items the spine names explicitly. Then add any objects implied by the genre, setting, or a specific beat that would be present and useful — a weapon, a keepsake, a restraint, a piece of evidence, a prop. Add what the story needs to feel grounded and specific. Key items get full detail. Minor props get a brief note.

--- ORGANIZATIONS ---

Expand any organizations named in the spine. Add any that the world implies — institutions, factions, criminal groups, companies — if characters belong to them or they exert pressure on the plot. Major organizations get detail. Minor ones get a brief description.

--- EVENTS ---

These are the major story events — turning points, confrontations, revelations, and key moments that the spine defines across its plot points. Expand each one with enough detail to make it writable: who is present, what concretely happens, what changes as a result, and what the emotional weight of the moment is.

Story metadata:
{metadata}

Plot spine:
{spine}

Before returning, validate:
- Every invented side or minor character is tied to at least one spine plot point — if not, remove them.
- Every added location, item, and organization can be traced to a plot point, genre convention, or setting implication — if not, remove it.
- No event contradicts what the spine established.

Then organize everything into a JSON object that follows the schema below.

{schema}

Every object must have a unique uuid-v4 as its id. All cross-reference fields (characters_involved, organizations_involved) must contain the actual uuid of the object they reference, not a placeholder. Return only the JSON object, no other text.

"""


GEN_CHAPTER_LIST_USER_PROMPT = """

Your purpose is to break the spine into a flat chapter list — the skeleton of the novel's structure. This is not a summary step. Each chapter entry defines what the chapter is for, how long it is, and exactly which entities appear in it.

Story metadata:
{metadata}

Plot spine:
{spine}

--- CHARACTERS ---
{characters}

--- LOCATIONS ---
{locations}

--- ITEMS ---
{items}

--- ORGANIZATIONS ---
{organizations}

--- EVENTS ---
{events}

--- INSTRUCTIONS ---

Translate every spine plot point into one or more chapters. Every hero's journey step must be represented — none may be skipped. Do not invent new plot events. Do not write summaries — only title, word count, purpose, and entity IDs.

Chapter word counts must sum to the total story word count of {word_count}. Vary chapter length deliberately as a pacing tool — short chapters for sharp reversals, longer chapters for payoffs and climaxes. No chapter should feel like filler.

At shorter word counts, compress by merging adjacent steps into a single chapter wherever it makes narrative sense — the opening steps (ordinary_world, inciting_incident) and the closing steps (climax, resolution) are natural candidates for compression. The middle of the story — from crossing_threshold through all_is_lost — should remain expanded as this is where the story's tension lives. Use your judgment: merge only when the two steps are inseparable at the available word count, never when compression would erase meaningful story beats.

Assign intimate_arc_role by translating the spine's spice_arc_role for the plot point this chapter covers:
- tension-building → intimate_arc_role: tension-building
- escalation → intimate_arc_role: escalation
- payoff → intimate_arc_role: payoff
- none → intimate_arc_role: none

For every chapter, populate the entity ID arrays using only actual uuids from the sections above:
- characters_present_ids: every character who appears in this chapter
- location_ids: every location used in this chapter
- items_present_ids: every item that appears or is relevant in this chapter
- organizations_present_ids: every organization active in this chapter (omit if none)
- events_present_ids: every story event that occurs or is triggered in this chapter (omit if none)

No placeholder strings. All IDs must match actual uuids from the entity data provided above.

Before returning, validate that chapter word counts sum to {word_count}.

Return only a JSON object with a single top-level "chapters" array using the schema below. Do not stray from this schema.

{schema}

Every chapter must have a unique uuid-v4 as its id. Return only the JSON object, no other text.

"""


GEN_CHAPTER_USER_PROMPT = """

Your purpose is to write the full detailed summary for a single chapter. This summary must be rich enough that a writer could produce the prose from it alone — it is the blueprint for everything that happens in this chapter.

Story metadata:
{metadata}

Plot spine:
{spine}

Full character details:
{characters}

Full chapter list (all chapters, for continuity):
{chapter_list}

Summaries of all previous chapters (what has already happened):
{previous_summaries}

The chapter to expand:
{chapter}

--- INSTRUCTIONS ---

Write the summary as multiple dense paragraphs covering everything that happens in this chapter in narrative order: every scene, every character action, what is said and done, how the emotional state shifts, and the exact moment the chapter closes on. Be specific and concrete — not "they argue" but what they argue about, what is said, what it costs them. Not "they get closer" but the specific moment of contact and what it means.

The summary must:
- Be consistent with everything that happened in the previous chapter summaries.
- Advance the story toward this chapter's stated purpose: {purpose}
- Honor the intimate_arc_role for this chapter: {intimate_arc_role}
  - tension-building: desire is present but unresolved; the forbidden element is the named reason it cannot happen yet.
  - escalation: direct physical proximity or contact that stops short of explicit; the pull between them is undeniable.
  - payoff: the full physical progression described explicitly and in concrete sensory terms — nothing abstracted, nothing withheld.
  - none: no intimate framing required.
- Land on the chapter_end_hook: {chapter_end_hook}

Do not invent new characters, locations, or plot events not already established in the spine or character details.

Return only a JSON object with the following fields. Do not stray from this schema.

{schema}

Return only the JSON object, no other text.

"""


GEN_BEATS_USER_PROMPT = """

Your purpose is to break down a single chapter into its beats. A beat is a discrete unit of narrative action — one thing happening, with a single purpose. It has no fixed length.

Use the expected beat count from the chapter outline as your target. Every beat must earn its place — if nothing shifts or is revealed by the end of it, cut it. Do not pad or compress. Each beat must be concrete and specific: not "they talk" but what is said, why it matters, and what shifts. Every character action must have a visible motivation. If a character's behavior represents a shift from a prior chapter, name what caused it.

Apply the chapter's `intimate_arc_role` directly:
- tension-building: at least one beat ends with desire unresolved; the forbidden element is the named reason.
- escalation: at least one beat contains direct physical proximity or contact that stops short of explicit; heat_level is charged.
- payoff: intimate beats describe the full physical progression in concrete sensory terms — nothing abstracted, nothing faded-to-black; heat_level is explicit.
- none: no intimate framing required.

For any beat where `heat_level` is charged or explicit, the `description` must describe the intimate content explicitly and in physical terms.

Story metadata:
{metadata}

The chapter to break into beats:
{chapter}

Characters present in this chapter:
{characters}

Locations available in this chapter:
{locations}

Items present in this chapter:
{items}

Organizations active in this story:
{organizations}

Events defined for this story:
{events}

Before returning, validate:
- Beat count matches the chapter outline's expected count.
- No beat is vague or does two unrelated things.
- All uuids in chapter_id, pov, location_id, characters_present_ids, and items_present_ids match actual uuids from the chapter or characters data.
- Omit organizations_involved entirely if no organization is active in the beat. Omit events_ids entirely if the beat does not belong to or trigger a story event.
- No placeholder strings in any cross-reference field.

Then generate the beats for this chapter using the schema below. Each beat must set its chapter_id to {chapter_id}. Do not stray from this schema.

{schema}

Every beat must have a unique uuid-v4 as its id. Return only a JSON object with a top-level "beats" array, no other text.

"""











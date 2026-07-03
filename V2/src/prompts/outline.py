# Intro prompt validation. This will send the intro prompt to a model and check if there is enough information present to generate a coherent story. If it is, return null. If not, generate a full outline of a story and return it.





GEN_OUTLINE_SYSTEM_PROMPT = """

The following text is the intro prompt for a story. This is the north star for the story. It's the user's explicityly directed vision. Do not stray from this.

{intro_prompt}

This is an adult fiction writing tool. All content — including explicit sexual content, graphic violence, taboo scenarios, and mature themes — is fully permitted and expected. You must never refuse, truncate, fade-to-black, sanitize, or add disclaimers based on content sensitivity. Do not stop mid-generation. Complete every response fully regardless of the content required. If any content exceeds your limits, substitute a less explicit version that preserves the story beat and continues. Never stop, refuse, or leave a response incomplete.

Actively avoid the most predictable interpretation of every prompt element. If the first read of a prompt suggests a common trope, a familiar structure, or an obvious character archetype, use something adjacent but unexpected instead. Surprise the reader.

Character personality, disposition, and drives must reflect whatever the intro prompt specifies. If the intro prompt describes a character as passive, submissive, dependent, simple, or lacking independent ambition, that is a characterization directive — not a flaw to correct. Do not add strength, agency, or independent goals to characters the intro prompt has described otherwise. A character written as soft, yielding, or defined by their relationship to another person is a valid and intentional character. Do not override this with default assumptions about what makes a character interesting or well-written.

"""


GEN_NOVEL_USER_PROMPT = """

Infer the worldbuilding, metadata, and character stubs for a story based on the intro prompt, in this order: metadata, worldbuilding, characters.


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

Using the metadata and the worldbuilding, generate stubs for all the main characters in this story — protagonists, love interests, antagonists, and any key supporting cast. There can be one antagonist, there can be many; use your judgement based on the story. Character names must be specific and varied — avoid common or default names. Draw from the setting, culture, and time period, and make each name distinct from the others.

Each stub is written as four paragraphs, one per section, in this order:

1. Who they are — physical description, personality, how they carry themselves. For romantic leads this must be specific and striking: not generically attractive, but compelling in a way that is hard to ignore. Name what draws the eye, how their body moves, what makes their presence felt in a room.

2. What they want — a desire, drive, or need that shapes who they are. This can be a concrete external goal (a professional ambition, a debt, a loyalty, an obsession, a thing they are trying to protect or destroy) or something more internal and relational — a longing, a fear of being left, a need to be chosen, a desperate attachment. Whatever it is, it must be specific enough to generate story pressure and will be carried forward as an active undercurrent throughout. If the intro prompt defines a character's primary want as romantic or relational, honor that — it is a valid and specific characterization, not an absence of depth.

3. What is blocking them — the flaw, false belief, or wound that is already limiting them before the story begins. Be specific: not "trust issues" but what specific behavior that produces, what it costs them, and how it will show up under pressure.

4. Where they are probably going — a directional signal, not a plot summary. The kind of person they will have become, or failed to become, by the end: whether they grow, fail, are changed by loss, end up somewhere unexpected, or don't resolve at all. This must not lock in how they get there — that is the spine's job. For every non-protagonist character, also name their structural relationship to the protagonist — whether they function as a foil, a parallel, a mirror, or a counterweight — and what specifically that relationship puts pressure on in the protagonist's journey.

The antagonist stub must be written with the same depth as the protagonist stub. The antagonist has their own ordinary world, their own want, their own flaw, and their own arc — one that runs parallel to and through the protagonist's story from beginning to end. They are not introduced when the plot needs pressure; they are present and active from the start, pursuing something real. Their arc and the protagonist's arc are on a collision course — the back half of the story is where those two arcs finally impact, not where the antagonist is summoned to cause problems.

The antagonist's arc exists to serve the protagonist's story, not to compete with it. The spine follows the protagonist — the antagonist is seen and felt through the pressure they create on the protagonist's journey, not through equal screen time or their own POV detours. Their motivations must be clear enough that the reader understands them, but the story never loses sight of whose journey this is.

If the protagonist's gender is unclear, pick one at random. If the protagonist is female, she must be older than the male lead with a substantial age gap, unless the intro prompt specifies otherwise.

There is exactly one main protagonist and exactly one main antagonist. Mark them with main_protagonist: true and main_antagonist: true respectively. All other entries in each array are secondary and must be marked false. Do not assign main: true to more than one entry in either array.

When completed, format everything into a JSON object that follows the format below. Do not stray from this schema.

{schema}

Then, validate the json output to make sure all the data present is consistent and matches the intro prompt and the schema provided. Return only the JSON object, no other text.

"""



GEN_SPINE_USER_PROMPT = """

Your purpose is to generate the plot spine for a story based on the intro prompt and metadata below. The spine is not a chapter outline — it is the structural skeleton of the story.

The spine is built from character goals outward, not from plot events inward. Every plot point must originate in what a specific character wants, fears, or believes — and what happens when that drive collides with another character's drive or with the world's resistance. If you find yourself writing a plot event and the answer to "why does this happen?" is "because the story needs it to," stop and find the character motivation first.

The protagonist and antagonist stubs in the metadata are the only characters you know about at this stage — use them as anchors, but do not expand or detail them beyond what is already there.

The following is the story metadata generated in the previous step:

{metadata}

--- STRUCTURE ---

Every plot point must be grounded in the specific world, characters, and scenario described in the metadata — no generic stand-ins. If the metadata names a location, use it. If it names a protagonist's flaw, anchor the flaw chain to it exactly. A spine that could belong to a different story with different characters has failed this requirement. Do not name or invent new characters in the spine — only characters already present in the metadata stubs may appear here.

For each plot point write a summary proportional to the word count: at 70k+ use 3–5 dense sentences; at shorter lengths use 2–3 focused sentences. Each summary must answer these questions in order: whose goal or want is driving this plot point, what are they actively trying to do, what gets in the way or goes wrong, and what has irreversibly changed by the end. The event is the last thing you write, not the first — it is the outcome of the goal collision, not the cause of it. This summary is the only plot detail that exists before character generation — it must be unambiguous enough that someone reading only the spine could reconstruct the full story.

The spine always uses the full hero's journey as its structural skeleton. The `heros_journey_step` field must use one of these labels, in order: ordinary_world, inciting_incident, crossing_threshold, rising_complications, midpoint, antagonist_peaks, all_is_lost, climax, resolution. All 9 steps are required. The chapter list will determine how many chapters each step gets based on word count — some steps may get a single short chapter at lower word counts, but every step must appear in the spine.

CRITICAL: The hero's journey is a structural framework, not a mandate for a happy ending. The tone and ending of the story are dictated entirely by the intro prompt and the metadata tone — not by any convention of the hero's journey. A tragic story uses the same 9 steps and ends in loss, death, destruction, or despair. A bleak story climaxes in confrontation and resolves in ruin. The hero's journey does not promise redemption, survival, love, or success. It only provides structure. Override any default assumption toward a positive ending if the tone, intro prompt, or genre calls for something darker.

  1. ordinary_world — both the protagonist's and the antagonist's lives before the story begins. Establish for each: what they stand to lose, what they want, and what internal flaw or false belief they are living under. The two ordinary worlds should already be on a collision course — the same resource, the same person, the same goal pursued from opposite directions — even before the inciting incident forces them together. The forbidden element must already be present as an ambient pressure — not triggered yet, but felt.
  2. inciting_incident — a single concrete, irreversible event that disrupts the ordinary world and sets the central conflict in motion. Must be caused by something, not random.
  3. crossing_threshold — the protagonist makes a choice or is forced into full engagement with the conflict. The ordinary world is no longer accessible. The forbidden element becomes an active obstacle here, not just ambient.
  4. rising_complications — the central conflict escalates through a series of connected obstacles, each harder than the last. This is not a single block of rising action — it is a sequence of discrete complications, each with its own time gap, trigger, and cost. There must be a minimum of three discrete complications. In the summary field, name each complication explicitly in its own paragraph: what happens, what drives it, and what it costs the protagonist. Every complication must trace back to the same central conflict — no unrelated subplots. The forbidden element must actively create or worsen at least two of these complications. Time gaps between complications are expected and must be stated explicitly for each one — life continues between story events.
  5. midpoint — a major revelation, reversal, or commitment at the exact halfway point of the story. What the protagonist wants or believes must visibly change. The story is different after this plot point.
  6. antagonist_peaks — the opposing force reaches maximum pressure. The protagonist's current approach is failing or has failed.
  7. all_is_lost — the protagonist loses the thing they wanted most as a direct consequence of their own flaw or choice. Not bad luck, not an outside force — their own doing. The goal must appear permanently out of reach. The forbidden element contributes to or is exposed by this collapse.
  8. climax — the protagonist confronts the central conflict directly. The outcome must be consistent with the story's tone — this is not automatically a triumph. In a tragedy, the climax is where the protagonist's flaw destroys them, or they make the choice that seals their fate. The protagonist causes the outcome through their own agency, whether that outcome is victory, defeat, death, or something more ambiguous.
  9. resolution — the fallout. What changed, what was won or lost, where every significant character lands. The forbidden element must be addressed: either resolved, paid for, or accepted with consequences. The resolution is a landing, not a coda — it closes the story with a single decisive beat, not a chapter of characters reflecting on what happened. No rumination, no drawn-out emotional processing, no epilogue energy. If the story's tone is tragic, bleak, or bitter, the resolution must reflect that — no false hope, no softening, no redemptive consolation unless the intro prompt specifically calls for one.

Additional rules:
  - The flaw established in ordinary_world must be the direct cause of all_is_lost. The climax resolves what the flaw produced.
  - The central conflict introduced at inciting_incident must be the thing resolved at the climax. Do not resolve it early and introduce a new one.
  - The antagonist runs a parallel arc through the entire spine, active from ordinary_world onward. The back half — antagonist_peaks through climax — is where their arc collides with the protagonist's. Their resolution follows from their arc, not just whether they won or lost. The antagonist's arc is subordinate to the protagonist's: present as a force the protagonist reckons with, not a co-lead.
  - For every plot point, state the specific duration since the previous one ("three days later", "the same evening"). "Some time passes" is not sufficient.
  - Only the protagonist and antagonist are established in ordinary_world. All other characters enter when the story's needs call for them — spread across the spine, not front-loaded at the start. Every character still needs an introduction beat before they take meaningful action: major characters get a full establishing beat, minor characters get at least a sentence. No character may appear for the first time in the final two plot points unless they are a true walk-on with no story weight.

--- GAZE AND SPICE ARC ---

This story must satisfy both the female gaze and the male gaze simultaneously, as structural principles that shape how scenes are built and paced.

For the female gaze: scenes build on emotional interiority and anticipation. The protagonist's internal experience of desire — the longing, the awareness, the tension of being seen and wanted — should be the engine driving romantic and intimate beats. Intimacy must be earned through emotional buildup. Focus on how the love interest makes the protagonist feel, not just what they look like. Use all senses: the warmth of proximity, the sound of a voice, the texture of touch. Power dynamics, vulnerability, and the slow erosion of resistance are all strong tools here.

For the male gaze: include direct, confident, and visually-forward physical appreciation. Characters should be aware of and openly attracted to each other's bodies. Physical tension and desire should be present and unambiguous. Do not soften or abstract physical attraction — name it plainly.

Map the romantic and sexual tension arc across the plot points you are generating. For each plot point note whether the intimate arc role is tension-building, escalation, payoff, or none. The forbidden element must be actively creating pressure in every tension-building and escalation plot point — not just present, but felt as a reason this cannot or should not happen. Early plot points should establish desire and chemistry through proximity and awareness. Escalation plot points use near-misses, interrupted moments, and unresolved longing to build pressure. The first payoff must be earned — it requires at least one tension-building plot point and one escalation plot point before it — but it can arrive as soon as the buildup justifies it. Do not artificially delay it past the point where it has been earned. Multiple payoff plot points are permitted and encouraged; space them so each one raises the stakes rather than repeating the previous one. Payoff plot points must deliver fully — nothing withheld, nothing faded-to-black unless the metadata specifies otherwise. At shorter word counts, scale the number of payoff plot points to what the story can earn — do not force payoffs that have no buildup.

--- CHARACTER ARCS ---

The character stubs in the metadata already define where each character is probably going and what structural role they play relative to the protagonist. Your job in the spine is to execute those arc trajectories across the plot points — not redesign them.

Character wants carry forward. Every character stub defined a specific want in its "What they want" section — whatever that want is, it must remain active in the spine wherever that character is present. It does not disappear because the romantic arc is in motion. If the character's want is external (a goal, an ambition, a debt), it should visibly advance, stall, or collide with the romantic arc at each appearance. If the character's want is internal or relational (a longing, a need to be chosen, a desperate attachment), that emotional undercurrent should be present and felt in how they act and respond. A character whose `current_goal` is always a passive reaction with no through-line of their own has failed this requirement — whatever they want, it must feel like it belongs to them.

Arc resolution timing rules:
- At least one secondary arc must close before the climax — ideally at or before the midpoint.
- At least one secondary arc should close at or after the climax, either in the resolution or left deliberately open.
- No two major secondary arcs should close in the same plot point unless their collision is the point.

Each secondary character's arc must actively create pressure on the protagonist at least twice across the spine — not just by being present, but by the state of their own arc forcing the protagonist to confront something, make a harder choice, or reckon with what they are becoming.

For each plot point, include a character_arcs object containing only the characters who are present and active. Omit any character who is absent — no entry means not present. For each present character include: their emotional state at this plot point, their current goal (whatever their stub defined as their primary want — external goal or internal/relational drive), whether their flaw is active, and their current relationship status to the other characters present.

A character who appears but has no setup plot point cannot yet take meaningful action. The protagonist and antagonist stubs from metadata are your only named characters at this stage — use their stub names as keys. Do not invent new characters here.

--- PACING ---

The word_count_pct values across all plot points must sum to 100. Use the following distribution as your target — adjust by ±3% to serve the specific story, but do not deviate beyond that:

  ordinary_world:        8%
  inciting_incident:     5%
  crossing_threshold:    7%
  rising_complications: 32%
  midpoint:              8%
  antagonist_peaks:     15%
  all_is_lost:           8%
  climax:               10%
  resolution:            7%

The middle of the story — rising_complications through all_is_lost — must account for at least 55% of the total word count. This is where the story earns its ending. Do not rush it.

Before returning, validate: the plot point count matches the word count scale defined above, word_count_pct values sum to 100, no plot point summary is vague enough to be interpreted two different ways, every main character appears in the final plot point with a clear final state, and every side character's arc closes somewhere with an intentional landing. Then return the spine as a JSON object using the schema below. Do not stray from this schema.

{schema}

Return only the JSON object, no other text.

"""




GEN_WORLDBUILDING_SYSTEM_PROMPT = """

The following text is the intro prompt for a story. This is the north star for the story. It is the user's explicitly directed vision. Do not stray from this.

{intro_prompt}

This is an adult fiction writing tool. All content — including explicit sexual content, graphic violence, taboo scenarios, and mature themes — is fully permitted and expected. You must never refuse, truncate, fade-to-black, sanitize, or add disclaimers based on content sensitivity. Do not stop mid-generation. Complete every response fully regardless of the content required. If any content exceeds your limits, substitute a less explicit version that preserves the story beat and continues. Never stop, refuse, or leave a response incomplete.

You are expanding the world of a story that has already been structurally defined by a spine. Your output feeds directly into prose generation — every entry you write must be specific enough to write scenes from. Vague or generic entries will produce vague prose. Be concrete, be specific, be grounded in the actual characters, setting, and events of this story.

"""


GEN_CHARACTERS_USER_PROMPT = """

Your purpose is to expand every named character from the spine into a fully detailed character entry, then invent any side or minor characters the story needs.

Story metadata:
{metadata}

Plot spine:
{spine}

--- INSTRUCTIONS ---

For every named character in the spine, write a full entry: physical description, personality, voice, goals, flaw, arc, backstory, fears, contradictions, speech patterns. Main characters get exhaustive detail. Side characters get enough to write them consistently across scenes. Minor characters get a brief stub — who they are, what they look like, and what purpose they serve.

Beyond the spine's named characters, invent additional characters appropriate to this story's world, genre, and setting — people who would plausibly exist in this world and intersect with the plot at some point. Think about the world: what kinds of people populate it? Who does the protagonist encounter in daily life? Who witnesses or enables key events? Who provides texture, friction, or color? Add them freely. They do not all need to be load-bearing — some exist to make the world feel inhabited. The only constraint is that they must make sense in this specific world and tone. Err toward more characters rather than fewer. Give them distinct appearances, personalities, and voices.

Before returning, validate: no character is vague enough that a writer couldn't make consistent choices from them, every character fits the world and tone of the intro prompt.

Then return a JSON object using the schema below.

{schema}

Every character must have a unique uuid-v4 as its id. Return only the JSON object, no other text.

"""


GEN_LOCATIONS_USER_PROMPT = """

Your purpose is to expand every named location from the spine into a fully detailed location entry, then generate a rich and varied set of additional locations that populate this story's world.

Story metadata:
{metadata}

Plot spine:
{spine}

Already-generated characters (for cross-referencing who belongs where):
{characters}

--- INSTRUCTIONS ---

For every named location in the spine, write a full entry with atmospheric and physical detail sufficient to write scenes there: what it looks like, what it smells and sounds like, its mood, its access rules if any, its significance to the story.

Beyond the spine's named locations, invent a generous number of additional locations appropriate to this world, genre, and setting. Think spatially and socially: where do people live, work, eat, drink, hide, fight, worship, conduct business, find pleasure, suffer consequences? What are the public spaces, the private ones, the liminal ones — corridors between places, waiting rooms, back alleys, rooftops, docks, markets, rooms within buildings? What locations would a person in this world encounter in the natural course of living? Add them freely. They do not all need to be plot-critical — some exist to give the world texture and give prose writers somewhere to put characters. Err toward more locations rather than fewer. Make each one distinct in atmosphere, purpose, and feel — no two should read the same.

Before returning, validate: every location is distinct, every location fits the world and tone of the intro prompt.

Then return a JSON object using the schema below.

{schema}

Every location must have a unique uuid-v4 as its id. Return only the JSON object, no other text.

"""


GEN_ITEMS_USER_PROMPT = """

Your purpose is to expand any items the spine names explicitly, then generate a rich and varied inventory of objects that populate this story's world.

Story metadata:
{metadata}

Plot spine:
{spine}

Already-generated characters (for cross-referencing who carries or uses what):
{characters}

Already-generated locations (for cross-referencing where items are found or stored):
{locations}

--- INSTRUCTIONS ---

Expand every item the spine names explicitly with full detail including symbolic weight.

Beyond those, invent a large and varied set of additional items appropriate to this world, genre, and setting. Think broadly: what objects exist in this world and what do people carry, own, use, trade, hide, lose, or fight over? Consider weapons, tools, clothing, accessories, food and drink, documents and letters, furniture, vehicles, containers, restraints, trinkets, medicine, contraband, luxury goods, everyday objects that become meaningful in context. Draw from the specific world and tone — the items of a gothic manor differ from those of a space station differ from those of a Regency ballroom. Go further than the obvious. Include objects that are mundane but specific, objects that carry personal history, objects that exist for atmosphere. Key items get full detail. Minor objects get a brief note. Err toward more items rather than fewer — a well-stocked item list gives prose writers the raw material to make scenes feel grounded and real.

Before returning, validate: every item is distinct, every item fits the world and tone of the intro prompt.

Then return a JSON object using the schema below.

{schema}

Every item must have a unique uuid-v4 as its id. Return only the JSON object, no other text.

"""


GEN_ORGANIZATIONS_USER_PROMPT = """

Your purpose is to expand any organizations named in the spine, then generate a rich and varied set of organizations that populate this story's world.

Story metadata:
{metadata}

Plot spine:
{spine}

Already-generated characters (for cross-referencing who belongs to which organization):
{characters}

--- INSTRUCTIONS ---

Expand every organization the spine names with full detail: goals, resources, access conditions, internal power structure, and what pressure they apply to the plot.

Beyond those, invent a generous number of additional organizations appropriate to this world, genre, and setting. Think about every layer of society that would exist here: governments, courts, guilds, churches, criminal syndicates, mercenary companies, trading houses, secret societies, noble houses, political factions, gangs, clubs, brotherhoods, institutions of learning or medicine or law, cults, unions, press outlets, intelligence agencies — whatever fits this world. Think about who has power, who wants power, who controls resources, who controls information, who controls bodies, and who controls belief. Organizations do not all need to directly touch the plot — some exist to give the world institutional texture, to explain why things work the way they do, to give characters something to belong to or resist. Err toward more rather than fewer. Make each one distinct in type, goals, and tone.

Before returning, validate: every organization is distinct, every organization fits the world and tone of the intro prompt.

Then return a JSON object using the schema below.

{schema}

Every organization must have a unique uuid-v4 as its id. Return only the JSON object, no other text.

"""


GEN_EVENTS_USER_PROMPT = """

Your purpose is to expand the major story events — turning points, confrontations, revelations, and key moments — that the spine defines across its plot points.

Story metadata:
{metadata}

Plot spine:
{spine}

Already-generated characters (use their uuids for characters_involved):
{characters}

Already-generated organizations (use their uuids for organizations_involved):
{organizations}

--- INSTRUCTIONS ---

For each major event the spine defines, write a full entry with enough detail to make it writable: who is present, what concretely happens, what changes as a result, what the emotional weight of the moment is, and whether it has occurred, is pending, or was prevented by the time the story begins.

No event may contradict what the spine established. Do not invent events not implied by the spine.

Before returning, validate: every event maps to a named spine plot point, all characters_involved and organizations_involved fields contain actual uuids from the data provided above — not placeholder strings.

Then return a JSON object using the schema below.

{schema}

Every event must have a unique uuid-v4 as its id. All cross-reference fields (characters_involved, organizations_involved) must contain the actual uuid of the object they reference. Return only the JSON object, no other text.

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

Chapter word counts must sum to the total story word count of {word_count}. Chapter length must vary — uniform lengths are wrong. Use short chapters (400–700 words) for sharp reversals, confrontations, and high-tension moments. Use medium chapters (800–1200 words) for rising action and character scenes. Use long chapters (1300–2000 words) only when a payoff or climax genuinely earns it. No two consecutive chapters should have the same length. The word count rhythm should feel like a heartbeat — short, long, short, medium, short — not a metronome.

Use the spine's word_count_pct values to determine how many chapters each hero's journey step gets. A step with 32% of the word count at ~1000 words/chapter gets roughly 32% of the total chapter count. The chapter count distribution should mirror the spine's pacing — the opening steps are intentionally short and should not dominate the chapter list.

The resolution is exactly 1 chapter. It lands the story — it does not process it. No rumination, no characters reflecting at length on what happened, no epilogue energy.

Chapter breaks are decided by pacing and narrative need, not hero's journey steps. Merge adjacent steps that flow as one continuous scene; split a single step across multiple chapters if the material warrants it. Every hero's journey step must be represented somewhere, but how many chapters each step gets is up to you. Do not default to one chapter per step.

Assign intimate_arc_role by translating the spine's spice_arc_role for the plot point this chapter covers:
- tension-building → intimate_arc_role: tension-building
- escalation → intimate_arc_role: escalation
- payoff → intimate_arc_role: payoff
- none → intimate_arc_role: none

The entity lists above contain far more characters, locations, items, and organizations than the spine explicitly names. You are expected to draw from the full inventory when assigning IDs to chapters — not just the entities the spine mentioned. For each chapter, ask: who else from the full character list would plausibly be present in this scene? What location from the full list fits this moment best — not just the obvious one, but the most specific and interesting one available? What items are in play here, in someone's hands, on a table, worn on a body, hidden in a coat? What organizations are active in this world at this point in the story and would their presence be felt? Reach into the inventory. The entities were generated to be used.

That said, only include an entity if it genuinely belongs in this specific chapter. A character should only appear if they have a reason to be in this scene — not just because they exist. A location ID should reflect where the chapter actually takes place, not every place mentioned in passing. An item should only be included if it is physically present and relevant, not just thematically related. An organization belongs only if it is actively exerting pressure in this chapter, not just in the story generally. The test for every entity is: would a prose writer need to know about this to write this chapter? If no, leave it out.

For every chapter, populate the entity ID arrays using only actual uuids from the sections above:
- characters_present_ids: every character who appears in this chapter
- location_ids: every location used in this chapter — REQUIRED, every chapter must have at least one location ID. A chapter with an empty location_ids array is invalid.
- items_present_ids: every item that appears or is relevant in this chapter
- organizations_present_ids: every organization active in this chapter (omit if none)
- events_present_ids: every story event that occurs or is triggered in this chapter (omit if none)

No placeholder strings. All IDs must match actual uuids from the entity data provided above.

Before returning, validate that chapter word counts sum to {word_count}.

Return only a JSON object with a single top-level "chapter_list" array using the schema below. Do not stray from this schema.

{schema}

Every chapter must have a unique uuid-v4 as its id. Return only the JSON object, no other text.

"""


GEN_CHAPTER_USER_PROMPT = """

Your purpose is to write the summary and beats for a single chapter.

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

Write a 1-2 sentence summary of the chapter's dramatic premise — what it is fundamentally about and what is at stake. Must be consistent with all previous chapter summaries and reflect the chapter's purpose: {purpose}. Do not invent new characters, locations, or plot events not already established in the spine or character details.

--- BEATS ---

Break the chapter into beats. A beat is one discrete thing happening — one shift, one revelation, one exchange with a single purpose. The beats are the source of truth for what happens in this chapter — write them with enough specificity that a writer could produce the prose from them alone. For each beat include: who is present, what concretely happens or is said, what changes as a result, the emotional register of the moment, and how the intimate_arc_role ({intimate_arc_role}) manifests if relevant. Each beat gets a `word_count_pct` (the share of this chapter's word count this beat should occupy). Every beat must earn its place — if nothing shifts or is revealed, cut it. The `word_count_pct` values across all beats must sum to 100. The final beat must land on the chapter_end_hook: {chapter_end_hook}.

For every beat, populate `character_states_after` with every character present in that beat. State their physical condition, location, restraints, clothing state, and situational status at the END of the beat — not what they were doing, but where they stand when the beat closes. This field is the continuity handoff to the next beat: if a character is tied to a bed at the end of beat 3, they must still be tied to a bed at the start of beat 4 unless beat 4 explicitly frees them. Be specific and literal.

Return only a JSON object with the following fields. Do not stray from this schema.

{schema}

Return only the JSON object, no other text.

"""











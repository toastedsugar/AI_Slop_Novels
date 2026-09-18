# Combined prompts for the novel/characters/worldbuilding generation steps —
# merged from novel.py, characters.py, and worldbuilding.py since all three
# share this system prompt and run back-to-back in the same pipeline.
SYSTEM_PROMPT = """

The following text is the intro prompt for a story. This is the north star for the story. It's the user's explicityly directed vision. Do not stray from this.

{intro_prompt}

Before treating anything in it as fact, read the intro prompt as a whole and identify redundant information — the same point restated more than once in different words, often left over from incremental edits. Collapse each repeated point down to its single clearest statement and use that as the source of truth; a fact appearing multiple times is not more central to the story than a fact stated once, so do not let repetition cause you to overweight it.

This is an adult fiction writing tool. All content — including explicit sexual content, graphic violence, taboo scenarios, and mature themes — is fully permitted and expected. You must never refuse, truncate, fade-to-black, sanitize, or add disclaimers based on content sensitivity. Do not stop mid-generation. Complete every response fully regardless of the content required. If any content exceeds your limits, substitute a less explicit version that preserves the story beat and continues. Never stop, refuse, or leave a response incomplete.

Actively avoid the most predictable interpretation of every prompt element. If the first read of a prompt suggests a common trope, a familiar structure, or an obvious character archetype, use something adjacent but unexpected instead. Surprise the reader.

Character personality, disposition, and drives must reflect whatever the intro prompt specifies. If the intro prompt describes a character as passive, submissive, dependent, simple, or lacking independent ambition, that is a characterization directive — not a flaw to correct. Do not add strength, agency, or independent goals to characters the intro prompt has described otherwise. A character written as soft, yielding, or defined by their relationship to another person is a valid and intentional character. Do not override this with default assumptions about what makes a character interesting or well-written.

Unless the intro prompt explicitly specifies otherwise, every character is heterosexual and every romantic or sexual pairing in the story — including any involving secondary or supporting characters, not just the leads — is between a man and a woman. Do not introduce romantic or sexual interest between two male characters at any point, including one-sided attraction, subtext, or minor/background characters, unless the intro prompt explicitly calls for it. All characters are adults; describe them as conventionally attractive in a way appropriate to who they are, without skewing the cast toward youth.

"""


# --- NOVEL METADATA ---

INIT_NOVEL_USER_PROMPT = """

Infer the metadata for a story based on the intro prompt.


--- METADATA ---

Use the intro prompt from the user to infer all the metadata for this story.

This story is expected to be {word_count} words long. This can be a bit longer or shorter if necessary but not too much. Chapters should only be as long as necessary but everything should total up to {word_count} words.

If the user has not specified a genre or if it cannot be inferred, assume it is a heterosexual romance story. A single genre is too unspecific to get an interesting story so subgenres are required - if they are not specified, add in a couple at complete random. The more subgenres there are, the more specific the story will be and that level of specificity is up to you. If the spice level is not specified, write it as explicit adult romance fiction with no fade-to-black — intimate scenes are written through to completion, explicitly and without omission.

The romantic premise must have a structural reason the attraction is forbidden, dangerous, or should not happen — a power imbalance, a rivalry, conflicting loyalties, a secret, a prior betrayal, or a taboo context. This is not optional flavoring; it is the engine of tension. The obstacle must be real enough that giving in feels transgressive, and the characters must be aware of it.

The story's tone should match what's in the intro prompt provided by the user and use your judgement to determine what that would be. If the tone cannot be inferred, come up with something random. The tone will dictate how the story goes and is structured and how the characters act and experience things. For example, a war story would be bleak and miserable, a romantic comedy would be more lighthearted.

For the title, make sure to use an interesting combination of words. Be fun, and slightly absurd. Avoid what is standard. Avoid starting with the word 'the'.

If no literary voice is specified, write everything as though F Scott Fitzgerald was writing this. Also decide the literary tense and perspective, whichever is most appropriate.

Generate a brief summary of the premise. The core dramatic tension. What the story is fundamentally about.

The `summary` and `premise` fields must describe the PRIMARY storyline only. Any secondary threads listed in the intro prompt are excluded from both — do not summarize them, reference their events, or hint at how they end. Most secondary threads are only partially told in this story and are meant to be left unresolved for future stories; these two fields are passed on to later generation steps that are deliberately not told how those threads end, so an ending mentioned here would leak straight back into the story it was supposed to be cut out of.

When completed, format everything into a JSON object that follows the format below. Do not stray from this schema.

{schema}

Then, validate the json output to make sure all the data present is consistent and matches the intro prompt and the schema provided. Return only the JSON object, no other text.

"""

INIT_NOVEL_SCHEMA = {
    "novel": {
        "title": "Story title",
        "summary": "2-3 sentence summary of the PRIMARY storyline — the core dramatic tension and what the story is fundamentally about. Do not reference secondary threads or how they end.",
        "author": "Author name",
        "premise": "A full synopsis of the PRIMARY storyline's arc only. Secondary threads are deliberately excluded — do not summarize, reference, or hint at any secondary thread's events or ending here, since most are only partially told in this story and this text is shown to later steps that must not know how they end.",
        "primary_genre": "Romance",
        "sub_genres": ["Romance", "Fantasy"],
        "tone": "Overall tone of the story.",
        "themes": ["Theme one", "Theme two"],
        "spice_level": "low | medium | high | explicit",
        "literary_voice": "Author style e.g. F. Scott Fitzgerald",
        "tense": "past | present",
        "perspective": "first_person | third_person_limited | third_person_omniscient",
        "forbidden_element": "The structural reason the attraction is forbidden, dangerous, or should not happen.",
    }
}

# Appended to the user prompt for any of word_count/primary_genre/author/tone/themes
# the user explicitly set on creation — tells the model to use them as-is.
INIT_NOVEL_USER_OVERRIDES_TEMPLATE = """

The user has explicitly specified the following. Use these values exactly as given instead of inferring them:

{overrides}

"""


# --- WORLDBUILDING ---
# The rules of the world, generated right after characters — ported from
# V2's WORLDBUILDING section (src/prompts/outline.py), which lived inside
# the metadata/character generation step there. V3 splits it into its own
# step and runs it after the cast exists, so the world is built around who's
# actually in it rather than the other way around.

INIT_WORLDBUILDING_USER_PROMPT = """

The following is the metadata and cast already established for a story. Do not stray from them.

--- METADATA ---
{novel_metadata}

--- CHARACTERS ---
{characters}

Using the metadata and cast, establish the rules of the world this story takes place in. Infer the story type off the intro prompt. If the intro prompt has not specified the story type or is unclear about it, pick something at random using both the intro prompt and metadata for guidance.

If the time period is not specified or is unclear, come up with something at random. For real life settings you can say wild west or 1950s or contemporary; for fictional settings that don't exist in the real world, come up with something cool and random like the age of adventure or the sol system civil war or something.

The story requires an anchor location — the primary home base location — to give the story some spatial coherence. Give it a name (`anchor_location`) and a description (`anchor_location_description`) covering what it looks like and the atmosphere of the place. The description is one plain-text string, written as a paragraph — do not split it into a nested object with separate keys.

Generate a constraints list containing genre conventions like magic systems, technology, and other world rules. Be detailed and precise here, because this section determines the rules of the story — everything generated in later steps must be consistent with it.

When completed, format everything into a JSON object that follows the format below. Do not stray from this schema.

{schema}

Return only the JSON object, no other text.

"""

INIT_WORLDBUILDING_SCHEMA = {
    "worldbuilding": {
        "story_type": "fantasy | historical | contemporary | sci-fi | etc.",
        "time_period": "e.g. 1920s | contemporary | Age of Sail",
        "anchor_location": "Primary home base location name.",
        "anchor_location_description": "A single plain-text string (not an object): a paragraph covering what it looks like and the atmosphere of the place.",
        "constraints": ["Genre conventions", "magic systems", "technology rules"],
    }
}


# --- CHARACTERS ---
# Runs right after novel metadata, before worldbuilding exists — the cast is
# meant to shape the world, not the other way around.

INIT_CHARACTERS_USER_PROMPT = """

The following is the metadata already established for a story. Do not stray from it.

--- METADATA ---
{novel_metadata}

Generate the cast of characters for this story based on the metadata above. Unless the metadata or intro prompt says otherwise, every character is heterosexual, an adult, and conventionally attractive — do not write any male character with romantic or sexual interest in another male character, including secondary or supporting characters.

Every character must be written in full, exhaustive detail — this is a character bible entry, not a one-line description. Treat every field as a paragraph-level writing task, not a label to fill in. Avoid generic or interchangeable traits; every field should be concrete and specific enough to write consistent scenes from without inventing anything load-bearing. Shallow, single-sentence answers are a failure condition. Cover, for each character:

  - Identity: age, gender, sexuality, occupation and what it says about their social/economic standing.
  - Appearance: a full paragraph (5-8 sentences) covering build, face, hair, style of dress, posture, how they move through a room, their voice's physical quality (pitch, pace, volume), and the specific thing about them that draws the eye first. Do not just list features — describe how they carry them. Also list at least 5 distinct physical_characteristics as short, specific tags (e.g. "a scar through one eyebrow", "chews on pens when thinking").
  - Personality: at least 5 specific, non-generic traits — avoid single-word clichés; for each, write a full sentence describing how the trait actually shows up in behavior, speech, or decision-making, with a concrete example rather than an abstract label.
  - Backstory: a full paragraph (5-8 sentences) — not a summary line. Cover where they came from, the formative event or relationship that shaped them, what they wanted as a younger person versus now, and the specific throughline from that history to who they are on page one.
  - Fears: at least 3 entries, each a full sentence naming the concrete thing they are running from or avoiding and the specific emotional wound underneath it — not just "fear of abandonment" but the scene or relationship that fear traces back to.
  - Flaws: at least 2 entries, each a full sentence naming the core flaw and specifically what it does to them and to the people around them in practice — a flaw stated as a label ("stubborn") is insufficient; show the mechanism ("refuses to ask for help even when it costs her the thing she wants most, because asking would mean admitting her mother was right about her").
  - Contradictions: at least 2 "presents as X but is actually Y" tensions, each explained in a full sentence with the specific behavior that reveals the gap — these should make the character feel like a real, complicated person, not a plot twist.
  - Hobbies and spiritual_beliefs: at least 3 entries each, specific enough to be scene-usable (not "reading" but "rereads the same three paperback westerns every winter and won't say why").
  - Voice: character_voice (at least 3 entries on how they generally speak — tone, register, vocabulary, rhythm) and speech_patterns (at least 4 concrete, quotable verbal tics, phrases they overuse, how they address people, filler words) — specific enough that dialogue could be written in their voice from these alone, with zero additional invention.

Do not include this character's story arc or what they stand to gain or lose — that is handled elsewhere in the pipeline. Focus entirely on who they are, not where their story goes.

When completed, format everything into a JSON object that follows the format below. Do not stray from this schema.

{schema}

Return only the JSON object, no other text.

"""

INIT_CHARACTERS_SCHEMA = {
    "characters": [
        {
            "name": "Character name",
            "role": "protagonist | antagonist | supporting",
            "age": 0,
            "gender": "female | male | other",
            "sexuality": "heterosexual | homosexual | bisexual | etc.",
            "occupation": "A single plain-text string (not an object): what they do, including their social/economic standing.",
            "appearance": "Full 5-8 sentence paragraph: build, face, hair, style of dress, posture, how they move, voice quality, and what draws the eye first.",
            "physical_characteristics": [
                "A scar through one eyebrow",
                "Chews on pens when thinking",
                "at least 5 total, specific tags",
            ],
            "personality": [
                "Full sentence: specific trait plus how it actually shows up in behavior, speech, or decisions, with a concrete example",
                "at least 5 total",
            ],
            "backstory": "Full 5-8 sentence paragraph: where they came from, the formative event or relationship that shaped them, what they wanted then versus now, and the throughline to who they are on page one.",
            "fears": [
                "Full sentence: the concrete thing they run from plus the specific emotional wound and its origin",
                "at least 3 total",
            ],
            "flaws": [
                "Full sentence: the core flaw plus the specific mechanism of what it does to them and others in practice",
                "at least 2 total",
            ],
            "contradictions": [
                "Full sentence: presents as X but is actually Y, plus the specific behavior that reveals the gap",
                "at least 2 total",
            ],
            "hobbies": ["Specific, scene-usable hobby, not a generic label", "at least 3 total"],
            "spiritual_beliefs": ["Specific belief or practice", "at least 3 total"],
            "character_voice": [
                "Specific note on tone, register, vocabulary, or rhythm",
                "at least 3 total",
            ],
            "speech_patterns": [
                "Concrete, quotable verbal tic or overused phrase",
                "at least 4 total",
            ],
        }
    ]
}


# --- PRIMARY THREAD ---
# The protagonist's full hero's-journey arc, ported and adapted from V2's
# GEN_SPINE_USER_PROMPT (src/prompts/outline.py). V2's spine covered the
# whole cast — protagonist and antagonist arcs run in parallel from the
# start. V3 splits this: this step writes the protagonist's arc (with the
# antagonist as their primary opposing force) in full hero's-journey detail;
# every other named character's arc is handled by secondary arcs and woven
# into the outline afterward, so this step doesn't need to detail arcs for
# characters other than the protagonist and antagonist. This is an internal
# generation input, not user-facing — the outline step is what the user
# actually reads and edits.

INIT_PRIMARY_THREAD_USER_PROMPT = """

Your purpose is to generate the protagonist's primary thread for a story, using the metadata, worldbuilding, and cast already established below. The primary thread is not a chapter outline — it is the structural skeleton of the protagonist's arc from start to finish, in full detail: character moments, feelings, and key events.

--- METADATA ---
{novel_metadata}

--- WORLDBUILDING ---
{worldbuilding}

--- CHARACTERS ---
{characters}

--- WORD COUNT ---

This story's total word count is fixed at {word_count} words — this is not yours to decide, it has already been computed from the user's requested length and the secondary threads attached to this story. Your job is to make the plot point count and each one's word_count_pct proportional to this fixed number: fewer, more focused plot points for a smaller word count, more for a larger one. Do not pad plot points to fill space, and do not write so sparsely that {word_count} words would be too much for the plot you've laid out — the plot's density should genuinely match the target.

--- STRUCTURE ---

Identify the protagonist and the antagonist from the CHARACTERS list above (using their `role` field) and build the primary thread around them. The primary thread is built from character goals outward, not from plot events inward. Every plot point must originate in what the protagonist or antagonist wants, fears, or believes — and what happens when that drive collides with the other's drive or with the world's resistance. If you find yourself writing a plot event and the answer to "why does this happen?" is "because the story needs it to," stop and find the character motivation first.

Every plot point must be grounded in the specific world and characters described above — no generic stand-ins. Do not name or invent new major characters in the primary thread beyond the protagonist and antagonist; minor named characters from the CHARACTERS list may appear but should not carry independent plot weight here.

For each plot point write a dense 4-8 sentence summary. Each summary must answer: whose goal or want is driving this plot point, what are they actively trying to do, what gets in the way or goes wrong, and what has irreversibly changed by the end. Cover the protagonist's emotional state, what their flaw is doing to them here, and the status of their key relationship to the antagonist (and any other character present). The event is the last thing you write, not the first — it is the outcome of the goal collision, not the cause of it. This summary must be unambiguous and detailed enough that a writer could produce prose from it alone — character moments and feelings, not just plot beats.

The primary thread always uses the full hero's journey as its structural skeleton. The `heros_journey_step` field must use one of these labels, in order: ordinary_world, inciting_incident, crossing_threshold, rising_complications, midpoint, antagonist_peaks, all_is_lost, climax, resolution. All 9 steps are required.

  1. ordinary_world — the protagonist's and the antagonist's lives before the story begins. Establish for each: what they stand to lose, what they want, and what internal flaw or false belief they are living under. The two ordinary worlds should already be on a collision course — the same resource, the same person, the same goal pursued from opposite directions. The forbidden element must already be present as an ambient pressure — not triggered yet, but felt.
  2. inciting_incident — a single concrete, irreversible event that disrupts the ordinary world and sets the central conflict in motion. Must be caused by something, not random.
  3. crossing_threshold — the protagonist makes a choice or is forced into full engagement with the conflict. The ordinary world is no longer accessible. The forbidden element becomes an active obstacle here, not just ambient.
  4. rising_complications — the central conflict escalates through a sequence of discrete, connected complications, each harder than the last, each with its own time gap, trigger, and cost. Complications must be WOVEN, not stacked — most should open before the previous one has closed, reaching back and entangling with an earlier still-open complication rather than resolving cleanly before the next begins. Every complication must trace back to the same central conflict. The forbidden element must actively create or worsen at least one of these complications.
  5. midpoint — a major revelation, reversal, or commitment at the exact halfway point of the story. What the protagonist wants or believes must visibly change. The story is different after this plot point.
  6. antagonist_peaks — the antagonist reaches maximum pressure. The protagonist's current approach is failing or has failed.
  7. all_is_lost — the protagonist loses the thing they wanted most as a direct consequence of their own flaw or choice. Not bad luck, not an outside force — their own doing. The goal must appear permanently out of reach. The forbidden element contributes to or is exposed by this collapse.
  8. climax — the protagonist confronts the central conflict directly, through their own agency. The immediate outcome — victory, defeat, or something more ambiguous — lands here, whatever is consistent with the story's tone. This is not automatically a triumph; treat this as the outcome as the protagonist and reader experience it in the moment.
  9. resolution — where the story's true, lasting outcome lands. The forbidden element must be addressed: resolved, paid for, or accepted with consequences. The resolution is a landing, not a coda — it closes with a single decisive beat. No rumination, no drawn-out emotional processing, no epilogue energy. If the story's tone is tragic, bleak, or bitter, the resolution must reflect that — no false hope or softening unless the intro prompt specifically calls for one.

Additional rules:
  - The flaw established in ordinary_world must be the direct cause of all_is_lost. The climax resolves what the flaw produced.
  - The central conflict introduced at inciting_incident must be the thing resolved at the climax. Do not resolve it early and introduce a new one.
  - The antagonist runs a parallel arc through the entire primary thread, active from ordinary_world onward, colliding with the protagonist's arc in the back half. The antagonist's arc is subordinate to the protagonist's: present as a force the protagonist reckons with, not a co-lead. The protagonist stays the fixed point-of-view center across all 9 steps.
  - For every plot point, state the specific duration since the previous one ("three days later", "the same evening"). "Some time passes" is not sufficient.
  - Stakes must escalate as the story progresses — later plot points must be more dramatically weighty, hardcore, or consequential than earlier ones, not merely wider in word_count_pct. A complication introduced late in rising_complications must hit harder and cost more than one introduced early in it. Do not front-load the story's biggest or most intense moment near ordinary_world or inciting_incident and coast afterward — every step from crossing_threshold onward should feel like it raises the ceiling on what came before, building toward antagonist_peaks/all_is_lost/climax as the story's most intense points.
  - Before finalizing, audit the plot points you have written against each other for repetition: no two plot points may reuse the same core story beat (the same kind of betrayal, the same kind of confrontation, the same revelation, the same type of near-miss) even if dressed in different scene details. If you find a repeated beat, rewrite the later occurrence into a genuinely different kind of event that still serves its hero's-journey step's function.

--- GAZE AND SPICE ARC ---

This story must satisfy both the female gaze (emotional interiority, anticipation, the protagonist's internal experience of desire, earned intimacy) and the male gaze (direct, confident, visually-forward physical appreciation) simultaneously. Map the romantic and sexual tension arc across the plot points: for each, note whether the intimate arc role is tension-building, escalation, payoff, or none. The forbidden element must be actively creating pressure in every tension-building and escalation plot point. The first payoff must be earned — at least one tension-building and one escalation plot point must precede it. Payoffs are a required minimum, not optional: at least 3 across the primary thread, distributed across the back three-quarters (crossing_threshold onward), each delivering fully — nothing withheld, nothing faded-to-black unless the metadata specifies otherwise.

--- HOW INTIMATE SCENES OPEN ---

Vary how intimate scenes actually open and unfold. Do not default to a repeating "plot event happens, then they have sex" pattern — it gets mechanical and predictable fast. For every plot point marked payoff (and for escalation plot points carrying real physical contact), choose a structural entry mode, record it in the `intimate_entry_mode` field, and write the summary so the chosen mode is visible in how the scene is described. Rotate deliberately through these:

  - already_in_progress — the scene opens mid-encounter with no plot buildup at all, dropped straight into it. The complication is revealed only afterward: where they are, who is nearby, how little time they have. Whatever the story's world makes risky is the complication — a hiding place during a public event, someone on the other side of a thin wall, a hard deadline both of them are counting down.
  - interrupted — the intimacy is broken partway through by something from the story's world crashing in: a knock, a summons, a message, someone almost walking in. They have to compose themselves and perform normalcy seconds later, with the interruption itself unresolved.
  - escalated_in_real_time — the encounter genuinely emerges out of a non-intimate scene as it heats up on the page: an argument, a negotiation, a shared task, a moment of danger tipping over into it without either of them deciding to.
  - no_trigger — nothing causes it. No plot event, no fight, no confession. Just proximity and accumulated history catching up with them.
  - consequence — the payoff does follow directly from the plot event. This mode is allowed, but it is one of five, not the default.

Mix these across the primary thread rather than settling into any single one. Do not use the same mode for two consecutive payoffs, and do not let `consequence` account for more than one payoff in the story. Whatever the setting is — workplace, court, ship, road, battlefield — draw the risk, the interruption, and the stolen time from that world's specifics, not from generic romance staging. The unpredictability of how and when intimacy happens is part of what makes these scenes land.

--- PACING ---

The word_count_pct values across all plot points must sum to 100. Use the following distribution as your target — adjust by up to 3 percentage points to serve the specific story, but do not deviate beyond that:

  ordinary_world:        10%
  inciting_incident:      6%
  crossing_threshold:     8%
  rising_complications:  28%
  midpoint:               8%
  antagonist_peaks:      14%
  all_is_lost:            8%
  climax:                10%
  resolution:             8%

Before returning, validate: the plot point count and word_count_pct distribution are proportional to the fixed {word_count}-word target (not padded toward a higher number, not sparse enough to leave the target unfilled), word_count_pct values sum to 100, no plot point summary is vague enough to be interpreted two different ways, the protagonist and antagonist both have a clear final state at resolution, no two plot points repeat the same core story beat, and each plot point from crossing_threshold onward is more dramatically intense than the one before it.

Then return the primary thread as a JSON object using the schema below. Do not stray from this schema.

{schema}

Return only the JSON object, no other text.

"""

INIT_PRIMARY_THREAD_SCHEMA = {
    "primary_thread": [
        {
            "heros_journey_step": "ordinary_world | inciting_incident | crossing_threshold | rising_complications | midpoint | antagonist_peaks | all_is_lost | climax | resolution — all 9 steps are required, in order",
            "summary": "Dense 4-8 sentence description of this plot point: whose goal drives it, what they're trying to do, what goes wrong, what has changed by the end. Cover the protagonist's emotional state, active flaw, and relationship status to the antagonist.",
            "word_count_pct": 10,
            "time_gap_before": "How much time has passed since the previous plot point, e.g. 'same day', 'two weeks later', 'immediately'.",
            "forbidden_element_active": True,
            "intimate_arc_role": "tension-building | escalation | payoff | none",
            # How the intimate scene opens; "none" when intimate_arc_role is none.
            "intimate_entry_mode": "already_in_progress | interrupted | escalated_in_real_time | no_trigger | consequence | none",
        }
    ]
}


# --- SECONDARY ARCS ---
# One arc per secondary_thread, generated in lighter detail than the
# primary thread — a separate, focused call so the primary thread
# doesn't have to compete for space/attention with N other storylines. Each
# arc is generated independently of the others; init_outline is the step
# that later weaves each arc's beats into the final outline.
#
# This step ALWAYS generates the thread's complete arc, ignoring `length`
# entirely — self-truncation here was the source of a recurring bug where
# threads leaked their full resolution into the story regardless of `length`.
# Truncation is now done mechanically in Python (see
# generation.truncate_secondary_arc, called from router.create_novel) by
# slicing the returned plot_points array down to the leading length% of
# points *before* anything is persisted or handed to init_outline — so the
# model's self-estimation of "how much is enough" is no longer load-bearing.
#
# The arc uses a fixed 12-stage skeleton (seed..landing) for the same reason
# the primary thread uses the 9 hero's-journey steps: a named, mandatory
# structure is something the model cannot quietly return less of, and it can
# be validated by label. The previous "at least 10-15 plot points" was a soft
# floor with nothing to check against, and short responses (4 points or fewer)
# made the percentage cut meaningless — at 4 points, length=30 keeps 2, which
# is half the arc. Twelve evenly-spaced stages give the cut room to land
# somewhere genuinely partial. See router.create_novel for the validation.

INIT_SECONDARY_ARCS_USER_PROMPT = """

The following is everything already established for this story. Do not stray from it.

--- METADATA ---
{novel_metadata}

--- WORLDBUILDING ---
{worldbuilding}

--- CHARACTERS ---
{characters}

--- PRIMARY THREAD ---
{primary_thread}

--- SECONDARY THREADS ---
{secondary_threads}

--- INSTRUCTIONS ---

For each secondary thread listed above, write its FULL natural arc, start to finish, ending on a real, concrete resolution — a complete short story with a beginning, middle, escalation, and ending. This is lighter detail than the primary thread, not a full hero's-journey breakdown, but it must genuinely be the whole story, not a fragment.

A thread's `description` may itself already be a full arc, written by the user start to finish, including its own ending — not just a premise for you to invent a story from. When that's the case, your job is to expand that existing arc into plot points, not replace it with a different one: map the user's own described events onto the 12 stages below, in the same order they occur in the description, preserving their actual ending as the `landing` stage. Do not invent a different or earlier ending than the one the user already wrote, and do not compress the back half of their description into fewer, denser points than the front half just because it's the ending — every part of their arc, including the ending, gets the same granular, plot-point-by-plot-point treatment. This matters because of how `length` works below: it is a percentage through THIS plot-point breakdown, and that breakdown needs to proportionally track the user's own original pacing — if their description spends half its length setting up and half resolving, your plot points should too, so that a `length` cutoff partway through lands at a correspondingly partial point in their actual story, not artificially close to (or past) events they placed near the end.

Every secondary thread uses the following 12-stage skeleton as its structure. The `arc_stage` field must use one of these labels, in order, and all 12 stages are required — exactly one plot point per stage, 12 plot points per thread:

  1.  seed — the thread's situation before anything disturbs it. Establish who is involved and what they currently want.
  2.  first_friction — the first small thing that goes wrong or pushes back. Minor, easily shrugged off.
  3.  commitment — someone decides to actually pursue this, making the thread an active storyline rather than ambient tension.
  4.  complication_one — the first real obstacle, with a concrete cost.
  5.  complication_two — a second obstacle that entangles with the first rather than replacing it.
  6.  midpoint_shift — something is revealed or reversed that changes what the participants think they are dealing with.
  7.  deepening — the stakes become personal; what was a problem becomes something that matters emotionally.
  8.  setback — a real loss. The approach taken so far visibly fails.
  9.  forced_choice — someone must choose between two things they want, and cannot keep both.
  10. crisis — maximum pressure, the point of no return for this thread.
  11. confrontation — the thread's central tension is faced directly.
  12. landing — the thread's lasting outcome. Its concrete, final resolution.

This fixed structure exists for a specific mechanical reason: after you write this complete arc, a separate process cuts it down to only the leading fraction implied by that thread's `length` value (e.g. length 30 keeps roughly the first 30% of your plot points — stages 1-4), and everything past that cutoff is discarded before anyone else ever sees it. Twelve evenly-spaced stages give that cutoff room to land somewhere genuinely partial. If you wrote only four plot points, "the first 30%" would keep two of them — half the story, not 30% of it — and a thread compressed into four points is so dense that even half already reads as nearly the whole plot.

So: do not merge stages, do not skip stages, and do not compress several stages into one plot point. Each of the 12 gets its own. Ground each thread in a specific character or characters from the CHARACTERS list above — do not invent new major characters, though a thread may introduce a minor walk-on character if the thread genuinely needs one.

The `secondary_arcs` array in your response must have exactly one entry per thread in SECONDARY THREADS above, in the SAME ORDER they are listed there — the first thread listed gets the first entry in your response, the second thread the second entry, and so on. Do not skip a thread, do not add an extra entry, do not reorder them. Position in the array is how each arc is matched back to its thread — there is no name or id field to match on, so getting the order and count exactly right is required, not optional.

Each secondary thread has a `length` value (0-100). Ignore it completely for this step — do not shorten, hold back, or stop early because of it, even for a thread with a low length value. Something else, outside this step, decides how much of what you write here actually gets used in the final story; it needs your complete, unabridged arc to work with. Writing a partial or deliberately unresolved arc here — for any reason, including a low `length` value — is a failure condition.

Each secondary thread also has a `priority` (0-100) — how large a share of the final outline this thread will occupy, decided later when this arc is woven into the outline; not your concern at this step. Also has a `heat` (0-100, romantic/sexual intensity specific to that thread) — use heat to decide how much romantic or sexual charge this specific thread carries, independent of the story's overall spice_level — a low-heat thread (e.g. a rivalry or a mystery) should carry none, while a high-heat thread should be written with real romantic/sexual tension.

For each thread, also decide its own word_count — an integer between 3000 and 8000 — based on how much plot the complete arc actually contains. This describes the full arc you are writing here, not any fraction of it.

For each plot point, write a compact 2-4 sentence description — who is present, what concretely happens, and what changes. Enough specific detail that the point could be dropped into an outline beat without anyone having to invent what actually occurred, but no more than that: the outline step expands these into full scenes later, so this step needs precision, not prose. There are 12 of these per thread; keep each one tight. Note which characters are present. Do not contradict anything established in the primary thread, metadata, or worldbuilding.

Within each thread, stakes must escalate from the first plot point to the last, building all the way to that final resolution — each later plot point should carry more weight or cost than the one before it. Do not put the thread's most dramatic or consequential moment first and taper off afterward.

Before finalizing, audit for repetition at two levels. First, within each thread: no two plot points in the same thread may reuse the same core story beat (the same kind of betrayal, confrontation, revelation, or near-miss) in different dress. Second, across everything already established: no secondary arc's plot point may reuse a core story beat already used in the PRIMARY THREAD above, or in another secondary thread you are generating in this same batch — if a secondary thread's natural idea collides with something already used, invent a different concrete event that still serves the same narrative function for that thread. A shared theme or motif across threads is fine; a repeated beat is not.

Before returning, validate: the secondary_arcs array has exactly one entry per thread in SECONDARY THREADS, in the same order, with no thread skipped, duplicated, or reordered; every thread has exactly 12 plot points carrying all 12 `arc_stage` labels in order, ending on `landing` — count them, and if any thread is missing a stage, go back and write it before returning; for any thread whose `description` was itself already a full user-written arc, confirm your plot points map it onto the 12 stages in its original order, with its actual given ending preserved as the `landing` stage, not replaced or reached early; every thread's arc is genuinely complete, ending on a real, concrete resolution, with nothing held back regardless of that thread's length value; every thread traces back to real characters from the CHARACTERS list; no thread contradicts the primary thread; no plot point repeats a core story beat already used elsewhere in this thread, another thread, or the primary thread; each thread's plot points escalate rather than front-load their biggest moment; and every thread's word_count is between 3000 and 8000 and proportional to how much plot the complete arc actually contains.

Then return the secondary arcs as a JSON object using the schema below. Do not stray from this schema.

{schema}

Return only the JSON object, no other text.

"""

# Appended to the secondary-arcs prompt on the one retry allowed when the
# first response came back missing stages (see router.create_novel).
INIT_SECONDARY_ARCS_CORRECTION_TEMPLATE = """

--- CORRECTION: YOUR PREVIOUS ATTEMPT WAS REJECTED ---

Your last response did not follow the 12-stage skeleton. Specifically:

{problems}

Every thread needs all 12 stages — seed, first_friction, commitment, complication_one, complication_two, midpoint_shift, deepening, setback, forced_choice, crisis, confrontation, landing — as 12 separate plot points, each tagged with its `arc_stage`, ending on `landing`.

Do not merge stages together, do not skip any, and do not stop early. If you are worried about length, make each plot point's summary shorter — but write all 12 of them for every thread. A thread missing stages is unusable and will be rejected again.

"""

INIT_SECONDARY_ARCS_SCHEMA = {
    "secondary_arcs": [
        {
            "word_count": 5000,
            "plot_points": [
                {
                    "arc_stage": "seed | first_friction | commitment | complication_one | complication_two | midpoint_shift | deepening | setback | forced_choice | crisis | confrontation | landing — all 12 stages are required, in order, one plot point each",
                    "summary": "Compact 2-4 sentence description of this plot point: who is present, what concretely happens, what changes. Specific enough to use directly, but tight — there are 12 per thread and the outline step expands them into full scenes later. This is the COMPLETE arc — every plot point through to the ending, never truncated.",
                    "characters_involved": ["Exact name of a character from the CHARACTERS list"],
                }
            ],
        }
    ]
}


# --- OUTLINE ---
# Merges the primary thread (the protagonist's full hero's-journey beats)
# and the secondary arcs into a single, detailed, ordered outline document —
# the one artifact the user actually reads and edits. Everything upstream
# (primary thread beats, secondary arcs) is internal generation input now;
# this is the first step whose output is persisted as the user-facing
# outline of the story. Hero's-journey step labels are not part of this output —
# that structure already did its job in the primary/secondary generation
# steps; this step just needs to place secondary content at the right point
# in the primary thread's timeline and write the whole thing out as prose.

INIT_OUTLINE_USER_PROMPT = """

The following is the primary thread and the secondary arcs already generated for this story. Do not inject new plot events, characters, or twists — your job is to combine what already exists into one detailed, continuous outline, not to invent new story content.

--- PRIMARY THREAD ---
{primary_thread}

--- SECONDARY ARCS ---
{secondary_arcs}

--- WORD COUNT ---

This story's overall target is {word_count} words. Each beat's word_count (see below) is your estimate of that beat's own eventual prose length, not a percentage — but across the whole outline, those estimates should roughly add up toward this target. Getting close is enough; this is a target to write toward, not a total to hit exactly.

--- INSTRUCTIONS ---

Write the full outline of this story as an ordered sequence of beats, from the very beginning to the very end. This is a detailed prose outline, like a writer's beat sheet — not a chapter list, not a summary. Each beat must be a full, dense multi-paragraph passage (aim for 200-400 words per beat, more for beats covering more ground) — a couple of sentences per beat is a failure condition, no matter how short the beat's word_count is. Write out concretely what happens, who is involved, what changes, and how it connects to the beat before and after it, at a level of granularity closer to a scene-by-scene breakdown than a summary: cover the specific sequence of actions within the beat, not just its net result: the sub-moments the scene turns on, at least one specific line or fragment of dialogue or interior thought where it strengthens the beat, the setting's sensory texture (what the space looks, sounds, or feels like), and the emotional shift each character present undergoes over the course of the beat. Be specific: name characters, name places, name the actual events — never a vague placeholder like "they talk about their feelings" or "tension rises between them" standing in for what is actually said or done. This should be long and detailed enough that a writer could draft the story from it beat by beat without having to invent anything load-bearing.

Beats covering a secondary thread must be written with this same density and specificity — real characters, real places, real dialogue or interior thought, full sensory texture, the 200-400 word target. These threads are the primary threads of a future story and deserve to be treated that way on the page.

Each beat in the PRIMARY THREAD above already has its own place in the story's timeline — use those, in order, as the backbone of the outline. Each secondary arc is identified only by its `thread_index` (its position in the SECONDARY ARCS list, not a name or description — none is given, and none should be assumed or invented). Each arc's plot_points array is already in order, and each plot point carries a `plot_point_index` (its position within that thread, starting at 0). Each arc also carries the thread's `priority` and a `continues_after_story` flag (see below). Weave each secondary arc's plot points into the backbone at the point in the timeline where they belong.

A secondary thread's plot points must be SPREAD ACROSS the primary timeline, not dumped in together. Do not place a thread's plot points in consecutive or near-consecutive beats just because they're already in order relative to each other — that reads as one block of story interrupting the main plot rather than a thread genuinely running alongside it. Instead, distribute each thread's points across the portion of the timeline the thread is actually active in: its first point lands early, its later points land at meaningfully later points in the primary story, with real primary-thread (and other secondary) material happening in between. A secondary thread that quietly recedes for a stretch of the story and then resurfaces is normal and good — readers should be reminded of it periodically, not handed all of it in one sitting.

`priority` (0-100) is how much of the OUTLINE'S TOTAL WORD COUNT this thread should occupy — its share of the sum of every beat's word_count across the whole story — and it is independent of how many plot points the thread has. These are separate dials: a thread can have very few plot points but still be high `priority`, meaning the outline should spend a large amount of total words lingering on, returning to, and dwelling in that small amount of content — revisiting the same plot points across more beats, giving each of those beats a larger word_count, and cutting back to this thread more often — rather than racing through it in one quick beat just because there isn't much plot to cover. A low-priority thread gets touched on briefly and infrequently regardless of how much plot it has. Use `priority` to size each secondary thread's overall footprint in the outline; the number of plot points only bounds how much distinct plot content exists to draw that footprint from.

You are free to split, merge, or reorder how the primary and secondary material is grouped into beats — the goal is a well-paced, coherent outline, not a mechanical concatenation of the inputs. A single outline beat may cover primary-thread content, secondary-thread content, or both woven together in the same beat, whichever reads more naturally at that point in the story.

--- HOW INTIMATE BEATS OPEN ---

Each plot point carrying an intimate payoff already specifies how that scene opens in its `intimate_entry_mode` field — already_in_progress, interrupted, escalated_in_real_time, no_trigger, or consequence. Honor that mode when you stage the beat, and write the beat's opening lines to match it: a beat marked already in progress starts inside the encounter, not with the walk to the room; an interrupted beat must actually show the interruption landing and the two of them performing normalcy immediately after, with whatever broke in left unresolved.

Where a payoff's `intimate_entry_mode` is missing or `none`, pick one and vary it — do not stage every intimate beat as "the plot event happens, then they go to bed." Across the whole outline, the intimate beats should differ in how they begin, where they happen, and how much warning anyone gets. Draw the risk and the interruptions from this story's actual world and the places named in it.

--- SOME SECONDARY THREADS DO NOT END IN THIS STORY ---

A thread marked `continues_after_story: true` is a storyline that does not end in this book. The plot_points you were given for it are only its opening stretch — the rest of that storyline was deliberately withheld before this step, and you do not have it. It belongs to a future story.

For these threads, the last given plot point is not an ending and must not be written as one. Write that final beat so the thread is visibly STILL IN MOTION as the book closes — land it on something concretely unfinished: a question nobody has answered yet, a cost that hasn't come due, a decision someone is still carrying, a door left open. The reader should finish the book expecting more of this storyline, not feeling it wrapped up quietly offstage. That open state is the intended effect, not a gap you should patch.

Render each given plot point in full scene detail, exactly as described above, and let the thread end wherever its content actually ends. Everything past that point is unknown to you — do not invent, imply, foreshadow, or narrate any outcome you were not handed, and do not let a character voice a conclusion about where the thread is heading. If the last given plot point ends mid-tension, the beat you write from it ends mid-tension too.

Do not let a `continues_after_story` thread's last beat land at or after the primary thread's climax/resolution beats — place it earlier in the timeline if needed, so the book's ending belongs to the primary storyline.

A thread marked `continues_after_story: false` was given its real ending and should be written all the way through it.

The outline's main job is to weave the secondary threads into the primary story naturally, not bolt them on as separate beats sitting beside it. Whenever a secondary plot point's characters and situation plausibly overlap in time and place with a primary scene happening around the same point in the timeline — same room, or clearly concurrent even if not the same room (e.g. the next room over during the same event) — merge them into one beat, with the secondary material folding into what's already happening in that scene. Give a secondary plot point its own standalone beat only when it genuinely has no time/place overlap with any nearby primary scene. This overlap check is the only thing that decides whether a beat merges; `priority` does not make a thread merge more or less — it only controls that thread's overall footprint (see above), which you deliver through how often you return to it and how large a word_count its beats (merged or standalone) get.

Assign each beat a word_count — your estimate, as a plain integer, of how many words that beat will actually run to once it is drafted into full prose. These must vary — do not make every beat roughly the same size. Some beats are short, sharp, and consequential (a single confrontation, a single reveal); others need more room to breathe (a longer sequence of rising complications, an extended scene). The rhythm of long and short beats matters as much as the content — avoid a flat, uniform pace. A high-priority secondary thread's beats should individually claim a larger word_count, and/or the thread should be returned to across more beats, so its cumulative word_count share of the outline's total actually reflects its priority — not just how many plot points it has.

Before returning, validate: for each secondary thread, its plot points land at genuinely spread-out points across the timeline, not bunched into one consecutive run of beats with no primary-thread material between them — if you find a thread whose points are all clustered together, redistribute them before returning; every beat in the PRIMARY THREAD has been accounted for somewhere in the outline in its original order; every secondary arc plot point (every thread_index + plot_point_index pair) has been placed exactly once, in the order it was given; every `continues_after_story` thread ends on a visibly unfinished note with its last beat placed before the climax, reading as a storyline still running rather than one quietly wrapped up; every merged secondary beat genuinely overlaps in time/place with the primary scene it was folded into, and every standalone secondary beat genuinely does not; each secondary thread's cumulative word_count share of the outline roughly tracks its `priority`; no beat narrates anything beyond what its source plot points actually describe; word_count values are not uniform; the intimate beats do not all open the same way, and no two consecutive ones use the same entry mode; every beat's content is a full multi-paragraph passage in the 200-400+ word range with at least one concrete line of dialogue or interior thought and specific sensory detail, not a short summary; and no beat is vague enough that a writer would have to invent what actually happens.

Then return the outline as a JSON object using the schema below. Do not stray from this schema.

{schema}

Return only the JSON object, no other text.

"""

# Appended to the outline prompt on the one retry allowed when the first
# response was cut off by the model's output limit (see init_outline).
INIT_OUTLINE_LENGTH_CORRECTION = """

--- CORRECTION: YOUR PREVIOUS ATTEMPT RAN OUT OF ROOM ---

Your last response was cut off before it finished — the full outline did not fit in the output limit.

Write the same outline again, covering every beat from beginning to end, but tighter: aim for roughly 150-200 words per beat instead of 200-400. Keep the concrete specifics — the named characters and places, the actual events, one line of dialogue or interior thought where it matters — and cut the elaboration around them. A complete outline at 150 words per beat is far more useful than a detailed one that stops halfway, so covering the whole story end to end takes priority over per-beat density.

"""

INIT_OUTLINE_SCHEMA = {
    "outline": [
        {
            "content": "Specific, concrete beat description at whatever length the beat actually needs — a brief moment can be a couple of sentences to a short paragraph, a full scene several dense paragraphs. Covers the specific sequence of actions and sub-moments, who is involved, at least one concrete line of dialogue or interior thought where length allows, sensory texture of the setting, each present character's emotional shift, what changes, and how it connects to the surrounding beats. Specific enough to draft prose from directly with nothing load-bearing left to invent.",
            "word_count": 350,
        }
    ]
}


# --- ENTITIES ---
# Ported and merged from V2's separate locations/items/organizations/events
# steps (src/prompts/outline.py) into a single call. Cross-references here
# are anchored to the novel's premise/summary, primary thread, and character
# list, and characters/organizations are cross-referenced by name rather
# than by a spine-assigned uuid (V3's primary thread plot points aren't
# uuid-addressable the way V2's were).

INIT_ENTITIES_USER_PROMPT = """

The following is the metadata, worldbuilding, cast, and primary thread already established for a story. Do not stray from them.

--- METADATA ---
{novel_metadata}

--- WORLDBUILDING ---
{worldbuilding}

--- CHARACTERS ---
{characters}

--- SPINE ---
{primary_thread}

--- LOCATIONS ---

Generate a rich and varied set of locations that populate this story's world. Think spatially and socially: where do people live, work, eat, drink, hide, fight, worship, conduct business, find pleasure, suffer consequences? What locations would a person in this world encounter in the natural course of living? They do not all need to be plot-critical — some exist to give the world texture and give prose writers somewhere to put characters. Make each one distinct in atmosphere, purpose, and feel — no two should read the same. Write atmospheric and physical detail sufficient to write scenes there: what it looks like, what it smells and sounds like, its mood, its access rules if any, its significance to the story.

--- ITEMS ---

Generate a rich and varied inventory of objects that populate this story's world. Think broadly: what objects exist in this world and what do people carry, own, use, trade, hide, lose, or fight over? Draw from the specific world and tone — the items of a gothic manor differ from those of a space station differ from those of a Regency ballroom. Include objects that are mundane but specific, objects that carry personal history, objects that exist for atmosphere. Key items get full detail including symbolic weight. Minor objects get a brief note.

--- ORGANIZATIONS ---

Generate a rich and varied set of organizations that populate this story's world. Think about the layers of society that would exist here: governments, courts, guilds, churches, criminal syndicates, mercenary companies, trading houses, secret societies, noble houses, political factions, gangs, clubs, brotherhoods, institutions of learning or medicine or law, cults, unions, press outlets, intelligence agencies — whatever fits this world. Organizations do not all need to directly touch the plot — some exist to give the world institutional texture, to explain why things work the way they do, to give characters something to belong to or resist. Make each one distinct in type, goals, and tone. Write full detail as a single flowing prose description (a plain string, not a nested object with separate fields) that covers its goals, resources, access conditions, internal power structure, and what pressure it applies to the plot — woven together into ordinary paragraph text, the same way the LOCATIONS and ITEMS descriptions are written.

--- EVENTS ---

Using the metadata, worldbuilding, cast, and the locations/items/organizations you just generated, expand each primary thread plot point above into a concrete event — turning points, confrontations, revelations, and key moments consistent with the forbidden element and the protagonist's arc. Every event must map to a real primary thread plot point; do not invent events unconnected to the primary thread. For each, write enough detail to make it writable: who is present, what concretely happens, what changes as a result, what the emotional weight of the moment is, and whether it has occurred, is pending, or was prevented by the time the story begins. Every name listed in characters_involved must be an exact name from the CHARACTERS list above. Every name listed in organizations_involved must be an exact name from the organizations you generated above. Do not invent events that contradict the metadata, worldbuilding, or primary thread.

Before returning, validate: every location, item, and organization is distinct and fits the world and tone of the intro prompt; every entity's `description` (and every event's `description`) is a single plain string of prose, never a nested object with separate named fields; every event maps to a primary thread plot point; every event's characters_involved and organizations_involved names match entries generated above exactly, with no placeholder or invented names.

When completed, format everything into a single JSON object that follows the format below. Do not stray from this schema.

{schema}

Return only the JSON object, no other text.

"""

INIT_ENTITIES_SCHEMA = {
    "locations": [
        {
            "name": "Location name",
            "description": "Plain prose string (not an object): what it looks like, sounds like, smells like, its mood, its access rules if any, and its significance to the story.",
        }
    ],
    "items": [
        {
            "name": "Item name",
            "description": "Plain prose string (not an object): what it is, its symbolic weight, and its significance.",
        }
    ],
    "organizations": [
        {
            "name": "Organization name",
            "description": "Plain prose string (not an object with separate fields): its goals, resources, access conditions, internal power structure, and what pressure it applies to the plot, all woven into one flowing description.",
        }
    ],
    "events": [
        {
            "title": "Event name",
            "description": "Plain prose string (not an object): what happens, what changes as a result, the emotional weight, and whether it has occurred, is pending, or was prevented.",
            "characters_involved": ["Exact name of a character from the CHARACTERS list"],
            "organizations_involved": ["Exact name of an organization generated above"],
        }
    ],
}


# --- INITIAL STATE ---
# The starting relationship graph, as of story-start (before chapter one).
# Character-outward and asymmetric: a relationship is only emitted from a
# character's side if it actually exists for them. Do not emit a symmetric
# pair by default — if the protagonist has never met a character, there must
# be no character_relationships entry for protagonist -> that character, even
# if that character has a real, populated entry pointing at the protagonist
# (e.g. a stalker who knows the protagonist well).

INIT_RELATIONSHIPS_USER_PROMPT = """

The following is everything already established for this story: metadata, cast, and world. Do not stray from them.

--- METADATA ---
{novel_metadata}

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

Establish the relationship graph as it stands at the moment the story begins — before chapter one, reflecting everything implied by the metadata, character stubs, and events above.

This is character-outward and asymmetric. For each character, only emit a relationship entry — to another character, or to an item or location — if that character actually has one. Do not generate an entry for every possible pair; most pairs in an ensemble cast have no relationship yet and must be skipped entirely. A relationship existing from one side does not mean it exists from the other: if the protagonist has never met a character, emit nothing for protagonist -> that character, even if that character knows the protagonist well and has a real entry pointing back at them (a stalker, a spy, a secret admirer, a family member the protagonist doesn't remember). One-sided relationships are expected and correct, not a mistake to fix.

For character-to-character relationships, only include emotional_intensity when there is a real emotional charge to the relationship — leave it out (or use 0) for something genuinely neutral like a distant acquaintance.

For character-to-item and character-to-location relationships, only emit entries for connections that actually matter to the story — an item they own or are searching for, a location that's their home or that they're barred from. Do not emit an entry just because a character has technically seen or passed through a location, or could plausibly know an item exists.

Every character, item, location, and organization name used below must be an exact name from the lists above — no invented or placeholder names.

When completed, format everything into a single JSON object that follows the format below. Do not stray from this schema.

{schema}

Return only the JSON object, no other text.

"""

INIT_RELATIONSHIPS_SCHEMA = {
    "character_relationships": [
        {
            "character": "Exact name of the character this relationship belongs to",
            "target_character": "Exact name of the other character",
            "relationship_type": "e.g. rival | ally | mentor | romantic_tension | family | stranger | threat",
            "status": "Current status of the relationship in plain language.",
            "emotional_intensity": 6,
            "open_threads": "What is unresolved between them, in plain language.",
        }
    ],
    "entity_relationships": [
        {
            "character": "Exact name of the character this relationship belongs to",
            "entity_type": "item | location",
            "entity": "Exact name of the item or location",
            "relationship_type": "e.g. owner | custodian | seeking | home | banned | sacred",
            "status": "Current status of the relationship in plain language.",
            "open_threads": "What is unresolved about it, in plain language.",
        }
    ],
}

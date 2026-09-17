from pydantic import BaseModel, Field


class Novel(BaseModel):
    id: str
    prompt: str
    title: str
    summary: str | None = None
    author: str | None = None
    word_count: int | None = None
    premise: str
    primary_genre: str | None = None
    sub_genres: list[str] = []
    tone: str | None = None
    themes: list[str] = []
    spice_level: str | None = None
    literary_voice: str | None = None
    tense: str | None = None
    perspective: str | None = None
    forbidden_element: str | None = None
    story_type: str | None = None
    time_period: str | None = None
    anchor_location: str | None = None
    anchor_location_description: str | None = None
    constraints: list[str] = []
    tone_notes: str | None = None
    characters_notes: str | None = None
    primary_thread: str | None = None
    romance_content: str | None = None
    # Decided by init_primary_thread (10000-14000), based on how much plot
    # the protagonist's arc actually needs. Null until that step runs.
    primary_word_count: int | None = None
    # Model alias actually used for each pipeline step at creation time (the
    # chosen alias, or the step default if none was chosen). Persisted so the
    # Prompts tab can preload the same choices for regeneration.
    metadata_model: str | None = None
    characters_model: str | None = None
    worldbuilding_model: str | None = None
    primary_thread_model: str | None = None
    secondary_arcs_model: str | None = None
    outline_model: str | None = None
    entities_model: str | None = None
    initial_state_model: str | None = None
    metadata_reasoning: bool = False
    characters_reasoning: bool = False
    worldbuilding_reasoning: bool = False
    primary_thread_reasoning: bool = False
    secondary_arcs_reasoning: bool = False
    outline_reasoning: bool = False
    entities_reasoning: bool = False
    initial_state_reasoning: bool = False


class NovelSummary(BaseModel):
    id: str
    title: str
    premise: str


# Subplot seed attached to a novel. length is the percentage of that
# storyline actually resolved in this story (the rest is left open for a
# later story). priority is narrative weight; heat is romantic/sexual
# intensity specific to that thread. All three range 0-100. word_count is
# decided by init_secondary_arcs (2000-4000) and is null until that step runs.
class SecondaryThread(BaseModel):
    id: str
    novel_id: str
    description: str
    length: int
    priority: int
    heat: int
    word_count: int | None = None


class SecondaryThreadCreate(BaseModel):
    description: str
    length: int
    priority: int
    heat: int


class SecondaryThreadUpdate(BaseModel):
    description: str | None = None
    length: int | None = None
    priority: int | None = None
    heat: int | None = None
    word_count: int | None = None


class Character(BaseModel):
    id: str
    novel_id: str
    name: str
    role: str | None = None
    age: int | None = None
    gender: str | None = None
    sexuality: str | None = None
    occupation: str | None = None
    appearance: str | None = None
    physical_characteristics: list[str] = []
    personality: list[str] = []
    backstory: str | None = None
    fears: list[str] = []
    flaws: list[str] = []
    contradictions: list[str] = []
    hobbies: list[str] = []
    spiritual_beliefs: list[str] = []
    character_voice: list[str] = []
    speech_patterns: list[str] = []


# One beat of the final, user-facing outline, in order. Written by
# init_outline, which weaves the (internal) primary thread and secondary
# arcs into this single detailed sequence. word_count is an absolute
# estimate of how many words this beat will run to once drafted into prose
# (not a percentage — beats vary freely in length, from a brief moment to a
# long scene, so there's no fixed total these need to sum to).
class OutlineBeat(BaseModel):
    id: str
    novel_id: str
    sort_order: int
    content: str
    word_count: int | None = None


class OutlineBeatUpdate(BaseModel):
    content: str | None = None
    word_count: int | None = None


class Location(BaseModel):
    id: str
    novel_id: str
    name: str
    description: str | None = None


class Item(BaseModel):
    id: str
    novel_id: str
    name: str
    description: str | None = None


class Organization(BaseModel):
    id: str
    novel_id: str
    name: str
    description: str | None = None


class Event(BaseModel):
    id: str
    novel_id: str
    title: str
    description: str | None = None
    characters_involved: list[str] = []
    organizations_involved: list[str] = []


class CharacterRelationship(BaseModel):
    id: str
    novel_id: str
    character_id: str
    target_character_id: str
    relationship_type: str | None = None
    status: str | None = None
    emotional_intensity: int | None = None
    open_threads: str | None = None


class EntityRelationship(BaseModel):
    id: str
    novel_id: str
    character_id: str
    entity_type: str
    entity_id: str
    relationship_type: str | None = None
    status: str | None = None
    open_threads: str | None = None


class CharacterUpdate(BaseModel):
    name: str | None = None
    role: str | None = None
    age: int | None = None
    gender: str | None = None
    sexuality: str | None = None
    occupation: str | None = None
    appearance: str | None = None
    physical_characteristics: list[str] | None = None
    personality: list[str] | None = None
    backstory: str | None = None
    fears: list[str] | None = None
    flaws: list[str] | None = None
    contradictions: list[str] | None = None
    hobbies: list[str] | None = None
    spiritual_beliefs: list[str] | None = None
    character_voice: list[str] | None = None
    speech_patterns: list[str] | None = None


class LocationUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class ItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class OrganizationUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class EventUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    characters_involved: list[str] | None = None
    organizations_involved: list[str] | None = None


class NovelCreate(BaseModel):
    title: str
    # Base target word count for the primary thread, chosen by the user.
    # calculate_word_count (see generation.py) adds bonuses on top of this
    # for secondary threads — this is a floor, not the final total.
    word_count: int = Field(default=20000, ge=1000, le=20000)
    # The five intro-prompt sections, ported from V2's single-prompt sections
    # (--- Premise ---, --- Tone ---, --- Characters ---, --- Story
    # Structure ---, --- Sexual/Romance ---). Stored separately so each has
    # its own dialogue box, then concatenated into intro_prompt for the LLM.
    premise: str
    tone_notes: str | None = None
    characters_notes: str | None = None
    primary_thread: str | None = None
    romance_content: str | None = None
    # Up to 3 subplot seeds (enforced client-side), submitted with the rest
    # of the novel and persisted alongside it.
    secondary_threads: list[SecondaryThreadCreate] = []
    primary_genre: str | None = None
    author: str | None = None
    themes: list[str] = []
    # Model alias (see model_routing.yaml) to use for each pipeline step.
    metadata_model: str | None = None
    characters_model: str | None = None
    worldbuilding_model: str | None = None
    primary_thread_model: str | None = None
    secondary_arcs_model: str | None = None
    outline_model: str | None = None
    entities_model: str | None = None
    initial_state_model: str | None = None
    # Whether to enable extended reasoning/thinking for each pipeline step.
    metadata_reasoning: bool = False
    characters_reasoning: bool = False
    worldbuilding_reasoning: bool = False
    primary_thread_reasoning: bool = False
    secondary_arcs_reasoning: bool = False
    outline_reasoning: bool = False
    entities_reasoning: bool = False
    initial_state_reasoning: bool = False


class NovelUpdate(BaseModel):
    title: str | None = None
    summary: str | None = None
    author: str | None = None
    premise: str | None = None
    primary_genre: str | None = None
    sub_genres: list[str] | None = None
    tone: str | None = None
    themes: list[str] | None = None
    spice_level: str | None = None
    literary_voice: str | None = None
    tense: str | None = None
    perspective: str | None = None
    forbidden_element: str | None = None
    story_type: str | None = None
    time_period: str | None = None
    anchor_location: str | None = None
    anchor_location_description: str | None = None
    constraints: list[str] | None = None
    tone_notes: str | None = None
    characters_notes: str | None = None
    primary_thread: str | None = None
    romance_content: str | None = None
    primary_word_count: int | None = None


class NovelCreateResponse(BaseModel):
    id: str

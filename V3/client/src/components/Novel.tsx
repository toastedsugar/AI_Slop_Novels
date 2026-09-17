import { useEffect, useState } from 'react'
import AutoGrowTextarea from './AutoGrowTextarea'
import CopyDialog from './CopyDialog'
import EntityCard from './EntityCard'
import Prompts from './Prompts'

interface NovelDetail {
  id: string
  prompt: string
  title: string
  summary: string | null
  author: string | null
  word_count: number | null
  premise: string
  primary_genre: string | null
  sub_genres: string[]
  tone: string | null
  themes: string[]
  spice_level: string | null
  literary_voice: string | null
  tense: string | null
  perspective: string | null
  forbidden_element: string | null
  story_type: string | null
  time_period: string | null
  anchor_location: string | null
  anchor_location_description: string | null
  constraints: string[]
  tone_notes: string | null
  characters_notes: string | null
  primary_thread: string | null
  romance_content: string | null
  primary_word_count: number | null
  metadata_model: string | null
  characters_model: string | null
  worldbuilding_model: string | null
  primary_thread_model: string | null
  secondary_arcs_model: string | null
  outline_model: string | null
  entities_model: string | null
  initial_state_model: string | null
  metadata_reasoning: boolean
  characters_reasoning: boolean
  worldbuilding_reasoning: boolean
  primary_thread_reasoning: boolean
  secondary_arcs_reasoning: boolean
  outline_reasoning: boolean
  entities_reasoning: boolean
  initial_state_reasoning: boolean
}

interface SecondaryThread {
  id: string
  novel_id: string
  description: string
  length: number
  priority: number
  heat: number
  word_count: number | null
}

interface OutlineBeat {
  id: string
  novel_id: string
  sort_order: number
  content: string
  word_count: number | null
}

interface Character {
  id: string
  novel_id: string
  name: string
  role: string | null
  age: number | null
  gender: string | null
  sexuality: string | null
  occupation: string | null
  appearance: string | null
  physical_characteristics: string[]
  personality: string[]
  backstory: string | null
  fears: string[]
  flaws: string[]
  contradictions: string[]
  hobbies: string[]
  spiritual_beliefs: string[]
  character_voice: string[]
  speech_patterns: string[]
}

interface Location {
  id: string
  novel_id: string
  name: string
  description: string | null
}

interface Item {
  id: string
  novel_id: string
  name: string
  description: string | null
}

interface Organization {
  id: string
  novel_id: string
  name: string
  description: string | null
}

interface StoryEvent {
  id: string
  novel_id: string
  title: string
  description: string | null
  characters_involved: string[]
  organizations_involved: string[]
}

interface NovelProps {
  name: string
  onNovelCreated: () => void
  onSelectNovel: (id: string | null) => void
}

const TABS = ['Prompts', 'Metadata', 'Characters', 'Outline', 'Locations', 'Items', 'Organizations', 'Events'] as const
type Tab = (typeof TABS)[number]

function Novel({ name: id, onNovelCreated, onSelectNovel }: NovelProps) {
  const [novel, setNovel] = useState<NovelDetail | null>(null)
  const [saved, setSavedNovel] = useState<NovelDetail | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)
  const [saveError, setSaveError] = useState<string | null>(null)
  const [justSaved, setJustSaved] = useState(false)
  const [activeTab, setActiveTab] = useState<Tab>('Prompts')

  const [secondaryThreads, setSecondaryThreads] = useState<SecondaryThread[] | null>(null)

  const [characters, setCharacters] = useState<Character[] | null>(null)
  const [charactersError, setCharactersError] = useState<string | null>(null)

  const [outline, setOutline] = useState<OutlineBeat[] | null>(null)
  const [outlineError, setOutlineError] = useState<string | null>(null)

  const [locations, setLocations] = useState<Location[] | null>(null)
  const [items, setItems] = useState<Item[] | null>(null)
  const [organizations, setOrganizations] = useState<Organization[] | null>(null)
  const [events, setEvents] = useState<StoryEvent[] | null>(null)
  const [worldError, setWorldError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    async function loadNovel() {
      setNovel(null)
      setSavedNovel(null)
      setError(null)
      try {
        const res = await fetch(`/api/v1/novel/${id}`)
        if (!res.ok) throw new Error(`GET /api/v1/novel/${id} failed: ${res.status}`)
        const data = await res.json()
        if (!cancelled) {
          setNovel(data)
          setSavedNovel(data)
        }
      } catch (err) {
        console.error(err)
        if (!cancelled) setError('Failed to load novel.')
      }
    }

    async function loadSecondaryThreads() {
      setSecondaryThreads(null)
      try {
        const res = await fetch(`/api/v1/novel/${id}/secondary-threads`)
        if (!res.ok) throw new Error(`GET /api/v1/novel/${id}/secondary-threads failed: ${res.status}`)
        const data = await res.json()
        if (!cancelled) setSecondaryThreads(data)
      } catch (err) {
        console.error(err)
      }
    }

    async function loadCharacters() {
      setCharacters(null)
      setCharactersError(null)
      try {
        const res = await fetch(`/api/v1/novel/${id}/characters`)
        if (!res.ok) throw new Error(`GET /api/v1/novel/${id}/characters failed: ${res.status}`)
        const data = await res.json()
        if (!cancelled) setCharacters(data)
      } catch (err) {
        console.error(err)
        if (!cancelled) setCharactersError('Failed to load characters.')
      }
    }

    async function loadOutline() {
      setOutline(null)
      setOutlineError(null)
      try {
        const res = await fetch(`/api/v1/novel/${id}/outline`)
        if (!res.ok) throw new Error(`GET /api/v1/novel/${id}/outline failed: ${res.status}`)
        const data = await res.json()
        if (!cancelled) setOutline(data)
      } catch (err) {
        console.error(err)
        if (!cancelled) setOutlineError('Failed to load outline.')
      }
    }

    async function loadWorld() {
      setLocations(null)
      setItems(null)
      setOrganizations(null)
      setEvents(null)
      setWorldError(null)
      try {
        const [locationsRes, itemsRes, organizationsRes, eventsRes] = await Promise.all([
          fetch(`/api/v1/novel/${id}/locations`),
          fetch(`/api/v1/novel/${id}/items`),
          fetch(`/api/v1/novel/${id}/organizations`),
          fetch(`/api/v1/novel/${id}/events`),
        ])
        if (!locationsRes.ok || !itemsRes.ok || !organizationsRes.ok || !eventsRes.ok) {
          throw new Error(`GET /api/v1/novel/${id}/{locations,items,organizations,events} failed`)
        }
        const [locationsData, itemsData, organizationsData, eventsData] = await Promise.all([
          locationsRes.json(),
          itemsRes.json(),
          organizationsRes.json(),
          eventsRes.json(),
        ])
        if (!cancelled) {
          setLocations(locationsData)
          setItems(itemsData)
          setOrganizations(organizationsData)
          setEvents(eventsData)
        }
      } catch (err) {
        console.error(err)
        if (!cancelled) setWorldError('Failed to load worldbuilding.')
      }
    }

    loadNovel()
    loadSecondaryThreads()
    loadCharacters()
    loadOutline()
    loadWorld()
    return () => {
      cancelled = true
    }
  }, [id])

  function updateField<K extends keyof NovelDetail>(field: K, value: NovelDetail[K]) {
    setNovel((prev) => (prev ? { ...prev, [field]: value } : prev))
    setJustSaved(false)
  }

  const isDirty = novel != null && saved != null && JSON.stringify(novel) !== JSON.stringify(saved)

  async function handleSubmit() {
    if (!novel || !isDirty) return

    setSaving(true)
    setSaveError(null)
    setJustSaved(false)
    try {
      const res = await fetch(`/api/v1/novel/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: novel.title,
          summary: novel.summary,
          author: novel.author,
          premise: novel.premise,
          primary_genre: novel.primary_genre,
          sub_genres: novel.sub_genres,
          tone: novel.tone,
          themes: novel.themes,
          spice_level: novel.spice_level,
          literary_voice: novel.literary_voice,
          tense: novel.tense,
          perspective: novel.perspective,
          forbidden_element: novel.forbidden_element,
          story_type: novel.story_type,
          time_period: novel.time_period,
          anchor_location: novel.anchor_location,
          anchor_location_description: novel.anchor_location_description,
          constraints: novel.constraints,
        }),
      })
      if (!res.ok) throw new Error(`PATCH /api/v1/novel/${id} failed: ${res.status}`)
      const data = await res.json()
      setNovel(data)
      setSavedNovel(data)
      setJustSaved(true)
    } catch (err) {
      console.error(err)
      setSaveError('Failed to save changes. Please try again.')
    } finally {
      setSaving(false)
    }
  }

  if (error) return <p className="novels-error">{error}</p>
  if (!novel) return <p>Loading novel...</p>

  return (
    <div className="novel-detail">
      {saving && <CopyDialog title="Updating Novel" message="Saving your changes..." />}

      <menu role="tablist" className="multirows novel-detail-tabs">
        {TABS.map((tab) => (
          <li key={tab} role="tab" aria-selected={activeTab === tab}>
            <a
              href={`#${tab}`}
              onClick={(e) => {
                e.preventDefault()
                setActiveTab(tab)
              }}
            >
              {tab}
            </a>
          </li>
        ))}
      </menu>

      <div className="window" role="tabpanel">
        <div className="window-body novel-detail-tabpanel-body">
          {activeTab === 'Metadata' && (
            <>
              <div className="novel-field">
                <label htmlFor="field-title">Title</label>
                <input
                  id="field-title"
                  type="text"
                  value={novel.title}
                  onChange={(e) => updateField('title', e.target.value)}
                />
              </div>

              <div className="novel-field">
                <label htmlFor="field-summary">Summary</label>
                <AutoGrowTextarea
                  id="field-summary"
                  value={novel.summary ?? ''}
                  onChange={(e) => updateField('summary', e.target.value)}
                />
              </div>

              <div className="novel-field">
                <label htmlFor="field-author">Author</label>
                <input
                  id="field-author"
                  type="text"
                  value={novel.author ?? ''}
                  onChange={(e) => updateField('author', e.target.value)}
                />
              </div>

              <div className="novel-field">
                <label htmlFor="field-genre">Genre</label>
                <input
                  id="field-genre"
                  type="text"
                  value={novel.primary_genre ?? ''}
                  onChange={(e) => updateField('primary_genre', e.target.value)}
                />
              </div>

              <div className="novel-field">
                <label htmlFor="field-sub-genres">Sub-genres</label>
                <input
                  id="field-sub-genres"
                  type="text"
                  value={novel.sub_genres.join(', ')}
                  onChange={(e) =>
                    updateField(
                      'sub_genres',
                      e.target.value
                        .split(',')
                        .map((s) => s.trim())
                        .filter(Boolean),
                    )
                  }
                />
              </div>

              <div className="novel-field">
                <label htmlFor="field-tone">Tone</label>
                <input
                  id="field-tone"
                  type="text"
                  value={novel.tone ?? ''}
                  onChange={(e) => updateField('tone', e.target.value)}
                />
              </div>

              <div className="novel-field">
                <label htmlFor="field-themes">Themes</label>
                <input
                  id="field-themes"
                  type="text"
                  value={novel.themes.join(', ')}
                  onChange={(e) =>
                    updateField(
                      'themes',
                      e.target.value
                        .split(',')
                        .map((s) => s.trim())
                        .filter(Boolean),
                    )
                  }
                />
              </div>

              <div className="novel-field">
                <label htmlFor="field-spice">Spice Level</label>
                <select
                  id="field-spice"
                  value={novel.spice_level ?? ''}
                  onChange={(e) => updateField('spice_level', e.target.value)}
                >
                  <option value="">—</option>
                  <option value="low">low</option>
                  <option value="medium">medium</option>
                  <option value="high">high</option>
                  <option value="explicit">explicit</option>
                </select>
              </div>

              <div className="novel-field">
                <label htmlFor="field-voice">Literary Voice</label>
                <input
                  id="field-voice"
                  type="text"
                  value={novel.literary_voice ?? ''}
                  onChange={(e) => updateField('literary_voice', e.target.value)}
                />
              </div>

              <div className="novel-field">
                <label htmlFor="field-tense">Tense</label>
                <select
                  id="field-tense"
                  value={novel.tense ?? ''}
                  onChange={(e) => updateField('tense', e.target.value)}
                >
                  <option value="">—</option>
                  <option value="past">past</option>
                  <option value="present">present</option>
                </select>
              </div>

              <div className="novel-field">
                <label htmlFor="field-perspective">Perspective</label>
                <select
                  id="field-perspective"
                  value={novel.perspective ?? ''}
                  onChange={(e) => updateField('perspective', e.target.value)}
                >
                  <option value="">—</option>
                  <option value="first_person">first_person</option>
                  <option value="third_person_limited">third_person_limited</option>
                  <option value="third_person_omniscient">third_person_omniscient</option>
                </select>
              </div>

              <div className="novel-field">
                <label htmlFor="field-forbidden">Forbidden Element</label>
                <AutoGrowTextarea
                  id="field-forbidden"
                  value={novel.forbidden_element ?? ''}
                  onChange={(e) => updateField('forbidden_element', e.target.value)}
                />
              </div>

              <div className="novel-field">
                <label htmlFor="field-story-type">Story Type</label>
                <input
                  id="field-story-type"
                  type="text"
                  value={novel.story_type ?? ''}
                  onChange={(e) => updateField('story_type', e.target.value)}
                />
              </div>

              <div className="novel-field">
                <label htmlFor="field-time-period">Time Period</label>
                <input
                  id="field-time-period"
                  type="text"
                  value={novel.time_period ?? ''}
                  onChange={(e) => updateField('time_period', e.target.value)}
                />
              </div>

              <div className="novel-field">
                <label htmlFor="field-anchor-location">Anchor Location</label>
                <input
                  id="field-anchor-location"
                  type="text"
                  value={novel.anchor_location ?? ''}
                  onChange={(e) => updateField('anchor_location', e.target.value)}
                />
              </div>

              <div className="novel-field">
                <label htmlFor="field-anchor-location-description">Anchor Location Description</label>
                <AutoGrowTextarea
                  id="field-anchor-location-description"
                  value={novel.anchor_location_description ?? ''}
                  onChange={(e) => updateField('anchor_location_description', e.target.value)}
                />
              </div>

              <div className="novel-field">
                <label htmlFor="field-constraints">Constraints</label>
                <AutoGrowTextarea
                  id="field-constraints"
                  value={novel.constraints.join(', ')}
                  onChange={(e) =>
                    updateField(
                      'constraints',
                      e.target.value
                        .split(',')
                        .map((s) => s.trim())
                        .filter(Boolean),
                    )
                  }
                />
              </div>

              <div className="novel-field">
                <label htmlFor="field-primary-word-count">Primary Word Count</label>
                <input
                  id="field-primary-word-count"
                  type="text"
                  readOnly
                  value={
                    novel.primary_word_count != null
                      ? `${novel.primary_word_count} words (target word count plus secondary thread bonuses)`
                      : 'Not yet generated'
                  }
                />
              </div>

              <div className="novel-character-card-actions">
                {saveError && <span className="novels-error">{saveError}</span>}
                {justSaved && !saveError && <span className="novel-detail-saved">Saved.</span>}
                <button type="button" disabled={saving || !isDirty} onClick={handleSubmit}>
                  {saving ? 'Saving...' : 'Update'}
                </button>
              </div>
            </>
          )}

          {activeTab === 'Prompts' && (
            <Prompts
              novelId={id}
              title={novel.title}
              wordCount={novel.word_count ?? 20000}
              premise={novel.premise}
              toneNotes={novel.tone_notes ?? ''}
              charactersNotes={novel.characters_notes ?? ''}
              primaryThread={novel.primary_thread ?? ''}
              romanceContent={novel.romance_content ?? ''}
              secondaryThreads={(secondaryThreads ?? []).map((t) => ({
                description: t.description,
                length: t.length,
                priority: t.priority,
                heat: t.heat,
              }))}
              primaryGenre={novel.primary_genre ?? ''}
              author={novel.author ?? ''}
              themes={novel.themes.join(', ')}
              metadataModel={novel.metadata_model ?? ''}
              charactersModel={novel.characters_model ?? ''}
              worldbuildingModel={novel.worldbuilding_model ?? ''}
              primaryThreadModel={novel.primary_thread_model ?? ''}
              secondaryArcsModel={novel.secondary_arcs_model ?? ''}
              outlineModel={novel.outline_model ?? ''}
              entitiesModel={novel.entities_model ?? ''}
              initialStateModel={novel.initial_state_model ?? ''}
              metadataReasoning={novel.metadata_reasoning}
              charactersReasoning={novel.characters_reasoning}
              worldbuildingReasoning={novel.worldbuilding_reasoning}
              primaryThreadReasoning={novel.primary_thread_reasoning}
              secondaryArcsReasoning={novel.secondary_arcs_reasoning}
              outlineReasoning={novel.outline_reasoning}
              entitiesReasoning={novel.entities_reasoning}
              initialStateReasoning={novel.initial_state_reasoning}
              onRegenerated={(newId) => {
                onNovelCreated()
                onSelectNovel(newId)
              }}
            />
          )}

          {activeTab === 'Characters' && (
            <>
              {charactersError && <p className="novels-error">{charactersError}</p>}
              {!charactersError && characters === null && <p>Loading characters...</p>}
              {!charactersError && characters !== null && characters.length === 0 && (
                <p>No characters generated yet.</p>
              )}
              {!charactersError && characters !== null && characters.length > 0 && (
                <div className="novel-characters-list">
                  {characters.map((character) => (
                    <EntityCard
                      key={character.id}
                      entity={character}
                      patchUrl={`/api/v1/novel/${id}/characters/${character.id}`}
                      onSaved={(updated) =>
                        setCharacters((prev) =>
                          prev ? prev.map((c) => (c.id === updated.id ? updated : c)) : prev,
                        )
                      }
                      renderFields={(draft, updateField) => {
                        const updateListField = (
                          field: 'physical_characteristics' | 'personality' | 'fears' | 'flaws' |
                            'contradictions' | 'hobbies' | 'spiritual_beliefs' | 'character_voice' |
                            'speech_patterns',
                          value: string,
                        ) =>
                          updateField(
                            field,
                            value
                              .split(',')
                              .map((s) => s.trim())
                              .filter(Boolean),
                          )
                        return (
                          <>
                            <div className="novel-field">
                              <label htmlFor={`char-name-${draft.id}`}>Name</label>
                              <input
                                id={`char-name-${draft.id}`}
                                type="text"
                                value={draft.name}
                                onChange={(e) => updateField('name', e.target.value)}
                              />
                            </div>
                            <div className="novel-field">
                              <label htmlFor={`char-role-${draft.id}`}>Role</label>
                              <input
                                id={`char-role-${draft.id}`}
                                type="text"
                                value={draft.role ?? ''}
                                onChange={(e) => updateField('role', e.target.value)}
                              />
                            </div>
                            <div className="novel-field">
                              <label htmlFor={`char-age-${draft.id}`}>Age</label>
                              <input
                                id={`char-age-${draft.id}`}
                                type="number"
                                value={draft.age ?? ''}
                                onChange={(e) =>
                                  updateField('age', e.target.value === '' ? null : Number(e.target.value))
                                }
                              />
                            </div>
                            <div className="novel-field">
                              <label htmlFor={`char-gender-${draft.id}`}>Gender</label>
                              <input
                                id={`char-gender-${draft.id}`}
                                type="text"
                                value={draft.gender ?? ''}
                                onChange={(e) => updateField('gender', e.target.value)}
                              />
                            </div>
                            <div className="novel-field">
                              <label htmlFor={`char-sexuality-${draft.id}`}>Sexuality</label>
                              <input
                                id={`char-sexuality-${draft.id}`}
                                type="text"
                                value={draft.sexuality ?? ''}
                                onChange={(e) => updateField('sexuality', e.target.value)}
                              />
                            </div>
                            <div className="novel-field">
                              <label htmlFor={`char-occupation-${draft.id}`}>Occupation</label>
                              <input
                                id={`char-occupation-${draft.id}`}
                                type="text"
                                value={draft.occupation ?? ''}
                                onChange={(e) => updateField('occupation', e.target.value)}
                              />
                            </div>
                            <div className="novel-field">
                              <label htmlFor={`char-appearance-${draft.id}`}>Appearance</label>
                              <AutoGrowTextarea
                                id={`char-appearance-${draft.id}`}
                                value={draft.appearance ?? ''}
                                onChange={(e) => updateField('appearance', e.target.value)}
                              />
                            </div>
                            <div className="novel-field">
                              <label htmlFor={`char-physical-${draft.id}`}>
                                Physical Characteristics (comma-separated)
                              </label>
                              <AutoGrowTextarea
                                id={`char-physical-${draft.id}`}
                                value={draft.physical_characteristics.join(', ')}
                                onChange={(e) => updateListField('physical_characteristics', e.target.value)}
                              />
                            </div>
                            <div className="novel-field">
                              <label htmlFor={`char-personality-${draft.id}`}>
                                Personality (comma-separated)
                              </label>
                              <AutoGrowTextarea
                                id={`char-personality-${draft.id}`}
                                value={draft.personality.join(', ')}
                                onChange={(e) => updateListField('personality', e.target.value)}
                              />
                            </div>
                            <div className="novel-field">
                              <label htmlFor={`char-backstory-${draft.id}`}>Backstory</label>
                              <AutoGrowTextarea
                                id={`char-backstory-${draft.id}`}
                                value={draft.backstory ?? ''}
                                onChange={(e) => updateField('backstory', e.target.value)}
                              />
                            </div>
                            <div className="novel-field">
                              <label htmlFor={`char-fears-${draft.id}`}>Fears (comma-separated)</label>
                              <AutoGrowTextarea
                                id={`char-fears-${draft.id}`}
                                value={draft.fears.join(', ')}
                                onChange={(e) => updateListField('fears', e.target.value)}
                              />
                            </div>
                            <div className="novel-field">
                              <label htmlFor={`char-flaws-${draft.id}`}>Flaws (comma-separated)</label>
                              <AutoGrowTextarea
                                id={`char-flaws-${draft.id}`}
                                value={draft.flaws.join(', ')}
                                onChange={(e) => updateListField('flaws', e.target.value)}
                              />
                            </div>
                            <div className="novel-field">
                              <label htmlFor={`char-contradictions-${draft.id}`}>
                                Contradictions (comma-separated)
                              </label>
                              <AutoGrowTextarea
                                id={`char-contradictions-${draft.id}`}
                                value={draft.contradictions.join(', ')}
                                onChange={(e) => updateListField('contradictions', e.target.value)}
                              />
                            </div>
                            <div className="novel-field">
                              <label htmlFor={`char-hobbies-${draft.id}`}>Hobbies (comma-separated)</label>
                              <AutoGrowTextarea
                                id={`char-hobbies-${draft.id}`}
                                value={draft.hobbies.join(', ')}
                                onChange={(e) => updateListField('hobbies', e.target.value)}
                              />
                            </div>
                            <div className="novel-field">
                              <label htmlFor={`char-beliefs-${draft.id}`}>
                                Spiritual Beliefs (comma-separated)
                              </label>
                              <AutoGrowTextarea
                                id={`char-beliefs-${draft.id}`}
                                value={draft.spiritual_beliefs.join(', ')}
                                onChange={(e) => updateListField('spiritual_beliefs', e.target.value)}
                              />
                            </div>
                            <div className="novel-field">
                              <label htmlFor={`char-voice-${draft.id}`}>
                                Character Voice (comma-separated)
                              </label>
                              <AutoGrowTextarea
                                id={`char-voice-${draft.id}`}
                                value={draft.character_voice.join(', ')}
                                onChange={(e) => updateListField('character_voice', e.target.value)}
                              />
                            </div>
                            <div className="novel-field">
                              <label htmlFor={`char-speech-${draft.id}`}>
                                Speech Patterns (comma-separated)
                              </label>
                              <AutoGrowTextarea
                                id={`char-speech-${draft.id}`}
                                value={draft.speech_patterns.join(', ')}
                                onChange={(e) => updateListField('speech_patterns', e.target.value)}
                              />
                            </div>
                          </>
                        )
                      }}
                    />
                  ))}
                </div>
              )}
            </>
          )}

          {activeTab === 'Outline' && (
            <>
              {outlineError && <p className="novels-error">{outlineError}</p>}
              {!outlineError && outline === null && <p>Loading outline...</p>}
              {!outlineError && outline !== null && outline.length === 0 && (
                <p>No outline generated yet.</p>
              )}
              {!outlineError && outline !== null && outline.length > 0 && (
                <div className="novel-characters-list">
                  {outline.map((beat, index) => (
                    <EntityCard
                      key={beat.id}
                      entity={beat}
                      patchUrl={`/api/v1/novel/${id}/outline-beats/${beat.id}`}
                      onSaved={(updated) =>
                        setOutline((prev) =>
                          prev ? prev.map((b) => (b.id === updated.id ? updated : b)) : prev,
                        )
                      }
                      renderFields={(draft, updateField) => (
                        <>
                          <div className="novel-field">
                            <label>Beat {index + 1}</label>
                          </div>

                          <div className="novel-field">
                            <label htmlFor={`beat-content-${draft.id}`}>Content</label>
                            <AutoGrowTextarea
                              id={`beat-content-${draft.id}`}
                              value={draft.content}
                              onChange={(e) => updateField('content', e.target.value)}
                            />
                          </div>

                          <div className="novel-field">
                            <label htmlFor={`beat-word-count-${draft.id}`}>Estimated Word Count</label>
                            <input
                              id={`beat-word-count-${draft.id}`}
                              type="number"
                              value={draft.word_count ?? ''}
                              onChange={(e) =>
                                updateField(
                                  'word_count',
                                  e.target.value === '' ? null : Number(e.target.value),
                                )
                              }
                            />
                          </div>
                        </>
                      )}
                    />
                  ))}
                </div>
              )}
            </>
          )}

          {activeTab === 'Locations' && (
            <>
              {worldError && <p className="novels-error">{worldError}</p>}
              {!worldError && locations === null && <p>Loading locations...</p>}
              {!worldError && locations !== null && locations.length === 0 && (
                <p>No locations generated yet.</p>
              )}
              {!worldError && locations !== null && locations.length > 0 && (
                <div className="novel-characters-list">
                  {locations.map((location) => (
                    <EntityCard
                      key={location.id}
                      entity={location}
                      patchUrl={`/api/v1/novel/${id}/locations/${location.id}`}
                      onSaved={(updated) =>
                        setLocations((prev) =>
                          prev ? prev.map((l) => (l.id === updated.id ? updated : l)) : prev,
                        )
                      }
                      renderFields={(draft, updateField) => (
                        <>
                          <div className="novel-field">
                            <label htmlFor={`location-name-${draft.id}`}>Name</label>
                            <input
                              id={`location-name-${draft.id}`}
                              type="text"
                              value={draft.name}
                              onChange={(e) => updateField('name', e.target.value)}
                            />
                          </div>
                          <div className="novel-field">
                            <label htmlFor={`location-description-${draft.id}`}>Description</label>
                            <AutoGrowTextarea
                              id={`location-description-${draft.id}`}
                              value={draft.description ?? ''}
                              onChange={(e) => updateField('description', e.target.value)}
                            />
                          </div>
                        </>
                      )}
                    />
                  ))}
                </div>
              )}
            </>
          )}

          {activeTab === 'Items' && (
            <>
              {worldError && <p className="novels-error">{worldError}</p>}
              {!worldError && items === null && <p>Loading items...</p>}
              {!worldError && items !== null && items.length === 0 && <p>No items generated yet.</p>}
              {!worldError && items !== null && items.length > 0 && (
                <div className="novel-characters-list">
                  {items.map((item) => (
                    <EntityCard
                      key={item.id}
                      entity={item}
                      patchUrl={`/api/v1/novel/${id}/items/${item.id}`}
                      onSaved={(updated) =>
                        setItems((prev) =>
                          prev ? prev.map((i) => (i.id === updated.id ? updated : i)) : prev,
                        )
                      }
                      renderFields={(draft, updateField) => (
                        <>
                          <div className="novel-field">
                            <label htmlFor={`item-name-${draft.id}`}>Name</label>
                            <input
                              id={`item-name-${draft.id}`}
                              type="text"
                              value={draft.name}
                              onChange={(e) => updateField('name', e.target.value)}
                            />
                          </div>
                          <div className="novel-field">
                            <label htmlFor={`item-description-${draft.id}`}>Description</label>
                            <AutoGrowTextarea
                              id={`item-description-${draft.id}`}
                              value={draft.description ?? ''}
                              onChange={(e) => updateField('description', e.target.value)}
                            />
                          </div>
                        </>
                      )}
                    />
                  ))}
                </div>
              )}
            </>
          )}

          {activeTab === 'Organizations' && (
            <>
              {worldError && <p className="novels-error">{worldError}</p>}
              {!worldError && organizations === null && <p>Loading organizations...</p>}
              {!worldError && organizations !== null && organizations.length === 0 && (
                <p>No organizations generated yet.</p>
              )}
              {!worldError && organizations !== null && organizations.length > 0 && (
                <div className="novel-characters-list">
                  {organizations.map((organization) => (
                    <EntityCard
                      key={organization.id}
                      entity={organization}
                      patchUrl={`/api/v1/novel/${id}/organizations/${organization.id}`}
                      onSaved={(updated) =>
                        setOrganizations((prev) =>
                          prev ? prev.map((o) => (o.id === updated.id ? updated : o)) : prev,
                        )
                      }
                      renderFields={(draft, updateField) => (
                        <>
                          <div className="novel-field">
                            <label htmlFor={`org-name-${draft.id}`}>Name</label>
                            <input
                              id={`org-name-${draft.id}`}
                              type="text"
                              value={draft.name}
                              onChange={(e) => updateField('name', e.target.value)}
                            />
                          </div>
                          <div className="novel-field">
                            <label htmlFor={`org-description-${draft.id}`}>Description</label>
                            <AutoGrowTextarea
                              id={`org-description-${draft.id}`}
                              value={draft.description ?? ''}
                              onChange={(e) => updateField('description', e.target.value)}
                            />
                          </div>
                        </>
                      )}
                    />
                  ))}
                </div>
              )}
            </>
          )}

          {activeTab === 'Events' && (
            <>
              {worldError && <p className="novels-error">{worldError}</p>}
              {!worldError && events === null && <p>Loading events...</p>}
              {!worldError && events !== null && events.length === 0 && <p>No events generated yet.</p>}
              {!worldError && events !== null && events.length > 0 && (
                <div className="novel-characters-list">
                  {events.map((event) => (
                    <EntityCard
                      key={event.id}
                      entity={event}
                      patchUrl={`/api/v1/novel/${id}/events/${event.id}`}
                      onSaved={(updated) =>
                        setEvents((prev) =>
                          prev ? prev.map((e) => (e.id === updated.id ? updated : e)) : prev,
                        )
                      }
                      renderFields={(draft, updateField) => (
                        <>
                          <div className="novel-field">
                            <label htmlFor={`event-title-${draft.id}`}>Title</label>
                            <input
                              id={`event-title-${draft.id}`}
                              type="text"
                              value={draft.title}
                              onChange={(e) => updateField('title', e.target.value)}
                            />
                          </div>
                          <div className="novel-field">
                            <label htmlFor={`event-description-${draft.id}`}>Description</label>
                            <AutoGrowTextarea
                              id={`event-description-${draft.id}`}
                              value={draft.description ?? ''}
                              onChange={(e) => updateField('description', e.target.value)}
                            />
                          </div>
                          <div className="novel-field">
                            <label htmlFor={`event-characters-${draft.id}`}>Characters Involved</label>
                            <input
                              id={`event-characters-${draft.id}`}
                              type="text"
                              value={draft.characters_involved.join(', ')}
                              onChange={(e) =>
                                updateField(
                                  'characters_involved',
                                  e.target.value
                                    .split(',')
                                    .map((s) => s.trim())
                                    .filter(Boolean),
                                )
                              }
                            />
                          </div>
                          <div className="novel-field">
                            <label htmlFor={`event-organizations-${draft.id}`}>
                              Organizations Involved
                            </label>
                            <input
                              id={`event-organizations-${draft.id}`}
                              type="text"
                              value={draft.organizations_involved.join(', ')}
                              onChange={(e) =>
                                updateField(
                                  'organizations_involved',
                                  e.target.value
                                    .split(',')
                                    .map((s) => s.trim())
                                    .filter(Boolean),
                                )
                              }
                            />
                          </div>
                        </>
                      )}
                    />
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default Novel

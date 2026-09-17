import { useEffect, useState } from 'react'
import AutoGrowTextarea from './AutoGrowTextarea'
import ConfirmDialog from './ConfirmDialog'

export interface DraftSecondaryThread {
  description: string
  length: number
  priority: number
  heat: number
}

export interface PromptFormValues {
  title: string
  wordCount: number
  premise: string
  toneNotes: string
  charactersNotes: string
  primaryThread: string
  romanceContent: string
  secondaryThreads: DraftSecondaryThread[]
  primaryGenre: string
  author: string
  themes: string
  metadataModel: string
  charactersModel: string
  worldbuildingModel: string
  primaryThreadModel: string
  secondaryArcsModel: string
  outlineModel: string
  entitiesModel: string
  initialStateModel: string
  metadataReasoning: boolean
  charactersReasoning: boolean
  worldbuildingReasoning: boolean
  primaryThreadReasoning: boolean
  secondaryArcsReasoning: boolean
  outlineReasoning: boolean
  entitiesReasoning: boolean
  initialStateReasoning: boolean
}

export const MIN_WORD_COUNT = 12000
export const MAX_WORD_COUNT = 20000

export const EMPTY_PROMPT_FORM_VALUES: PromptFormValues = {
  title: '',
  wordCount: MAX_WORD_COUNT,
  premise: '',
  toneNotes: '',
  charactersNotes: '',
  primaryThread: '',
  romanceContent: '',
  secondaryThreads: [],
  primaryGenre: '',
  author: '',
  themes: '',
  metadataModel: '',
  charactersModel: '',
  worldbuildingModel: '',
  primaryThreadModel: '',
  secondaryArcsModel: '',
  outlineModel: '',
  entitiesModel: '',
  initialStateModel: '',
  metadataReasoning: false,
  charactersReasoning: false,
  worldbuildingReasoning: false,
  primaryThreadReasoning: false,
  secondaryArcsReasoning: false,
  outlineReasoning: false,
  entitiesReasoning: false,
  initialStateReasoning: false,
}

// Maps form state to the POST /api/v1/novel request body. Shared so the
// create flow and the regenerate flow send an identical payload shape.
export function toNovelCreatePayload(values: PromptFormValues) {
  return {
    title: values.title,
    word_count: values.wordCount,
    premise: values.premise,
    tone_notes: values.toneNotes || null,
    characters_notes: values.charactersNotes || null,
    primary_thread: values.primaryThread || null,
    romance_content: values.romanceContent || null,
    secondary_threads: values.secondaryThreads,
    primary_genre: values.primaryGenre || null,
    author: values.author || null,
    themes: values.themes
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean),
    metadata_model: values.metadataModel || null,
    characters_model: values.charactersModel || null,
    worldbuilding_model: values.worldbuildingModel || null,
    primary_thread_model: values.primaryThreadModel || null,
    secondary_arcs_model: values.secondaryArcsModel || null,
    outline_model: values.outlineModel || null,
    entities_model: values.entitiesModel || null,
    initial_state_model: values.initialStateModel || null,
    metadata_reasoning: values.metadataReasoning,
    characters_reasoning: values.charactersReasoning,
    worldbuilding_reasoning: values.worldbuildingReasoning,
    primary_thread_reasoning: values.primaryThreadReasoning,
    secondary_arcs_reasoning: values.secondaryArcsReasoning,
    outline_reasoning: values.outlineReasoning,
    entities_reasoning: values.entitiesReasoning,
    initial_state_reasoning: values.initialStateReasoning,
  }
}

interface PromptFormProps {
  legend: string
  submitLabel: string
  submitPendingLabel: string
  initialValues: PromptFormValues
  submitting: boolean
  error: string | null
  onSubmit: (values: PromptFormValues) => void
  // When set, the submit button stays disabled until the form differs from
  // initialValues (used by Regenerate, which should be a no-op otherwise).
  requireDirty?: boolean
  // When set, clicking submit shows a Windows-98-style confirmation dialog
  // with this message before calling onSubmit (used by Regenerate, since it
  // deletes everything generated for the novel).
  confirmMessage?: string
  confirmTitle?: string
}

const MAX_SECONDARY_THREADS = 3

// The novel intro-prompt form: every field the pipeline reads before the
// first token is generated. Shared by the "New Novel" create flow and the
// per-novel "Prompts" tab (whose Regenerate button wipes and reruns the
// pipeline with these same fields) so the two stay identical by construction.
function PromptForm({
  legend,
  submitLabel,
  submitPendingLabel,
  initialValues,
  submitting,
  error,
  onSubmit,
  requireDirty = false,
  confirmMessage,
  confirmTitle = 'Confirm',
}: PromptFormProps) {
  const [confirming, setConfirming] = useState(false)
  const [title, setTitle] = useState(initialValues.title)
  const [wordCountText, setWordCountText] = useState(String(initialValues.wordCount))
  const wordCount = Number(wordCountText)
  const wordCountValid =
    wordCountText.trim() !== '' &&
    Number.isFinite(wordCount) &&
    wordCount >= MIN_WORD_COUNT &&
    wordCount <= MAX_WORD_COUNT
  const [premise, setPremise] = useState(initialValues.premise)
  const [toneNotes, setToneNotes] = useState(initialValues.toneNotes)
  const [charactersNotes, setCharactersNotes] = useState(initialValues.charactersNotes)
  const [primaryThread, setPrimaryThread] = useState(initialValues.primaryThread)
  const [romanceContent, setRomanceContent] = useState(initialValues.romanceContent)
  const [secondaryThreads, setSecondaryThreads] = useState<DraftSecondaryThread[]>(
    initialValues.secondaryThreads,
  )
  const [primaryGenre, setPrimaryGenre] = useState(initialValues.primaryGenre)
  const [author, setAuthor] = useState(initialValues.author)
  const [themes, setThemes] = useState(initialValues.themes)

  const [availableModels, setAvailableModels] = useState<string[]>([])
  const [metadataModel, setMetadataModel] = useState(initialValues.metadataModel)
  const [charactersModel, setCharactersModel] = useState(initialValues.charactersModel)
  const [worldbuildingModel, setWorldbuildingModel] = useState(initialValues.worldbuildingModel)
  const [primaryThreadModel, setPrimaryThreadModel] = useState(initialValues.primaryThreadModel)
  const [secondaryArcsModel, setSecondaryArcsModel] = useState(initialValues.secondaryArcsModel)
  const [outlineModel, setOutlineModel] = useState(initialValues.outlineModel)
  const [entitiesModel, setEntitiesModel] = useState(initialValues.entitiesModel)
  const [initialStateModel, setInitialStateModel] = useState(initialValues.initialStateModel)
  const [metadataReasoning, setMetadataReasoning] = useState(initialValues.metadataReasoning)
  const [charactersReasoning, setCharactersReasoning] = useState(initialValues.charactersReasoning)
  const [worldbuildingReasoning, setWorldbuildingReasoning] = useState(
    initialValues.worldbuildingReasoning,
  )
  const [primaryThreadReasoning, setPrimaryThreadReasoning] = useState(
    initialValues.primaryThreadReasoning,
  )
  const [secondaryArcsReasoning, setSecondaryArcsReasoning] = useState(
    initialValues.secondaryArcsReasoning,
  )
  const [outlineReasoning, setOutlineReasoning] = useState(initialValues.outlineReasoning)
  const [entitiesReasoning, setEntitiesReasoning] = useState(initialValues.entitiesReasoning)
  const [initialStateReasoning, setInitialStateReasoning] = useState(
    initialValues.initialStateReasoning,
  )

  // Mirrors initialValues, except the model fields are backfilled with
  // step defaults the same way the form fields are below (loadModels). Used
  // as the dirty-check baseline instead of the raw prop, so a novel with no
  // recorded model choice (pre-existing novels, before models were persisted)
  // doesn't read as "dirty" the instant defaults load in.
  const [baseline, setBaseline] = useState(initialValues)

  useEffect(() => {
    async function loadModels() {
      try {
        const res = await fetch('/api/v1/models')
        if (!res.ok) throw new Error(`GET /api/v1/models failed: ${res.status}`)
        const data = await res.json()
        setAvailableModels(data.models)
        setMetadataModel((m) => m || data.defaults.metadata)
        setCharactersModel((m) => m || data.defaults.characters)
        setWorldbuildingModel((m) => m || data.defaults.worldbuilding)
        setPrimaryThreadModel((m) => m || data.defaults.primary_thread)
        setSecondaryArcsModel((m) => m || data.defaults.secondary_arcs)
        setOutlineModel((m) => m || data.defaults.outline)
        setEntitiesModel((m) => m || data.defaults.entities)
        setInitialStateModel((m) => m || data.defaults.initial_state)
        setBaseline((prev) => ({
          ...prev,
          metadataModel: prev.metadataModel || data.defaults.metadata,
          charactersModel: prev.charactersModel || data.defaults.characters,
          worldbuildingModel: prev.worldbuildingModel || data.defaults.worldbuilding,
          primaryThreadModel: prev.primaryThreadModel || data.defaults.primary_thread,
          secondaryArcsModel: prev.secondaryArcsModel || data.defaults.secondary_arcs,
          outlineModel: prev.outlineModel || data.defaults.outline,
          entitiesModel: prev.entitiesModel || data.defaults.entities,
          initialStateModel: prev.initialStateModel || data.defaults.initial_state,
        }))
      } catch (err) {
        console.error(err)
      }
    }
    loadModels()
  }, [])

  function handleAddThread() {
    setSecondaryThreads((prev) => [...prev, { description: '', length: 30, priority: 50, heat: 50 }])
  }

  function updateThread<K extends keyof DraftSecondaryThread>(
    index: number,
    field: K,
    value: DraftSecondaryThread[K],
  ) {
    setSecondaryThreads((prev) =>
      prev.map((thread, i) => (i === index ? { ...thread, [field]: value } : thread)),
    )
  }

  function handleRemoveThread(index: number) {
    setSecondaryThreads((prev) => prev.filter((_, i) => i !== index))
  }

  const currentValues: PromptFormValues = {
    title,
    wordCount,
    premise,
    toneNotes,
    charactersNotes,
    primaryThread,
    romanceContent,
    secondaryThreads,
    primaryGenre,
    author,
    themes,
    metadataModel,
    charactersModel,
    worldbuildingModel,
    primaryThreadModel,
    secondaryArcsModel,
    outlineModel,
    entitiesModel,
    initialStateModel,
    metadataReasoning,
    charactersReasoning,
    worldbuildingReasoning,
    primaryThreadReasoning,
    secondaryArcsReasoning,
    outlineReasoning,
    entitiesReasoning,
    initialStateReasoning,
  }

  const isDirty = JSON.stringify(currentValues) !== JSON.stringify(baseline)

  function handleSubmitClick() {
    if (confirmMessage) {
      setConfirming(true)
      return
    }
    onSubmit(currentValues)
  }

  function handleConfirm() {
    setConfirming(false)
    onSubmit(currentValues)
  }

  return (
    <div className="novels-page">
      {confirming && confirmMessage && (
        <ConfirmDialog
          title={confirmTitle}
          message={confirmMessage}
          confirmLabel={submitLabel}
          onConfirm={handleConfirm}
          onCancel={() => setConfirming(false)}
        />
      )}

      <fieldset className="novels-create">
        <legend>{legend}</legend>

        <div className="field-row-stacked novels-create-title">
          <label htmlFor="novel-title">Title</label>
          <AutoGrowTextarea
            id="novel-title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
        </div>

        <div className="field-row-stacked novels-create-word-count">
          <label htmlFor="novel-word-count">
            Target Word Count — the primary thread's base length; secondary threads add on top of
            this
          </label>
          <input
            id="novel-word-count"
            type="number"
            min={MIN_WORD_COUNT}
            max={MAX_WORD_COUNT}
            step={500}
            className={wordCountValid ? undefined : 'field-invalid'}
            value={wordCountText}
            onChange={(e) => setWordCountText(e.target.value)}
          />
          {!wordCountValid && (
            <p className="novels-error">
              Must be between {MIN_WORD_COUNT.toLocaleString()} and {MAX_WORD_COUNT.toLocaleString()}{' '}
              words.
            </p>
          )}
        </div>

        <div className="field-row-stacked">
          <label htmlFor="novel-premise">Premise</label>
          <AutoGrowTextarea
            id="novel-premise"
            placeholder="The elevator pitch — what is this story about, in a sentence or two?"
            value={premise}
            onChange={(e) => setPremise(e.target.value)}
          />
        </div>

        <div className="field-row-stacked">
          <label htmlFor="novel-tone-notes">Tone (optional)</label>
          <AutoGrowTextarea
            id="novel-tone-notes"
            placeholder="Tone notes here, the more detail the better. Mood, atmosphere, comparable authors or works, how dark/light/serious/campy this should feel."
            value={toneNotes}
            onChange={(e) => setToneNotes(e.target.value)}
          />
        </div>

        <div className="field-row-stacked">
          <label htmlFor="novel-characters-notes">Characters (optional)</label>
          <AutoGrowTextarea
            id="novel-characters-notes"
            placeholder="Character notes here, the more detail the better. Who's in this story, what do they look like, what do they want, how do they talk?"
            value={charactersNotes}
            onChange={(e) => setCharactersNotes(e.target.value)}
          />
        </div>

        <div className="field-row-stacked">
          <label htmlFor="novel-primary-thread">Story Structure (optional)</label>
          <AutoGrowTextarea
            id="novel-primary-thread"
            placeholder="Story structure here, the more detail the better. This is the primary thread — what actually happens, in order, from beginning to end. This is the most important section."
            value={primaryThread}
            onChange={(e) => setPrimaryThread(e.target.value)}
          />
        </div>

        <fieldset className="novels-create-pipeline-step">
          <legend>Secondary Threads (optional)</legend>

          {secondaryThreads.map((thread, index) => (
            <div className="field-row-stacked novels-secondary-thread-form" key={index}>
              <label htmlFor={`novel-thread-description-${index}`}>Description</label>
              <AutoGrowTextarea
                id={`novel-thread-description-${index}`}
                placeholder="This secondary thread's storyline, the more detail the better."
                value={thread.description}
                onChange={(e) => updateThread(index, 'description', e.target.value)}
              />

              <label htmlFor={`novel-thread-length-${index}`}>
                Length ({thread.length}%) — how much of this storyline resolves in this story; the
                rest is left open for later
              </label>
              <input
                id={`novel-thread-length-${index}`}
                type="range"
                min={0}
                max={100}
                value={thread.length}
                onChange={(e) => updateThread(index, 'length', Number(e.target.value))}
              />

              <label htmlFor={`novel-thread-priority-${index}`}>
                Priority ({thread.priority}/100) — how much narrative weight this thread gets
              </label>
              <input
                id={`novel-thread-priority-${index}`}
                type="range"
                min={0}
                max={100}
                value={thread.priority}
                onChange={(e) => updateThread(index, 'priority', Number(e.target.value))}
              />

              <label htmlFor={`novel-thread-heat-${index}`}>
                Heat ({thread.heat}/100) — romantic/sexual intensity of this thread
              </label>
              <input
                id={`novel-thread-heat-${index}`}
                type="range"
                min={0}
                max={100}
                value={thread.heat}
                onChange={(e) => updateThread(index, 'heat', Number(e.target.value))}
              />

              <div className="field-row novels-secondary-thread-form-actions">
                <button type="button" onClick={() => handleRemoveThread(index)}>
                  Delete
                </button>
              </div>
            </div>
          ))}

          {secondaryThreads.length < MAX_SECONDARY_THREADS && (
            <div className="field-row">
              <button type="button" onClick={handleAddThread}>
                Create Thread
              </button>
            </div>
          )}
        </fieldset>

        <div className="field-row-stacked">
          <label htmlFor="novel-romance-content">Sexual/Romance (optional)</label>
          <AutoGrowTextarea
            id="novel-romance-content"
            placeholder="Romance and sexual content notes here, the more detail the better. Pairings, dynamics, spice level, specific scenarios or kinks to include."
            value={romanceContent}
            onChange={(e) => setRomanceContent(e.target.value)}
          />
        </div>

        <div className="novels-create-grid">
          <div className="field-row-stacked">
            <label htmlFor="novel-genre">Primary Genre (optional)</label>
            <AutoGrowTextarea
              id="novel-genre"
              value={primaryGenre}
              onChange={(e) => setPrimaryGenre(e.target.value)}
            />
          </div>

          <div className="field-row-stacked">
            <label htmlFor="novel-author">Author's Name (optional)</label>
            <AutoGrowTextarea
              id="novel-author"
              value={author}
              onChange={(e) => setAuthor(e.target.value)}
            />
          </div>

          <div className="field-row-stacked">
            <label htmlFor="novel-themes">Themes (optional, comma-separated)</label>
            <AutoGrowTextarea
              id="novel-themes"
              value={themes}
              onChange={(e) => setThemes(e.target.value)}
            />
          </div>
        </div>

        <div className="novels-create-pipeline">
          <fieldset className="novels-create-pipeline-step">
            <legend>Metadata</legend>
            <div className="novels-create-pipeline-row">
              <div className="field-row-stacked novels-create-pipeline-select">
                <label htmlFor="novel-metadata-model">Model</label>
                <select
                  id="novel-metadata-model"
                  value={metadataModel}
                  onChange={(e) => setMetadataModel(e.target.value)}
                >
                  {availableModels.map((m) => (
                    <option key={m} value={m}>
                      {m}
                    </option>
                  ))}
                </select>
              </div>
              <div className="field-row">
                <input
                  id="novel-metadata-reasoning"
                  type="checkbox"
                  checked={metadataReasoning}
                  onChange={(e) => setMetadataReasoning(e.target.checked)}
                />
                <label htmlFor="novel-metadata-reasoning">Reasoning</label>
              </div>
            </div>
          </fieldset>

          <fieldset className="novels-create-pipeline-step">
            <legend>Characters</legend>
            <div className="novels-create-pipeline-row">
              <div className="field-row-stacked novels-create-pipeline-select">
                <label htmlFor="novel-characters-model">Model</label>
                <select
                  id="novel-characters-model"
                  value={charactersModel}
                  onChange={(e) => setCharactersModel(e.target.value)}
                >
                  {availableModels.map((m) => (
                    <option key={m} value={m}>
                      {m}
                    </option>
                  ))}
                </select>
              </div>
              <div className="field-row">
                <input
                  id="novel-characters-reasoning"
                  type="checkbox"
                  checked={charactersReasoning}
                  onChange={(e) => setCharactersReasoning(e.target.checked)}
                />
                <label htmlFor="novel-characters-reasoning">Reasoning</label>
              </div>
            </div>
          </fieldset>

          <fieldset className="novels-create-pipeline-step">
            <legend>Worldbuilding</legend>
            <div className="novels-create-pipeline-row">
              <div className="field-row-stacked novels-create-pipeline-select">
                <label htmlFor="novel-worldbuilding-model">Model</label>
                <select
                  id="novel-worldbuilding-model"
                  value={worldbuildingModel}
                  onChange={(e) => setWorldbuildingModel(e.target.value)}
                >
                  {availableModels.map((m) => (
                    <option key={m} value={m}>
                      {m}
                    </option>
                  ))}
                </select>
              </div>
              <div className="field-row">
                <input
                  id="novel-worldbuilding-reasoning"
                  type="checkbox"
                  checked={worldbuildingReasoning}
                  onChange={(e) => setWorldbuildingReasoning(e.target.checked)}
                />
                <label htmlFor="novel-worldbuilding-reasoning">Reasoning</label>
              </div>
            </div>
          </fieldset>

          <fieldset className="novels-create-pipeline-step">
            <legend>Primary Thread</legend>
            <div className="novels-create-pipeline-row">
              <div className="field-row-stacked novels-create-pipeline-select">
                <label htmlFor="novel-primary-thread-model">Model</label>
                <select
                  id="novel-primary-thread-model"
                  value={primaryThreadModel}
                  onChange={(e) => setPrimaryThreadModel(e.target.value)}
                >
                  {availableModels.map((m) => (
                    <option key={m} value={m}>
                      {m}
                    </option>
                  ))}
                </select>
              </div>
              <div className="field-row">
                <input
                  id="novel-primary-thread-reasoning"
                  type="checkbox"
                  checked={primaryThreadReasoning}
                  onChange={(e) => setPrimaryThreadReasoning(e.target.checked)}
                />
                <label htmlFor="novel-primary-thread-reasoning">Reasoning</label>
              </div>
            </div>
          </fieldset>

          <fieldset className="novels-create-pipeline-step">
            <legend>Secondary Arcs</legend>
            <div className="novels-create-pipeline-row">
              <div className="field-row-stacked novels-create-pipeline-select">
                <label htmlFor="novel-secondary-arcs-model">Model</label>
                <select
                  id="novel-secondary-arcs-model"
                  value={secondaryArcsModel}
                  onChange={(e) => setSecondaryArcsModel(e.target.value)}
                >
                  {availableModels.map((m) => (
                    <option key={m} value={m}>
                      {m}
                    </option>
                  ))}
                </select>
              </div>
              <div className="field-row">
                <input
                  id="novel-secondary-arcs-reasoning"
                  type="checkbox"
                  checked={secondaryArcsReasoning}
                  onChange={(e) => setSecondaryArcsReasoning(e.target.checked)}
                />
                <label htmlFor="novel-secondary-arcs-reasoning">Reasoning</label>
              </div>
            </div>
          </fieldset>

          <fieldset className="novels-create-pipeline-step">
            <legend>Outline</legend>
            <div className="novels-create-pipeline-row">
              <div className="field-row-stacked novels-create-pipeline-select">
                <label htmlFor="novel-outline-model">Model</label>
                <select
                  id="novel-outline-model"
                  value={outlineModel}
                  onChange={(e) => setOutlineModel(e.target.value)}
                >
                  {availableModels.map((m) => (
                    <option key={m} value={m}>
                      {m}
                    </option>
                  ))}
                </select>
              </div>
              <div className="field-row">
                <input
                  id="novel-outline-reasoning"
                  type="checkbox"
                  checked={outlineReasoning}
                  onChange={(e) => setOutlineReasoning(e.target.checked)}
                />
                <label htmlFor="novel-outline-reasoning">Reasoning</label>
              </div>
            </div>
          </fieldset>

          <fieldset className="novels-create-pipeline-step">
            <legend>Entities</legend>
            <div className="novels-create-pipeline-row">
              <div className="field-row-stacked novels-create-pipeline-select">
                <label htmlFor="novel-entities-model">Model</label>
                <select
                  id="novel-entities-model"
                  value={entitiesModel}
                  onChange={(e) => setEntitiesModel(e.target.value)}
                >
                  {availableModels.map((m) => (
                    <option key={m} value={m}>
                      {m}
                    </option>
                  ))}
                </select>
              </div>
              <div className="field-row">
                <input
                  id="novel-entities-reasoning"
                  type="checkbox"
                  checked={entitiesReasoning}
                  onChange={(e) => setEntitiesReasoning(e.target.checked)}
                />
                <label htmlFor="novel-entities-reasoning">Reasoning</label>
              </div>
            </div>
          </fieldset>

          <fieldset className="novels-create-pipeline-step" disabled>
            <legend>Initial State (coming soon)</legend>
            <div className="novels-create-pipeline-row">
              <div className="field-row-stacked novels-create-pipeline-select">
                <label htmlFor="novel-initial-state-model">Model</label>
                <select
                  id="novel-initial-state-model"
                  value={initialStateModel}
                  onChange={(e) => setInitialStateModel(e.target.value)}
                  disabled
                >
                  {availableModels.map((m) => (
                    <option key={m} value={m}>
                      {m}
                    </option>
                  ))}
                </select>
              </div>
              <div className="field-row">
                <input
                  id="novel-initial-state-reasoning"
                  type="checkbox"
                  checked={initialStateReasoning}
                  onChange={(e) => setInitialStateReasoning(e.target.checked)}
                  disabled
                />
                <label htmlFor="novel-initial-state-reasoning">Reasoning</label>
              </div>
            </div>
          </fieldset>
        </div>

        {error && <p className="novels-error">{error}</p>}

        <div className="novels-create-actions">
          <button
            type="button"
            disabled={
              submitting ||
              !title.trim() ||
              !premise.trim() ||
              !wordCountValid ||
              (requireDirty && !isDirty)
            }
            onClick={handleSubmitClick}
          >
            {submitting ? submitPendingLabel : submitLabel}
          </button>
        </div>
      </fieldset>
    </div>
  )
}

export default PromptForm

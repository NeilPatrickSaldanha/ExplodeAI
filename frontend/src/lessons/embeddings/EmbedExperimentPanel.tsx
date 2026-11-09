import * as Tabs from '@radix-ui/react-tabs'
import { ExperimentGuide, TabHint } from '../../components/ExperimentGuide'
import type { EmbedParams, EmbedResult, Lesson, Visual } from '../../api/types'
import { KindBadge, Segmented, Slider } from '../../components/controls'
import { Named } from '../../voice'
import { Chips } from '../tokenization/TokStageIO'
import { VectorStrip } from '../rag/StageIO'
import { Neighbours, SemanticSpace, TokenHeat } from './EmbedViews'

interface Props {
  lesson: Lesson
  params: EmbedParams
  update: <K extends keyof EmbedParams>(key: K, value: EmbedParams[K]) => void
  result: EmbedResult | null
  loading: boolean
  error: string | null
  locked?: (keyof EmbedParams)[]
}

export function EmbedExperimentPanel({ lesson, params, update, result, loading, error, locked = [] }: Props) {
  const isLocked = (k: keyof EmbedParams) => locked.includes(k)
  const presetNote = lesson.experiment.presets.find((p) => p.text === params.text)?.note
  const visual = (id: string) => lesson.visuals.find((v) => v.id === id) as Visual
  return (
    <div className="experiment" aria-busy={loading}>
      <div className="experiment__head">
        <KindBadge visual={visual('experiment')} />
        <span className="label" role="status">
          {loading ? 'RUNNING…' : error ? 'ERROR' : result ? `${result.query.dim}-D · ${result.query.embedder.toUpperCase()}${result.comparable ? '' : ' · NOT COMPARABLE'}` : ''}
        </span>
      </div>
      <p className="experiment__corpus">{lesson.experiment.corpus_note}</p>

      <div className={`field${isLocked('text') ? ' is-locked' : ''}`}>
        <label className="label" htmlFor="emb-text">
          <Named label="Your text" />
        </label>
        <input id="emb-text" className="input" value={params.text} maxLength={4000} disabled={isLocked('text')} onChange={(e) => update('text', e.target.value)} />
        {!isLocked('text') && (
          <div className="presets" role="group" aria-label="Example texts">
            {lesson.experiment.presets.map((p) => (
              <button key={p.label} type="button" className="chip" onClick={() => update('text', p.text ?? '')}>
                {p.label}
              </button>
            ))}
          </div>
        )}
        {!isLocked('text') && <ExperimentGuide guide={lesson.experiment.guide} presets={lesson.experiment.presets} value={params.text} />}
        {!lesson.experiment.guide && presetNote && <p className="notice">{presetNote}</p>}
      </div>

      <div className="controls">
        <Segmented label="Library embedder" value={params.library_embedder} disabled={isLocked('library_embedder')} onChange={(v) => update('library_embedder', v)}
          options={[{ value: 'neural', label: 'Neural (bge-small)' }, { value: 'lexical', label: 'Lexical' }]} />
        <Segmented label="Your-text embedder" value={params.query_embedder} disabled={isLocked('query_embedder')} onChange={(v) => update('query_embedder', v)}
          options={[{ value: 'neural', label: 'Neural (bge-small)' }, { value: 'lexical', label: 'Lexical' }]} />
        <Segmented label="Pooling" value={params.pooling} disabled={isLocked('pooling')} onChange={(v) => update('pooling', v)}
          options={[{ value: 'cls', label: '[CLS] token' }, { value: 'mean', label: 'Mean of tokens' }]} />
        <Segmented label="Similarity" value={params.metric} disabled={isLocked('metric')} onChange={(v) => update('metric', v)}
          options={[{ value: 'cosine', label: 'Cosine' }, { value: 'dot', label: 'Dot product' }, { value: 'euclidean', label: 'Euclidean' }]} />
        <Segmented label="Normalize to length 1" value={params.normalize ? 'on' : 'off'} disabled={isLocked('normalize')} onChange={(v) => update('normalize', v === 'on')}
          options={[{ value: 'on', label: 'On' }, { value: 'off', label: 'Off' }]} />
        <Segmented label="BGE query instruction" value={params.query_instruction ? 'on' : 'off'} disabled={isLocked('query_instruction')} onChange={(v) => update('query_instruction', v === 'on')}
          options={[{ value: 'off', label: 'Off' }, { value: 'on', label: 'On' }]} />
        <Slider id="emb-topk" label="Neighbours" min={1} max={10} value={params.top_k} disabled={isLocked('top_k')} onChange={(v) => update('top_k', v)} />
      </div>

      {error && (
        <p className="notice notice--error" role="alert">
          {error}
        </p>
      )}

      {result && (
        <Tabs.Root defaultValue="space" className="rtabs">
          <Tabs.List className="rtabs__list" aria-label="Experiment results">
            <Tabs.Trigger value="space" className="rtabs__tab"><Named label="Semantic space" /></Tabs.Trigger>
            <Tabs.Trigger value="neighbours" className="rtabs__tab"><Named label="Neighbours" /></Tabs.Trigger>
            <Tabs.Trigger value="tokens" className="rtabs__tab"><Named label="Tokens" /></Tabs.Trigger>
            <Tabs.Trigger value="vector" className="rtabs__tab"><Named label="Vector" /></Tabs.Trigger>
          </Tabs.List>
          <Tabs.Content value="space" className="rtabs__panel">
<TabHint guide={lesson.experiment.guide} id="space" />
            <KindBadge visual={visual('semantic-space')} />
            <SemanticSpace result={result} />
          </Tabs.Content>
          <Tabs.Content value="neighbours" className="rtabs__panel">
<TabHint guide={lesson.experiment.guide} id="neighbours" />
            <Neighbours result={result} />
          </Tabs.Content>
          <Tabs.Content value="tokens" className="rtabs__panel">
<TabHint guide={lesson.experiment.guide} id="tokens" />
            <Chips items={result.query.tokens.map((t) => t.text)} max={60} label="Tokens the model reads" />
            {result.query.truncated && <p className="notice notice--warn">Longer than {result.model.max_tokens} tokens: the rest was cut off before the model saw it.</p>}
            {result.query.token_vectors && <TokenHeat tokens={result.query.tokens} rows={result.query.token_vectors} />}
          </Tabs.Content>
          <Tabs.Content value="vector" className="rtabs__panel">
<TabHint guide={lesson.experiment.guide} id="vector" />
            <VectorStrip values={result.query.pooled_preview} label={`First ${result.query.pooled_preview.length} of ${result.query.dim} values`} />
            <p className="label">
              FIRST {result.query.pooled_preview.length} OF {result.query.dim} VALUES · LENGTH {result.query.norm_before.toFixed(3)} → {result.query.norm_after.toFixed(3)}
            </p>
          </Tabs.Content>
        </Tabs.Root>
      )}
    </div>
  )
}

import * as Tabs from '@radix-ui/react-tabs'
import { lazy, Suspense } from 'react'
import type { Lesson, RagParams, RagResult, Visual } from '../../api/types'
import { KindBadge, Segmented, Slider } from '../../components/controls'
import { AnswerView, ChunkDocView, PromptView, RankingTable } from './ResultViews'

const VectorSpace = lazy(() => import('./VectorSpace').then((m) => ({ default: m.VectorSpace })))

interface Props {
  lesson: Lesson
  params: RagParams
  update: <K extends keyof RagParams>(key: K, value: RagParams[K]) => void
  result: RagResult | null
  loading: boolean
  error: string | null
  locked?: (keyof RagParams)[]
  neuralAvailable: boolean
}

export function ExperimentPanel({ lesson, params, update, result, loading, error, locked = [], neuralAvailable }: Props) {
  const isLocked = (k: keyof RagParams) => locked.includes(k)
  const visual = (id: string) => lesson.visuals.find((v) => v.id === id) as Visual
  return (
    <div className="experiment" aria-busy={loading}>
      <div className="experiment__head">
        <KindBadge visual={visual('experiment')} />
        <span className="label" role="status">
          {loading ? 'RUNNING…' : error ? 'ERROR' : result ? `${result.chunks.length} CHUNKS · ${result.embedding.name}` : ''}
        </span>
      </div>
      <p className="experiment__corpus">{lesson.experiment.corpus_note}</p>

      <div className={`field${isLocked('query') ? ' is-locked' : ''}`}>
        <label className="label" htmlFor="q">
          Question
        </label>
        <input
          id="q"
          className="input"
          value={params.query}
          maxLength={300}
          disabled={isLocked('query')}
          onChange={(e) => update('query', e.target.value)}
        />
        {!isLocked('query') && (
          <div className="presets" role="group" aria-label="Example questions">
            {lesson.experiment.presets.map((p) => (
              <button key={p.label} type="button" className="chip" onClick={() => update('query', p.query ?? '')}>
                {p.label}
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="controls">
        <Segmented
          label="Chunking"
          value={params.strategy}
          disabled={isLocked('strategy')}
          onChange={(v) => update('strategy', v)}
          options={[
            { value: 'sentence', label: 'Sentences' },
            { value: 'fixed', label: 'Fixed words' },
          ]}
        />
        <Slider id="size" label="Chunk size" unit="words" min={4} max={120} value={params.chunk_size} disabled={isLocked('chunk_size')} onChange={(v) => update('chunk_size', v)} />
        <Slider id="overlap" label="Overlap" unit="words" min={0} max={Math.max(0, Math.min(60, params.chunk_size - 1))} value={params.overlap} disabled={isLocked('overlap')} onChange={(v) => update('overlap', v)} />
        <Segmented
          label="Retrieval"
          value={params.method}
          disabled={isLocked('method')}
          onChange={(v) => update('method', v)}
          options={[
            { value: 'dense', label: 'Dense' },
            { value: 'bm25', label: 'BM25' },
            { value: 'hybrid', label: 'Hybrid' },
          ]}
        />
        <Slider id="topk" label="Top-k" min={1} max={10} value={params.top_k} disabled={isLocked('top_k')} onChange={(v) => update('top_k', v)} />
        <Slider id="budget" label="Context budget" unit="words" min={10} max={400} step={5} value={params.context_budget_words} disabled={isLocked('context_budget_words')} onChange={(v) => update('context_budget_words', v)} />
        <Segmented
          label="Embedder"
          value={params.embedder}
          disabled={isLocked('embedder')}
          onChange={(v) => update('embedder', v)}
          options={[
            { value: 'lexical-hashing', label: 'TF-IDF hashing' },
            { value: 'neural-local', label: neuralAvailable ? 'Local neural' : 'Local neural (not installed)', disabled: !neuralAvailable },
          ]}
        />
      </div>
      {params.embedder === 'lexical-hashing' && (
        <p className="notice">
          The built-in embedder is lexical: it hashes words into {result?.embedding.dim ?? 1024} dimensions, so “refund”
          and “money back” don't land near each other. A neural embedding model would place them close.
        </p>
      )}

      {error && (
        <p className="notice notice--error" role="alert">
          {error}. Check that the backend is running (<code>make dev</code>).
        </p>
      )}

      {result && (
        <Tabs.Root defaultValue="chunks" className="rtabs">
          <Tabs.List className="rtabs__list" aria-label="Experiment results">
            <Tabs.Trigger value="chunks" className="rtabs__tab">Chunks</Tabs.Trigger>
            <Tabs.Trigger value="space" className="rtabs__tab">Vector space</Tabs.Trigger>
            <Tabs.Trigger value="ranking" className="rtabs__tab">Ranking</Tabs.Trigger>
            <Tabs.Trigger value="prompt" className="rtabs__tab">Prompt</Tabs.Trigger>
            <Tabs.Trigger value="answer" className="rtabs__tab">Answer</Tabs.Trigger>
          </Tabs.List>
          <Tabs.Content value="chunks" className="rtabs__panel">
            <ChunkDocView result={result} />
          </Tabs.Content>
          <Tabs.Content value="space" className="rtabs__panel">
            <KindBadge visual={visual('vector-space')} />
            <Suspense fallback={<p className="label">Loading…</p>}>
              <VectorSpace result={result} />
            </Suspense>
          </Tabs.Content>
          <Tabs.Content value="ranking" className="rtabs__panel">
            <RankingTable result={result} />
          </Tabs.Content>
          <Tabs.Content value="prompt" className="rtabs__panel">
            <PromptView result={result} />
          </Tabs.Content>
          <Tabs.Content value="answer" className="rtabs__panel">
            <KindBadge visual={visual('answer')} />
            <AnswerView result={result} params={locked.length ? undefined : params} />
          </Tabs.Content>
        </Tabs.Root>
      )}
    </div>
  )
}

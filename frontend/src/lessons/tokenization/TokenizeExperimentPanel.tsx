import * as Tabs from '@radix-ui/react-tabs'
import type { Lesson, TokenizeParams, TokenizeResult, Visual } from '../../api/types'
import { KindBadge, Segmented, Slider } from '../../components/controls'
import { MergeReplay, MergeTable, TokenStrip, TradeoffChart } from './TokenViews'

interface Props {
  lesson: Lesson
  params: TokenizeParams
  update: <K extends keyof TokenizeParams>(key: K, value: TokenizeParams[K]) => void
  result: TokenizeResult | null
  loading: boolean
  error: string | null
  locked?: (keyof TokenizeParams)[]
  maxMerges: number
  reducedMotion: boolean
}

export function TokenizeExperimentPanel({ lesson, params, update, result, loading, error, locked = [], maxMerges, reducedMotion }: Props) {
  const isLocked = (k: keyof TokenizeParams) => locked.includes(k)
  const visual = (id: string) => lesson.visuals.find((v) => v.id === id) as Visual
  const ranOut = result && result.training.merges_learned < result.training.merges_requested
  return (
    <div className="experiment" aria-busy={loading}>
      <div className="experiment__head">
        <KindBadge visual={visual('experiment')} />
        <span className="label" role="status">
          {loading ? 'RUNNING…' : error ? 'ERROR' : result ? `${result.encoding.count} TOKENS · VOCAB ${result.vocabulary.size}` : ''}
        </span>
      </div>
      <p className="experiment__corpus">{lesson.experiment.corpus_note}</p>

      <div className={`field${isLocked('text') ? ' is-locked' : ''}`}>
        <label className="label" htmlFor="tok-text">
          Text to tokenize
        </label>
        <input id="tok-text" className="input" value={params.text} maxLength={400} disabled={isLocked('text')} onChange={(e) => update('text', e.target.value)} />
        {!isLocked('text') && (
          <div className="presets" role="group" aria-label="Example texts">
            {lesson.experiment.presets.map((p) => (
              <button key={p.label} type="button" className="chip" onClick={() => update('text', p.text ?? '')}>
                {p.label}
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="controls">
        <Slider id="merges" label="Merges learned" min={0} max={maxMerges} value={params.merges} disabled={isLocked('merges')} onChange={(v) => update('merges', v)} />
        <Segmented
          label="Base alphabet"
          value={params.base}
          disabled={isLocked('base')}
          onChange={(v) => update('base', v)}
          options={[
            { value: 'bytes', label: '256 bytes' },
            { value: 'chars', label: 'Training characters' },
          ]}
        />
        <Segmented
          label="Pre-tokenizer"
          value={params.pre_tokenizer}
          disabled={isLocked('pre_tokenizer')}
          onChange={(v) => update('pre_tokenizer', v)}
          options={[
            { value: 'words', label: 'Words' },
            { value: 'none', label: 'None' },
          ]}
        />
        <Segmented
          label="Merge order when encoding"
          value={params.merge_order}
          disabled={isLocked('merge_order')}
          onChange={(v) => update('merge_order', v)}
          options={[
            { value: 'learned', label: 'Learned order' },
            { value: 'reversed', label: 'Reversed' },
          ]}
        />
      </div>
      <p className="notice">
        This tokenizer is trained on the sample corpus only. Its token counts tell you nothing about the GPT, Claude or
        Gemini tokenizers, which learned far larger vocabularies from far more text.
      </p>
      {ranOut && (
        <p className="notice notice--warn" role="status">
          Training ran out of pairs after {result.training.merges_learned} merges: every piece of the corpus is already a single token.
        </p>
      )}

      {error && (
        <p className="notice notice--error" role="alert">
          {error}. Check that the backend is running (<code>make dev</code>).
        </p>
      )}

      {result && (
        <Tabs.Root defaultValue="tokens" className="rtabs">
          <Tabs.List className="rtabs__list" aria-label="Experiment results">
            <Tabs.Trigger value="tokens" className="rtabs__tab">Tokens</Tabs.Trigger>
            <Tabs.Trigger value="replay" className="rtabs__tab">Replay</Tabs.Trigger>
            <Tabs.Trigger value="merges" className="rtabs__tab">Merges</Tabs.Trigger>
            <Tabs.Trigger value="tradeoff" className="rtabs__tab">Trade-off</Tabs.Trigger>
          </Tabs.List>
          <Tabs.Content value="tokens" className="rtabs__panel">
            <TokenStrip result={result} />
          </Tabs.Content>
          <Tabs.Content value="replay" className="rtabs__panel">
            <KindBadge visual={visual('merge-replay')} />
            <MergeReplay result={result} reducedMotion={reducedMotion} />
          </Tabs.Content>
          <Tabs.Content value="merges" className="rtabs__panel">
            <MergeTable result={result} />
          </Tabs.Content>
          <Tabs.Content value="tradeoff" className="rtabs__panel">
            <KindBadge visual={visual('tradeoff')} />
            <TradeoffChart result={result} />
          </Tabs.Content>
        </Tabs.Root>
      )}
    </div>
  )
}

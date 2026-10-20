import * as Tabs from '@radix-ui/react-tabs'
import { useState } from 'react'
import type { AttendParams, AttendResult, Lesson, Visual } from '../../api/types'
import { KindBadge, Segmented } from '../../components/controls'
import { AttentionGrid, LookFrom, OutputView, QKVView, StatsStrip } from './AttendViews'

interface Props {
  lesson: Lesson
  params: AttendParams
  update: <K extends keyof AttendParams>(key: K, value: AttendParams[K]) => void
  result: AttendResult | null
  loading: boolean
  error: string | null
  locked?: (keyof AttendParams)[]
}

const onOff = (v: boolean) => (v ? 'on' : 'off')

export function AttendExperimentPanel({ lesson, params, update, result, loading, error, locked = [] }: Props) {
  const isLocked = (k: keyof AttendParams) => locked.includes(k)
  const visual = (id: string) => lesson.visuals.find((v) => v.id === id) as Visual
  const presetNote = lesson.experiment.presets.find((p) => p.text === params.text)?.note
  const [row, setRow] = useState(0)
  const heads = result?.model.heads ?? params.heads
  const head = Math.min(params.head, heads - 1)
  const [view, setView] = useState<'mean' | number>('mean')
  const shown = view === 'mean' || view >= heads ? 'mean' : view
  const safeRow = result ? Math.min(row, result.tokens.length - 1) : 0
  return (
    <div className="experiment" aria-busy={loading}>
      <div className="experiment__head">
        <KindBadge visual={visual('experiment')} />
        <span className="label" role="status">
          {loading ? 'RUNNING…' : error ? 'ERROR' : result ? `TOY LAYER · ${result.model.heads} HEAD${result.model.heads > 1 ? 'S' : ''} · d_k ${result.model.head_dim}` : ''}
        </span>
      </div>
      <p className="experiment__corpus">{lesson.experiment.corpus_note}</p>

      <div className={`field${isLocked('text') ? ' is-locked' : ''}`}>
        <label className="label" htmlFor="att-text">
          Sentence (up to 12 words)
        </label>
        <input id="att-text" className="input" value={params.text} maxLength={120} disabled={isLocked('text')} onChange={(e) => update('text', e.target.value)} />
        {!isLocked('text') && (
          <div className="presets" role="group" aria-label="Example sentences">
            {lesson.experiment.presets.map((p) => (
              <button key={p.label} type="button" className="chip" onClick={() => update('text', p.text ?? '')}>
                {p.label}
              </button>
            ))}
          </div>
        )}
        {presetNote && <p className="notice">{presetNote}</p>}
      </div>

      <div className="controls">
        <Segmented label="Heads" value={String(params.heads)} disabled={isLocked('heads')} onChange={(v) => update('heads', Number(v) as AttendParams['heads'])}
          options={[1, 2, 4, 8].map((h) => ({ value: String(h), label: `${h}` }))} />
        <Segmented label="Scale scores by 1/√d_k" value={onOff(params.scale)} disabled={isLocked('scale')} onChange={(v) => update('scale', v === 'on')}
          options={[{ value: 'on', label: 'On' }, { value: 'off', label: 'Off' }]} />
        <Segmented label="Causal mask (hide later words)" value={onOff(params.causal)} disabled={isLocked('causal')} onChange={(v) => update('causal', v === 'on')}
          options={[{ value: 'off', label: 'Off' }, { value: 'on', label: 'On' }]} />
        <Segmented label="Position vectors" value={onOff(params.position)} disabled={isLocked('position')} onChange={(v) => update('position', v === 'on')}
          options={[{ value: 'on', label: 'On' }, { value: 'off', label: 'Off' }]} />
      </div>

      {error && (
        <p className="notice notice--error" role="alert">
          {error}
        </p>
      )}

      {result && (
        <>
          <p className="notice" role="note">
            {result.model.note}
          </p>
          <Tabs.Root defaultValue="grid" className="rtabs">
            <Tabs.List className="rtabs__list" aria-label="Experiment results">
              <Tabs.Trigger value="grid" className="rtabs__tab">Attention grid</Tabs.Trigger>
              <Tabs.Trigger value="word" className="rtabs__tab">One word</Tabs.Trigger>
              <Tabs.Trigger value="qkv" className="rtabs__tab">Q · K · V</Tabs.Trigger>
              <Tabs.Trigger value="out" className="rtabs__tab">Output</Tabs.Trigger>
            </Tabs.List>
            <Tabs.Content value="grid" className="rtabs__panel">
              {heads > 1 && (
                <Segmented label="Head to show" value={String(shown)} onChange={(v) => { const x = v === 'mean' ? 'mean' : Number(v); setView(x); if (x !== 'mean') update('head', x) }}
                  options={[{ value: 'mean', label: 'Average' }, ...Array.from({ length: heads }, (_, i) => ({ value: String(i), label: `Head ${i + 1}` }))]} />
              )}
              <AttentionGrid
                tokens={result.tokens.map((t) => t.text)}
                weights={shown === 'mean' ? result.weights_mean : result.heads[shown].weights}
                causal={result.params.causal}
                selectedRow={safeRow}
                onRow={setRow}
                caption={`Attention weights, ${shown === 'mean' ? 'average of all heads' : `head ${shown + 1}`}`}
              />
              <StatsStrip result={result} />
            </Tabs.Content>
            <Tabs.Content value="word" className="rtabs__panel">
              <LookFrom result={result} row={safeRow} onRow={setRow} head={shown} />
            </Tabs.Content>
            <Tabs.Content value="qkv" className="rtabs__panel">
              <QKVView result={result} head={head} />
            </Tabs.Content>
            <Tabs.Content value="out" className="rtabs__panel">
              <OutputView result={result} />
            </Tabs.Content>
          </Tabs.Root>
        </>
      )}
    </div>
  )
}

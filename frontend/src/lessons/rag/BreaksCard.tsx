import { CheckCircle, Prohibit, Warning, XCircle } from '@phosphor-icons/react'
import { useState } from 'react'
import { api } from '../../api/client'
import type { AblationOutcome, AblationResult, Component, RagParams, Visual } from '../../api/types'
import { KindBadge } from '../../components/controls'

interface Props {
  component: Component
  params: RagParams
  visual?: Visual
}

/**
 * What breaks if this stage is removed? States the effect, then lets the learner
 * actually remove it: the pipeline runs for real without the stage, side by side
 * with the full pipeline. The parent keys this card by stage + settings so a
 * stale comparison never shows.
 */
export function BreaksCard({ component, params, visual }: Props) {
  const [result, setResult] = useState<AblationResult | null>(null)
  const [state, setState] = useState<'idle' | 'loading' | 'error'>('idle')

  const run = async () => {
    setState('loading')
    try {
      setResult(await api.ablate(params, component.id))
      setState('idle')
    } catch {
      setState('error')
    }
  }

  return (
    <section className="breaks" aria-labelledby={`breaks-${component.id}`}>
      <h4 id={`breaks-${component.id}`} className="breaks__title">
        <Warning weight="bold" aria-hidden /> What breaks if removed?
      </h4>
      <p className="breaks__text">{component.breaks_if_removed}</p>
      {!result && (
        <button type="button" className="btn breaks__run" onClick={run} disabled={state === 'loading'} data-state={state === 'loading' ? 'loading' : undefined}>
          <Prohibit aria-hidden /> {state === 'loading' ? 'Running…' : `Run without the ${component.label.toLowerCase()}`}
        </button>
      )}
      {state === 'error' && <p className="notice notice--error" role="alert">The comparison could not run. Is the backend up?</p>}
      {result && (
        <div className="breaks__compare" role="status" aria-live="polite">
          {visual && <KindBadge visual={visual} />}
          <div className="breaks__cols">
            <Outcome title="Full pipeline" o={result.baseline} />
            <Outcome title={`Without ${component.label.toLowerCase()}`} o={result.ablated} broken />
          </div>
        </div>
      )}
    </section>
  )
}

function Outcome({ title, o, broken }: { title: string; o: AblationOutcome; broken?: boolean }) {
  return (
    <div className={`outcome${broken ? ' outcome--broken' : ''}`}>
      <p className="label">{title}</p>
      <dl className="outcome__stats">
        <div><dt>Chunks</dt><dd>{o.chunks}</dd></div>
        <div><dt>Retrieved</dt><dd>{o.retrieved.length}</dd></div>
        <div><dt>In prompt</dt><dd>{o.prompt.included.length}</dd></div>
      </dl>
      <p className="outcome__answer">
        {o.answer.has_answer ? <CheckCircle weight="fill" aria-hidden className="is-pass" /> : <XCircle weight="fill" aria-hidden className="is-fail" />}
        <span>{o.answer.text ?? 'No answer: nothing generates one.'}</span>
      </p>
      {o.notes.length > 0 && <p className="outcome__notes">{o.notes.join(' · ')}</p>}
    </div>
  )
}

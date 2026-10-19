import { Prohibit, Warning } from '@phosphor-icons/react'
import { useState, type ReactNode } from 'react'
import type { Component, Visual } from '../../../api/types'
import { KindBadge } from '../../../components/controls'

interface Props<T> {
  component: Component
  /** Runs the real pipeline twice: as configured, and with this stage removed. */
  run: () => Promise<{ baseline: T; ablated: T }>
  renderOutcome: (outcome: T, broken: boolean) => ReactNode
  visual?: Visual
  /** Name of the full system, e.g. "pipeline" or "tokenizer". */
  system?: string
}

/**
 * What breaks if this stage is removed? States the effect, then lets the learner
 * actually remove it and compare against the full system, side by side. Lesson-
 * agnostic: the caller supplies the runner and how to draw an outcome. The parent
 * keys this card by stage + settings so a stale comparison never shows.
 */
export function BreaksCard<T>({ component, run, renderOutcome, visual, system = 'pipeline' }: Props<T>) {
  const [result, setResult] = useState<{ baseline: T; ablated: T } | null>(null)
  const [state, setState] = useState<'idle' | 'loading' | 'error'>('idle')

  const go = async () => {
    setState('loading')
    try {
      setResult(await run())
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
        <button type="button" className="btn breaks__run" onClick={go} disabled={state === 'loading'} data-state={state === 'loading' ? 'loading' : undefined}>
          <Prohibit aria-hidden /> {state === 'loading' ? 'Running…' : `Run without the ${component.label.toLowerCase()}`}
        </button>
      )}
      {state === 'error' && <p className="notice notice--error" role="alert">The comparison could not run. Is the backend up?</p>}
      {result && (
        <div className="breaks__compare" role="status" aria-live="polite">
          {visual && <KindBadge visual={visual} />}
          <div className="breaks__cols">
            <div className="outcome">
              <p className="label">Full {system}</p>
              {renderOutcome(result.baseline, false)}
            </div>
            <div className="outcome outcome--broken">
              <p className="label">Without {component.label.toLowerCase()}</p>
              {renderOutcome(result.ablated, true)}
            </div>
          </div>
        </div>
      )}
    </section>
  )
}

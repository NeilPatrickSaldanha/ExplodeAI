import { CheckCircle, Lightbulb, Wrench, XCircle } from '@phosphor-icons/react'
import { useState } from 'react'
import type { Challenge, ChallengeOutcome } from '../../api/types'

type AnyChallenge = Pick<Challenge, 'id' | 'title' | 'brief' | 'hint' | 'explanation'> & { locked_params: readonly string[] }

interface Props<C extends AnyChallenge, O extends ChallengeOutcome> {
  challenges: C[]
  active: C | null
  solved: string[]
  /** Runs the server-side check for the active challenge with the learner's current settings. */
  onCheck: (c: C) => Promise<O>
  onStart: (c: C) => void
  onExit: () => void
  onSolved: (id: string, check: O) => void
  intro?: string
}

/** Break & fix list and runner. Lesson-agnostic: the caller supplies the server check. */
export function Challenges<C extends AnyChallenge, O extends ChallengeOutcome>({ challenges, active, solved, onCheck, onStart, onExit, onSolved, intro }: Props<C, O>) {
  const [check, setCheck] = useState<O | null>(null)
  const [state, setState] = useState<'idle' | 'loading' | 'error'>('idle')
  const [showHint, setShowHint] = useState(false)

  if (!active) {
    return (
      <div className="challenges">
        <p>{intro ?? 'Each pipeline below is broken in one specific way. Find the cause in the experiment, then fix it with the controls left unlocked.'}</p>
        <ol className="challenge-list">
          {challenges.map((c) => (
            <li key={c.id}>
              <button
                type="button"
                className="challenge-card"
                onClick={() => {
                  setCheck(null)
                  setShowHint(false)
                  onStart(c)
                }}
              >
                <span className="challenge-card__title">{c.title}</span>
                <span className="label">
                  {solved.includes(c.id) ? (
                    <>
                      <CheckCircle weight="fill" aria-hidden /> SOLVED
                    </>
                  ) : (
                    <>
                      <Wrench weight="bold" aria-hidden /> BROKEN
                    </>
                  )}
                </span>
              </button>
            </li>
          ))}
        </ol>
      </div>
    )
  }

  const run = async () => {
    setState('loading')
    try {
      const out = await onCheck(active)
      setCheck(out)
      setState('idle')
      if (out.passed) onSolved(active.id, out)
    } catch {
      setState('error')
    }
  }

  return (
    <div className="challenges">
      <button type="button" className="btn" onClick={onExit}>
        ← All challenges
      </button>
      <h3 className="challenges__title">{active.title}</h3>
      <p>{active.brief}</p>
      <p className="label">LOCKED · {active.locked_params.join(' · ').replaceAll('_', ' ')}</p>
      <div className="challenges__actions">
        <button type="button" className="btn btn--primary" onClick={run} data-state={state === 'loading' ? 'loading' : undefined} disabled={state === 'loading'}>
          {state === 'loading' ? 'Checking…' : 'Check my fix'}
        </button>
        <button type="button" className="btn" aria-expanded={showHint} onClick={() => setShowHint((s) => !s)}>
          <Lightbulb aria-hidden /> {showHint ? 'Hide hint' : 'Hint'}
        </button>
      </div>
      {showHint && <p className="notice">{active.hint}</p>}
      {state === 'error' && (
        <p className="notice notice--error" role="alert">
          The check could not run. Is the backend up?
        </p>
      )}
      {check && (
        <div className={`check ${check.passed ? 'check--pass' : 'check--fail'}`} role="status" aria-live="polite">
          <p className="check__verdict">
            {check.passed ? <CheckCircle weight="fill" aria-hidden /> : <XCircle weight="fill" aria-hidden />}
            {check.passed ? 'Fixed.' : 'Still broken.'}
          </p>
          <ul>
            {check.checks.map((c, i) => (
              <li key={i} className={c.passed ? 'is-pass' : 'is-fail'}>
                {c.passed ? '✓' : '✗'} {c.message}
              </li>
            ))}
          </ul>
          {check.passed && <p>{active.explanation}</p>}
        </div>
      )}
    </div>
  )
}

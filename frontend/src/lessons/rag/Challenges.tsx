import { CheckCircle, Lightbulb, Wrench, XCircle } from '@phosphor-icons/react'
import { useState } from 'react'
import { api } from '../../api/client'
import type { Challenge, ChallengeCheck, Lesson, RagParams } from '../../api/types'

interface Props {
  lesson: Lesson
  active: Challenge | null
  solved: string[]
  params: RagParams
  onStart: (c: Challenge) => void
  onExit: () => void
  onSolved: (id: string, check: ChallengeCheck) => void
}

export function Challenges({ lesson, active, solved, params, onStart, onExit, onSolved }: Props) {
  const [check, setCheck] = useState<ChallengeCheck | null>(null)
  const [state, setState] = useState<'idle' | 'loading' | 'error'>('idle')
  const [showHint, setShowHint] = useState(false)

  if (!active) {
    return (
      <div className="challenges">
        <p>Each pipeline below is broken in one specific way. Find the cause in the experiment, then fix it with the controls left unlocked.</p>
        <ol className="challenge-list">
          {lesson.challenges.map((c) => (
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
      const out = await api.checkChallenge(lesson.id, active.id, params)
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

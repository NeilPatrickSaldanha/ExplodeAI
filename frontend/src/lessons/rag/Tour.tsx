import { ArrowLeft, ArrowRight } from '@phosphor-icons/react'
import type { Lesson, Source } from '../../api/types'
import { ClaimCard } from './Inspector'

interface Props {
  lesson: Lesson
  step: number
  onStep: (i: number) => void
  sources: Map<string, Source>
}

export function Tour({ lesson, step, onStep, sources }: Props) {
  const s = lesson.tour[step]
  const claims = s.claims.map((id) => lesson.claims.find((c) => c.id === id)!).filter(Boolean)
  return (
    <div className="tour">
      <p className="label">
        STEP {step + 1} OF {lesson.tour.length}
      </p>
      <progress className="tour__progress" max={lesson.tour.length} value={step + 1} aria-label="Tour progress" />
      <h2 className="tour__title">{s.title}</h2>
      <p>{s.body}</p>
      <ul className="claims">
        {claims.map((c) => (
          <ClaimCard key={c.id} claim={c} sources={sources} />
        ))}
      </ul>
      <div className="tour__nav">
        <button type="button" className="btn" disabled={step === 0} onClick={() => onStep(step - 1)}>
          <ArrowLeft aria-hidden /> Back
        </button>
        <button type="button" className="btn btn--primary" disabled={step === lesson.tour.length - 1} onClick={() => onStep(step + 1)}>
          Next <ArrowRight aria-hidden />
        </button>
      </div>
    </div>
  )
}

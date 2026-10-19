import { CheckCircle, XCircle } from '@phosphor-icons/react'
import type { AblationOutcome } from '../../api/types'

/** One side of the RAG "what breaks if removed?" comparison. */
export function ragOutcome(o: AblationOutcome) {
  return (
    <>
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
    </>
  )
}

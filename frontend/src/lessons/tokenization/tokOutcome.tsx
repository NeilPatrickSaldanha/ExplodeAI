import { CheckCircle, XCircle } from '@phosphor-icons/react'
import type { TokenizeAblationOutcome } from '../../api/types'
import { Chips } from './TokStageIO'

/** One side of the tokenization "what breaks if removed?" comparison. */
export function tokOutcome(o: TokenizeAblationOutcome) {
  return (
    <>
      <dl className="outcome__stats">
        <div><dt>Tokens</dt><dd>{o.tokens ?? '—'}</dd></div>
        <div><dt>Merges</dt><dd>{o.merges}</dd></div>
        <div><dt>Unknown</dt><dd>{o.unk_count}</dd></div>
      </dl>
      {o.preview.length > 0 && <Chips items={o.preview} max={12} label="First tokens" />}
      <p className="outcome__answer">
        {o.round_trip ? <CheckCircle weight="fill" aria-hidden className="is-pass" /> : <XCircle weight="fill" aria-hidden className="is-fail" />}
        <span>{o.decoded === null ? 'Not decoded: no text comes back.' : o.round_trip ? 'Round trip exact.' : `Decodes to “${o.decoded}”`}</span>
      </p>
      {o.notes.length > 0 && <p className="outcome__notes">{o.notes.join(' · ')}</p>}
    </>
  )
}

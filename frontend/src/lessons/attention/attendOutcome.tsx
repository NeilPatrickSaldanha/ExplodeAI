import type { AttendAblationOutcome } from '../../api/types'

/** One side of the attention "what breaks if removed?" comparison. */
export function attendOutcome(o: AttendAblationOutcome) {
  const pct = (v: number | null) => (v === null ? '—' : `${Math.round(v * 100)}%`)
  return (
    <>
      <dl className="outcome__stats">
        <div><dt>Weights</dt><dd>{o.has_weights ? 'yes' : 'none'}</dd></div>
        <div><dt>Output</dt><dd>{o.output_shape ?? 'none'}</dd></div>
        <div>
          <dt>Row sums</dt>
          <dd>{o.row_sum_min === null ? '—' : o.row_sum_min === o.row_sum_max ? o.row_sum_min.toFixed(2) : `${o.row_sum_min.toFixed(1)} … ${o.row_sum_max?.toFixed(1)}`}</dd>
        </div>
        <div><dt>Looks at later words</dt><dd>{pct(o.future_mass)}</dd></div>
        <div><dt>Looks at itself</dt><dd>{pct(o.self_weight)}</dd></div>
        <div><dt>Order matters</dt><dd>{o.order_gap === null ? '—' : o.order_gap > 0.05 ? 'yes' : 'no'}</dd></div>
      </dl>
      {o.has_negative && <p className="outcome__answer">Some weights are negative.</p>}
      {o.notes.length > 0 && <p className="outcome__notes">{o.notes.join(' · ')}</p>}
    </>
  )
}

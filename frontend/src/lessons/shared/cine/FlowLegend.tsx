import type { FlowKind } from '../../../engine/types'

const DASH: Record<FlowKind, string | undefined> = { document: undefined, vector: '6 4', query: '2 4' }

export type FlowLabels = Record<FlowKind, string>

/** Legend for the three flow kinds. Line style differs as well as colour; labels are per lesson. */
export function FlowLegend({ labels }: { labels: FlowLabels }) {
  return (
    <ul className="flow-legend" aria-label="Flow legend">
      {(Object.keys(DASH) as FlowKind[]).map((kind) => (
        <li key={kind} className={`flow-legend__item flow-legend__item--${kind}`}>
          <svg width="28" height="8" aria-hidden="true">
            <line x1="1" y1="4" x2="27" y2="4" strokeDasharray={DASH[kind]} />
          </svg>
          {labels[kind]}
        </li>
      ))}
    </ul>
  )
}

/** Legend for the three flow kinds. Line style differs as well as colour. */
const ITEMS = [
  { kind: 'document', label: 'Text flow', dash: undefined },
  { kind: 'vector', label: 'Vector flow', dash: '6 4' },
  { kind: 'query', label: 'Your question', dash: '2 4' },
] as const

export function FlowLegend() {
  return (
    <ul className="flow-legend" aria-label="Flow legend">
      {ITEMS.map((i) => (
        <li key={i.kind} className={`flow-legend__item flow-legend__item--${i.kind}`}>
          <svg width="28" height="8" aria-hidden="true">
            <line x1="1" y1="4" x2="27" y2="4" strokeDasharray={i.dash} />
          </svg>
          {i.label}
        </li>
      ))}
    </ul>
  )
}

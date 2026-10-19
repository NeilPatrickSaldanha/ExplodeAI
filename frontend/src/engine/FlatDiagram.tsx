import { linkKey, type AssemblySpec, type Readouts, type ViewState } from './types'
import { neighbours, topDown } from './math'

interface Props {
  spec: AssemblySpec
  view: ViewState
  readouts?: Readouts
  onSelect: (id: string | null) => void
  title: string
}

const W = 960
const H = 420
const BOX_W = 132
const BOX_H = 58

/**
 * 2D fallback: same spec, top-down. Used when WebGL is unavailable, on request,
 * and as a lighter view on small screens. Every part is a real <button>-like
 * focusable element, so it is fully keyboard-operable.
 */
export function FlatDiagram({ spec, view, readouts, onSelect, title }: Props) {
  const pos = topDown(spec, Math.max(view.explode, 0.6), W, H, 80)
  const active = view.isolate && view.selectedId ? new Set([view.selectedId, ...neighbours(spec, view.selectedId)]) : null

  return (
    <svg className="flat-diagram" viewBox={`0 0 ${W} ${H}`} role="group" aria-label={title}>
      <defs>
        <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
          <path d="M 0 0 L 10 5 L 0 10 z" className="flat-diagram__arrowhead" />
        </marker>
      </defs>
      {spec.links.map((l) => {
        const a = pos[l.source]
        const b = pos[l.target]
        const dim = active && !(active.has(l.source) && active.has(l.target))
        const dx = b.x - a.x
        const dy = b.y - a.y
        const len = Math.hypot(dx, dy) || 1
        const ux = dx / len
        const uy = dy / len
        const off = Math.abs(ux) * (BOX_W / 2) + Math.abs(uy) * (BOX_H / 2) + 6
        const readout = readouts?.links?.[linkKey(l)]
        return (
          <g key={linkKey(l)} className={dim ? 'is-dim' : undefined}>
            <line
              x1={a.x + ux * off}
              y1={a.y + uy * off}
              x2={b.x - ux * off}
              y2={b.y - uy * off}
              className={`flat-diagram__link flat-diagram__link--${l.kind ?? "document"}`}
              markerEnd="url(#arrow)"
            />
            <text x={(a.x + b.x) / 2} y={(a.y + b.y) / 2 - 8} className="flat-diagram__link-label" textAnchor="middle">
              {l.label}
              {readout ? ` · ${readout}` : ''}
            </text>
          </g>
        )
      })}
      {spec.parts.map((p) => {
        const { x, y } = pos[p.id]
        const selected = view.selectedId === p.id
        const dim = active && !active.has(p.id)
        return (
          <g
            key={p.id}
            transform={`translate(${x - BOX_W / 2} ${y - BOX_H / 2})`}
            className={`flat-diagram__part${selected ? ' is-selected' : ''}${dim ? ' is-dim' : ''}${p.prop ? ' is-prop' : ''}`}
            {...(p.prop
              ? { role: 'img' }
              : { role: 'button', tabIndex: 0 })}
            aria-pressed={p.prop ? undefined : selected}
            aria-label={`${p.label}, ${p.group} stage${readouts?.parts?.[p.id] ? `, ${readouts.parts[p.id]}` : ''}`}
            onClick={p.prop ? undefined : () => onSelect(selected ? null : p.id)}
            onKeyDown={p.prop ? undefined : (e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault()
                onSelect(selected ? null : p.id)
              }
            }}
          >
            <rect width={BOX_W} height={BOX_H} rx={8} />
            <text x={12} y={24} className="flat-diagram__name">
              {p.label}
            </text>
            <text x={12} y={44} className="flat-diagram__meta">
              {readouts?.parts?.[p.id] ?? p.group.toUpperCase()}
            </text>
          </g>
        )
      })}
    </svg>
  )
}

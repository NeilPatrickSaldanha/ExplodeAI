import { useEffect, useRef, useState } from 'react'
import { flatLayout } from './flatLayout'
import { neighbours } from './math'
import { type AssemblySpec, type Readouts, type ViewState } from './types'

interface Props {
  spec: AssemblySpec
  view: ViewState
  readouts?: Readouts
  onSelect: (id: string | null) => void
  title: string
}

const fit = (text: string, chars: number) => (text.length <= chars ? text : `${text.slice(0, Math.max(1, chars - 1)).trimEnd()}…`)

/** Up to two lines, broken at spaces; the last line is shortened with an ellipsis if it still does not fit. */
function wrap(text: string, chars: number): string[] {
  if (text.length <= chars) return [text]
  const words = text.split(' ')
  let first = ''
  let i = 0
  while (i < words.length && (first ? `${first} ${words[i]}` : words[i]).length <= chars) first = first ? `${first} ${words[i++]}` : words[i++]
  if (!first) return [fit(text, chars)]
  return [first, fit(words.slice(i).join(' '), chars)]
}

function useSize(ref: React.RefObject<HTMLElement | null>): [number, number] {
  const [size, setSize] = useState<[number, number]>([960, 420])
  useEffect(() => {
    const el = ref.current
    if (!el || typeof ResizeObserver === 'undefined') return
    const read = () => {
      const r = el.getBoundingClientRect()
      if (r.width > 0 && r.height > 0) setSize([Math.round(r.width), Math.round(r.height)])
    }
    read()
    const ro = new ResizeObserver(read)
    ro.observe(el)
    return () => ro.disconnect()
  }, [ref])
  return size
}

/**
 * 2D diagram: the same spec as the 3D view, laid out for the real container size. Nodes never overlap,
 * every link label sits in a pill with a background (so it stays readable over lines), and the look is
 * identical for every lesson. Parts are focusable buttons, so it is fully keyboard-operable.
 */
export function FlatDiagram({ spec, view, readouts, onSelect, title }: Props) {
  const host = useRef<HTMLDivElement>(null)
  const [cw, ch] = useSize(host)
  const L = flatLayout(spec, cw, ch, readouts)
  const active = view.isolate && view.selectedId ? new Set([view.selectedId, ...neighbours(spec, view.selectedId)]) : null
  // Narrow boxes (phones) fold the number into the name instead of spending room on a badge.
  const narrow = L.boxW < 132
  const nameChars = Math.floor((L.boxW - (narrow ? 24 : 54)) / 7.4)
  const metaChars = Math.floor((L.boxW - 20) / 6.9)

  return (
    <div className="flat-diagram-wrap" ref={host}>
      <svg className="flat-diagram" width={L.width} height={L.height} viewBox={`0 0 ${L.width} ${L.height}`} role="group" aria-label={title}>
        <defs>
          {(['document', 'vector', 'query'] as const).map((k) => (
            <marker key={k} id={`flat-arrow-${k}`} viewBox="0 0 10 10" refX="8" refY="5" markerWidth="8" markerHeight="8" orient="auto">
              <path d="M 0 0 L 10 5 L 0 10 z" className={`flat-diagram__arrowhead flat-diagram__arrowhead--${k}`} />
            </marker>
          ))}
        </defs>
        {/* Lines first, then nodes, then label pills, so a label is never hidden by a line or a node. */}
        {L.links.map((l) => {
          const dim = active && !(active.has(l.source) && active.has(l.target))
          const focus = view.selectedId && (l.source === view.selectedId || l.target === view.selectedId)
          return (
            <line
              key={l.key}
              x1={l.x1}
              y1={l.y1}
              x2={l.x2}
              y2={l.y2}
              className={`flat-diagram__link flat-diagram__link--${l.kind}${dim ? ' is-dim' : ''}${focus ? ' is-focus' : ''}`}
              markerEnd={`url(#flat-arrow-${l.kind})`}
            />
          )
        })}
        {spec.parts.map((p, i) => {
          const { x, y } = L.pos[p.id]
          const selected = view.selectedId === p.id
          const dim = active && !active.has(p.id)
          const meta = readouts?.parts?.[p.id] ?? p.group.toUpperCase()
          const num = p.number ?? String(i + 1).padStart(2, '0')
          return (
            <g
              key={p.id}
              transform={`translate(${x - L.boxW / 2} ${y - L.boxH / 2})`}
              className={`flat-diagram__part${selected ? ' is-selected' : ''}${dim ? ' is-dim' : ''}${p.prop ? ' is-prop' : ''}`}
              {...(p.prop ? { role: 'img' } : { role: 'button', tabIndex: 0 })}
              aria-pressed={p.prop ? undefined : selected}
              aria-label={`${p.label}, ${p.group} stage${readouts?.parts?.[p.id] ? `, ${readouts.parts[p.id]}` : ''}`}
              onClick={p.prop ? undefined : () => onSelect(selected ? null : p.id)}
              onKeyDown={
                p.prop
                  ? undefined
                  : (e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault()
                        onSelect(selected ? null : p.id)
                      }
                    }
              }
            >
              <title>{`${p.label}${meta ? ` · ${meta}` : ''}`}</title>
              <rect width={L.boxW} height={L.boxH} rx={10} />
              {!p.prop && !narrow && (
                <>
                  <rect className="flat-diagram__badge" x={10} y={12} width={26} height={18} rx={4} />
                  <text className="flat-diagram__num" x={23} y={25} textAnchor="middle">
                    {num}
                  </text>
                </>
              )}
              {(() => {
                const text = narrow && !p.prop ? `${num} ${p.label}` : p.label
                const lines = wrap(text, p.prop ? nameChars + 4 : nameChars)
                return lines.map((line, k) => (
                  <text key={k} x={p.prop || narrow ? 12 : 44} y={(lines.length > 1 ? 23 : 28) + k * 16} className="flat-diagram__name">
                    {line}
                  </text>
                ))
              })()}
              <text x={12} y={58} className="flat-diagram__meta">
                {fit(meta, metaChars)}
              </text>
            </g>
          )
        })}
        {L.links.map((l) => {
          const dim = active && !(active.has(l.source) && active.has(l.target))
          const { pill } = l
          return (
            <g key={`${l.key}-label`} className={dim ? 'is-dim' : undefined}>
              {l.detached && <line className="flat-diagram__leader" x1={pill.cx} y1={pill.cy} x2={l.mx} y2={l.my} />}
              <g className={`flat-diagram__pill flat-diagram__pill--${l.kind}`} transform={`translate(${pill.cx - pill.w / 2} ${pill.cy - pill.h / 2})`}>
              <rect width={pill.w} height={pill.h} rx={7} />
              <rect className="flat-diagram__pill-bar" width={3} height={pill.h - 8} x={4} y={4} rx={1.5} />
              {pill.lines.map((line, i) => (
                <text key={i} x={pill.w / 2 + 1} y={14 + i * 15} textAnchor="middle" className={i === 0 && pill.lines.length > 1 ? 'flat-diagram__pill-label' : 'flat-diagram__pill-text'}>
                  {line}
                </text>
              ))}
              </g>
            </g>
          )
        })}
      </svg>
    </div>
  )
}

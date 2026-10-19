import { CheckCircle } from '@phosphor-icons/react'
import { useRef, type KeyboardEvent } from 'react'
import type { Component } from '../../../api/types'
import { StageIcon } from './StageIcon'

interface Props {
  stages: Component[]
  activeId: string | null
  explored: string[]
  onSelect: (id: string) => void
}

/**
 * The 8-stage progression bar. Every stage is a real button; ←/→ move between
 * stages (and select them), Home/End jump to the ends.
 */
export function StageBar({ stages, activeId, explored, onSelect }: Props) {
  const refs = useRef<(HTMLButtonElement | null)[]>([])
  const onKeyDown = (e: KeyboardEvent, i: number) => {
    const to = e.key === 'ArrowRight' ? i + 1 : e.key === 'ArrowLeft' ? i - 1 : e.key === 'Home' ? 0 : e.key === 'End' ? stages.length - 1 : null
    if (to === null || to < 0 || to >= stages.length) return
    e.preventDefault()
    refs.current[to]?.focus()
    onSelect(stages[to].id)
  }
  return (
    <nav className="stagebar" aria-label="Pipeline stages">
      <ol>
        {stages.map((s, i) => {
          const active = s.id === activeId
          return (
            <li key={s.id}>
              <button
                ref={(el) => {
                  refs.current[i] = el
                }}
                type="button"
                className={`stagebar__btn${active ? ' is-active' : ''}`}
                aria-current={active ? 'step' : undefined}
                onClick={() => onSelect(s.id)}
                onKeyDown={(e) => onKeyDown(e, i)}
              >
                <StageIcon name={s.icon} className="stagebar__icon" weight={active ? 'fill' : 'regular'} />
                <span className="stagebar__text">
                  <span className="stagebar__num">{String(i + 1).padStart(2, '0')}</span>
                  <span className="stagebar__name">{s.label}</span>
                  {s.subtitle && <span className="stagebar__sub">{s.subtitle}</span>}
                </span>
                {explored.includes(s.id) && <CheckCircle className="stagebar__seen" weight="fill" aria-label="explored" />}
              </button>
            </li>
          )
        })}
      </ol>
    </nav>
  )
}

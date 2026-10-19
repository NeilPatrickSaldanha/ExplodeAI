import { ArrowDown, ArrowUp, CheckCircle, DotsSixVertical, XCircle } from '@phosphor-icons/react'
import { useMemo, useState } from 'react'
import { api } from '../../api/client'
import type { Lesson, ReconstructionResult } from '../../api/types'
import { moveItem, scrambled } from './rebuildOrder'

interface Props {
  lesson: Lesson
  solved: boolean
  onSolved: () => void
}

export function Rebuild({ lesson, solved, onSolved }: Props) {
  const label = useMemo(() => new Map(lesson.components.map((c) => [c.id, c.label])), [lesson])
  const [order, setOrder] = useState(() => scrambled(lesson.components.map((c) => c.id), lesson.reconstruction.dependencies))
  const [dragging, setDragging] = useState<number | null>(null)
  const [result, setResult] = useState<ReconstructionResult | null>(null)
  const [announce, setAnnounce] = useState('')

  const move = (from: number, to: number) => {
    const next = moveItem(order, from, to)
    if (next !== order) {
      setOrder(next)
      setResult(null)
      setAnnounce(`${label.get(order[from])} moved to position ${to + 1} of ${order.length}.`)
    }
  }

  const check = async () => {
    try {
      const r = await api.checkReconstruction(lesson.id, order)
      setResult(r)
      if (r.correct) onSolved()
    } catch {
      setResult({ correct: false, violations: [], message: 'The check could not run. Is the backend up?' })
    }
  }

  const bad = new Set(result?.violations.map((v) => v.stage))

  return (
    <div className="rebuild">
      <p>{lesson.reconstruction.prompt} More than one order can be correct.</p>
      <ol className="rebuild__list" aria-label="Pipeline stages in run order">
        {order.map((id, i) => (
          <li
            key={id}
            className={`rebuild__item${dragging === i ? ' is-dragging' : ''}${bad.has(id) ? ' is-bad' : ''}`}
            draggable
            onDragStart={(e) => {
              setDragging(i)
              e.dataTransfer.effectAllowed = 'move'
              e.dataTransfer.setData('text/plain', String(i))
            }}
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => {
              e.preventDefault()
              const from = Number(e.dataTransfer.getData('text/plain'))
              move(from, i)
              setDragging(null)
            }}
            onDragEnd={() => setDragging(null)}
          >
            <DotsSixVertical aria-hidden className="rebuild__grip" />
            <span className="rebuild__pos label">{String(i + 1).padStart(2, '0')}</span>
            <span className="rebuild__name">{label.get(id)}</span>
            {bad.has(id) && (
              <span className="rebuild__why">
                needs {result!.violations.filter((v) => v.stage === id).map((v) => label.get(v.needs)).join(', ')} first
              </span>
            )}
            <span className="rebuild__btns">
              <button type="button" className="btn btn--icon" aria-label={`Move ${label.get(id)} up`} disabled={i === 0} onClick={() => move(i, i - 1)}>
                <ArrowUp aria-hidden />
              </button>
              <button type="button" className="btn btn--icon" aria-label={`Move ${label.get(id)} down`} disabled={i === order.length - 1} onClick={() => move(i, i + 1)}>
                <ArrowDown aria-hidden />
              </button>
            </span>
          </li>
        ))}
      </ol>
      <p className="visually-hidden" aria-live="polite">
        {announce}
      </p>
      <button type="button" className="btn btn--primary" onClick={check}>
        Check order
      </button>
      {(result || solved) && (
        <p className={`check ${result?.correct || (!result && solved) ? 'check--pass' : 'check--fail'}`} role="status">
          {result?.correct || (!result && solved) ? <CheckCircle weight="fill" aria-hidden /> : <XCircle weight="fill" aria-hidden />}{' '}
          {result ? result.message : 'You have rebuilt this pipeline before.'}
        </p>
      )}
    </div>
  )
}

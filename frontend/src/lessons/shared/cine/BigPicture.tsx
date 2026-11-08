import { Compass } from '@phosphor-icons/react'
import { useEffect, useRef, useState } from 'react'
import type { Lesson } from '../../../api/types'

/**
 * The whole lesson in plain words, before any part is opened: a short story, one analogy with every
 * stage mapped to its stand-in (and where the analogy stops being true), and the one example the
 * stages follow. A slim bar that opens as a floating panel over the page, so it never pushes the diagram or the
 * stage panel down. Always starts closed; Escape, the bar or choosing a stage closes it.
 */
export function BigPicture({ lesson, onGoTo }: { lesson: Lesson; onGoTo: (id: string) => void }) {
  const bp = lesson.big_picture
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDetailsElement>(null)
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      // close the element itself: its toggle event updates `open`, so a key press that lands before React has caught up still works
      if (e.key === 'Escape' && ref.current?.open) ref.current.open = false
    }
    window.addEventListener('keydown', onKey, true)
    return () => window.removeEventListener('keydown', onKey, true)
  }, [])
  if (!bp) return null
  const idOf = (label: string) => lesson.components.find((c) => c.label === label)?.id

  return (
    <details
      ref={ref}
      className="bigpic"
      open={open}
      onToggle={(e) => setOpen((e.currentTarget as HTMLDetailsElement).open)}
    >
      <summary className="bigpic__summary">
        <Compass weight="duotone" aria-hidden />
        <span>The big picture</span>
        <span className="label bigpic__hint">{open ? 'HIDE' : 'OPEN THE STORY, THE ANALOGY AND THE EXAMPLE'}</span>
      </summary>
      <div className="bigpic__body">
        <div className="bigpic__col">
          <h3>What is going on?</h3>
          <p className="bigpic__story">{bp.story}</p>
          <div className="bigpic__example">
            <span className="label">{bp.example.title.toUpperCase()}</span>
            <q>{bp.example.input}</q>
            <p>{bp.example.note}</p>
          </div>
        </div>
        <div className="bigpic__col">
          <h3>Think of it like: {bp.analogy.title}</h3>
          <ul className="bigpic__map" aria-label="Each stage and what it is in the analogy">
            {bp.analogy.mapping.map((m) => (
              <li key={m.part}>
                <button type="button" className="chip" onClick={() => {
                    const id = idOf(m.part)
                    if (!id) return
                    setOpen(false)
                    onGoTo(id)
                  }}>
                  {m.part}
                </button>
                <span aria-hidden>=</span>
                <span>{m.becomes}</span>
              </li>
            ))}
          </ul>
          <p className="bigpic__breaks">
            <span className="label">WHERE THE ANALOGY STOPS BEING TRUE</span>
            {bp.analogy.breaks}
          </p>
        </div>
      </div>
    </details>
  )
}

import { Compass } from '@phosphor-icons/react'
import { useState } from 'react'
import type { Lesson } from '../../../api/types'

const key = (lessonId: string) => `explodeai.bigpicture.${lessonId}`
const read = (lessonId: string) => {
  try {
    return localStorage.getItem(key(lessonId)) !== 'closed'
  } catch {
    return true
  }
}

/**
 * The whole lesson in plain words, before any part is opened: a short story, one analogy with every
 * stage mapped to its stand-in (and where the analogy stops being true), and the one example the
 * stages follow. Open on a first visit, remembered once the learner closes it.
 */
export function BigPicture({ lesson, onGoTo }: { lesson: Lesson; onGoTo: (id: string) => void }) {
  const bp = lesson.big_picture
  const [open, setOpen] = useState(() => read(lesson.id))
  if (!bp) return null
  const idOf = (label: string) => lesson.components.find((c) => c.label === label)?.id

  return (
    <details
      className="bigpic"
      open={open}
      onToggle={(e) => {
        const now = (e.currentTarget as HTMLDetailsElement).open
        setOpen(now)
        try {
          localStorage.setItem(key(lesson.id), now ? 'open' : 'closed')
        } catch {
          /* storage unavailable */
        }
      }}
    >
      <summary className="bigpic__summary">
        <Compass weight="duotone" aria-hidden />
        <span>The big picture</span>
        <span className="label bigpic__hint">{open ? 'HIDE' : 'SHOW THE STORY, THE ANALOGY AND THE EXAMPLE'}</span>
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
                <button type="button" className="chip" onClick={() => idOf(m.part) && onGoTo(idOf(m.part)!)}>
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

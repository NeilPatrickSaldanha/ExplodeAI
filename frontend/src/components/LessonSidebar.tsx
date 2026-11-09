import { CheckCircle } from '@phosphor-icons/react'
import { useEffect, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { api } from '../api/client'
import type { LessonSummary } from '../api/types'
import { useVoice } from '../voiceContext'

/** Short names for the side list; falls back to the lesson's own title. */
const SHORT: Record<string, string> = {
  'rag-pipeline': 'RAG',
  tokenization: 'Tokenization',
  embeddings: 'Embeddings',
  attention: 'Attention',
  agents: 'Agents',
}

/**
 * The course at a glance, always on screen on wide displays: every lesson in order, the one you are in
 * highlighted, and a check once you have explored every stage of it. Hidden on narrower screens, where
 * the "Lessons" link in the header does the job.
 */
export function LessonSidebar() {
  const { pathname } = useLocation()
  const { voice } = useVoice()
  const [lessons, setLessons] = useState<LessonSummary[]>([])
  const [done, setDone] = useState<Record<string, boolean>>({})

  useEffect(() => {
    api.lessons(voice).then(setLessons).catch(() => undefined)
  }, [voice])

  // Re-read progress when you move between pages, so a check appears after you finish a lesson.
  useEffect(() => {
    if (lessons.length === 0) return
    let live = true
    Promise.all(
      lessons.map((l) =>
        api
          .progress(l.id)
          .then((p) => [l.id, p.explored_components.length >= l.component_count] as const)
          .catch(() => [l.id, false] as const),
      ),
    ).then((rows) => live && setDone(Object.fromEntries(rows)))
    return () => {
      live = false
    }
  }, [lessons, pathname])

  if (lessons.length === 0) return null
  return (
    <aside className="side" aria-label="Course navigation">
      <p className="label side__group">AI fundamentals</p>
      <ol className="side__list">
        {lessons.map((l, i) => {
          const active = pathname === `/lessons/${l.id}`
          return (
            <li key={l.id}>
              <Link
                to={`/lessons/${l.id}`}
                className={`side__item${active ? ' is-active' : ''}`}
                aria-current={active ? 'page' : undefined}
                aria-label={`Open lesson ${i + 1}: ${SHORT[l.id] ?? l.title}${done[l.id] ? ', all stages explored' : ''}`}
              >
                <span className="side__num" aria-hidden>
                  {String(i + 1).padStart(2, '0')}
                </span>
                <span className="side__name" aria-hidden>
                  {SHORT[l.id] ?? l.title}
                </span>
                {done[l.id] && <CheckCircle weight="fill" className="side__done" aria-hidden />}
              </Link>
            </li>
          )
        })}
      </ol>
      <p className="side__note">Each lesson takes about {Math.round(lessons.reduce((s, l) => s + l.estimated_minutes, 0) / lessons.length)} minutes.</p>
    </aside>
  )
}

import { Moon, Sun } from '@phosphor-icons/react'
import { useEffect, useState } from 'react'
import { BrowserRouter, Link, Route, Routes, useParams } from 'react-router-dom'
import { api } from './api/client'
import type { Lesson, LessonSummary } from './api/types'
import { RagLessonPage } from './lessons/rag/RagLessonPage'

type Theme = 'light' | 'dark' | null
const THEME_KEY = 'explodeai.theme'

function useTheme(): [Theme, (t: Theme) => void] {
  const [theme, setTheme] = useState<Theme>(() => {
    try {
      return (localStorage.getItem(THEME_KEY) as Theme) || null
    } catch {
      return null
    }
  })
  useEffect(() => {
    const root = document.documentElement
    if (theme) root.dataset.theme = theme
    else delete root.dataset.theme
    try {
      if (theme) localStorage.setItem(THEME_KEY, theme)
      else localStorage.removeItem(THEME_KEY)
    } catch {
      /* storage unavailable */
    }
  }, [theme])
  return [theme, setTheme]
}

function Shell({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useTheme()
  const isLight = theme === 'light' || (theme === null && window.matchMedia?.('(prefers-color-scheme: light)').matches)
  return (
    <>
      <a href="#main" className="skip-link">
        Skip to content
      </a>
      {/* N9 edge-aligned minimal: wordmark hard-left, one utility hard-right. */}
      <header className="nav">
        <Link to="/" className="nav__wordmark">
          explode<span>ai</span>
        </Link>
        <div className="nav__right">
          <Link to="/" className="nav__link">
            Lessons
          </Link>
          <button type="button" className="btn btn--icon" aria-label={isLight ? 'Switch to dark theme' : 'Switch to light theme'} onClick={() => setTheme(isLight ? 'dark' : 'light')}>
            {isLight ? <Moon aria-hidden /> : <Sun aria-hidden />}
          </button>
        </div>
      </header>
      <main id="main" tabIndex={-1}>
        {children}
      </main>
      {/* Ft2 inline single line */}
      <footer className="foot">
        <span>explodeai · every claim cited, every experiment real, every simulation labelled.</span>
      </footer>
    </>
  )
}

function Home() {
  const [lessons, setLessons] = useState<LessonSummary[] | null>(null)
  const [error, setError] = useState(false)
  useEffect(() => {
    api.lessons().then(setLessons).catch(() => setError(true))
  }, [])
  return (
    <section className="home">
      <p className="label">AI ENGINEERING, TAKEN APART</p>
      <h1>
        learn systems by&nbsp;<em>exploding</em>&nbsp;them.
      </h1>
      <p className="home__lede">
        Rotate a system in 3D, pull it apart, isolate a part, run it for real, break it on purpose, then rebuild it.
        Every claim links to its source.
      </p>
      {error && (
        <p className="notice notice--error" role="alert">
          Could not reach the ExplodeAI backend. Start it with <code>make dev</code>.
        </p>
      )}
      {lessons && lessons.length === 0 && (
        <p className="notice">No lessons have passed verification yet. Drafts appear when SHOW_DRAFT_LESSONS=true.</p>
      )}
      <ol className="home__lessons">
        {lessons?.map((l, i) => (
          <li key={l.id}>
            <Link to={`/lessons/${l.id}`} className="lesson-link">
              <span className="label">
                {String(i + 1).padStart(2, '0')} · {l.estimated_minutes} MIN · {l.component_count} PARTS
                {l.status === 'draft' ? ' · DRAFT' : ''}
              </span>
              <span className="lesson-link__title">{l.title}</span>
              <span className="lesson-link__summary">{l.summary}</span>
            </Link>
          </li>
        ))}
      </ol>
    </section>
  )
}

function LessonRoute() {
  const { id = '' } = useParams()
  const [state, setState] = useState<{ id: string; lesson?: Lesson; error?: string } | null>(null)
  useEffect(() => {
    let live = true
    api
      .lesson(id)
      .then((lesson) => live && setState({ id, lesson }))
      .catch((e) => live && setState({ id, error: e.status === 404 ? 'This lesson does not exist or has not been published.' : 'Could not load the lesson.' }))
    return () => {
      live = false
    }
  }, [id])
  const current = state?.id === id ? state : null
  if (current?.error) return <p className="notice notice--error page-pad">{current.error}</p>
  const lesson = current?.lesson
  if (!lesson) return <p className="label page-pad">Loading lesson…</p>
  if (lesson.id === 'rag-pipeline') return <RagLessonPage lesson={lesson} />
  return <p className="notice page-pad">This lesson has no interactive module yet.</p>
}

export default function App() {
  return (
    <BrowserRouter>
      <Shell>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/lessons/:id" element={<LessonRoute />} />
          <Route path="*" element={<p className="notice page-pad">Page not found.</p>} />
        </Routes>
      </Shell>
    </BrowserRouter>
  )
}

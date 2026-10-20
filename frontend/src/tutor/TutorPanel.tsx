import { ChatCircleText, Lock, Question, Sparkle, X } from '@phosphor-icons/react'
import { useCallback, useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { api, ApiError } from '../api/client'
import type { AIStatus, TutorAnswer, TutorCheck, TutorClaim, TutorLlmAnswer, TutorSource } from '../api/types'
import './tutor.css'

const usd = (n: number) => (n < 0.01 ? `$${n.toFixed(5)}` : `$${n.toFixed(2)}`)
const OPEN_KEY = 'explodeai.tutor.open'

type Message =
  | { id: number; role: 'user'; text: string }
  | { id: number; role: 'tutor'; question: string; answer: TutorAnswer }
  | { id: number; role: 'quiz'; check: TutorCheck; revealed: boolean }
  | { id: number; role: 'error'; text: string }

type NewMessage = Message extends infer M ? (M extends { id: number } ? Omit<M, 'id'> : never) : never

interface Props {
  lessonId: string
  lessonNumber: number
  stageId: string | null
  stageLabel: string | null
  onGoToStage: (id: string) => void
}

/**
 * "Ask ExplodeAI": a tutor grounded only in the lessons. Answers quote verified lesson content and
 * show the claims and sources behind every sentence. If the lessons do not cover a question it says
 * so. The optional paid polish is off unless the server enables it, shows its worst-case cost first,
 * and needs a click for every request.
 */
export function TutorPanel({ lessonId, lessonNumber, stageId, stageLabel, onGoToStage }: Props) {
  const [open, setOpen] = useState(() => {
    try {
      return sessionStorage.getItem(OPEN_KEY) === '1'
    } catch {
      return false
    }
  })
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [busy, setBusy] = useState(false)
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [quizN, setQuizN] = useState(0)
  const next = useRef(1)
  const fab = useRef<HTMLButtonElement>(null)
  const field = useRef<HTMLInputElement>(null)
  const log = useRef<HTMLDivElement>(null)

  const setOpenPersist = (v: boolean) => {
    setOpen(v)
    try {
      sessionStorage.setItem(OPEN_KEY, v ? '1' : '0')
    } catch {
      /* storage unavailable */
    }
  }

  useEffect(() => {
    if (!open) return
    let live = true
    api.tutorSuggestions(lessonId, stageId).then((r) => live && setSuggestions(r.suggestions)).catch(() => live && setSuggestions([]))
    return () => {
      live = false
    }
  }, [open, lessonId, stageId])

  useEffect(() => {
    log.current?.scrollTo({ top: log.current.scrollHeight })
  }, [messages])

  const push = useCallback((m: NewMessage) => setMessages((all) => [...all, { ...m, id: next.current++ } as Message]), [])

  const ask = async (q: string) => {
    const question = q.trim()
    if (question.length < 3 || busy) return
    setInput('')
    push({ role: 'user', text: question })
    setBusy(true)
    try {
      const answer = await api.askTutor(question, lessonId, stageId)
      push({ role: 'tutor', question, answer })
    } catch (e) {
      push({ role: 'error', text: e instanceof ApiError ? e.message : 'The tutor could not answer just now.' })
    } finally {
      setBusy(false)
      field.current?.focus()
    }
  }

  const quiz = async () => {
    if (!stageId || busy) return
    setBusy(true)
    try {
      const check = await api.tutorCheck(lessonId, stageId, quizN)
      setQuizN((n) => n + 1)
      push({ role: 'quiz', check, revealed: false })
    } catch (e) {
      push({ role: 'error', text: e instanceof ApiError ? e.message : 'Could not load a question.' })
    } finally {
      setBusy(false)
    }
  }

  const close = () => {
    setOpenPersist(false)
    fab.current?.focus()
  }

  return (
    <>
      <button
        ref={fab}
        type="button"
        className="tutor-fab"
        aria-expanded={open}
        aria-controls="tutor-panel"
        onClick={() => (open ? close() : setOpenPersist(true))}
      >
        <ChatCircleText weight="fill" aria-hidden /> Ask ExplodeAI
      </button>
      {open && (
        <aside
          id="tutor-panel"
          className="tutor"
          aria-label="Ask ExplodeAI"
          onKeyDown={(e) => {
            if (e.key === 'Escape') close()
          }}
        >
          <header className="tutor__head">
            <div>
              <h2 className="tutor__title">Ask ExplodeAI</h2>
              <p className="label" data-testid="tutor-context">
                LESSON {String(lessonNumber).padStart(2, '0')}
                {stageLabel ? ` · ${stageLabel.toUpperCase()}` : ''}
              </p>
            </div>
            <button type="button" className="btn btn--icon" aria-label="Close the tutor" onClick={close}>
              <X aria-hidden />
            </button>
          </header>
          <p className="tutor__promise">Answers come only from ExplodeAI&apos;s verified lessons, with their sources. If the lessons don&apos;t cover it, I&apos;ll say so.</p>

          <div className="tutor__log" ref={log} role="log" aria-live="polite" aria-label="Conversation" tabIndex={0}>
            {messages.length === 0 && <p className="tutor__empty">Ask about anything in the four lessons, or let me quiz you on the stage you are looking at.</p>}
            {messages.map((m) => (
              <MessageView key={m.id} m={m} lessonId={lessonId} stageId={stageId} onGoToStage={onGoToStage} onReveal={() => setMessages((all) => all.map((x) => (x.id === m.id && x.role === 'quiz' ? { ...x, revealed: true } : x)))} onNextQuiz={quiz} onAsk={ask} />
            ))}
            {busy && <p className="label" role="status">THINKING…</p>}
          </div>

          <div className="tutor__chips" role="group" aria-label="Suggested questions">
            <button type="button" className="chip chip--quiz" onClick={quiz} disabled={!stageId || busy} title={stageId ? 'Ask me a question about this stage' : 'Select a stage first'}>
              <Question aria-hidden /> Quiz me on {stageLabel ?? 'a stage'}
            </button>
            {suggestions.map((s) => (
              <button key={s} type="button" className="chip" onClick={() => ask(s)} disabled={busy}>
                {s}
              </button>
            ))}
          </div>
          <form
            className="tutor__form"
            onSubmit={(e) => {
              e.preventDefault()
              ask(input)
            }}
          >
            <label className="visually-hidden" htmlFor="tutor-input">
              Your question
            </label>
            <input id="tutor-input" ref={field} className="input" value={input} maxLength={300} placeholder="Ask a question…" onChange={(e) => setInput(e.target.value)} autoComplete="off" />
            <button type="submit" className="btn btn--primary" disabled={busy || input.trim().length < 3}>
              Ask
            </button>
          </form>
        </aside>
      )}
    </>
  )
}

function MessageView({
  m, lessonId, stageId, onGoToStage, onReveal, onNextQuiz, onAsk,
}: {
  m: Message
  lessonId: string
  stageId: string | null
  onGoToStage: (id: string) => void
  onReveal: () => void
  onNextQuiz: () => void
  onAsk: (q: string) => void
}) {
  if (m.role === 'user') return <p className="tmsg tmsg--user">{m.text}</p>
  if (m.role === 'error') return <p className="notice notice--error tmsg" role="alert">{m.text}</p>
  if (m.role === 'quiz') {
    const c = m.check
    return (
      <div className="tmsg tmsg--quiz">
        <span className="label">QUIZ · {c.stage_label.toUpperCase()} · {c.index + 1} OF {c.total}</span>
        <p className="tmsg__q">{c.question}</p>
        {!m.revealed ? (
          <>
            <p className="tmsg__hint">Hint: {c.hint}</p>
            <button type="button" className="btn" onClick={onReveal}>Show the answer</button>
          </>
        ) : (
          <>
            <p className="tmsg__a">{c.answer}</p>
            <p className="label">FROM THE LESSON · {c.claim_ids.length} VERIFIED CLAIM{c.claim_ids.length === 1 ? '' : 'S'} BEHIND IT</p>
            <button type="button" className="btn" onClick={onNextQuiz}>Next question</button>
          </>
        )}
      </div>
    )
  }
  const a = m.answer
  if (!a.covered) {
    return (
      <div className="tmsg tmsg--tutor tmsg--none">
        <p>{a.message}</p>
        <p className="label">I CAN HELP WITH</p>
        <ul className="tmsg__topics">
          {a.topics.map((t) => (
            <li key={t.lesson_id}>
              <Link to={`/lessons/${t.lesson_id}`}>Lesson {String(t.number).padStart(2, '0')} · {t.title}</Link>
            </li>
          ))}
        </ul>
      </div>
    )
  }
  return (
    <div className="tmsg tmsg--tutor">
      <div className="tmsg__body">
        {a.sentences.map((s) => (
          <p key={s.passage_id + s.text}>
            {s.text}{' '}
            <span className="tmsg__cites" aria-label="Verified claims behind this sentence">
              {s.claim_ids.map((id) => (
                <code key={id} className="tmsg__cite">{id}</code>
              ))}
            </span>
          </p>
        ))}
      </div>
      {a.analogy && (
        <p className="tmsg__analogy">
          <span className="label">ANALOGY · TEACHING AID</span>
          {a.analogy.text}
        </p>
      )}
      <Evidence claims={a.claims} sources={a.sources} />
      {a.related.length > 0 && (
        <div className="tmsg__related" role="group" aria-label="Open the related stage">
          {a.related.map((r) =>
            r.lesson_id === lessonId ? (
              <button key={r.stage_id} type="button" className="chip" onClick={() => onGoToStage(r.stage_id)} aria-current={r.stage_id === stageId ? 'true' : undefined}>
                Show me: {r.stage_label}
              </button>
            ) : (
              <Link key={r.lesson_id + r.stage_id} className="chip" to={`/lessons/${r.lesson_id}`}>
                {r.lesson_title.split(',')[0]} · {r.stage_label}
              </Link>
            ),
          )}
        </div>
      )}
      {a.meta.method === 'bm25' && <p className="label">KEYWORD MATCHING ONLY: THE LOCAL MEANING MODEL IS NOT INSTALLED</p>}
      <Polish question={(m as Extract<Message, { role: 'tutor' }>).question} lessonId={lessonId} stageId={stageId} onAsk={onAsk} />
    </div>
  )
}

function Evidence({ claims, sources }: { claims: TutorClaim[]; sources: TutorSource[] }) {
  return (
    <details className="tmsg__evidence">
      <summary>
        Evidence: {claims.length} verified claim{claims.length === 1 ? '' : 's'}, {sources.length} source{sources.length === 1 ? '' : 's'}
      </summary>
      <ul className="tmsg__claims">
        {claims.map((c) => (
          <li key={c.id}>
            <code>{c.id}</code> {c.text}
          </li>
        ))}
      </ul>
      <ul className="tmsg__sources">
        {sources.map((s) => (
          <li key={s.id}>
            <a href={s.url} target="_blank" rel="noreferrer noopener">
              {s.title}
            </a>{' '}
            <span className="label">{s.publisher}{s.version ? ` · ${s.version}` : ''}</span>
          </li>
        ))}
      </ul>
    </details>
  )
}

/** Optional, paid, per-click: an LLM rewrites the answer from the same lesson passages only. */
function Polish({ question, lessonId, stageId }: { question: string; lessonId: string; stageId: string | null; onAsk: (q: string) => void }) {
  const [status, setStatus] = useState<AIStatus | null>(null)
  const [openIt, setOpenIt] = useState(false)
  const [estimate, setEstimate] = useState<number | null>(null)
  const [out, setOut] = useState<TutorLlmAnswer | null>(null)
  const [state, setState] = useState<'idle' | 'loading'>('idle')
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!openIt) return
    api.aiStatus().then(setStatus).catch(() => setStatus(null))
  }, [openIt])

  const usable = (status?.allowed_models.filter((m) => m.usable) ?? []).sort(
    (a, b) => a.input_usd_per_million_tokens + a.output_usd_per_million_tokens - (b.input_usd_per_million_tokens + b.output_usd_per_million_tokens),
  )
  const model = usable[0]
  const enabled = !!status?.enabled && !!model

  useEffect(() => {
    if (!enabled || !model) return
    let live = true
    api.tutorEstimate(question, model.provider, model.model, lessonId, stageId).then((e) => live && setEstimate(e.max_cost_usd)).catch(() => live && setEstimate(null))
    return () => {
      live = false
    }
  }, [enabled, model, question, lessonId, stageId])

  if (!openIt) {
    return (
      <button type="button" className="tmsg__polish-open" onClick={() => setOpenIt(true)}>
        <Sparkle aria-hidden /> Polish with AI (optional, paid)
      </button>
    )
  }
  if (!status) return <p className="label" role="status">CHECKING…</p>
  if (!enabled) {
    return (
      <p className="tmsg__polish-off">
        <Lock aria-hidden /> AI polish is off on this server. The answer above is the full, free answer.
      </p>
    )
  }
  const run = async () => {
    setState('loading')
    setError(null)
    try {
      setOut(await api.askTutorLlm(question, model.provider, model.model, lessonId, stageId))
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'The request failed.')
    } finally {
      setState('idle')
    }
  }
  return (
    <div className="tmsg__polish">
      {!out && (
        <button type="button" className="btn btn--primary" onClick={run} disabled={state === 'loading'}>
          {state === 'loading' ? 'Asking…' : `Ask ${model.model}${estimate !== null ? ` · max ${usd(estimate)}` : ''}`}
        </button>
      )}
      {error && <p className="notice notice--error" role="alert">{error}</p>}
      {out && (
        <div aria-live="polite">
          <span className="kind-badge kind-badge--real_execution">LLM · paid · from lesson passages only</span>
          <p>{out.text}</p>
          {out.grounded === false && <p className="label">SOME CITATIONS WERE REMOVED OR MISSING: CHECK THE EVIDENCE ABOVE</p>}
          <p className="label">COST {usd(out.cost_usd)} · {out.model}</p>
        </div>
      )}
    </div>
  )
}

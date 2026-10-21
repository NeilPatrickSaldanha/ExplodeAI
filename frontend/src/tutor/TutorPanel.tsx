import { ArrowRight, ChatCircleText, Lock, Question, Sparkle, X } from '@phosphor-icons/react'
import { Fragment, useCallback, useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { api, ApiError } from '../api/client'
import type { AIStatus, TutorAnswer, TutorCheck, TutorClaim, TutorLlmAnswer, TutorPlain, TutorSource, TutorTurn } from '../api/types'
import './tutor.css'

const usd = (n: number) => (n < 0.01 ? `$${n.toFixed(5)}` : `$${n.toFixed(2)}`)
const OPEN_KEY = 'explodeai.tutor.open'
/** On a phone the tutor is a big sheet over the lesson, so it never stays open between pages. */
const isPhone = () => typeof window !== 'undefined' && window.matchMedia('(max-width: 40rem)').matches
const AI_KEY = 'explodeai.tutor.ai'

const store = {
  get: (k: string) => {
    try {
      return sessionStorage.getItem(k) === '1'
    } catch {
      return false
    }
  },
  set: (k: string, v: boolean) => {
    try {
      sessionStorage.setItem(k, v ? '1' : '0')
    } catch {
      /* storage unavailable */
    }
  },
}

type Message =
  | { id: number; role: 'user'; text: string }
  | { id: number; role: 'tutor'; question: string; answer: TutorAnswer }
  | { id: number; role: 'llm'; question: string; out: TutorLlmAnswer }
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

/** What the tutor said last, in a few words, so the next question can refer back to it. */
function turnOf(m: Message): TutorTurn | null {
  if (m.role === 'tutor') {
    const a = m.answer
    const stage = a.plain?.stage_id ?? a.related[0]?.stage_id ?? a.sentences[0]?.stage_id ?? null
    const lesson = a.plain?.lesson_id ?? a.related[0]?.lesson_id ?? a.sentences[0]?.lesson_id ?? null
    const text = a.plain?.what ?? a.sentences[0]?.text ?? a.message ?? ''
    return { question: m.question, answer_text: text.slice(0, 600), lesson_id: lesson, stage_id: stage }
  }
  if (m.role === 'llm') {
    const r = m.out.related?.[0]
    return { question: m.question, answer_text: (m.out.text ?? '').slice(0, 800), lesson_id: r?.lesson_id ?? null, stage_id: r?.stage_id ?? null }
  }
  return null
}

/**
 * "Ask ExplodeAI": a tutor grounded only in the lessons. By default it is free and offline: it leads
 * with the stage's plain-words explanation, then quotes verified lesson content with the claims and
 * sources behind each sentence, and remembers the conversation. An opt-in "Explain with AI" switch
 * lets a language model re-word answers from the same lesson passages; it is paid, shows its cost,
 * and is off unless the server has AI enabled.
 */
export function TutorPanel({ lessonId, lessonNumber, stageId, stageLabel, onGoToStage }: Props) {
  const [open, setOpen] = useState(() => store.get(OPEN_KEY) && !isPhone())
  const [aiMode, setAiMode] = useState(() => store.get(AI_KEY))
  const [status, setStatus] = useState<AIStatus | null>(null)
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
    if (!isPhone()) store.set(OPEN_KEY, v)
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
    if (open) api.aiStatus().then(setStatus).catch(() => setStatus(null))
  }, [open])

  useEffect(() => {
    log.current?.scrollTo({ top: log.current.scrollHeight })
  }, [messages])

  const usable = (status?.allowed_models.filter((m) => m.usable) ?? []).sort(
    (a, b) => a.input_usd_per_million_tokens + a.output_usd_per_million_tokens - (b.input_usd_per_million_tokens + b.output_usd_per_million_tokens),
  )
  const model = usable[0]
  const aiAvailable = !!status?.enabled && !!model
  const aiOn = aiMode && aiAvailable

  const push = useCallback((m: NewMessage) => setMessages((all) => [...all, { ...m, id: next.current++ } as Message]), [])
  const history = (): TutorTurn[] => messages.map(turnOf).filter((t): t is TutorTurn => !!t).slice(-4)

  const ask = async (q: string) => {
    const question = q.trim()
    if (!question || busy) return
    setInput('')
    const past = history()
    push({ role: 'user', text: question })
    setBusy(true)
    try {
      if (aiOn && model) {
        try {
          const out = await api.askTutorLlm(question, model.provider, model.model, lessonId, stageId, past)
          if (out.is_llm === false) push({ role: 'tutor', question, answer: out as unknown as TutorAnswer })
          else {
            push({ role: 'llm', question, out })
            if (out.spent_total_usd !== undefined) setStatus((s) => (s ? { ...s, limits: { ...s.limits, spent_total_usd: out.spent_total_usd as number } } : s))
          }
        } catch (e) {
          push({ role: 'error', text: `${e instanceof ApiError ? e.message : 'The AI request failed.'} Showing the free answer instead.` })
          push({ role: 'tutor', question, answer: await api.askTutor(question, lessonId, stageId, past) })
        }
      } else {
        push({ role: 'tutor', question, answer: await api.askTutor(question, lessonId, stageId, past) })
      }
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
      <button ref={fab} type="button" className="tutor-fab" aria-expanded={open} aria-controls="tutor-panel" onClick={() => (open ? close() : setOpenPersist(true))}>
        <ChatCircleText weight="fill" aria-hidden /> <span className="tutor-fab__text">Ask ExplodeAI</span>
      </button>
      {open && (
        <aside
          id="tutor-panel"
          className={`tutor${messages.length > 0 ? ' tutor--talking' : ''}`}
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
            {messages.length === 0 && <p className="tutor__empty">Ask in your own words, say “explain it simpler” or “give me an example” after an answer, or press Quiz me.</p>}
            {messages.map((m) => (
              <MessageView
                key={m.id}
                m={m}
                lessonId={lessonId}
                stageId={stageId}
                onGoToStage={onGoToStage}
                onReveal={() => setMessages((all) => all.map((x) => (x.id === m.id && x.role === 'quiz' ? { ...x, revealed: true } : x)))}
                onNextQuiz={quiz}
                history={history}
                aiAvailable={aiAvailable}
                aiOn={aiOn}
              />
            ))}
            {busy && (
              <p className="label" role="status">
                THINKING…
              </p>
            )}
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
          <AiSwitch status={status} aiAvailable={aiAvailable} aiMode={aiMode} model={model?.model} onChange={(v) => { setAiMode(v); store.set(AI_KEY, v) }} />
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
            <button type="submit" className="btn btn--primary" disabled={busy || !input.trim()}>
              Ask
            </button>
          </form>
        </aside>
      )}
    </>
  )
}

function AiSwitch({ status, aiAvailable, aiMode, model, onChange }: { status: AIStatus | null; aiAvailable: boolean; aiMode: boolean; model?: string; onChange: (v: boolean) => void }) {
  if (!status) return null
  if (!aiAvailable) {
    return (
      <p className="tutor__ai tutor__ai--off">
        <Lock aria-hidden /> Explain with AI: off on this server. Answers are free and quote the lessons.
      </p>
    )
  }
  return (
    <label className="tutor__ai">
      <input type="checkbox" checked={aiMode} onChange={(e) => onChange(e.target.checked)} />
      <span>
        <Sparkle aria-hidden /> Explain with AI <span className="label" title={`Model: ${model}`}>PAID · ABOUT $0.0002 PER ANSWER · {usd(status.limits.spent_total_usd)} OF {usd(status.limits.total_budget_usd)} USED</span>
      </span>
    </label>
  )
}

function MessageView({
  m, lessonId, stageId, onGoToStage, onReveal, onNextQuiz, history, aiAvailable, aiOn,
}: {
  m: Message
  lessonId: string
  stageId: string | null
  onGoToStage: (id: string) => void
  onReveal: () => void
  onNextQuiz: () => void
  history: () => TutorTurn[]
  aiAvailable: boolean
  aiOn: boolean
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
  if (m.role === 'llm') return <LlmView out={m.out} lessonId={lessonId} stageId={stageId} onGoToStage={onGoToStage} />
  const a = m.answer
  if (a.type === 'chat') return <p className="tmsg tmsg--tutor tmsg--chat">{a.message}</p>
  const lead = a.lead ? <p className="tmsg tmsg--tutor tmsg--chat tmsg--lead">{a.lead}</p> : null
  if (lead) return <>{lead}<MessageView m={{ ...m, answer: { ...a, lead: null } }} lessonId={lessonId} stageId={stageId} onGoToStage={onGoToStage} onReveal={onReveal} onNextQuiz={onNextQuiz} history={history} aiAvailable={aiAvailable} aiOn={aiOn} /></>
  if (a.type === 'overview') return <OverviewView lessons={a.lessons ?? []} focus={a.focus_number ?? null} currentLesson={lessonId} />
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
      {a.plain && <PlainView plain={a.plain} />}
      {a.sentences.length > 0 && (
        <div className="tmsg__body">
          {a.plain && <span className="label">FROM THE LESSONS · VERIFIED</span>}
          {a.sentences.map((s) => (
            <p key={s.passage_id + s.text}>
              {s.text}{' '}
              <span className="tmsg__cites" aria-label="Verified claims behind this sentence">
                {s.claim_ids.map((id) => (
                  <Fragment key={id}>
                    <code className="tmsg__cite">{id}</code>{' '}
                  </Fragment>
                ))}
              </span>
            </p>
          ))}
        </div>
      )}
      {a.analogy && (
        <p className="tmsg__analogy">
          <span className="label">ANALOGY · TEACHING AID</span>
          {a.analogy.text}
        </p>
      )}
      {a.claims.length > 0 && <Evidence claims={a.claims} sources={a.sources} />}
      <Related related={a.related} lessonId={lessonId} stageId={stageId} onGoToStage={onGoToStage} />
      {a.meta.method === 'bm25' && <p className="label">KEYWORD MATCHING ONLY: THE LOCAL MEANING MODEL IS NOT INSTALLED</p>}
      {a.sentences.length > 0 && !aiOn && <Polish question={(m as Extract<Message, { role: 'tutor' }>).question} lessonId={lessonId} stageId={stageId} history={history} available={aiAvailable} />}
    </div>
  )
}

/** The course itself: what each lesson covers, from the lessons' own summaries and objectives. */
function OverviewView({ lessons, focus, currentLesson }: { lessons: NonNullable<TutorAnswer['lessons']>; focus: number | null; currentLesson: string }) {
  return (
    <div className="tmsg tmsg--tutor tmsg--overview">
      <span className="label">{focus ? `LESSON ${String(focus).padStart(2, '0')}` : `${lessons.length} LESSONS`}</span>
      <ul className="tover">
        {lessons.map((l) => (
          <li key={l.lesson_id}>
            <p className="tover__title">
              <Link to={`/lessons/${l.lesson_id}`}>
                Lesson {String(l.number).padStart(2, '0')} · {l.title}
              </Link>
              {l.lesson_id === currentLesson && <span className="label"> · YOU ARE HERE</span>}
            </p>
            <p>{l.summary}</p>
            <p className="label">ABOUT {l.minutes} MIN · {l.stages.length} STAGES</p>
            {focus && (
              <>
                <p className="label">YOU WILL BE ABLE TO</p>
                <ul className="tmsg__claims">
                  {l.objectives.map((o) => (
                    <li key={o}>{o}</li>
                  ))}
                </ul>
                <p className="label">STAGES: {l.stages.join(' → ').toUpperCase()}</p>
              </>
            )}
          </li>
        ))}
      </ul>
    </div>
  )
}

function Related({ related, lessonId, stageId, onGoToStage }: { related: TutorAnswer['related']; lessonId: string; stageId: string | null; onGoToStage: (id: string) => void }) {
  if (related.length === 0) return null
  return (
    <div className="tmsg__related" role="group" aria-label="Open the related stage">
      {related.map((r) =>
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
  )
}

/** The stage's beginner explanation: what it is, a picture in words, and a tiny worked example. */
function PlainView({ plain }: { plain: TutorPlain }) {
  return (
    <section className="tplain" aria-label={`In plain words: ${plain.stage_label}`}>
      <span className="label">IN PLAIN WORDS · {plain.stage_label.toUpperCase()}</span>
      {plain.what && <p className="tplain__what">{plain.what}</p>}
      {plain.why && <p>{plain.why}</p>}
      {plain.analogy && (
        <p className="tmsg__analogy">
          <span className="label">THINK OF IT LIKE · TEACHING AID</span>
          {plain.analogy}
        </p>
      )}
      {plain.happens.length > 0 && (
        <ol className="tplain__steps">
          {plain.happens.map((h) => (
            <li key={h}>{h}</li>
          ))}
        </ol>
      )}
      {plain.example && (
        <div className="tplain__example">
          <span className="label">EXAMPLE · ILLUSTRATIVE</span>
          <p>
            <b>{plain.example.input}</b> <ArrowRight aria-hidden /> {plain.example.steps.join(', then ')} <ArrowRight aria-hidden /> <b>{plain.example.output}</b>
          </p>
        </div>
      )}
      {plain.misconfigured && (
        <p>
          <span className="label">IF IT GOES WRONG</span> {plain.misconfigured}
        </p>
      )}
      {plain.more && <p>{plain.more}</p>}
    </section>
  )
}

const CITE = /\[([a-z0-9][a-z0-9-]*)\]/g

function LlmView({ out, lessonId, stageId, onGoToStage }: { out: TutorLlmAnswer; lessonId: string; stageId: string | null; onGoToStage: (id: string) => void }) {
  const text = out.text ?? ''
  const parts: (string | { id: string })[] = []
  let last = 0
  for (const match of text.matchAll(CITE)) {
    parts.push(text.slice(last, match.index), { id: match[1] })
    last = (match.index ?? 0) + match[0].length
  }
  parts.push(text.slice(last))
  return (
    <div className="tmsg tmsg--tutor tmsg--llm">
      {out.lead && <p className="tmsg__lead">{out.lead}</p>}
      <span className="kind-badge kind-badge--real_execution">AI · paid · from the lessons only</span>
      <p className="tmsg__llmtext">
        {parts.map((p, i) =>
          typeof p === 'string' ? (
            <Fragment key={i}>{p}</Fragment>
          ) : (
            <code key={i} className="tmsg__cite">{p.id}</code>
          ),
        )}
      </p>
      {out.has_citations === false && <p className="label">THIS WORDING HAS NO CITATIONS: THE EVIDENCE BELOW IS WHAT IT WAS BUILT FROM</p>}
      {out.has_citations !== false && out.grounded === false && <p className="label">SOME CITATIONS WERE REMOVED: CHECK THE EVIDENCE</p>}
      {(out.claims?.length ?? 0) > 0 && <Evidence claims={out.claims ?? []} sources={out.sources ?? []} />}
      <Related related={out.related ?? []} lessonId={lessonId} stageId={stageId} onGoToStage={onGoToStage} />
      <p className="label">COST {usd(out.cost_usd)} · {out.model}</p>
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

/** Optional, paid, per-click: an LLM re-words this one answer from the same lesson passages. */
function Polish({ question, lessonId, stageId, history, available }: { question: string; lessonId: string; stageId: string | null; history: () => TutorTurn[]; available: boolean }) {
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
    api.tutorEstimate(question, model.provider, model.model, lessonId, stageId, history()).then((e) => live && setEstimate(e.max_cost_usd)).catch(() => live && setEstimate(null))
    return () => {
      live = false
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [enabled, model, question, lessonId, stageId])

  if (!openIt) {
    return (
      <button type="button" className="tmsg__polish-open" onClick={() => setOpenIt(true)}>
        <Sparkle aria-hidden /> Re-explain this with AI (optional, paid)
      </button>
    )
  }
  if (!status) return <p className="label" role="status">CHECKING…</p>
  if (!enabled || !available) {
    return (
      <p className="tmsg__polish-off">
        <Lock aria-hidden /> AI is off on this server. The answer above is the full, free answer.
      </p>
    )
  }
  const run = async () => {
    setState('loading')
    setError(null)
    try {
      setOut(await api.askTutorLlm(question, model.provider, model.model, lessonId, stageId, history()))
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

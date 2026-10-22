import { CheckCircle, HandPalm, Prohibit, Warning, XCircle } from '@phosphor-icons/react'
import type { ReactNode } from 'react'
import { STATUS_TEXT, fmt } from './agentText'
import type { AgentDecision, AgentMessage, AgentResult, AgentStep, AgentToolDef } from '../../api/types'

/** Arguments as `name: "value"` pairs on one line. */
export function Args({ args }: { args: Record<string, unknown> }) {
  const entries = Object.entries(args)
  if (!entries.length) return <code className="io-mono">no arguments</code>
  return (
    <code className="io-mono agent-args">
      {entries.map(([k, v], i) => (
        <span key={k}>
          {i > 0 && ', '}
          {k}: {typeof v === 'string' ? `“${v}”` : fmt(v)}
        </span>
      ))}
    </code>
  )
}

/** A short, readable form of a tool's result. */
export function ResultText({ tool, content }: { tool?: string; content: Record<string, unknown> | null }) {
  if (!content) return <>nothing came back</>
  if ('error' in content) return <>error: {String(content.error)}</>
  if (tool === 'search_help_centre' || 'results' in content) {
    const results = (content.results as { title: string; score: number }[]) ?? []
    return <>{results.length ? results.map((r) => `“${r.title}”`).join(' and ') : 'no matching articles'}</>
  }
  if ('found' in content) {
    return content.found ? (
      <>
        {String(content.item)}, {Number(content.price).toLocaleString()} CAD, {String(content.status)}
        {content.delivered ? ` on ${String(content.delivered)}` : ''}
        {content.custom_built ? ', custom-built' : ''}
      </>
    ) : (
      <>no order {String(content.order_id)}</>
    )
  }
  if ('days' in content) return <>{String(content.days)} days</>
  if ('issued' in content) return <>refund {String(content.refund_id)}: {Number(content.amount).toLocaleString()} {String(content.currency)}</>
  return <>{fmt(content)}</>
}

function Row({ label, tone, children }: { label: string; tone?: 'ok' | 'bad' | 'warn'; children: ReactNode }) {
  return (
    <div className={`atrace__row${tone ? ` is-${tone}` : ''}`}>
      <span className="label atrace__label">{label}</span>
      <div className="atrace__body">{children}</div>
    </div>
  )
}

function ToolChoice({ d }: { d: AgentDecision }) {
  if (d.scores.length < 2) return null
  const max = Math.max(0.001, ...d.scores.map((s) => s.score))
  return (
    <ul className="atrace__scores" aria-label="How well each tool's description matches what the agent wants">
      {d.scores.map((s) => (
        <li key={s.tool} className={s.tool === d.tool ? 'is-chosen' : undefined}>
          <span className="atrace__scorebar" style={{ width: `${Math.max(2, (s.score / max) * 100)}%` }} aria-hidden />
          <code>{s.tool}</code>
          <span className="label">{s.score.toFixed(2)}{s.tool === d.tool ? ' · CHOSEN' : ''}</span>
        </li>
      ))}
    </ul>
  )
}

function StepView({ step }: { step: AgentStep }) {
  const d = step.decision
  const v = step.validation
  const ex = step.execution
  const ob = step.observation
  return (
    <li className="atrace__step">
      <header className="atrace__head">
        <span className="atrace__num">{step.index}</span>
        <span className="label">STEP {step.index} · THE MODEL SEES {step.tokens_in.toLocaleString()} TOKENS</span>
      </header>
      {!d && <Row label="Decide" tone="bad">Nothing decides what to do next.</Row>}
      {d?.kind === 'tool_call' && d.tool && (
        <>
          <Row label="Decide">
            <p className="atrace__why">{d.reason}</p>
            <p>
              Calls <code>{d.tool}</code> with <Args args={d.arguments} />
            </p>
            <ToolChoice d={d} />
          </Row>
          {v && (
            <Row label="Check" tone={v.errors.length ? 'bad' : v.checked ? 'ok' : 'warn'}>
              {!v.checked ? (
                <>
                  <Prohibit aria-hidden /> Arguments are not checked, so whatever it wrote goes straight to the tool.
                </>
              ) : v.errors.length ? (
                <>
                  <XCircle aria-hidden /> Rejected: {v.errors.join('; ')}
                </>
              ) : (
                <>
                  <CheckCircle aria-hidden /> Arguments match the tool’s schema.
                </>
              )}
            </Row>
          )}
          {ex && (
            <Row label="Run" tone={ex.ran ? undefined : 'warn'}>
              {ex.ran ? (
                <>
                  The application ran <code>{d.tool}</code>
                  {ex.approved_by_person ? ' after a person approved it' : ''}.
                </>
              ) : (
                <>
                  {ex.reason === 'waiting for a person to approve' ? <HandPalm aria-hidden /> : <Warning aria-hidden />} Not run:{' '}
                  {ex.reason}.
                </>
              )}
            </Row>
          )}
          {ob && (
            <Row label="Result" tone={ob.is_error ? 'bad' : undefined}>
              {ob.returned ? <ResultText tool={d.tool ?? undefined} content={ob.content} /> : 'The result was dropped, so the agent never sees it.'}
            </Row>
          )}
        </>
      )}
      {d?.kind === 'final' && (
        <Row label="Decide" tone="ok">
          {d.reason}
        </Row>
      )}
    </li>
  )
}

export function LoopTrace({ result }: { result: AgentResult }) {
  return (
    <div className="atrace">
      <p className={`atrace__status is-${result.status}`} role="status">
        {result.status === 'answered' ? <CheckCircle aria-hidden /> : result.status === 'needs_approval' ? <HandPalm aria-hidden /> : <Warning aria-hidden />}{' '}
        {STATUS_TEXT[result.status]} · {result.stats.steps} step{result.stats.steps === 1 ? '' : 's'}
      </p>
      <ol className="atrace__steps" aria-label="Every step the agent took">
        {result.steps.map((s) => (
          <StepView key={s.index} step={s} />
        ))}
      </ol>
      {result.answer && (
        <blockquote className="atrace__answer">
          <span className="label">FINAL ANSWER · BUILT ONLY FROM THE TOOL RESULTS ABOVE</span>
          <p>{result.answer}</p>
        </blockquote>
      )}
    </div>
  )
}

/** Exactly what the model is sent on the last step: system prompt, tool definitions and every message so far. */
export function ConversationView({ result }: { result: AgentResult }) {
  const last = result.steps[result.steps.length - 1]
  return (
    <div className="aconv">
      <p className="notice">
        This is the whole conversation the model reads on its <strong>last</strong> step ({last?.tokens_in.toLocaleString()} tokens). Every
        step re-sends all of it. {result.model.token_label}
      </p>
      <Bubble role="System" tokens>
        {result.system}
      </Bubble>
      <Bubble role="Tools">{result.tools.length ? result.tools.map((t) => t.name).join(', ') : 'none'}</Bubble>
      {result.messages.map((m, i) => (
        <Bubble key={i} role={roleOf(m)} tone={m.role === 'tool' && m.is_error ? 'bad' : undefined}>
          {textOf(m)}
        </Bubble>
      ))}
    </div>
  )
}

const roleOf = (m: AgentMessage) => (m.role === 'user' ? 'You' : m.role === 'tool' ? `Result · ${m.tool}` : m.kind === 'final' ? 'Agent' : `Agent calls · ${m.tool}`)
const textOf = (m: AgentMessage) => (m.role === 'tool' ? fmt(m.content) : m.role === 'assistant' && m.kind === 'tool_call' ? fmt(m.arguments) : m.content)

function Bubble({ role, tone, children }: { role: string; tone?: 'bad'; tokens?: boolean; children: ReactNode }) {
  return (
    <div className={`aconv__msg${tone ? ` is-${tone}` : ''}`}>
      <span className="label">{role}</span>
      <p>{children}</p>
    </div>
  )
}

export function ToolsView({ tools }: { tools: AgentToolDef[] }) {
  if (!tools.length) return <p className="notice">No tools are available to the agent.</p>
  return (
    <ul className="atools">
      {tools.map((t) => (
        <li key={t.name} className="atools__tool">
          <header>
            <code>{t.name}</code>
            {t.side_effects && <span className="label atools__warn">CHANGES THINGS · NEEDS APPROVAL</span>}
          </header>
          <p>{t.description}</p>
          <dl>
            {Object.entries(t.input_schema.properties).map(([k, v]) => (
              <div key={k}>
                <dt>
                  <code>{k}</code>
                  {t.input_schema.required.includes(k) && <span className="label"> REQUIRED</span>}
                </dt>
                <dd>
                  {v.type}
                  {v.pattern ? <code> must match {v.pattern}</code> : null}
                </dd>
              </div>
            ))}
          </dl>
        </li>
      ))}
    </ul>
  )
}

/** Tokens the model reads on each step. Each bar is one step; the printed number is the same value. */
export function ContextChart({ result }: { result: AgentResult }) {
  const max = Math.max(1, ...result.steps.map((s) => s.tokens_in))
  const cap = result.steps.length > 14
  const steps = cap ? result.steps.filter((_, i) => i % Math.ceil(result.steps.length / 14) === 0 || i === result.steps.length - 1) : result.steps
  return (
    <figure className="actx">
      <figcaption className="label">TOKENS THE MODEL READS ON EACH STEP · {result.model.token_label.toUpperCase()}</figcaption>
      <ol className="actx__bars">
        {steps.map((s) => (
          <li key={s.index}>
            <span className="actx__val">{s.tokens_in.toLocaleString()}</span>
            <span className="actx__bar" style={{ height: `${Math.max(4, (s.tokens_in / max) * 100)}%` }} aria-hidden />
            <span className="label">{s.index}</span>
          </li>
        ))}
      </ol>
      <p className="actx__sum">
        Added up, the model read <strong>{result.stats.tokens_total.toLocaleString()}</strong> tokens in {result.stats.steps} steps. The last
        step alone was {result.stats.tokens_last.toLocaleString()}: each step pays for everything before it again.
      </p>
    </figure>
  )
}

export function StatsStrip({ result }: { result: AgentResult }) {
  const s = result.stats
  return (
    <dl className="outcome__stats" aria-label="Numbers from this run">
      <div><dt>Steps</dt><dd>{s.steps}</dd></div>
      <div><dt>Tools run</dt><dd>{s.tool_runs}</dd></div>
      <div><dt>Bad calls caught</dt><dd>{s.invalid_calls}</dd></div>
      <div><dt>Tokens read, total</dt><dd>{s.tokens_total.toLocaleString()}</dd></div>
      <div><dt>Refunds issued</dt><dd>{result.refunds.length}</dd></div>
      <div><dt>Without approval</dt><dd>{s.unapproved_side_effects}</dd></div>
    </dl>
  )
}

export function ApprovalCard({ result, onApprove }: { result: AgentResult; onApprove: () => void }) {
  if (result.status !== 'needs_approval' || !result.held) return null
  const a = result.held.arguments
  return (
    <section className="aapprove" aria-labelledby="aapprove-title">
      <h4 id="aapprove-title">
        <HandPalm weight="bold" aria-hidden /> The agent wants to move money
      </h4>
      <p>
        It asks to run <code>{result.held.tool}</code> for order <code>{String(a.order_id)}</code>, amount{' '}
        <strong>{Number(a.amount).toLocaleString()} CAD</strong>. Nothing has happened yet. This is a made-up shop and a pretend ledger, but
        a real agent would wait here for a person.
      </p>
      <button type="button" className="btn" onClick={onApprove}>
        Approve this refund
      </button>
    </section>
  )
}

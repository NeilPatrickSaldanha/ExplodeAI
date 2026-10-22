import { ArrowRight } from '@phosphor-icons/react'
import type { ReactNode } from 'react'
import type { AgentResult, Component } from '../../api/types'
import { Chips } from '../tokenization/TokStageIO'
import { STATUS_TEXT } from './agentText'
import { Args, ResultText } from './AgentViews'

/** What goes in → what comes out of one agent step, from the last REAL run. */
export function AgentStageIO({ component, result }: { component: Component; result: AgentResult | null }) {
  const io = result ? views(component.id, result) : null
  return (
    <div className="stage-io" aria-label={`What goes into and comes out of ${component.label}`}>
      <Card title="Goes in" items={component.inputs ?? []}>{io?.input}</Card>
      <ArrowRight className="stage-io__arrow" aria-hidden />
      <Card title="Comes out" items={component.outputs ?? []}>{io?.output}</Card>
    </div>
  )
}

function Card({ title, items, children }: { title: string; items: string[]; children?: ReactNode }) {
  return (
    <section className="io-card">
      <h4 className="label">{title}</h4>
      <p className="io-card__what">{items.join(' + ') || '—'}</p>
      <div className="io-card__viz">{children ?? <span className="label">RUNNING…</span>}</div>
    </section>
  )
}

const Mono = ({ children }: { children: ReactNode }) => <code className="io-mono">{children}</code>

function views(id: string, r: AgentResult): { input: ReactNode; output: ReactNode } {
  const first = r.steps.find((s) => s.decision?.kind === 'tool_call')
  const toolSteps = r.steps.filter((s) => s.decision?.kind === 'tool_call')
  const lastTool = toolSteps[toolSteps.length - 1]
  switch (id) {
    case 'goal':
      return { input: <p className="io-quote">“{r.params.goal}”</p>, output: <Mono>1 user message</Mono> }
    case 'tools':
      return {
        input: <Mono>{r.params.descriptions} descriptions</Mono>,
        output: r.tools.length ? <Chips items={r.tools.map((t) => t.name)} max={6} label="Tools" /> : <Mono>no tools</Mono>,
      }
    case 'decide':
      return {
        input: <Mono>goal + {r.tools.length} tools{r.steps.length > 1 ? ` + ${r.steps.length - 1} earlier step${r.steps.length > 2 ? 's' : ''}` : ''}</Mono>,
        output: first?.decision?.tool ? (
          <>
            <Mono>{first.decision.tool}</Mono>
            <Args args={first.decision.arguments} />
          </>
        ) : (
          <Mono>{r.answer ? 'a final answer' : 'no decision'}</Mono>
        ),
      }
    case 'validate': {
      const bad = toolSteps.find((s) => s.validation?.errors.length)
      return {
        input: bad?.decision ? <Args args={bad.decision.arguments} /> : first?.decision ? <Args args={first.decision.arguments} /> : <Mono>no call</Mono>,
        output: !r.params.validate_args ? (
          <Mono>not checked</Mono>
        ) : bad ? (
          <Mono>rejected: {bad.validation?.errors[0]}</Mono>
        ) : (
          <Mono>all {toolSteps.length} calls valid</Mono>
        ),
      }
    }
    case 'execute':
      return {
        input: <Mono>{toolSteps.length} checked call{toolSteps.length === 1 ? '' : 's'}</Mono>,
        output: <Mono>{r.stats.tool_runs} run by the application</Mono>,
      }
    case 'observe': {
      const ran = toolSteps.find((s) => s.observation?.returned)
      return {
        input: <Mono>raw output of the tool</Mono>,
        output: ran?.observation ? (
          <Mono>
            <ResultText tool={ran.decision?.tool ?? undefined} content={ran.observation.content} />
          </Mono>
        ) : (
          <Mono>no result</Mono>
        ),
      }
    }
    case 'context':
      return {
        input: <Mono>{r.messages.length} messages so far</Mono>,
        output: <Mono>{r.steps[0]?.tokens_in.toLocaleString()} → {r.stats.tokens_last.toLocaleString()} tokens</Mono>,
      }
    default:
      return {
        input: <Mono>{lastTool || r.answer ? (r.answer ? 'final answer' : 'a tool call') : 'no decision'}</Mono>,
        output: <Mono>{STATUS_TEXT[r.status]}</Mono>,
      }
  }
}

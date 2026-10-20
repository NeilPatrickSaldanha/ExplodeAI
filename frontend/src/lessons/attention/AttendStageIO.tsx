import { ArrowRight } from '@phosphor-icons/react'
import type { ReactNode } from 'react'
import type { AttendResult, Component } from '../../api/types'
import { Chips } from '../tokenization/TokStageIO'
import { TokenHeat } from '../embeddings/EmbedViews'
import { AttentionGrid } from './AttendViews'

/** What goes in → what comes out of one attention step, from the last REAL run. */
export function AttendStageIO({ component, result }: { component: Component; result: AttendResult | null }) {
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

function views(id: string, r: AttendResult): { input: ReactNode; output: ReactNode } {
  const n = r.tokens.length
  const words = r.tokens.map((t) => t.text)
  const h = r.heads[Math.min(r.selected_head, r.heads.length - 1)]
  switch (id) {
    case 'tokens':
      return { input: <p className="io-quote">“{r.params.text}”</p>, output: <Chips items={words} max={12} label="Tokens" /> }
    case 'embed_pos':
      return {
        input: <Mono>{n} words · fixed random vector each</Mono>,
        output: <TokenHeat tokens={r.tokens.slice(0, 5)} rows={r.embedding.input_preview.slice(0, 5)} />,
      }
    case 'qkv':
      return {
        input: <Mono>{n} × {r.model.d_model}</Mono>,
        output: <TokenHeat tokens={r.tokens.slice(0, 4)} rows={h.q.slice(0, 4)} />,
      }
    case 'scores':
      return {
        input: <Mono>Q and K · head {h.index + 1}</Mono>,
        output: <Mono>{n} × {n} scores · spread {r.stats.score_std_used.toFixed(1)}</Mono>,
      }
    case 'mask':
      return {
        input: <Mono>{n} × {n} scores</Mono>,
        output: <Mono>{r.params.causal ? 'later words hidden (−∞)' : 'nothing hidden'}</Mono>,
      }
    case 'softmax':
      return {
        input: <Mono>{n} × {n} scores</Mono>,
        output: <AttentionGrid tokens={words} weights={h.weights} causal={r.params.causal} caption="Attention weights, head view" compact />,
      }
    case 'mix':
      return {
        input: <Mono>weights + V</Mono>,
        output: <Mono>{r.model.heads} × {n} × {r.model.head_dim}</Mono>,
      }
    default:
      return {
        input: <Mono>{r.model.heads} head results</Mono>,
        output: <TokenHeat tokens={r.tokens.slice(0, 4)} rows={r.output.preview.slice(0, 4)} />,
      }
  }
}

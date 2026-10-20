import { ArrowRight } from '@phosphor-icons/react'
import type { ReactNode } from 'react'
import type { Component, EmbedResult } from '../../api/types'
import { VectorStrip } from '../rag/StageIO'
import { Chips } from '../tokenization/TokStageIO'
import { Neighbours, TokenHeat } from './EmbedViews'

/** What goes in → what comes out of one stage, from the last REAL run. */
export function EmbedStageIO({ component, result }: { component: Component; result: EmbedResult | null }) {
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

function views(id: string, r: EmbedResult): { input: ReactNode; output: ReactNode } {
  const q = r.query
  const neural = q.embedder === 'neural'
  const cats = r.library.categories
  switch (id) {
    case 'library':
      return {
        input: <Mono>{cats.join(' · ')}</Mono>,
        output: <Mono>{r.library.items.length} sentences</Mono>,
      }
    case 'your_text':
      return { input: <p className="io-quote">“{q.text}”</p>, output: <p className="io-quote">“{q.model_input}”</p> }
    case 'tokenizer':
      return {
        input: <p className="io-quote">“{q.model_input}”</p>,
        output: <Chips items={q.tokens.map((t) => t.text)} max={14} label={neural ? 'WordPiece tokens' : 'Lexical terms'} />,
      }
    case 'encoder':
      return {
        input: <Mono>{q.tokens.length} token ids</Mono>,
        output: q.token_vectors ? <TokenHeat tokens={q.tokens} rows={q.token_vectors.slice(0, 8)} /> : <Mono>lexical: no encoder</Mono>,
      }
    case 'pooling':
      return {
        input: <Mono>{neural ? `${q.tokens.length} × ${q.dim} token vectors` : 'hashed terms'}</Mono>,
        output: <VectorStrip values={q.pooled_preview} label={`One ${q.dim}-dimensional vector, first ${q.pooled_preview.length} values`} />,
      }
    case 'normalizer':
      return {
        input: <Mono>length {q.norm_before.toFixed(3)}</Mono>,
        output: <Mono>length {q.norm_after.toFixed(3)}</Mono>,
      }
    case 'similarity':
      return {
        input: <Mono>1 + {r.library.items.length} vectors · {r.params.metric}</Mono>,
        output: <Neighbours result={r} max={3} />,
      }
    default:
      return {
        input: <Mono>{r.library.items.length + 1} × {r.model.dim}</Mono>,
        output: <Mono>3D points · {Math.round(r.projection.explained_variance * 100)}% kept</Mono>,
      }
  }
}

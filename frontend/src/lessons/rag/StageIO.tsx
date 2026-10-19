import { ArrowRight } from '@phosphor-icons/react'
import type { ReactNode } from 'react'
import type { Component, RagResult } from '../../api/types'

/**
 * "What goes in → what comes out" for one stage, drawn from the last REAL run.
 * Every number here is read from the experiment result; nothing is mocked.
 */
export function StageIO({ component, result }: { component: Component; result: RagResult | null }) {
  const io = result ? views(component.id, result) : null
  return (
    <div className="stage-io" aria-label={`What goes into and comes out of ${component.label}`}>
      <IOCard title="Goes in" items={component.inputs ?? []}>{io?.input}</IOCard>
      <ArrowRight className="stage-io__arrow" aria-hidden />
      <IOCard title="Comes out" items={component.outputs ?? []}>{io?.output}</IOCard>
    </div>
  )
}

function IOCard({ title, items, children }: { title: string; items: string[]; children?: ReactNode }) {
  return (
    <section className="io-card">
      <h4 className="label">{title}</h4>
      <p className="io-card__what">{items.join(' + ') || '—'}</p>
      <div className="io-card__viz">{children ?? <span className="label">RUNNING…</span>}</div>
    </section>
  )
}

/** A vector drawn as a strip of cells: height of each cell = value (real numbers from the run). */
export function VectorStrip({ values, label }: { values: number[]; label: string }) {
  const max = Math.max(1e-9, ...values.map((v) => Math.abs(v)))
  return (
    <div className="vstrip" role="img" aria-label={label}>
      {values.map((v, i) => (
        <span key={i} className={v >= 0 ? 'is-pos' : 'is-neg'} style={{ transform: `scaleY(${Math.max(0.08, Math.abs(v) / max)})` }} />
      ))}
    </div>
  )
}

function Mono({ children }: { children: ReactNode }) {
  return <code className="io-mono">{children}</code>
}

function ChunkList({ ids, scores }: { ids: string[]; scores?: number[] }) {
  return (
    <ol className="io-list">
      {ids.slice(0, 4).map((id, i) => (
        <li key={id}>
          <Mono>{id}</Mono>
          {scores && <span className="io-list__score">{scores[i].toFixed(3)}</span>}
        </li>
      ))}
      {ids.length > 4 && <li className="label">+{ids.length - 4} MORE</li>}
    </ol>
  )
}

function Budget({ used, budget, dropped }: { used: number; budget: number; dropped: number }) {
  const pct = Math.min(100, Math.round((used / budget) * 100))
  return (
    <div className="io-budget" role="img" aria-label={`${used} of ${budget} words used, ${dropped} chunks dropped`}>
      <span className="io-budget__bar" style={{ transform: `scaleX(${pct / 100})` }} />
      <span className="label">
        {used}/{budget} WORDS{dropped ? ` · ${dropped} DROPPED` : ''}
      </span>
    </div>
  )
}

function views(id: string, r: RagResult): { input: ReactNode; output: ReactNode } {
  const chunkIds = r.chunks.map((c) => c.id)
  // The PCA point is the only per-vector data the API ships; show the query's 3 coordinates
  // honestly labelled, and a strip of all chunks' first PCA axis for the index.
  const firstAxis = r.chunks.map((c) => c.point[0])
  const docs = r.corpus.documents
  switch (id) {
    case 'corpus':
      return {
        input: <ul className="io-docs">{docs.slice(0, 4).map((d) => <li key={d.id}>{d.title}</li>)}</ul>,
        output: <Mono>{docs.length} docs · {docs.reduce((n, d) => n + d.text.split(/\s+/).length, 0)} words</Mono>,
      }
    case 'chunker':
      return {
        input: <Mono>{docs.length} docs</Mono>,
        output: <ChunkList ids={chunkIds} />,
      }
    case 'embedder':
      return {
        input: <Mono>{r.chunks.length} chunks of text</Mono>,
        output: (
          <>
            <VectorStrip values={firstAxis} label={`One value per chunk on the first PCA axis of ${r.chunks.length} chunk vectors`} />
            <span className="label">{r.chunks.length} × {r.embedding.dim}-D</span>
          </>
        ),
      }
    case 'vector_index':
      return {
        input: <Mono>{r.chunks.length} × {r.embedding.dim} vectors</Mono>,
        output: <Mono>flat index · exact search</Mono>,
      }
    case 'query_encoder':
      return {
        input: <p className="io-quote">“{r.query.text}”</p>,
        output: (
          <>
            <VectorStrip values={r.query.point} label="Query vector, first three PCA coordinates" />
            <span className="label">1 × {r.embedding.dim}-D (3 PCA COORDS SHOWN)</span>
          </>
        ),
      }
    case 'retriever':
      return {
        input: <Mono>query vector + {r.chunks.length} vectors</Mono>,
        output: <ChunkList ids={r.retrieved.map((x) => x.chunk_id)} scores={r.retrieved.map((x) => x.score)} />,
      }
    case 'prompt_builder':
      return {
        input: <Mono>{r.retrieved.length} chunks + question</Mono>,
        output: <Budget used={r.prompt.context_words} budget={r.prompt.budget_words} dropped={r.prompt.dropped.length} />,
      }
    default:
      return {
        input: <Mono>{r.prompt.text.split(/\s+/).length}-word prompt</Mono>,
        output: <p className="io-quote">{r.answer.text}</p>,
      }
  }
}

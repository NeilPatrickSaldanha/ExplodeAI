import type { ChunkOut, RagResult, RagParams } from '../../api/types'
import { LLMAnswerPanel } from './LLMAnswerPanel'

/** Document text with chunk boundaries, overlaps, and retrieved chunks marked. */
export function ChunkDocView({ result }: { result: RagResult }) {
  const retrieved = new Set(result.retrieved.map((r) => r.chunk_id))
  return (
    <div className="docview">
      <p className="docview__legend label">
        <span className="swatch swatch--chunk" /> chunk <span className="swatch swatch--overlap" /> overlap{' '}
        <span className="swatch swatch--hit" /> retrieved · ▏marks a chunk start
      </p>
      {result.corpus.documents.map((doc) => {
        const chunks = result.chunks.filter((c) => c.doc_id === doc.id)
        return (
          <article key={doc.id} className="docview__doc" aria-label={`${doc.title}: ${chunks.length} chunks`}>
            <h4 className="label">
              {doc.id} · {chunks.length} chunks
            </h4>
            <p className="docview__text">{renderRuns(doc.text, chunks, retrieved)}</p>
          </article>
        )
      })}
    </div>
  )
}

function renderRuns(text: string, chunks: ChunkOut[], retrieved: Set<string>) {
  const cuts = new Set<number>([0, text.length])
  for (const c of chunks) {
    cuts.add(c.start)
    cuts.add(c.end)
  }
  const points = [...cuts].sort((a, b) => a - b)
  const starts = new Map(chunks.map((c) => [c.start, c]))
  const out: React.ReactNode[] = []
  for (let i = 0; i < points.length - 1; i++) {
    const [s, e] = [points[i], points[i + 1]]
    const covering = chunks.filter((c) => c.start <= s && c.end >= e)
    const hit = covering.some((c) => retrieved.has(c.id))
    const startChunk = starts.get(s)
    if (startChunk) {
      out.push(
        <span key={`m${s}`} className="docview__mark" title={startChunk.id}>
          <span className="visually-hidden">start of {startChunk.id}</span>
        </span>,
      )
    }
    const cls = ['run', covering.length > 1 ? 'run--overlap' : covering.length === 1 ? 'run--chunk' : '', hit ? 'run--hit' : '']
    out.push(
      <span key={`r${s}`} className={cls.join(' ')}>
        {text.slice(s, e)}
      </span>,
    )
  }
  return out
}

export function RankingTable({ result }: { result: RagResult }) {
  const finalRank = new Map(result.retrieved.map((r) => [r.chunk_id, r]))
  const showBm25 = result.chunks.some((c) => c.bm25_rank !== null)
  const rows = [...result.chunks].sort((a, b) => {
    const ra = finalRank.get(a.id)?.rank ?? 999
    const rb = finalRank.get(b.id)?.rank ?? 999
    return ra - rb || a.dense_rank - b.dense_rank
  })
  return (
    <div className="table-wrap" role="region" aria-label="Chunk ranking" tabIndex={0}>
      <table className="ranking">
        <caption className="visually-hidden">Every chunk with its dense and keyword rank. Retrieved chunks first.</caption>
        <thead>
          <tr>
            <th scope="col">Kept</th>
            <th scope="col">Chunk</th>
            <th scope="col">Dense rank · cosine</th>
            {showBm25 && <th scope="col">BM25 rank · score</th>}
            <th scope="col">Text</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((c) => {
            const hit = finalRank.get(c.id)
            return (
              <tr key={c.id} className={hit ? 'is-hit' : undefined}>
                <td>{hit ? `#${hit.rank}` : '—'}</td>
                <td>
                  <code>{c.id}</code>
                </td>
                <td>
                  {c.dense_rank} · {c.dense_score.toFixed(3)}
                </td>
                {showBm25 && (
                  <td>
                    {c.bm25_rank} · {c.bm25_score?.toFixed(2)}
                  </td>
                )}
                <td className="ranking__text">{c.text}</td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}

export function PromptView({ result }: { result: RagResult }) {
  const { prompt } = result
  return (
    <div className="promptview">
      <p className="label">
        {prompt.context_words} / {prompt.budget_words} words of context · {prompt.included.length} included ·{' '}
        {prompt.dropped.length} dropped
      </p>
      {prompt.dropped.length > 0 && (
        <p className="notice notice--warn" role="status">
          Dropped to fit the budget: {prompt.dropped.map((d) => <code key={d}>{d}</code>)}
        </p>
      )}
      <pre className="promptview__text" tabIndex={0} aria-label="Assembled prompt">
        {prompt.text}
      </pre>
    </div>
  )
}

export function AnswerView({ result, params }: { result: RagResult; params?: RagParams }) {
  return (
    <div className="answerview">
      <p className="answerview__text" aria-live="polite">
        {result.answer.sentences.length === 0
          ? result.answer.text
          : result.answer.sentences.map((s, i) => (
              <span key={i}>
                {s.text} <code className="cite">[{s.source}]</code>{' '}
              </span>
            ))}
      </p>
      <p className="answerview__note">
        This answer comes from an extractive baseline: it quotes the retrieved sentences that share the most words
        with your question. A language model would write a fluent answer from the same prompt, and could still be
        wrong.
      </p>
      {params && <LLMAnswerPanel key={JSON.stringify(params)} params={params} />}
    </div>
  )
}

export function TimingStrip({ result }: { result: Pick<RagResult, 'stages' | 'timings_ms'> | null }) {
  const stages = result?.stages ?? []
  const max = Math.max(0.001, ...stages.map((s) => result?.timings_ms[s] ?? 0))
  const total = stages.reduce((s, k) => s + (result?.timings_ms[k] ?? 0), 0)
  return (
    <aside className="meter" aria-label="Stage timings from the last real run">
      <p className="label meter__label">STAGE TIMINGS · REAL RUN</p>
      <ol className="meter__bars">
        {stages.map((s) => {
          const ms = result!.timings_ms[s]
          return (
            <li key={s} title={`${s}: ${ms.toFixed(2)} ms`}>
              <span className="meter__bar" style={{ transform: `scaleY(${Math.max(0.06, Math.sqrt(ms / max))})` }} />
              <span className="visually-hidden">
                {s}: {ms.toFixed(2)} milliseconds
              </span>
            </li>
          )
        })}
      </ol>
      <p className="label meter__label">{result ? `TOTAL · ${total.toFixed(1)} MS` : 'NO RUN YET'}</p>
    </aside>
  )
}

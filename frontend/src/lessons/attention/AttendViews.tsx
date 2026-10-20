import { useState } from 'react'
import type { AttendResult } from '../../api/types'
import { TokenHeat } from '../embeddings/EmbedViews'

const pct = (w: number) => `${Math.round(w * 100)}%`

/**
 * The attention grid as a real table: each ROW is the word that is asking, each COLUMN is a
 * word it can look at, and a row adds up to 100%. Cell fill height encodes the weight and the
 * number is always printed, so colour is never the only cue. Hatched cells are hidden by the
 * causal mask.
 */
export function AttentionGrid({
  tokens,
  weights,
  causal,
  selectedRow,
  onRow,
  caption,
  compact = false,
}: {
  tokens: string[]
  weights: number[][]
  causal: boolean
  selectedRow?: number | null
  onRow?: (i: number) => void
  caption: string
  compact?: boolean
}) {
  const [hover, setHover] = useState<[number, number] | null>(null)
  const n = tokens.length
  return (
    <figure className={`agrid${compact ? ' agrid--compact' : ''}`}>
      <div className="table-wrap" role="region" aria-label={caption} tabIndex={0}>
        <table className="agrid__table">
          <caption className="visually-hidden">{caption}</caption>
          <thead>
            <tr>
              <td className="agrid__corner" aria-hidden />
              {tokens.map((t, j) => (
                <th key={j} scope="col" className="agrid__col">
                  <span>{t}</span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {weights.map((row, i) => (
              <tr key={i} className={selectedRow === i ? 'is-selected' : ''}>
                <th scope="row" className="agrid__row">
                  {onRow && !compact ? (
                    <button type="button" aria-pressed={selectedRow === i} onClick={() => onRow(i)}>
                      {tokens[i]}
                    </button>
                  ) : (
                    tokens[i]
                  )}
                </th>
                {row.map((w, j) => {
                  const hidden = causal && j > i
                  return (
                    <td
                      key={j}
                      className={`agrid__cell${hidden ? ' is-hidden' : ''}`}
                      title={hidden ? `${tokens[i]} cannot see ${tokens[j]} (masked)` : `${tokens[i]} → ${tokens[j]}: ${pct(w)}`}
                      onMouseEnter={() => setHover([i, j])}
                      onMouseLeave={() => setHover(null)}
                    >
                      {!hidden && <span className="agrid__bar" style={{ height: `${Math.max(2, w * 100)}%` }} aria-hidden />}
                      <span className="agrid__num">{hidden ? '–' : n <= 8 || compact ? (w * 100).toFixed(0) : ''}</span>
                      <span className="visually-hidden">{hidden ? 'masked' : pct(w)}</span>
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {!compact && (
        <figcaption className="agrid__note" aria-live="polite">
          {hover
            ? causal && hover[1] > hover[0]
              ? `“${tokens[hover[0]]}” cannot see “${tokens[hover[1]]}”: the causal mask hides later words.`
              : `“${tokens[hover[0]]}” gives “${tokens[hover[1]]}” ${pct(weights[hover[0]][hover[1]])} of its attention.`
            : 'Each row is a word asking; each column is a word it can look at. A row adds up to 100%.'}
        </figcaption>
      )}
    </figure>
  )
}

/** One word's attention as a sentence: every word shaded by how much this word looks at it. */
export function LookFrom({ result, row, onRow, head }: { result: AttendResult; row: number; onRow: (i: number) => void; head: number | 'mean' }) {
  const w = head === 'mean' ? result.weights_mean[row] : result.heads[head].weights[row]
  const sorted = w.map((v, j) => ({ v, j })).sort((a, b) => b.v - a.v)
  return (
    <div className="look">
      <p className="label">PICK THE WORD THAT IS LOOKING</p>
      <div className="look__tokens" role="group" aria-label="Words in the sentence">
        {result.tokens.map((t, i) => (
          <button key={i} type="button" className={`look__tok${i === row ? ' is-asker' : ''}`} aria-pressed={i === row} onClick={() => onRow(i)}>
            <span className="look__fill" style={{ height: `${Math.round(w[i] * 100)}%` }} aria-hidden />
            <span className="look__text">{t.text}</span>
            <span className="look__pct">{pct(w[i])}</span>
          </button>
        ))}
      </div>
      <ol className="look__list">
        {sorted.slice(0, 4).map(({ v, j }) => (
          <li key={j}>
            <code>{result.tokens[j].text}</code>
            <span className="look__bar" aria-hidden>
              <span style={{ width: `${v * 100}%` }} />
            </span>
            <span className="neigh__score">{pct(v)}</span>
          </li>
        ))}
      </ol>
      <p className="look__note">
        “{result.tokens[row].text}” builds its new vector from <b>{result.tokens[sorted[0].j].text}</b> most, then the others in
        proportion. The weights on the right add up to 100%.
      </p>
    </div>
  )
}

/** Q, K and V for one head: three vectors per word (first values shown), all real. */
export function QKVView({ result, head }: { result: AttendResult; head: number }) {
  const h = result.heads[head]
  const toks = result.tokens.slice(0, 8)
  return (
    <div className="qkv">
      {(
        [
          ['Q', 'Query: what this word is looking for', h.q],
          ['K', 'Key: what this word offers to be found by', h.k],
          ['V', 'Value: what this word passes on if chosen', h.v],
        ] as const
      ).map(([name, desc, rows]) => (
        <section key={name} className="qkv__block">
          <h4 className="label">
            {name} · {desc}
          </h4>
          <TokenHeat tokens={toks} rows={rows.slice(0, 8)} />
        </section>
      ))}
      <p className="label">
        HEAD {head + 1} OF {result.model.heads} · FIRST {h.q[0]?.length ?? 0} OF {result.model.head_dim} VALUES SHOWN
      </p>
    </div>
  )
}

export function OutputView({ result }: { result: AttendResult }) {
  return (
    <div className="qkv">
      <TokenHeat tokens={result.tokens.slice(0, 8)} rows={result.output.preview.slice(0, 8)} />
      <p className="label">
        {result.tokens.length} NEW VECTORS OF {result.model.d_model} NUMBERS · FIRST {result.output.preview[0]?.length ?? 0} SHOWN
      </p>
    </div>
  )
}

export function StatsStrip({ result }: { result: AttendResult }) {
  const s = result.stats
  return (
    <dl className="outcome__stats" aria-label="Numbers from this run">
      <div>
        <dt>Score spread before scaling</dt>
        <dd>
          {s.score_std_raw.toFixed(1)} <span className="label">EXPECTED ≈ √{s.head_dim} = {s.expected_raw_std.toFixed(1)}</span>
        </dd>
      </div>
      <div>
        <dt>Score spread used</dt>
        <dd>{s.score_std_used.toFixed(1)}</dd>
      </div>
      <div>
        <dt>Strongest weight (average)</dt>
        <dd>{pct(s.mean_max_weight)}</dd>
      </div>
      <div>
        <dt>Attention on later words</dt>
        <dd>{pct(s.future_mass)}</dd>
      </div>
    </dl>
  )
}

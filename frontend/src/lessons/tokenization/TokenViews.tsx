import { CheckCircle, Pause, Play, SkipBack, SkipForward, XCircle } from '@phosphor-icons/react'
import { useEffect, useMemo, useState } from 'react'
import type { TokenizeResult } from '../../api/types'
import { Slider } from '../../components/controls'
import { replayEvents, segmentationAt, showToken } from './adapter'

/** The encoded text as a row of tokens, with ids, bytes, and the decoded round trip. */
export function TokenStrip({ result }: { result: TokenizeResult }) {
  const [showBytes, setShowBytes] = useState(false)
  const { encoding, decoding, input } = result
  return (
    <div className="tokstrip">
      <p className="label">
        {encoding.count} TOKENS · {input.bytes} BYTES · {input.characters} CHARACTERS · · = SPACE · PARTIAL = PART OF A CHARACTER
      </p>
      <ol className="tokstrip__list" aria-label={`${encoding.count} tokens`}>
        {encoding.tokens.map((t, i) => (
          <li
            key={i}
            className={`tok${t.is_unk ? ' tok--unk' : ''}${t.text === null ? ' tok--partial' : ''}`}
            title={t.is_unk ? 'Unknown token: this character is not in the base alphabet' : t.text === null ? `bytes ${t.bytes_hex}: part of a multi-byte character` : `bytes ${t.bytes_hex}`}
          >
            <span className="tok__text">{t.is_unk ? '[UNK]' : t.text === null ? t.bytes_hex : showToken(t.text)}</span>
            <span className="tok__id">
              {t.is_unk ? 'UNKNOWN' : t.text === null ? 'PARTIAL' : `#${t.id}`}
            </span>
            {showBytes && !t.is_unk && <span className="tok__bytes">{t.bytes_hex}</span>}
          </li>
        ))}
      </ol>
      <button type="button" className="btn" aria-pressed={showBytes} onClick={() => setShowBytes((s) => !s)}>
        {showBytes ? 'Hide bytes' : 'Show bytes'}
      </button>
      <div className={`check ${decoding.round_trip ? 'check--pass' : 'check--fail'}`} role="status">
        <p className="check__verdict">
          {decoding.round_trip ? <CheckCircle weight="fill" aria-hidden /> : <XCircle weight="fill" aria-hidden />}
          {decoding.round_trip ? 'Round trip exact: decoding gives back your text.' : 'Round trip fails: the decoded text differs.'}
        </p>
        <p className="tokstrip__decoded">
          <span className="label">DECODED</span> <code>{decoding.text}</code>
        </p>
        {decoding.unk_count > 0 && <p>{decoding.unk_count} token(s) were [UNK], so those characters are gone.</p>}
      </div>
    </div>
  )
}

/** Every merge training learned, in order, plus how the corpus's commonest words were built. */
export function MergeTable({ result }: { result: TokenizeResult }) {
  const { training } = result
  return (
    <div className="merges">
      <p className="label">
        {training.merges_learned} MERGES LEARNED · VOCABULARY {result.vocabulary.base_size} BASE + {result.vocabulary.merges} MERGES +{' '}
        {result.vocabulary.special.length} SPECIAL = {result.vocabulary.size}
      </p>
      {training.word_history.length > 0 && (
        <ul className="wordhist" aria-label="How the most frequent words were built">
          {training.word_history.map((w) => (
            <li key={w.word}>
              <span className="label">
                {showToken(w.word)} · ×{w.count}
              </span>
              <ol className="wordhist__steps">
                <li>
                  <Pieces pieces={w.start} />
                </li>
                {w.steps.map((s) => (
                  <li key={s.after_merges}>
                    <span className="wordhist__after label">after {s.after_merges}</span>
                    <Pieces pieces={s.pieces} />
                  </li>
                ))}
              </ol>
            </li>
          ))}
        </ul>
      )}
      <div className="table-wrap merges__wrap" role="region" aria-label="Learned merges in order" tabIndex={0}>
        <table className="ranking">
          <caption className="visually-hidden">Every merge in the order training learned it, with the pair count at that step.</caption>
          <thead>
            <tr>
              <th scope="col">Rank</th>
              <th scope="col">Pair</th>
              <th scope="col">New token</th>
              <th scope="col">Pair count</th>
            </tr>
          </thead>
          <tbody>
            {training.steps.map((s) => (
              <tr key={s.rank}>
                <td>{s.rank + 1}</td>
                <td>
                  <code>{showToken(s.left)}</code> + <code>{showToken(s.right)}</code>
                </td>
                <td>
                  <code>{showToken(s.token)}</code>
                </td>
                <td>{s.count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function Pieces({ pieces, fresh }: { pieces: string[]; fresh?: string }) {
  return (
    <span className="pieces">
      {pieces.map((p, i) => (
        <span key={i} className={`pieces__p${fresh !== undefined && p === fresh ? ' is-fresh' : ''}`}>
          {showToken(p)}
        </span>
      ))}
    </span>
  )
}

/**
 * Step through the merges the encoder applied to your text. The steps are the
 * backend's real trace; this view only chooses which step to show. Autoplay is
 * offered only when motion is allowed; Previous/Next and the slider always work.
 */
export function MergeReplay({ result, reducedMotion }: { result: TokenizeResult; reducedMotion: boolean }) {
  const events = useMemo(() => replayEvents(result), [result])
  const [state, setState] = useState({ events, k: events.length, playing: false })
  // A new run resets the replay to the final tokens (state derived during render).
  if (state.events !== events) setState({ events, k: events.length, playing: false })
  const k = Math.min(state.k, events.length)
  const playing = state.playing && !reducedMotion && k < events.length
  const setK = (next: number) => setState((s) => ({ ...s, k: next, playing: false }))

  useEffect(() => {
    if (!playing) return
    const id = setTimeout(() => setState((s) => ({ ...s, k: s.k + 1 })), 650)
    return () => clearTimeout(id)
  }, [playing, k])

  const segs = segmentationAt(result, events, k)
  const current = k > 0 ? events[k - 1] : null
  const total = segs.reduce((n, s) => n + s.length, 0)

  if (events.length === 0) {
    return <p className="notice">No merge applies to this text yet. Every piece stays as base symbols. Add merges or try a sentence from the corpus.</p>
  }

  return (
    <div className="replay">
      <div className="replay__controls">
        <button type="button" className="btn btn--icon" aria-label="Previous merge" disabled={k === 0} onClick={() => setK(k - 1)}>
          <SkipBack aria-hidden />
        </button>
        {!reducedMotion && (
          <button
            type="button"
            className="btn btn--icon"
            aria-label={playing ? 'Pause replay' : 'Play replay'}
            aria-pressed={playing}
            onClick={() => setState((s) => ({ ...s, k: !playing && k >= events.length ? 0 : k, playing: !playing }))}
          >
            {playing ? <Pause aria-hidden /> : <Play aria-hidden />}
          </button>
        )}
        <button type="button" className="btn btn--icon" aria-label="Next merge" disabled={k >= events.length} onClick={() => setK(k + 1)}>
          <SkipForward aria-hidden />
        </button>
        <div className="replay__slider">
          <Slider id="replay-step" label="Merges applied" min={0} max={events.length} value={k} format={(v) => `${v} / ${events.length}`} onChange={setK} />
        </div>
      </div>
      {reducedMotion && <p className="label">AUTOPLAY OFF · REDUCED MOTION · STEP WITH THE BUTTONS OR SLIDER</p>}
      <p className="replay__now" aria-live="polite">
        {current ? (
          <>
            Step {k}: merge rank {current.rank + 1} makes <code>{showToken(current.token)}</code>. {total} tokens so far.
          </>
        ) : (
          <>Start: every piece spelled in base symbols. {total} tokens.</>
        )}
      </p>
      <p className="replay__text">
        {segs.map((s, i) => (
          <Pieces key={i} pieces={s} fresh={current && current.piece === i ? current.token : undefined} />
        ))}
      </p>
    </div>
  )
}

const W = 320
const H = 180
const PAD = { l: 40, r: 12, t: 12, b: 34 }

/**
 * Vocabulary size vs the number of tokens your text needs. One series, one
 * y-axis; bytes per token for the corpus is in the table below, not on a second axis.
 */
export function TradeoffChart({ result }: { result: TokenizeResult }) {
  const pts = result.sweep
  const [hover, setHover] = useState<number | null>(null)
  const xs = pts.map((p) => p.vocab_size)
  const ys = pts.map((p) => p.input_tokens)
  const [x0, x1] = [Math.min(...xs), Math.max(...xs, Math.min(...xs) + 1)]
  const y1 = Math.max(...ys, 1)
  const sx = (v: number) => PAD.l + ((v - x0) / (x1 - x0)) * (W - PAD.l - PAD.r)
  const sy = (v: number) => H - PAD.b - (v / y1) * (H - PAD.t - PAD.b)
  const path = pts.map((p, i) => `${i ? 'L' : 'M'}${sx(p.vocab_size).toFixed(1)},${sy(p.input_tokens).toFixed(1)}`).join(' ')
  const currentIdx = pts.findIndex((p) => p.merges === Math.min(result.params.merges, result.training.merges_learned))
  const shown = hover ?? currentIdx
  const yTicks = [0, Math.round(y1 / 2), y1]

  return (
    <figure className="tradeoff">
      <figcaption className="tradeoff__title">Tokens your text needs, by vocabulary size</figcaption>
      <svg viewBox={`0 0 ${W} ${H}`} className="tradeoff__svg" role="img" aria-label={`Line chart: as the vocabulary grows from ${x0} to ${x1} entries, your text needs ${ys[0]} down to ${ys[ys.length - 1]} tokens.`} onMouseLeave={() => setHover(null)}>
        {yTicks.map((t) => (
          <g key={t}>
            <line className="tradeoff__grid" x1={PAD.l} x2={W - PAD.r} y1={sy(t)} y2={sy(t)} />
            <text className="tradeoff__tick" x={PAD.l - 6} y={sy(t)} dy="0.32em" textAnchor="end">
              {t}
            </text>
          </g>
        ))}
        <line className="tradeoff__axis" x1={PAD.l} x2={W - PAD.r} y1={H - PAD.b} y2={H - PAD.b} />
        {[x0, x1].map((t, i) => (
          <text key={t} className="tradeoff__tick" x={sx(t)} y={H - PAD.b + 14} textAnchor={i ? 'end' : 'start'}>
            {t}
          </text>
        ))}
        <text className="tradeoff__axislabel" x={(PAD.l + W - PAD.r) / 2} y={H - 4} textAnchor="middle">
          vocabulary size (entries)
        </text>
        <text className="tradeoff__axislabel" transform={`translate(10 ${(PAD.t + H - PAD.b) / 2}) rotate(-90)`} textAnchor="middle">
          tokens
        </text>
        <path className="tradeoff__line" d={path} />
        {shown >= 0 && <line className="tradeoff__cross" x1={sx(pts[shown].vocab_size)} x2={sx(pts[shown].vocab_size)} y1={PAD.t} y2={H - PAD.b} />}
        {pts.map((p, i) => (
          <g key={p.merges}>
            <circle className={`tradeoff__pt${i === currentIdx ? ' is-current' : ''}`} cx={sx(p.vocab_size)} cy={sy(p.input_tokens)} r={i === currentIdx ? 5 : 3} />
            {/* Hit target bigger than the mark. */}
            <rect x={sx(p.vocab_size) - 10} y={PAD.t} width={20} height={H - PAD.t - PAD.b} fill="transparent" onMouseEnter={() => setHover(i)} />
          </g>
        ))}
      </svg>
      {shown >= 0 && (
        <p className="tradeoff__readout label" aria-live="polite">
          {hover === null ? 'YOUR SETTING · ' : ''}
          {pts[shown].merges} MERGES · VOCAB {pts[shown].vocab_size} · {pts[shown].input_tokens} TOKENS
        </p>
      )}
      <div className="table-wrap" role="region" aria-label="Trade-off data" tabIndex={0}>
        <table className="ranking">
          <caption className="visually-hidden">The same data as the chart, plus how many corpus bytes each token covers.</caption>
          <thead>
            <tr>
              <th scope="col">Merges</th>
              <th scope="col">Vocabulary</th>
              <th scope="col">Your text · tokens</th>
              <th scope="col">Corpus bytes/token (in-sample)</th>
            </tr>
          </thead>
          <tbody>
            {pts.map((p, i) => (
              <tr key={p.merges} className={i === currentIdx ? 'is-hit' : undefined}>
                <td>
                  {p.merges}
                  {i === currentIdx ? ' (yours)' : ''}
                </td>
                <td>{p.vocab_size}</td>
                <td>{p.input_tokens}</td>
                <td>{p.corpus_bytes_per_token.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </figure>
  )
}

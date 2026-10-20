import type { EmbedAblationOutcome } from '../../api/types'

/** One side of the embeddings "what breaks if removed?" comparison. */
export function embedOutcome(o: EmbedAblationOutcome) {
  return (
    <>
      <dl className="outcome__stats">
        <div><dt>Library vectors</dt><dd>{o.library_vectors ?? '—'}</dd></div>
        <div><dt>Your vector</dt><dd>{o.query_vector_dim ? `${o.query_vector_dim}-D` : o.token_vectors ? `${o.token_vectors} tokens` : '—'}</dd></div>
        <div><dt>Map</dt><dd>{o.has_map ? 'yes' : 'no'}</dd></div>
      </dl>
      {o.neighbours.length > 0 ? (
        <ol className="outcome__list">
          {o.neighbours.map((n) => (
            <li key={n.id}>
              <code>{n.id}</code> {n.score === null ? <span className="label">UNRANKED</span> : <span className="neigh__score">{n.score.toFixed(3)}</span>}
            </li>
          ))}
        </ol>
      ) : (
        <p className="outcome__answer">No neighbours.</p>
      )}
      {o.score_range && <p className="label">SCORES {o.score_range[0]} … {o.score_range[1]}</p>}
      {o.notes.length > 0 && <p className="outcome__notes">{o.notes.join(' · ')}</p>}
    </>
  )
}

import { Eye } from '@phosphor-icons/react'
import type { ExperimentGuide as Guide } from '../api/types'

interface Preset {
  label: string
  query?: string
  text?: string
}

/**
 * "What to notice": for the example the learner picked, what to do and what they should see, plus other
 * things worth trying. It answers the question a first-time visitor has in front of a wall of results:
 * what am I supposed to be looking at?
 */
export function ExperimentGuide({ guide, presets, value }: { guide?: Guide; presets: Preset[]; value: string }) {
  if (!guide) return null
  const picked = presets.find((p) => (p.text ?? p.query) === value)?.label
  const entry = picked ? guide.presets[picked] : undefined
  return (
    <section className="xguide" aria-label="What to notice">
      <h4 className="xguide__title">
        <Eye weight="duotone" aria-hidden /> What to notice
      </h4>
      <p className="xguide__intro">{guide.intro}</p>
      {entry ? (
        <div className="xguide__preset">
          <p>
            <span className="label">TRY</span> {entry.try}
          </p>
          <p>
            <span className="label">YOU SHOULD SEE</span> {entry.notice}
          </p>
        </div>
      ) : (
        <p className="xguide__hint">Click one of the example buttons above for a walk-through of what to look for.</p>
      )}
      <details className="xguide__ideas">
        <summary>More things to try</summary>
        <ul>
          {guide.ideas.map((i) => (
            <li key={i.do}>
              <strong>{i.do}</strong>
              <span>{i.see}</span>
            </li>
          ))}
        </ul>
      </details>
    </section>
  )
}

/** One plain sentence at the top of a result tab: what this tab is for. */
export function TabHint({ guide, id }: { guide?: Guide; id: string }) {
  const text = guide?.tabs[id]
  if (!text) return null
  return (
    <p className="tabhint">
      <span className="label">IN THIS TAB</span> {text}
    </p>
  )
}

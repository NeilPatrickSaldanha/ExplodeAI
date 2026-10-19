import { ArrowSquareOut, CheckCircle, Circle, MinusCircle, XCircle } from '@phosphor-icons/react'
import type { Claim, Component, Lesson, PassStatus, Source } from '../../api/types'

const PASS_ICON: Record<PassStatus, { icon: React.ReactNode; text: string }> = {
  passed: { icon: <CheckCircle weight="fill" aria-hidden />, text: 'passed' },
  pending: { icon: <Circle weight="bold" aria-hidden />, text: 'pending' },
  failed: { icon: <XCircle weight="fill" aria-hidden />, text: 'failed' },
  not_applicable: { icon: <MinusCircle weight="bold" aria-hidden />, text: 'not applicable' },
}

export function VerificationDots({ claim }: { claim: Claim }) {
  const passes = [
    ['Primary sources', claim.verification.primary],
    ['Cross-check', claim.verification.cross_check],
    ['Technical', claim.verification.technical],
  ] as const
  return (
    <ul className="vdots" aria-label="Verification passes">
      {passes.map(([name, p]) => (
        <li key={name} className={`vdots__item vdots__item--${p.status}`} title={`${name}: ${PASS_ICON[p.status].text}${p.notes ? ` — ${p.notes}` : ''}`}>
          {PASS_ICON[p.status].icon}
          <span className="visually-hidden">
            {name}: {PASS_ICON[p.status].text}
          </span>
        </li>
      ))}
    </ul>
  )
}

export function ClaimCard({ claim, sources }: { claim: Claim; sources: Map<string, Source> }) {
  return (
    <li className="claim">
      <div className="claim__head">
        <span className="label">
          {claim.kind === 'provider_specific' ? `${claim.provider} · provider-specific` : claim.kind}
        </span>
        <VerificationDots claim={claim} />
      </div>
      <p className="claim__text">{claim.text}</p>
      <ul className="claim__cites">
        {claim.citations.map((c, i) => {
          const s = sources.get(c.source)
          return (
            <li key={i}>
              <blockquote>“{c.excerpt}”</blockquote>
              {s ? (
                <a href={s.url} target="_blank" rel="noreferrer noopener" className="claim__source">
                  {s.publisher} — {s.title}
                  {c.locator ? `, ${c.locator}` : ''}
                  <ArrowSquareOut aria-label="opens in a new tab" />
                </a>
              ) : (
                <span className="claim__source">{c.source}</span>
              )}
            </li>
          )
        })}
      </ul>
    </li>
  )
}

interface Props {
  lesson: Lesson
  component: Component | undefined
  readout?: string
  sources: Map<string, Source>
}

export function Inspector({ lesson, component, readout, sources }: Props) {
  if (!component) {
    return (
      <div className="inspector inspector--empty">
        <p className="label">Pick a part</p>
        <p>Click any part in the model, or move through them with the arrow keys.</p>
        <h3 className="inspector__sub">by the end you can</h3>
        <ul className="objectives">
          {lesson.objectives.map((o) => (
            <li key={o}>{o}</li>
          ))}
        </ul>
      </div>
    )
  }
  const claims = component.claims
    .map((id) => lesson.claims.find((c) => c.id === id))
    .filter((c): c is Claim => Boolean(c))
  const stage = lesson.components.indexOf(component) + 1
  return (
    <div className="inspector">
      <p className="label">
        STAGE {String(stage).padStart(2, '0')} · {component.phase}
        {readout ? ` · ${readout}` : ''}
      </p>
      <h2 className="inspector__title">{component.label}</h2>
      <p className="inspector__short">{component.short}</p>
      <p>{component.detail}</p>
      <h3 className="inspector__sub">what the sources say</h3>
      <ul className="claims">
        {claims.map((c) => (
          <ClaimCard key={c.id} claim={c} sources={sources} />
        ))}
      </ul>
    </div>
  )
}

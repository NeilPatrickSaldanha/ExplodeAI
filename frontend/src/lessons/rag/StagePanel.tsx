import { CaretDown, CaretLeft, CaretRight, CheckCircle, Pause, Play, SealCheck } from '@phosphor-icons/react'
import { lazy, Suspense, useState } from 'react'
import type { Claim, Component, Lesson, RagParams, RagResult, Source } from '../../api/types'
import type { PartSpec } from '../../engine/types'
import { BreaksCard } from './BreaksCard'
import { ClaimCard } from './Inspector'
import { StageIcon } from './StageIcon'
import { StageIO } from './StageIO'

const PartCloseup = lazy(() => import('./PartCloseup').then((m) => ({ default: m.PartCloseup })))

export interface TourState {
  step: number
  total: number
  title: string
  body: string
  autoplay: boolean
  speed: 1 | 2
  onToggleAutoplay: () => void
  onSpeed: (s: 1 | 2) => void
}

interface Props {
  lesson: Lesson
  component: Component | undefined
  part: PartSpec | undefined
  index: number
  result: RagResult | null
  params: RagParams
  sources: Map<string, Source>
  reducedMotion: boolean
  onStep: (delta: number) => void
  tour?: TourState
}

const passed = (c: Claim) =>
  [c.verification.primary, c.verification.cross_check, c.verification.technical].every((p) => p.status === 'passed' || p.status === 'not_applicable')

/**
 * Right-hand stage panel: show first, explain second. A close-up of the part, what
 * goes in and comes out (real data), what breaks if it is removed (a real run),
 * and compact, source-backed facts that expand to their citations.
 */
export function StagePanel({ lesson, component, part, index, result, params, sources, reducedMotion, onStep, tour }: Props) {
  const [openClaim, setOpenClaim] = useState<string | null>(null)
  const total = lesson.components.length

  if (!component || !part) {
    return (
      <div className="spanel spanel--empty">
        <p className="label">PICK A STAGE</p>
        <p className="spanel__lede">Click any part of the machine, or use the stage bar below.</p>
        <ul className="objectives">
          {lesson.objectives.map((o) => (
            <li key={o}>{o}</li>
          ))}
        </ul>
      </div>
    )
  }

  const claims = component.claims.map((id) => lesson.claims.find((c) => c.id === id)).filter((c): c is Claim => !!c)
  const verified = claims.filter(passed).length
  const ablationVisual = lesson.visuals.find((v) => v.id === 'ablation')

  return (
    <div className="spanel">
      {tour && (
        <div className="spanel__tour" role="group" aria-label="Guided tour">
          <div className="spanel__tour-head">
            <span className="label">
              TOUR · STEP {tour.step + 1} OF {tour.total}
            </span>
            <span className="spanel__tour-ctrl">
              <button type="button" className="btn btn--icon" aria-pressed={tour.autoplay} aria-label={tour.autoplay ? 'Pause auto-play' : 'Auto-play the tour'} onClick={tour.onToggleAutoplay}>
                {tour.autoplay ? <Pause aria-hidden /> : <Play aria-hidden />}
              </button>
              <button type="button" className="btn spanel__speed" aria-label={`Auto-play speed ${tour.speed}x`} onClick={() => tour.onSpeed(tour.speed === 1 ? 2 : 1)}>
                {tour.speed}×
              </button>
            </span>
          </div>
          <progress className="tour__progress" max={tour.total} value={tour.step + 1} aria-label="Tour progress" />
          <p className="spanel__tour-title">{tour.title}</p>
          <p className="spanel__tour-body">{tour.body}</p>
        </div>
      )}

      <header className="spanel__head">
        <span className="label">
          STAGE {String(index + 1).padStart(2, '0')} / {String(total).padStart(2, '0')} · {component.phase}
        </span>
        <span className="spanel__nav">
          <button type="button" className="btn btn--icon" aria-label="Previous stage" disabled={index === 0} onClick={() => onStep(-1)}>
            <CaretLeft aria-hidden />
          </button>
          <button type="button" className="btn btn--icon" aria-label="Next stage" disabled={index === total - 1} onClick={() => onStep(1)}>
            <CaretRight aria-hidden />
          </button>
        </span>
      </header>

      <div className="spanel__title-row">
        <span className="spanel__badge" aria-hidden>
          <StageIcon name={component.icon} weight="duotone" />
        </span>
        <div>
          <h2 className="spanel__title">{component.label}</h2>
          <p className="spanel__lede">{component.short}</p>
        </div>
      </div>

      <Suspense fallback={<div className="closeup closeup--loading" />}>
        <PartCloseup part={part} reducedMotion={reducedMotion} label={`Close-up of the ${component.label}, showing its internal parts`} />
      </Suspense>

      <StageIO component={component} result={result} />

      {component.breaks_if_removed && <BreaksCard key={`${component.id}|${JSON.stringify(params)}`} component={component} params={params} visual={ablationVisual} />}

      <section className="facts" aria-labelledby="facts-title">
        <h4 id="facts-title" className="facts__title">
          <SealCheck weight="fill" aria-hidden /> Source-backed facts
          <span className="label">
            {verified}/{claims.length} VERIFIED
          </span>
        </h4>
        <ul className="facts__list">
          {claims.map((c) => {
            const open = openClaim === c.id
            const first = sources.get(c.citations[0]?.source)
            return (
              <li key={c.id} className={`fact${open ? ' is-open' : ''}`}>
                <button type="button" className="fact__head" aria-expanded={open} onClick={() => setOpenClaim(open ? null : c.id)}>
                  <CheckCircle weight="fill" className={passed(c) ? 'is-pass' : ''} aria-label={passed(c) ? 'verified' : 'not fully verified'} />
                  <span className="fact__text">{c.text}</span>
                  <span className="fact__src label">{c.provider ?? first?.publisher.split(' ')[0] ?? ''}</span>
                  <CaretDown className="fact__caret" aria-hidden />
                </button>
                {open && (
                  <ul className="claims">
                    <ClaimCard claim={c} sources={sources} />
                  </ul>
                )}
              </li>
            )
          })}
        </ul>
      </section>
    </div>
  )
}

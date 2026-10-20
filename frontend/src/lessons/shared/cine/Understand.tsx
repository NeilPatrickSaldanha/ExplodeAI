import { ArrowRight, Lightbulb, Play, SkipForward } from '@phosphor-icons/react'
import { useEffect, useRef, useState } from 'react'
import type { Component, Explain } from '../../../api/types'

interface Props {
  component: Component
  explain: Explain
  /** The stages that feed this one and the ones it feeds, from the lesson's connections. */
  before: Component[]
  after: Component[]
  reducedMotion: boolean
  onGoTo: (id: string) => void
}

/**
 * Beginner-first depth for one stage. The short version (what it does, an analogy,
 * a step-through example) is always visible. The rest sits in expandable sections so
 * nobody is handed a wall of text. Examples and analogies are labelled as teaching
 * aids; the verified facts are in "Source-backed facts" below.
 */
export function Understand({ component, explain, before, after, reducedMotion, onGoTo }: Props) {
  return (
    <section className="understand" aria-labelledby="understand-title">
      <h4 id="understand-title" className="understand__title">
        <Lightbulb weight="fill" aria-hidden /> Understand this stage
      </h4>
      <p className="understand__what">{explain.what}</p>
      <p className="understand__analogy">
        <span className="label">ANALOGY · TEACHING AID</span>
        {explain.analogy}
      </p>

      <div className="understand__connect">
        <span className="label">CONNECTED STAGES</span>
        <div className="understand__links" role="group" aria-label="Connected stages">
          {before.map((c) => (
            <button key={c.id} type="button" className="chip" onClick={() => onGoTo(c.id)}>
              ← from {c.label}
            </button>
          ))}
          {after.map((c) => (
            <button key={c.id} type="button" className="chip" onClick={() => onGoTo(c.id)}>
              to {c.label} →
            </button>
          ))}
        </div>
      </div>

      <MiniDemo key={component.id} example={explain.example} reducedMotion={reducedMotion} />

      <Section title="Why it is needed">
        <p>{explain.why}</p>
      </Section>
      <Section title="What happens to the data">
        <ol className="understand__steps">
          {explain.happens.map((h) => (
            <li key={h}>{h}</li>
          ))}
        </ol>
      </Section>
      <Section title="Where it goes next">
        <p>{explain.goes_to}</p>
      </Section>
      <Section title="If it is set up wrong" tone="warn">
        <p>{explain.misconfigured}</p>
      </Section>
      <Section title="Learn more (technical)">
        <p>{explain.learn_more}</p>
        <p className="label">BACKED BY {explain.claims.length} VERIFIED {explain.claims.length === 1 ? 'CLAIM' : 'CLAIMS'} BELOW</p>
      </Section>
    </section>
  )
}

function Section({ title, tone, children }: { title: string; tone?: 'warn'; children: React.ReactNode }) {
  return (
    <details className={`understand__sec${tone ? ` understand__sec--${tone}` : ''}`}>
      <summary>{title}</summary>
      <div className="understand__body">{children}</div>
    </details>
  )
}

/** A tiny input → steps → output demonstration the learner can play or step through. */
function MiniDemo({ example, reducedMotion }: { example: Explain['example']; reducedMotion: boolean }) {
  const total = example.steps.length + 2 // input, each step, output
  const [shown, setShown] = useState(reducedMotion ? total : 1)
  const [playing, setPlaying] = useState(false)
  const timer = useRef<ReturnType<typeof setInterval>>(undefined)

  useEffect(() => {
    if (!playing) return
    timer.current = setInterval(() => {
      setShown((n) => {
        if (n + 1 >= total) setPlaying(false)
        return Math.min(total, n + 1)
      })
    }, 900)
    return () => clearInterval(timer.current)
  }, [playing, total])

  const done = shown >= total
  const play = () => {
    setShown(1)
    if (reducedMotion) setShown(total)
    else setPlaying(true)
  }
  const step = () => {
    setPlaying(false)
    setShown(done ? 1 : shown + 1)
  }

  return (
    <div className="demo" role="group" aria-label="Worked example">
      <div className="demo__head">
        <span className="label">ILLUSTRATIVE EXAMPLE</span>
        <span className="demo__ctrl">
          <button type="button" className="btn" onClick={play}>
            <Play weight="fill" aria-hidden /> {done || playing ? 'Replay' : 'Play'}
          </button>
          <button type="button" className="btn" onClick={step}>
            <SkipForward aria-hidden /> {done ? 'Restart' : 'Step'}
          </button>
        </span>
      </div>
      <div className="demo__flow" aria-live="polite">
        <div className="demo__card is-on">
          <span className="label">IN</span>
          <span>{example.input}</span>
        </div>
        <ArrowRight className="demo__arrow" aria-hidden />
        <ol className="demo__steps">
          {example.steps.map((s, i) => (
            <li key={s} className={shown > i + 1 ? 'is-on' : ''}>
              {s}
            </li>
          ))}
        </ol>
        <ArrowRight className="demo__arrow" aria-hidden />
        <div className={`demo__card${shown >= total ? ' is-on' : ''}`}>
          <span className="label">OUT</span>
          <span>{example.output}</span>
        </div>
      </div>
    </div>
  )
}

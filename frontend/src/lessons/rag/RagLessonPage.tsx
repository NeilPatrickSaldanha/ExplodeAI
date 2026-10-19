import * as Tabs from '@radix-ui/react-tabs'
import { ArrowsClockwise, CornersOut, Crosshair, Cube, Pause, Play, Wind, Square } from '@phosphor-icons/react'
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { api } from '../../api/client'
import type { Challenge, Lesson, RagConfig, Source } from '../../api/types'
import { KindBadge, Slider, Toggle } from '../../components/controls'
import { ExplodedView, type RenderMode } from '../../engine/ExplodedView'
import { useReducedMotion } from '../../engine/hooks'
import type { ViewState } from '../../engine/types'
import { lessonToSpec, readoutsFromResult } from './adapter'
import { Challenges } from './Challenges'
import { ExperimentPanel } from './ExperimentPanel'
import { Inspector } from './Inspector'
import { Rebuild } from './Rebuild'
import { TimingStrip } from './ResultViews'
import { Tour } from './Tour'
import { DEFAULT_PARAMS, useExperiment } from './useExperiment'

type Mode = 'explore' | 'tour' | 'experiment' | 'challenges' | 'rebuild'

function verifiedCount(lesson: Lesson) {
  const ok = (s: string) => s === 'passed' || s === 'not_applicable'
  return lesson.claims.filter((c) => ok(c.verification.primary.status) && ok(c.verification.cross_check.status) && ok(c.verification.technical.status)).length
}

export function RagLessonPage({ lesson }: { lesson: Lesson }) {
  const spec = useMemo(() => lessonToSpec(lesson), [lesson])
  const sources = useMemo(() => new Map<string, Source>(lesson.sources.map((s) => [s.id, s])), [lesson])
  const [motionOverride, setMotionOverride] = useState<boolean | null>(null)
  const reducedMotion = useReducedMotion(motionOverride)
  const [renderMode, setRenderMode] = useState<RenderMode>('3d')
  const [view, setView] = useState<ViewState>({ explode: 0, selectedId: null, isolate: false, flow: true })
  const [resetSignal, setResetSignal] = useState(0)
  const [mode, setMode] = useState<Mode>('explore')
  const [tourStep, setTourStep] = useState(0)
  const [challenge, setChallenge] = useState<Challenge | null>(null)
  const [config, setConfig] = useState<RagConfig | null>(null)
  const [explored, setExplored] = useState<string[]>([])
  const [solved, setSolved] = useState<string[]>([])
  const [rebuilt, setRebuilt] = useState(false)
  const exp = useExperiment()

  // One orchestrated entrance: the assembly explodes open once on load.
  useEffect(() => {
    const id = setTimeout(() => setView((v) => ({ ...v, explode: 0.85 })), reducedMotion ? 0 : 350)
    return () => clearTimeout(id)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    api.ragConfig().then(setConfig).catch(() => setConfig(null))
    api
      .progress(lesson.id)
      .then((p) => {
        setExplored(p.explored_components)
        setSolved(p.solved_challenges)
        setRebuilt(p.reconstruction_solved)
      })
      .catch(() => undefined)
  }, [lesson.id])

  const saveTimer = useRef<ReturnType<typeof setTimeout>>(undefined)
  const select = useCallback(
    (id: string | null) => {
      setView((v) => ({ ...v, selectedId: id, isolate: id ? v.isolate : false }))
      if (id) {
        setExplored((prev) => {
          if (prev.includes(id)) return prev
          const next = [...prev, id]
          clearTimeout(saveTimer.current)
          saveTimer.current = setTimeout(() => api.saveProgress(lesson.id, { explored_components: next }).catch(() => undefined), 600)
          return next
        })
      }
    },
    [lesson.id],
  )

  const onTab = (m: string) => {
    setMode(m as Mode)
    if (m === 'tour') {
      const c = lesson.tour[tourStep].component
      select(c)
      setView((v) => ({ ...v, isolate: true }))
    } else {
      setView((v) => ({ ...v, isolate: false }))
    }
    if (m !== 'challenges' && challenge) exitChallenge()
  }

  const goTour = (i: number) => {
    setTourStep(i)
    select(lesson.tour[i].component)
    setView((v) => ({ ...v, isolate: true }))
  }

  const startChallenge = (c: Challenge) => {
    setChallenge(c)
    exp.setParams({ ...DEFAULT_PARAMS, ...c.broken_params })
  }
  const exitChallenge = () => {
    setChallenge(null)
    exp.setParams(DEFAULT_PARAMS)
  }

  const readouts = readoutsFromResult(exp.result)
  const selected = lesson.components.find((c) => c.id === view.selectedId)
  const visual = (id: string) => lesson.visuals.find((v) => v.id === id)!
  const verified = verifiedCount(lesson)

  return (
    <article className="lesson">
      <header className="lesson__head">
        <div className="lesson__titles">
          <p className="label">
            LESSON 01 · {lesson.estimated_minutes} MIN · {lesson.components.length} PARTS
          </p>
          <h1>
            retrieval-augmented generation,&nbsp;<em>exploded</em>
          </h1>
          <p className="lesson__summary">{lesson.summary}</p>
        </div>
        <div className="lesson__status">
          {lesson.status === 'draft' ? (
            <p className="status-pill status-pill--draft" role="note">
              Draft: verification in progress · {verified}/{lesson.claims.length} claims through all three passes
            </p>
          ) : (
            <p className="status-pill status-pill--ok">
              Verified: {verified}/{lesson.claims.length} claims through all three passes
            </p>
          )}
          <p className="label">
            EXPLORED {explored.length}/{lesson.components.length} · FIXED {solved.length}/{lesson.challenges.length} · REBUILT {rebuilt ? 'YES' : 'NO'}
          </p>
        </div>
      </header>

      <TimingStrip result={exp.result} />

      <div className="lesson__grid">
        <section className="stage" aria-label="Exploded model">
          <div className="stage__frame">
            <ExplodedView
              spec={spec}
              view={view}
              readouts={readouts}
              mode={renderMode}
              reducedMotion={reducedMotion}
              onSelect={select}
              onToggleIsolate={() => setView((v) => ({ ...v, isolate: !v.isolate }))}
              title="Exploded view of a retrieval-augmented generation pipeline"
              resetSignal={resetSignal}
            />
            <div className="stage__badges">
              <KindBadge visual={visual('exploded-view')} />
              {exp.result && <span className="label stage__live">LIVE VALUES FROM YOUR LAST RUN</span>}
            </div>
          </div>

          <div className="stage__toolbar" role="toolbar" aria-label="View controls">
            <div className="stage__explode">
              <Slider id="explode" label="Explode" min={0} max={1} step={0.01} value={view.explode} format={(v) => `${Math.round(v * 100)}%`} onChange={(v) => setView((s) => ({ ...s, explode: v }))} />
            </div>
            <Toggle pressed={view.flow} onChange={(f) => setView((s) => ({ ...s, flow: f }))} label="Animate data flow">
              {view.flow ? <Pause aria-hidden /> : <Play aria-hidden />} Flow
            </Toggle>
            <Toggle pressed={view.isolate} onChange={(i) => setView((s) => ({ ...s, isolate: i && !!s.selectedId }))} label="Isolate the selected part">
              <Crosshair aria-hidden /> Isolate
            </Toggle>
            <Toggle pressed={renderMode === '2d'} onChange={(flat) => setRenderMode(flat ? '2d' : '3d')} label="Switch between 3D and 2D">
              {renderMode === '2d' ? <Square aria-hidden /> : <Cube aria-hidden />} {renderMode === '2d' ? '2D' : '3D'}
            </Toggle>
            <Toggle pressed={reducedMotion} onChange={(r) => setMotionOverride(r)} label="Reduce motion">
              <Wind aria-hidden /> Calm
            </Toggle>
            <button type="button" className="btn btn--icon" aria-label="Reset camera" title="Reset camera" onClick={() => { select(null); setResetSignal((s) => s + 1) }}>
              <ArrowsClockwise aria-hidden />
            </button>
          </div>

          <nav className="partlist" aria-label="Parts">
            <ol>
              {lesson.components.map((c, i) => (
                <li key={c.id}>
                  <button type="button" className={`partlist__btn${view.selectedId === c.id ? ' is-selected' : ''}`} aria-pressed={view.selectedId === c.id} onClick={() => select(view.selectedId === c.id ? null : c.id)}>
                    <span className="label">{String(i + 1).padStart(2, '0')}</span> {c.label}
                    {explored.includes(c.id) && <span className="visually-hidden"> (explored)</span>}
                    {explored.includes(c.id) && <span className="partlist__seen" aria-hidden>•</span>}
                  </button>
                </li>
              ))}
            </ol>
          </nav>
        </section>

        <section className="panel" aria-label="Lesson activities">
          <Tabs.Root value={mode} onValueChange={onTab}>
            <Tabs.List className="modes" aria-label="Mode">
              <Tabs.Trigger className="modes__tab" value="explore">Explore</Tabs.Trigger>
              <Tabs.Trigger className="modes__tab" value="tour">Tour</Tabs.Trigger>
              <Tabs.Trigger className="modes__tab" value="experiment">Experiment</Tabs.Trigger>
              <Tabs.Trigger className="modes__tab" value="challenges">Break &amp; fix</Tabs.Trigger>
              <Tabs.Trigger className="modes__tab" value="rebuild">Rebuild</Tabs.Trigger>
            </Tabs.List>
            <Tabs.Content value="explore" className="panel__body">
              <Inspector lesson={lesson} component={selected} readout={selected ? readouts?.parts?.[selected.id] : undefined} sources={sources} />
            </Tabs.Content>
            <Tabs.Content value="tour" className="panel__body">
              <Tour lesson={lesson} step={tourStep} onStep={goTour} sources={sources} />
            </Tabs.Content>
            <Tabs.Content value="experiment" className="panel__body">
              <ExperimentPanel lesson={lesson} {...exp} neuralAvailable={!!config?.embedders.find((e) => e.id === 'neural-local')?.available} />
            </Tabs.Content>
            <Tabs.Content value="challenges" className="panel__body">
              <Challenges
                lesson={lesson}
                active={challenge}
                solved={solved}
                params={exp.params}
                onStart={startChallenge}
                onExit={exitChallenge}
                onSolved={(id) => {
                  const next = solved.includes(id) ? solved : [...solved, id]
                  setSolved(next)
                  api.saveProgress(lesson.id, { solved_challenges: next }).catch(() => undefined)
                }}
              />
              {challenge && (
                <ExperimentPanel lesson={lesson} {...exp} locked={challenge.locked_params} neuralAvailable={false} />
              )}
            </Tabs.Content>
            <Tabs.Content value="rebuild" className="panel__body">
              <Rebuild
                lesson={lesson}
                solved={rebuilt}
                onSolved={() => {
                  setRebuilt(true)
                  api.saveProgress(lesson.id, { reconstruction_solved: true }).catch(() => undefined)
                }}
              />
            </Tabs.Content>
          </Tabs.Root>
        </section>
      </div>
      <details className="sources">
        <summary>
          <CornersOut aria-hidden /> All {lesson.sources.length} sources for this lesson
        </summary>
        <ul>
          {lesson.sources.map((s) => (
            <li key={s.id}>
              <a href={s.url} target="_blank" rel="noreferrer noopener">
                {s.title}
              </a>{' '}
              — {s.publisher}
              {s.version ? `, ${s.version}` : ''}. Accessed {s.accessed}.
            </li>
          ))}
        </ul>
      </details>
    </article>
  )
}

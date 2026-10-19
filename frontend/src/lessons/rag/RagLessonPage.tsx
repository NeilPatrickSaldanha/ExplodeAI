import * as Tabs from '@radix-ui/react-tabs'
import { ArrowsClockwise, CornersOut, Crosshair, Cube, Info, Pause, Play, SealCheck, Square, Wind } from '@phosphor-icons/react'
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
import { FlowLegend } from './FlowLegend'
import { Rebuild } from './Rebuild'
import { TimingStrip } from './ResultViews'
import { StageBar } from './StageBar'
import { StagePanel } from './StagePanel'
import { DEFAULT_PARAMS, useExperiment } from './useExperiment'
import './rag-cine.css'

type Mode = 'explore' | 'tour' | 'experiment' | 'challenges' | 'rebuild'

/** Seconds each stage stays on screen during tour auto-play, at 1×. */
const AUTOPLAY_SECONDS = 8

function verifiedCount(lesson: Lesson) {
  const ok = (s: string) => s === 'passed' || s === 'not_applicable'
  return lesson.claims.filter((c) => ok(c.verification.primary.status) && ok(c.verification.cross_check.status) && ok(c.verification.technical.status)).length
}

export function RagLessonPage({ lesson }: { lesson: Lesson }) {
  const spec = useMemo(() => lessonToSpec(lesson), [lesson])
  const sources = useMemo(() => new Map<string, Source>(lesson.sources.map((s) => [s.id, s])), [lesson])
  const stageIds = useMemo(() => lesson.components.map((c) => c.id), [lesson])
  // Tour step for each stage, so a click anywhere keeps the tour in sync.
  const tourIndexOf = useMemo(() => new Map(lesson.tour.map((t, i) => [t.component, i])), [lesson])
  const [motionOverride, setMotionOverride] = useState<boolean | null>(null)
  const reducedMotion = useReducedMotion(motionOverride)
  const [renderMode, setRenderMode] = useState<RenderMode>('3d')
  const [view, setView] = useState<ViewState>({ explode: 0, selectedId: null, isolate: false, flow: true, linkCards: 'selected' })
  const [resetSignal, setResetSignal] = useState(0)
  const [mode, setMode] = useState<Mode>('explore')
  const [tourStep, setTourStep] = useState(0)
  const [autoplay, setAutoplay] = useState(false)
  const [speed, setSpeed] = useState<1 | 2>(1)
  const [challenge, setChallenge] = useState<Challenge | null>(null)
  const [config, setConfig] = useState<RagConfig | null>(null)
  const [explored, setExplored] = useState<string[]>([])
  const [solved, setSolved] = useState<string[]>([])
  const [rebuilt, setRebuilt] = useState(false)
  const exp = useExperiment()

  // One orchestrated entrance: the machine explodes open, then stage 01 lights up.
  useEffect(() => {
    // Stage 01 is shown, not marked explored: progress only counts the learner's own clicks.
    const id = setTimeout(() => setView((v) => ({ ...v, explode: 0.85, selectedId: v.selectedId ?? stageIds[0] })), reducedMotion ? 0 : 350)
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
  const markExplored = useCallback(
    (id: string) =>
      setExplored((prev) => {
        if (prev.includes(id)) return prev
        const next = [...prev, id]
        clearTimeout(saveTimer.current)
        saveTimer.current = setTimeout(() => api.saveProgress(lesson.id, { explored_components: next }).catch(() => undefined), 600)
        return next
      }),
    [lesson.id],
  )

  /**
   * The single way to change stage — scene click, stage bar, panel arrows,
   * keyboard, tour next/back and auto-play all route here, so the selected node,
   * tour step, right panel and flow emphasis can never disagree.
   */
  const goToStage = useCallback(
    (id: string | null) => {
      setView((v) => ({ ...v, selectedId: id, isolate: id ? v.isolate : false }))
      if (!id) return
      markExplored(id)
      const t = tourIndexOf.get(id)
      if (t !== undefined) setTourStep(t)
    },
    [markExplored, tourIndexOf],
  )

  const index = view.selectedId ? stageIds.indexOf(view.selectedId) : -1
  const step = (delta: number) => {
    const next = Math.min(stageIds.length - 1, Math.max(0, (index < 0 ? -1 : index) + delta))
    goToStage(stageIds[next])
  }

  // Tour auto-play: advance one stage at a time, stop at the end. User-started and
  // pausable at any time (WCAG 2.2.2).
  useEffect(() => {
    if (!autoplay || mode !== 'tour') return
    const id = setTimeout(() => {
      if (tourStep >= lesson.tour.length - 1) setAutoplay(false)
      else goToStage(lesson.tour[tourStep + 1].component)
    }, (AUTOPLAY_SECONDS * 1000) / speed)
    return () => clearTimeout(id)
  }, [autoplay, mode, tourStep, speed, lesson.tour, goToStage])

  const onTab = (m: string) => {
    setMode(m as Mode)
    if (m === 'tour') goToStage(lesson.tour[tourStep].component)
    if (m !== 'tour') setAutoplay(false)
    if (m !== 'challenges' && challenge) exitChallenge()
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
  const selectedPart = spec.parts.find((p) => p.id === view.selectedId)
  const visual = (id: string) => lesson.visuals.find((v) => v.id === id)!
  const verified = verifiedCount(lesson)
  const tour = lesson.tour[tourStep]

  const stagePanel = (withTour: boolean) => (
    <StagePanel
      lesson={lesson}
      component={selected}
      part={selectedPart}
      index={index}
      result={exp.result}
      params={exp.params}
      sources={sources}
      reducedMotion={reducedMotion}
      onStep={step}
      tour={
        withTour
          ? {
              step: tourStep,
              total: lesson.tour.length,
              title: tour.title,
              body: tour.body,
              autoplay,
              speed,
              onToggleAutoplay: () => setAutoplay((a) => !a),
              onSpeed: setSpeed,
            }
          : undefined
      }
    />
  )

  return (
    <Tabs.Root value={mode} onValueChange={onTab} asChild>
      <article className="lesson cine">
        <header className="cine__head">
          <div className="cine__titles">
            <p className="label">LESSON 01 · INGESTION → GENERATION · {lesson.estimated_minutes} MIN</p>
            <h1>
              retrieval-augmented generation,&nbsp;<em>exploded</em>
            </h1>
            <p className="cine__summary">Follow a real RAG pipeline through the machine. Click any part to see what goes in, what comes out, and what breaks without it.</p>
          </div>
          <div className="cine__meta">
            {lesson.status === 'draft' ? (
              <p className="status-pill status-pill--draft" role="note">
                Draft: verification in progress · {verified}/{lesson.claims.length} claims through all three passes
              </p>
            ) : (
              <p className="status-pill status-pill--ok">
                <SealCheck weight="fill" aria-hidden /> Verified: {verified}/{lesson.claims.length} claims through all three passes
              </p>
            )}
            <p className="label">
              EXPLORED {explored.length}/{lesson.components.length} · FIXED {solved.length}/{lesson.challenges.length} · REBUILT {rebuilt ? 'YES' : 'NO'}
            </p>
            <Tabs.List className="cine__modes" aria-label="Mode">
              <Tabs.Trigger className="cine__mode" value="explore">Explore</Tabs.Trigger>
              <Tabs.Trigger className="cine__mode" value="tour">Tour</Tabs.Trigger>
              <Tabs.Trigger className="cine__mode" value="experiment">Experiment</Tabs.Trigger>
              <Tabs.Trigger className="cine__mode" value="challenges">Break &amp; fix</Tabs.Trigger>
              <Tabs.Trigger className="cine__mode" value="rebuild">Rebuild</Tabs.Trigger>
            </Tabs.List>
          </div>
        </header>

        <div className="cine__grid">
          <section className="cine__stage" aria-label="Exploded model">
            <div className="cine__frame">
              <ExplodedView
                spec={spec}
                view={view}
                readouts={readouts}
                mode={renderMode}
                reducedMotion={reducedMotion}
                onSelect={goToStage}
                onToggleIsolate={() => setView((v) => ({ ...v, isolate: !v.isolate }))}
                title="Exploded view of a retrieval-augmented generation pipeline"
                resetSignal={resetSignal}
              />
              <div className="cine__overlay cine__overlay--tl">
                <KindBadge visual={visual('exploded-view')} />
                {exp.result && <span className="label cine__live">LIVE VALUES FROM YOUR LAST RUN</span>}
              </div>
              <div className="cine__overlay cine__overlay--tr">
                <FlowLegend />
              </div>
              <div className="cine__toolbar" role="toolbar" aria-label="View controls">
                <div className="cine__explode">
                  <Slider id="explode" label="Explode" min={0} max={1} step={0.01} value={view.explode} format={(v) => `${Math.round(v * 100)}%`} onChange={(v) => setView((s) => ({ ...s, explode: v }))} />
                </div>
                <Toggle pressed={view.flow} onChange={(f) => setView((s) => ({ ...s, flow: f }))} label="Animate data flow">
                  {view.flow ? <Pause aria-hidden /> : <Play aria-hidden />} Flow
                </Toggle>
                <Toggle pressed={view.linkCards === 'all'} onChange={(on) => setView((s) => ({ ...s, linkCards: on ? 'all' : 'selected' }))} label="Show data on every link">
                  <Info aria-hidden /> Data
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
                <button type="button" className="btn btn--icon" aria-label="Reset camera" title="Reset camera" onClick={() => { goToStage(null); setResetSignal((s) => s + 1) }}>
                  <ArrowsClockwise aria-hidden />
                </button>
              </div>
            </div>
          </section>

          <aside className="cine__panel" aria-label="Lesson activities">
            <Tabs.Content value="explore" className="cine__panel-body">
              {stagePanel(false)}
            </Tabs.Content>
            <Tabs.Content value="tour" className="cine__panel-body">
              {stagePanel(true)}
            </Tabs.Content>
            <Tabs.Content value="experiment" className="cine__panel-body">
              <ExperimentPanel lesson={lesson} {...exp} neuralAvailable={!!config?.embedders.find((e) => e.id === 'neural-local')?.available} />
            </Tabs.Content>
            <Tabs.Content value="challenges" className="cine__panel-body">
              <Challenges
                challenges={lesson.challenges}
                active={challenge}
                solved={solved}
                onCheck={(c) => api.checkChallenge(lesson.id, c.id, exp.params)}
                onStart={startChallenge}
                onExit={exitChallenge}
                onSolved={(id) => {
                  const next = solved.includes(id) ? solved : [...solved, id]
                  setSolved(next)
                  api.saveProgress(lesson.id, { solved_challenges: next }).catch(() => undefined)
                }}
              />
              {challenge && <ExperimentPanel lesson={lesson} {...exp} locked={challenge.locked_params} neuralAvailable={false} />}
            </Tabs.Content>
            <Tabs.Content value="rebuild" className="cine__panel-body">
              <Rebuild
                lesson={lesson}
                solved={rebuilt}
                onSolved={() => {
                  setRebuilt(true)
                  api.saveProgress(lesson.id, { reconstruction_solved: true }).catch(() => undefined)
                }}
              />
            </Tabs.Content>
          </aside>
        </div>

        <StageBar stages={lesson.components} activeId={view.selectedId} explored={explored} onSelect={goToStage} />
        <p className="cine__hints label">
          <span>CLICK ANY PART OR STAGE TO JUMP</span>
          <span>← → MOVE BETWEEN STAGES</span>
          <span>ENTER ISOLATES · ESC CLEARS</span>
        </p>

        <TimingStrip result={exp.result} />

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
    </Tabs.Root>
  )
}

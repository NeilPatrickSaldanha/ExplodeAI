import * as Tabs from '@radix-ui/react-tabs'
import { ArrowsClockwise, CornersOut, Crosshair, Cube, Hand, Info, Pause, Play, Question, SealCheck, Square, Wind } from '@phosphor-icons/react'
import { useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from 'react'
import { api } from '../../../api/client'
import type { Component, Lesson, Source } from '../../../api/types'
import { KindBadge, Slider, Toggle } from '../../../components/controls'
import { ExplodedView, type RenderMode } from '../../../engine/ExplodedView'
import { useReducedMotion } from '../../../engine/hooks'
import type { AssemblySpec, Readouts, ViewState } from '../../../engine/types'
import './cine.css'
import { FlowLegend, type FlowLabels } from './FlowLegend'
import { StageBar } from './StageBar'
import { StagePanel } from './StagePanel'
import { TutorPanel } from '../../../tutor/TutorPanel'
import { Tutorial } from './Tutorial'
import { tutorialSeen } from './tutorialStorage'

export type Mode = 'explore' | 'tour' | 'experiment' | 'challenges' | 'rebuild'

/** Seconds each stage stays on screen during tour auto-play, at 1×. */
const AUTOPLAY_SECONDS = 8

/** Progress handles the lesson's own tabs use to record solved challenges / rebuild. */
export interface ProgressHandles {
  solved: string[]
  rebuilt: boolean
  markSolved: (id: string) => void
  markRebuilt: () => void
  /** Live reduced-motion state (OS setting or the "Calm" toggle). */
  reducedMotion: boolean
}

interface Props {
  lesson: Lesson
  spec: AssemblySpec
  readouts?: Readouts
  /** True once a real run has produced the readouts. */
  live: boolean
  eyebrow: string
  title: ReactNode
  summary: string
  sceneTitle: string
  flowLabels: FlowLabels
  /** What goes in → what comes out, for the selected stage (real data). */
  renderIO: (c: Component) => ReactNode
  /** The "what breaks if removed?" card for the selected stage. */
  renderBreaks: (c: Component) => ReactNode
  /** Experiment, Break & fix and Rebuild tab contents. */
  tabs: (p: ProgressHandles) => { experiment: ReactNode; challenges: ReactNode; rebuild: ReactNode }
  /** Called on every mode change (e.g. to leave an active challenge). */
  onModeChange?: (mode: Mode) => void
  /** Real per-stage timings strip, below the stage bar. */
  timings: ReactNode
}

function verifiedCount(lesson: Lesson) {
  const ok = (s: string) => s === 'passed' || s === 'not_applicable'
  return lesson.claims.filter((c) => ok(c.verification.primary.status) && ok(c.verification.cross_check.status) && ok(c.verification.technical.status)).length
}

/**
 * The cinematic lesson shell shared by every exploded-view lesson: hero scene with
 * flow legend and toolbar, stage panel (Explore / Tour), the lesson's own tabs,
 * the stage bar, timings and sources. Owns stage navigation, tour sync, auto-play
 * and progress, so every lesson behaves the same.
 */
export function CineLesson({ lesson, spec, readouts, live, eyebrow, title, summary, sceneTitle, flowLabels, renderIO, renderBreaks, tabs, onModeChange, timings }: Props) {
  const sources = useMemo(() => new Map<string, Source>(lesson.sources.map((s) => [s.id, s])), [lesson])
  const stageIds = useMemo(() => lesson.components.map((c) => c.id), [lesson])
  // Tour step for each stage, so a click anywhere keeps the tour in sync.
  const tourIndexOf = useMemo(() => new Map(lesson.tour.map((t, i) => [t.component, i])), [lesson])
  const [motionOverride, setMotionOverride] = useState<boolean | null>(null)
  const reducedMotion = useReducedMotion(motionOverride)
  const [renderMode, setRenderMode] = useState<RenderMode>('3d')
  const [view, setView] = useState<ViewState>({ explode: 0, selectedId: null, isolate: false, flow: true, linkCards: 'selected', pan: false })
  const [resetSignal, setResetSignal] = useState(0)
  const [mode, setMode] = useState<Mode>('explore')
  const [tourStep, setTourStep] = useState(0)
  const [autoplay, setAutoplay] = useState(false)
  const [speed, setSpeed] = useState<1 | 2>(1)
  const [explored, setExplored] = useState<string[]>([])
  const [solved, setSolved] = useState<string[]>([])
  const [rebuilt, setRebuilt] = useState(false)
  const [tutorialOpen, setTutorialOpen] = useState(false)
  const replayRef = useRef<HTMLButtonElement>(null)

  // One orchestrated entrance: the machine explodes open, then stage 01 lights up.
  useEffect(() => {
    // Stage 01 is shown, not marked explored: progress only counts the learner's own clicks.
    const id = setTimeout(() => setView((v) => ({ ...v, explode: 1, selectedId: v.selectedId ?? stageIds[0] })), reducedMotion ? 0 : 350)
    return () => clearTimeout(id)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // First visit ever: offer the walkthrough once the scene has opened up.
  useEffect(() => {
    if (tutorialSeen()) return
    const id = setTimeout(() => setTutorialOpen(true), 1200)
    return () => clearTimeout(id)
  }, [])

  useEffect(() => {
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

  // Play from here; on the last step, Play restarts the tour from the first stage.
  const togglePlay = () => {
    if (autoplay) return setAutoplay(false)
    if (tourStep >= lesson.tour.length - 1) goToStage(lesson.tour[0].component)
    setAutoplay(true)
  }

  const onTab = (m: string) => {
    setMode(m as Mode)
    if (m === 'tour') goToStage(lesson.tour[tourStep].component)
    if (m !== 'tour') setAutoplay(false)
    onModeChange?.(m as Mode)
  }

  const progress: ProgressHandles = {
    solved,
    rebuilt,
    reducedMotion,
    markSolved: (id) => {
      const next = solved.includes(id) ? solved : [...solved, id]
      setSolved(next)
      api.saveProgress(lesson.id, { solved_challenges: next }).catch(() => undefined)
    },
    markRebuilt: () => {
      setRebuilt(true)
      api.saveProgress(lesson.id, { reconstruction_solved: true }).catch(() => undefined)
    },
  }
  const tabContent = tabs(progress)

  const selected = lesson.components.find((c) => c.id === view.selectedId)
  const selectedPart = spec.parts.find((p) => p.id === view.selectedId)
  const verified = verifiedCount(lesson)
  const tour = lesson.tour[tourStep]
  const sceneBadge = lesson.visuals.find((v) => v.id === 'exploded-view')

  const stagePanel = (withTour: boolean) => (
    <StagePanel
      lesson={lesson}
      component={selected}
      part={selectedPart}
      index={index}
      io={selected && renderIO(selected)}
      breaks={selected?.breaks_if_removed ? renderBreaks(selected) : null}
      sources={sources}
      reducedMotion={reducedMotion}
      onStep={step}
      onGoTo={goToStage}
      tour={
        withTour
          ? {
              step: tourStep,
              total: lesson.tour.length,
              title: tour.title,
              body: tour.body,
              autoplay,
              dwell: AUTOPLAY_SECONDS / speed,
              speed,
              onToggleAutoplay: togglePlay,
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
            <p className="label">{eyebrow}</p>
            <h1>{title}</h1>
            <p className="cine__summary">{summary}</p>
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
            <button ref={replayRef} type="button" className="btn cine__howto" onClick={() => setTutorialOpen(true)}>
              <Question aria-hidden /> How to use
            </button>
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
                title={sceneTitle}
                resetSignal={resetSignal}
              />
              <div className="cine__overlay cine__overlay--tl">
                {sceneBadge && <KindBadge visual={sceneBadge} />}
                {live && <span className="label cine__live">LIVE VALUES FROM YOUR LAST RUN</span>}
              </div>
              <div className="cine__overlay cine__overlay--tr">
                <FlowLegend labels={flowLabels} />
              </div>
              <div className="cine__toolbar" role="toolbar" aria-label="View controls">
                <div className="cine__explode">
                  <Slider id="explode" label="Explode" min={0} max={1} step={0.01} value={view.explode} format={(v) => `${Math.round(v * 100)}%`} onChange={(v) => setView((s) => ({ ...s, explode: v }))} />
                </div>
                <Toggle pressed={view.flow} onChange={(f) => setView((s) => ({ ...s, flow: f }))} label={view.flow ? 'Pause the data-flow animation' : 'Play the data-flow animation'}>
                  {view.flow ? <Pause aria-hidden /> : <Play aria-hidden />} {view.flow ? 'Flow on' : 'Flow off'}
                </Toggle>
                <Toggle pressed={view.linkCards === 'all'} onChange={(on) => setView((s) => ({ ...s, linkCards: on ? 'all' : 'selected' }))} label="Show data on every link">
                  <Info aria-hidden /> Data
                </Toggle>
                <Toggle
                  pressed={!!view.pan && renderMode === '3d'}
                  disabled={renderMode !== '3d'}
                  onChange={(on) => setView((s) => ({ ...s, pan: on }))}
                  label={renderMode === '3d' ? 'Move: drag to slide the whole diagram instead of rotating it' : 'Move works in the 3D view'}
                >
                  <Hand aria-hidden /> Move
                </Toggle>
                <Toggle
                  pressed={view.isolate}
                  disabled={!view.selectedId}
                  onChange={(i) => setView((s) => ({ ...s, isolate: i && !!s.selectedId }))}
                  label={view.selectedId ? 'Isolate the selected part' : 'Select a stage first, then isolate it'}
                >
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
              {tabContent.experiment}
            </Tabs.Content>
            <Tabs.Content value="challenges" className="cine__panel-body">
              {tabContent.challenges}
            </Tabs.Content>
            <Tabs.Content value="rebuild" className="cine__panel-body">
              {tabContent.rebuild}
            </Tabs.Content>
          </aside>
        </div>

        <StageBar stages={lesson.components} activeId={view.selectedId} explored={explored} onSelect={goToStage} />
        <p className="cine__hints label">
          <span>CLICK ANY PART OR STAGE TO JUMP</span>
          <span>← → MOVE BETWEEN STAGES</span>
          <span>ENTER ISOLATES · ESC CLEARS</span>
        </p>

        {timings}

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
        <TutorPanel
          lessonId={lesson.id}
          lessonNumber={lesson.number}
          stageId={view.selectedId}
          stageLabel={selected?.label ?? null}
          onGoToStage={goToStage}
        />
        {tutorialOpen && (
          <Tutorial
            signals={{ mode, selectedId: view.selectedId, explode: view.explode, autoplay }}
            actions={{
              setMode: (m) => {
                setMode(m)
                if (m === 'tour') goToStage(lesson.tour[tourStep].component)
              },
              stopAutoplay: () => setAutoplay(false),
            }}
            reducedMotion={reducedMotion}
            onClose={() => {
              setTutorialOpen(false)
              replayRef.current?.focus()
            }}
          />
        )}
      </article>
    </Tabs.Root>
  )
}

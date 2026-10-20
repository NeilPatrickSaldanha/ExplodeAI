import { ArrowLeft, ArrowRight, CheckCircle, Circle, X } from '@phosphor-icons/react'
import { useCallback, useEffect, useLayoutEffect, useRef, useState } from 'react'
import type { Mode } from './CineLesson'
import { rememberTutorial } from './tutorialStorage'
import './tutorial.css'

/** What the learner is doing right now, so tasks can notice they happened. */
export interface TutorialSignals {
  mode: Mode
  selectedId: string | null
  explode: number
  autoplay: boolean
}

export interface TutorialActions {
  setMode: (m: Mode) => void
  stopAutoplay: () => void
}

type TaskId = 'rotate' | 'zoom' | 'explode' | 'select' | 'play'

interface Step {
  id: string
  title: string
  body: string
  /** CSS selector of the element to spotlight. No target = centred card. */
  target?: string
  /** Where to put the card relative to the target. */
  place?: 'right' | 'left' | 'below' | 'above'
  task?: { id: TaskId; text: string }
  /** Mode to show before this step. */
  mode?: Mode
  list?: string[]
}

const STEPS: Step[] = [
  {
    id: 'welcome',
    title: 'Welcome to ExplodeAI',
    body: 'A one-minute tour of the controls. You learn by seeing and doing, so a few steps ask you to try something. You can skip any time and replay it later.',
  },
  {
    id: 'rotate',
    title: 'Turn the machine',
    body: 'This 3D model is the system you are learning, pulled apart so every stage is visible. Drag it to rotate it. On a keyboard, focus it and use the arrow keys.',
    target: '.cine__frame',
    place: 'right',
    task: { id: 'rotate', text: 'Drag the model' },
  },
  {
    id: 'zoom',
    title: 'Zoom in and out',
    body: 'Scroll, or pinch on a touch screen, to zoom. The reset button in the toolbar brings the whole machine back into view.',
    target: '.cine__frame',
    place: 'right',
    task: { id: 'zoom', text: 'Scroll or pinch to zoom' },
  },
  {
    id: 'explode',
    title: 'Pull it apart',
    body: 'This slider moves the parts away from each other so you can see how they connect. Drag it, or focus it and use the arrow keys.',
    target: '.cine__explode',
    place: 'above',
    task: { id: 'explode', text: 'Move the Explode slider' },
  },
  {
    id: 'select',
    title: 'Open a stage',
    body: 'Click any part, or any card in the stage bar, to see what goes in, what comes out, and what breaks without it. The right panel explains it step by step.',
    target: '.stagebar',
    place: 'above',
    task: { id: 'select', text: 'Pick a different stage' },
    mode: 'explore',
  },
  {
    id: 'panel',
    title: 'Learn at your own pace',
    body: 'This panel starts simple: what the stage does, an analogy and a small example you can play. Open the sections for the why, the data and the technical detail. Every fact links to its sources.',
    target: '.cine__panel',
    place: 'left',
  },
  {
    id: 'modes',
    title: 'Five ways to learn',
    body: 'Switch modes here. Each one teaches the same system differently.',
    target: '.cine__modes',
    place: 'below',
    list: ['Explore: click around at your own pace', 'Tour: a guided walk through every stage', 'Experiment: run the real code with your own input', 'Break & fix: repair something that is broken', 'Rebuild: put the stages in the right order'],
  },
  {
    id: 'tour',
    title: 'Play the tour',
    body: 'Play moves to the next stage by itself and shows a countdown. Pause stops it where you are. The arrows step manually, and 1× / 2× changes the speed.',
    target: '.spanel__play',
    place: 'left',
    mode: 'tour',
    task: { id: 'play', text: 'Press Play' },
  },
  {
    id: 'toolbar',
    title: 'View controls',
    body: 'Flow animates the data moving between stages (it can be paused). Data shows what travels on every link. Isolate fades everything but the selected stage. 3D / 2D switches views. Calm reduces motion.',
    target: '.cine__toolbar',
    place: 'above',
  },
  {
    id: 'keys',
    title: 'Keyboard and touch',
    body: 'Tab reaches every control. With the model focused, arrow keys move between stages, Enter isolates one and Escape clears it. On phones, tap a stage card instead of dragging.',
    target: '.cine__hints',
    place: 'above',
  },
  {
    id: 'finish',
    title: 'You are ready',
    body: 'Explore, then try the Experiment and Break & fix modes. If you want this tour again, use the “How to use” button at the top of the lesson.',
    mode: 'explore',
  },
]

interface Rect {
  top: number
  left: number
  width: number
  height: number
}

const PAD = 8

function useTargetRect(selector: string | undefined, active: boolean): Rect | null {
  const [rect, setRect] = useState<Rect | null>(null)
  useLayoutEffect(() => {
    if (!active || !selector) return
    let raf = 0
    let last = ''
    const measure = () => {
      const el = document.querySelector(selector)
      if (el) {
        const r = el.getBoundingClientRect()
        const key = `${Math.round(r.top)}:${Math.round(r.left)}:${Math.round(r.width)}:${Math.round(r.height)}`
        if (key !== last) {
          last = key
          setRect({ top: r.top, left: r.left, width: r.width, height: r.height })
        }
      } else if (last !== 'none') {
        last = 'none'
        setRect(null)
      }
      raf = window.setTimeout(measure, 200) as unknown as number
    }
    document.querySelector(selector)?.scrollIntoView({ block: 'center', behavior: 'auto' })
    measure()
    return () => clearTimeout(raf)
  }, [selector, active])
  return selector && active ? rect : null
}

interface Props {
  signals: TutorialSignals
  actions: TutorialActions
  reducedMotion: boolean
  onClose: () => void
}

/**
 * First-run walkthrough: spotlights one control at a time and dims the rest. Some
 * steps ask the learner to try something. Next, Back, Skip and Finish are always
 * available, Escape skips, and the result is remembered so it only auto-opens once.
 */
export function Tutorial({ signals, actions, reducedMotion, onClose }: Props) {
  const [i, setI] = useState(0)
  // Gesture tasks (drag, scroll, pinch) are recorded; the rest are derived from lesson state.
  const [gestures, setGestures] = useState<Set<TaskId>>(new Set())
  const [base, setBase] = useState(signals)
  const step = STEPS[i]
  const last = i === STEPS.length - 1
  const rect = useTargetRect(step.target, true)
  const cardRef = useRef<HTMLDivElement>(null)
  const complete = useCallback((t: TaskId) => setGestures((d) => (d.has(t) ? d : new Set(d).add(t))), [])

  // Entering a step: switch mode if asked and hand focus to the card.
  useEffect(() => {
    if (step.mode && signals.mode !== step.mode) actions.setMode(step.mode)
    cardRef.current?.focus()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [i])

  const derived: Record<string, boolean> = {
    explode: Math.abs(signals.explode - base.explode) > 0.04,
    select: !!signals.selectedId && signals.selectedId !== base.selectedId,
    play: signals.autoplay && !base.autoplay,
  }
  const isDone = (t: TaskId) => gestures.has(t) || !!derived[t]

  // Tasks that are gestures on the 3D scene: dragging and scrolling.
  useEffect(() => {
    const frame = document.querySelector('.cine__frame')
    if (!frame) return
    let down: { x: number; y: number } | null = null
    const onDown = (e: Event) => {
      const p = e as PointerEvent
      down = { x: p.clientX, y: p.clientY }
    }
    const onMove = (e: Event) => {
      const p = e as PointerEvent
      if (down && Math.hypot(p.clientX - down.x, p.clientY - down.y) > 24) complete('rotate')
    }
    const onUp = () => (down = null)
    const onWheel = () => complete('zoom')
    let pinch = 0
    const onTouch = (e: Event) => {
      if ((e as TouchEvent).touches.length === 2 && ++pinch > 3) complete('zoom')
    }
    frame.addEventListener('pointerdown', onDown)
    frame.addEventListener('pointermove', onMove)
    window.addEventListener('pointerup', onUp)
    frame.addEventListener('wheel', onWheel, { passive: true })
    frame.addEventListener('touchmove', onTouch, { passive: true })
    return () => {
      frame.removeEventListener('pointerdown', onDown)
      frame.removeEventListener('pointermove', onMove)
      window.removeEventListener('pointerup', onUp)
      frame.removeEventListener('wheel', onWheel)
      frame.removeEventListener('touchmove', onTouch)
    }
  }, [complete])

  const finish = (how: 'done' | 'skipped') => {
    rememberTutorial(how)
    actions.stopAutoplay()
    actions.setMode('explore')
    onClose()
  }

  const go = (n: number) => {
    setI(n)
    setBase(signals) // each step measures what the learner does from here
  }
  const next = () => (last ? finish('done') : go(i + 1))
  const back = () => go(Math.max(0, i - 1))

  const onKey = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      e.stopPropagation()
      finish('skipped')
    }
    if (e.key === 'Tab') {
      const focusables = cardRef.current?.querySelectorAll<HTMLElement>('button:not([disabled])')
      if (!focusables?.length) return
      const first = focusables[0]
      const lastEl = focusables[focusables.length - 1]
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault()
        lastEl.focus()
      } else if (!e.shiftKey && document.activeElement === lastEl) {
        e.preventDefault()
        first.focus()
      }
    }
  }

  const vw = window.innerWidth
  const vh = window.innerHeight
  const sheet = vw < 640
  const hole = rect && { top: rect.top - PAD, left: rect.left - PAD, width: rect.width + PAD * 2, height: rect.height + PAD * 2 }
  const cardStyle: React.CSSProperties = {}
  if (!sheet && hole) {
    const W = 340
    const H = 300
    const clampX = (x: number) => Math.min(Math.max(12, x), vw - W - 12)
    const clampY = (y: number) => Math.min(Math.max(12, y), vh - H - 12)
    const place = step.place ?? 'below'
    if (place === 'right' && hole.left + hole.width + W + 24 < vw) {
      cardStyle.left = hole.left + hole.width + 12
      cardStyle.top = clampY(hole.top + 12)
    } else if (place === 'left' && hole.left - W - 24 > 0) {
      cardStyle.left = hole.left - W - 12
      cardStyle.top = clampY(hole.top + 12)
    } else if (place === 'above' && hole.top - H - 12 > 0) {
      cardStyle.left = clampX(hole.left)
      cardStyle.top = hole.top - H - 12
    } else if (hole.top + hole.height + H + 24 < vh) {
      cardStyle.left = clampX(hole.left)
      cardStyle.top = hole.top + hole.height + 12
    } else {
      // No room around it: sit inside the top-left of the highlighted area.
      cardStyle.left = clampX(hole.left + 16)
      cardStyle.top = clampY(hole.top + 16)
    }
  }
  const centred = !hole && !sheet

  const taskDone = step.task ? isDone(step.task.id) : false

  return (
    <div className="tut" role="presentation">
      {hole ? (
        <>
          {/* Four panels dim and block everything except the highlighted control. */}
          <div className="tut__dim" style={{ top: 0, left: 0, right: 0, height: Math.max(0, hole.top) }} />
          <div className="tut__dim" style={{ top: hole.top + hole.height, left: 0, right: 0, bottom: 0 }} />
          <div className="tut__dim" style={{ top: hole.top, left: 0, width: Math.max(0, hole.left), height: hole.height }} />
          <div className="tut__dim" style={{ top: hole.top, left: hole.left + hole.width, right: 0, height: hole.height }} />
          <div className={`tut__ring${reducedMotion ? '' : ' is-animated'}`} style={{ top: hole.top, left: hole.left, width: hole.width, height: hole.height }} />
        </>
      ) : (
        <div className="tut__dim" style={{ inset: 0 }} />
      )}
      <div
        ref={cardRef}
        className={`tut__card${sheet ? ' tut__card--sheet' : ''}${centred ? ' tut__card--center' : ''}`}
        style={cardStyle}
        role="dialog"
        aria-modal="true"
        aria-labelledby="tut-title"
        aria-describedby="tut-body"
        tabIndex={-1}
        onKeyDown={onKey}
      >
        <div className="tut__top">
          <span className="label">
            HOW TO USE · {i + 1} OF {STEPS.length}
          </span>
          <button type="button" className="btn btn--icon" aria-label="Skip the tutorial" title="Skip (Esc)" onClick={() => finish('skipped')}>
            <X aria-hidden />
          </button>
        </div>
        <h2 id="tut-title" className="tut__title">
          {step.title}
        </h2>
        <p id="tut-body" className="tut__body">
          {step.body}
        </p>
        {step.list && (
          <ul className="tut__list">
            {step.list.map((l) => (
              <li key={l}>{l}</li>
            ))}
          </ul>
        )}
        {step.task && (
          <p className={`tut__task${taskDone ? ' is-done' : ''}`} role="status">
            {taskDone ? <CheckCircle weight="fill" aria-hidden /> : <Circle aria-hidden />}
            {taskDone ? 'Nice, that worked.' : `Try it: ${step.task.text}`}
          </p>
        )}
        <progress className="tut__progress" max={STEPS.length} value={i + 1} aria-label="Tutorial progress" />
        <div className="tut__actions">
          <button type="button" className="btn" onClick={back} disabled={i === 0}>
            <ArrowLeft aria-hidden /> Back
          </button>
          {!last && (
            <button type="button" className="btn tut__skip" onClick={() => finish('skipped')}>
              Skip
            </button>
          )}
          <button type="button" className="btn tut__next" onClick={next} data-primary={!step.task || taskDone ? 'true' : 'false'}>
            {last ? 'Finish' : i === 0 ? 'Start' : 'Next'} {!last && <ArrowRight aria-hidden />}
          </button>
        </div>
      </div>
    </div>
  )
}

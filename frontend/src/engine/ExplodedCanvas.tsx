import { ContactShadows, OrbitControls } from '@react-three/drei'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { useEffect, useMemo, useRef, useState, type RefObject } from 'react'
import { MOUSE, TOUCH, Vector3, type PerspectiveCamera } from 'three'
import type { OrbitControls as OrbitControlsImpl } from 'three-stdlib'
import { FOV, fitView, viewDirFor, type FitPoint } from './camera'
import { scenePalette } from './colors'
import { useThemeVersion } from './hooks'
import { LabelProjector, type LabelAnchor } from './LabelLayer'
import { Links3D } from './Links3D'
import { bounds, labelAnchor, linkControlPoint, linkEnd, neighbours, partPosition, quadBezier } from './math'
import { Part3D } from './Part3D'
import { StudioLight } from './StudioLight'
import { linkKey, type AssemblySpec, type Readouts, type Vec3, type ViewState } from './types'

export interface ExplodedCanvasProps {
  spec: AssemblySpec
  view: ViewState
  readouts?: Readouts
  reducedMotion: boolean
  onSelect: (id: string | null) => void
  ariaLabel: string
  /** Bump to re-frame the camera on the whole assembly. */
  resetSignal?: number
}

/** Smoothly follow a target value (snaps when motion is reduced). */
function useAnimated(target: number, reduced: boolean): number {
  const [value, setValue] = useState(target)
  const valueRef = useRef(target)
  useEffect(() => {
    if (reduced) {
      valueRef.current = target
      return
    }
    let raf = 0
    const tick = () => {
      const v = valueRef.current
      const next = Math.abs(target - v) < 0.002 ? target : v + (target - v) * 0.14
      valueRef.current = next
      setValue(next)
      if (next !== target) raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
  }, [target, reduced])
  return reduced ? target : value
}

function CameraRig({
  goal,
  reduced,
  resetSignal,
  framePoints,
  labelAnchors,
  elements,
  center,
  focusKey,
}: {
  goal: Vec3
  reduced: boolean
  resetSignal?: number
  framePoints: Vec3[]
  /** Where each part's label hangs at full explosion, so the frame can leave room for the label cards. */
  labelAnchors: { id: string; at: Vec3; below?: boolean }[]
  elements: RefObject<Map<string, HTMLElement>>
  center: Vec3
  /** Changes when the selected stage changes: the only time the camera drifts towards a goal. */
  focusKey: string | null
}) {
  const controls = useThree((s) => s.controls) as OrbitControlsImpl | null
  const camera = useThree((s) => s.camera) as PerspectiveCamera
  const gl = useThree((s) => s.gl)
  const size = useThree((s) => s.size)
  const invalidate = useThree((s) => s.invalidate)
  // The selection can nudge the aim by `goal - center`; the framing's own centre is the baseline.
  const lean = useMemo(() => new Vector3(...goal).sub(new Vector3(...center)), [goal, center])
  const goalVec = useMemo(() => new Vector3(), [])
  // The camera eases towards the selected stage once, then leaves the view alone, so a pan sticks.
  const settling = useRef(true)
  // Where the framed model sits, so the camera can lean from here and come back to it.
  const home = useRef<Vector3>(new Vector3(...center))
  useEffect(() => {
    settling.current = true
  }, [focusKey, resetSignal])
  useEffect(() => {
    if (!controls) return
    const stop = () => {
      settling.current = false
    }
    controls.addEventListener('start', stop)
    return () => controls.removeEventListener('start', stop)
  }, [controls])

  useEffect(() => {
    // Leave ~100px either side for the HTML labels that sit on the outermost parts.
    const halfW = Math.max(size.width, 200) / 2
    const marginX = Math.max(0.6, 1 - 14 / halfW)
    const aspect = size.width / Math.max(size.height, 1)
    // The top badges and the bottom view toolbar cover part of the canvas: frame inside what is left,
    // and centre the model in that space rather than in the whole canvas.
    const padTop = 75
    // The toolbar wraps onto a second row on narrower screens, so measure how far up it reaches.
    const frame = gl.domElement.closest('.cine__frame') ?? gl.domElement.parentElement?.parentElement
    const bar = frame?.querySelector('[role="toolbar"]')
    const canvasBox = gl.domElement.getBoundingClientRect()
    const padBottom = bar ? Math.max(70, canvasBox.bottom - bar.getBoundingClientRect().top + 18) : 100
    const h = Math.max(size.height, 200)
    const marginY = Math.min(0.9, 1 - (padTop + padBottom) / h)
    const centerY = (padBottom - padTop) / h
    // Each label card is centred on its anchor and hangs above it. Use its real size, so the cards at
    // the edges stay inside the canvas and the visible extent, not just the parts, is what gets centred.
    const labelPoints: FitPoint[] = labelAnchors.map((a) => {
      const el = elements.current?.get(a.id)
      const w = el?.offsetWidth || 190
      const lh = el?.offsetHeight || 62
      const pad = lh / (h / 2)
      return a.below ? { at: a.at, padX: (w / 2 + 6) / halfW, padBottom: pad } : { at: a.at, padX: (w / 2 + 6) / halfW, padTop: pad }
    })
    const fit = fitView([...framePoints, ...labelPoints], center, aspect, { marginX, marginY, centerY })
    home.current.set(...fit.target)
    camera.position.copy(home.current).addScaledVector(viewDirFor(aspect), fit.distance)
    if (controls) {
      controls.target.copy(home.current)
      controls.update()
    }
    invalidate()
    // Re-frame on explicit reset, first mount, or a viewport size change.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [resetSignal, controls, size.width, size.height])

  useFrame(() => {
    if (!controls || !settling.current) return
    goalVec.copy(home.current).add(lean)
    if (controls.target.distanceTo(goalVec) < 0.005) return
    if (reduced) controls.target.copy(goalVec)
    else controls.target.lerp(goalVec, 0.09)
    controls.update()
    invalidate()
  })
  return null
}

export function ExplodedCanvas({ spec, view, readouts, reducedMotion, onSelect, ariaLabel, resetSignal }: ExplodedCanvasProps) {
  const themeVersion = useThemeVersion()
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const palette = useMemo(() => scenePalette(), [themeVersion])
  const t = useAnimated(view.explode, reducedMotion)

  const positions = useMemo(
    () => Object.fromEntries(spec.parts.map((p) => [p.id, partPosition(p, t)])) as Record<string, Vec3>,
    [spec, t],
  )
  // Frame for full explosion so the camera never needs to move as parts separate.
  const frame = useMemo(() => bounds(spec, 1), [spec])
  // Frame on every part's footprint and label height at full explosion.
  const framePoints = useMemo(
    () =>
      spec.parts.flatMap((p) => {
        const [x, y, z] = partPosition(p, 1)
        const [w, h, d] = p.size
        return [[x - w / 2, y, z - d / 2], [x + w / 2, y + h + 0.9, z + d / 2]] as Vec3[]
      }),
    [spec],
  )
  // Models in the front row hang their labels below them, towards the viewer, so labels never cover models.
  const below = useMemo(() => {
    const mid = bounds(spec, 1).center[2]
    return new Set(spec.parts.filter((p) => p.model && partPosition(p, 1)[2] > mid).map((p) => p.id))
  }, [spec])
  // Label anchors at full explosion (the same offsets the live labels use), for framing the camera.
  const labelAnchorsFull = useMemo(
    () => spec.parts.map((p) => ({ id: p.id, at: labelAnchor(partPosition(p, 1), p, 0.8, below.has(p.id)), below: below.has(p.id) })),
    [spec, below],
  )
  const [sceneWidth, setSceneWidth] = useState(1000)
  const compact = sceneWidth < 640
  // Phones: numbered markers (matching the numbered part list); full label when selected.
  const tiny = sceneWidth < 480
  const active = useMemo(() => {
    if (!view.isolate || !view.selectedId) return null
    return new Set([view.selectedId, ...neighbours(spec, view.selectedId)])
  }, [spec, view.isolate, view.selectedId])

  // No lean toward the selected part: any shift moves the tight framing's edge parts out of view.
  const FOCUS_PULL = 0
  const sel = view.selectedId ? positions[view.selectedId] : undefined
  const goal: Vec3 = sel
    ? [0, 1, 2].map((i) => frame.center[i] + (sel[i] - frame.center[i]) * FOCUS_PULL) as Vec3
    : frame.center
  const animating = view.flow && !reducedMotion
  const partInfo = useMemo(() => Object.fromEntries(spec.parts.map((p) => [p.id, { size: p.size, model: p.model }])), [spec])
  // Lessons whose stages are real 3D models get studio lighting and soft shadows for their materials.
  const hasModels = spec.parts.some((p) => p.model)

  // Label anchors: a callout above each part, plus data cards at link midpoints.
  const cardMode = view.linkCards ?? 'selected'
  const linkLabels = tiny || cardMode === 'none'
    ? []
    : spec.links.filter((l) => cardMode === 'all' || (!!view.selectedId && (l.source === view.selectedId || l.target === view.selectedId)))
  const anchors = useRef<LabelAnchor[]>([])
  anchors.current = [
    ...spec.parts.map((p) => ({ id: p.id, at: labelAnchor(positions[p.id], p, 0.55 + t * 0.25, below.has(p.id)), below: below.has(p.id) })),
    ...linkLabels.map((l) => {
      const a = positions[l.source]
      const b = positions[l.target]
      const s = linkEnd(a, b, partInfo[l.source])
      const e = linkEnd(b, a, partInfo[l.target])
      const m = quadBezier(s, linkControlPoint(s, e), e, 0.5)
      return { id: linkKey(l), at: [m[0], m[1] + 0.12, m[2]] as Vec3 }
    }),
  ]
  const elements = useRef(new Map<string, HTMLElement>())
  const register = (id: string) => (el: HTMLElement | null) => {
    if (el) elements.current.set(id, el)
    else elements.current.delete(id)
  }

  return (
    <div className="scene" data-pan={view.pan ? 'true' : undefined}>
      <Canvas
        frameloop="demand"
        dpr={[1, 2]}
        camera={{ fov: FOV, near: 0.1, far: 300, position: [1, 14, 20] }}
        onPointerMissed={() => onSelect(null)}
        aria-label={ariaLabel}
        role="img"
      >
        <color attach="background" args={[palette.paper]} />
        <ambientLight intensity={hasModels ? 0.25 : 0.55} />
        <directionalLight position={[6, 10, 6]} intensity={hasModels ? 0.9 : 1.1} />
        <directionalLight position={[-8, 4, -6]} intensity={0.35} />
        {hasModels && <StudioLight />}
        {/* Drawn once, and again only when the parts move (the key changes), not on every frame. */}
        {hasModels && <ContactShadows key={Math.round(t * 20)} frames={1} position={[frame.center[0], 0.001, frame.center[2]]} scale={40} resolution={512} blur={2.4} far={2.5} opacity={0.7} />}
        <FrameLimiter active={animating} fps={30} />
        <gridHelper args={[40, 40, palette.muted, palette.edge]} position={[0, -0.02, 0]} material-transparent material-opacity={0.12} />
        {spec.parts.map((p) => (
          <Part3D
            key={p.id}
            part={p}
            at={positions[p.id]}
            explode={t}
            selected={view.selectedId === p.id}
            dimmed={active !== null && !active.has(p.id)}
            palette={palette}
            onSelect={onSelect}
          />
        ))}
        <Links3D links={spec.links} positions={positions} flow={view.flow} reducedMotion={reducedMotion} activeIds={active} focusId={view.selectedId} palette={palette} parts={partInfo} />
        <OrbitControls
          makeDefault
          enableDamping={!reducedMotion}
          minDistance={3}
          maxDistance={60}
          maxPolarAngle={Math.PI * 0.47}
          screenSpacePanning
          // Hand mode: a plain drag slides the diagram. Otherwise a plain drag rotates it, right-drag or
          // Shift-drag slides it, and two fingers always pinch to zoom and slide.
          mouseButtons={{ LEFT: view.pan ? MOUSE.PAN : MOUSE.ROTATE, MIDDLE: MOUSE.DOLLY, RIGHT: view.pan ? MOUSE.ROTATE : MOUSE.PAN }}
          touches={{ ONE: view.pan ? TOUCH.PAN : TOUCH.ROTATE, TWO: TOUCH.DOLLY_PAN }}
        />
        <CameraRig goal={goal} reduced={reducedMotion} resetSignal={resetSignal} framePoints={framePoints} labelAnchors={labelAnchorsFull} elements={elements} center={frame.center} focusKey={view.selectedId} />
        <SizeReporter onWidth={setSceneWidth} />
        <LabelProjector anchors={anchors} elements={elements} />
      </Canvas>
      <div className="scene__labels" aria-hidden="true">
        {spec.parts.map((p, i) => {
          const dim = active !== null && !active.has(p.id)
          const isSel = view.selectedId === p.id
          const num = p.number ?? String(i + 1).padStart(2, '0')
          const readout = readouts?.parts?.[p.id]
          const cls = ['callout part-label', compact && 'is-compact', isSel && 'is-selected', dim && 'is-dim', p.prop && 'is-prop'].filter(Boolean).join(' ')
          if (tiny && !isSel && !p.prop) {
            return (
              <div key={p.id} ref={register(p.id)} className={`${cls} is-marker`}>
                <span className="callout__num">{num}</span>
              </div>
            )
          }
          return (
            <div key={p.id} ref={register(p.id)} className={cls}>
              {!p.prop && <span className="callout__num">{num}</span>}
              <span className="callout__body">
                <span className="callout__name">{p.label}</span>
                {p.subtitle && !compact && isSel && <span className="callout__sub">{p.subtitle}</span>}
                {readout && (!compact || isSel || (p.prop && !tiny)) && <span className="callout__readout">{readout}</span>}
              </span>
            </div>
          )
        })}
        {linkLabels.map((l) => (
          <div key={linkKey(l)} ref={register(linkKey(l))} className={`link-card link-card--${l.kind ?? 'document'}`}>
            <span className="link-card__label">{l.label}</span>
            {readouts?.links?.[linkKey(l)] && <b>{readouts.links[linkKey(l)]}</b>}
          </div>
        ))}
      </div>
    </div>
  )
}

/** Redraw at a steady 30 frames a second while the flow animation runs, instead of as fast as the display allows. */
function FrameLimiter({ active, fps }: { active: boolean; fps: number }) {
  const invalidate = useThree((s) => s.invalidate)
  useEffect(() => {
    if (!active) return
    const id = window.setInterval(invalidate, 1000 / fps)
    return () => window.clearInterval(id)
  }, [active, fps, invalidate])
  return null
}

function SizeReporter({ onWidth }: { onWidth: (w: number) => void }) {
  const width = useThree((s) => s.size.width)
  useEffect(() => onWidth(width), [width, onWidth])
  return null
}

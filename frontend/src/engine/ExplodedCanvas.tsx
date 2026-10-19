import { OrbitControls } from '@react-three/drei'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { useEffect, useMemo, useRef, useState } from 'react'
import { Vector3, type PerspectiveCamera } from 'three'
import type { OrbitControls as OrbitControlsImpl } from 'three-stdlib'
import { FOV, fitDistance, viewDirFor } from './camera'
import { scenePalette } from './colors'
import { useThemeVersion } from './hooks'
import { LabelProjector, type LabelAnchor } from './LabelLayer'
import { Links3D } from './Links3D'
import { bounds, linkControlPoint, neighbours, partPosition, quadBezier } from './math'
import { Part3D } from './Part3D'
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

function CameraRig({ goal, reduced, resetSignal, framePoints, center }: { goal: Vec3; reduced: boolean; resetSignal?: number; framePoints: Vec3[]; center: Vec3 }) {
  const controls = useThree((s) => s.controls) as OrbitControlsImpl | null
  const camera = useThree((s) => s.camera) as PerspectiveCamera
  const size = useThree((s) => s.size)
  const invalidate = useThree((s) => s.invalidate)
  const goalVec = useMemo(() => new Vector3(...goal), [goal])

  useEffect(() => {
    // Leave ~70px either side for the HTML labels that sit on the outermost parts.
    const margin = Math.min(0.86, 1 - 140 / Math.max(size.width, 200))
    const aspect = size.width / Math.max(size.height, 1)
    const d = fitDistance(framePoints, center, aspect, margin)
    camera.position.set(...center).addScaledVector(viewDirFor(aspect), d)
    if (controls) {
      controls.target.set(...center)
      controls.update()
    }
    invalidate()
    // Re-frame on explicit reset, first mount, or a viewport size change.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [resetSignal, controls, size.width, size.height])

  useFrame(() => {
    if (!controls) return
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
  const [sceneWidth, setSceneWidth] = useState(1000)
  const compact = sceneWidth < 640
  // Phones: numbered markers (matching the numbered part list); full label when selected.
  const tiny = sceneWidth < 480
  const active = useMemo(() => {
    if (!view.isolate || !view.selectedId) return null
    return new Set([view.selectedId, ...neighbours(spec, view.selectedId)])
  }, [spec, view.isolate, view.selectedId])

  // Lean the camera a little toward the selected part, but keep the whole system in frame.
  const FOCUS_PULL = 0.28
  const sel = view.selectedId ? positions[view.selectedId] : undefined
  const goal: Vec3 = sel
    ? [0, 1, 2].map((i) => frame.center[i] + (sel[i] - frame.center[i]) * FOCUS_PULL) as Vec3
    : frame.center
  const animating = view.flow && !reducedMotion

  // Label anchors: a callout above each part, plus data cards at link midpoints.
  const cardMode = view.linkCards ?? 'selected'
  const linkLabels = tiny || cardMode === 'none'
    ? []
    : spec.links.filter((l) => cardMode === 'all' || (!!view.selectedId && (l.source === view.selectedId || l.target === view.selectedId)))
  const anchors = useRef<LabelAnchor[]>([])
  anchors.current = [
    ...spec.parts.map((p) => {
      const at = positions[p.id]
      return { id: p.id, at: [at[0], at[1] + p.size[1] + 0.55 + t * 0.25, at[2]] as Vec3 }
    }),
    ...linkLabels.map((l) => {
      const a = positions[l.source]
      const b = positions[l.target]
      const s: Vec3 = [a[0], a[1] + 0.25, a[2]]
      const e: Vec3 = [b[0], b[1] + 0.25, b[2]]
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
    <div className="scene">
      <Canvas
        frameloop={animating ? 'always' : 'demand'}
        dpr={[1, 2]}
        camera={{ fov: FOV, near: 0.1, far: 300, position: [1, 14, 20] }}
        onPointerMissed={() => onSelect(null)}
        aria-label={ariaLabel}
        role="img"
      >
        <color attach="background" args={[palette.paper]} />
        <ambientLight intensity={0.55} />
        <directionalLight position={[6, 10, 6]} intensity={1.1} />
        <directionalLight position={[-8, 4, -6]} intensity={0.35} />
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
        <Links3D links={spec.links} positions={positions} flow={view.flow} reducedMotion={reducedMotion} activeIds={active} focusId={view.selectedId} palette={palette} />
        <OrbitControls makeDefault enableDamping={!reducedMotion} minDistance={3} maxDistance={60} maxPolarAngle={Math.PI * 0.47} />
        <CameraRig goal={goal} reduced={reducedMotion} resetSignal={resetSignal} framePoints={framePoints} center={frame.center} />
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
                {p.subtitle && !compact && <span className="callout__sub">{p.subtitle}</span>}
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

function SizeReporter({ onWidth }: { onWidth: (w: number) => void }) {
  const width = useThree((s) => s.size.width)
  useEffect(() => onWidth(width), [width, onWidth])
  return null
}

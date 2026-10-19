import { lazy, Suspense, useCallback, useRef, type KeyboardEvent } from 'react'
import './engine.css'
import { FlatDiagram } from './FlatDiagram'
import { hasWebGL } from './hooks'
import { stepIndex } from './math'
import type { AssemblySpec, Readouts, ViewState } from './types'

const ExplodedCanvas = lazy(() => import('./ExplodedCanvas').then((m) => ({ default: m.ExplodedCanvas })))

export type RenderMode = '3d' | '2d'

interface Props {
  spec: AssemblySpec
  view: ViewState
  readouts?: Readouts
  mode: RenderMode
  reducedMotion: boolean
  onSelect: (id: string | null) => void
  onToggleIsolate: () => void
  title: string
  resetSignal?: number
}

/**
 * Engine entry point. Chooses 3D or 2D, and adds keyboard control to the scene:
 * ←/→ cycle parts, Enter isolates, Esc clears. The same actions are available
 * from the part list beside the scene, so nothing depends on pointer input.
 */
export function ExplodedView({ spec, view, readouts, mode, reducedMotion, onSelect, onToggleIsolate, title, resetSignal }: Props) {
  const use3d = mode === '3d' && hasWebGL()
  const ref = useRef<HTMLDivElement>(null)

  const onKeyDown = useCallback(
    (e: KeyboardEvent) => {
      const ids = spec.parts.filter((p) => !p.prop).map((p) => p.id)
      const i = view.selectedId ? ids.indexOf(view.selectedId) : -1
      if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
        e.preventDefault()
        onSelect(ids[stepIndex(i, 1, ids.length)])
      } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
        e.preventDefault()
        onSelect(ids[stepIndex(i, -1, ids.length)])
      } else if (e.key === 'Enter' && view.selectedId) {
        e.preventDefault()
        onToggleIsolate()
      } else if (e.key === 'Escape') {
        onSelect(null)
      }
    },
    [spec, view.selectedId, onSelect, onToggleIsolate],
  )

  const selected = spec.parts.find((p) => p.id === view.selectedId)

  return (
    <div
      ref={ref}
      className="exploded-view"
      tabIndex={use3d ? 0 : -1}
      onKeyDown={use3d ? onKeyDown : undefined}
      aria-label={`${title}. Use arrow keys to move between parts, Enter to isolate, Escape to clear.`}
      aria-describedby="exploded-view-status"
      data-mode={use3d ? '3d' : '2d'}
    >
      {use3d ? (
        <Suspense fallback={<div className="exploded-view__loading label">Loading 3D view…</div>}>
          <ExplodedCanvas
            spec={spec}
            view={view}
            readouts={readouts}
            reducedMotion={reducedMotion}
            onSelect={onSelect}
            ariaLabel={title}
            resetSignal={resetSignal}
          />
        </Suspense>
      ) : (
        <FlatDiagram spec={spec} view={view} readouts={readouts} onSelect={onSelect} title={title} />
      )}
      <p id="exploded-view-status" className="visually-hidden" aria-live="polite">
        {selected ? `${selected.label} selected${view.isolate ? ', isolated' : ''}.` : 'No part selected.'}
      </p>
      {mode === '3d' && !use3d && (
        <p className="exploded-view__note label">WebGL unavailable — showing the 2D diagram.</p>
      )}
    </div>
  )
}

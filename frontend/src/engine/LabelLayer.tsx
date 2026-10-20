import { useFrame, useThree } from '@react-three/fiber'
import type { RefObject } from 'react'
import { Vector3 } from 'three'
import type { Vec3 } from './types'

export interface LabelAnchor {
  id: string
  at: Vec3
}

/**
 * Lives inside the Canvas. After each rendered frame, projects every anchor to
 * screen space and moves its DOM label with a transform — no React re-render,
 * no nested React roots. Labels behind the camera are hidden.
 */
export function LabelProjector({
  anchors,
  elements,
}: {
  anchors: RefObject<LabelAnchor[]>
  elements: RefObject<Map<string, HTMLElement>>
}) {
  const camera = useThree((s) => s.camera)
  const size = useThree((s) => s.size)
  const v = new Vector3()
  useFrame(() => {
    for (const a of anchors.current ?? []) {
      const el = elements.current?.get(a.id)
      if (!el) continue
      v.set(a.at[0], a.at[1], a.at[2]).project(camera)
      const visible = v.z < 1 && Math.abs(v.x) < 1.2 && Math.abs(v.y) < 1.2
      // Keep the whole label inside the canvas, whatever the framing.
      const half = el.offsetWidth / 2 + 6
      const raw = ((v.x + 1) / 2) * size.width
      const x = size.width > half * 2 ? Math.min(Math.max(raw, half), size.width - half) : raw
      const y = ((1 - v.y) / 2) * size.height
      el.style.transform = `translate(${x.toFixed(1)}px, ${y.toFixed(1)}px) translate(-50%, -100%)`
      el.style.visibility = visible ? 'visible' : 'hidden'
    }
  })
  return null
}

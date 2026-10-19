import { Line } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import { useMemo, useRef } from 'react'
import type { Mesh } from 'three'
import type { ScenePalette } from './colors'
import { linkControlPoint, quadBezier } from './math'
import type { LinkSpec, Vec3 } from './types'
import { linkKey } from './types'

interface Props {
  links: LinkSpec[]
  positions: Record<string, Vec3>
  flow: boolean
  reducedMotion: boolean
  activeIds: Set<string> | null
  palette: ScenePalette
}

const PACKETS_PER_LINK = 3

export function Links3D({ links, positions, flow, reducedMotion, activeIds, palette }: Props) {
  return (
    <>
      {links.map((link) => {
        const a = positions[link.source]
        const b = positions[link.target]
        if (!a || !b) return null
        const active = !activeIds || (activeIds.has(link.source) && activeIds.has(link.target))
        return (
          <OneLink
            key={linkKey(link)}
            a={a}
            b={b}
            animate={flow && !reducedMotion && active}
            dim={!active}
            palette={palette}
          />
        )
      })}
    </>
  )
}

function OneLink({
  a,
  b,
  animate,
  dim,
  palette,
}: {
  a: Vec3
  b: Vec3
  animate: boolean
  dim: boolean
  palette: ScenePalette
}) {
  const lift = (p: Vec3): Vec3 => [p[0], p[1] + 0.25, p[2]]
  const start = lift(a)
  const end = lift(b)
  const ctrl = linkControlPoint(start, end)
  const points = useMemo(
    () => Array.from({ length: 33 }, (_, i) => quadBezier(start, ctrl, end, i / 32)),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [start.join(), end.join()],
  )
  const packets = useRef<(Mesh | null)[]>([])
  const arrowAt = quadBezier(start, ctrl, end, 0.86)

  useFrame(({ clock }) => {
    if (!animate) return
    const t = clock.getElapsedTime() * 0.35
    packets.current.forEach((m, i) => {
      if (!m) return
      const u = (t + i / PACKETS_PER_LINK) % 1
      const p = quadBezier(start, ctrl, end, u)
      m.position.set(p[0], p[1], p[2])
    })
  })

  return (
    <group>
      <Line points={points} color={dim ? palette.muted : palette.flow} lineWidth={dim ? 1 : 1.6} transparent opacity={dim ? 0.2 : 0.75} />
      {animate ? (
        Array.from({ length: PACKETS_PER_LINK }, (_, i) => (
          <mesh key={i} ref={(m) => { packets.current[i] = m }}>
            <boxGeometry args={[0.09, 0.09, 0.09]} />
            <meshBasicMaterial color={palette.flow} />
          </mesh>
        ))
      ) : (
        !dim && (
          // Reduced motion / paused: a static direction marker instead of moving packets.
          <mesh position={arrowAt}>
            <octahedronGeometry args={[0.07]} />
            <meshBasicMaterial color={palette.flow} />
          </mesh>
        )
      )}
    </group>
  )
}

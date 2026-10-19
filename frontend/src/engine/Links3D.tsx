import { Line } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import { useMemo, useRef } from 'react'
import type { Mesh } from 'three'
import type { ScenePalette } from './colors'
import { linkControlPoint, quadBezier } from './math'
import type { FlowKind, LinkSpec, Vec3 } from './types'
import { linkKey } from './types'

interface Props {
  links: LinkSpec[]
  positions: Record<string, Vec3>
  flow: boolean
  reducedMotion: boolean
  /** Isolation: links outside this set fade right back. */
  activeIds: Set<string> | null
  /** Links touching this part are drawn brighter and faster. */
  focusId?: string | null
  palette: ScenePalette
}

/**
 * Line style and packet shape per flow kind, so the three flows read apart even
 * without colour: solid + cubes (text), dashed + spheres (vectors), dotted +
 * diamonds (the user's question).
 */
const STYLE: Record<FlowKind, { dash: number; gap: number; packets: number; speed: number }> = {
  document: { dash: 0, gap: 0, packets: 3, speed: 0.32 },
  vector: { dash: 0.16, gap: 0.1, packets: 4, speed: 0.42 },
  query: { dash: 0.05, gap: 0.09, packets: 3, speed: 0.38 },
}

function flowColor(kind: FlowKind, p: ScenePalette) {
  return kind === 'vector' ? p.flowVector : kind === 'query' ? p.flowQuery : p.flow
}

export function Links3D({ links, positions, flow, reducedMotion, activeIds, focusId, palette }: Props) {
  return (
    <>
      {links.map((link) => {
        const a = positions[link.source]
        const b = positions[link.target]
        if (!a || !b) return null
        const active = !activeIds || (activeIds.has(link.source) && activeIds.has(link.target))
        const focused = !!focusId && (link.source === focusId || link.target === focusId)
        return (
          <OneLink
            key={linkKey(link)}
            a={a}
            b={b}
            kind={link.kind ?? 'document'}
            animate={flow && !reducedMotion && active}
            dim={!active}
            focused={focused}
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
  kind,
  animate,
  dim,
  focused,
  palette,
}: {
  a: Vec3
  b: Vec3
  kind: FlowKind
  animate: boolean
  dim: boolean
  focused: boolean
  palette: ScenePalette
}) {
  const style = STYLE[kind]
  const color = dim ? palette.muted : flowColor(kind, palette)
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
  const speed = style.speed * (focused ? 1.6 : 1)

  useFrame(({ clock }) => {
    if (!animate) return
    const t = clock.getElapsedTime() * speed
    packets.current.forEach((m, i) => {
      if (!m) return
      const u = (t + i / style.packets) % 1
      const p = quadBezier(start, ctrl, end, u)
      m.position.set(p[0], p[1], p[2])
    })
  })

  const size = focused ? 0.11 : 0.085
  const packet = (i: number) => (
    <mesh key={i} ref={(m) => { packets.current[i] = m }}>
      {kind === 'vector' ? (
        <sphereGeometry args={[size * 0.6, 12, 12]} />
      ) : kind === 'query' ? (
        <octahedronGeometry args={[size * 0.75]} />
      ) : (
        <boxGeometry args={[size, size, size]} />
      )}
      <meshBasicMaterial color={color} />
    </mesh>
  )

  return (
    <group>
      {focused && !dim && (
        // Soft wide underlay so the active paths read as "lit".
        <Line points={points} color={color} lineWidth={7} transparent opacity={0.16} />
      )}
      <Line
        points={points}
        color={color}
        lineWidth={dim ? 1 : focused ? 2.6 : 1.6}
        transparent
        opacity={dim ? 0.2 : focused ? 1 : 0.7}
        dashed={style.dash > 0}
        dashSize={style.dash || undefined}
        gapSize={style.gap || undefined}
      />
      {animate
        ? Array.from({ length: style.packets }, (_, i) => packet(i))
        : !dim && (
            // Reduced motion / paused: a static direction marker instead of moving packets.
            <mesh position={arrowAt}>
              <octahedronGeometry args={[0.07]} />
              <meshBasicMaterial color={color} />
            </mesh>
          )}
    </group>
  )
}

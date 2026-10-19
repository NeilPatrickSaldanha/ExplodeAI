import { Edges } from '@react-three/drei'
import type { ThreeEvent } from '@react-three/fiber'
import { useMemo, useState } from 'react'
import type { ScenePalette } from './colors'
import type { PartShape, PartSpec, Vec3 } from './types'

interface Props {
  part: PartSpec
  at: Vec3
  explode: number
  selected: boolean
  dimmed: boolean
  palette: ScenePalette
  onSelect: (id: string) => void
}

/**
 * One component of the system. Each shape also has an internal "sub-explosion":
 * slices separate, pages fan, disks stack — so the part reads as made of parts.
 */
export function Part3D({ part, at, explode, selected, dimmed, palette, onSelect }: Props) {
  const [hovered, setHovered] = useState(false)
  const edge = selected ? palette.accent : hovered ? palette.ink : palette.edge
  const opacity = dimmed ? 0.14 : 1

  const handleClick = (e: ThreeEvent<MouseEvent>) => {
    e.stopPropagation()
    onSelect(part.id)
  }

  return (
    <group
      position={at}
      onClick={handleClick}
      onPointerOver={(e) => {
        e.stopPropagation()
        setHovered(true)
        document.body.style.cursor = 'pointer'
      }}
      onPointerOut={() => {
        setHovered(false)
        document.body.style.cursor = ''
      }}
    >
      <ShapeMeshes shape={part.shape} size={part.size} t={explode} color={palette.part} edge={edge} opacity={opacity} />
    </group>
  )
}

interface ShapeProps {
  shape: PartShape
  size: Vec3
  t: number
  color: string
  edge: string
  opacity: number
}

function Mat({ color, opacity }: { color: string; opacity: number }) {
  return (
    <meshStandardMaterial
      color={color}
      roughness={0.55}
      metalness={0.15}
      transparent={opacity < 1}
      opacity={opacity}
      depthWrite={opacity === 1}
    />
  )
}

function ShapeMeshes({ shape, size, t, color, edge, opacity }: ShapeProps) {
  const [w, h, d] = size
  const layers = useMemo(() => {
    switch (shape) {
      case 'slab': // chunker: a block cut into slices that separate
        return Array.from({ length: 5 }, (_, i) => ({
          key: i,
          pos: [(i - 2) * (w / 5 + t * 0.12), h / 2, 0] as Vec3,
          box: [w / 5 - 0.02, h, d] as Vec3,
        }))
      case 'stack': // documents / prompt: sheets that fan upward
        return Array.from({ length: 4 }, (_, i) => ({
          key: i,
          pos: [i * 0.04 * t, 0.06 + i * (0.09 + t * 0.1), -i * 0.04 * t] as Vec3,
          box: [w, 0.06, d] as Vec3,
        }))
      default:
        return []
    }
  }, [shape, w, h, d, t])

  const edgeEl = <Edges color={edge} threshold={20} />

  if (shape === 'slab' || shape === 'stack') {
    return (
      <>
        {layers.map((l) => (
          <mesh key={l.key} position={l.pos} castShadow>
            <boxGeometry args={l.box} />
            <Mat color={color} opacity={opacity} />
            {edgeEl}
          </mesh>
        ))}
      </>
    )
  }

  if (shape === 'cylinder') {
    // vector index: stacked disks that separate like a database symbol
    return (
      <>
        {[0, 1, 2].map((i) => (
          <mesh key={i} position={[0, 0.12 + i * (0.22 + t * 0.12), 0]}>
            <cylinderGeometry args={[w / 2, w / 2, 0.18, 40]} />
            <Mat color={color} opacity={opacity} />
            {edgeEl}
          </mesh>
        ))}
      </>
    )
  }

  if (shape === 'prism') {
    // embedder: a prism with a thin "dispersion" plate that slides out
    return (
      <>
        <mesh position={[0, h / 2, 0]} rotation={[Math.PI / 2, 0, 0]}>
          <cylinderGeometry args={[h * 0.7, h * 0.7, d, 3]} />
          <Mat color={color} opacity={opacity} />
          {edgeEl}
        </mesh>
        <mesh position={[w / 2 + 0.1 + t * 0.25, h / 2, 0]}>
          <boxGeometry args={[0.04, h * 0.9, d * 0.9]} />
          <Mat color={color} opacity={opacity} />
          {edgeEl}
        </mesh>
      </>
    )
  }

  if (shape === 'ring') {
    // retriever: a ring with a filter disk that rises out of it
    return (
      <>
        <mesh position={[0, 0.2, 0]} rotation={[Math.PI / 2, 0, 0]}>
          <torusGeometry args={[w / 2, 0.08, 16, 48]} />
          <Mat color={color} opacity={opacity} />
        </mesh>
        <mesh position={[0, 0.2 + t * 0.35, 0]}>
          <cylinderGeometry args={[w / 3, w / 3, 0.05, 32]} />
          <Mat color={color} opacity={opacity} />
          {edgeEl}
        </mesh>
      </>
    )
  }

  if (shape === 'lens') {
    // generator: two lens elements that separate along the optical axis
    return (
      <>
        {[-1, 1].map((s) => (
          <mesh key={s} position={[s * (0.12 + t * 0.18), h / 2, 0]} rotation={[0, 0, Math.PI / 2]}>
            <cylinderGeometry args={[h * 0.6, h * 0.6, 0.12, 40]} />
            <Mat color={color} opacity={opacity} />
            {edgeEl}
          </mesh>
        ))}
      </>
    )
  }

  // grid: a block of cells
  return (
    <>
      {[-1, 0, 1].flatMap((x) =>
        [-1, 0, 1].map((z) => (
          <mesh key={`${x}${z}`} position={[x * (w / 3 + t * 0.06), h / 2, z * (d / 3 + t * 0.06)]}>
            <boxGeometry args={[w / 3 - 0.03, h, d / 3 - 0.03]} />
            <Mat color={color} opacity={opacity} />
            {edgeEl}
          </mesh>
        )),
      )}
    </>
  )
}

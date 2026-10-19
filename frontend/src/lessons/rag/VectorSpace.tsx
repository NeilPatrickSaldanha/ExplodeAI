import { Line, OrbitControls } from '@react-three/drei'
import { Canvas } from '@react-three/fiber'
import { useMemo, useState } from 'react'
import type { RagResult } from '../../api/types'
import { scenePalette } from '../../engine/colors'
import { hasWebGL, useThemeVersion } from '../../engine/hooks'

const SCALE = 3

/** Real chunk and query vectors, projected to 3D with PCA (approximate distances). */
export function VectorSpace({ result }: { result: RagResult }) {
  const pct = Math.round(result.projection.explained_variance * 100)
  const retrieved = new Set(result.retrieved.map((r) => r.chunk_id))
  const [hover, setHover] = useState<string | null>(null)
  const hovered = result.chunks.find((c) => c.id === hover)
  return (
    <figure className="vspace">
      {hasWebGL() ? <Scene result={result} retrieved={retrieved} onHover={setHover} /> : <Flat result={result} retrieved={retrieved} />}
      <p className="vspace__hover" aria-live="polite">
        {hovered ? (
          <>
            <code>{hovered.id}</code> {hovered.text}
          </>
        ) : (
          'Hover a point to read its chunk. Drag to rotate.'
        )}
      </p>
      <figcaption className="label">
        PCA → 3D · {pct}% OF VARIANCE KEPT · ◆ QUERY · ● RETRIEVED · ○ OTHER CHUNKS
      </figcaption>
      <p className="vspace__note">
        3D distances only approximate the real {result.embedding.dim}-dimensional ones. The ranking table holds the
        exact scores.
      </p>
    </figure>
  )
}

function Scene({ result, retrieved, onHover }: { result: RagResult; retrieved: Set<string>; onHover: (id: string | null) => void }) {
  const v = useThemeVersion()
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const pal = useMemo(() => scenePalette(), [v])
  const q = result.query.point.map((x) => x * SCALE) as [number, number, number]
  return (
    <div className="vspace__canvas">
      <Canvas
        frameloop="demand"
        camera={{ position: [4.5, 3.5, 6], fov: 45 }}
        role="img"
        aria-label={`Vector space: ${result.chunks.length} chunks and the query, top ${retrieved.size} highlighted`}
      >
        <color attach="background" args={[pal.paper]} />
        <ambientLight intensity={0.8} />
        <directionalLight position={[4, 6, 3]} intensity={0.8} />
        {result.chunks.map((c) => {
          const p = c.point.map((x) => x * SCALE) as [number, number, number]
          const hit = retrieved.has(c.id)
          return (
            <group key={c.id}>
              <mesh
                position={p}
                onPointerOver={(e) => {
                  e.stopPropagation()
                  onHover(c.id)
                }}
                onPointerOut={() => onHover(null)}
              >
                <sphereGeometry args={[hit ? 0.11 : 0.07, 20, 20]} />
                <meshStandardMaterial color={hit ? pal.accent : pal.muted} wireframe={!hit} />
              </mesh>
              {hit && <Line points={[q, p]} color={pal.accent} lineWidth={1.2} transparent opacity={0.7} />}
            </group>
          )
        })}
        <mesh position={q}>
          <octahedronGeometry args={[0.16]} />
          <meshStandardMaterial color={pal.accent2} />
        </mesh>
        <OrbitControls makeDefault enablePan={false} />
      </Canvas>
    </div>
  )
}

function Flat({ result, retrieved }: { result: RagResult; retrieved: Set<string> }) {
  const S = 140
  const to = (p: number[]) => [160 + p[0] * S, 160 - p[1] * S]
  const [qx, qy] = to(result.query.point)
  return (
    <svg viewBox="0 0 320 320" className="vspace__flat" role="img" aria-label="Vector space, 2D projection">
      {result.chunks.map((c) => {
        const [x, y] = to(c.point)
        const hit = retrieved.has(c.id)
        return (
          <g key={c.id}>
            {hit && <line x1={qx} y1={qy} x2={x} y2={y} className="vspace__ray" />}
            <circle cx={x} cy={y} r={hit ? 6 : 4} className={hit ? 'vspace__hit' : 'vspace__pt'}>
              <title>{c.id}</title>
            </circle>
          </g>
        )
      })}
      <rect x={qx - 6} y={qy - 6} width={12} height={12} transform={`rotate(45 ${qx} ${qy})`} className="vspace__query" />
    </svg>
  )
}

import { Line, OrbitControls } from '@react-three/drei'
import { Canvas } from '@react-three/fiber'
import { useMemo, useState } from 'react'
import type { EmbedResult } from '../../api/types'
import { resolveTokenColor, scenePalette } from '../../engine/colors'
import { hasWebGL, useThemeVersion } from '../../engine/hooks'
import { CATEGORY_SHAPE, categoryToken } from './adapter'

/**
 * One row per token, one cell per dimension (first 24 of 384 shown). Cell height
 * is the magnitude, fill tells the sign. These are the encoder's real outputs.
 */
export function TokenHeat({ tokens, rows }: { tokens: { text: string }[]; rows: number[][] }) {
  const max = Math.max(1e-9, ...rows.flat().map((v) => Math.abs(v)))
  return (
    <div className="tokheat" role="img" aria-label={`${rows.length} token vectors, first ${rows[0]?.length ?? 0} dimensions each`}>
      {rows.map((row, i) => (
        <div className="tokheat__row" key={i}>
          <code className="tokheat__tok">{tokens[i]?.text}</code>
          <span className="tokheat__cells">
            {row.map((v, j) => (
              <span key={j} className={v >= 0 ? 'is-pos' : 'is-neg'} style={{ transform: `scaleY(${Math.max(0.1, Math.abs(v) / max)})` }} />
            ))}
          </span>
        </div>
      ))}
    </div>
  )
}

export function CategoryGlyph({ category, categories }: { category: string; categories: string[] }) {
  const shape = CATEGORY_SHAPE[category] ?? 'sphere'
  return <span className={`glyph glyph--${shape}`} style={{ background: `var(${categoryToken(categories, category)})` }} aria-hidden />
}

export function Neighbours({ result, max = 10 }: { result: EmbedResult; max?: number }) {
  if (!result.comparable) {
    return (
      <p className="notice notice--error" role="status">
        {result.notes[0] ?? 'These vectors cannot be compared.'}
      </p>
    )
  }
  const cats = result.library.categories
  return (
    <ol className="neigh">
      {result.neighbours.slice(0, max).map((n) => (
        <li key={n.id}>
          <CategoryGlyph category={n.category} categories={cats} />
          <span className="neigh__text">{n.text}</span>
          <span className="label">{n.category}</span>
          <span className="neigh__score">{n.score.toFixed(3)}</span>
        </li>
      ))}
    </ol>
  )
}

/** The library and your text, projected to 3D with PCA. Topics by shape and colour. */
export function SemanticSpace({ result }: { result: EmbedResult }) {
  const [hover, setHover] = useState<string | null>(null)
  const [asTable, setAsTable] = useState(false)
  const cats = result.library.categories
  const item = result.library.items.find((i) => i.id === hover)
  const pct = Math.round(result.projection.explained_variance * 100)
  return (
    <figure className="sspace">
      <div className="sspace__bar">
        <span className="label">PCA → 3D · {pct}% OF VARIANCE KEPT</span>
        <button type="button" className="btn btn--toggle" aria-pressed={asTable} onClick={() => setAsTable((t) => !t)}>
          {asTable ? 'Show map' : 'Show as table'}
        </button>
      </div>
      {asTable ? (
        <SpaceTable result={result} />
      ) : hasWebGL() ? (
        <SpaceScene result={result} onHover={setHover} />
      ) : (
        <SpaceFlat result={result} />
      )}
      <ul className="sspace__legend" aria-label="Topics">
        {cats.map((c) => (
          <li key={c}>
            <CategoryGlyph category={c} categories={cats} /> {c}
          </li>
        ))}
        <li>
          <span className="glyph glyph--query" aria-hidden /> your text
        </li>
      </ul>
      <p className="sspace__hover" aria-live="polite">
        {item ? `${item.text} · ${item.category}${item.score !== null ? ` · ${item.score.toFixed(3)}` : ''}` : 'Hover a point to read it. Drag to rotate.'}
      </p>
      <figcaption className="sspace__note">
        Three axes keep {pct}% of the spread of {result.model.dim} dimensions, so 3D distances only approximate the real
        ones. The neighbours list holds the exact scores.
      </figcaption>
    </figure>
  )
}

function SpaceScene({ result, onHover }: { result: EmbedResult; onHover: (id: string | null) => void }) {
  const v = useThemeVersion()
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const pal = useMemo(() => scenePalette(), [v])
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const colors = useMemo(() => Object.fromEntries(result.library.categories.map((c) => [c, resolveTokenColor(categoryToken(result.library.categories, c))])), [v, result.library.categories])
  const S = 3
  const q = result.query.point?.map((x) => x * S) as [number, number, number] | undefined
  const top = new Set(result.neighbours.map((n) => n.id))
  return (
    <div className="sspace__canvas">
      <Canvas frameloop="demand" camera={{ position: [4.2, 3.2, 5.6], fov: 45 }} role="img" aria-label={`Semantic space: ${result.library.items.length} sentences in ${result.library.categories.length} topics and your text`}>
        <color attach="background" args={[pal.paper]} />
        <ambientLight intensity={0.8} />
        <directionalLight position={[4, 6, 3]} intensity={0.9} />
        {result.library.items.map((it) => {
          const p = it.point.map((x) => x * S) as [number, number, number]
          const shape = CATEGORY_SHAPE[it.category]
          const r = top.has(it.id) ? 0.13 : 0.09
          return (
            <group key={it.id}>
              <mesh
                position={p}
                onPointerOver={(e) => {
                  e.stopPropagation()
                  onHover(it.id)
                }}
                onPointerOut={() => onHover(null)}
              >
                {shape === 'box' ? <boxGeometry args={[r * 1.6, r * 1.6, r * 1.6]} /> : shape === 'cylinder' ? <cylinderGeometry args={[r, r, r * 1.8, 20]} /> : shape === 'cone' ? <coneGeometry args={[r, r * 2, 20]} /> : <sphereGeometry args={[r, 20, 20]} />}
                <meshStandardMaterial color={colors[it.category]} />
              </mesh>
              {q && top.has(it.id) && <Line points={[q, p]} color={pal.accent} lineWidth={1.2} transparent opacity={0.65} />}
            </group>
          )
        })}
        {q && (
          <mesh position={q} rotation={[Math.PI / 2, 0, 0]}>
            <torusGeometry args={[0.16, 0.05, 12, 32]} />
            <meshStandardMaterial color={pal.accent2} />
          </mesh>
        )}
        <OrbitControls makeDefault enablePan={false} />
      </Canvas>
    </div>
  )
}

function SpaceFlat({ result }: { result: EmbedResult }) {
  const cats = result.library.categories
  const to = (p: number[]) => [160 + p[0] * 130, 160 - p[1] * 130]
  const q = result.query.point ? to(result.query.point) : null
  return (
    <svg viewBox="0 0 320 320" className="sspace__flat" role="img" aria-label="Semantic space, 2D projection">
      {result.library.items.map((it) => {
        const [x, y] = to(it.point)
        return (
          <circle key={it.id} cx={x} cy={y} r={5} style={{ fill: `var(${categoryToken(cats, it.category)})` }}>
            <title>{`${it.text} (${it.category})`}</title>
          </circle>
        )
      })}
      {q && <circle cx={q[0]} cy={q[1]} r={8} className="sspace__q" />}
    </svg>
  )
}

function SpaceTable({ result }: { result: EmbedResult }) {
  const rows = [...result.library.items].sort((a, b) => (a.rank ?? 999) - (b.rank ?? 999))
  return (
    <div className="table-wrap" role="region" aria-label="All sentences and scores" tabIndex={0}>
      <table className="ranking">
        <thead>
          <tr>
            <th scope="col">Rank</th>
            <th scope="col">Topic</th>
            <th scope="col">Sentence</th>
            <th scope="col">Score</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.id}>
              <td>{r.rank ?? '—'}</td>
              <td>{r.category}</td>
              <td className="ranking__text">{r.text}</td>
              <td>{r.score === null ? '—' : r.score.toFixed(3)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

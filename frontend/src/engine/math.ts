import type { AssemblySpec, PartSpec, Vec3 } from './types'

export const clamp01 = (t: number) => Math.min(1, Math.max(0, t))

export function easeInOutCubic(t: number): number {
  const x = clamp01(t)
  return x < 0.5 ? 4 * x * x * x : 1 - (-2 * x + 2) ** 3 / 2
}

/** Height of the arc parts travel along while exploding (0 at both ends). */
export const LIFT = 0.9

/**
 * Stretch each part's explode offset per axis. The scene frame is wide and shallow,
 * so a lesson chooses how far its parts spread along x, y and z; the camera re-frames
 * for the stretched layout, which keeps labels and links apart and in view.
 */
export function spreadParts<T extends { explode: Vec3 }>(parts: T[], spread: Vec3): T[] {
  return parts.map((p) => ({ ...p, explode: [p.explode[0] * spread[0], p.explode[1] * spread[1], p.explode[2] * spread[2]] as Vec3 }))
}

/** World position of a part at explosion factor t. */
export function partPosition(part: Pick<PartSpec, 'position' | 'explode'>, t: number): Vec3 {
  // Linear on purpose: the slider is the control, so every 10% must move the parts by the same visible
  // amount. (An ease-in-out curve made 80% to 100% look identical.)
  const e = clamp01(t)
  const lift = Math.sin(Math.PI * clamp01(t)) * LIFT
  return [
    part.position[0] + part.explode[0] * e,
    part.position[1] + part.explode[1] * e + lift,
    part.position[2] + part.explode[2] * e,
  ]
}

/** Control point for a link curve: midpoint raised so links arc over parts. */
export function linkControlPoint(a: Vec3, b: Vec3): Vec3 {
  const dist = Math.hypot(b[0] - a[0], b[2] - a[2])
  return [(a[0] + b[0]) / 2, Math.max(a[1], b[1]) + 0.35 + dist * 0.12, (a[2] + b[2]) / 2]
}

/** Point on a quadratic Bézier at u ∈ [0, 1]. */
export function quadBezier(a: Vec3, c: Vec3, b: Vec3, u: number): Vec3 {
  const v = 1 - u
  return [0, 1, 2].map((i) => v * v * a[i] + 2 * v * u * c[i] + u * u * b[i]) as Vec3
}

/** Bounding sphere of all parts at a given explosion, used to frame the camera. */
export function bounds(spec: AssemblySpec, t: number): { center: Vec3; radius: number } {
  const pts = spec.parts.map((p) => partPosition(p, t))
  if (pts.length === 0) return { center: [0, 0, 0], radius: 1 }
  const center = [0, 1, 2].map((i) => pts.reduce((s, p) => s + p[i], 0) / pts.length) as Vec3
  const radius = Math.max(1, ...pts.map((p) => Math.hypot(p[0] - center[0], p[1] - center[1], p[2] - center[2])))
  return { center, radius }
}

/** Ids of parts directly linked to `id` (either direction). */
export function neighbours(spec: AssemblySpec, id: string): Set<string> {
  const out = new Set<string>()
  for (const l of spec.links) {
    if (l.source === id) out.add(l.target)
    if (l.target === id) out.add(l.source)
  }
  return out
}

/** Keyboard navigation: wrap-around index step. */
export function stepIndex(current: number, delta: number, length: number): number {
  if (length === 0) return -1
  if (current < 0) return delta > 0 ? 0 : length - 1
  return (((current + delta) % length) + length) % length
}

/** Project a 3D layout onto 2D (top-down x/z) for the flat fallback diagram. */
export function topDown(spec: AssemblySpec, t: number, width: number, height: number, pad = 48) {
  const pts = spec.parts.map((p) => partPosition(p, t))
  const xs = pts.map((p) => p[0])
  const zs = pts.map((p) => p[2])
  const [minX, maxX, minZ, maxZ] = [Math.min(...xs), Math.max(...xs), Math.min(...zs), Math.max(...zs)]
  const sx = (width - pad * 2) / Math.max(maxX - minX, 1e-6)
  const sz = (height - pad * 2) / Math.max(maxZ - minZ, 1e-6)
  const s = Math.min(sx, sz)
  const ox = (width - (maxX - minX) * s) / 2
  const oz = (height - (maxZ - minZ) * s) / 2
  return Object.fromEntries(
    spec.parts.map((p, i) => [p.id, { x: ox + (pts[i][0] - minX) * s, y: oz + (pts[i][2] - minZ) * s }]),
  ) as Record<string, { x: number; y: number }>
}

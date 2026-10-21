import type { AssemblySpec, Readouts } from './types'
import { linkKey } from './types'

/** Layout for the 2D diagram: real pixel sizes, no overlaps, every link label placed clear of the nodes. */
export const BOX_H = 68
export const PAD = 28
const BOX_W_MAX = 164
const BOX_W_MIN = 92
const GAP_X = 44
const GAP_Y = 52
const LABEL_CHAR = 6.4
const LABEL_LINE = 15

export interface Pill {
  cx: number
  cy: number
  w: number
  h: number
  lines: string[]
}

export interface FlatLink {
  key: string
  source: string
  target: string
  kind: 'document' | 'vector' | 'query'
  x1: number
  y1: number
  x2: number
  y2: number
  pill: Pill
  /** The link's midpoint, and whether the label was moved off the line (then a leader joins them). */
  mx: number
  my: number
  detached: boolean
}

export interface FlatLayout {
  width: number
  height: number
  boxW: number
  boxH: number
  portrait: boolean
  pos: Record<string, { x: number; y: number }>
  links: FlatLink[]
}

/** Number of distinct positions along one axis (values closer than `tol` count as the same). */
function levels(values: number[], tol = 0.5): number {
  const sorted = [...values].sort((a, b) => a - b)
  let n = 0
  let last = -Infinity
  for (const v of sorted) {
    if (v - last > tol) n++
    last = v
  }
  return n
}

type Rect = { x: number; y: number; w: number; h: number }
const overlaps = (a: Rect, b: Rect, m = 0) => a.x < b.x + b.w + m && a.x + a.w + m > b.x && a.y < b.y + b.h + m && a.y + a.h + m > b.y

/** Where the line from a box centre towards (tx, ty) leaves the box. */
function edge(cx: number, cy: number, tx: number, ty: number, boxW: number, gap = 5) {
  const dx = tx - cx
  const dy = ty - cy
  const len = Math.hypot(dx, dy) || 1
  const ux = dx / len
  const uy = dy / len
  const t = Math.min(ux ? boxW / 2 / Math.abs(ux) : Infinity, uy ? BOX_H / 2 / Math.abs(uy) : Infinity) + gap
  return { x: cx + ux * t, y: cy + uy * t, ux, uy }
}

/**
 * The 2D diagram uses each part's exploded offset only (the layout the lesson was designed with), so it is
 * identical whatever the Explode slider says and rows line up in columns.
 */
export function flatLayout(spec: AssemblySpec, cw: number, ch: number, readouts?: Readouts, extra = 0): FlatLayout {
  const portrait = cw < 620
  const pts = spec.parts.map((p) => p.explode)
  // Landscape: x runs left to right. Portrait: the same flow runs top to bottom.
  const hv = pts.map((p) => (portrait ? p[2] : p[0]))
  const vv = pts.map((p) => (portrait ? p[0] : p[2]))
  const nH = Math.max(1, levels(hv))
  const nV = Math.max(1, levels(vv))
  // Keep clear of the badges at the top and the view toolbar at the bottom (which sit over the scene on wide
  // screens; on phones the toolbar is below it but the legend wraps under the badges).
  const padT = portrait ? 116 : 72
  const padB = portrait ? PAD : 104
  const [hmin, hmax] = [Math.min(...hv), Math.max(...hv)]
  const [vmin, vmax] = [Math.min(...vv), Math.max(...vv)]
  // Phones scroll, so give labels generous room between rows.
  const gapY = (portrait ? 80 : GAP_Y) + extra
  const boxMin = portrait ? 88 : BOX_W_MIN
  const gapX = portrait ? 28 : GAP_X
  const height = Math.max(ch, Math.round(padT + padB + nV * BOX_H + (nV - 1) * gapY))

  const place = (boxW: number, width: number) => {
    const spanX = width - 2 * PAD - boxW
    const spanY = height - padT - padB - BOX_H
    return spec.parts.map((_, i) => ({
      x: PAD + boxW / 2 + (hmax > hmin ? ((hv[i] - hmin) / (hmax - hmin)) * spanX : spanX / 2),
      y: padT + BOX_H / 2 + (vmax > vmin ? ((vv[i] - vmin) / (vmax - vmin)) * spanY : spanY / 2),
    }))
  }
  const fits = (w: number, W: number) => {
    const pts2 = place(w, W)
    for (let i = 0; i < pts2.length; i++)
      for (let j = i + 1; j < pts2.length; j++)
        if (Math.abs(pts2[i].y - pts2[j].y) < BOX_H + 20 && Math.abs(pts2[i].x - pts2[j].x) < w + 20) return false
    return true
  }
  // The widest box that still leaves room between neighbours in the same band, so names stay readable.
  // Only if even the narrowest box does not fit is the canvas made wider than the container (it then scrolls).
  let boxW = boxMin
  let width = Math.max(cw, 2 * PAD + boxMin)
  let found = false
  for (let w = BOX_W_MAX; w >= boxMin; w -= 6) {
    if (fits(w, width)) {
      boxW = w
      found = true
      break
    }
  }
  if (!found) {
    const cap = Math.round(2 * PAD + nH * boxMin + (nH - 1) * gapX)
    while (width < cap && !fits(boxMin, width)) width += 24
  }
  const pos: FlatLayout['pos'] = {}
  place(boxW, width).forEach((pt, i) => {
    pos[spec.parts[i].id] = pt
  })

  // Nudge apart any boxes that still touch.
  const ids = spec.parts.map((p) => p.id)
  for (let pass = 0; pass < 40; pass++) {
    let moved = false
    for (let i = 0; i < ids.length; i++) {
      for (let j = i + 1; j < ids.length; j++) {
        const a = pos[ids[i]]
        const b = pos[ids[j]]
        const ox = boxW + 16 - Math.abs(a.x - b.x)
        const oy = BOX_H + 16 - Math.abs(a.y - b.y)
        if (ox > 0 && oy > 0) {
          moved = true
          if (oy <= ox) {
            const s = (a.y <= b.y ? 1 : -1) * (oy / 2 + 0.5)
            a.y -= s
            b.y += s
          } else {
            const s = (a.x <= b.x ? 1 : -1) * (ox / 2 + 0.5)
            a.x -= s
            b.x += s
          }
        }
      }
    }
    for (const id of ids) {
      pos[id].x = Math.min(width - PAD - boxW / 2, Math.max(PAD + boxW / 2, pos[id].x))
      pos[id].y = Math.min(height - padB - BOX_H / 2, Math.max(padT + BOX_H / 2, pos[id].y))
    }
    if (!moved) break
  }

  const boxes: Rect[] = ids.map((id) => ({ x: pos[id].x - boxW / 2, y: pos[id].y - BOX_H / 2, w: boxW, h: BOX_H }))
  const placed: Rect[] = []
  let collided = false
  const links: FlatLink[] = spec.links.map((l) => {
    const a = pos[l.source]
    const b = pos[l.target]
    const p1 = edge(a.x, a.y, b.x, b.y, boxW)
    const p2 = edge(b.x, b.y, a.x, a.y, boxW)
    const readout = readouts?.links?.[linkKey(l)]
    const lines = readout ? [l.label, readout] : [l.label]
    const w = Math.round(Math.max(...lines.map((s) => s.length)) * LABEL_CHAR + 22)
    const h = lines.length * LABEL_LINE + 9
    const nx = -p1.uy
    const ny = p1.ux
    const dx = p2.x - p1.x
    const dy = p2.y - p1.y
    let best: { cx: number; cy: number; cost: number } | null = null
    for (const off of [0, 24, -24, 44, -44, 64, -64, 88, -88, 112, -112]) {
      for (const s of [0.5, 0.42, 0.58, 0.34, 0.66, 0.26, 0.74]) {
        const cx = p1.x + dx * s + nx * off
        const cy = p1.y + dy * s + ny * off
        const r: Rect = { x: cx - w / 2, y: cy - h / 2, w, h }
        let cost = Math.abs(off) * 0.4 + Math.abs(s - 0.5) * 20
        // A label that would cover most of a short link hides its arrow: prefer to sit beside it.
        if (off === 0 && Math.abs(nx) * h + Math.abs(ny) * w > 0 && w * Math.abs(p1.ux) + h * Math.abs(p1.uy) > 0.7 * Math.hypot(dx, dy)) cost += 60
        for (const bx of boxes) if (overlaps(r, bx, 5)) cost += 1000
        for (const o of placed) if (overlaps(r, o, 4)) cost += 500
        if (r.x < 4 || r.y < 4 || r.x + w > width - 4 || r.y + h > height - 4) cost += 800
        if (!best || cost < best.cost) best = { cx, cy, cost }
      }
    }
    if (best!.cost >= 500) collided = true
    const pill: Pill = { cx: best!.cx, cy: best!.cy, w, h, lines }
    const mx = (p1.x + p2.x) / 2
    const my = (p1.y + p2.y) / 2
    const dist = Math.abs((pill.cx - p1.x) * p1.uy - (pill.cy - p1.y) * p1.ux)
    const along = (pill.cx - mx) * p1.ux + (pill.cy - my) * p1.uy
    placed.push({ x: pill.cx - w / 2, y: pill.cy - h / 2, w, h })
    return { key: linkKey(l), source: l.source, target: l.target, kind: l.kind ?? 'document', x1: p1.x, y1: p1.y, x2: p2.x, y2: p2.y, pill, mx, my, detached: dist > h / 2 + 2 || Math.abs(along) > 0.3 * Math.hypot(dx, dy) }
  })

  // A label had nowhere clear to go: add room between rows (and, on wide screens, between columns) and retry.
  if (collided && extra < 240) return flatLayout(spec, cw, ch, readouts, extra + 40)
  return { width, height, boxW, boxH: BOX_H, portrait, pos, links }
}

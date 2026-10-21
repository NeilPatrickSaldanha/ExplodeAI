import { describe, expect, it } from 'vitest'
import { BOX_H, flatLayout } from './flatLayout'
import type { AssemblySpec } from './types'

const part = (id: string, explode: [number, number, number]) => ({
  id,
  label: id,
  group: 'g',
  shape: 'slab' as const,
  size: [1, 1, 1] as [number, number, number],
  position: [0, 0, 0] as [number, number, number],
  explode,
})
// A two-row snake like the lessons use.
const spec: AssemblySpec = {
  parts: [part('a', [-4, 0, -2]), part('b', [-1.5, 0, -2]), part('c', [1.5, 0, -2]), part('d', [4, 0, -2]), part('e', [4, 0, 2]), part('f', [1.5, 0, 2]), part('g', [-1.5, 0, 2]), part('h', [-4, 0, 2])],
  links: [
    { source: 'a', target: 'b', label: 'words' },
    { source: 'b', target: 'c', label: 'word vectors', kind: 'vector' },
    { source: 'c', target: 'd', label: 'scores and weights', kind: 'query' },
    { source: 'd', target: 'e', label: 'masked scores' },
    { source: 'e', target: 'f', label: 'weights', kind: 'vector' },
    { source: 'f', target: 'g', label: 'mixed values' },
    { source: 'g', target: 'h', label: 'heads', kind: 'vector' },
  ],
}

const overlap = (a: { x: number; y: number; w: number; h: number }, b: { x: number; y: number; w: number; h: number }) =>
  a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y

describe('flatLayout', () => {
  for (const [w, h] of [[1200, 600], [900, 560], [768, 700], [390, 700], [320, 560]]) {
    it(`keeps nodes and labels apart at ${w}×${h}`, () => {
      const L = flatLayout(spec, w, h)
      const boxes = Object.values(L.pos).map((p) => ({ x: p.x - L.boxW / 2, y: p.y - BOX_H / 2, w: L.boxW, h: BOX_H }))
      for (let i = 0; i < boxes.length; i++) for (let j = i + 1; j < boxes.length; j++) expect(overlap(boxes[i], boxes[j])).toBe(false)
      const pills = L.links.map((l) => ({ x: l.pill.cx - l.pill.w / 2, y: l.pill.cy - l.pill.h / 2, w: l.pill.w, h: l.pill.h }))
      for (const p of pills) {
        for (const b of boxes) expect(overlap(p, b)).toBe(false)
        expect(p.x).toBeGreaterThanOrEqual(0)
        expect(p.x + p.w).toBeLessThanOrEqual(L.width)
      }
      for (let i = 0; i < pills.length; i++) for (let j = i + 1; j < pills.length; j++) expect(overlap(pills[i], pills[j])).toBe(false)
    })
  }

  it('uses the real container size and goes vertical on narrow screens', () => {
    expect(flatLayout(spec, 1200, 600).portrait).toBe(false)
    const phone = flatLayout(spec, 390, 600)
    expect(phone.portrait).toBe(true)
    expect(phone.height).toBeGreaterThan(600) // scrolls vertically instead of shrinking the text
    expect(phone.width).toBeLessThanOrEqual(390)
  })

  it('is independent of how far the parts are exploded in 3D', () => {
    const half = { ...spec, parts: spec.parts.map((p) => ({ ...p, position: [3, 0, 3] as [number, number, number] })) }
    expect(flatLayout(half, 1000, 600).pos).toEqual(flatLayout(spec, 1000, 600).pos)
  })

  it('shows readouts on the labels and ends each link at a box edge, not a box centre', () => {
    const L = flatLayout(spec, 1000, 600, { links: { 'a->b': '6 words' } })
    expect(L.links[0].pill.lines).toEqual(['words', '6 words'])
    const a = L.pos.a
    expect(Math.hypot(L.links[0].x1 - a.x, L.links[0].y1 - a.y)).toBeGreaterThan(L.boxW / 2 - 1)
  })
})

import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { ExplodedView } from './ExplodedView'
import { bounds, easeInOutCubic, neighbours, partPosition, quadBezier, spreadParts, stepIndex, topDown } from './math'
import type { AssemblySpec, ViewState } from './types'

const spec: AssemblySpec = {
  parts: [
    { id: 'a', label: 'Alpha', group: 'one', shape: 'slab', size: [1, 1, 1], position: [0, 0, 0], explode: [-4, 0, 0] },
    { id: 'b', label: 'Beta', group: 'one', shape: 'ring', size: [1, 1, 1], position: [1, 0, 0], explode: [0, 0, 3] },
    { id: 'c', label: 'Gamma', group: 'two', shape: 'lens', size: [1, 1, 1], position: [2, 0, 0], explode: [4, 0, 0] },
  ],
  links: [
    { source: 'a', target: 'b', label: 'ab' },
    { source: 'b', target: 'c', label: 'bc' },
  ],
}
const view = (v: Partial<ViewState> = {}): ViewState => ({ explode: 1, selectedId: null, isolate: false, flow: false, ...v })

describe('engine math', () => {
  it('eases monotonically from 0 to 1', () => {
    expect(easeInOutCubic(0)).toBe(0)
    expect(easeInOutCubic(1)).toBe(1)
    const samples = Array.from({ length: 11 }, (_, i) => easeInOutCubic(i / 10))
    samples.slice(1).forEach((s, i) => expect(s).toBeGreaterThanOrEqual(samples[i]))
  })

  it('puts parts at their assembled and exploded positions, lifting only mid-flight', () => {
    expect(partPosition(spec.parts[0], 0)).toEqual([0, 0, 0])
    const end = partPosition(spec.parts[0], 1)
    expect(end[0]).toBeCloseTo(-4)
    expect(end[1]).toBeCloseTo(0)
    expect(partPosition(spec.parts[0], 0.5)[1]).toBeGreaterThan(0)
  })

  it('bezier hits both endpoints', () => {
    expect(quadBezier([0, 0, 0], [1, 2, 0], [2, 0, 0], 0)).toEqual([0, 0, 0])
    expect(quadBezier([0, 0, 0], [1, 2, 0], [2, 0, 0], 1)).toEqual([2, 0, 0])
  })

  it('finds neighbours in both directions', () => {
    expect([...neighbours(spec, 'b')].sort()).toEqual(['a', 'c'])
  })

  it('wraps keyboard navigation', () => {
    expect(stepIndex(-1, 1, 3)).toBe(0)
    expect(stepIndex(-1, -1, 3)).toBe(2)
    expect(stepIndex(2, 1, 3)).toBe(0)
    expect(stepIndex(0, -1, 3)).toBe(2)
  })

  it('spreads explode offsets per axis without touching assembled positions', () => {
    const [p] = spreadParts([spec.parts[1]], [2, 1, 3])
    expect(p.explode).toEqual([0, 0, 9])
    expect(p.position).toEqual(spec.parts[1].position)
  })

  it('bounds grow as the assembly explodes', () => {
    expect(bounds(spec, 1).radius).toBeGreaterThan(bounds(spec, 0).radius)
  })

  it('top-down projection keeps every part inside the canvas', () => {
    const pos = topDown(spec, 1, 400, 200, 20)
    for (const { x, y } of Object.values(pos)) {
      expect(x).toBeGreaterThanOrEqual(20)
      expect(x).toBeLessThanOrEqual(380)
      expect(y).toBeGreaterThanOrEqual(0)
      expect(y).toBeLessThanOrEqual(200)
    }
  })
})

describe('ExplodedView (2D fallback, no WebGL in jsdom)', () => {
  it('renders every part as a keyboard-operable control', () => {
    const onSelect = vi.fn()
    render(<ExplodedView spec={spec} view={view()} mode="3d" reducedMotion onSelect={onSelect} onToggleIsolate={() => {}} title="Test assembly" />)
    expect(screen.getByText(/WebGL unavailable/)).toBeInTheDocument()
    const beta = screen.getByRole('button', { name: /Beta/ })
    fireEvent.keyDown(beta, { key: 'Enter' })
    expect(onSelect).toHaveBeenCalledWith('b')
  })

  it('shows live readouts and dims non-neighbours when isolating', () => {
    const { container } = render(
      <ExplodedView
        spec={spec}
        view={view({ selectedId: 'a', isolate: true })}
        readouts={{ parts: { a: '6 DOCS' } }}
        mode="2d"
        reducedMotion
        onSelect={() => {}}
        onToggleIsolate={() => {}}
        title="Test assembly"
      />,
    )
    expect(screen.getByRole('button', { name: /Alpha.*6 DOCS/ })).toHaveAttribute('aria-pressed', 'true')
    expect(container.querySelector('.flat-diagram__part.is-dim')).toHaveTextContent('Gamma')
    expect(screen.getByText('Alpha selected, isolated.')).toBeInTheDocument()
  })
})

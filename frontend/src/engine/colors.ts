/**
 * Three.js can't parse oklch(). Resolve a CSS custom property to sRGB hex by
 * letting the browser rasterise it, so the 3D scene uses the same tokens as the UI.
 */
const cache = new Map<string, string>()

export function resolveTokenColor(token: string, fallback = '#888888'): string {
  if (typeof document === 'undefined') return fallback
  const raw = getComputedStyle(document.documentElement).getPropertyValue(token).trim()
  if (!raw) return fallback
  const hit = cache.get(raw)
  if (hit) return hit
  try {
    const canvas = document.createElement('canvas')
    canvas.width = canvas.height = 1
    const ctx = canvas.getContext('2d', { willReadFrequently: true })
    if (!ctx) return fallback
    ctx.fillStyle = fallback
    ctx.fillStyle = raw
    ctx.fillRect(0, 0, 1, 1)
    const [r, g, b] = ctx.getImageData(0, 0, 1, 1).data
    const hex = `#${[r, g, b].map((n) => n.toString(16).padStart(2, '0')).join('')}`
    cache.set(raw, hex)
    return hex
  } catch {
    return fallback
  }
}

export interface ScenePalette {
  part: string
  edge: string
  accent: string
  accent2: string
  flow: string
  flowVector: string
  flowQuery: string
  ink: string
  muted: string
  paper: string
}

export function scenePalette(): ScenePalette {
  return {
    part: resolveTokenColor('--scene-part'),
    edge: resolveTokenColor('--scene-part-edge'),
    accent: resolveTokenColor('--color-accent'),
    accent2: resolveTokenColor('--color-accent-2'),
    flow: resolveTokenColor('--scene-flow'),
    flowVector: resolveTokenColor('--scene-flow-vector'),
    flowQuery: resolveTokenColor('--scene-flow-query'),
    ink: resolveTokenColor('--color-ink'),
    muted: resolveTokenColor('--color-muted'),
    paper: resolveTokenColor('--color-paper'),
  }
}

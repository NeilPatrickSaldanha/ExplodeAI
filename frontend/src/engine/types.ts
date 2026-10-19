/**
 * Exploded-view engine contract. The engine knows nothing about RAG: any lesson
 * describes its system as parts + links and gets 3D, 2D and list views for free.
 */
export type Vec3 = [number, number, number]
export type PartShape = 'slab' | 'stack' | 'cylinder' | 'grid' | 'prism' | 'lens' | 'ring'

export interface PartSpec {
  id: string
  label: string
  /** Free-form group (e.g. pipeline phase) — rendered as text, never by colour alone. */
  group: string
  shape: PartShape
  size: Vec3
  /** Assembled (collapsed) position. */
  position: Vec3
  /** Offset added at full explosion. */
  explode: Vec3
}

export interface LinkSpec {
  source: string
  target: string
  label: string
}

export interface AssemblySpec {
  parts: PartSpec[]
  links: LinkSpec[]
}

export interface ViewState {
  /** 0 = assembled, 1 = fully exploded. */
  explode: number
  selectedId: string | null
  /** When true, everything except the selected part (and its links) fades back. */
  isolate: boolean
  /** Animate packets along links. */
  flow: boolean
}

/** Live readouts attached to parts and links (real values from an experiment run). */
export interface Readouts {
  parts?: Record<string, string>
  links?: Record<string, string>
}

export const linkKey = (l: { source: string; target: string }) => `${l.source}->${l.target}`

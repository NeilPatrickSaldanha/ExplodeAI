import type { EmbedResult, Lesson } from '../../api/types'
import type { AssemblySpec, Readouts } from '../../engine/types'
import { spreadParts } from '../../engine/math'
import { linkKey } from '../../engine/types'

/** How far this lesson's parts spread when fully exploded (x, y, z). */
const SPREAD: [number, number, number] = [2.3, 1.2, 1.7]

export function lessonToSpec(lesson: Lesson): AssemblySpec {
  return {
    parts: spreadParts(lesson.components.map((c, i) => ({
      id: c.id,
      label: c.label,
      group: c.phase,
      shape: c.geometry.shape,
      size: c.geometry.size,
      position: c.position,
      explode: c.explode,
      subtitle: c.subtitle ?? undefined,
      number: String(i + 1).padStart(2, '0'),
    })), SPREAD),
    links: lesson.connections.map((c) => ({ source: c.source, target: c.target, label: c.payload, kind: c.flow ?? 'document' })),
  }
}

const link = (source: string, target: string) => linkKey({ source, target })

/** Real values from the last embeddings run, shown as callouts in the scene. */
export function readoutsFromResult(r: EmbedResult | null): Readouts | undefined {
  if (!r) return undefined
  const q = r.query
  const neural = q.embedder === 'neural'
  const top = r.neighbours[0]
  return {
    parts: {
      library: `${r.library.items.length} SENTENCES`,
      your_text: `${q.text.split(/\s+/).length} WORDS`,
      tokenizer: neural ? `${q.tokens.length} TOKENS${q.truncated ? ' · TRUNCATED' : ''}` : `${q.tokens.length} TERMS · LEXICAL`,
      encoder: neural ? `${q.tokens.length} × ${q.dim}` : 'NO ENCODER · LEXICAL',
      pooling: neural ? `${r.params.pooling.toUpperCase()} → 1 × ${q.dim}` : 'HASHED TERMS',
      normalizer: `LENGTH ${q.norm_before.toFixed(2)} → ${q.norm_after.toFixed(2)}`,
      similarity: r.comparable && top ? `${top.category.toUpperCase()} ${top.score.toFixed(2)}` : 'NOT COMPARABLE',
      semantic_space: `PCA ${Math.round(r.projection.explained_variance * 100)}% KEPT`,
    },
    links: {
      [link('your_text', 'tokenizer')]: `${q.text.length} chars`,
      [link('tokenizer', 'encoder')]: `${q.tokens.length} ids`,
      [link('encoder', 'pooling')]: `${q.tokens.length}×${q.dim}`,
      [link('pooling', 'normalizer')]: `1×${q.dim}`,
      [link('normalizer', 'similarity')]: `${r.library.items.length + 1} vectors`,
      [link('normalizer', 'semantic_space')]: `${r.library.items.length + 1} points`,
    },
  }
}

export const CATEGORY_SHAPE: Record<string, 'sphere' | 'box' | 'cylinder' | 'cone'> = {
  animals: 'sphere',
  food: 'box',
  furniture: 'cylinder',
  vehicles: 'cone',
}

/** Fixed-order categorical slot per topic (never cycled, never by rank). */
export const categoryToken = (categories: string[], c: string) => `--cat-${categories.indexOf(c) + 1}`

import type { AttendResult, Lesson } from '../../api/types'
import { spreadParts } from '../../engine/math'
import type { AssemblySpec, Readouts } from '../../engine/types'
import { linkKey } from '../../engine/types'

/** How far this lesson's parts spread when fully exploded (x, y, z). */
const SPREAD: [number, number, number] = [2.3, 1.2, 1.5]

export function lessonToSpec(lesson: Lesson): AssemblySpec {
  return {
    parts: spreadParts(
      lesson.components.map((c, i) => ({
        id: c.id,
        label: c.label,
        group: c.phase,
        shape: c.geometry.shape,
        size: c.geometry.size,
        position: c.position,
        explode: c.explode,
        subtitle: c.subtitle ?? undefined,
        number: String(i + 1).padStart(2, '0'),
      })),
      SPREAD,
    ),
    links: lesson.connections.map((c) => ({ source: c.source, target: c.target, label: c.payload, kind: c.flow ?? 'document' })),
  }
}

const link = (source: string, target: string) => linkKey({ source, target })

/** Real values from the last run, shown as callouts in the scene. */
export function readoutsFromResult(r: AttendResult | null): Readouts | undefined {
  if (!r) return undefined
  const n = r.tokens.length
  const s = r.stats
  return {
    parts: {
      tokens: `${n} TOKENS`,
      embed_pos: r.params.position ? `${r.model.d_model}-D + POSITION` : `${r.model.d_model}-D · NO POSITION`,
      qkv: `${r.model.heads} × ${r.model.head_dim}`,
      scores: `${n} × ${n} · STD ${s.score_std_used.toFixed(1)}`,
      mask: r.params.causal ? 'CAUSAL' : 'NONE',
      softmax: `MAX ${Math.round(s.mean_max_weight * 100)}%`,
      mix: `${r.model.heads} × ${n} × ${r.model.head_dim}`,
      output: `${n} × ${r.model.d_model}`,
    },
    links: {
      [link('tokens', 'embed_pos')]: `${n} words`,
      [link('embed_pos', 'qkv')]: `${n}×${r.model.d_model}`,
      [link('qkv', 'scores')]: 'Q and K',
      [link('scores', 'mask')]: `${n}×${n}`,
      [link('mask', 'softmax')]: `${n}×${n}`,
      [link('softmax', 'mix')]: 'weights',
      [link('qkv', 'mix')]: 'V',
      [link('mix', 'output')]: `${r.model.heads} heads`,
    },
  }
}

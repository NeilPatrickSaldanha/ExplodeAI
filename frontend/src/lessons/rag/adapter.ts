import type { Lesson, RagResult } from '../../api/types'
import type { AssemblySpec, Readouts } from '../../engine/types'
import { spreadParts } from '../../engine/math'
import { linkKey } from '../../engine/types'

/** Id of the scenery card for the learner's question (not a pipeline stage). */
export const QUESTION_PROP = 'question'

/** How far this lesson's parts spread when fully exploded (x, y, z). */
const SPREAD: [number, number, number] = [2.6, 1.2, 1.25]

export function lessonToSpec(lesson: Lesson): AssemblySpec {
  const parts: AssemblySpec['parts'] = lesson.components.map((c, i) => ({
    id: c.id,
    label: c.label,
    group: c.phase,
    shape: c.geometry.shape,
    size: c.geometry.size,
    position: c.position,
    explode: c.explode,
    subtitle: c.subtitle ?? undefined,
    number: String(i + 1).padStart(2, '0'),
  }))
  const links: AssemblySpec['links'] = lesson.connections.map((c) => ({
    source: c.source,
    target: c.target,
    label: c.payload,
    kind: c.flow ?? 'document',
  }))
  const qe = lesson.components.find((c) => c.id === 'query_encoder')
  if (qe) {
    // The question enters from the front, just ahead of the query embedder.
    parts.push({
      id: QUESTION_PROP,
      label: 'Your question',
      group: 'input',
      shape: 'card',
      size: [1.3, 0.75, 0.05],
      position: [qe.position[0], 0, qe.position[2] + 0.9],
      explode: [qe.explode[0], 0, qe.explode[2] + 1.6],
      prop: true,
    })
    links.unshift({ source: QUESTION_PROP, target: qe.id, label: 'question', kind: 'query' })
  }
  return { parts: spreadParts(parts, SPREAD), links }
}

const METHOD_LABEL = { dense: 'DENSE', bm25: 'BM25', hybrid: 'HYBRID · RRF' } as const

/** Real values from the last experiment run, shown as callouts in the scene. */
export function readoutsFromResult(r: RagResult | null): Readouts | undefined {
  if (!r) return undefined
  const n = r.chunks.length
  const k = r.retrieved.length
  return {
    parts: {
      [QUESTION_PROP]: `“${r.query.text.length > 34 ? `${r.query.text.slice(0, 33)}…` : r.query.text}”`,
      corpus: `${r.corpus.documents.length} DOCS`,
      chunker: `${n} CHUNKS · ${r.params.strategy.toUpperCase()}`,
      embedder: `${r.embedding.dim}-D`,
      vector_index: `${n} VECTORS · FLAT`,
      query_encoder: `1 VECTOR · ${r.embedding.dim}-D`,
      retriever: `TOP-${k} · ${METHOD_LABEL[r.params.method]}`,
      prompt_builder: `${r.prompt.context_words}/${r.prompt.budget_words} WORDS`,
      generator: r.answer.is_llm ? 'LLM' : 'EXTRACTIVE · NOT AN LLM',
    },
    links: {
      [linkKey({ source: QUESTION_PROP, target: 'query_encoder' })]: `${r.query.text.split(/\s+/).length} WORDS`,
      [linkKey({ source: 'corpus', target: 'chunker' })]: `${r.corpus.documents.length}`,
      [linkKey({ source: 'chunker', target: 'embedder' })]: `${n}`,
      [linkKey({ source: 'embedder', target: 'vector_index' })]: `${n}×${r.embedding.dim}`,
      [linkKey({ source: 'vector_index', target: 'retriever' })]: `${n} SEARCHABLE`,
      [linkKey({ source: 'query_encoder', target: 'retriever' })]: `1×${r.embedding.dim}`,
      [linkKey({ source: 'retriever', target: 'prompt_builder' })]: `${k}`,
      [linkKey({ source: 'prompt_builder', target: 'generator' })]: `${r.prompt.included.length} in · ${r.prompt.dropped.length} dropped`,
    },
  }
}

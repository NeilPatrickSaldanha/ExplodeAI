import type { Lesson, RagResult } from '../../api/types'
import type { AssemblySpec, Readouts } from '../../engine/types'
import { linkKey } from '../../engine/types'

export function lessonToSpec(lesson: Lesson): AssemblySpec {
  return {
    parts: lesson.components.map((c) => ({
      id: c.id,
      label: c.label,
      group: c.phase,
      shape: c.geometry.shape,
      size: c.geometry.size,
      position: c.position,
      explode: c.explode,
    })),
    links: lesson.connections.map((c) => ({ source: c.source, target: c.target, label: c.payload })),
  }
}

const METHOD_LABEL = { dense: 'DENSE', bm25: 'BM25', hybrid: 'HYBRID · RRF' } as const

/** Real values from the last experiment run, shown as callouts in the scene. */
export function readoutsFromResult(r: RagResult | null): Readouts | undefined {
  if (!r) return undefined
  const n = r.chunks.length
  const k = r.retrieved.length
  return {
    parts: {
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
      [linkKey({ source: 'corpus', target: 'chunker' })]: `${r.corpus.documents.length}`,
      [linkKey({ source: 'chunker', target: 'embedder' })]: `${n}`,
      [linkKey({ source: 'embedder', target: 'vector_index' })]: `${n}×${r.embedding.dim}`,
      [linkKey({ source: 'query_encoder', target: 'retriever' })]: `1×${r.embedding.dim}`,
      [linkKey({ source: 'retriever', target: 'prompt_builder' })]: `${k}`,
      [linkKey({ source: 'prompt_builder', target: 'generator' })]: `${r.prompt.included.length} in · ${r.prompt.dropped.length} dropped`,
    },
  }
}

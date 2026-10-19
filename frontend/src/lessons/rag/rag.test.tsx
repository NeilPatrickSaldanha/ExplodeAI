import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import type { RagResult } from '../../api/types'
import { KindBadge } from '../../components/controls'
import { readoutsFromResult } from './adapter'
import { moveItem, scrambled } from './rebuildOrder'
import { AnswerView, ChunkDocView, PromptView } from './ResultViews'

const deps = {
  corpus: [],
  chunker: ['corpus'],
  embedder: ['chunker'],
  vector_index: ['embedder'],
  query_encoder: [],
  retriever: ['vector_index', 'query_encoder'],
  prompt_builder: ['retriever'],
  generator: ['prompt_builder'],
}

const isValid = (order: string[]) => {
  const pos = new Map(order.map((s, i) => [s, i]))
  return Object.entries(deps).every(([s, needs]) => needs.every((n) => pos.get(n)! < pos.get(s)!))
}

const result: RagResult = {
  params: { corpus_id: 'c', query: 'q', strategy: 'fixed', chunk_size: 3, overlap: 1, embedder: 'lexical-hashing', method: 'hybrid', top_k: 1, context_budget_words: 3 },
  corpus: { id: 'c', note: 'n', documents: [{ id: 'd', title: 'D', text: 'one two three four five' }] },
  chunks: [
    { id: 'd#0', doc_id: 'd', index: 0, text: 'one two three', start: 0, end: 13, words: 3, point: [0, 0, 0], dense_score: 0.5, dense_rank: 1, bm25_score: 1, bm25_rank: 1 },
    { id: 'd#1', doc_id: 'd', index: 1, text: 'three four five', start: 8, end: 23, words: 3, point: [1, 0, 0], dense_score: 0.1, dense_rank: 2, bm25_score: 0, bm25_rank: 2 },
  ],
  embedding: { name: 'tfidf-hashing-1024', kind: 'lexical-hashing', dim: 1024 },
  query: { text: 'q', point: [0, 0, 0] },
  projection: { method: 'pca', explained_variance: 0.5 },
  retrieved: [{ chunk_id: 'd#0', score: 0.03, rank: 1 }],
  prompt: { text: '<documents>…</documents>\n\nQuestion: q', included: ['d#0'], dropped: ['d#1'], context_words: 3, budget_words: 3 },
  answer: { mode: 'extractive-baseline', is_llm: false, text: 'one two three [d#0]', sentences: [{ text: 'one two three', source: 'd#0' }] },
  timings_ms: {},
  stages: [],
}

describe('rebuild helpers', () => {
  it('never starts the puzzle already solved', () => {
    const order = scrambled(Object.keys(deps), deps)
    expect([...order].sort()).toEqual(Object.keys(deps).sort())
    expect(isValid(order)).toBe(false)
  })

  it('moves items and ignores out-of-range moves', () => {
    expect(moveItem(['a', 'b', 'c'], 0, 2)).toEqual(['b', 'c', 'a'])
    const same = ['a', 'b']
    expect(moveItem(same, 0, -1)).toBe(same)
  })
})

describe('result views', () => {
  it('marks overlap and retrieved text in the document view', () => {
    const { container } = render(<ChunkDocView result={result} />)
    expect(container.querySelector('.run--overlap')).toHaveTextContent('three')
    expect(container.querySelector('.run--hit')).toBeInTheDocument()
    expect(screen.getByText('start of d#1')).toBeInTheDocument()
  })

  it('reports dropped chunks in the prompt view', () => {
    render(<PromptView result={result} />)
    expect(screen.getByRole('status')).toHaveTextContent('d#1')
  })

  it('labels the offline answer as not an LLM', () => {
    render(<AnswerView result={result} />)
    expect(screen.getByText(/extractive baseline/)).toBeInTheDocument()
    expect(screen.getByText('[d#0]')).toBeInTheDocument()
  })

  it('every visual kind renders with text, not colour alone', () => {
    render(<KindBadge visual={{ id: 'x', kind: 'simulation', label: 'Simulation', description: 'd' }} />)
    expect(screen.getByText('Simulation')).toBeInTheDocument()
  })
})

describe('scene readouts', () => {
  it('come from the real run, including dropped chunks', () => {
    const r = readoutsFromResult(result)!
    expect(r.parts!.chunker).toBe('2 CHUNKS · FIXED')
    expect(r.parts!.retriever).toBe('TOP-1 · HYBRID · RRF')
    expect(r.parts!.generator).toContain('NOT AN LLM')
    expect(r.links!['prompt_builder->generator']).toBe('1 in · 1 dropped')
  })
})

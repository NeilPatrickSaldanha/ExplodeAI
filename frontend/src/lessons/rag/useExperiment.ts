import { useCallback, useEffect, useRef, useState } from 'react'
import { api } from '../../api/client'
import type { RagParams, RagResult } from '../../api/types'

export const DEFAULT_PARAMS: RagParams = {
  corpus_id: 'ridgeline-help-centre',
  query: 'How long do I have to return a bike?',
  strategy: 'sentence',
  chunk_size: 40,
  overlap: 0,
  embedder: 'lexical-hashing',
  method: 'dense',
  top_k: 3,
  context_budget_words: 200,
}

/** Experiment state with debounced auto-run. Every run is a real backend execution. */
export function useExperiment(initial: Partial<RagParams> = {}) {
  const [params, setParams] = useState<RagParams>({ ...DEFAULT_PARAMS, ...initial })
  const [result, setResult] = useState<RagResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const seq = useRef(0)

  const run = useCallback(async (p: RagParams) => {
    const mine = ++seq.current
    setLoading(true)
    try {
      const r = await api.runRag(p)
      if (mine === seq.current) {
        setResult(r)
        setError(null)
      }
    } catch (e) {
      if (mine === seq.current) setError(e instanceof Error ? e.message : 'Experiment failed')
    } finally {
      if (mine === seq.current) setLoading(false)
    }
  }, [])

  useEffect(() => {
    const id = setTimeout(() => run(params), 300)
    return () => clearTimeout(id)
  }, [params, run])

  const update = useCallback(<K extends keyof RagParams>(key: K, value: RagParams[K]) => {
    setParams((p) => {
      const next = { ...p, [key]: value }
      // Keep the invariant overlap < chunk_size so the UI never sends an invalid run.
      if (next.overlap >= next.chunk_size) next.overlap = Math.max(0, next.chunk_size - 1)
      return next
    })
  }, [])

  return { params, setParams, update, result, setResult, error, loading }
}

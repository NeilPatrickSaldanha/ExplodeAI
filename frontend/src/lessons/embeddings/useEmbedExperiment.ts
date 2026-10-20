import { useCallback, useEffect, useRef, useState } from 'react'
import { api } from '../../api/client'
import type { EmbedParams, EmbedResult } from '../../api/types'

export const DEFAULT_PARAMS: EmbedParams = {
  library_id: 'four-topics',
  text: 'A puppy playing fetch in the park',
  library_embedder: 'neural',
  query_embedder: 'neural',
  pooling: 'cls',
  normalize: true,
  metric: 'cosine',
  query_instruction: false,
  top_k: 5,
}

/** Embeddings experiment state with debounced auto-run. Every run is a real backend execution. */
export function useEmbedExperiment(initial: Partial<EmbedParams> = {}) {
  const [params, setParams] = useState<EmbedParams>({ ...DEFAULT_PARAMS, ...initial })
  const [result, setResult] = useState<EmbedResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const seq = useRef(0)

  const run = useCallback(async (p: EmbedParams) => {
    const mine = ++seq.current
    setLoading(true)
    try {
      const r = await api.runEmbed(p)
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
    if (!params.text.trim()) return
    const id = setTimeout(() => run(params), 300)
    return () => clearTimeout(id)
  }, [params, run])

  const update = useCallback(<K extends keyof EmbedParams>(key: K, value: EmbedParams[K]) => {
    setParams((p) => ({ ...p, [key]: value }))
  }, [])

  return { params, setParams, update, result, setResult, error, loading }
}

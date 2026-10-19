import { useCallback, useEffect, useRef, useState } from 'react'
import { api } from '../../api/client'
import type { TokenizeParams, TokenizeResult } from '../../api/types'

export const DEFAULT_PARAMS: TokenizeParams = {
  corpus_id: 'greyhaven-keepers-log',
  text: 'The keeper lit the lantern at dusk.',
  merges: 100,
  base: 'bytes',
  pre_tokenizer: 'words',
  merge_order: 'learned',
}

/** Tokenizer experiment state with debounced auto-run. Every run is a real backend execution. */
export function useTokenizeExperiment(initial: Partial<TokenizeParams> = {}) {
  const [params, setParams] = useState<TokenizeParams>({ ...DEFAULT_PARAMS, ...initial })
  const [result, setResult] = useState<TokenizeResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const seq = useRef(0)

  const run = useCallback(async (p: TokenizeParams) => {
    const mine = ++seq.current
    setLoading(true)
    try {
      const r = await api.runTokenize(p)
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
    if (!params.text) return
    const id = setTimeout(() => run(params), 250)
    return () => clearTimeout(id)
  }, [params, run])

  const update = useCallback(<K extends keyof TokenizeParams>(key: K, value: TokenizeParams[K]) => {
    setParams((p) => ({ ...p, [key]: value }))
  }, [])

  return { params, setParams, update, result, setResult, error, loading }
}

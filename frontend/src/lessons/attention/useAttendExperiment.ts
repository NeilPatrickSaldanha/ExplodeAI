import { useCallback, useEffect, useRef, useState } from 'react'
import { api } from '../../api/client'
import type { AttendParams, AttendResult } from '../../api/types'

export const DEFAULT_PARAMS: AttendParams = {
  text: 'the cat sat on the mat',
  heads: 2,
  scale: true,
  causal: false,
  position: true,
  head: 0,
}

/** Attention experiment state with debounced auto-run. Every run is a real backend execution. */
export function useAttendExperiment(initial: Partial<AttendParams> = {}) {
  const [params, setParams] = useState<AttendParams>({ ...DEFAULT_PARAMS, ...initial })
  const [result, setResult] = useState<AttendResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const seq = useRef(0)

  const run = useCallback(async (p: AttendParams) => {
    const mine = ++seq.current
    setLoading(true)
    try {
      const r = await api.runAttend(p)
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
    const id = setTimeout(() => run(params), 250)
    return () => clearTimeout(id)
  }, [params, run])

  const update = useCallback(<K extends keyof AttendParams>(key: K, value: AttendParams[K]) => {
    setParams((p) => ({ ...p, [key]: value }))
  }, [])

  return { params, setParams, update, result, setResult, error, loading }
}

import { useCallback, useEffect, useRef, useState } from 'react'
import { api } from '../../api/client'
import type { AgentParams, AgentResult } from '../../api/types'

export const DEFAULT_PARAMS: AgentParams = {
  goal: "Hi! I'd like to return my E-Trail from order 1001. Can I get a refund?",
  descriptions: 'detailed',
  validate_args: true,
  max_steps: 8,
  require_approval: true,
  approve: false,
  refund_tool: true,
  poisoned_doc: false,
}

/** Agent experiment state with debounced auto-run. Every run is a real backend execution of the loop. */
export function useAgentExperiment(initial: Partial<AgentParams> = {}) {
  const [params, setParams] = useState<AgentParams>({ ...DEFAULT_PARAMS, ...initial })
  const [result, setResult] = useState<AgentResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const seq = useRef(0)

  const run = useCallback(async (p: AgentParams) => {
    const mine = ++seq.current
    setLoading(true)
    try {
      const r = await api.runAgent(p)
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
    if (params.goal.trim().length < 3) return
    const id = setTimeout(() => run(params), 250)
    return () => clearTimeout(id)
  }, [params, run])

  // Changing any setting takes back an earlier approval: a person approves one specific run.
  const update = useCallback(<K extends keyof AgentParams>(key: K, value: AgentParams[K]) => {
    setParams((p) => ({ ...p, [key]: value, ...(key === 'approve' ? {} : { approve: false }) }))
  }, [])

  return { params, setParams, update, result, setResult, error, loading }
}

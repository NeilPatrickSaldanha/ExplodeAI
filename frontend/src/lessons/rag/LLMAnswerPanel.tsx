import { Lock, Sparkle } from '@phosphor-icons/react'
import { useEffect, useState } from 'react'
import { api, ApiError } from '../../api/client'
import type { AIStatus, LLMAnswer, RagParams } from '../../api/types'
import { Segmented } from '../../components/controls'

const usd = (n: number) => (n < 0.01 ? `$${n.toFixed(5)}` : `$${n.toFixed(2)}`)

/**
 * Optional paid step: the same assembled prompt, answered by a real language model.
 * Off unless the backend has a key, AI_FEATURES_ENABLED and an allow-listed price.
 * The worst-case cost is shown before the click; the click is the per-request
 * confirmation; the actual cost comes back from the provider's token counts.
 * The parent keys this panel by the experiment settings, so an answer never
 * outlives the prompt it was generated from.
 */
export function LLMAnswerPanel({ params }: { params: RagParams }) {
  const [status, setStatus] = useState<AIStatus | null>(null)
  const [choice, setChoice] = useState<string | null>(null)
  const [estimate, setEstimate] = useState<number | null>(null)
  const [answer, setAnswer] = useState<LLMAnswer | null>(null)
  const [state, setState] = useState<'idle' | 'loading' | 'error'>('idle')
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.aiStatus().then(setStatus).catch(() => setStatus(null))
  }, [])

  // Cheapest first, so the default choice is the cheapest usable model.
  const usable = (status?.allowed_models.filter((m) => m.usable) ?? []).sort(
    (a, b) => a.input_usd_per_million_tokens + a.output_usd_per_million_tokens - (b.input_usd_per_million_tokens + b.output_usd_per_million_tokens),
  )
  const selected = usable.find((m) => `${m.provider}/${m.model}` === choice) ?? usable[0]

  useEffect(() => {
    if (!status?.enabled || !selected) return
    let live = true
    api
      .estimateRagAnswer(params, selected.provider, selected.model)
      .then((e) => live && setEstimate(e.max_cost_usd))
      .catch(() => live && setEstimate(null))
    return () => {
      live = false
    }
  }, [status?.enabled, selected, params])

  if (!status) return null
  const limits = status.limits
  const budget = (
    <span className="label">
      {usd(limits.spent_total_usd)} OF {usd(limits.total_budget_usd)} BUDGET USED
    </span>
  )

  if (!status.enabled || usable.length === 0) {
    return (
      <section className="llm llm--off" aria-labelledby="llm-title">
        <h4 id="llm-title" className="llm__title">
          <Lock aria-hidden /> Real LLM answer: off
        </h4>
        <p className="llm__note">
          {status.emergency_disabled
            ? 'Paid AI is switched off by the kill switch.'
            : !status.enabled
              ? 'Paid AI is disabled on this server.'
              : 'No API key is configured. Add ANTHROPIC_API_KEY, OPENAI_API_KEY or GEMINI_API_KEY to backend/.env and restart the backend.'}
        </p>
        {budget}
      </section>
    )
  }

  const run = async () => {
    setState('loading')
    setError(null)
    try {
      const out = await api.ragAnswer(params, selected.provider, selected.model)
      setAnswer(out)
      setState('idle')
      setStatus((s) => (s ? { ...s, limits: { ...s.limits, spent_total_usd: out.spent_total_usd } } : s))
    } catch (e) {
      setState('error')
      setError(e instanceof ApiError ? e.message : 'The request failed.')
    }
  }

  return (
    <section className="llm" aria-labelledby="llm-title">
      <h4 id="llm-title" className="llm__title">
        <Sparkle aria-hidden /> Ask a real LLM (paid)
      </h4>
      <p className="llm__note">Same assembled prompt, answered by a language model instead of the extractive baseline.</p>
      {usable.length > 1 && (
        <Segmented
          label="Model"
          value={`${selected.provider}/${selected.model}`}
          onChange={setChoice}
          options={usable.map((m) => ({ value: `${m.provider}/${m.model}`, label: m.model }))}
        />
      )}
      <button type="button" className="btn btn--primary" onClick={run} disabled={state === 'loading'} data-state={state === 'loading' ? 'loading' : undefined}>
        {state === 'loading' ? 'Generating…' : `Generate${estimate !== null ? ` · max ${usd(estimate)}` : ''}`}
      </button>
      {budget}
      {error && (
        <p className="notice notice--error" role="alert">
          {error}
        </p>
      )}
      {answer && (
        <div className="llm__answer" aria-live="polite">
          <span className="kind-badge kind-badge--real_execution">Real execution · LLM · paid</span>
          <p className="answerview__text">{answer.text}</p>
          <p className="label">
            {answer.model} · {answer.input_tokens ?? '?'} IN / {answer.output_tokens ?? '?'} OUT TOKENS · COST {usd(answer.cost_usd)}
          </p>
        </div>
      )}
    </section>
  )
}

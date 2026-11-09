import type { AgentAblationOutcome } from '../../api/types'
import { STATUS_TEXT } from './agentText'
import { Named } from '../../voice'

/** One side of the agent "what breaks if removed?" comparison. */
export function agentOutcome(o: AgentAblationOutcome) {
  return (
    <>
      <dl className="outcome__stats">
        <div><dt><Named label="Ended" /></dt><dd>{STATUS_TEXT[o.status]}</dd></div>
        <div><dt><Named label="Steps" /></dt><dd>{o.steps}</dd></div>
        <div><dt><Named label="Tools run" /></dt><dd>{o.tool_runs}</dd></div>
        <div><dt><Named label="Bad calls caught" /></dt><dd>{o.invalid_calls}</dd></div>
        <div><dt><Named label="Tokens read" /></dt><dd>{o.tokens_total.toLocaleString()}</dd></div>
      </dl>
      <p className="outcome__answer">{o.answer ?? 'No answer.'}</p>
      {o.calls.length > 0 && (
        <p className="outcome__notes">
          Calls: {o.calls.slice(0, 5).join(' → ')}
          {o.calls.length > 5 ? ` … (${o.calls.length} in all)` : ''}
        </p>
      )}
      {o.notes.length > 0 && <p className="outcome__notes">{o.notes.join(' · ')}</p>}
    </>
  )
}

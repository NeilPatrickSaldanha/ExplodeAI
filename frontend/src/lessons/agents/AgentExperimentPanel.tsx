import * as Tabs from '@radix-ui/react-tabs'
import type { AgentParams, AgentResult, Lesson, Visual } from '../../api/types'
import { KindBadge, Segmented } from '../../components/controls'
import { ApprovalCard, ContextChart, ConversationView, LoopTrace, StatsStrip, ToolsView } from './AgentViews'

interface Props {
  lesson: Lesson
  params: AgentParams
  update: <K extends keyof AgentParams>(key: K, value: AgentParams[K]) => void
  result: AgentResult | null
  loading: boolean
  error: string | null
  locked?: (keyof AgentParams)[]
}

const onOff = (v: boolean) => (v ? 'on' : 'off')
const LIMITS = ['3', '8', '20', 'none'] as const

export function AgentExperimentPanel({ lesson, params, update, result, loading, error, locked = [] }: Props) {
  const isLocked = (k: keyof AgentParams) => locked.includes(k)
  const visual = (id: string) => lesson.visuals.find((v) => v.id === id) as Visual
  const presetNote = lesson.experiment.presets.find((p) => p.text === params.goal)?.note
  return (
    <div className="experiment" aria-busy={loading}>
      <div className="experiment__head">
        <KindBadge visual={visual('experiment')} />
        <KindBadge visual={visual('decider')} />
        <span className="label" role="status">
          {loading ? 'RUNNING…' : error ? 'ERROR' : result ? `STAND-IN DECIDER · ${result.stats.steps} STEP${result.stats.steps === 1 ? '' : 'S'}` : ''}
        </span>
      </div>
      <p className="experiment__corpus">{lesson.experiment.corpus_note}</p>

      <div className={`field${isLocked('goal') ? ' is-locked' : ''}`}>
        <label className="label" htmlFor="agent-goal">
          What the customer writes
        </label>
        <input id="agent-goal" className="input" value={params.goal} maxLength={300} disabled={isLocked('goal')} onChange={(e) => update('goal', e.target.value)} />
        {!isLocked('goal') && (
          <div className="presets" role="group" aria-label="Example requests">
            {lesson.experiment.presets.map((p) => (
              <button key={p.label} type="button" className="chip" onClick={() => update('goal', p.text ?? '')}>
                {p.label}
              </button>
            ))}
          </div>
        )}
        {presetNote && <p className="notice">{presetNote}</p>}
      </div>

      <div className="controls">
        <Segmented label="Tool descriptions" value={params.descriptions} disabled={isLocked('descriptions')} onChange={(v) => update('descriptions', v)}
          options={[{ value: 'detailed', label: 'Detailed' }, { value: 'vague', label: 'Vague' }]} />
        <Segmented label="Check arguments before running" value={onOff(params.validate_args)} disabled={isLocked('validate_args')} onChange={(v) => update('validate_args', v === 'on')}
          options={[{ value: 'on', label: 'On' }, { value: 'off', label: 'Off' }]} />
        <Segmented label="Step limit" value={params.max_steps === null ? 'none' : String(params.max_steps)} disabled={isLocked('max_steps')}
          onChange={(v) => update('max_steps', v === 'none' ? null : Number(v))}
          options={LIMITS.map((l) => ({ value: l, label: l === 'none' ? 'None' : l }))} />
        <Segmented label="Person approves refunds" value={onOff(params.require_approval)} disabled={isLocked('require_approval')} onChange={(v) => update('require_approval', v === 'on')}
          options={[{ value: 'on', label: 'On' }, { value: 'off', label: 'Off' }]} />
        <Segmented label="Refund tool available" value={onOff(params.refund_tool)} disabled={isLocked('refund_tool')} onChange={(v) => update('refund_tool', v === 'on')}
          options={[{ value: 'on', label: 'On' }, { value: 'off', label: 'Off' }]} />
        <Segmented label="Forum post in the help centre" value={onOff(params.poisoned_doc)} disabled={isLocked('poisoned_doc')} onChange={(v) => update('poisoned_doc', v === 'on')}
          options={[{ value: 'off', label: 'Off' }, { value: 'on', label: 'On' }]} />
      </div>

      {error && (
        <p className="notice notice--error" role="alert">
          {error}
        </p>
      )}

      {result && (
        <>
          <p className="notice" role="note">
            {result.model.note}
          </p>
          <ApprovalCard result={result} onApprove={() => update('approve', true)} />
          <Tabs.Root defaultValue="loop" className="rtabs">
            <Tabs.List className="rtabs__list" aria-label="Experiment results">
              <Tabs.Trigger value="loop" className="rtabs__tab">The loop</Tabs.Trigger>
              <Tabs.Trigger value="conversation" className="rtabs__tab">What the model reads</Tabs.Trigger>
              <Tabs.Trigger value="tools" className="rtabs__tab">Tools</Tabs.Trigger>
              <Tabs.Trigger value="context" className="rtabs__tab">Token cost</Tabs.Trigger>
            </Tabs.List>
            <Tabs.Content value="loop" className="rtabs__panel">
              <LoopTrace result={result} />
              <StatsStrip result={result} />
            </Tabs.Content>
            <Tabs.Content value="conversation" className="rtabs__panel">
              <ConversationView result={result} />
            </Tabs.Content>
            <Tabs.Content value="tools" className="rtabs__panel">
              <ToolsView tools={result.tools} />
            </Tabs.Content>
            <Tabs.Content value="context" className="rtabs__panel">
              <ContextChart result={result} />
            </Tabs.Content>
          </Tabs.Root>
        </>
      )}
    </div>
  )
}

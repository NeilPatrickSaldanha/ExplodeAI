import type { AgentStatus } from '../../api/types'

export const STATUS_TEXT: Record<AgentStatus, string> = {
  running: 'Running',
  answered: 'Answered',
  needs_approval: 'Waiting for a person to approve',
  step_limit: 'Stopped by the step limit, no answer',
  safety_cap: 'Cut off by the experiment’s safety cap, no step limit set',
  no_decision: 'Nothing decides, so nothing happens',
  no_goal: 'No goal, so nothing to do',
}

export const fmt = (v: unknown): string => (typeof v === 'string' ? v : JSON.stringify(v))

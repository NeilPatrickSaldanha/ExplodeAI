import type { AgentResult, Lesson } from '../../api/types'
import { spreadParts } from '../../engine/math'
import type { AssemblySpec, Readouts } from '../../engine/types'
import { linkKey } from '../../engine/types'

/** How far this lesson's parts spread when fully exploded (x, y, z). */
const SPREAD: [number, number, number] = [3, 1.4, 2.2]

export function lessonToSpec(lesson: Lesson): AssemblySpec {
  return {
    parts: spreadParts(
      lesson.components.map((c, i) => ({
        id: c.id,
        label: c.label,
        group: c.phase,
        shape: c.geometry.shape,
        size: c.geometry.size,
        position: c.position,
        explode: c.explode,
        subtitle: c.subtitle ?? undefined,
        number: String(i + 1).padStart(2, '0'),
      })),
      SPREAD,
    ),
    links: lesson.connections.map((c) => ({ source: c.source, target: c.target, label: c.payload, kind: c.flow ?? 'document' })),
  }
}

const link = (source: string, target: string) => linkKey({ source, target })

const STATUS_TEXT: Record<AgentResult['status'], string> = {
  running: 'RUNNING',
  answered: 'ANSWERED',
  needs_approval: 'WAITING FOR A PERSON',
  step_limit: 'STOPPED AT LIMIT',
  safety_cap: 'CUT OFF BY SAFETY CAP',
  no_decision: 'NOTHING DECIDES',
  no_goal: 'NO GOAL',
}

/** Real values from the last run, shown as callouts in the scene. */
export function readoutsFromResult(r: AgentResult | null): Readouts | undefined {
  if (!r) return undefined
  const s = r.stats
  return {
    parts: {
      goal: `${r.params.goal.split(/\s+/).length} WORDS`,
      tools: `${r.tools.length} TOOLS`,
      decide: `${s.steps} DECISIONS`,
      validate: r.params.validate_args ? `${s.invalid_calls} CAUGHT` : 'OFF',
      execute: `${s.tool_runs} RUNS`,
      observe: `${r.messages.filter((m) => m.role === 'tool').length} RESULTS`,
      context: `${s.tokens_last.toLocaleString()} TOKENS`,
      stop: STATUS_TEXT[r.status],
    },
    links: {
      [link('tools', 'decide')]: `${r.tools.length} definitions`,
      [link('decide', 'validate')]: 'tool + arguments',
      [link('validate', 'execute')]: 'checked call',
      [link('execute', 'observe')]: 'raw result',
      [link('observe', 'context')]: 'tool_result',
      [link('context', 'decide')]: `${s.tokens_last.toLocaleString()} tokens`,
      [link('decide', 'stop')]: r.answer ? 'final answer' : 'no answer',
    },
  }
}

import { useMemo, useState } from 'react'
import { api } from '../../api/client'
import type { AgentParams, Challenge, Lesson } from '../../api/types'
import { Challenges } from '../rag/Challenges'
import { Rebuild } from '../rag/Rebuild'
import { TimingStrip } from '../rag/ResultViews'
import { BreaksCard } from '../shared/cine/BreaksCard'
import { CineLesson } from '../shared/cine/CineLesson'
import type { FlowLabels } from '../shared/cine/FlowLegend'
import { lessonToSpec, readoutsFromResult } from './adapter'
import { agentOutcome } from './agentOutcome'
import { AgentExperimentPanel } from './AgentExperimentPanel'
import { AgentStageIO } from './AgentStageIO'
import './agents.css'
import { DEFAULT_PARAMS, useAgentExperiment } from './useAgentExperiment'

type AgentChallenge = Challenge<AgentParams>

const FLOW_LABELS: FlowLabels = { document: 'Messages', vector: 'Tool calls & results', query: 'The goal' }

export function AgentLessonPage({ lesson }: { lesson: Lesson }) {
  const spec = useMemo(() => lessonToSpec(lesson), [lesson])
  const challenges = lesson.challenges as unknown as AgentChallenge[]
  const [challenge, setChallenge] = useState<AgentChallenge | null>(null)
  const exp = useAgentExperiment()

  const startChallenge = (c: AgentChallenge) => {
    setChallenge(c)
    exp.setParams({ ...DEFAULT_PARAMS, ...c.broken_params })
  }
  const exitChallenge = () => {
    setChallenge(null)
    exp.setParams(DEFAULT_PARAMS)
  }

  return (
    <CineLesson
      lesson={lesson}
      spec={spec}
      readouts={readoutsFromResult(exp.result)}
      live={!!exp.result}
      eyebrow={`LESSON 05 · GOAL → DECIDE → ACT → OBSERVE → REPEAT · ${lesson.estimated_minutes} MIN`}
      title={
        <>
          tool-using agents,&nbsp;<em>exploded</em>
        </>
      }
      summary="See a model in a loop: it decides, the application acts, the result goes back in. Click any part to see what goes in, what comes out, and what breaks without it."
      sceneTitle="Exploded view of one tool-using agent loop"
      flowLabels={FLOW_LABELS}
      renderIO={(c) => <AgentStageIO component={c} result={exp.result} />}
      renderBreaks={(c) => (
        <BreaksCard
          key={`${c.id}|${JSON.stringify(exp.params)}`}
          component={c}
          run={() => api.ablateAgent(exp.params, c.id)}
          renderOutcome={agentOutcome}
          visual={lesson.visuals.find((v) => v.id === 'ablation')}
          system="loop"
        />
      )}
      onModeChange={(m) => {
        if (m !== 'challenges' && challenge) exitChallenge()
      }}
      timings={<TimingStrip result={exp.result} />}
      tabs={(progress) => ({
        experiment: <AgentExperimentPanel lesson={lesson} {...exp} />,
        challenges: (
          <>
            <Challenges
              challenges={challenges}
              active={challenge}
              solved={progress.solved}
              intro="Each setup below makes the agent misbehave for one specific reason. Find it in the experiment, then fix it with the controls left unlocked. The server re-runs your settings and checks the result."
              onCheck={(c) => api.checkAgentChallenge(lesson.id, c.id, exp.params)}
              onStart={startChallenge}
              onExit={exitChallenge}
              onSolved={(id) => progress.markSolved(id)}
            />
            {challenge && <AgentExperimentPanel lesson={lesson} {...exp} locked={challenge.locked_params} />}
          </>
        ),
        rebuild: <Rebuild lesson={lesson} solved={progress.rebuilt} onSolved={progress.markRebuilt} />,
      })}
    />
  )
}

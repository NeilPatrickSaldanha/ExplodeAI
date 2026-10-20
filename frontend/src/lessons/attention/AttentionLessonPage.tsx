import { useMemo, useState } from 'react'
import { api } from '../../api/client'
import type { AttendParams, Challenge, Lesson } from '../../api/types'
import { Challenges } from '../rag/Challenges'
import { Rebuild } from '../rag/Rebuild'
import { TimingStrip } from '../rag/ResultViews'
import { BreaksCard } from '../shared/cine/BreaksCard'
import { CineLesson } from '../shared/cine/CineLesson'
import type { FlowLabels } from '../shared/cine/FlowLegend'
import { lessonToSpec, readoutsFromResult } from './adapter'
import { AttendExperimentPanel } from './AttendExperimentPanel'
import { attendOutcome } from './attendOutcome'
import { AttendStageIO } from './AttendStageIO'
import './attention.css'
import { DEFAULT_PARAMS, useAttendExperiment } from './useAttendExperiment'

type AttendChallenge = Challenge<AttendParams>

const FLOW_LABELS: FlowLabels = { document: 'Words', vector: 'Vectors', query: 'Scores & weights' }

export function AttentionLessonPage({ lesson }: { lesson: Lesson }) {
  const spec = useMemo(() => lessonToSpec(lesson), [lesson])
  const challenges = lesson.challenges as unknown as AttendChallenge[]
  const [challenge, setChallenge] = useState<AttendChallenge | null>(null)
  const exp = useAttendExperiment()

  const startChallenge = (c: AttendChallenge) => {
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
      eyebrow={`LESSON 04 · WORDS → QUERIES, KEYS, VALUES → MIXED MEANING · ${lesson.estimated_minutes} MIN`}
      title={
        <>
          attention,&nbsp;<em>exploded</em>
        </>
      }
      summary="Watch every word decide which other words to look at, then blend what it finds. Click any part to see what goes in, what comes out, and what breaks without it."
      sceneTitle="Exploded view of one self-attention layer"
      flowLabels={FLOW_LABELS}
      renderIO={(c) => <AttendStageIO component={c} result={exp.result} />}
      renderBreaks={(c) => (
        <BreaksCard
          key={`${c.id}|${JSON.stringify(exp.params)}`}
          component={c}
          run={() => api.ablateAttend(exp.params, c.id)}
          renderOutcome={attendOutcome}
          visual={lesson.visuals.find((v) => v.id === 'ablation')}
          system="layer"
        />
      )}
      onModeChange={(m) => {
        if (m !== 'challenges' && challenge) exitChallenge()
      }}
      timings={<TimingStrip result={exp.result} />}
      tabs={(progress) => ({
        experiment: <AttendExperimentPanel lesson={lesson} {...exp} />,
        challenges: (
          <>
            <Challenges
              challenges={challenges}
              active={challenge}
              solved={progress.solved}
              intro="Each setup below makes attention misbehave for one specific reason. Find it in the experiment, then fix it with the controls left unlocked. The server re-runs your settings and checks the result."
              onCheck={(c) => api.checkAttendChallenge(lesson.id, c.id, exp.params)}
              onStart={startChallenge}
              onExit={exitChallenge}
              onSolved={(id) => progress.markSolved(id)}
            />
            {challenge && <AttendExperimentPanel lesson={lesson} {...exp} locked={challenge.locked_params} />}
          </>
        ),
        rebuild: <Rebuild lesson={lesson} solved={progress.rebuilt} onSolved={progress.markRebuilt} />,
      })}
    />
  )
}

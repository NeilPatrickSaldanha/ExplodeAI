import { useEffect, useMemo, useState } from 'react'
import { api } from '../../api/client'
import type { Challenge, Lesson, RagConfig } from '../../api/types'
import { BreaksCard } from '../shared/cine/BreaksCard'
import { CineLesson } from '../shared/cine/CineLesson'
import type { FlowLabels } from '../shared/cine/FlowLegend'
import { lessonToSpec, readoutsFromResult } from './adapter'
import { Challenges } from './Challenges'
import { ExperimentPanel } from './ExperimentPanel'
import { ragOutcome } from './ragOutcome'
import { Rebuild } from './Rebuild'
import { TimingStrip } from './ResultViews'
import { StageIO } from './StageIO'
import { DEFAULT_PARAMS, useExperiment } from './useExperiment'

const FLOW_LABELS: FlowLabels = { document: 'Text flow', vector: 'Vector flow', query: 'Your question' }

export function RagLessonPage({ lesson }: { lesson: Lesson }) {
  const spec = useMemo(() => lessonToSpec(lesson), [lesson])
  const [challenge, setChallenge] = useState<Challenge | null>(null)
  const [config, setConfig] = useState<RagConfig | null>(null)
  const exp = useExperiment()

  useEffect(() => {
    api.ragConfig().then(setConfig).catch(() => setConfig(null))
  }, [])

  const startChallenge = (c: Challenge) => {
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
      eyebrow={`LESSON 01 · INGESTION → GENERATION · ${lesson.estimated_minutes} MIN`}
      title={
        <>
          retrieval-augmented generation,&nbsp;<em>exploded</em>
        </>
      }
      summary="Follow a real RAG pipeline through the machine. Click any part to see what goes in, what comes out, and what breaks without it."
      sceneTitle="Exploded view of a retrieval-augmented generation pipeline"
      flowLabels={FLOW_LABELS}
      renderIO={(c) => <StageIO component={c} result={exp.result} />}
      renderBreaks={(c) => (
        <BreaksCard
          key={`${c.id}|${JSON.stringify(exp.params)}`}
          component={c}
          run={() => api.ablate(exp.params, c.id)}
          renderOutcome={ragOutcome}
          visual={lesson.visuals.find((v) => v.id === 'ablation')}
        />
      )}
      onModeChange={(m) => {
        if (m !== 'challenges' && challenge) exitChallenge()
      }}
      timings={<TimingStrip result={exp.result} />}
      tabs={(progress) => ({
        experiment: <ExperimentPanel lesson={lesson} {...exp} neuralAvailable={!!config?.embedders.find((e) => e.id === 'neural-local')?.available} />,
        challenges: (
          <>
            <Challenges
              challenges={lesson.challenges}
              active={challenge}
              solved={progress.solved}
              onCheck={(c) => api.checkChallenge(lesson.id, c.id, exp.params)}
              onStart={startChallenge}
              onExit={exitChallenge}
              onSolved={(id) => progress.markSolved(id)}
            />
            {challenge && <ExperimentPanel lesson={lesson} {...exp} locked={challenge.locked_params} neuralAvailable={false} />}
          </>
        ),
        rebuild: <Rebuild lesson={lesson} solved={progress.rebuilt} onSolved={progress.markRebuilt} />,
      })}
    />
  )
}

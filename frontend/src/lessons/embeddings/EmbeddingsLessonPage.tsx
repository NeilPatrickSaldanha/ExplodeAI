import { useMemo, useState } from 'react'
import { api } from '../../api/client'
import type { Challenge, EmbedParams, Lesson } from '../../api/types'
import { Challenges } from '../rag/Challenges'
import { Rebuild } from '../rag/Rebuild'
import { TimingStrip } from '../rag/ResultViews'
import { BreaksCard } from '../shared/cine/BreaksCard'
import { CineLesson } from '../shared/cine/CineLesson'
import type { FlowLabels } from '../shared/cine/FlowLegend'
import { lessonToSpec, readoutsFromResult } from './adapter'
import { EmbedExperimentPanel } from './EmbedExperimentPanel'
import { embedOutcome } from './embedOutcome'
import './embeddings.css'
import { EmbedStageIO } from './EmbedStageIO'
import { DEFAULT_PARAMS, useEmbedExperiment } from './useEmbedExperiment'

type EmbedChallenge = Challenge<EmbedParams>

const FLOW_LABELS: FlowLabels = { document: 'Text', vector: 'Vectors', query: 'Your text' }

export function EmbeddingsLessonPage({ lesson }: { lesson: Lesson }) {
  const spec = useMemo(() => lessonToSpec(lesson), [lesson])
  const challenges = lesson.challenges as unknown as EmbedChallenge[]
  const [challenge, setChallenge] = useState<EmbedChallenge | null>(null)
  const exp = useEmbedExperiment()

  const startChallenge = (c: EmbedChallenge) => {
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
      eyebrow={`LESSON 03 · TEXT → TOKENS → VECTORS → MEANING · ${lesson.estimated_minutes} MIN`}
      title={
        <>
          embeddings,&nbsp;<em>exploded</em>
        </>
      }
      summary="Watch a sentence become 384 numbers and land near sentences that mean the same thing. Click any part to see what goes in, what comes out, and what breaks without it."
      sceneTitle="Exploded view of a sentence-embedding model"
      flowLabels={FLOW_LABELS}
      renderIO={(c) => <EmbedStageIO component={c} result={exp.result} />}
      renderBreaks={(c) => (
        <BreaksCard
          key={`${c.id}|${JSON.stringify(exp.params)}`}
          component={c}
          run={() => api.ablateEmbed(exp.params, c.id)}
          renderOutcome={embedOutcome}
          visual={lesson.visuals.find((v) => v.id === 'ablation')}
          system="model"
        />
      )}
      onModeChange={(m) => {
        if (m !== 'challenges' && challenge) exitChallenge()
      }}
      timings={<TimingStrip result={exp.result} />}
      tabs={(progress) => ({
        experiment: <EmbedExperimentPanel lesson={lesson} {...exp} />,
        challenges: (
          <>
            <Challenges
              challenges={challenges}
              active={challenge}
              solved={progress.solved}
              intro="Each setup below finds the wrong neighbours, or none, for one specific reason. Find it in the experiment, then fix it with the controls left unlocked. The server re-runs your settings and checks the result."
              onCheck={(c) => api.checkEmbedChallenge(lesson.id, c.id, exp.params)}
              onStart={startChallenge}
              onExit={exitChallenge}
              onSolved={(id) => progress.markSolved(id)}
            />
            {challenge && <EmbedExperimentPanel lesson={lesson} {...exp} locked={challenge.locked_params} />}
          </>
        ),
        rebuild: <Rebuild lesson={lesson} solved={progress.rebuilt} onSolved={progress.markRebuilt} />,
      })}
    />
  )
}

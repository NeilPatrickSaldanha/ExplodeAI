import { useEffect, useMemo, useState } from 'react'
import { ablateTokenize, api } from '../../api/client'
import type { Challenge, Lesson, TokenizeConfig, TokenizeParams } from '../../api/types'
// Lesson-agnostic pieces shared with Lesson 01.
import { Challenges } from '../rag/Challenges'
import { Rebuild } from '../rag/Rebuild'
import { TimingStrip } from '../rag/ResultViews'
import { BreaksCard } from '../shared/cine/BreaksCard'
import { CineLesson } from '../shared/cine/CineLesson'
import type { FlowLabels } from '../shared/cine/FlowLegend'
import { lessonToSpec, readoutsFromResult } from './adapter'
import { TokenizeExperimentPanel } from './TokenizeExperimentPanel'
import './tokenization.css'
import { tokOutcome } from './tokOutcome'
import { TokStageIO } from './TokStageIO'
import { DEFAULT_PARAMS, useTokenizeExperiment } from './useTokenizeExperiment'

type TokChallenge = Challenge<TokenizeParams>

const FLOW_LABELS: FlowLabels = { document: 'Text', vector: 'Symbols & ids', query: 'Your text' }

export function TokenizationLessonPage({ lesson }: { lesson: Lesson }) {
  const spec = useMemo(() => lessonToSpec(lesson), [lesson])
  const challenges = lesson.challenges as unknown as TokChallenge[]
  const [challenge, setChallenge] = useState<TokChallenge | null>(null)
  const [config, setConfig] = useState<TokenizeConfig | null>(null)
  const exp = useTokenizeExperiment()

  useEffect(() => {
    api.tokenizeConfig().then(setConfig).catch(() => setConfig(null))
  }, [])

  const startChallenge = (c: TokChallenge) => {
    setChallenge(c)
    exp.setParams({ ...DEFAULT_PARAMS, ...c.broken_params })
  }
  const exitChallenge = () => {
    setChallenge(null)
    exp.setParams(DEFAULT_PARAMS)
  }
  const maxMerges = config?.max_merges ?? 300

  return (
    <CineLesson
      lesson={lesson}
      spec={spec}
      readouts={readoutsFromResult(exp.result)}
      live={!!exp.result}
      eyebrow={`LESSON 02 · TRAINING → ENCODING → DECODING · ${lesson.estimated_minutes} MIN`}
      title={
        <>
          tokenization,&nbsp;<em>exploded</em>
        </>
      }
      summary="Watch text become token ids and come back again. Click any part to see what goes in, what comes out, and what breaks without it."
      sceneTitle="Exploded view of a byte-pair-encoding tokenizer"
      flowLabels={FLOW_LABELS}
      renderIO={(c) => <TokStageIO component={c} result={exp.result} />}
      renderBreaks={(c) => (
        <BreaksCard
          key={`${c.id}|${JSON.stringify(exp.params)}`}
          component={c}
          run={() => ablateTokenize(exp.params, c.id)}
          renderOutcome={tokOutcome}
          visual={lesson.visuals.find((v) => v.id === 'ablation')}
          system="tokenizer"
        />
      )}
      onModeChange={(m) => {
        if (m !== 'challenges' && challenge) exitChallenge()
      }}
      timings={<TimingStrip result={exp.result} />}
      tabs={(progress) => ({
        experiment: <TokenizeExperimentPanel lesson={lesson} {...exp} maxMerges={maxMerges} reducedMotion={progress.reducedMotion} />,
        challenges: (
          <>
            <Challenges
              challenges={challenges}
              active={challenge}
              solved={progress.solved}
              intro="Each tokenizer below is broken in one specific way. Find the cause in the experiment, then fix it with the controls left unlocked. The server re-runs your settings and checks the result."
              onCheck={(c) => api.checkTokenizeChallenge(lesson.id, c.id, exp.params)}
              onStart={startChallenge}
              onExit={exitChallenge}
              onSolved={(id) => progress.markSolved(id)}
            />
            {challenge && <TokenizeExperimentPanel lesson={lesson} {...exp} locked={challenge.locked_params} maxMerges={maxMerges} reducedMotion={progress.reducedMotion} />}
          </>
        ),
        rebuild: <Rebuild lesson={lesson} solved={progress.rebuilt} onSolved={progress.markRebuilt} />,
      })}
    />
  )
}

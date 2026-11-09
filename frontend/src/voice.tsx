import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'
import { LabelContext, VOICE_KEY, VoiceContext, useLabel, type Voice } from './voiceContext'

const readVoice = (): Voice => {
  try {
    return localStorage.getItem(VOICE_KEY) === 'technical' ? 'technical' : 'plain'
  } catch {
    return 'plain'
  }
}

export function VoiceProvider({ children }: { children: ReactNode }) {
  const [voice, setVoiceState] = useState<Voice>(readVoice)
  const setVoice = useCallback((v: Voice) => {
    setVoiceState(v)
    try {
      localStorage.setItem(VOICE_KEY, v)
    } catch {
      /* storage unavailable */
    }
  }, [])
  useEffect(() => {
    document.documentElement.dataset.voice = voice
  }, [voice])
  const value = useMemo(() => ({ voice, setVoice }), [voice, setVoice])
  return <VoiceContext.Provider value={value}>{children}</VoiceContext.Provider>
}

export function LabelsProvider({ labels, children }: { labels?: Record<string, string>; children: ReactNode }) {
  return <LabelContext.Provider value={labels ?? {}}>{children}</LabelContext.Provider>
}

/** A label that shows the everyday name first and the technical name small beside it. */
export function Named({ label }: { label: string }) {
  const { text, tech } = useLabel(label)
  return (
    <>
      {text}
      {tech && <span className="term"> · {tech}</span>}
    </>
  )
}

import { createContext, useContext } from 'react'

/**
 * Two ways of telling the same lesson. "plain" leads with everyday words and shows the standard
 * ("technical") name beside each one; "technical" is the original wording. Same lesson, same claims.
 */
export type Voice = 'plain' | 'technical'
export const VOICE_KEY = 'explodeai.voice'

export interface VoiceState {
  voice: Voice
  setVoice: (v: Voice) => void
}

export const VoiceContext = createContext<VoiceState>({ voice: 'plain', setVoice: () => undefined })
export const useVoice = () => useContext(VoiceContext)

/** Everyday names for controls and tabs, keyed by their technical names. Empty in the technical voice. */
export const LabelContext = createContext<Record<string, string>>({})

/** The everyday name for a control, and its technical name when the two differ. */
export function useLabel(technical: string): { text: string; tech: string | null } {
  const plain = useContext(LabelContext)[technical]
  return plain && plain !== technical ? { text: plain, tech: technical } : { text: technical, tech: null }
}

/** Plain text of a label, for accessible names and tooltips: "Everyday name (technical name)". */
export function useLabelText(technical: string): string {
  const { text, tech } = useLabel(technical)
  return tech ? `${text} (${tech})` : text
}

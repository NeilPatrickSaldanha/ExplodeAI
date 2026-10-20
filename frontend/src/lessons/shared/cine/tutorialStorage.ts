export const TUTORIAL_KEY = 'explodeai.tutorial'

/** True once the learner has finished or skipped the tutorial (or storage is unavailable). */
export function tutorialSeen(): boolean {
  try {
    return localStorage.getItem(TUTORIAL_KEY) !== null
  } catch {
    return true // storage blocked: never nag
  }
}

export function rememberTutorial(value: 'done' | 'skipped') {
  try {
    localStorage.setItem(TUTORIAL_KEY, value)
  } catch {
    /* storage unavailable */
  }
}

import { useEffect, useState } from 'react'

/** Live prefers-reduced-motion (reacts to mid-session OS changes), with a user override. */
export function useReducedMotion(override: boolean | null = null): boolean {
  const query = '(prefers-reduced-motion: reduce)'
  const [system, setSystem] = useState(() =>
    typeof window !== 'undefined' && window.matchMedia ? window.matchMedia(query).matches : false,
  )
  useEffect(() => {
    if (!window.matchMedia) return
    const mq = window.matchMedia(query)
    const onChange = (e: MediaQueryListEvent) => setSystem(e.matches)
    mq.addEventListener('change', onChange)
    return () => mq.removeEventListener('change', onChange)
  }, [])
  return override ?? system
}

let webglCache: boolean | null = null

export function hasWebGL(): boolean {
  if (webglCache !== null) return webglCache
  try {
    const canvas = document.createElement('canvas')
    webglCache = !!(canvas.getContext('webgl2') || canvas.getContext('webgl'))
  } catch {
    webglCache = false
  }
  return webglCache
}

/** Re-render when the colour theme changes (OS preference or data-theme toggle). */
export function useThemeVersion(): number {
  const [v, setV] = useState(0)
  useEffect(() => {
    const bump = () => setV((x) => x + 1)
    const mq = window.matchMedia?.('(prefers-color-scheme: light)')
    mq?.addEventListener('change', bump)
    const obs = new MutationObserver(bump)
    obs.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] })
    return () => {
      mq?.removeEventListener('change', bump)
      obs.disconnect()
    }
  }, [])
  return v
}

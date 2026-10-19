/** Deterministic shuffle that never starts in a valid order. */
export function scrambled(ids: string[], deps: Record<string, string[]>): string[] {
  const out = [...ids]
  let seed = 7
  for (let i = out.length - 1; i > 0; i--) {
    seed = (seed * 9301 + 49297) % 233280
    const j = Math.floor((seed / 233280) * (i + 1))
    ;[out[i], out[j]] = [out[j], out[i]]
  }
  const pos = new Map(out.map((s, i) => [s, i]))
  const valid = Object.entries(deps).every(([s, needs]) => needs.every((n) => pos.get(n)! < pos.get(s)!))
  return valid ? [...out].reverse() : out
}

export function moveItem<T>(list: T[], from: number, to: number): T[] {
  if (to < 0 || to >= list.length || from === to) return list
  const next = [...list]
  const [item] = next.splice(from, 1)
  next.splice(to, 0, item)
  return next
}

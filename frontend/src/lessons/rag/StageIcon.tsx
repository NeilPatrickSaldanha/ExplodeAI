import { ChatText, Cube, Database, Files, MagnifyingGlass, Scissors, Sparkle, Stack, type Icon, type IconWeight } from '@phosphor-icons/react'

const ICONS: Record<string, Icon> = { Files, Scissors, Cube, Database, ChatText, MagnifyingGlass, Stack, Sparkle }

/** Phosphor icon named in lesson content (decorative: the stage name is always shown as text). */
export function StageIcon({ name, className, weight }: { name?: string | null; className?: string; weight?: IconWeight }) {
  const Icon = (name && ICONS[name]) || Cube
  return <Icon className={className} weight={weight} aria-hidden />
}

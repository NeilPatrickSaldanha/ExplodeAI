import {
  ArrowCounterClockwise,
  ArrowsMerge,
  Books,
  Brain,
  Eye,
  FlagCheckered,
  Notebook,
  ShieldCheck,
  Target,
  Wrench,
  ChatText,
  Cube,
  Database,
  Files,
  GridFour,
  Hash,
  MagnifyingGlass,
  Scissors,
  Scroll,
  Sparkle,
  Stack,
  TextAa,
  type Icon,
  type IconWeight,
} from '@phosphor-icons/react'

const ICONS: Record<string, Icon> = {
  Files, Scissors, Cube, Database, ChatText, MagnifyingGlass, Stack, Sparkle,
  Scroll, GridFour, ArrowsMerge, Books, TextAa, Hash, ArrowCounterClockwise,
  Brain, Eye, FlagCheckered, Notebook, ShieldCheck, Target, Wrench,
}

/** Phosphor icon named in lesson content (decorative: the stage name is always shown as text). */
export function StageIcon({ name, className, weight }: { name?: string | null; className?: string; weight?: IconWeight }) {
  const Icon = (name && ICONS[name]) || Cube
  return <Icon className={className} weight={weight} aria-hidden />
}

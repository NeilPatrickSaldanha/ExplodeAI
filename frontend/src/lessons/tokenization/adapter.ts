import type { Lesson, TokenizeResult } from '../../api/types'
import type { AssemblySpec, Readouts } from '../../engine/types'
import { linkKey } from '../../engine/types'

export function lessonToSpec(lesson: Lesson): AssemblySpec {
  return {
    parts: lesson.components.map((c) => ({
      id: c.id,
      label: c.label,
      group: c.phase,
      shape: c.geometry.shape,
      size: c.geometry.size,
      position: c.position,
      explode: c.explode,
    })),
    links: lesson.connections.map((c) => ({ source: c.source, target: c.target, label: c.payload })),
  }
}

const link = (source: string, target: string) => linkKey({ source, target })

/** Real values from the last tokenizer run, shown as callouts in the scene. */
export function readoutsFromResult(r: TokenizeResult | null): Readouts | undefined {
  if (!r) return undefined
  const { training: t } = r
  return {
    parts: {
      corpus: `${r.corpus.bytes} BYTES`,
      pre_tokenizer: r.pre_tokens.mode === 'words' ? `${r.pre_tokens.count} PIECES` : 'NO SPLIT',
      base_alphabet: `${r.base.size} SYMBOLS · ${r.base.mode === 'bytes' ? 'BYTES' : 'CHARS + UNK'}`,
      merge_learner: `${t.merges_learned}/${t.merges_requested} MERGES`,
      vocabulary: `${r.vocabulary.size} ENTRIES`,
      input_text: `${r.input.bytes} BYTES`,
      encoder: `${r.encoding.count} TOKENS${r.encoding.order === 'reversed' ? ' · REVERSED' : ''}`,
      decoder: r.decoding.round_trip ? 'ROUND TRIP EXACT' : 'ROUND TRIP FAILS',
    },
    links: {
      [link('corpus', 'pre_tokenizer')]: `${r.corpus.characters} chars`,
      [link('pre_tokenizer', 'base_alphabet')]: `${r.pre_tokens.unique} distinct`,
      [link('base_alphabet', 'merge_learner')]: `${r.base.size} symbols`,
      [link('merge_learner', 'vocabulary')]: `${t.merges_learned} merges`,
      [link('vocabulary', 'encoder')]: `${r.vocabulary.size}`,
      [link('input_text', 'encoder')]: `${r.input.pieces} pieces`,
      [link('encoder', 'decoder')]: `${r.encoding.count} ids`,
    },
  }
}

/** Make whitespace visible inside a token: a leading space is part of the token. */
export function showToken(text: string): string {
  return text.replaceAll(' ', '·').replaceAll('\n', '↵').replaceAll('\t', '⇥')
}

export interface ReplayEvent {
  piece: number
  rank: number
  token: string
  pieces: string[]
}

/**
 * Every merge the encoder applied, in learned (rank) order across all pieces.
 * Each piece is merged independently, so this ordering is exactly what the
 * encoder did, just interleaved for display. Nothing is recomputed here.
 */
export function replayEvents(r: TokenizeResult): ReplayEvent[] {
  return r.encoding.pieces
    .flatMap((p, piece) => p.steps.map((s) => ({ piece, rank: s.rank, token: s.token, pieces: s.pieces })))
    .sort((a, b) => (r.encoding.order === 'reversed' ? b.rank - a.rank : a.rank - b.rank) || a.piece - b.piece)
}

/** Segmentation of every piece after the first `k` replay events. */
export function segmentationAt(r: TokenizeResult, events: ReplayEvent[], k: number): string[][] {
  const out = r.encoding.pieces.map((p) => p.start)
  for (const e of events.slice(0, k)) out[e.piece] = e.pieces
  return out
}

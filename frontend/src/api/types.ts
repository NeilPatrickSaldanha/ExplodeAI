export type Vec3 = [number, number, number]
export type PassStatus = 'pending' | 'passed' | 'failed' | 'not_applicable'

export interface Citation {
  source: string
  locator: string | null
  excerpt: string
}

export interface VerificationPass {
  status: PassStatus
  date: string | null
  by: string | null
  notes: string | null
}

export interface Claim {
  id: string
  text: string
  kind: 'fact' | 'definition' | 'provider_specific' | 'simplification'
  provider: string | null
  citations: Citation[]
  verification: { primary: VerificationPass; cross_check: VerificationPass; technical: VerificationPass }
}

export interface Source {
  id: string
  title: string
  publisher: string
  url: string
  type: string
  version: string | null
  accessed: string
}

export type Shape = 'slab' | 'stack' | 'cylinder' | 'grid' | 'prism' | 'lens' | 'ring'

export interface Component {
  id: string
  label: string
  /** Free-form group, e.g. the pipeline phase. */
  phase: string
  short: string
  detail: string
  claims: string[]
  geometry: { shape: Shape; size: Vec3 }
  position: Vec3
  explode: Vec3
  subtitle?: string | null
  icon?: string | null
  inputs?: string[]
  outputs?: string[]
  breaks_if_removed?: string | null
}

export interface Visual {
  id: string
  kind: 'real_execution' | 'simulation' | 'conceptual'
  label: string
  description: string
}

export interface Challenge<P = RagParams> {
  id: string
  title: string
  brief: string
  broken_params: Partial<P>
  locked_params: (keyof P & string)[]
  checks: { type: string; gold: string[]; limit: number | null }[]
  hint: string
  explanation: string
  claims: string[]
}

export interface Lesson {
  id: string
  title: string
  summary: string
  status: 'draft' | 'published'
  version: string
  updated: string
  estimated_minutes: number
  objectives: string[]
  claims: Claim[]
  components: Component[]
  connections: { source: string; target: string; payload: string; flow?: 'document' | 'vector' | 'query' | null }[]
  visuals: Visual[]
  experiment: { engine: string; presets: { label: string; query?: string; text?: string }[]; corpus_note: string }
  challenges: Challenge[]
  reconstruction: { prompt: string; dependencies: Record<string, string[]> }
  tour: { component: string; title: string; body: string; claims: string[] }[]
  sources: Source[]
  validation_problems: string[]
}

export interface LessonSummary {
  id: string
  title: string
  summary: string
  status: string
  estimated_minutes: number
  component_count: number
}

export interface RagParams {
  corpus_id: string
  query: string
  strategy: 'fixed' | 'sentence'
  chunk_size: number
  overlap: number
  embedder: 'lexical-hashing' | 'neural-local'
  method: 'dense' | 'bm25' | 'hybrid'
  top_k: number
  context_budget_words: number
}

export interface ChunkOut {
  id: string
  doc_id: string
  index: number
  text: string
  start: number
  end: number
  words: number
  point: Vec3
  dense_score: number
  dense_rank: number
  bm25_score: number | null
  bm25_rank: number | null
}

export interface RagResult {
  params: RagParams
  corpus: { id: string; note: string; documents: { id: string; title: string; text: string }[] }
  chunks: ChunkOut[]
  embedding: { name: string; kind: string; dim: number }
  query: { text: string; point: Vec3 }
  projection: { method: string; explained_variance: number }
  retrieved: { chunk_id: string; score: number; rank: number }[]
  prompt: { text: string; included: string[]; dropped: string[]; context_words: number; budget_words: number }
  answer: { mode: string; is_llm: boolean; text: string; sentences: { text: string; source: string }[] }
  timings_ms: Record<string, number>
  stages: string[]
}

export interface ChallengeOutcome {
  passed: boolean
  checks: { type: string; gold: string; passed: boolean; message: string }[]
}

export interface ChallengeCheck extends ChallengeOutcome {
  result: RagResult
}

export interface RagConfig {
  defaults: RagParams
  embedders: { id: string; label: string; available: boolean }[]
  stages: string[]
}

export interface Progress {
  lesson_id: string
  explored_components: string[]
  solved_challenges: string[]
  reconstruction_solved: boolean
}

export interface ReconstructionResult {
  correct: boolean
  violations: { stage: string; needs: string }[]
  message: string
}

/* ------------------------------------------------------------ tokenization */

export interface TokenizeParams {
  corpus_id: string
  text: string
  merges: number
  base: 'bytes' | 'chars'
  pre_tokenizer: 'words' | 'none'
  merge_order: 'learned' | 'reversed'
}

export interface TokenOut {
  id: number
  /** Readable text, or null when the token's bytes are not valid UTF-8 on their own. */
  text: string | null
  bytes_hex: string
  is_unk: boolean
}

export interface PieceTrace {
  text: string
  start: string[]
  steps: { rank: number; token: string; pieces: string[] }[]
}

export interface SweepPoint {
  merges: number
  vocab_size: number
  input_tokens: number
  corpus_tokens: number
  corpus_bytes_per_token: number
}

export interface TokenizeResult {
  params: TokenizeParams
  label: string
  corpus: { id: string; title: string; note: string; text: string; characters: number; bytes: number }
  pre_tokens: { mode: string; count: number; unique: number; sample: { text: string; count: number }[] }
  base: { mode: TokenizeParams['base']; size: number; has_unk: boolean }
  training: {
    merges_requested: number
    merges_learned: number
    steps: { rank: number; left: string; right: string; token: string; token_id: number; count: number }[]
    word_history: { word: string; count: number; start: string[]; steps: { after_merges: number; pieces: string[] }[] }[]
  }
  vocabulary: {
    size: number
    base_size: number
    merges: number
    special: { text: string; id: number }[]
    crossing_word_boundary: string[]
  }
  input: { text: string; characters: number; bytes: number; pieces: number }
  encoding: { order: TokenizeParams['merge_order']; ids: number[]; tokens: TokenOut[]; count: number; pieces: PieceTrace[] }
  decoding: { text: string; round_trip: boolean; unk_count: number }
  sweep: SweepPoint[]
  timings_ms: Record<string, number>
  stages: string[]
}

export interface TokenizeCheck extends ChallengeOutcome {
  result: TokenizeResult
}

export interface TokenizeConfig {
  defaults: TokenizeParams
  max_merges: number
  label: string
  stages: string[]
}

/* ------------------------------------------------------------ ablation */

export interface AblationOutcome {
  removed: string | null
  chunks: number
  retrieved: { chunk_id: string; text: string }[]
  prompt: { included: string[]; dropped: string[]; context_words: number; budget_words: number }
  answer: { text: string | null; has_answer: boolean; is_llm: boolean }
  notes: string[]
}

export interface AblationResult {
  baseline: AblationOutcome
  ablated: AblationOutcome
}

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
  phase: 'ingestion' | 'query' | 'generation'
  short: string
  detail: string
  claims: string[]
  geometry: { shape: Shape; size: Vec3 }
  position: Vec3
  explode: Vec3
}

export interface Visual {
  id: string
  kind: 'real_execution' | 'simulation' | 'conceptual'
  label: string
  description: string
}

export interface Challenge {
  id: string
  title: string
  brief: string
  broken_params: Partial<RagParams>
  locked_params: (keyof RagParams)[]
  checks: { type: string; gold: string[] }[]
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
  connections: { source: string; target: string; payload: string }[]
  visuals: Visual[]
  experiment: { presets: { label: string; query: string }[]; corpus_note: string }
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

export interface ChallengeCheck {
  passed: boolean
  checks: { type: string; gold: string; passed: boolean; message: string }[]
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

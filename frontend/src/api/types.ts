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

export interface Explain {
  what: string
  why: string
  analogy: string
  happens: string[]
  goes_to: string
  example: { input: string; steps: string[]; output: string }
  misconfigured: string
  learn_more: string
  claims: string[]
}

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
  explain?: Explain | null
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
  number: number
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
  experiment: { engine: string; presets: { label: string; query?: string; text?: string; note?: string }[]; corpus_note: string }
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

/* ------------------------------------------------------------ paid AI */

export interface AIModelOption {
  provider: 'anthropic' | 'openai' | 'gemini'
  model: string
  usable: boolean
  input_usd_per_million_tokens: number
  output_usd_per_million_tokens: number
  price_checked: string
}

export interface AIStatus {
  enabled: boolean
  emergency_disabled: boolean
  allowed_models: AIModelOption[]
  limits: { daily_budget_usd: number; total_budget_usd: number; spent_today_usd: number; spent_total_usd: number; max_output_tokens: number }
}

export interface LLMAnswer {
  text: string
  provider: string
  model: string
  input_tokens: number | null
  output_tokens: number | null
  cost_usd: number
  max_cost_usd: number
  spent_total_usd: number
  included: string[]
  is_llm: true
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

/* ------------------------------------------------- tokenization ablation */

export interface TokenizeAblationOutcome {
  removed: string | null
  vocab_size: number
  merges: number
  crossing_word_boundary: number
  tokens: number | null
  preview: string[]
  unk_count: number
  decoded: string | null
  round_trip: boolean
  notes: string[]
}

/* ------------------------------------------------------------ embeddings */

export interface EmbedParams {
  library_id: string
  text: string
  library_embedder: 'neural' | 'lexical'
  query_embedder: 'neural' | 'lexical'
  pooling: 'cls' | 'mean'
  normalize: boolean
  metric: 'cosine' | 'dot' | 'euclidean'
  query_instruction: boolean
  top_k: number
}

export interface EmbedItem {
  id: string
  category: string
  text: string
  tokens: number
  score: number | null
  rank: number | null
  point: Vec3
}

export interface EmbedResult {
  params: EmbedParams
  model: { name: string; build: string; dim: number; max_tokens: number | null }
  library: { id: string; note: string; categories: string[]; items: EmbedItem[] }
  query: {
    text: string
    model_input: string
    embedder: string
    tokens: { text: string; id: number | null }[]
    truncated: boolean
    token_vectors: number[][] | null
    pooled_preview: number[]
    norm_before: number
    norm_after: number
    dim: number
    point: Vec3 | null
  }
  comparable: boolean
  neighbours: { id: string; category: string; text: string; score: number; rank: number }[]
  votes: Record<string, number>
  projection: { method: string; explained_variance: number }
  notes: string[]
  timings_ms: Record<string, number>
  stages: string[]
}

export interface EmbedAblationOutcome {
  removed: string | null
  library_vectors: string | null
  query_vector_dim: number | null
  token_vectors: string | null
  neighbours: { id: string; category: string; score: number | null }[]
  top_category: string | null
  score_range: [number, number] | null
  has_map: boolean
  notes: string[]
}

export interface EmbedCheck extends ChallengeOutcome {
  result: EmbedResult
}

export interface AttendParams {
  text: string
  heads: 1 | 2 | 4 | 8
  scale: boolean
  causal: boolean
  position: boolean
  head: number
}

export interface AttendHead {
  index: number
  q: number[][]
  k: number[][]
  v: number[][]
  scores_raw: number[][]
  scores: number[][]
  weights: number[][]
}

export interface AttendResult {
  params: AttendParams
  model: { kind: 'toy'; note: string; d_model: number; heads: number; head_dim: number; seed: number }
  tokens: { index: number; text: string }[]
  embedding: { word_preview: number[][]; position_preview: number[][] | null; input_preview: number[][] }
  heads: AttendHead[]
  selected_head: number
  weights_mean: number[][]
  output: { preview: number[][]; norms: number[] }
  stats: {
    head_dim: number
    score_std_raw: number
    score_std_used: number
    expected_raw_std: number
    mean_max_weight: number
    mean_entropy: number
    future_mass: number
    self_weight: number
    row_sum_min: number
    row_sum_max: number
    order_gap: number
  }
  notes: string[]
  timings_ms: Record<string, number>
  stages: string[]
}

export interface AttendAblationOutcome {
  removed: string | null
  has_weights: boolean
  has_output: boolean
  output_shape: string | null
  weights: number[][] | null
  row_sum_min: number | null
  row_sum_max: number | null
  has_negative: boolean | null
  future_mass: number | null
  self_weight: number | null
  mean_max_weight: number | null
  order_gap: number | null
  uniform: boolean | null
  notes: string[]
}

export interface AttendCheck extends ChallengeOutcome {
  result: AttendResult
}

export interface TutorSentence {
  text: string
  passage_id: string
  kind: string
  claim_ids: string[]
  lesson_id: string
  lesson_title: string
  stage_id: string | null
  stage_label: string | null
}

export interface TutorRelated {
  lesson_id: string
  lesson_title: string
  stage_id: string
  stage_label: string
}

export interface TutorClaim {
  id: string
  lesson_id: string
  text: string
}

export interface TutorSource {
  id: string
  title: string
  publisher: string
  url: string
  version?: string | null
}

export interface TutorPlain {
  lesson_id: string
  stage_id: string
  stage_label: string
  mode: 'answer' | 'simplify' | 'example' | 'why' | 'more'
  what: string | null
  why: string | null
  analogy: string | null
  example: { input: string; steps: string[]; output: string } | null
  happens: string[]
  misconfigured: string | null
  more: string | null
}

export interface TutorTurn {
  question: string
  answer_text?: string | null
  lesson_id?: string | null
  stage_id?: string | null
}

export interface TutorLessonCard {
  number: number
  lesson_id: string
  title: string
  summary: string
  objectives: string[]
  minutes: number
  stages: string[]
}

export interface TutorAnswer {
  lead?: string | null  // a short conversational opener, e.g. "Hi!"
  type: 'answer' | 'plain' | 'chat' | 'none' | 'llm' | 'overview'
  lessons?: TutorLessonCard[]
  focus_number?: number | null
  plain: TutorPlain | null
  covered: boolean
  message: string | null
  sentences: TutorSentence[]
  analogy: { text: string; stage_label: string | null; note: string } | null
  claims: TutorClaim[]
  sources: TutorSource[]
  related: TutorRelated[]
  topics: { lesson_id: string; title: string; number: number }[]
  meta: { method: string; covered: boolean; coverage: number; best_dense: number | null }
}

export interface TutorCheck {
  kind: string
  question: string
  answer: string
  hint: string
  lesson_id: string
  stage_id: string
  stage_label: string
  claim_ids: string[]
  index: number
  total: number
}

export interface TutorLlmAnswer extends Partial<TutorAnswer> {
  text?: string
  cited?: string[]
  removed_citations?: string[]
  grounded?: boolean
  has_citations?: boolean
  covered: boolean
  provider?: string
  model?: string
  input_tokens?: number | null
  output_tokens?: number | null
  cost_usd: number
  max_cost_usd?: number
  spent_total_usd?: number
  is_llm: boolean
}

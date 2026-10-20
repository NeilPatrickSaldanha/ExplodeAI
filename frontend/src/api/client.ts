import type {
  AblationResult,
  ChallengeCheck,
  Lesson,
  LessonSummary,
  Progress,
  RagConfig,
  RagParams,
  RagResult,
  ReconstructionResult,
  TokenizeCheck,
  TokenizeConfig,
  TokenizeParams,
  TokenizeResult,
} from './types'

const LEARNER_KEY = 'explodeai.learner'

/** Anonymous per-browser id. Not personal data; never leaves our own backend. */
export function learnerId(): string {
  try {
    let id = localStorage.getItem(LEARNER_KEY)
    if (!id) {
      id = crypto.randomUUID()
      localStorage.setItem(LEARNER_KEY, id)
    }
    return id
  } catch {
    return 'anonymous'
  }
}

export class ApiError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, {
    ...init,
    headers: { 'Content-Type': 'application/json', 'X-Learner-Id': learnerId(), ...init?.headers },
  })
  if (!res.ok) {
    let message = `Request failed (${res.status})`
    try {
      const body = await res.json()
      const d = body.detail
      message = typeof d === 'string' ? d : Array.isArray(d) ? d.map((e) => e.msg).join('; ') : d?.message ?? message
    } catch {
      /* non-JSON error body */
    }
    throw new ApiError(res.status, message)
  }
  return res.json() as Promise<T>
}

const post = <T>(path: string, body: unknown) => request<T>(path, { method: 'POST', body: JSON.stringify(body) })

export const api = {
  lessons: () => request<LessonSummary[]>('/api/lessons'),
  lesson: (id: string) => request<Lesson>(`/api/lessons/${id}`),
  ragConfig: () => request<RagConfig>('/api/experiments/rag/config'),
  runEmbed: (params: Partial<import('./types').EmbedParams>) =>
    post<import('./types').EmbedResult>('/api/experiments/embed/run', params),
  ablateEmbed: (params: Partial<import('./types').EmbedParams>, stage: string) =>
    post<{ baseline: import('./types').EmbedAblationOutcome; ablated: import('./types').EmbedAblationOutcome }>(
      '/api/experiments/embed/ablate', { ...params, stage }),
  checkEmbedChallenge: (lessonId: string, challengeId: string, params: Partial<import('./types').EmbedParams>) =>
    post<import('./types').EmbedCheck>(`/api/experiments/embed/challenges/${lessonId}/${challengeId}/check`, params),
  aiStatus: () => request<import('./types').AIStatus>('/api/ai/status'),
  estimateRagAnswer: (params: Partial<RagParams>, provider: string, model: string) =>
    post<{ max_cost_usd: number; prompt_words: number }>('/api/ai/rag-answer/estimate', { ...params, provider, model }),
  ragAnswer: (params: Partial<RagParams>, provider: string, model: string) =>
    post<import('./types').LLMAnswer>('/api/ai/rag-answer', { ...params, provider, model, confirm_paid: true }),
  runRag: (params: Partial<RagParams>) => post<RagResult>('/api/experiments/rag/run', params),
  checkChallenge: (lessonId: string, challengeId: string, params: Partial<RagParams>) =>
    post<ChallengeCheck>(`/api/experiments/rag/challenges/${lessonId}/${challengeId}/check`, params),
  ablate: (params: Partial<RagParams>, stage: string) =>
    post<AblationResult>('/api/experiments/rag/ablate', { ...params, stage }),
  tokenizeConfig: () => request<TokenizeConfig>('/api/experiments/tokenize/config'),
  runTokenize: (params: Partial<TokenizeParams>) => post<TokenizeResult>('/api/experiments/tokenize/run', params),
  checkTokenizeChallenge: (lessonId: string, challengeId: string, params: Partial<TokenizeParams>) =>
    post<TokenizeCheck>(`/api/experiments/tokenize/challenges/${lessonId}/${challengeId}/check`, params),
  checkReconstruction: (lessonId: string, order: string[]) =>
    post<ReconstructionResult>(`/api/lessons/${lessonId}/reconstruction/check`, { order }),
  progress: (lessonId: string) => request<Progress>(`/api/progress/${lessonId}`),
  saveProgress: (lessonId: string, update: Partial<Omit<Progress, 'lesson_id'>>) =>
    request<Progress>(`/api/progress/${lessonId}`, { method: 'PUT', body: JSON.stringify(update) }),
}

/** Run the tokenizer as configured and with one stage removed (real execution, both). */
export const ablateTokenize = (params: Partial<import('./types').TokenizeParams>, stage: string) =>
  post<{ baseline: import('./types').TokenizeAblationOutcome; ablated: import('./types').TokenizeAblationOutcome }>(
    '/api/experiments/tokenize/ablate',
    { ...params, stage },
  )

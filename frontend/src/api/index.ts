import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export const api = axios.create({
  baseURL: BASE_URL,
  timeout: 120_000,
})

// ── Types ──────────────────────────────────────────────

export interface Citation {
  citation_id: number
  doc_id: string | null
  chunk_id: string | null
  chunk_index: number | null
  page_start: number | null
  page_end: number | null
  section: string | null
  snippet: string
}

export interface UploadResponse {
  document_id: string
  filename: string
  status: string
}

export interface DocumentItem {
  doc_id: string
  filename: string
  file_type: string
  uploaded_at: string
}

export interface AskResponse {
  answer: string
  citations: Citation[]
}

export interface TraceStep {
  thought: string
  action: string
  observation: string
}

export interface AgentResponse {
  workflow_status: string
  tool_used: string
  tool_arguments: Record<string, unknown>
  tool_result: Record<string, unknown>
  final_answer: string
  trace: TraceStep[]
}

export interface RoastPersona {
  persona_name: string
  core_traits: string[]
  behavior_pattern: string
  roast_angle: string
}

export interface RoastScores {
  scores: Record<string, number>
  diagnosis_rate: number
}

export interface RoastResponse {
  query: string
  method: string
  persona: RoastPersona
  scores: RoastScores
  tags: string[]
  contradictions: string[]
  roast_text: string
  citations: Citation[]
  retrieval_count: number
}

// ── Endpoints ─────────────────────────────────────────

export const uploadFile = (file: File) => {
  const form = new FormData()
  form.append('file', file)
  return api.post<UploadResponse>('/upload', form)
}

export const listDocuments = () =>
  api.get<{ documents: DocumentItem[] }>('/documents')

export const ask = (payload: {
  question: string
  document_ids?: string[]
  top_k?: number
  method?: string
}) => api.post<AskResponse>('/ask', payload)

export const runAgent = (payload: {
  question: string
  method?: string
  top_k?: number
  document_ids?: string[]
  target_id?: string
  style_preference?: string
}) => api.post<AgentResponse>('/agent', payload)

export const runRoast = (payload: {
  query: string
  document_ids?: string[]
  top_k?: number
  method?: string
  style_preference?: string
  target_id?: string
}) => api.post<RoastResponse>('/roast', payload)

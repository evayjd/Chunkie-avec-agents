export interface Document {
  id: string
  filename: string
  display_name: string
  file_type: string
  file_size_bytes: number
  status: 'pending' | 'processing' | 'indexed' | 'failed'
  language: string | null
  total_chunks: number
  error_message: string | null
  description: string | null
  created_at: string
  updated_at: string
}

export interface Citation {
  citation_number: number
  chunk_id: string
  document_id: string
  snippet: string
  score: number
}

export interface ChatMessage {
  id?: string
  role: 'user' | 'assistant'
  content: string
  citations?: Citation[]
  is_grounded?: boolean
  timestamp: string
}

export interface ChatResponse {
  answer: string
  citations: Citation[]
  conversation_id: string
  message_id: string
  is_grounded: boolean
  retrieval_metadata?: Record<string, number>
}

export interface DimensionScore {
  dimension: string
  score: number
  label: string
}

export interface PersonaTag {
  tag: string
  label: string
  confidence: number
  evidence_snippet: string
  citation_number?: number
}

export interface RoastProfile {
  roast_text: string
  dimension_scores: DimensionScore[]
  persona_tags: PersonaTag[]
  document_count: number
  language: string
}

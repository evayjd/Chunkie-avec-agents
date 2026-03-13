export type RetrievalMethod = 'vector' | 'hybrid' | 'rerank';

export interface UploadResponse {
  document_id: string;
  filename: string;
  status: string;
}

export interface CitationItem {
  citation_id: number;
  doc_id?: string | null;
  chunk_id?: string | null;
  chunk_index?: number | null;
  page_start?: number | null;
  page_end?: number | null;
  section?: string | null;
  snippet?: string | null;
}

export interface AskRequest {
  question: string;
  document_ids?: string[] | null;
  top_k: number;
  method: RetrievalMethod;
}

export interface AskResponse {
  answer: string;
  citations: CitationItem[];
}

export interface DocumentItem {
  doc_id: string;
  filename: string;
  file_type: string;
  uploaded_at: string;
}

export interface DocumentsResponse {
  documents: DocumentItem[];
}

export interface RoastRequest {
  query: string;
  document_ids?: string[] | null;
  top_k: number;
  method: RetrievalMethod;
  style_preference?: string | null;
  target_id?: string | null;
}

export interface RoastPersona {
  persona_name?: string;
  core_traits?: string[];
  behavior_pattern?: string;
  roast_angle?: string;
  [key: string]: unknown;
}

export interface RoastScoresPayload {
  scores?: Record<string, number>;
  diagnosis_rate?: number;
  [key: string]: unknown;
}

export interface RoastResponse {
  query: string;
  method: RetrievalMethod | string;
  persona: RoastPersona;
  scores: RoastScoresPayload;
  tags: string[];
  contradictions: string[];
  roast_text: string;
  citations: CitationItem[];
  retrieval_count: number;
}

export interface AgentRequest {
  question: string;
  method: RetrievalMethod;
  top_k: number;
  document_ids?: string[] | null;
  target_id?: string | null;
  style_preference?: string | null;
}

export interface TraceStep {
  thought: string;
  action: string;
  observation: string;
}

export interface RagChunk {
  citation_id?: number;
  doc_id?: string | null;
  chunk_id?: string | null;
  chunk_index?: number | null;
  content?: string;
  page_start?: number | null;
  page_end?: number | null;
  section?: string | null;
  rerank_score?: number;
  metadata?: Record<string, unknown>;
}

export interface RetrievalVerdict {
  ok: boolean;
  score: number;
  reason: string;
  retrieval_count: number;
}

export interface RetrievalProbe {
  ok: boolean;
  stage: 'first_pass' | 'second_pass' | 'failed' | string;
  relaxed_query?: string;
  verdict: RetrievalVerdict;
  retrieval_result?: {
    question?: string;
    method?: string;
    top_k?: number;
    document_ids?: string[] | null;
    chunks?: RagChunk[];
    citations?: CitationItem[];
    retrieval_count?: number;
  };
}

export interface AnswerToolResult {
  answer?: string;
  citations?: CitationItem[];
  used_general_knowledge?: boolean;
  fallback_notice?: string | null;
  retrieval_verifier?: RetrievalProbe;
}

export interface SummaryToolResult {
  target_id?: string;
  style_preference?: string;
  summary?: string;
  citations?: CitationItem[];
  retrieval_verifier?: RetrievalProbe;
}

export interface CompareToolResult {
  document_ids?: string[];
  style_preference?: string;
  comparison?: string;
  citations?: CitationItem[];
  retrieval_verifier?: RetrievalProbe;
}

export interface RoastToolResult extends RoastResponse {
  retrieval_verifier?: RetrievalProbe;
}

export interface RagSearchToolResult {
  question?: string;
  method?: string;
  top_k?: number;
  document_ids?: string[] | null;
  chunks?: RagChunk[];
  citations?: CitationItem[];
  retrieval_count?: number;
  retrieval_verifier?: RetrievalProbe;
}

export type AgentToolResult =
  | AnswerToolResult
  | SummaryToolResult
  | CompareToolResult
  | RoastToolResult
  | RagSearchToolResult
  | Record<string, unknown>;

export interface AgentResponse {
  workflow_status: string;
  tool_used: string;
  tool_arguments: Record<string, unknown>;
  tool_result: AgentToolResult;
  final_answer: string;
  trace: TraceStep[];
}
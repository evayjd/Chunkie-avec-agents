import { http } from './http';
import type {
  AgentRequest,
  AgentResponse,
  AskRequest,
  AskResponse,
  DocumentsResponse,
  RoastRequest,
  RoastResponse,
  UploadResponse
} from '@/types/api';

export async function fetchDocuments() {
  const { data } = await http.get<DocumentsResponse>('/documents');
  return data;
}

export async function uploadDocument(file: File) {
  const formData = new FormData();
  formData.append('file', file);

  const { data } = await http.post<UploadResponse>('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });

  return data;
}

export async function askQuestion(payload: AskRequest) {
  const { data } = await http.post<AskResponse>('/ask', payload);
  return data;
}

export async function runAgent(payload: AgentRequest) {
  const { data } = await http.post<AgentResponse>('/agent', payload);
  return data;
}

export async function runRoast(payload: RoastRequest) {
  const { data } = await http.post<RoastResponse>('/roast', payload);
  return data;
}
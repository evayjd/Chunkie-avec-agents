import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

export const api = axios.create({
  baseURL: BASE_URL,
  timeout: 120_000,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.response.use(
  (res) => res,
  (error) => {
    const msg = error.response?.data?.detail || error.message || '请求失败'
    return Promise.reject(new Error(msg))
  },
)

export async function uploadDocument(file: File) {
  const form = new FormData()
  form.append('file', file)
  const res = await api.post('/documents/', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return res.data
}

export async function listDocuments() {
  const res = await api.get('/documents/')
  return res.data
}

export async function deleteDocument(id: string) {
  await api.delete(`/documents/${id}`)
}

export async function sendChat(
  query: string,
  conversationId?: string,
  documentIds?: string[],
  language?: string,
) {
  const res = await api.post('/chat/', { query, conversation_id: conversationId, document_ids: documentIds, language })
  return res.data
}

export async function generateRoast(documentIds?: string[], language = 'zh') {
  const res = await api.post('/roast/', { document_ids: documentIds, language })
  return res.data
}

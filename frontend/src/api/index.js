import axios from 'axios';
const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';
export const api = axios.create({
    baseURL: BASE_URL,
    timeout: 120000,
});
// ── Endpoints ─────────────────────────────────────────
export const uploadFile = (file) => {
    const form = new FormData();
    form.append('file', file);
    return api.post('/upload', form);
};
export const listDocuments = () => api.get('/documents');
export const ask = (payload) => api.post('/ask', payload);
export const runAgent = (payload) => api.post('/agent', payload);
export const runRoast = (payload) => api.post('/roast', payload);

import { http } from './http';
export async function fetchDocuments() {
    const { data } = await http.get('/documents');
    return data;
}
export async function uploadDocument(file) {
    const formData = new FormData();
    formData.append('file', file);
    const { data } = await http.post('/upload', formData, {
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    });
    return data;
}
export async function askQuestion(payload) {
    const { data } = await http.post('/ask', payload);
    return data;
}
export async function runAgent(payload) {
    const { data } = await http.post('/agent', payload);
    return data;
}
export async function runRoast(payload) {
    const { data } = await http.post('/roast', payload);
    return data;
}

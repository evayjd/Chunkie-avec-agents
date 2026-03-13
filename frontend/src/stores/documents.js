import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { fetchDocuments as apiFetchDocuments, uploadDocument } from '@/services/ragApi';
export const useDocumentsStore = defineStore('documents', () => {
    const documents = ref([]);
    const uploading = ref(false);
    const loading = ref(false);
    const error = ref(null);
    const selectedDocumentIds = ref([]);
    const selectedDocuments = computed(() => documents.value.filter(d => selectedDocumentIds.value.includes(d.doc_id)));
    async function loadDocuments(force = false) {
        if (!force && documents.value.length > 0)
            return;
        loading.value = true;
        error.value = null;
        try {
            const res = await apiFetchDocuments();
            documents.value = res.documents ?? [];
        }
        catch (e) {
            error.value = e?.response?.data?.detail ?? 'Failed to load documents';
        }
        finally {
            loading.value = false;
        }
    }
    const fetchDocuments = () => loadDocuments(true);
    function toggleDocument(docId) {
        const idx = selectedDocumentIds.value.indexOf(docId);
        if (idx === -1)
            selectedDocumentIds.value.push(docId);
        else
            selectedDocumentIds.value.splice(idx, 1);
    }
    function clearSelection() {
        selectedDocumentIds.value = [];
    }
    async function upload(file) {
        uploading.value = true;
        error.value = null;
        try {
            const res = await uploadDocument(file);
            await loadDocuments(true);
            return res.document_id;
        }
        catch (e) {
            error.value = e?.response?.data?.detail ?? 'Upload failed';
            return null;
        }
        finally {
            uploading.value = false;
        }
    }
    return {
        documents, uploading, loading, error,
        selectedDocumentIds, selectedDocuments,
        loadDocuments, fetchDocuments,
        toggleDocument, clearSelection, upload,
    };
});

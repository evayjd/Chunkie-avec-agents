import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { fetchDocuments as apiFetchDocuments, uploadDocument } from '@/services/ragApi'
import type { DocumentItem } from '@/types/api'

export const useDocumentsStore = defineStore('documents', () => {
  const documents           = ref<DocumentItem[]>([])
  const uploading           = ref(false)
  const loading             = ref(false)
  const error               = ref<string | null>(null)
  const selectedDocumentIds = ref<string[]>([])

  const selectedDocuments = computed(() =>
    documents.value.filter(d => selectedDocumentIds.value.includes(d.doc_id))
  )

  async function loadDocuments(force = false) {
    if (!force && documents.value.length > 0) return
    loading.value = true
    error.value   = null
    try {
      const res = await apiFetchDocuments()
      documents.value = res.documents ?? []
    } catch (e: any) {
      error.value = e?.response?.data?.detail ?? 'Failed to load documents'
    } finally {
      loading.value = false
    }
  }

  const fetchDocuments = () => loadDocuments(true)

  function toggleDocument(docId: string) {
    const idx = selectedDocumentIds.value.indexOf(docId)
    if (idx === -1) selectedDocumentIds.value.push(docId)
    else            selectedDocumentIds.value.splice(idx, 1)
  }

  function clearSelection() {
    selectedDocumentIds.value = []
  }

  async function upload(file: File): Promise<string | null> {
    uploading.value = true
    error.value     = null
    try {
      const res = await uploadDocument(file)
      await loadDocuments(true)
      return res.document_id
    } catch (e: any) {
      error.value = e?.response?.data?.detail ?? 'Upload failed'
      return null
    } finally {
      uploading.value = false
    }
  }

  return {
    documents, uploading, loading, error,
    selectedDocumentIds, selectedDocuments,
    loadDocuments, fetchDocuments,
    toggleDocument, clearSelection, upload,
  }
})

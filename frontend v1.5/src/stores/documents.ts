import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Document } from '@/types'
import { listDocuments, uploadDocument, deleteDocument } from '@/utils/api'

export const useDocumentsStore = defineStore('documents', () => {
  const documents = ref<Document[]>([])
  const loading = ref(false)
  const uploading = ref(false)
  const error = ref<string | null>(null)

  async function fetchDocuments() {
    loading.value = true
    error.value = null
    try {
      const data = await listDocuments()
      documents.value = data.documents || []
    } catch (e: any) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function upload(file: File) {
    uploading.value = true
    error.value = null
    try {
      const doc = await uploadDocument(file)
      documents.value.unshift(doc)
      return doc
    } catch (e: any) {
      error.value = e.message
      throw e
    } finally {
      uploading.value = false
    }
  }

  async function remove(id: string) {
    await deleteDocument(id)
    documents.value = documents.value.filter((d) => d.id !== id)
  }

  return { documents, loading, uploading, error, fetchDocuments, upload, remove }
})

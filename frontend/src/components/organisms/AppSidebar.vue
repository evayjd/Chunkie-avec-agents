<template>
  <aside class="flex flex-col gap-4 h-full p-3">
    <!-- upload -->
    <div>
      <p class="section-label mb-2">上传文档</p>
      <UploadPanel />
    </div>

    <!-- document list -->
    <div class="flex-1 min-h-0 flex flex-col">
      <div class="flex items-center justify-between mb-2">
        <p class="section-label">文档</p>
        <button
          class="text-xs text-stone-400 hover:text-petal-500 transition"
          :class="{ 'opacity-50 cursor-not-allowed': loading }"
          @click="loadDocuments(true)"
        >刷新</button>
      </div>

      <div v-if="loading" class="flex justify-center py-4">
        <LoadingSpinner size="sm" />
      </div>
      <div v-else class="overflow-y-auto flex-1">
        <DocumentSelector />
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useDocumentsStore } from '@/stores/documents'
import UploadPanel from './UploadPanel.vue'
import DocumentSelector from './DocumentSelector.vue'
import LoadingSpinner from '@/components/atoms/LoadingSpinner.vue'

const store = useDocumentsStore()
const { loading } = storeToRefs(store)
const { loadDocuments } = store

onMounted(() => loadDocuments())
</script>

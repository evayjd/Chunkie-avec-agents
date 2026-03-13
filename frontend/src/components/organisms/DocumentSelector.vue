<template>
  <div class="flex flex-col gap-1">
    <!-- header -->
    <div v-if="documents.length" class="flex items-center justify-between mb-1">
      <span class="section-label">已选 {{ selectedDocumentIds.length }} / {{ documents.length }}</span>
      <button
        v-if="selectedDocumentIds.length"
        class="text-xs text-red-400 hover:text-red-600 transition"
        @click="clearSelection"
      >清除</button>
    </div>

    <!-- list -->
    <DocumentListItem
      v-for="doc in documents"
      :key="doc.doc_id"
      :document="doc"
      :selected="selectedDocumentIds.includes(doc.doc_id)"
      @toggle="toggleDocument"
    />

    <!-- empty -->
    <p v-if="!documents.length" class="text-xs text-stone-400 text-center py-6">
      暂无文档，请先上传
    </p>
  </div>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useDocumentsStore } from '@/stores/documents'
import DocumentListItem from '@/components/molecules/DocumentListItem.vue'

const store = useDocumentsStore()
const { documents, selectedDocumentIds } = storeToRefs(store)
const { toggleDocument, clearSelection } = store
</script>

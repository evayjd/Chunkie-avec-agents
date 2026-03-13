<template>
  <div class="relative min-h-full">
    <DecorDots />
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xl font-semibold text-gray-900">{{ $t('documents.title') }}</h2>
      <label class="btn-primary cursor-pointer">
        <span v-if="!docsStore.uploading">{{ $t('documents.upload') }}</span>
        <span v-else>{{ $t('documents.uploading') }}</span>
        <input type="file" class="hidden" accept=".pdf,.md,.txt,.docx" @change="handleUpload" />
      </label>
    </div>

    <!-- Error -->
    <div v-if="docsStore.error" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
      {{ docsStore.error }}
    </div>

    <!-- Loading -->
    <div v-if="docsStore.loading" class="text-center py-20 text-gray-400">
      <div class="animate-spin text-4xl mb-3">⟳</div>
      <p>{{ $t('common.loading') }}</p>
    </div>

    <!-- Empty state -->
    <div
      v-else-if="docsStore.documents.length === 0"
      class="text-center py-20 text-gray-400 border-2 border-dashed border-gray-200 rounded-2xl cursor-pointer hover:border-primary-300 transition-colors"
    >
      <img :src="docIcon" class="w-56 h-64 mx-auto mb-4 opacity-70" />
      <p>{{ $t('documents.empty') }}</p>
    </div>

    <!-- Document list -->
    <div v-else class="bg-white border border-gray-200 rounded-2xl shadow-sm p-4">
      <div class="grid gap-3"></div>
      <div
        v-for="doc in docsStore.documents"
        :key="doc.id"
        class="card flex items-start gap-4"
      >
        <div class="text-3xl">{{ fileIcon(doc.file_type) }}</div>
        <div class="flex-1 min-w-0">
          <p class="font-medium text-gray-900 truncate">{{ doc.display_name }}</p>
          <p class="text-xs text-gray-400 mt-0.5">
            {{ formatSize(doc.file_size_bytes) }}
            <span v-if="doc.total_chunks"> · {{ doc.total_chunks }} {{ $t('common.chunks') }}</span>
          </p>
        </div>
        <div class="flex items-center gap-2 shrink-0">
          <span :class="statusBadge(doc.status)">{{ $t(`documents.status.${doc.status}`) }}</span>
          <button class="text-gray-400 hover:text-red-500 text-xs transition-colors" @click="handleDelete(doc.id)">
            {{ $t('documents.delete') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>


<script setup lang="ts">
const docIcon = new URL('../Decor/doc.png', import.meta.url).href
import { onMounted } from 'vue'
import { useDocumentsStore } from '@/stores/documents'
import DecorDots from '@/Decor/DecorDots.vue'

const docsStore = useDocumentsStore()


onMounted(() => docsStore.fetchDocuments())

async function handleUpload(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  await docsStore.upload(file)
  // Poll status until ready
  setTimeout(() => docsStore.fetchDocuments(), 3000)
}

async function handleDelete(id: string) {
  if (!confirm('确认删除此文档？')) return
  await docsStore.remove(id)
}

function fileIcon(type: string) {
  const map: Record<string, string> = {
    pdf: '📕', md: '📝', txt: '📄', docx: '📘',
  }
  return map[type] || '📄'
}

function formatSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}

function statusBadge(status: string) {
  const map: Record<string, string> = {
    pending: 'badge badge-yellow',
    processing: 'badge badge-blue',
    indexed: 'badge badge-green',
    failed: 'badge badge-red',
  }
  return map[status] || 'badge'
}
</script>

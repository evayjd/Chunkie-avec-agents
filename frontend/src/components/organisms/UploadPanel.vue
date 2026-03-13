<template>
  <div
    class="relative rounded-xl border-2 border-dashed border-petal-300 bg-petal-50
           flex flex-col items-center justify-center gap-2 h-28 transition
           hover:border-petal-400 hover:bg-petal-50/80 cursor-pointer"
    @dragover.prevent
    @drop.prevent="handleDrop"
    @click="fileInput?.click()"
  >
    <template v-if="uploading">
      <LoadingSpinner size="md" />
      <span class="text-xs text-petal-500">处理中…</span>
    </template>
    <template v-else>
      <span class="text-petal-400 text-xl">↑</span>
      <span class="text-xs text-stone-500 text-center px-4">
        拖拽或点击上传<br>
        <span class="text-stone-400">pdf · docx · txt · md · html</span>
      </span>
    </template>

    <input
      ref="fileInput"
      class="hidden"
      type="file"
      accept=".pdf,.docx,.txt,.md,.html,.htm"
      @change="handleInput"
    />
  </div>

  <p v-if="errorMsg" class="mt-1 text-xs text-red-500">{{ errorMsg }}</p>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useUpload } from '@/composables/useUpload'
import LoadingSpinner from '@/components/atoms/LoadingSpinner.vue'

const { upload, uploading } = useUpload()
const fileInput = ref<HTMLInputElement | null>(null)
const errorMsg  = ref<string | null>(null)

async function processFile(file: File | undefined) {
  if (!file) return
  errorMsg.value = null
  try {
    await upload(file)
  } catch {
    errorMsg.value = '上传失败，请重试'
  }
  if (fileInput.value) fileInput.value.value = ''
}

function handleInput(e: Event) {
  processFile((e.target as HTMLInputElement).files?.[0])
}

function handleDrop(e: DragEvent) {
  processFile(e.dataTransfer?.files?.[0])
}
</script>

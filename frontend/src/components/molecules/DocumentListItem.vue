<template>
  <button
    class="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-left
           transition hover:bg-blush-50"
    @click="$emit('toggle', document.doc_id)"
  >
    <!-- checkbox -->
    <span
      :class="[
        'shrink-0 h-4 w-4 rounded border transition',
        selected
          ? 'bg-petal-400 border-petal-400'
          : 'border-stone-300 bg-white'
      ]"
    >
      <svg v-if="selected" viewBox="0 0 12 12" fill="none" class="w-full h-full p-0.5">
        <path d="M2 6l3 3 5-5" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </span>

    <!-- filename -->
    <span class="flex-1 min-w-0 text-sm text-stone-700 truncate">
      {{ document.filename }}
    </span>

    <!-- type badge -->
    <span class="shrink-0 pill bg-stone-100 text-stone-500 text-[10px]">
      {{ document.file_type?.replace('.', '') || 'doc' }}
    </span>
  </button>
</template>

<script setup lang="ts">
import type { DocumentItem } from '@/types/api'

defineProps<{ document: DocumentItem; selected: boolean }>()
defineEmits<{ (e: 'toggle', id: string): void }>()
</script>

<template>
  <button
    class="inline-flex items-center rounded-full bg-petal-100 px-2 py-0.5 text-xs font-medium
           text-petal-600 transition hover:bg-petal-200 cursor-pointer"
    @click="$emit('open', citation)"
  >
    [{{ citation.citation_id }}]
  </button>
</template>

<script setup lang="ts">
import type { CitationItem } from '@/types/api'

defineProps<{ citation: CitationItem }>()
defineEmits<{ (e: 'open', citation: CitationItem): void }>()
</script>

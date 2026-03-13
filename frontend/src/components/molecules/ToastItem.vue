<template>
  <div
    :class="[
      'flex items-start gap-3 rounded-xl border bg-white pl-4 pr-3 py-3 min-w-64 max-w-sm shadow-sm',
      borderClass
    ]"
  >
    <!-- icon -->
    <span :class="['mt-0.5 shrink-0 text-sm font-bold', iconColor]">{{ icon }}</span>

    <!-- text -->
    <div class="flex-1 min-w-0">
      <p class="text-sm font-medium text-stone-800">{{ toast.title }}</p>
      <p v-if="toast.description" class="mt-0.5 text-xs text-stone-500">{{ toast.description }}</p>
    </div>

    <!-- dismiss -->
    <button
      class="shrink-0 text-stone-400 hover:text-stone-600 transition text-lg leading-none mt-0.5"
      @click="$emit('dismiss', toast.id)"
      aria-label="Dismiss"
    >×</button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ToastMessage } from '@/types/ui'

const props = defineProps<{ toast: ToastMessage }>()
defineEmits<{ (e: 'dismiss', id: string): void }>()

const borderClass = computed(() => {
  switch (props.toast.tone) {
    case 'success': return 'border-l-4 border-green-400 border-y-stone-200 border-r-stone-200'
    case 'warning': return 'border-l-4 border-amber-400 border-y-stone-200 border-r-stone-200'
    case 'error':   return 'border-l-4 border-red-400 border-y-stone-200 border-r-stone-200'
    default:        return 'border-l-4 border-petal-400 border-y-stone-200 border-r-stone-200'
  }
})

const iconColor = computed(() => {
  switch (props.toast.tone) {
    case 'success': return 'text-green-500'
    case 'warning': return 'text-amber-500'
    case 'error':   return 'text-red-500'
    default:        return 'text-petal-400'
  }
})

const icon = computed(() => {
  switch (props.toast.tone) {
    case 'success': return '✓'
    case 'warning': return '!'
    case 'error':   return '✕'
    default:        return '✦'
  }
})
</script>

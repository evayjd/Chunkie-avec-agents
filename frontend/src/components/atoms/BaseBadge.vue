<template>
  <span :class="['pill', toneClass]">
    <slot />{{ label }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    tone?: 'default' | 'info' | 'success' | 'warning' | 'error'
    label?: string
  }>(),
  { tone: 'default' }
)

const toneClass = computed(() => {
  switch (props.tone) {
    case 'info':    return 'bg-blue-50 text-blue-600'
    case 'success': return 'bg-green-50 text-green-700'
    case 'warning': return 'bg-amber-50 text-amber-700'
    case 'error':   return 'bg-red-50 text-red-600'
    default:        return 'bg-blush-100 text-petal-600'
  }
})
</script>

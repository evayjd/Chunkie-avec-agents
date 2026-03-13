<template>
  <div
    :class="[
      'inline-block animate-spin rounded-full border-2 border-petal-100 border-t-petal-400',
      sizeClass
    ]"
    aria-hidden="true"
  />
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{ size?: 'sm' | 'md' | 'lg' }>(),
  { size: 'md' }
)

const sizeClass = computed(() => {
  switch (props.size) {
    case 'sm': return 'h-4 w-4'
    case 'lg': return 'h-9 w-9'
    default:   return 'h-6 w-6'
  }
})
</script>

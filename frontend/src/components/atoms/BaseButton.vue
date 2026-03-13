<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    :class="[
      'inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-petal-300 focus:ring-offset-1',
      sizeClass,
      variantClass,
      (disabled || loading) ? 'cursor-not-allowed opacity-40' : 'cursor-pointer'
    ]"
  >
    <span
      v-if="loading"
      class="inline-block rounded-full border-2 border-current/30 border-t-current animate-spin shrink-0"
      :class="spinSize"
      aria-hidden="true"
    />
    <slot name="icon" />
    <span>{{ loading ? (loadingText ?? label ?? '处理中...') : label }}</span>
    <slot />
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  label?: string
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger'
  type?: 'button' | 'submit'
  disabled?: boolean
  loading?: boolean
  loadingText?: string
  size?: 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  type: 'button',
  disabled: false,
  loading: false,
  size: 'md'
})

const sizeClass = computed(() => {
  switch (props.size) {
    case 'sm': return 'text-xs px-3 py-1.5'
    case 'lg': return 'text-sm px-5 py-2.5'
    default:   return 'text-sm px-4 py-2'
  }
})

const spinSize = computed(() => {
  switch (props.size) {
    case 'sm': return 'h-3 w-3'
    case 'lg': return 'h-4 w-4'
    default:   return 'h-3.5 w-3.5'
  }
})

const variantClass = computed(() => {
  switch (props.variant) {
    case 'secondary':
      return 'bg-petal-100 text-petal-600 hover:bg-petal-200'
    case 'ghost':
      return 'bg-transparent text-petal-600 hover:bg-petal-50 border border-petal-200'
    case 'danger':
      return 'bg-red-50 text-red-600 hover:bg-red-100 border border-red-200'
    default:
      return 'bg-petal-500 text-white hover:bg-petal-600'
  }
})
</script>

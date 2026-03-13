<template>
  <div class="card-muted px-4 py-3">
    <p class="section-label">{{ label }}</p>
    <p class="mt-1 text-xl font-semibold text-petal-500">{{ value }}</p>
    <p v-if="hint" class="mt-1 text-xs text-stone-400">{{ hint }}</p>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  label: string
  value: string | number
  hint?: string
}>()
</script>

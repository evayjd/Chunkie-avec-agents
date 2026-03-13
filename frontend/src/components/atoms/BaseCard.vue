<template>
  <section :class="['card', compact ? 'p-3' : 'p-5']">
    <slot />
  </section>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{ compact?: boolean }>(),
  { compact: false }
)
</script>

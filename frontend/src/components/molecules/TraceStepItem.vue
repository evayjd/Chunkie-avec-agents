<template>
  <div class="flex gap-3">
    <!-- timeline dot + line -->
    <div class="flex flex-col items-center shrink-0">
      <span
        class="flex h-5 w-5 items-center justify-center rounded-full bg-petal-100
               text-[10px] font-semibold text-petal-600 shrink-0"
      >{{ index + 1 }}</span>
      <span class="flex-1 w-px bg-stone-200 mt-1" />
    </div>

    <!-- content -->
    <div class="pb-4 min-w-0 flex-1">
      <!-- action badge -->
      <span class="inline-block rounded bg-stone-100 px-2 py-0.5 text-xs font-mono text-stone-600 mb-2">
        {{ step.action }}
      </span>

      <!-- thought -->
      <p v-if="step.thought" class="text-xs text-stone-500 italic mb-1">{{ step.thought }}</p>

      <!-- observation -->
      <p class="text-sm text-stone-700 whitespace-pre-wrap break-words">{{ step.observation }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { TraceStep } from '@/types/api'

defineProps<{ step: TraceStep; index: number }>()
</script>

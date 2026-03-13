<template>
  <div v-if="verifier" class="card-muted p-4">
    <div class="flex items-center justify-between mb-3">
      <span class="section-label">检索验证</span>
      <span
        :class="[
          'pill text-xs font-medium',
          verifier.ok ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-600'
        ]"
      >{{ verifier.ok ? '通过' : '未通过' }}</span>
    </div>

    <div class="grid grid-cols-3 gap-2 mb-3">
      <div class="text-center">
        <p class="section-label">得分</p>
        <p class="text-base font-semibold text-petal-500 mt-0.5">
          {{ (verifier.verdict.score * 100).toFixed(0) }}%
        </p>
      </div>
      <div class="text-center">
        <p class="section-label">命中块</p>
        <p class="text-base font-semibold text-stone-700 mt-0.5">{{ verifier.verdict.retrieval_count }}</p>
      </div>
      <div class="text-center">
        <p class="section-label">原因</p>
        <p class="text-xs text-stone-500 mt-0.5">{{ verifier.verdict.reason }}</p>
      </div>
    </div>

    <div v-if="verifier.relaxed_query" class="mt-2">
      <p class="section-label mb-1">宽泛查询</p>
      <p class="text-xs text-stone-500 italic">{{ verifier.relaxed_query }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { RetrievalProbe } from '@/types/api'
defineProps<{ verifier?: RetrievalProbe | null }>()
</script>

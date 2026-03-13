<template>
  <div class="flex flex-col gap-5">
    <!-- form card -->
    <div class="card p-5">
      <h2 class="page-title mb-4">✦ Agent Workflow</h2>
      <form class="flex flex-col gap-4" @submit.prevent="submitAgent">
        <BaseTextarea
          v-model="question"
          label="问题"
          placeholder="例：总结这份文档、对比选中的文档、Roast 这个用户…"
          :rows="3"
        />

        <div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
          <!-- method pills -->
          <div class="col-span-2 sm:col-span-1">
            <p class="text-xs font-medium text-stone-500 mb-1.5">检索方式</p>
            <div class="flex gap-1">
              <button
                v-for="m in methods"
                :key="m"
                type="button"
                :class="[
                  'px-2.5 py-1 rounded-full text-xs font-medium transition',
                  method === m
                    ? 'bg-petal-500 text-white'
                    : 'bg-stone-100 text-stone-500 hover:bg-petal-100 hover:text-petal-600'
                ]"
                @click="method = m as any"
              >{{ m }}</button>
            </div>
          </div>

          <BaseInput v-model="topKText" label="Top K" type="number" />
          <BaseInput v-model="targetId"       label="Target ID" placeholder="文档 UUID" />
          <BaseInput v-model="stylePreference" label="风格偏好"  placeholder="sharp_witty" />
        </div>

        <BaseButton label="执行 Agent" type="submit" :loading="pending" loading-text="执行中…" />
      </form>
    </div>

    <!-- results -->
    <template v-if="response">
      <!-- status row -->
      <div class="flex items-center gap-2 flex-wrap">
        <span :class="['pill', response.workflow_status === 'DONE' ? 'bg-petal-100 text-petal-600' : 'bg-stone-100 text-stone-500']">
          {{ response.workflow_status }}
        </span>
        <span class="pill bg-blush-100 text-stone-600 font-mono">{{ response.tool_used }}</span>
        <span class="pill bg-stone-100 text-stone-500">{{ response.trace.length }} steps</span>
      </div>

      <!-- trace timeline -->
      <div class="card p-5">
        <p class="section-label mb-4">推理过程</p>
        <div v-if="response.trace.length" class="flex flex-col">
          <TraceStepItem
            v-for="(step, i) in response.trace"
            :key="`${i}-${step.action}`"
            :step="step"
            :index="i"
          />
        </div>
        <p v-else class="text-sm text-stone-400">无追踪步骤</p>
      </div>

      <!-- fallback notice -->
      <div
        v-if="fallbackNotice"
        class="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800"
      >{{ fallbackNotice }}</div>

      <!-- final answer -->
      <div class="card p-5">
        <div class="flex items-center justify-between mb-3">
          <p class="section-label">最终回答</p>
          <span class="pill bg-blush-100 text-stone-600 text-xs font-mono">{{ response.tool_used }}</span>
        </div>
        <p class="text-sm text-stone-700 leading-relaxed whitespace-pre-wrap">{{ response.final_answer }}</p>
      </div>

      <!-- retrieval verifier -->
      <RetrievalVerifierPanel :verifier="retrievalVerifier" />

      <!-- citations -->
      <div v-if="citations.length" class="card p-5">
        <p class="section-label mb-3">引用 ({{ citations.length }})</p>
        <div class="flex flex-wrap gap-2">
          <CitationChip
            v-for="c in citations"
            :key="c.citation_id"
            :citation="c"
            @open="openCitation"
          />
        </div>
      </div>

      <!-- tool arguments (collapsible) -->
      <details class="card p-4 text-sm">
        <summary class="section-label cursor-pointer select-none">Tool Arguments</summary>
        <pre class="mt-3 overflow-x-auto rounded-lg bg-stone-50 p-3 text-xs text-stone-600 leading-relaxed">{{ toolArgumentsJson }}</pre>
      </details>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useAgent } from '@/composables/useAgent'
import { useCitationPreview } from '@/composables/useCitationPreview'
import { useAgentStore } from '@/stores/agent'
import BaseTextarea from '@/components/atoms/BaseTextarea.vue'
import BaseInput from '@/components/atoms/BaseInput.vue'
import BaseButton from '@/components/atoms/BaseButton.vue'
import CitationChip from '@/components/molecules/CitationChip.vue'
import TraceStepItem from '@/components/molecules/TraceStepItem.vue'
import RetrievalVerifierPanel from './RetrievalVerifierPanel.vue'
import type { RetrievalMethod } from '@/types/api'
import { prettyJson } from '@/utils/format'

const agentStore = useAgentStore()
const question       = ref('')
const targetId       = ref('')
const method         = ref<RetrievalMethod>(agentStore.method)
const topKText       = ref(String(agentStore.topK))
const stylePreference= ref(agentStore.stylePreference)
const methods        = ['vector', 'hybrid', 'rerank']

const { pending, response, submit } = useAgent()
const { openCitation } = useCitationPreview()

watch(method,          v => agentStore.setMethod(v))
watch(stylePreference, v => agentStore.setStylePreference(v))
watch(topKText, v => { const n = Number(v); if (!isNaN(n) && n > 0) agentStore.setTopK(n) })

async function submitAgent() {
  if (!question.value.trim()) return
  await submit(question.value.trim(), targetId.value.trim() || null)
}

const toolArgumentsJson = computed(() => prettyJson(response.value?.tool_arguments || {}))

const retrievalVerifier = computed(() => {
  const r = response.value?.tool_result as Record<string, unknown> | undefined
  return (r?.retrieval_verifier as any) ?? null
})

const citations = computed(() => {
  const r = response.value?.tool_result as Record<string, unknown> | undefined
  return Array.isArray(r?.citations) ? r!.citations : []
})

const fallbackNotice = computed(() => {
  const r = response.value?.tool_result as Record<string, unknown> | undefined
  return typeof r?.fallback_notice === 'string' ? r.fallback_notice : ''
})
</script>

<template>
  <div class="flex gap-6 h-full min-h-0">
    <!-- ── Left panel: form ── -->
    <div class="w-72 shrink-0 flex flex-col gap-4">
      <div class="card p-5">
        <h2 class="page-title mb-1">Roast</h2>
        <p class="text-xs text-stone-400 mb-4">Generate a witty roast from your documents.</p>

        <form class="space-y-4" @submit.prevent="submitRoast">
          <BaseTextarea
            v-model="query"
            label="Roast Query"
            placeholder="Describe the target or paste a prompt…"
            :rows="5"
          />

          <!-- method pills -->
          <div>
            <p class="section-label mb-2">Method</p>
            <div class="flex rounded-lg border border-stone-200 overflow-hidden text-xs font-medium">
              <button
                v-for="m in methods"
                :key="m"
                type="button"
                :class="[
                  'flex-1 py-1.5 transition-colors',
                  method === m
                    ? 'bg-petal-500 text-white'
                    : 'bg-white text-stone-500 hover:bg-petal-50'
                ]"
                @click="method = m"
              >{{ m }}</button>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <BaseInput v-model="topKText" label="Top K" type="number" />
            <BaseInput v-model="stylePreference" label="Style" placeholder="sharp_witty" />
          </div>

          <BaseInput v-model="targetId" label="Target ID" placeholder="doc UUID (optional)" />

          <BaseButton
            label="Run Roast"
            type="submit"
            class="w-full"
            :loading="pending"
            loading-text="Generating…"
          />
        </form>
      </div>
    </div>

    <!-- ── Right panel: results ── -->
    <div class="flex-1 min-w-0 overflow-y-auto flex flex-col gap-5 pr-1">
      <template v-if="response">
        <!-- stat row -->
        <div class="grid grid-cols-4 gap-3">
          <StatCard label="Method" :value="response.method" />
          <StatCard label="Retrieved" :value="response.retrieval_count" />
          <StatCard label="Diag. Rate" :value="response.scores?.diagnosis_rate ?? '—'" />
          <StatCard label="Tags" :value="response.tags.length" />
        </div>

        <!-- persona + radar -->
        <div class="grid gap-5 xl:grid-cols-2">
          <!-- persona -->
          <div class="card p-5 space-y-4">
            <div class="flex items-center justify-between">
              <h3 class="text-sm font-semibold text-stone-800">Persona</h3>
              <span class="pill">{{ response.persona?.persona_name || 'Unknown' }}</span>
            </div>

            <div>
              <p class="section-label mb-2">Core Traits</p>
              <div class="flex flex-wrap gap-2">
                <span
                  v-for="trait in response.persona?.core_traits || []"
                  :key="trait"
                  class="pill"
                >{{ trait }}</span>
              </div>
            </div>

            <div>
              <p class="section-label mb-1">Behavior Pattern</p>
              <p class="text-sm text-stone-700 leading-6">{{ response.persona?.behavior_pattern || '—' }}</p>
            </div>

            <div>
              <p class="section-label mb-1">Roast Angle</p>
              <p class="text-sm text-stone-700 leading-6">{{ response.persona?.roast_angle || '—' }}</p>
            </div>
          </div>

          <!-- radar -->
          <div class="card p-5">
            <div class="flex items-center justify-between mb-3">
              <h3 class="text-sm font-semibold text-stone-800">Score Radar</h3>
              <p class="text-xs text-stone-400">0–100 normalized</p>
            </div>
            <RadarChart :scores="scoreMap" />
          </div>
        </div>

        <!-- tags -->
        <div v-if="response.tags.length" class="flex flex-wrap gap-2">
          <span
            v-for="tag in response.tags"
            :key="tag"
            class="pill bg-blush-100 text-petal-600"
          >#{{ tag }}</span>
        </div>

        <!-- roast text + contradictions -->
        <div class="grid gap-5 xl:grid-cols-[0.9fr_1.1fr]">
          <!-- contradictions -->
          <div class="card p-5">
            <div class="flex items-center justify-between mb-3">
              <h3 class="text-sm font-semibold text-stone-800">Contradictions</h3>
              <BaseBadge tone="warning">{{ response.contradictions.length }}</BaseBadge>
            </div>
            <ul class="space-y-2">
              <li
                v-for="(item, i) in response.contradictions"
                :key="i"
                class="rounded-xl border border-blush-200 bg-blush-50 p-3 text-sm leading-6 text-stone-700"
              >{{ item }}</li>
              <li v-if="!response.contradictions.length" class="text-xs text-stone-400">No contradictions found.</li>
            </ul>
          </div>

          <!-- roast text -->
          <div class="card p-5">
            <h3 class="text-sm font-semibold text-stone-800 mb-3">Roast Text</h3>
            <p class="whitespace-pre-wrap text-sm leading-7 text-stone-800 italic
                       bg-petal-50 border-l-4 border-petal-400 rounded-r-xl px-4 py-3">
              {{ response.roast_text }}
            </p>
          </div>
        </div>

        <!-- citations -->
        <div class="card p-5">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-sm font-semibold text-stone-800">Citations</h3>
            <BaseBadge>{{ response.citations.length }}</BaseBadge>
          </div>
          <div class="grid gap-3">
            <div
              v-for="citation in response.citations"
              :key="citation.citation_id"
              class="card-muted p-3"
            >
              <div class="flex items-center justify-between mb-1">
                <CitationChip :citation="citation" @open="openCitation" />
                <p class="text-xs text-stone-400">
                  doc {{ citation.doc_id || '—' }} · page {{ citation.page_start ?? '—' }}
                </p>
              </div>
              <p class="text-sm leading-6 text-stone-600">{{ citation.snippet || 'No snippet.' }}</p>
            </div>
          </div>
        </div>
      </template>

      <!-- empty state -->
      <div v-else class="flex-1 flex flex-col items-center justify-center gap-3 text-stone-400 min-h-[300px]">
        <span class="text-3xl">✦</span>
        <p class="text-sm">Run a roast to see results here.</p>
      </div>
    </div>
  </div>
  <div class="pointer-events-none fixed bottom-0 right-0 -z-10">
    <img :src="roastImg" class="h-[420px] object-contain opacity-90" />
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import BaseTextarea from '@/components/atoms/BaseTextarea.vue';
import BaseInput from '@/components/atoms/BaseInput.vue';
import BaseButton from '@/components/atoms/BaseButton.vue';
import BaseBadge from '@/components/atoms/BaseBadge.vue';
import CitationChip from '@/components/molecules/CitationChip.vue';
import StatCard from '@/components/molecules/StatCard.vue';
import RadarChart from '@/components/charts/RadarChart.vue';
import { useRoast } from '@/composables/useRoast';
import { useCitationPreview } from '@/composables/useCitationPreview';
import { useAgentStore } from '@/stores/agent';
import type { RetrievalMethod } from '@/types/api';
import roastImg from '@/assets/roast.png'

const agentStore = useAgentStore();

const methods: RetrievalMethod[] = ['vector', 'hybrid', 'rerank'];
const query = ref('');
const targetId = ref('');
const method = ref<RetrievalMethod>(agentStore.method);
const topKText = ref(String(Math.max(agentStore.topK, 6)));
const stylePreference = ref(agentStore.stylePreference);

const { pending, response, submit } = useRoast();
const { openCitation } = useCitationPreview();

watch(method, (v) => agentStore.setMethod(v));
watch(stylePreference, (v) => agentStore.setStylePreference(v));
watch(topKText, (v) => {
  const n = Number(v);
  if (!Number.isNaN(n) && n > 0) agentStore.setTopK(n);
});

async function submitRoast() {
  if (!query.value.trim()) return;
  await submit(query.value.trim(), targetId.value.trim() || null);
}

const scoreMap = computed<Record<string, number>>(() => {
  const maybe = response.value?.scores?.scores;
  return maybe && typeof maybe === 'object' ? (maybe as Record<string, number>) : {};
});
</script>

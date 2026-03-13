<template>
  <div class="p-6 max-w-4xl mx-auto">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xl font-semibold text-gray-900">{{ $t('roast.title') }}</h2>
      <button class="btn-primary" :disabled="loading" @click="handleGenerate">
        <span v-if="loading">{{ $t('roast.generating') }}</span>
        <span v-else>{{ $t('roast.generate') }}</span>
      </button>
    </div>

    <!-- Error -->
    <div v-if="error" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
      {{ error }}
    </div>

    <!-- Loading spinner -->
    <div v-if="loading" class="flex justify-center py-20">
      <svg class="animate-spin h-8 w-8 text-purple-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
      </svg>
    </div>

    <!-- Empty state -->
    <div v-if="!profile && !loading" class="text-center py-20 text-gray-400">
      <img :src="roastIcon" class="w-64 h-64 mx-auto mb-4 opacity-70" />
      <p>{{ hasIndexedDocs ? $t('roast.emptyReady') : $t('roast.empty') }}</p>
    </div>

    <!-- Results -->
    <div v-if="profile && !loading" class="space-y-6">
      <!-- Roast text -->
      <div class="bg-white rounded-xl border border-neutral-200 shadow-sm p-6">
        <p class="text-gray-800 leading-relaxed whitespace-pre-wrap text-[15px]">{{ cleanRoastText(profile.roast_text) }}</p>
      </div>

      <!-- Radar chart + dimension bars -->
      <div class="grid md:grid-cols-2 gap-6">
        <!-- Radar chart -->
        <div class="bg-white rounded-xl border border-neutral-200 shadow-sm p-6">
          <h3 class="font-semibold text-gray-700 mb-4">{{ $t('roast.radarTitle') }}</h3>
          <div class="max-w-[360px] mx-auto">
            <Radar :data="radarData" :options="radarOptions" />
          </div>
        </div>

        <!-- Dimension score bars -->
        <div class="bg-white rounded-xl border border-neutral-200 shadow-sm p-6">
          <h3 class="font-semibold text-gray-700 mb-4">{{ $t('roast.dimensionTitle') }}</h3>
          <div class="space-y-3">
            <div
              v-for="dim in profile.dimension_scores"
              :key="dim.dimension"
              class="flex items-center gap-3"
            >
              <span class="text-xs text-gray-500 w-32 shrink-0 truncate" :title="dim.label || $t(`roast.dimensions.${dim.dimension}`)">
                {{ dim.label || $t(`roast.dimensions.${dim.dimension}`) }}
              </span>
              <div class="flex-1 bg-gray-100 rounded-full h-2">
                <div
                  class="bg-purple-500 h-2 rounded-full transition-all duration-700"
                  :style="{ width: `${normalizeScore(dim.score)}%` }"
                />
              </div>
              <span class="text-xs font-mono text-gray-600 w-8 text-right">{{ dim.score }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Persona tags -->
      <div v-if="profile.persona_tags && profile.persona_tags.length" class="bg-white rounded-xl border border-neutral-200 shadow-sm p-6">
        <h3 class="font-semibold text-gray-700 mb-4">{{ $t('roast.tags') }}</h3>
        <div class="flex flex-wrap gap-2">
          <div
            v-for="tag in profile.persona_tags"
            :key="tag.tag"
            class="group relative"
          >
            <span
              class="px-3 py-1 text-xs rounded-full bg-purple-50 text-purple-700 border border-purple-200 cursor-pointer hover:bg-purple-100 transition-colors inline-flex items-center gap-1"
            >
              {{ tag.label || tag.tag }}
              <span class="text-purple-400">{{ (tag.confidence * 100).toFixed(0) }}%</span>
            </span>
            <div
              v-if="tag.evidence_snippet"
              class="hidden group-hover:block absolute bottom-full left-0 mb-1 w-64 bg-gray-900 text-white text-xs rounded-lg p-2 z-10 shadow-lg"
            >
              {{ tag.evidence_snippet.slice(0, 150) }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Radar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from 'chart.js'
import { useI18n } from 'vue-i18n'
import { useDocumentsStore } from '@/stores/documents'
import { generateRoast } from '@/utils/api'
import type { RoastProfile } from '@/types'

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend)

const { t, locale } = useI18n()
const docsStore = useDocumentsStore()
const hasIndexedDocs = computed(() => docsStore.documents.some((d) => d.status === 'indexed'))

const profile = ref<RoastProfile | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)
const roastIcon = new URL('../Decor/roast.png', import.meta.url).href

// 后端评分范围已改为 0–100（见 backend/app/core/scoring_rules.py）
const MAX_SCORE = 100

function normalizeScore(score: number): number {
  // 分数本身已是 0–100，直接截断取整即可
  return Math.min(100, Math.max(0, Math.round(score)))
}

function cleanRoastText(text: string): string {
  const trimmed = text.trim()
  // If the text looks like a JSON object, try to extract the "roast" field
  if (trimmed.startsWith('{') || trimmed.startsWith('```')) {
    try {
      const stripped = trimmed.replace(/```(?:json)?\s*/g, '').trim()
      const start = stripped.indexOf('{')
      const end = stripped.lastIndexOf('}') + 1
      if (start !== -1 && end > 0) {
        const parsed = JSON.parse(stripped.slice(start, end))
        if (parsed.roast) return parsed.roast
      }
    } catch {
      // fall through to return original
    }
  }
  return text
}

function parseProfile(data: unknown): RoastProfile {
  if (typeof data === 'string') {
    try {
      return JSON.parse(data) as RoastProfile
    } catch {
      throw new Error('Failed to parse roast response')
    }
  }
  return data as RoastProfile
}

async function handleGenerate() {
  loading.value = true
  error.value = null
  try {
    const docIds = docsStore.documents
      .filter((d) => d.status === 'indexed')
      .map((d) => d.id)
    const raw = await generateRoast(docIds, locale.value)
    profile.value = parseProfile(raw)
  } catch (e: any) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

const radarData = computed(() => {
  if (!profile.value) return { labels: [], datasets: [] }
  return {
    labels: profile.value.dimension_scores.map((d) =>
      d.label || t(`roast.dimensions.${d.dimension}`)
    ),
    datasets: [
      {
        label: t('roast.radarTitle'),
        data: profile.value.dimension_scores.map((d) => normalizeScore(d.score)),
        backgroundColor: 'rgba(139, 92, 246, 0.25)',
        borderColor: 'rgba(139, 92, 246, 0.9)',
        pointBackgroundColor: 'rgba(139, 92, 246, 1)',
        pointRadius: 4,
        borderWidth: 2,
        fill: true,
      },
    ],
  }
})

const radarOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: true,
  scales: {
    r: {
      min: 0,
      max: 100,
      ticks: { display: false, stepSize: 20 },
      grid: { color: 'rgba(0,0,0,0.08)' },
      angleLines: { color: 'rgba(0,0,0,0.08)' },
      pointLabels: {
        font: { size: 11 },
        color: '#6b7280',
      },
    },
  },
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: {
        label: (ctx: any) => {
          const raw = profile.value?.dimension_scores[ctx.dataIndex]?.score ?? ctx.raw
          return ` ${raw} / ${MAX_SCORE}`
        },
      },
    },
  },
}))

// Re-render chart when profile updates
watch(profile, () => {}, { deep: true })
</script>

<template>
  <div class="flex flex-col h-full">
    <!-- chat messages -->
    <div ref="scrollEl" class="flex-1 overflow-y-auto px-6 py-5 flex flex-col gap-3 min-h-0">
      <!-- empty state -->
      <div v-if="!messages.length" class="flex flex-col items-center justify-center h-full gap-2 text-center">
        <span class="text-4xl text-petal-200">✦</span>
        <p class="text-sm text-stone-400">问我任何关于你文档的问题</p>
      </div>

      <!-- messages -->
      <template v-for="msg in messages" :key="msg.id">
        <!-- user -->
        <div v-if="msg.role === 'user'" class="flex justify-end">
          <div class="max-w-[70%] bg-stone-800 text-white rounded-2xl rounded-tr-sm px-4 py-3 text-sm leading-relaxed">
            {{ msg.content }}
          </div>
        </div>

        <!-- assistant -->
        <div v-else class="flex justify-start">
          <div class="max-w-[80%] bg-white border-l-2 border-petal-300 rounded-xl rounded-tl-sm px-4 py-3 text-sm text-stone-700 leading-relaxed">
            <template v-for="part in msg.parts" :key="part.key">
              <span v-if="part.type === 'text'">{{ part.value }}</span>
              <CitationChip
                v-else-if="part.type === 'citation' && part.citation"
                :citation="part.citation"
                @open="openCitation"
              />
            </template>
          </div>
        </div>
      </template>

      <!-- loading -->
      <div v-if="pending" class="flex justify-start">
        <div class="bg-white border-l-2 border-petal-200 rounded-xl px-4 py-3">
          <span class="inline-flex gap-1">
            <span class="w-1.5 h-1.5 rounded-full bg-petal-300 animate-bounce" style="animation-delay:0ms" />
            <span class="w-1.5 h-1.5 rounded-full bg-petal-300 animate-bounce" style="animation-delay:150ms" />
            <span class="w-1.5 h-1.5 rounded-full bg-petal-300 animate-bounce" style="animation-delay:300ms" />
          </span>
        </div>
      </div>
    </div>

    <!-- illustration placeholder (above input bar) -->
    <div class="illust-placeholder h-32 mx-6 mb-3 shrink-0">
      <span class="text-3xl">✦</span>
      <span class="text-xs">插画区域</span>
    </div>

    <!-- input bar -->
    <div class="shrink-0 bg-white border-t border-stone-200 px-6 py-4">
      <!-- method pills -->
      <div class="flex gap-1.5 mb-3">
        <button
          v-for="m in methods"
          :key="m"
          :class="[
            'px-3 py-1 rounded-full text-xs font-medium transition',
            method === m
              ? 'bg-petal-500 text-white'
              : 'bg-stone-100 text-stone-500 hover:bg-petal-100 hover:text-petal-600'
          ]"
          @click="method = m as any"
        >{{ m }}</button>
      </div>

      <!-- textarea + send -->
      <form class="flex gap-2 items-end" @submit.prevent="submitAsk">
        <div class="flex-1">
          <textarea
            ref="textareaEl"
            v-model="question"
            rows="1"
            placeholder="输入你的问题…"
            class="w-full rounded-lg border border-stone-200 bg-white px-3 py-2 text-sm text-stone-800
                   placeholder-stone-400 outline-none resize-none transition
                   focus:border-petal-300 focus:ring-2 focus:ring-petal-100"
            @keydown.enter.exact.prevent="submitAsk"
            @input="autoResize"
          />
        </div>
        <BaseButton
          type="submit"
          label="发送"
          size="sm"
          :loading="pending"
          loading-text="…"
        />
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch } from 'vue'
import { storeToRefs } from 'pinia'
import BaseButton from '@/components/atoms/BaseButton.vue'
import CitationChip from '@/components/molecules/CitationChip.vue'
import { useAsk } from '@/composables/useAsk'
import { useCitationPreview } from '@/composables/useCitationPreview'
import { useAgentStore } from '@/stores/agent'
import type { CitationItem, RetrievalMethod } from '@/types/api'

const agentStore = useAgentStore()
const { method: storeMethod } = storeToRefs(agentStore)
const method    = ref<RetrievalMethod>(storeMethod.value)
const question  = ref('')
const textareaEl = ref<HTMLTextAreaElement | null>(null)
const scrollEl   = ref<HTMLDivElement | null>(null)
const methods    = ['vector', 'hybrid', 'rerank']

const { pending, response, submit } = useAsk()
const { openCitation } = useCitationPreview()

watch(method, v => agentStore.setMethod(v))

interface MsgPart { key: string; type: 'text' | 'citation'; value?: string; citation?: CitationItem }
interface Message  { id: number; role: 'user' | 'assistant'; content?: string; parts?: MsgPart[] }

const messages = ref<Message[]>([])
let msgId = 0

function parseAnswer(answer: string, citations: CitationItem[]): MsgPart[] {
  const map = new Map<number, CitationItem>()
  citations.forEach(c => map.set(c.citation_id, c))
  const parts: MsgPart[] = []
  const regex = /\[(\d+)\]/g
  let last = 0, m: RegExpExecArray | null
  while ((m = regex.exec(answer))) {
    if (m.index > last) parts.push({ key: `t${last}`, type: 'text', value: answer.slice(last, m.index) })
    parts.push({ key: `c${m.index}`, type: 'citation', citation: map.get(Number(m[1])) })
    last = regex.lastIndex
  }
  if (last < answer.length) parts.push({ key: `te`, type: 'text', value: answer.slice(last) })
  return parts
}

async function submitAsk() {
  const q = question.value.trim()
  if (!q || pending.value) return
  messages.value.push({ id: msgId++, role: 'user', content: q })
  question.value = ''
  if (textareaEl.value) { textareaEl.value.style.height = 'auto' }
  await nextTick()
  scrollToBottom()
  try {
    const res = await submit(q)
    if (res) {
      messages.value.push({
        id: msgId++,
        role: 'assistant',
        parts: parseAnswer(res.answer, res.citations)
      })
    }
  } finally {
    await nextTick()
    scrollToBottom()
  }
}

function scrollToBottom() {
  if (scrollEl.value) scrollEl.value.scrollTop = scrollEl.value.scrollHeight
}

function autoResize(e: Event) {
  const el = e.target as HTMLTextAreaElement
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 120) + 'px'
}
</script>

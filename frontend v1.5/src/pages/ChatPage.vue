<template>
  <div class="flex flex-col h-screen">
    <!-- Header -->
    <div class="border-b border-gray-200 px-6 py-4 bg-white flex items-center justify-between">
      <div>
        <h2 class="font-semibold text-gray-900">{{ $t('nav.chat') }}</h2>
        <p v-if="!hasIndexedDocs" class="text-xs text-gray-400">{{ $t('chat.noSources') }}</p>
      </div>
      <button class="btn-secondary text-xs" @click="chatStore.clearConversation()">
        新建对话
      </button>
    </div>

    <!-- Messages -->
    <div ref="messagesEl" class="flex-1 overflow-y-auto p-6 space-y-4">
      <div v-if="chatStore.messages.length === 0" class="text-center py-20 text-gray-400">
        <img :src="roastIcon" class="w-64 h-64 mx-auto mb-4 opacity-70" />
        <p>{{ $t('chat.placeholder') }}</p>
      </div>

      <div
        v-for="(msg, i) in chatStore.messages"
        :key="i"
        :class="msg.role === 'user' ? 'flex justify-end' : 'flex justify-start'"
      >
        <div
          :class="[
            'max-w-2xl rounded-2xl px-4 py-3 text-sm',
            msg.role === 'user'
              ? 'bg-primary-600 text-white'
              : 'bg-white border border-gray-200 text-gray-800 shadow-sm',
          ]"
        >
          <p class="whitespace-pre-wrap">{{ msg.content }}</p>

          <!-- Citations -->
          <div v-if="msg.citations && msg.citations.length" class="mt-3 pt-3 border-t border-gray-100">
            <p class="text-xs font-medium text-gray-500 mb-2">{{ $t('chat.citations') }}</p>
            <div v-for="c in msg.citations" :key="c.citation_number" class="text-xs text-gray-500 mb-1">
              <span class="font-mono text-primary-600">[{{ c.citation_number }}]</span>
              {{ c.snippet.slice(0, 120) }}…
            </div>
          </div>

          <!-- Grounded badge -->
          <div v-if="msg.role === 'assistant'" class="mt-2">
            <span :class="msg.is_grounded ? 'badge-green' : 'badge-yellow'">
              {{ msg.is_grounded ? $t('chat.grounded') : $t('chat.ungrounded') }}
            </span>
          </div>
        </div>
      </div>

      <!-- Thinking indicator -->
      <div v-if="chatStore.thinking" class="flex justify-start">
        <div class="bg-white border border-gray-200 rounded-2xl px-4 py-3 shadow-sm">
          <div class="flex gap-1 items-center">
            <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay:0ms"></span>
            <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay:150ms"></span>
            <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay:300ms"></span>
          </div>
        </div>
      </div>
    </div>

    <!-- Input -->
    <div class="border-t border-gray-200 bg-white px-6 py-4">
      <div class="flex gap-3">
        <textarea
          v-model="query"
          :placeholder="$t('chat.placeholder')"
          rows="2"
          class="flex-1 resize-none border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
          @keydown.enter.exact.prevent="handleSend"
        />
        <button
          class="btn-primary self-end"
          :disabled="!query.trim() || chatStore.thinking"
          @click="handleSend"
        >
          {{ $t('chat.send') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch } from 'vue'
import { useChatStore } from '@/stores/chat'
import { useDocumentsStore } from '@/stores/documents'
import { useI18n } from 'vue-i18n'

const { locale } = useI18n()
const chatStore = useChatStore()
const docsStore = useDocumentsStore()
const hasIndexedDocs = computed(() => docsStore.documents.some((d) => d.status === 'indexed'))
const query = ref('')
const messagesEl = ref<HTMLElement | null>(null)
  const roastIcon = new URL('../Decor/ask.png', import.meta.url).href

async function handleSend() {
  const q = query.value.trim()
  if (!q) return
  query.value = ''
  const readyDocIds = docsStore.documents
    .filter((d) => d.status === 'indexed')
    .map((d) => d.id)
  await chatStore.send(q, readyDocIds, locale.value)
  await nextTick()
  messagesEl.value?.scrollTo({ top: messagesEl.value.scrollHeight, behavior: 'smooth' })
}

watch(
  () => chatStore.messages.length,
  async () => {
    await nextTick()
    messagesEl.value?.scrollTo({ top: messagesEl.value.scrollHeight, behavior: 'smooth' })
  },
)
</script>

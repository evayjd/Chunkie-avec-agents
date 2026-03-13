<template>
  <div class="h-full flex">

    <!-- ════════════════════════════════════════════════
         LEFT COLUMN — upload + docs
    ═══════════════════════════════════════════════════ -->
    <section class="flex w-72 shrink-0 flex-col border-r border-blush-200 bg-white">

      <!-- header -->
      <div class="border-b border-blush-100 px-4 py-4">
        <h2 class="text-sm font-semibold text-stone-700">Documents</h2>
        <p class="text-xs text-stone-400 mt-0.5">Upload to begin chatting</p>ƒ
      </div>

      <!-- upload zone -->
      <div class="px-4 py-4 border-b border-blush-100">
        <div
          class="flex cursor-pointer flex-col items-center justify-center gap-2 rounded-xl
                 border-2 border-dashed py-6 transition-all duration-200"
          :class="isDragging
            ? 'border-petal-400 bg-petal-50'
            : 'border-blush-300 bg-blush-50/50 hover:border-petal-300 hover:bg-petal-50/40'"
          @click="fileInput?.click()"
          @dragover.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
          @drop.prevent="handleDrop"
        >
          <div class="flex h-9 w-9 items-center justify-center rounded-full bg-petal-100">
            <svg class="h-4 w-4 text-petal-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round"
                d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5m-13.5-9L12 3m0 0 4.5 4.5M12 3v13.5" />
            </svg>
          </div>
          <span class="text-xs text-stone-500">
            Drop files or <span class="font-medium text-petal-500">browse</span>
          </span>
          <span class="text-[11px] text-stone-400">PDF · TXT · MD · DOCX</span>
          <input
            ref="fileInput"
            type="file"
            class="hidden"
            accept=".pdf,.txt,.md,.html,.docx"
            multiple
            @change="handleFileSelect"
          />
        </div>

        <div v-if="docStore.uploading" class="mt-2 flex items-center gap-2 text-xs text-stone-500">
          <LoadingSpinner size="sm" />
          <span>Processing…</span>
        </div>
        <p v-if="docStore.error" class="mt-1 text-xs text-red-500">{{ docStore.error }}</p>
      </div>

      <!-- doc list -->
      <div class="flex-1 overflow-y-auto px-4 py-3 space-y-1">
        <div v-if="!docStore.documents.length" class="py-6 text-center">
          <p class="text-xs text-stone-400">No documents yet.</p>
          <p class="text-[11px] text-stone-300 mt-0.5">Upload one above to get started.</p>
        </div>

        <button
          v-for="doc in docStore.documents"
          :key="doc.doc_id"
          class="w-full flex items-center gap-2.5 rounded-xl border px-3 py-2 text-left transition-all"
          :class="docStore.selectedDocumentIds.includes(doc.doc_id)
            ? 'border-petal-300 bg-petal-50 text-petal-700'
            : 'border-blush-200 bg-white text-stone-600 hover:border-petal-200 hover:bg-blush-50'"
          @click="docStore.toggleDocument(doc.doc_id)"
        >
          <span class="text-base shrink-0">{{ fileIcon(doc.file_type) }}</span>
          <span class="flex-1 truncate text-xs font-medium">{{ doc.filename }}</span>
          <span
            v-if="docStore.selectedDocumentIds.includes(doc.doc_id)"
            class="h-1.5 w-1.5 shrink-0 rounded-full bg-petal-400"
          />
        </button>

        <p v-if="docStore.documents.length" class="pt-1 text-center text-[11px] text-stone-400">
          {{ docStore.selectedDocumentIds.length
            ? `${docStore.selectedDocumentIds.length} selected`
            : 'Click to filter by document' }}
        </p>
      </div>

      <!-- method selector -->
      <div class="border-t border-blush-100 px-4 py-3">
        <p class="section-label mb-2">Retrieval Method</p>
        <div class="flex rounded-lg border border-stone-200 overflow-hidden text-xs font-medium">
          <button
            v-for="m in methods"
            :key="m"
            class="flex-1 py-1.5 transition-colors"
            :class="agentStore.method === m
              ? 'bg-petal-500 text-white'
              : 'bg-white text-stone-500 hover:bg-petal-50'"
            @click="agentStore.setMethod(m)"
          >{{ m }}</button>
        </div>
      </div>
    </section>

    <!-- ════════════════════════════════════════════════
         RIGHT COLUMN — chat
    ═══════════════════════════════════════════════════ -->
    <section class="flex flex-1 flex-col overflow-hidden">

      <!-- page header -->
      <div class="flex items-center justify-between border-b border-blush-100 bg-white/60 px-6 py-4 shrink-0">
        <div>
          <h1 class="text-base font-semibold text-stone-700">Ask your documents</h1>
          <p class="text-xs text-stone-400 mt-0.5">
            RAG · <span class="font-medium text-stone-500">{{ agentStore.method }}</span>
            · top {{ agentStore.topK }}
          </p>
        </div>
        <button
          v-if="messages.length"
          class="rounded-xl border border-blush-200 px-3 py-1.5 text-xs text-stone-500
                 hover:border-petal-300 hover:text-petal-600 transition-colors"
          @click="messages = []"
        >Clear chat</button>
      </div>

      <!-- messages area -->
      <div ref="chatEl" class="flex-1 overflow-y-auto px-6 py-5 space-y-4">

        <!-- empty state -->
        <div v-if="!messages.length"
          class="flex h-full flex-col items-center justify-center gap-3 text-center pb-10"
        >
          <div class="text-3xl opacity-50">✦</div>
          <p class="text-sm font-medium text-stone-500">Start a conversation</p>
          <p class="text-xs text-stone-400 max-w-xs leading-relaxed">
            Upload a document on the left, then ask anything about it.
          </p>
          <div class="mt-2 flex flex-wrap justify-center gap-2">
            <button
              v-for="s in suggestions"
              :key="s"
              class="rounded-full border border-blush-200 bg-white px-3 py-1.5 text-xs text-stone-600
                     hover:border-petal-300 hover:text-petal-600 transition-colors"
              @click="inputText = s"
            >{{ s }}</button>
          </div>
        </div>

        <!-- message bubbles -->
        <template v-else>
          <div
            v-for="(msg, i) in messages"
            :key="i"
            :class="msg.role === 'user' ? 'flex justify-end' : 'flex justify-start'"
          >
            <!-- user -->
            <div
              v-if="msg.role === 'user'"
              class="max-w-[70%] rounded-2xl rounded-br-sm bg-petal-500 px-4 py-2.5 text-sm text-white"
            >{{ msg.content }}</div>

            <!-- assistant -->
            <div v-else class="max-w-[80%] space-y-2">
              <div class="card px-4 py-3 text-sm text-stone-700 leading-relaxed whitespace-pre-wrap border-l-4 border-petal-200">
                {{ msg.content }}
              </div>
              <div v-if="msg.citations?.length" class="flex flex-wrap gap-1.5">
                <button
                  v-for="c in msg.citations"
                  :key="c.citation_id"
                  class="pill border border-blush-200 bg-blush-50 text-stone-500
                         hover:border-petal-300 hover:text-petal-600 transition-colors"
                  @click="openCitation(c)"
                >
                  [{{ c.citation_id }}]
                  <span v-if="c.page_start" class="text-stone-400 ml-0.5">p.{{ c.page_start }}</span>
                </button>
              </div>
            </div>
          </div>

          <!-- thinking dots -->
          <div v-if="pending" class="flex justify-start">
            <div class="card px-4 py-3 flex items-center gap-2">
              <div class="flex gap-1">
                <span
                  v-for="n in 3"
                  :key="n"
                  class="h-1.5 w-1.5 rounded-full bg-petal-400 animate-bounce"
                  :style="`animation-delay:${(n-1)*150}ms`"
                />
              </div>
              <span class="text-xs text-stone-400">Thinking…</span>
            </div>
          </div>
        </template>
      </div>

      
      <div class="illust-placeholder h-60 mx-6 mb-3 shrink-0 flex items-center justify-center">
        <img :src="ballerinaImg" class="h-full object-contain" />
      </div>

      <!-- input bar -->
      <div class="border-t border-blush-100 bg-white/70 px-5 py-4 shrink-0">
        <div class="flex items-end gap-3">
          <div class="flex-1">
            <textarea
              ref="textareaEl"
              v-model="inputText"
              rows="1"
              placeholder="Ask anything about your documents…"
              class="w-full resize-none rounded-xl border border-blush-200 bg-white px-4 py-3
                     text-sm text-stone-700 placeholder:text-stone-400
                     focus:border-petal-300 focus:outline-none focus:ring-2 focus:ring-petal-100
                     transition-all leading-relaxed"
              style="max-height: 120px; overflow-y: auto"
              @keydown.enter.exact.prevent="sendMessage"
              @input="autoResize"
            />
          </div>
          <button
            class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl
                   bg-petal-500 text-white shadow-sm transition-all
                   hover:bg-petal-600 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="!inputText.trim() || pending"
            @click="sendMessage"
          >
            <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round"
                d="M6 12 3.269 3.125A59.769 59.769 0 0 1 21.485 12 59.768 59.768 0 0 1 3.27 20.875L5.999 12Zm0 0h7.5" />
            </svg>
          </button>
        </div>
        <p class="mt-1.5 text-[11px] text-stone-400">Enter to send · Shift+Enter for newline</p>
      </div>
    </section>

    <div class="pointer-events-none fixed bottom-0 right-0 -z-10">
      <img :src="askImg" class="h-[420px] object-contain opacity-90" />
    </div>

    <!-- citation drawer -->
    <CitationDrawer />
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted } from 'vue'
import { useAsk } from '@/composables/useAsk'
import { useDocumentsStore } from '@/stores/documents'
import { useAgentStore } from '@/stores/agent'
import { useCitationPreview } from '@/composables/useCitationPreview'
import LoadingSpinner from '@/components/atoms/LoadingSpinner.vue'
import CitationDrawer from '@/components/organisms/CitationDrawer.vue'
import type { CitationItem, RetrievalMethod } from '@/types/api'
import askImg from '@/assets/ask.png'


interface Message {
  role: 'user' | 'assistant'
  content: string
  citations?: CitationItem[]
}

const docStore   = useDocumentsStore()
const agentStore = useAgentStore()
const { pending, submit } = useAsk()
const { openCitation } = useCitationPreview()

onMounted(() => docStore.loadDocuments())

const messages  = ref<Message[]>([])
const inputText = ref('')
const isDragging = ref(false)
const fileInput  = ref<HTMLInputElement | null>(null)
const textareaEl = ref<HTMLTextAreaElement | null>(null)
const chatEl     = ref<HTMLElement | null>(null)

const methods: RetrievalMethod[] = ['vector', 'hybrid', 'rerank']
const suggestions = [
  'Summarise the main points',
  'What are the key findings?',
  'List the important dates',
]

function fileIcon(type: string) {
  const m: Record<string, string> = {
    '.pdf': '📄', '.txt': '📝', '.md': '📋', '.docx': '📘', '.html': '🌐', '.htm': '🌐',
  }
  return m[type?.toLowerCase()] ?? '📎'
}

function handleDrop(e: DragEvent) {
  isDragging.value = false
  const files = e.dataTransfer?.files
  if (!files) return
  Array.from(files).forEach(f => docStore.upload(f))
}

function handleFileSelect(e: Event) {
  const files = (e.target as HTMLInputElement).files
  if (!files) return
  Array.from(files).forEach(f => docStore.upload(f))
}

async function sendMessage() {
  const q = inputText.value.trim()
  if (!q || pending.value) return
  messages.value.push({ role: 'user', content: q })
  inputText.value = ''
  autoResize()
  await scrollToBottom()
  try {
    const res = await submit(q)
    if (res) {
      messages.value.push({
        role: 'assistant',
        content: res.answer,
        citations: res.citations,
      })
    }
  } catch {
    messages.value.push({
      role: 'assistant',
      content: 'Something went wrong. Please try again.',
    })
  }
  await scrollToBottom()
}

async function scrollToBottom() {
  await nextTick()
  if (chatEl.value) chatEl.value.scrollTop = chatEl.value.scrollHeight
}

function autoResize() {
  const el = textareaEl.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = `${el.scrollHeight}px`
}
</script>

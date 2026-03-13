<template>
  <TransitionRoot :show="open" as="template">
    <Dialog as="div" class="relative z-50" @close="closeCitation">
      <!-- backdrop -->
      <TransitionChild
        as="template"
        enter="transition-opacity duration-200" enter-from="opacity-0" enter-to="opacity-100"
        leave="transition-opacity duration-150" leave-from="opacity-100" leave-to="opacity-0"
      >
        <div class="fixed inset-0 bg-stone-900/20" />
      </TransitionChild>

      <div class="fixed inset-0 overflow-hidden">
        <div class="absolute inset-0 overflow-hidden">
          <div class="pointer-events-none fixed inset-y-0 right-0 flex max-w-full">
            <TransitionChild
              as="template"
              enter="transform transition duration-200" enter-from="translate-x-full" enter-to="translate-x-0"
              leave="transform transition duration-150" leave-from="translate-x-0" leave-to="translate-x-full"
            >
              <DialogPanel class="pointer-events-auto w-96">
                <div class="flex h-full flex-col bg-white border-l border-stone-200">
                  <!-- header -->
                  <div class="flex items-center justify-between px-5 py-4 border-b border-stone-200">
                    <DialogTitle class="text-sm font-semibold text-stone-800">
                      引用 <span class="text-petal-500">[{{ activeCitation?.citation_id ?? '—' }}]</span>
                    </DialogTitle>
                    <button
                      class="text-stone-400 hover:text-stone-600 transition text-lg leading-none"
                      @click="closeCitation"
                    >×</button>
                  </div>

                  <!-- body -->
                  <div class="flex-1 overflow-y-auto px-5 py-4 space-y-4">
                    <div class="grid grid-cols-2 gap-3">
                      <div class="card-muted p-3">
                        <p class="section-label mb-1">Chunk Index</p>
                        <p class="text-sm text-stone-700">{{ activeCitation?.chunk_index ?? '—' }}</p>
                      </div>
                      <div class="card-muted p-3">
                        <p class="section-label mb-1">页码</p>
                        <p class="text-sm text-stone-700">
                          {{ activeCitation?.page_start ?? '—' }}
                          <span v-if="activeCitation?.page_end && activeCitation.page_end !== activeCitation.page_start">
                            → {{ activeCitation.page_end }}
                          </span>
                        </p>
                      </div>
                    </div>

                    <div v-if="activeCitation?.section" class="card-muted p-3">
                      <p class="section-label mb-1">章节</p>
                      <p class="text-sm text-stone-700">{{ activeCitation.section }}</p>
                    </div>

                    <div class="card p-4">
                      <p class="section-label mb-2">原文片段</p>
                      <p class="text-sm text-stone-700 leading-relaxed whitespace-pre-wrap">
                        {{ activeCitation?.snippet || '后端未返回原文片段。' }}
                      </p>
                    </div>

                    <div v-if="activeCitation?.doc_id" class="card-muted p-3">
                      <p class="section-label mb-1">Doc ID</p>
                      <p class="text-xs font-mono text-stone-500 break-all">{{ activeCitation.doc_id }}</p>
                    </div>
                  </div>
                </div>
              </DialogPanel>
            </TransitionChild>
          </div>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue'
import { useCitationPreview } from '@/composables/useCitationPreview'

const { activeCitation, citationDrawerOpen, closeCitation } = useCitationPreview()
const open = computed(() => citationDrawerOpen.value)
</script>

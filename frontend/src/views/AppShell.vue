<template>
  <div class="flex min-h-screen">
    <!-- ── Sidebar ─────────────────────────────────────── -->
    <aside class="fixed inset-y-0 left-0 z-30 flex w-56 flex-col border-r border-blush-200 bg-white/90 backdrop-blur-sm">

      <!-- Logo -->
      <div class="flex items-center gap-2.5 px-5 py-5 border-b border-blush-100">
        <div class="flex h-8 w-8 items-center justify-center rounded-xl bg-gradient-to-br from-petal-400 to-petal-500 shadow-sm">
          <svg class="h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09Z" />
          </svg>
        </div>
        <span class="text-base font-semibold tracking-tight text-stone-700">Chunkie</span>
      </div>

      <!-- Nav -->
      <nav class="flex-1 space-y-0.5 px-3 py-4">
        <RouterLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="group flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-150"
          :class="isActive(item.to)
            ? 'bg-petal-100/80 text-petal-600'
            : 'text-stone-500 hover:bg-blush-50 hover:text-stone-700'"
        >
          <component
            :is="item.icon"
            class="h-4 w-4 shrink-0 transition-colors"
            :class="isActive(item.to) ? 'text-petal-500' : 'text-stone-400 group-hover:text-stone-600'"
          />
          {{ item.label }}
          <span
            v-if="isActive(item.to)"
            class="ml-auto h-1.5 w-1.5 rounded-full bg-petal-400"
          />
        </RouterLink>
      </nav>

      <!-- Footer hint -->
      <div class="px-5 py-4 border-t border-blush-100">
        <p class="text-[11px] leading-relaxed text-stone-400">
          Upload documents · Ask questions · Get roasted
        </p>
      </div>
    </aside>

    <!-- ── Main content ────────────────────────────────── -->
    <main class="ml-56 flex-1 min-h-0 overflow-y-auto">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import { h } from 'vue'

const route = useRoute()

function isActive(path: string) {
  return route.path === path || (path !== '/' && route.path.startsWith(path))
}

// Icon components (inline SVG as render functions to avoid heroicons dep issues)
const IconAsk = () => h('svg', { fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor', 'stroke-width': '2' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d: 'M8.625 12a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0H8.25m4.125 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0H12m4.125 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 0 1-2.555-.337A5.972 5.972 0 0 1 5.41 20.97a5.969 5.969 0 0 1-.474-.065 4.48 4.48 0 0 0 .978-2.025c.09-.457-.133-.901-.467-1.226C3.93 16.178 3 14.189 3 12c0-4.556 4.03-8.25 9-8.25s9 3.694 9 8.25Z' })
])

const IconAgent = () => h('svg', { fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor', 'stroke-width': '2' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d: 'M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z' })
])

const IconRoast = () => h('svg', { fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor', 'stroke-width': '2' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d: 'M15.182 15.182a4.5 4.5 0 0 1-6.364 0M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0ZM9.75 9.75c0 .414-.168.75-.375.75S9 10.164 9 9.75 9.168 9 9.375 9s.375.336.375.75Zm-.375 0h.008v.015h-.008V9.75Zm5.625 0c0 .414-.168.75-.375.75s-.375-.336-.375-.75.168-.75.375-.75.375.336.375.75Zm-.375 0h.008v.015h-.008V9.75Z' })
])

const navItems = [
  { to: '/ask',   label: 'Ask',   icon: IconAsk   },
  { to: '/agent', label: 'Agent', icon: IconAgent },
  { to: '/roast', label: 'Roast', icon: IconRoast },
]
</script>

<template>
  <!-- 背景容器 -->
  <div class="min-h-screen flex bg-dots">
    <!-- Sidebar -->
    <aside
      class="w-64 bg-white/80 backdrop-blur border-r border-neutral-200 flex flex-col shadow-sm"
    >
      <!-- Logo -->
      <div class="p-6 border-b border-neutral-200">
        <h1 class="text-5xl font-kaeru text-blue-300 tracking-wider">Chunkie</h1>
        <p class="text-xs text-gray-400 mt-1">{{ $t('app.tagline') }}</p>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 p-4 space-y-2">
        <RouterLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="flex items-center gap-3 px-3 py-2 rounded-xl text-sm font-medium transition-all"
          :class="[
            $route.path === item.to
              ? 'bg-primary-100 text-primary-500 shadow-sm'
              : 'text-gray-600 hover:bg-white hover:shadow-sm'
          ]"
        >
          <span class="text-lg">{{ item.icon }}</span>
          {{ $t(item.label) }}
        </RouterLink>
      </nav>

      <!-- Language -->
      <div class="p-4 border-t border-neutral-200">
        <select
          v-model="currentLocale"
          class="w-full text-xs border border-gray-200 rounded-lg px-2 py-1 text-gray-600 bg-white"
        >
          <option value="zh">中文</option>
          <option value="en">English</option>
          <option value="fr">Français</option>
        </select>
      </div>
    </aside>

    <!-- Main content -->
    <main class="flex-1 overflow-auto p-8">
      <RouterView />
    </main>

  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'


const { locale } = useI18n()

const currentLocale = computed({
  get: () => locale.value,
  set: (val) => { locale.value = val },
})

const navItems = [
  { to: '/', icon: '💬', label: 'nav.chat' },
  { to: '/documents', icon: '📄', label: 'nav.documents' },
  { to: '/roast', icon: '🎭', label: 'nav.roast' },
]
</script>


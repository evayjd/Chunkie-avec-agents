<template>
  <div class="fixed right-4 top-4 z-[90] flex w-[360px] max-w-[calc(100vw-2rem)] flex-col gap-3">
    <ToastItem
      v-for="toast in toasts"
      :key="toast.id"
      :toast="toast"
    />
  </div>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { useUiStore } from '@/stores/ui';
import ToastItem from '@/components/molecules/ToastItem.vue';

const ui = useUiStore();
const { toasts } = storeToRefs(ui);
</script>
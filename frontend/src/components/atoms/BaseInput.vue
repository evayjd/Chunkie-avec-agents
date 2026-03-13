<template>
  <div class="w-full">
    <label v-if="label" class="block text-xs font-medium text-stone-500 mb-1">
      {{ label }}
    </label>
    <input
      :value="modelValue"
      :type="type"
      :placeholder="placeholder"
      :disabled="disabled"
      class="w-full rounded-lg border border-stone-200 bg-white px-3 py-2 text-sm text-stone-800
             placeholder-stone-400 outline-none transition
             focus:border-petal-300 focus:ring-2 focus:ring-petal-100
             disabled:opacity-50 disabled:cursor-not-allowed"
      @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
    />
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    modelValue: string
    label?: string
    placeholder?: string
    type?: string
    disabled?: boolean
  }>(),
  { type: 'text', disabled: false }
)

defineEmits<{ (e: 'update:modelValue', value: string): void }>()
</script>

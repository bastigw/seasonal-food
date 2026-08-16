<script setup>
import { computed } from 'vue'
import { strings } from '../i18n/strings.js'

const props = defineProps({
  modelValue: { type: String, required: true },
})
defineEmits(['update:modelValue'])

const ariaLabel = computed(() => strings[props.modelValue].languageSelect)
</script>

<template>
  <div
    class="relative flex flex-none items-center gap-0.5 self-start overflow-hidden rounded-t-xl border-b-2 border-transparent px-2 pb-3 pt-2 text-sm font-medium text-stone-500 transition-colors dark:text-stone-400"
  >
    <span class="text-sm font-semibold tracking-tighter" aria-hidden="true">文A</span>
    <svg
      class="h-3 w-3 opacity-60"
      viewBox="0 0 20 20"
      fill="currentColor"
      aria-hidden="true"
    >
      <path
        fill-rule="evenodd"
        d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z"
        clip-rule="evenodd"
      />
    </svg>
    <select
      class="absolute inset-0 h-full w-full cursor-pointer appearance-none opacity-0"
      :aria-label="ariaLabel"
      :value="modelValue"
      @change="$emit('update:modelValue', $event.target.value)"
    >
      <option value="en">🇬🇧 English</option>
      <option value="de">🇩🇪 Deutsch</option>
    </select>
  </div>
</template>

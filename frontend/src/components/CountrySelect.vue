<script setup>
import { computed } from 'vue'

const props = defineProps({
  countries: { type: Array, required: true },
  modelValue: { type: String, required: true },
})
defineEmits(['update:modelValue'])

const isSelected = computed(() => props.countries.some((c) => c.code === props.modelValue))
const flag = computed(
  () => props.countries.find((c) => c.code === props.modelValue)?.flag ?? '\u{1F310}'
)
</script>

<template>
  <div
    class="relative flex flex-none items-center gap-0.5 self-start rounded-t-xl border-b-2 px-2 pb-3 pt-2 text-sm font-medium transition-colors"
    :class="
      isSelected
        ? 'border-emerald-600 text-emerald-700 dark:border-emerald-400 dark:text-emerald-400'
        : 'border-transparent text-stone-500 dark:text-stone-400'
    "
  >
    <span class="text-base" aria-hidden="true">{{ flag }}</span>
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
      aria-label="More countries"
      :value="isSelected ? modelValue : ''"
      @change="$emit('update:modelValue', $event.target.value)"
    >
      <option value="" disabled>More countries</option>
      <option v-for="country in countries" :key="country.code" :value="country.code">
        {{ country.flag }} {{ country.label }}
      </option>
    </select>
  </div>
</template>

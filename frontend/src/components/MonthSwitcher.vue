<script setup>
import { IconChevronLeft, IconChevronRight } from '@tabler/icons-vue'

defineProps({
  label: { type: String, required: true },
  year: { type: Number, required: true },
})
defineEmits(['prev', 'next'])
</script>

<template>
  <div class="flex items-center justify-center gap-4 px-4 py-4">
    <button
      type="button"
      aria-label="Previous month"
      class="rounded-full p-2 text-stone-500 transition hover:bg-stone-200 active:scale-95 dark:text-stone-400 dark:hover:bg-stone-800"
      @click="$emit('prev')"
    >
      <IconChevronLeft :size="20" :stroke-width="2" />
    </button>
    <h1 class="min-w-[11rem] text-center text-lg font-semibold tracking-tight">
      {{ label }} {{ year }}
    </h1>
    <button
      type="button"
      aria-label="Next month"
      class="rounded-full p-2 text-stone-500 transition hover:bg-stone-200 active:scale-95 dark:text-stone-400 dark:hover:bg-stone-800"
      @click="$emit('next')"
    >
      <IconChevronRight :size="20" :stroke-width="2" />
    </button>
  </div>
</template>

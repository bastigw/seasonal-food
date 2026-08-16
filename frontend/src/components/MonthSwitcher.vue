<script setup>
import { computed } from 'vue'
import { IconChevronLeft, IconChevronRight, IconChevronDown } from '@tabler/icons-vue'
import { strings } from '../i18n/strings.js'

const props = defineProps({
  label: { type: String, required: true },
  monthNames: { type: Array, required: true },
  modelValue: { type: Number, required: true },
  lang: { type: String, default: 'en' },
})
defineEmits(['prev', 'next', 'update:modelValue'])

const t = computed(() => strings[props.lang])
</script>

<template>
  <div class="flex items-center justify-center gap-4 px-4 py-4">
    <button
      type="button"
      :aria-label="t.prevMonth"
      class="rounded-full p-2 text-stone-500 transition hover:bg-stone-200 active:scale-95 dark:text-stone-400 dark:hover:bg-stone-800"
      @click="$emit('prev')"
    >
      <IconChevronLeft :size="20" :stroke-width="2" />
    </button>
    <div class="relative flex min-w-[9rem] items-center justify-center gap-1 overflow-hidden rounded-lg px-2 py-1 transition hover:bg-stone-200 dark:hover:bg-stone-800">
      <h1 class="text-center text-lg font-semibold tracking-tight">
        {{ label }}
      </h1>
      <IconChevronDown :size="16" :stroke-width="2" class="text-stone-400 dark:text-stone-500" />
      <select
        class="absolute inset-0 h-full w-full cursor-pointer appearance-none opacity-0"
        :aria-label="t.selectMonth"
        :value="modelValue"
        @change="$emit('update:modelValue', Number($event.target.value))"
      >
        <option v-for="(name, index) in monthNames" :key="name" :value="index + 1">
          {{ name }}
        </option>
      </select>
    </div>
    <button
      type="button"
      :aria-label="t.nextMonth"
      class="rounded-full p-2 text-stone-500 transition hover:bg-stone-200 active:scale-95 dark:text-stone-400 dark:hover:bg-stone-800"
      @click="$emit('next')"
    >
      <IconChevronRight :size="20" :stroke-width="2" />
    </button>
  </div>
</template>

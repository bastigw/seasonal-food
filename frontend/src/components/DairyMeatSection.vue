<script setup>
import { computed } from 'vue'
import { strings } from '../i18n/strings.js'

const props = defineProps({
  items: { type: Array, required: true },
  lang: { type: String, default: 'en' },
  scaleMax: { type: Number, required: true },
})

const open = defineModel('open', { type: Boolean, default: false })

const t = computed(() => strings[props.lang])
const width = (value) => `${Math.max(4, Math.min(100, (value / props.scaleMax) * 100))}%`
</script>

<template>
  <section class="mt-2 border-t border-stone-100 pt-3 dark:border-stone-900">
    <button
      type="button"
      class="flex w-full items-center gap-1.5 text-left text-sm font-semibold text-stone-700 dark:text-stone-200"
      :aria-expanded="open"
      aria-controls="dairy-meat-list"
      @click="open = !open"
    >
      <span class="text-base" aria-hidden="true">🥩</span>
      {{ t.dairyMeat }}
      <svg
        viewBox="0 0 24 24"
        width="16"
        height="16"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        class="ml-auto text-stone-400 transition-transform motion-reduce:transition-none dark:text-stone-500"
        :class="open ? 'rotate-180' : ''"
        aria-hidden="true"
      >
        <path d="M6 9l6 6 6-6" stroke-linecap="round" stroke-linejoin="round" />
      </svg>
    </button>
    <div v-if="open" id="dairy-meat-list">
      <p class="pb-1 pt-2 text-xs text-stone-500 dark:text-stone-400">{{ t.dairyMeatNote }}</p>
      <ul>
        <li
          v-for="item in items"
          :key="item.id"
          class="grid grid-cols-[6.5rem_minmax(0,1fr)_5.5rem] items-center gap-3 py-1.5"
        >
          <span class="text-sm leading-tight">{{ item.name[lang] }}</span>
          <span class="h-2.5 overflow-hidden rounded-full bg-stone-200 dark:bg-stone-800">
            <span
              class="block h-full rounded-full bg-stone-500 dark:bg-stone-400"
              :style="{ width: width(item.kgCo2ePerKg) }"
            />
          </span>
          <span class="block text-right text-sm font-semibold tabular-nums">{{ item.kgCo2ePerKg.toFixed(1) }}</span>
        </li>
      </ul>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { strings } from '../i18n/strings.js'

const props = defineProps({
  item: { type: Object, required: true },
  lang: { type: String, default: 'en' },
  // kg CO2e per kg that fills the track. Shared by the whole page so bars stay
  // comparable, and raised when the dairy/meat comparison is open.
  scaleMax: { type: Number, required: true },
})

const emit = defineEmits(['select'])

const t = computed(() => strings[props.lang])
const width = computed(() => `${Math.max(4, Math.min(100, (props.item.kgCo2ePerKg / props.scaleMax) * 100))}%`)
const value = computed(() => props.item.kgCo2ePerKg.toFixed(2))
const shortIsLikely = computed(() => props.item.probShort >= 0.5)
const likelihood = computed(() => {
  const pct = Math.round((shortIsLikely.value ? props.item.probShort : props.item.probFar) * 100)
  return (shortIsLikely.value ? t.value.short : t.value.far).replace('{n}', pct)
})
const isRough = computed(() => props.item.confidence === 'low')

const barTone = {
  low: 'bg-emerald-500 dark:bg-emerald-400',
  medium: 'bg-amber-400 dark:bg-amber-400',
  high: 'bg-rose-500 dark:bg-rose-400',
}
</script>

<template>
  <li>
    <button
      type="button"
      class="grid w-full grid-cols-[6.5rem_minmax(0,1fr)_5.5rem] items-center gap-3 rounded-lg py-1.5 text-left transition-colors active:bg-stone-100 dark:active:bg-stone-900"
      @click="emit('select', item)"
    >
      <span class="text-sm leading-tight">{{ item.name[lang] }}</span>
      <span class="h-2.5 overflow-hidden rounded-full bg-stone-200 dark:bg-stone-800">
        <span
          class="block h-full rounded-full transition-[width] duration-500 ease-out motion-reduce:transition-none"
          :class="barTone[item.tier]" :style="{ width }" />
      </span>
      <span class="text-right leading-tight">
        <span class="block text-sm font-semibold tabular-nums">
          {{ value }}<span class="sr-only"> {{ t['tier' + item.tier[0].toUpperCase() + item.tier.slice(1)] }}</span>
        </span>
        <span
          class="block text-[11px]"
          :class="shortIsLikely ? 'text-stone-500 dark:text-stone-400' : 'text-stone-500 dark:text-stone-400'"
          :title="isRough ? t.roughEstimate : undefined"
        >
          <span v-if="isRough" aria-hidden="true">≈ </span>{{ likelihood }}
        </span>
      </span>
    </button>
  </li>
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount, ref, watch } from 'vue'
import { strings } from '../i18n/strings.js'

const props = defineProps({
  item: { type: Object, required: true },
  series: { type: Array, required: true },
  currentMonth: { type: Number, required: true },
  lang: { type: String, default: 'en' },
})

const emit = defineEmits(['close'])

const t = computed(() => strings[props.lang])

const monthLabels = computed(() => {
  const fmt = new Intl.DateTimeFormat(props.lang, { month: 'short', timeZone: 'UTC' })
  return Array.from({ length: 12 }, (_, i) => fmt.format(new Date(Date.UTC(2024, i, 1))))
})

const monthNamesLong = computed(() => {
  const fmt = new Intl.DateTimeFormat(props.lang, { month: 'long', timeZone: 'UTC' })
  return Array.from({ length: 12 }, (_, i) => fmt.format(new Date(Date.UTC(2024, i, 1))))
})

// The month whose breakdown (value, scenario mix, origins) is shown below
// the chart. Defaults to the currently selected month, but clicking any
// other present point on the chart makes that month active instead.
const activeMonth = ref(props.currentMonth)
watch(
  () => props.currentMonth,
  (month) => {
    activeMonth.value = month
  }
)

function selectMonth(entry) {
  if (entry.present) activeMonth.value = entry.month
}

const activeEntry = computed(() => props.series.find((s) => s.month === activeMonth.value))
const activeItem = computed(() => activeEntry.value?.item ?? props.item)
const activeMonthSummary = computed(() => {
  const label = activeMonth.value === props.currentMonth ? t.value.thisMonth : monthNamesLong.value[activeMonth.value - 1]
  return `${label}: ${activeItem.value.kgCo2ePerPortion.toFixed(2)} kg CO₂e`
})

const CHART_W = 300
const CHART_H = 150
const PAD_X = 14
const PAD_TOP = 22
const PAD_BOTTOM = 22

function xFor(monthIndex) {
  return PAD_X + (monthIndex * (CHART_W - 2 * PAD_X)) / 11
}

// Break a series' points into contiguous "present" runs, so a month where
// that country isn't in the top 3 (or the item is out of season) shows as a
// gap instead of a straight line drawn across it.
function pathsFor(points) {
  const paths = []
  let current = ''
  for (const p of points) {
    if (p.present) {
      current += current ? ` L ${p.x} ${p.y}` : `M ${p.x} ${p.y}`
    } else if (current) {
      paths.push(current)
      current = ''
    }
  }
  if (current) paths.push(current)
  return paths
}

const ORIGIN_COLORS = ['#0ea5e9', '#f59e0b', '#10b981', '#a855f7', '#ef4444', '#14b8a6', '#6366f1', '#ec4899']

// One line per origin country, not one blended average line: for every
// month, its own top-3 origins (from originBreakdown) each get their own
// real value plotted, so e.g. Colombia and Costa Rica bananas show as two
// distinct lines instead of one averaged-together figure.
const originCodesInOrder = computed(() => {
  const seen = new Set()
  const codes = []
  for (const entry of props.series) {
    for (const o of entry.item?.originBreakdown ?? []) {
      if (!seen.has(o.code)) {
        seen.add(o.code)
        codes.push(o.code)
      }
    }
  }
  return codes
})

const chartScaleMax = computed(() => {
  const values = props.series.flatMap((entry) => (entry.item?.originBreakdown ?? []).map((o) => o.kgCo2ePerPortion))
  return Math.max(0.01, ...values) * 1.15
})

function yFor(value) {
  const usable = CHART_H - PAD_TOP - PAD_BOTTOM
  const clamped = Math.max(0, Math.min(1, value / chartScaleMax.value))
  return PAD_TOP + usable * (1 - clamped)
}

const originSeries = computed(() => {
  let display
  try {
    display = new Intl.DisplayNames([props.lang], { type: 'region' })
  } catch {
    display = null
  }
  return originCodesInOrder.value.map((code, i) => {
    const points = props.series.map((entry, idx) => {
      const row = (entry.item?.originBreakdown ?? []).find((o) => o.code === code)
      return {
        month: entry.month,
        present: !!row,
        value: row ? row.kgCo2ePerPortion : null,
        x: xFor(idx),
        y: row ? yFor(row.kgCo2ePerPortion) : null,
      }
    })
    return {
      code,
      name: display?.of(code) ?? code,
      color: ORIGIN_COLORS[i % ORIGIN_COLORS.length],
      points,
      linePaths: pathsFor(points),
    }
  })
})

// Whether the item has any month at all where it's absent (out of season),
// for the note below the chart - independent of which origins supply it.
const hasOutOfSeasonMonth = computed(() => props.series.some((s) => !s.present))

const sortedMix = computed(() => {
  const mix = activeItem.value.mix ?? {}
  return Object.entries(mix).sort(([, a], [, b]) => b - a)
})

// Per-country footprint, so e.g. Colombian vs. Costa Rican bananas show up
// as their own real numbers instead of one blended-away figure.
const originRows = computed(() => {
  let display
  try {
    display = new Intl.DisplayNames([props.lang], { type: 'region' })
  } catch {
    display = null
  }
  return (activeItem.value.originBreakdown ?? []).map((o) => ({
    ...o,
    name: display?.of(o.code) ?? o.code,
    proxyNote:
      o.productionSource === 'proxy' && o.proxyFrom
        ? t.value.productionProxy.replace('{country}', display?.of(o.proxyFrom) ?? o.proxyFrom)
        : null,
  }))
})
// Bars scaled relative to the largest of the shown origins, so small
// differences between countries are still visible.
const originScaleMax = computed(() => Math.max(0.01, ...originRows.value.map((o) => o.kgCo2ePerPortion)))

function scenarioLabel(key) {
  return t.value[`scenario_${key}`] ?? key
}

// Production vs. transport (vs. cold storage, where relevant) for the
// active month's item, so it's clear when a footprint is high because of
// how the food was grown rather than how far it travelled.
const breakdownParts = computed(() => {
  const it = activeItem.value
  const total = it.kgCo2ePerPortion || 1
  return [
    { key: 'production', value: it.productionKgPerPortion, color: 'bg-stone-600 dark:bg-stone-300' },
    { key: 'transport', value: it.transportKgPerPortion, color: 'bg-sky-500 dark:bg-sky-400' },
    { key: 'storage', value: it.storageKgPerPortion, color: 'bg-violet-400 dark:bg-violet-400' },
  ]
    .filter((p) => p.value > 0)
    .map((p) => ({ ...p, pct: Math.round((p.value / total) * 100) }))
})

function handleKeydown(event) {
  if (event.key === 'Escape') emit('close')
}

onMounted(() => window.addEventListener('keydown', handleKeydown))
onBeforeUnmount(() => window.removeEventListener('keydown', handleKeydown))

// Swipe-down-to-close for the mobile bottom sheet. The gesture works from
// anywhere on the sheet while its content is scrolled to the top, so a plain
// downward swipe dismisses it; once the content is scrolled, swipes scroll as
// usual and only the handle/header still starts a drag.
const CLOSE_DISTANCE = 60
const CLOSE_VELOCITY = 0.3 // px/ms
const DRAG_SLOP = 6 // px of downward travel before a touch becomes a drag

const sheetEl = ref(null)
const dragging = ref(false)
const dragOffset = ref(0)
let dragArmed = false
let dragStartY = 0
let dragStartTime = 0

const sheetStyle = computed(() => {
  if (!dragging.value || dragOffset.value <= 0) return {}
  return { transform: `translateY(${dragOffset.value}px)`, transition: 'none' }
})

const backdropStyle = computed(() => {
  if (!dragging.value || dragOffset.value <= 0) return {}
  const fade = Math.max(0, 1 - dragOffset.value / 400)
  return { opacity: fade }
})

function onDragStart(event) {
  dragging.value = false
  dragOffset.value = 0
  const inHeader = !!event.target.closest?.('[data-drag-handle]')
  dragArmed = inHeader || (sheetEl.value?.scrollTop ?? 0) <= 0
  dragStartY = event.touches[0].clientY
  dragStartTime = event.timeStamp
}

function onDragMove(event) {
  if (!dragArmed) return
  const delta = event.touches[0].clientY - dragStartY
  if (!dragging.value) {
    if (delta <= DRAG_SLOP) return
    dragging.value = true
  }
  dragOffset.value = Math.max(0, delta - DRAG_SLOP)
  if (event.cancelable) event.preventDefault()
}

function onDragEnd(event) {
  const wasDragging = dragging.value
  const elapsed = event.timeStamp - dragStartTime || 1
  const velocity = dragOffset.value / elapsed
  const shouldClose = wasDragging && (dragOffset.value > CLOSE_DISTANCE || velocity > CLOSE_VELOCITY)
  dragArmed = false
  dragging.value = false
  dragOffset.value = 0
  if (shouldClose) emit('close')
}
</script>

<template>
  <div
    class="fixed inset-0 z-30 flex items-end justify-center bg-stone-950/40 backdrop-blur-sm transition-opacity sm:items-center sm:p-4"
    :style="backdropStyle"
    @click.self="emit('close')"
  >
    <div
      class="max-h-[85vh] w-full max-w-md overflow-y-auto overscroll-y-contain rounded-t-2xl bg-stone-50 p-5 pb-[calc(env(safe-area-inset-bottom)_+_1.25rem)] shadow-xl transition-transform dark:bg-stone-900 sm:max-h-[80vh] sm:rounded-2xl sm:pb-5"
      ref="sheetEl"
      role="dialog"
      aria-modal="true"
      :style="sheetStyle"
      @touchstart.passive="onDragStart"
      @touchmove="onDragMove"
      @touchend="onDragEnd"
      @touchcancel="onDragEnd"
    >
      <div class="-mx-5 -mt-5 mb-2 flex justify-center pb-1 pt-2 sm:hidden" data-drag-handle>
        <span class="h-1.5 w-10 rounded-full bg-stone-300 dark:bg-stone-700" aria-hidden="true" />
      </div>
      <div class="mb-3 flex items-start justify-between gap-3" data-drag-handle>
        <div>
          <h2 class="text-base font-semibold">{{ item.name[lang] }}</h2>
          <p class="text-xs text-stone-500 dark:text-stone-400">{{ activeMonthSummary }}</p>
        </div>
        <button
          type="button"
          class="-m-2 rounded-full p-2 text-stone-400 hover:text-stone-700 dark:hover:text-stone-200"
          :aria-label="t.close"
          @click="emit('close')"
        >
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M6 6l12 12M18 6L6 18" stroke-linecap="round" />
          </svg>
        </button>
      </div>

      <section v-if="breakdownParts.length" class="mb-5">
        <h3 class="mb-2 text-[11px] font-medium uppercase tracking-wide text-stone-400 dark:text-stone-500">
          {{ t.footprintBreakdown }} · {{ monthNamesLong[activeMonth - 1] }}
        </h3>
        <span class="flex h-2.5 overflow-hidden rounded-full bg-stone-200 dark:bg-stone-800">
          <span
            v-for="part in breakdownParts"
            :key="part.key"
            class="block h-full first:rounded-l-full last:rounded-r-full"
            :class="part.color"
            :style="{ width: `${part.pct}%` }"
          />
        </span>
        <ul class="mt-2 space-y-1">
          <li v-for="part in breakdownParts" :key="part.key" class="flex items-center gap-2 text-xs">
            <span class="h-2 w-2 shrink-0 rounded-full" :class="part.color" aria-hidden="true" />
            <span class="text-stone-600 dark:text-stone-300">{{ t[`breakdown_${part.key}`] }}</span>
            <span class="ml-auto shrink-0 tabular-nums text-stone-500 dark:text-stone-400">
              {{ part.value.toFixed(2) }} kg ({{ part.pct }}%)
            </span>
          </li>
        </ul>
      </section>

      <section class="mb-5">
        <h3 class="mb-2 text-[11px] font-medium uppercase tracking-wide text-stone-400 dark:text-stone-500">
          {{ t.yearChartTitle }}
        </h3>
        <svg :viewBox="`0 0 ${CHART_W} ${CHART_H}`" class="w-full" role="img" :aria-label="t.yearChartTitle">
          <template v-for="s in originSeries" :key="s.code">
            <path
              v-for="(d, i) in s.linePaths"
              :key="i"
              :d="d"
              fill="none"
              :stroke="s.color"
              stroke-width="1.75"
              stroke-linecap="round"
            />
            <template v-for="p in s.points" :key="p.month">
              <circle
                v-if="p.present"
                :cx="p.x"
                :cy="p.y"
                :r="p.month === activeMonth ? 4.5 : 2.75"
                :fill="s.color"
                :stroke-width="p.month === currentMonth ? 2 : 0"
                stroke="white"
                class="cursor-pointer"
                role="button"
                tabindex="0"
                :aria-label="`${s.name}, ${monthNamesLong[p.month - 1]}: ${p.value.toFixed(2)} kg CO₂e`"
                @click="selectMonth(p)"
                @keydown.enter="selectMonth(p)"
              />
              <!-- Larger invisible hit target so small dots stay easy to tap. -->
              <circle
                v-if="p.present"
                :cx="p.x"
                :cy="p.y"
                r="9"
                fill="transparent"
                class="cursor-pointer"
                @click="selectMonth(p)"
              />
            </template>
          </template>
          <text
            v-for="(label, i) in monthLabels"
            :key="i"
            :x="xFor(i)"
            :y="CHART_H - 4"
            text-anchor="middle"
            class="pointer-events-none text-[8px]"
            :class="
              i + 1 === activeMonth
                ? 'fill-stone-600 font-medium dark:fill-stone-300'
                : 'fill-stone-400 dark:fill-stone-500'
            "
          >
            {{ label }}
          </text>
        </svg>
        <ul class="mt-1 flex flex-wrap justify-center gap-x-3 gap-y-1">
          <li v-for="s in originSeries" :key="s.code" class="flex items-center gap-1 text-[11px]">
            <span class="h-2 w-2 shrink-0 rounded-full" :style="{ backgroundColor: s.color }" aria-hidden="true" />
            <span class="text-stone-500 dark:text-stone-400">{{ s.name }}</span>
          </li>
        </ul>
        <p v-if="hasOutOfSeasonMonth" class="mt-1 text-[11px] text-stone-400 dark:text-stone-500">
          {{ t.outOfSeason }}: {{ series.filter((s) => !s.present).map((s) => monthLabels[s.month - 1]).join(', ') }}
        </p>
      </section>

      <section v-if="sortedMix.length" class="mb-5">
        <h3 class="mb-2 text-[11px] font-medium uppercase tracking-wide text-stone-400 dark:text-stone-500">
          {{ t.supplyRoutes }} · {{ monthNamesLong[activeMonth - 1] }}
        </h3>
        <ul class="space-y-2">
          <li v-for="[key, share] in sortedMix" :key="key" class="text-xs">
            <div class="mb-1 flex items-baseline justify-between gap-2">
              <span class="text-stone-600 dark:text-stone-300">{{ scenarioLabel(key) }}</span>
              <span class="shrink-0 tabular-nums text-stone-500 dark:text-stone-400">
                {{ Math.round(share * 100) }}%
              </span>
            </div>
            <span class="block h-1.5 overflow-hidden rounded-full bg-stone-200 dark:bg-stone-800">
              <span
                class="block h-full rounded-full bg-stone-400 dark:bg-stone-500"
                :style="{ width: `${Math.round(share * 100)}%` }"
              />
            </span>
          </li>
        </ul>
      </section>

      <section v-if="originRows.length">
        <h3 class="mb-2 text-[11px] font-medium uppercase tracking-wide text-stone-400 dark:text-stone-500">
          {{ t.topOrigins }} · {{ monthNamesLong[activeMonth - 1] }}
        </h3>
        <ul class="space-y-2">
          <li v-for="o in originRows" :key="o.code" class="text-xs">
            <div class="mb-1 flex items-baseline justify-between gap-2">
              <span class="text-stone-600 dark:text-stone-300">
                {{ o.name }} <span class="text-stone-400 dark:text-stone-500">· {{ Math.round(o.share * 100) }}%</span>
              </span>
              <span class="shrink-0 tabular-nums font-medium text-stone-700 dark:text-stone-200">
                {{ o.kgCo2ePerPortion.toFixed(2) }} kg
              </span>
            </div>
            <span class="block h-1.5 overflow-hidden rounded-full bg-stone-200 dark:bg-stone-800">
              <span
                class="block h-full rounded-full bg-stone-400 dark:bg-stone-500"
                :class="o.proxyNote ? 'opacity-60' : ''"
                :style="{ width: `${Math.max(4, (o.kgCo2ePerPortion / originScaleMax) * 100)}%` }"
              />
            </span>
            <span v-if="o.proxyNote" class="mt-0.5 block text-[10px] italic text-stone-400 dark:text-stone-500">
              {{ o.proxyNote }}
            </span>
          </li>
        </ul>
      </section>

      <p v-if="activeItem.confidence === 'low'" class="mt-4 text-[11px] text-stone-400 dark:text-stone-500">
        {{ t.roughEstimate }}
      </p>
    </div>
  </div>
</template>

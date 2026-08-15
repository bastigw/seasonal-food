<script setup>
import { ref, computed, watch } from 'vue'
import seasonalData from './data/seasonal.json'
import CountryTabs from './components/CountryTabs.vue'
import MonthSwitcher from './components/MonthSwitcher.vue'
import ProduceSection from './components/ProduceSection.vue'
import EmptyState from './components/EmptyState.vue'

const { countries, monthNames, data } = seasonalData

function readHash() {
  const params = new URLSearchParams(window.location.hash.slice(1))
  const country = params.get('country')
  const month = Number(params.get('month'))
  const year = Number(params.get('year'))
  return {
    country: countries.some((c) => c.code === country) ? country : null,
    month: month >= 1 && month <= 12 ? month : null,
    year: Number.isInteger(year) ? year : null,
  }
}

const today = new Date()
const initial = readHash()

const selectedCountry = ref(initial.country ?? 'DE')
const selectedMonth = ref(initial.month ?? today.getMonth() + 1)
const selectedYear = ref(initial.year ?? today.getFullYear())

watch([selectedCountry, selectedMonth, selectedYear], ([country, month, year]) => {
  const params = new URLSearchParams({ country, month: String(month), year: String(year) })
  history.replaceState(null, '', `#${params.toString()}`)
})

const monthLabel = computed(() => monthNames[selectedMonth.value - 1])
const currentCountry = computed(() => countries.find((c) => c.code === selectedCountry.value))
const seasonal = computed(() => data[selectedCountry.value][String(selectedMonth.value)])
const freshGroups = computed(() => [...seasonal.value.fresh.vegetable, ...seasonal.value.fresh.fruit])
const storedGroups = computed(() => [...seasonal.value.stored.vegetable, ...seasonal.value.stored.fruit])
const isEmpty = computed(() => freshGroups.value.length === 0 && storedGroups.value.length === 0)

function shiftMonth(delta) {
  let month = selectedMonth.value + delta
  if (month < 1) {
    month = 12
    selectedYear.value -= 1
  } else if (month > 12) {
    month = 1
    selectedYear.value += 1
  }
  selectedMonth.value = month
}
</script>

<template>
  <div class="min-h-dvh bg-stone-50 text-stone-900 dark:bg-stone-950 dark:text-stone-100">
    <div class="mx-auto max-w-md">
      <CountryTabs :countries="countries" v-model="selectedCountry" />
      <MonthSwitcher
        :label="monthLabel"
        :year="selectedYear"
        @prev="shiftMonth(-1)"
        @next="shiftMonth(1)"
      />

      <main class="px-4 pb-12">
        <p
          v-if="currentCountry.note"
          class="mb-4 text-sm text-stone-500 dark:text-stone-400"
        >
          {{ currentCountry.note }}
        </p>

        <Transition name="fade" mode="out-in">
          <div :key="`${selectedCountry}-${selectedMonth}`">
            <EmptyState v-if="isEmpty" label="Nothing tracked for this month yet." />
            <template v-else>
              <ProduceSection title="Fresh this month" :groups="freshGroups" tone="fresh" />
              <ProduceSection title="Still in season, from storage" :groups="storedGroups" tone="stored" />
            </template>
          </div>
        </Transition>

        <p class="pt-4 text-center text-xs text-stone-400 dark:text-stone-600">
          Data from EUFIC (eufic.org)
        </p>
      </main>
    </div>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.fade-enter-from {
  opacity: 0;
  transform: translateY(4px);
}
.fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

@media (prefers-reduced-motion: reduce) {
  .fade-enter-active,
  .fade-leave-active {
    transition: none;
  }
}
</style>

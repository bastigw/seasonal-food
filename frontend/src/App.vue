<script setup>
import { ref, computed, watch } from 'vue'
import seasonalData from './data/seasonal.json'
import CountryTabs from './components/CountryTabs.vue'
import CountrySelect from './components/CountrySelect.vue'
import MonthSwitcher from './components/MonthSwitcher.vue'
import ProduceSection from './components/ProduceSection.vue'
import EmptyState from './components/EmptyState.vue'

const { countries, monthNames, data } = seasonalData
const mainCountries = countries.filter((c) => c.main)
const otherCountries = countries.filter((c) => !c.main)

function readHash() {
  const params = new URLSearchParams(window.location.hash.slice(1))
  const country = params.get('country')
  const month = Number(params.get('month'))
  return {
    country: countries.some((c) => c.code === country) ? country : null,
    month: month >= 1 && month <= 12 ? month : null,
  }
}

const today = new Date()
const initial = readHash()

const selectedCountry = ref(initial.country ?? 'GB')
const selectedMonth = ref(initial.month ?? today.getMonth() + 1)

watch([selectedCountry, selectedMonth], ([country, month]) => {
  const params = new URLSearchParams({ country, month: String(month) })
  history.replaceState(null, '', `#${params.toString()}`)
})

const monthLabel = computed(() => monthNames[selectedMonth.value - 1])
const seasonal = computed(() => data[selectedCountry.value][String(selectedMonth.value)])
const freshVeg = computed(() => seasonal.value.fresh.vegetable)
const freshFruit = computed(() => seasonal.value.fresh.fruit)
const storedVeg = computed(() => seasonal.value.stored.vegetable)
const storedFruit = computed(() => seasonal.value.stored.fruit)
const isEmpty = computed(
  () =>
    !freshVeg.value.length &&
    !freshFruit.value.length &&
    !storedVeg.value.length &&
    !storedFruit.value.length
)

function shiftMonth(delta) {
  let month = selectedMonth.value + delta
  if (month < 1) month = 12
  else if (month > 12) month = 1
  selectedMonth.value = month
}
</script>

<template>
  <div class="min-h-dvh bg-stone-50 text-stone-900 dark:bg-stone-950 dark:text-stone-100">
    <div class="mx-auto max-w-md">
      <nav
        class="sticky top-0 z-10 flex gap-1 border-b border-stone-200 bg-stone-50/90 px-3 pt-3 backdrop-blur dark:border-stone-800 dark:bg-stone-950/90"
        aria-label="Country"
      >
        <CountryTabs :countries="mainCountries" v-model="selectedCountry" />
        <CountrySelect :countries="otherCountries" v-model="selectedCountry" />
      </nav>
      <MonthSwitcher :label="monthLabel" @prev="shiftMonth(-1)" @next="shiftMonth(1)" />

      <main class="px-4 pb-12">
        <Transition name="fade" mode="out-in">
          <div :key="`${selectedCountry}-${selectedMonth}`">
            <EmptyState v-if="isEmpty" label="Nothing tracked for this month yet." />
            <template v-else>
              <ProduceSection
                title="Fresh this month"
                :vegetable-groups="freshVeg"
                :fruit-groups="freshFruit"
                tone="fresh"
              />
              <ProduceSection
                title="Still in season, from storage"
                :vegetable-groups="storedVeg"
                :fruit-groups="storedFruit"
                tone="stored"
              />
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

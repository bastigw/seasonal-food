<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import seasonalData from './data/seasonal.json'
import { strings } from './i18n/strings.js'
import {
  countryNames as deCountryNames,
  monthNames as deMonthNames,
  groupNames as deGroupNames,
  produceNames as deProduceNames,
} from './i18n/translations.js'
import LanguageSelect from './components/LanguageSelect.vue'
import CountryTabs from './components/CountryTabs.vue'
import CountrySelect from './components/CountrySelect.vue'
import MonthSwitcher from './components/MonthSwitcher.vue'
import ProduceSection from './components/ProduceSection.vue'
import EmptyState from './components/EmptyState.vue'

const { countries, monthNames, data } = seasonalData

function readHash() {
  const params = new URLSearchParams(window.location.hash.slice(1))
  const country = params.get('country')
  const month = Number(params.get('month'))
  const lang = params.get('lang')
  return {
    country: countries.some((c) => c.code === country) ? country : null,
    month: month >= 1 && month <= 12 ? month : null,
    lang: lang === 'en' || lang === 'de' ? lang : null,
  }
}

function detectLanguage() {
  const browserLang = typeof navigator !== 'undefined' ? navigator.language : ''
  return browserLang?.toLowerCase().startsWith('de') ? 'de' : 'en'
}

function initialLanguage(hashLang) {
  if (hashLang) return hashLang
  const saved = localStorage.getItem('lang')
  if (saved === 'en' || saved === 'de') return saved
  return detectLanguage()
}

const today = new Date()
const initial = readHash()

const selectedCountry = ref(initial.country ?? 'GB')
const selectedMonth = ref(initial.month ?? today.getMonth() + 1)
const selectedLanguage = ref(initialLanguage(initial.lang))

watch([selectedCountry, selectedMonth, selectedLanguage], ([country, month, lang]) => {
  const params = new URLSearchParams({ country, month: String(month), lang })
  history.replaceState(null, '', `#${params.toString()}`)
  localStorage.setItem('lang', lang)
})

const t = computed(() => strings[selectedLanguage.value])

watch(
  selectedLanguage,
  (lang) => {
    document.title = strings[lang].pageTitle
  },
  { immediate: true }
)

const localizedCountries = computed(() =>
  countries.map((c) => ({
    ...c,
    label: selectedLanguage.value === 'de' ? deCountryNames[c.code] ?? c.label : c.label,
  }))
)
const mainCountries = computed(() => localizedCountries.value.filter((c) => c.main))
const otherCountries = computed(() => localizedCountries.value.filter((c) => !c.main))

const localizedMonthNames = computed(() =>
  selectedLanguage.value === 'de' ? deMonthNames : monthNames
)

function localizeGroups(groups) {
  return groups.map((group) => ({
    ...group,
    label: selectedLanguage.value === 'de' ? deGroupNames[group.group] ?? group.group : group.group,
    items: group.items.map((item) => ({
      ...item,
      name:
        selectedLanguage.value === 'de'
          ? deProduceNames[item.name.toLowerCase()] ?? item.name
          : item.name,
    })),
  }))
}

const monthLabel = computed(() => localizedMonthNames.value[selectedMonth.value - 1])
const seasonal = computed(() => data[selectedCountry.value][String(selectedMonth.value)])
const freshVeg = computed(() => localizeGroups(seasonal.value.fresh.vegetable))
const freshFruit = computed(() => localizeGroups(seasonal.value.fresh.fruit))
const storedVeg = computed(() => localizeGroups(seasonal.value.stored.vegetable))
const storedFruit = computed(() => localizeGroups(seasonal.value.stored.fruit))
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

// In standalone mode the selector bar is pinned to the bottom of the
// viewport, so the food list needs matching padding-bottom to avoid
// being hidden behind it. Measure the bar so that padding stays exact
// as its content (flags, translations, safe-area insets) changes.
const footerEl = ref(null)
const footerHeight = ref(0)
let footerObserver

onMounted(() => {
  if (footerEl.value && typeof ResizeObserver !== 'undefined') {
    footerObserver = new ResizeObserver(([entry]) => {
      footerHeight.value = entry.target.offsetHeight
    })
    footerObserver.observe(footerEl.value)
  }
})

onBeforeUnmount(() => {
  footerObserver?.disconnect()
})
</script>

<template>
  <div class="min-h-dvh bg-stone-50 text-stone-900 dark:bg-stone-950 dark:text-stone-100">
    <div class="mx-auto flex max-w-md flex-col standalone:min-h-dvh">
      <div
        ref="footerEl"
        class="order-1 standalone:order-2 standalone:sticky standalone:bottom-0 standalone:z-20 standalone:border-t standalone:border-stone-200 standalone:bg-stone-50/90 standalone:pb-[env(safe-area-inset-bottom)] standalone:backdrop-blur dark:standalone:border-stone-800 dark:standalone:bg-stone-950/90"
      >
        <nav
          class="sticky top-0 z-10 flex gap-1 border-b border-stone-200 bg-stone-50/90 px-3 pt-3 backdrop-blur standalone:static standalone:z-auto standalone:border-b-0 dark:border-stone-800 dark:bg-stone-950/90"
          :aria-label="t.countryNav"
        >
          <LanguageSelect v-model="selectedLanguage" />
          <CountryTabs :countries="mainCountries" v-model="selectedCountry" />
          <CountrySelect :countries="otherCountries" v-model="selectedCountry" :lang="selectedLanguage" />
        </nav>
        <MonthSwitcher
          :label="monthLabel"
          :month-names="localizedMonthNames"
          v-model="selectedMonth"
          :lang="selectedLanguage"
          @prev="shiftMonth(-1)"
          @next="shiftMonth(1)"
        />
      </div>

      <main
        class="order-2 px-4 pb-12 standalone:order-1 standalone:flex-1 standalone:pb-[var(--footer-h)] standalone:pt-[calc(env(safe-area-inset-top)_+_1.5rem)]"
        :style="{ '--footer-h': footerHeight ? `${footerHeight}px` : '7rem' }"
      >
        <Transition name="fade" mode="out-in">
          <div :key="`${selectedCountry}-${selectedMonth}`">
            <EmptyState v-if="isEmpty" :label="t.emptyState" />
            <template v-else>
              <ProduceSection
                :title="t.freshTitle"
                :vegetable-groups="freshVeg"
                :fruit-groups="freshFruit"
                tone="fresh"
                :lang="selectedLanguage"
              />
              <ProduceSection
                :title="t.storedTitle"
                :vegetable-groups="storedVeg"
                :fruit-groups="storedFruit"
                tone="stored"
                :lang="selectedLanguage"
              />
            </template>
          </div>
        </Transition>

        <p class="pt-4 text-center text-xs text-stone-400 dark:text-stone-600 standalone:pt-2">
          {{ t.dataSource }}
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

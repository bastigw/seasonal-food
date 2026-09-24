<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import impactData from './data/impact.json'
import { strings } from './i18n/strings.js'
import LanguageSelect from './components/LanguageSelect.vue'
import CountryTabs from './components/CountryTabs.vue'
import MonthSwitcher from './components/MonthSwitcher.vue'
import ImpactSection from './components/ImpactSection.vue'
import ItemDetailSheet from './components/ItemDetailSheet.vue'
import { buildItemSeries } from './lib/impactSeries.js'

const { countries, data } = impactData

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

const selectedLanguage = ref(initialLanguage(initial.lang))
const selectedCountry = ref(initial.country ?? (selectedLanguage.value === 'de' ? 'DE' : 'GB'))
const selectedMonth = ref(initial.month ?? today.getMonth() + 1)

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
  countries.map((c) => ({ ...c, label: c.label[selectedLanguage.value] }))
)

const localizedMonthNames = computed(() => {
  const fmt = new Intl.DateTimeFormat(selectedLanguage.value, { month: 'long', timeZone: 'UTC' })
  return Array.from({ length: 12 }, (_, i) => fmt.format(new Date(Date.UTC(2024, i, 1))))
})

const monthLabel = computed(() => localizedMonthNames.value[selectedMonth.value - 1])
const impact = computed(() => data[selectedCountry.value][String(selectedMonth.value)])
const isEmpty = computed(() => !impact.value.vegetable.length && !impact.value.fruit.length)

const selectedItemId = ref(null)
const selectedItem = computed(() => {
  if (!selectedItemId.value) return null
  const groups = [...impact.value.vegetable, ...impact.value.fruit]
  for (const group of groups) {
    const match = group.items.find((item) => item.id === selectedItemId.value)
    if (match) return match
  }
  return null
})
const selectedItemSeries = computed(() =>
  selectedItemId.value ? buildItemSeries(data, selectedCountry.value, selectedItemId.value).series : []
)

// If country/month changes to where the selected item no longer appears
// (out of season, or not grown in that country), close the sheet instead
// of showing stale data.
watch(selectedItem, (item) => {
  if (!item) selectedItemId.value = null
})

function openItemDetail(item) {
  selectedItemId.value = item.id
}

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
          <CountryTabs :countries="localizedCountries" v-model="selectedCountry" />
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
            <p v-if="isEmpty" class="py-12 text-center text-sm text-stone-400 dark:text-stone-500">
              {{ t.emptyState }}
            </p>
            <template v-else>
              <p class="pb-3 text-xs text-stone-500 dark:text-stone-400">{{ t.legend }}</p>
              <ImpactSection
                icon="🥕"
                :title="t.vegetables"
                :groups="impact.vegetable"
                :lang="selectedLanguage"
                @select="openItemDetail"
              />
              <ImpactSection
                icon="🍎"
                :title="t.fruit"
                :groups="impact.fruit"
                :lang="selectedLanguage"
                @select="openItemDetail"
              />
            </template>
          </div>
        </Transition>

        <p class="pt-4 text-center text-xs text-stone-400 dark:text-stone-600 standalone:pt-2">
          {{ t.disclaimer }}
        </p>
      </main>

      <ItemDetailSheet
        v-if="selectedItem"
        :item="selectedItem"
        :series="selectedItemSeries"
        :current-month="selectedMonth"
        :lang="selectedLanguage"
        @close="selectedItemId = null"
      />
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

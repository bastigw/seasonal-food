<script setup>
import { computed, reactive, ref } from 'vue'
import CollapsibleSection from './CollapsibleSection.vue'

const props = defineProps({
  title: { type: String, required: true },
  vegetableGroups: { type: Array, required: true },
  fruitGroups: { type: Array, required: true },
  tone: { type: String, required: true }, // 'fresh' | 'stored'
})

const chipTone = {
  fresh: {
    vegetable:
      'border-emerald-200 bg-emerald-50 text-emerald-800 dark:border-emerald-900 dark:bg-emerald-950 dark:text-emerald-300',
    fruit:
      'border-amber-200 bg-amber-50 text-amber-800 dark:border-amber-900 dark:bg-amber-950 dark:text-amber-300',
  },
  stored: {
    vegetable:
      'border-stone-200 bg-stone-100 text-stone-600 dark:border-stone-800 dark:bg-stone-900 dark:text-stone-400',
    fruit:
      'border-stone-200 bg-stone-100 text-stone-600 dark:border-stone-800 dark:bg-stone-900 dark:text-stone-400',
  },
}

// Groups this small already take up about as much room collapsed as
// expanded, so there's no point making them start closed.
const SMALL_GROUP_THRESHOLD = 3

const isSmall = (group) => group.items.length <= SMALL_GROUP_THRESHOLD

function initialOpenState(groups) {
  const state = {}
  for (const group of groups) {
    state[group.group] = isSmall(group)
  }
  return reactive(state)
}

const countOf = (groups) => groups.reduce((sum, group) => sum + group.items.length, 0)

const vegOpen = ref(true)
const vegGroupOpen = initialOpenState(props.vegetableGroups)
const vegCount = computed(() => countOf(props.vegetableGroups))
const allVegOpen = computed(() => props.vegetableGroups.every((g) => vegGroupOpen[g.group]))
function toggleAllVeg() {
  const next = !allVegOpen.value
  for (const group of props.vegetableGroups) vegGroupOpen[group.group] = next
}
function resetVeg() {
  vegOpen.value = true
  for (const group of props.vegetableGroups) vegGroupOpen[group.group] = isSmall(group)
}

const fruitOpen = ref(true)
const fruitGroupOpen = initialOpenState(props.fruitGroups)
const fruitCount = computed(() => countOf(props.fruitGroups))
const allFruitOpen = computed(() => props.fruitGroups.every((g) => fruitGroupOpen[g.group]))
function toggleAllFruit() {
  const next = !allFruitOpen.value
  for (const group of props.fruitGroups) fruitGroupOpen[group.group] = next
}
function resetFruit() {
  fruitOpen.value = true
  for (const group of props.fruitGroups) fruitGroupOpen[group.group] = isSmall(group)
}
</script>

<template>
  <section v-if="vegetableGroups.length || fruitGroups.length" class="mb-5">
    <h2 class="mb-2 text-xs font-semibold uppercase tracking-wide text-stone-400 dark:text-stone-500">
      {{ title }}
    </h2>

    <CollapsibleSection
      v-if="vegetableGroups.length"
      v-model="vegOpen"
      icon="🥕"
      label="Vegetables"
      :count="vegCount"
      size="category"
      class="mb-1 border-b border-stone-200 dark:border-stone-800"
    >
      <div v-if="vegetableGroups.length > 1" class="flex items-center justify-end gap-3 pb-1">
        <button
          type="button"
          class="text-xs font-medium text-stone-500 hover:underline dark:text-stone-400"
          @click="resetVeg"
        >
          Reset
        </button>
        <button
          type="button"
          class="text-xs font-medium text-emerald-700 hover:underline dark:text-emerald-400"
          @click="toggleAllVeg"
        >
          {{ allVegOpen ? 'Collapse all' : 'Expand all' }}
        </button>
      </div>
      <CollapsibleSection
        v-for="group in vegetableGroups"
        :key="group.group"
        v-model="vegGroupOpen[group.group]"
        :icon="group.icon"
        :label="group.group"
        :count="group.items.length"
        size="group"
        class="border-t border-stone-100 first:border-t-0 dark:border-stone-900"
      >
        <div class="flex flex-wrap gap-1.5 pb-2">
          <span
            v-for="item in group.items"
            :key="item.name"
            class="inline-flex items-center gap-1 rounded-full border px-3 py-1 text-sm"
            :class="chipTone[tone].vegetable"
          >
            <span aria-hidden="true">{{ item.icon }}</span>
            {{ item.name }}
            <span v-if="item.stage" class="opacity-60">({{ item.stage }})</span>
          </span>
        </div>
      </CollapsibleSection>
    </CollapsibleSection>

    <CollapsibleSection
      v-if="fruitGroups.length"
      v-model="fruitOpen"
      icon="🍎"
      label="Fruit"
      :count="fruitCount"
      size="category"
    >
      <div v-if="fruitGroups.length > 1" class="flex items-center justify-end gap-3 pb-1">
        <button
          type="button"
          class="text-xs font-medium text-stone-500 hover:underline dark:text-stone-400"
          @click="resetFruit"
        >
          Reset
        </button>
        <button
          type="button"
          class="text-xs font-medium text-amber-700 hover:underline dark:text-amber-400"
          @click="toggleAllFruit"
        >
          {{ allFruitOpen ? 'Collapse all' : 'Expand all' }}
        </button>
      </div>
      <CollapsibleSection
        v-for="group in fruitGroups"
        :key="group.group"
        v-model="fruitGroupOpen[group.group]"
        :icon="group.icon"
        :label="group.group"
        :count="group.items.length"
        size="group"
        class="border-t border-stone-100 first:border-t-0 dark:border-stone-900"
      >
        <div class="flex flex-wrap gap-1.5 pb-2">
          <span
            v-for="item in group.items"
            :key="item.name"
            class="inline-flex items-center gap-1 rounded-full border px-3 py-1 text-sm"
            :class="chipTone[tone].fruit"
          >
            <span aria-hidden="true">{{ item.icon }}</span>
            {{ item.name }}
            <span v-if="item.stage" class="opacity-60">({{ item.stage }})</span>
          </span>
        </div>
      </CollapsibleSection>
    </CollapsibleSection>
  </section>
</template>

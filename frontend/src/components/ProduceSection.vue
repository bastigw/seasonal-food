<script setup>
import { computed } from 'vue'
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

const countOf = (groups) => groups.reduce((sum, group) => sum + group.items.length, 0)
const vegCount = computed(() => countOf(props.vegetableGroups))
const fruitCount = computed(() => countOf(props.fruitGroups))
</script>

<template>
  <section v-if="vegetableGroups.length || fruitGroups.length" class="mb-5">
    <h2 class="mb-2 text-xs font-semibold uppercase tracking-wide text-stone-400 dark:text-stone-500">
      {{ title }}
    </h2>

    <CollapsibleSection
      v-if="vegetableGroups.length"
      icon="🥕"
      label="Vegetables"
      :count="vegCount"
      size="category"
      class="mb-1 border-b border-stone-200 dark:border-stone-800"
    >
      <CollapsibleSection
        v-for="group in vegetableGroups"
        :key="group.group"
        :icon="group.icon"
        :label="group.group"
        :count="group.items.length"
        size="group"
        :default-open="false"
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
      icon="🍎"
      label="Fruit"
      :count="fruitCount"
      size="category"
    >
      <CollapsibleSection
        v-for="group in fruitGroups"
        :key="group.group"
        :icon="group.icon"
        :label="group.group"
        :count="group.items.length"
        size="group"
        :default-open="false"
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

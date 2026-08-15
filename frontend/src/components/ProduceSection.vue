<script setup>
defineProps({
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
</script>

<template>
  <section v-if="vegetableGroups.length || fruitGroups.length" class="mb-6">
    <h2 class="mb-3 text-xs font-semibold uppercase tracking-wide text-stone-400 dark:text-stone-500">
      {{ title }}
    </h2>

    <div v-if="vegetableGroups.length" class="mb-4">
      <h3 class="mb-2 flex items-center gap-1.5 text-sm font-semibold text-stone-700 dark:text-stone-200">
        <span aria-hidden="true">🥕</span> Vegetables
      </h3>
      <div v-for="group in vegetableGroups" :key="group.group" class="mb-3">
        <p class="mb-1.5 flex items-center gap-1 text-[11px] font-medium uppercase tracking-wide text-stone-400 dark:text-stone-500">
          <span aria-hidden="true">{{ group.icon }}</span> {{ group.group }}
        </p>
        <div class="flex flex-wrap gap-1.5">
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
      </div>
    </div>

    <div v-if="fruitGroups.length">
      <h3 class="mb-2 flex items-center gap-1.5 text-sm font-semibold text-stone-700 dark:text-stone-200">
        <span aria-hidden="true">🍎</span> Fruit
      </h3>
      <div v-for="group in fruitGroups" :key="group.group" class="mb-3">
        <p class="mb-1.5 flex items-center gap-1 text-[11px] font-medium uppercase tracking-wide text-stone-400 dark:text-stone-500">
          <span aria-hidden="true">{{ group.icon }}</span> {{ group.group }}
        </p>
        <div class="flex flex-wrap gap-1.5">
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
      </div>
    </div>
  </section>
</template>

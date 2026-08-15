<script setup>
defineProps({
  title: { type: String, required: true },
  groups: { type: Array, required: true },
  tone: { type: String, required: true }, // 'fresh' | 'stored'
})
</script>

<template>
  <section v-if="groups.length" class="mb-6">
    <h2 class="mb-3 text-xs font-semibold uppercase tracking-wide text-stone-400 dark:text-stone-500">
      {{ title }}
    </h2>
    <div v-for="group in groups" :key="group.group" class="mb-4">
      <h3 class="mb-2 text-[11px] font-medium uppercase tracking-wide text-stone-400 dark:text-stone-500">
        {{ group.group }}
      </h3>
      <div class="flex flex-wrap gap-1.5">
        <span
          v-for="item in group.items"
          :key="item.name"
          class="inline-flex items-center rounded-full border px-3 py-1 text-sm"
          :class="
            tone === 'fresh'
              ? 'border-emerald-200 bg-emerald-50 text-emerald-800 dark:border-emerald-900 dark:bg-emerald-950 dark:text-emerald-300'
              : 'border-stone-200 bg-stone-100 text-stone-600 dark:border-stone-800 dark:bg-stone-900 dark:text-stone-400'
          "
        >
          {{ item.name }}
          <span v-if="item.stage" class="ml-1 opacity-60">({{ item.stage }})</span>
        </span>
      </div>
    </div>
  </section>
</template>

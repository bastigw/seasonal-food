<script setup>
import ImpactRow from './ImpactRow.vue'

defineProps({
  icon: { type: String, required: true },
  title: { type: String, required: true },
  groups: { type: Array, required: true },
  lang: { type: String, default: 'en' },
})

const emit = defineEmits(['select'])
</script>

<template>
  <section v-if="groups.length" class="mb-6">
    <h2 class="mb-1 flex items-center gap-1.5 text-sm font-semibold text-stone-700 dark:text-stone-200">
      <span class="text-base" aria-hidden="true">{{ icon }}</span>
      {{ title }}
    </h2>
    <div v-for="group in groups" :key="group.group" class="border-t border-stone-100 pt-2 dark:border-stone-900">
      <h3 class="text-[11px] font-medium uppercase tracking-wide text-stone-400 dark:text-stone-500">
        {{ group.label[lang] }}
      </h3>
      <ul class="pb-1">
        <ImpactRow
          v-for="item in group.items"
          :key="item.id"
          :item="item"
          :lang="lang"
          @select="emit('select', $event)"
        />
      </ul>
    </div>
  </section>
</template>

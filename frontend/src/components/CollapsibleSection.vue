<script setup>
import { IconChevronDown } from '@tabler/icons-vue'

defineProps({
  icon: { type: String, required: true },
  label: { type: String, required: true },
  count: { type: Number, required: true },
  modelValue: { type: Boolean, required: true },
  size: { type: String, default: 'group' }, // 'category' | 'group'
})
const emit = defineEmits(['update:modelValue'])

function onToggle(event) {
  emit('update:modelValue', event.target.open)
}
</script>

<template>
  <details :open="modelValue" @toggle="onToggle">
    <summary
      class="flex cursor-pointer items-center justify-between gap-2 py-1.5"
      :class="
        size === 'category'
          ? 'text-sm font-semibold text-stone-700 dark:text-stone-200'
          : 'text-[11px] font-medium uppercase tracking-wide text-stone-400 dark:text-stone-500'
      "
    >
      <span class="flex items-center gap-1.5">
        <span :class="size === 'category' ? 'text-base' : ''" aria-hidden="true">{{ icon }}</span>
        {{ label }}
      </span>
      <span class="flex items-center gap-1 text-stone-400 dark:text-stone-500">
        <span class="text-xs tabular-nums">{{ count }}</span>
        <IconChevronDown :size="14" :stroke-width="2" class="chevron transition-transform duration-150" />
      </span>
    </summary>
    <div class="pb-1 pt-1">
      <slot />
    </div>
  </details>
</template>

<style scoped>
summary {
  list-style: none;
}
summary::-webkit-details-marker {
  display: none;
}
details[open] > summary .chevron {
  transform: rotate(180deg);
}
</style>

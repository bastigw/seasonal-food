<script setup>
defineProps({
  countries: { type: Array, required: true },
  modelValue: { type: String, required: true },
})
defineEmits(['update:modelValue'])
</script>

<template>
  <button
    v-for="country in countries"
    :key="country.code"
    type="button"
    class="flex-1 rounded-t-xl border-b-2 px-2 pb-3 pt-2 text-sm font-medium transition-colors active:scale-[0.98]"
    :class="
      country.code === modelValue
        ? 'border-emerald-600 text-emerald-700 dark:border-emerald-400 dark:text-emerald-400'
        : 'border-transparent text-stone-500 hover:text-stone-700 dark:text-stone-400 dark:hover:text-stone-200'
    "
    :aria-current="country.code === modelValue ? 'true' : undefined"
    @click="$emit('update:modelValue', country.code)"
  >
    <span class="text-base" aria-hidden="true">{{ country.flag }}</span>
    <span class="ml-1">{{ country.code }}</span>
  </button>
</template>

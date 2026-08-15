<script setup>
defineProps({
  label: { type: String, required: true },
})
</script>

<template>
  <p class="py-12 text-center text-sm text-stone-400 dark:text-stone-500">
    {{ label }}
  </p>
</template>

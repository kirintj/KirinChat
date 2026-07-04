<script setup lang="ts">
import { provide } from 'vue'

interface Props {
  model?: Record<string, any>
  rules?: Record<string, any>
}
const props = defineProps<Props>()
provide('h-form', {
  model: props.model,
  rules: props.rules,
})
</script>

<template>
  <form class="h-form" @submit.prevent>
    <slot />
  </form>
</template>

<style scoped>
.h-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}
</style>

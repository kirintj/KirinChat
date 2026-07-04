<script setup lang="ts">
interface Props {
  label?: string
  prop?: string
  error?: string
}
defineProps<Props>()
</script>

<template>
  <div class="h-form-item">
    <label v-if="label" class="h-form-item__label">{{ label }}</label>
    <div class="h-form-item__content">
      <slot />
      <div v-if="error" class="h-form-item__error">{{ error }}</div>
    </div>
  </div>
</template>

<style scoped>
.h-form-item { display: flex; flex-direction: column; gap: 6px; }
.h-form-item__label { font-size: var(--font-size-base); font-weight: 500; color: var(--color-text-primary); }
.h-form-item__error { font-size: var(--font-size-xs); color: var(--color-error); margin-top: 4px; }
</style>

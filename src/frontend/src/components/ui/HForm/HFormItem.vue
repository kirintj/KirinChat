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
.h-form-item__label { font-size: var(--harmony-font-size-body-m); font-weight: 500; color: var(--harmony-font-primary); }
.h-form-item__error { font-size: var(--harmony-font-size-body-s); color: var(--harmony-warning); margin-top: 4px; }
</style>

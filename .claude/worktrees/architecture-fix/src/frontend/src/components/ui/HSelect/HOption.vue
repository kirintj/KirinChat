<script setup lang="ts">
import { inject, computed } from 'vue'

interface Props {
  value: string | number
  label?: string
}
const props = defineProps<Props>()
const select = inject<any>('h-select')
const isSelected = computed(() => select?.modelValue.value === props.value)
</script>

<template>
  <div
    class="h-option"
    :class="{ 'h-option--selected': isSelected }"
    @click="select?.select(props.value)"
  >
    <slot>{{ label || value }}</slot>
  </div>
</template>

<style scoped>
.h-option {
  padding: 8px 12px; font-size: var(--font-size-base);
  color: var(--color-text-primary);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background var(--duration-fast) var(--easing);
}
.h-option:hover { background: var(--color-primary-bg); }
.h-option--selected { background: var(--color-primary-bg); color: var(--color-primary); font-weight: 500; }
</style>

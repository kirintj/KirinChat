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
    <span class="h-option__overlay"></span>
    <slot>{{ label || value }}</slot>
  </div>
</template>

<style scoped>
.h-option {
  position: relative;
  overflow: hidden;
  padding: 8px 12px;
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
  border-radius: 4px;
  cursor: pointer;
}
.h-option__overlay {
  position: absolute; inset: 0;
  pointer-events: none;
  opacity: 0;
  transition: opacity var(--duration-fast) var(--easing);
}
.h-option:hover .h-option__overlay {
  opacity: 1;
  background: var(--color-bg-hover);
}
.h-option:active .h-option__overlay {
  opacity: 1;
  background: var(--color-bg-active);
}
.h-option--selected {
  background: var(--harmony-interactive-select);
  color: var(--color-primary);
  font-weight: 500;
}
</style>

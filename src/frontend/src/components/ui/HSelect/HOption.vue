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
  font-size: var(--harmony-font-size-body-m);
  color: var(--harmony-font-primary);
  border-radius: var(--harmony-corner-radius-level2);
  cursor: pointer;
}
.h-option__overlay {
  position: absolute; inset: 0;
  pointer-events: none;
  opacity: 0;
  transition: opacity var(--harmony-duration-fast) var(--harmony-motion-standard);
}
.h-option:hover .h-option__overlay {
  opacity: 1;
  background: var(--harmony-interactive-hover);
}
.h-option:active .h-option__overlay {
  opacity: 1;
  background: var(--harmony-interactive-pressed);
}
.h-option--selected {
  background: var(--harmony-interactive-select);
  color: var(--harmony-brand);
  font-weight: 500;
}
</style>

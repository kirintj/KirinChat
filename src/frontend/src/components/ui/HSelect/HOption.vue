<script setup lang="ts">
import { inject, computed, onMounted, onUnmounted } from 'vue'

interface Props {
  value: string | number
  label?: string
}
const props = defineProps<Props>()
const select = inject<any>('h-select')
const isSelected = computed(() => select?.modelValue.value === props.value)

const displayLabel = computed(() => props.label || String(props.value))
const isFilteredOut = computed(() => {
  if (!select?.filterText?.value) return false
  const keyword = select.filterText.value.toLowerCase()
  return !displayLabel.value.toLowerCase().includes(keyword)
})

onMounted(() => {
  select?.registerOption?.(props.value, displayLabel.value)
})

onUnmounted(() => {
  select?.unregisterOption?.(props.value)
})
</script>

<template>
  <div
    v-show="!isFilteredOut"
    class="h-option"
    :class="{ 'h-option--selected': isSelected }"
    @click="select?.select(props.value)"
  >
    <span class="h-option__overlay"></span>
    <slot>{{ displayLabel }}</slot>
  </div>
</template>

<style scoped>
.h-option {
  position: relative;
  overflow: hidden;
  padding: 8px 12px;
  font-size: var(--harmony-font-size-body-m);
  color: var(--harmony-font-primary);
  border-radius: var(--harmony-corner-radius-level8);
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

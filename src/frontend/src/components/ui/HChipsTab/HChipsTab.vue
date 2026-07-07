<script setup lang="ts">
interface Props {
  items?: string[]
  modelValue?: string
}

withDefaults(defineProps<Props>(), {
  items: () => [],
  modelValue: '',
})

const emit = defineEmits<{ 'update:modelValue': [value: string] }>()
</script>

<template>
  <div class="h-chips-tab">
    <button
      v-for="item in items"
      :key="item"
      class="h-chips-tab__item"
      :class="{ 'h-chips-tab__item--active': item === modelValue }"
      @click="emit('update:modelValue', item)"
    >
      {{ item }}
    </button>
  </div>
</template>

<style scoped>
.h-chips-tab {
  display: flex;
  gap: var(--harmony-padding-level2);
  flex-wrap: wrap;
}

.h-chips-tab__item {
  padding: var(--harmony-padding-level2) var(--harmony-padding-level4);
  border-radius: var(--harmony-corner-radius-level18);
  border: 1px solid var(--harmony-comp-divider);
  background: transparent;
  color: var(--harmony-font-secondary);
  font-size: var(--harmony-font-size-body-m);
  cursor: pointer;
  transition: all var(--harmony-duration-fast) var(--harmony-motion-standard);
  white-space: nowrap;
}

.h-chips-tab__item:hover {
  background: var(--harmony-interactive-hover);
}

.h-chips-tab__item--active {
  background: var(--harmony-comp-emphasize-tertiary);
  border-color: var(--harmony-brand);
  color: var(--harmony-brand);
}
</style>

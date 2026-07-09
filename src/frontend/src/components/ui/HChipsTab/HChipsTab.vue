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
  padding: var(--harmony-padding-level5) var(--harmony-padding-level6);
  flex-wrap: wrap;
}

.h-chips-tab__item {
  height: 36px;
  padding: var(--harmony-padding-level4) var(--harmony-padding-level8);
  border-radius: var(--harmony-corner-radius-level10);
  border: none;
  background: var(--harmony-comp-background-tertiary);
  color: var(--harmony-font-secondary);
  font-size: var(--harmony-font-size-body-l);
  cursor: pointer;
  transition: all var(--harmony-duration-fast) var(--harmony-motion-standard);
  white-space: nowrap;
  box-sizing: border-box;
}

.h-chips-tab__item:hover {
  background: var(--harmony-comp-background-tertiary);
}

.h-chips-tab__item:active {
  background: var(--harmony-comp-background-secondary);
}

.h-chips-tab__item--active {
  background: var(--harmony-brand);
  color: var(--harmony-font-on-primary);
  backdrop-filter: blur(8px);
  box-shadow: var(--harmony-shadow-lg),
              var(--harmony-shadow-dialog);
}
</style>

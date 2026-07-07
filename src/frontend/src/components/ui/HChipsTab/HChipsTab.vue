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
  border-radius: 20px;
  border: none;
  background: rgba(255, 255, 255, 0.05);
  color: rgba(0, 0, 0, 0.6);
  font-size: var(--harmony-font-size-body-l);
  cursor: pointer;
  transition: all var(--harmony-duration-fast) var(--harmony-motion-standard);
  white-space: nowrap;
  box-sizing: border-box;
}

.h-chips-tab__item:hover {
  background: rgba(0, 0, 0, 0.047);
}

.h-chips-tab__item:active {
  background: rgba(0, 0, 0, 0.098);
}

.h-chips-tab__item--active {
  background: #0091FF;
  color: rgba(255, 255, 255, 1);
  backdrop-filter: blur(8px);
  box-shadow: 0 8px 48px rgba(0, 0, 0, 0.08),
              0 4px 8px rgba(0, 0, 0, 0.25);
}
</style>

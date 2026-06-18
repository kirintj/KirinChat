<script setup lang="ts">
import { ref, provide, computed } from 'vue'
interface Props { modelValue?: string }
const props = defineProps<Props>()
const emit = defineEmits<{ 'update:modelValue': [value: string] }>()
const tabs = ref<{ name: string; label: string }[]>([])
provide('h-tabs', {
  active: computed(() => props.modelValue),
  register: (name: string, label: string) => { if (!tabs.value.find(t => t.name === name)) tabs.value.push({ name, label }) },
})
</script>

<template>
  <div class="h-tabs">
    <div class="h-tabs__header">
      <div v-for="tab in tabs" :key="tab.name" class="h-tabs__item" :class="{ 'h-tabs__item--active': modelValue === tab.name }" @click="emit('update:modelValue', tab.name)">{{ tab.label }}</div>
    </div>
    <div class="h-tabs__content"><slot /></div>
  </div>
</template>

<style scoped>
.h-tabs__header { display: flex; gap: 4px; border-bottom: 1px solid var(--color-border); margin-bottom: 16px; }
.h-tabs__item { padding: 10px 16px; font-size: var(--font-size-base); color: var(--color-text-secondary); cursor: pointer; border-bottom: 2px solid transparent; transition: all var(--duration-fast) var(--easing); }
.h-tabs__item:hover { color: var(--color-text-primary); }
.h-tabs__item--active { color: var(--color-primary); border-bottom-color: var(--color-primary); font-weight: 500; }
</style>

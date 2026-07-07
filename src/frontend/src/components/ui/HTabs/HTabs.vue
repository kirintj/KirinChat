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
      <div v-for="tab in tabs" :key="tab.name" class="h-tabs__item" :class="{ 'h-tabs__item--active': modelValue === tab.name }" @click="emit('update:modelValue', tab.name)" tabindex="0" @keydown.enter.space="emit('update:modelValue', tab.name)">
        <span class="h-tabs__item-overlay"></span>
        {{ tab.label }}
      </div>
    </div>
    <div class="h-tabs__content"><slot /></div>
  </div>
</template>

<style scoped>
.h-tabs__header { display: flex; gap: var(--harmony-padding-level4); border-bottom: 1px solid var(--harmony-comp-divider); margin-bottom: var(--harmony-padding-level8); }
.h-tabs__item {
  position: relative; overflow: hidden;
  padding: var(--harmony-padding-level4) var(--harmony-padding-level8); font-size: var(--harmony-font-size-body-m);
  color: var(--harmony-font-secondary); cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: border-color var(--harmony-duration-fast) var(--harmony-motion-standard), color var(--harmony-duration-fast) var(--harmony-motion-standard);
}
.h-tabs__item:focus-visible { outline: 2px solid var(--harmony-interactive-focus); outline-offset: -2px; border-radius: var(--harmony-corner-radius-level4); }
.h-tabs__item-overlay {
  position: absolute; inset: 0;
  pointer-events: none; opacity: 0;
  transition: opacity var(--harmony-duration-fast) var(--harmony-motion-standard);
}
.h-tabs__item:hover .h-tabs__item-overlay { opacity: 1; background: var(--harmony-interactive-hover); }
.h-tabs__item:hover { color: var(--harmony-font-primary); }
.h-tabs__item--active { color: var(--harmony-brand)); border-bottom-color: var(--harmony-brand)); font-weight: 500; }
</style>

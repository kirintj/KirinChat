<script setup lang="ts">
import { HIcon } from '@/components/ui'

interface ToolbarItem {
  key: string
  icon: string
  label?: string
  disabled?: boolean
}

interface Props {
  items?: ToolbarItem[]
}

withDefaults(defineProps<Props>(), {
  items: () => [],
})

const emit = defineEmits<{ click: [key: string] }>()
</script>

<template>
  <div class="h-toolbar">
    <button
      v-for="item in items"
      :key="item.key"
      class="h-toolbar__item"
      :class="{ 'h-toolbar__item--disabled': item.disabled }"
      :disabled="item.disabled"
      :title="item.label"
      @click="emit('click', item.key)"
    >
      <HIcon :name="item.icon" :size="20" />
      <span v-if="item.label" class="h-toolbar__label">{{ item.label }}</span>
    </button>
  </div>
</template>

<style scoped>
.h-toolbar {
  display: flex;
  align-items: center;
  gap: var(--harmony-padding-level2);
  padding: var(--harmony-padding-level2);
  background: var(--harmony-comp-background-secondary);
  border-radius: var(--harmony-corner-radius-level8);
  backdrop-filter: blur(20px) saturate(1.8);
  -webkit-backdrop-filter: blur(20px) saturate(1.8);
  box-shadow: var(--harmony-shadow-md);
}

.h-toolbar__item {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--harmony-padding-level2);
  padding: var(--harmony-padding-level2);
  border: none;
  background: transparent;
  color: var(--harmony-font-secondary);
  border-radius: var(--harmony-corner-radius-level4);
  cursor: pointer;
  transition: background var(--harmony-duration-fast) var(--harmony-motion-standard),
              color var(--harmony-duration-fast) var(--harmony-motion-standard);
}

.h-toolbar__item:hover {
  background: var(--harmony-interactive-hover);
  color: var(--harmony-font-primary);
}

.h-toolbar__item:active {
  background: var(--harmony-interactive-pressed);
}

.h-toolbar__item--disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.h-toolbar__label {
  font-size: var(--harmony-font-size-body-s);
}
</style>

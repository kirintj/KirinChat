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
      <HIcon :name="item.icon" :size="24" />
      <span v-if="item.label" class="h-toolbar__label">{{ item.label }}</span>
    </button>
  </div>
</template>

<style scoped>
.h-toolbar {
  display: flex;
  align-items: center;
  height: 56px;
  padding: 0 var(--harmony-padding-level6);
  gap: 0;
  background: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(80px) saturate(1.8);
  -webkit-backdrop-filter: blur(80px) saturate(1.8);
  mix-blend-mode: plus-lighter;
  border-radius: 28px;
  box-shadow: 0 4px 48px rgba(0, 0, 0, 0.08),
              0 4px 8px rgba(0, 0, 0, 0.25);
}

.h-toolbar__item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  gap: var(--harmony-padding-level2);
  padding: var(--harmony-padding-level2) 0;
  border: none;
  background: transparent;
  color: var(--harmony-font-secondary);
  border-radius: var(--harmony-corner-radius-level7);
  cursor: pointer;
  transition: background var(--harmony-duration-fast) var(--harmony-motion-standard),
              color var(--harmony-duration-fast) var(--harmony-motion-standard);
}

.h-toolbar__item:hover {
  background: rgba(0, 0, 0, 0.05);
}

.h-toolbar__item:active {
  background: rgba(0, 0, 0, 0.1);
}

.h-toolbar__item--disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.h-toolbar__label {
  font-size: 10px;
  font-weight: 500;
  line-height: 14px;
}
</style>

<script setup lang="ts">
import { HIcon } from '@/components/ui'

interface Props {
  variant?: 'single' | 'icondot' | 'iconsingle' | '2lines' | 'icon2lines' | '3lines'
  clickable?: boolean
}

withDefaults(defineProps<Props>(), {
  variant: 'single',
  clickable: false,
})

const emit = defineEmits<{ click: [event: MouseEvent] }>()
</script>

<template>
  <div
    class="h-list-item"
    :class="[
      `h-list-item--${variant}`,
      { 'h-list-item--clickable': clickable },
    ]"
    @click="clickable && emit('click', $event)"
  >
    <div v-if="$slots.prefix" class="h-list-item__prefix">
      <slot name="prefix" />
    </div>
    <div class="h-list-item__content">
      <div class="h-list-item__title">
        <slot />
      </div>
      <div v-if="$slots.description" class="h-list-item__desc">
        <slot name="description" />
      </div>
    </div>
    <div v-if="$slots.suffix" class="h-list-item__suffix">
      <slot name="suffix" />
    </div>
  </div>
</template>

<style scoped>
.h-list-item {
  display: flex;
  align-items: center;
  padding: 0 var(--harmony-padding-level6);
  gap: var(--harmony-padding-level4);
  box-sizing: border-box;
  width: 328px;
  transition: background var(--harmony-duration-fast) var(--harmony-motion-standard);
}

/* 6种高度变体 */
.h-list-item--single { height: 48px; }
.h-list-item--icondot { height: 56px; }
.h-list-item--iconsingle { height: 64px; }
.h-list-item--2lines { height: 64px; }
.h-list-item--icon2lines { height: 72px; }
.h-list-item--3lines { height: 96px; }

.h-list-item--clickable {
  cursor: pointer;
}

.h-list-item--clickable:hover {
  background: var(--harmony-interactive-hover);
}

.h-list-item--clickable:active {
  background: var(--harmony-interactive-pressed);
}

.h-list-item__prefix {
  flex-shrink: 0;
  display: flex;
  align-items: center;
}

.h-list-item__content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.h-list-item__title {
  font-size: var(--harmony-font-size-body-l);
  font-weight: 500;
  color: var(--harmony-font-primary);
  line-height: 1.4;
}

.h-list-item__desc {
  font-size: var(--harmony-font-size-body-m);
  font-weight: 400;
  color: var(--harmony-font-tertiary);
}

.h-list-item__suffix {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  color: var(--harmony-font-tertiary);
}
</style>

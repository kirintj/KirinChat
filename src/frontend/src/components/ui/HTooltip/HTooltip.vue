<script setup lang="ts">
import { ref } from 'vue'
interface Props {
  content: string
  placement?: 'top' | 'bottom' | 'left' | 'right'
  delay?: number
}
withDefaults(defineProps<Props>(), { placement: 'top', delay: 200 })
const visible = ref(false)
let timer: ReturnType<typeof setTimeout> | null = null
function show() { timer = setTimeout(() => { visible.value = true }, 200) }
function hide() { if (timer) clearTimeout(timer); visible.value = false }
</script>

<template>
  <div class="h-tooltip-wrapper" @mouseenter="show" @mouseleave="hide">
    <slot />
    <Transition name="h-tooltip">
      <div v-if="visible" :class="['h-tooltip', `h-tooltip--${placement}`]">
        <div class="h-tooltip__content">{{ content }}</div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.h-tooltip-wrapper { position: relative; display: inline-flex; }
.h-tooltip {
  position: absolute; padding: 6px 10px;
  background: var(--color-bg-secondary);
  backdrop-filter: blur(16px) saturate(1.2);
  border: 1px solid var(--color-border);
  border-radius: var(--harmony-corner-radius-level8);
  font-size: var(--font-size-xs);
  color: var(--color-text-primary);
  white-space: nowrap; z-index: var(--z-dropdown);
  box-shadow: var(--shadow-md); pointer-events: none;
}
.h-tooltip--top { bottom: calc(100% + 6px); left: 50%; transform: translateX(-50%); }
.h-tooltip--bottom { top: calc(100% + 6px); left: 50%; transform: translateX(-50%); }
.h-tooltip--left { right: calc(100% + 6px); top: 50%; transform: translateY(-50%); }
.h-tooltip--right { left: calc(100% + 6px); top: 50%; transform: translateY(-50%); }
</style>

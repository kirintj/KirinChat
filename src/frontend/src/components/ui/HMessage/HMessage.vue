<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface Props {
  type: 'success' | 'error' | 'warning' | 'info'
  message: string
  duration?: number
  onClose?: () => void
}

const props = withDefaults(defineProps<Props>(), {
  duration: 3000,
})

const visible = ref(false)

onMounted(() => {
  requestAnimationFrame(() => { visible.value = true })
  if (props.duration > 0) {
    setTimeout(() => {
      visible.value = false
      setTimeout(() => props.onClose?.(), 200)
    }, props.duration)
  }
})

function close() {
  visible.value = false
  setTimeout(() => props.onClose?.(), 200)
}

const icons: Record<string, string> = {
  success: '✓',
  error: '✕',
  warning: '!',
  info: 'i',
}
</script>

<template>
  <div
    class="h-message"
    :class="[`h-message--${type}`, { 'h-message--visible': visible }]"
    @click="close"
  >
    <span class="h-message__icon">{{ icons[type] }}</span>
    <span class="h-message__text">{{ message }}</span>
  </div>
</template>

<style scoped>
.h-message {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%) translateY(-20px);
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: var(--harmony-corner-radius-level10);
  background: var(--color-bg-secondary);
  backdrop-filter: blur(20px) saturate(1.2);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-lg);
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
  opacity: 0;
  transition: all var(--duration-normal) var(--easing);
  z-index: var(--z-toast);
  cursor: pointer;
}
.h-message--visible {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}
.h-message__icon {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  color: var(--color-on-primary);
  flex-shrink: 0;
}
.h-message--success .h-message__icon { background: var(--color-success); }
.h-message--error .h-message__icon { background: var(--color-error); }
.h-message--warning .h-message__icon { background: var(--color-warning); color: var(--color-text-primary); }
.h-message--info .h-message__icon { background: var(--color-primary); }
</style>

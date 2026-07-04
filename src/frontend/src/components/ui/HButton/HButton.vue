<!-- src/frontend/src/components/ui/HButton/HButton.vue -->
<script setup lang="ts">
interface Props {
  type?: 'primary' | 'secondary' | 'text' | 'danger'
  size?: 'small' | 'medium' | 'large'
  disabled?: boolean
  loading?: boolean
  block?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  type: 'primary',
  size: 'medium',
  disabled: false,
  loading: false,
  block: false,
})

defineEmits<{
  click: [event: MouseEvent]
}>()
</script>

<template>
  <button
    class="h-button"
    :class="[
      `h-button--${type}`,
      `h-button--${size}`,
      { 'h-button--disabled': disabled, 'h-button--loading': loading, 'h-button--block': block }
    ]"
    :disabled="disabled || loading"
    @click="$emit('click', $event)"
  >
    <span class="h-button__overlay"></span>
    <span class="h-button__focus-ring"></span>
    <span v-if="loading" class="h-button__spinner"></span>
    <slot></slot>
  </button>
</template>

<style scoped>
.h-button {
  position: relative;
  overflow: hidden;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border: none;
  border-radius: var(--radius-md);
  font-family: var(--font-family);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--duration-fast) var(--easing);
  white-space: nowrap;
  user-select: none;
}

/* Overlay layer for hover/pressed states */
.h-button__overlay {
  position: absolute;
  inset: 0;
  pointer-events: none;
  border-radius: inherit;
  opacity: 0;
  transition: opacity var(--duration-fast) var(--easing);
}
.h-button:hover .h-button__overlay {
  opacity: 1;
  background: var(--color-bg-hover);
}
.h-button:active .h-button__overlay {
  background: var(--color-bg-active);
}

/* Focus ring layer */
.h-button__focus-ring {
  position: absolute;
  inset: -4px;
  border-radius: calc(inherit + 4px);
  border: 2px solid var(--color-focus-ring);
  opacity: 0;
  pointer-events: none;
  transition: opacity var(--duration-fast) var(--easing);
}
.h-button:focus-visible .h-button__focus-ring {
  opacity: 1;
}

/* Sizes */
.h-button--small {
  min-width: 72px;
  height: 28px;
  border-radius: 14px;
  padding: 0 12px;
  font-size: var(--font-size-sm);
}
.h-button--medium {
  min-width: 120px;
  height: 40px;
  border-radius: 20px;
  padding: 0 16px;
  font-size: var(--font-size-lg);
}
.h-button--large {
  min-width: 140px;
  height: 44px;
  border-radius: 22px;
  padding: 0 24px;
  font-size: var(--font-size-lg);
}

/* Primary */
.h-button--primary {
  background: var(--color-primary);
  color: var(--color-on-primary);
  backdrop-filter: blur(30px) saturate(1.2);
}

/* Secondary */
.h-button--secondary {
  background: var(--color-primary-bg);
  color: var(--color-primary);
  backdrop-filter: blur(8px);
}

/* Text */
.h-button--text {
  background: transparent;
  color: var(--color-primary);
}

/* Danger */
.h-button--danger {
  background: var(--color-danger);
  color: var(--color-on-primary);
}

/* Disabled */
.h-button--disabled,
.h-button:disabled {
  opacity: 0.4;
  pointer-events: none;
}

/* Loading */
.h-button--loading {
  color: transparent;
}
.h-button--small.h-button--loading {
  min-width: 80px;
}
.h-button--medium.h-button--loading {
  min-width: 128px;
}
.h-button--large.h-button--loading {
  min-width: 148px;
}
.h-button__spinner {
  position: absolute;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: var(--color-on-primary);
  border-radius: 50%;
  animation: h-spin 0.6s linear infinite;
}

/* Block */
.h-button--block {
  width: 100%;
}

@keyframes h-spin {
  to { transform: rotate(360deg); }
}
</style>

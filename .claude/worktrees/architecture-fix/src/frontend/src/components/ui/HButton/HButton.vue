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
    <span v-if="loading" class="h-button__spinner"></span>
    <slot />
  </button>
</template>

<style scoped>
.h-button {
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

/* Sizes */
.h-button--small {
  height: 32px;
  padding: 0 12px;
  font-size: var(--font-size-sm);
}
.h-button--medium {
  height: 36px;
  padding: 0 16px;
  font-size: var(--font-size-base);
}
.h-button--large {
  height: 44px;
  padding: 0 24px;
  font-size: var(--font-size-lg);
}

/* Primary */
.h-button--primary {
  background: var(--color-primary);
  color: #ffffff;
}
.h-button--primary:hover:not(:disabled) {
  background: var(--color-primary-hover);
}
.h-button--primary:active:not(:disabled) {
  background: var(--color-primary-active);
}

/* Secondary */
.h-button--secondary {
  background: var(--color-primary-bg);
  color: var(--color-primary);
}
.h-button--secondary:hover:not(:disabled) {
  background: var(--color-primary);
  color: #ffffff;
}

/* Text */
.h-button--text {
  background: transparent;
  color: var(--color-primary);
}
.h-button--text:hover:not(:disabled) {
  background: var(--color-primary-bg);
}

/* Danger */
.h-button--danger {
  background: var(--color-danger);
  color: #ffffff;
}
.h-button--danger:hover:not(:disabled) {
  opacity: 0.9;
}

/* Disabled */
.h-button--disabled,
.h-button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* Loading */
.h-button--loading {
  position: relative;
  color: transparent;
}
.h-button__spinner {
  position: absolute;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #ffffff;
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

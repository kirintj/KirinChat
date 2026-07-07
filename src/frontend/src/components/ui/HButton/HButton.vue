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
  border-radius: var(--harmony-corner-radius-level6);
  font-family: var(--harmony-font-family);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--harmony-duration-fast) var(--harmony-motion-standard);
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
  transition: opacity var(--harmony-duration-fast) var(--harmony-motion-standard);
}
.h-button:hover .h-button__overlay {
  opacity: 1;
  background: var(--harmony-interactive-hover);
}
.h-button:active .h-button__overlay {
  background: var(--harmony-interactive-pressed);
}

/* Focus ring layer */
.h-button__focus-ring {
  position: absolute;
  inset: -4px;
  border-radius: calc(inherit + 4px);
  border: 2px solid var(--harmony-interactive-focus);
  opacity: 0;
  pointer-events: none;
  transition: opacity var(--harmony-duration-fast) var(--harmony-motion-standard);
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
  font-size: var(--harmony-font-size-subtitle-s);
}
.h-button--medium {
  min-width: 120px;
  height: 40px;
  border-radius: 20px;
  padding: 0 16px;
  font-size: var(--harmony-font-size-body-l);
}
.h-button--large {
  min-width: 140px;
  height: 44px;
  border-radius: 22px;
  padding: 0 24px;
  font-size: var(--harmony-font-size-body-l);
}

/* Primary */
.h-button--primary {
  background: var(--harmony-brand));
  color: var(--harmony-font-on-primary);
  backdrop-filter: blur(30px) saturate(1.2);
}

/* Secondary */
.h-button--secondary {
  background: var(--harmony-comp-emphasize-tertiary);
  color: var(--harmony-brand));
  backdrop-filter: blur(8px);
}

/* Text */
.h-button--text {
  background: transparent;
  color: var(--harmony-brand));
}

/* Danger */
.h-button--danger {
  background: var(--harmony-warning);
  color: var(--harmony-font-on-primary);
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
  border-top-color: var(--harmony-font-on-primary);
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

<script setup lang="ts">
interface Props {
  type?: 'default' | 'primary' | 'success' | 'warning' | 'danger'
  closable?: boolean
}
withDefaults(defineProps<Props>(), { type: 'default', closable: false })
defineEmits<{ close: [] }>()
</script>

<template>
  <span class="h-tag" :class="`h-tag--${type}`">
    <span class="h-tag__overlay"></span>
    <slot />
    <span v-if="closable" class="h-tag__close" @click="$emit('close')">✕</span>
  </span>
</template>

<style scoped>
.h-tag {
  position: relative; overflow: hidden;
  display: inline-flex; align-items: center; gap: var(--spacing-xs);
  padding: var(--spacing-2xs) var(--spacing-sm); border-radius: var(--radius-full);
  font-size: var(--font-size-xs); font-weight: 500; line-height: 20px;
}
.h-tag__overlay {
  position: absolute; inset: 0;
  pointer-events: none; opacity: 0;
  transition: opacity var(--duration-fast) var(--easing);
}
.h-tag:hover .h-tag__overlay { opacity: 1; background: var(--color-bg-hover); }
.h-tag--default { background: var(--color-bg-tertiary); color: var(--color-text-secondary); border: 1px solid var(--color-border); }
.h-tag--primary { background: var(--color-primary-bg); color: var(--color-primary); }
.h-tag--success { background: var(--color-success-bg); color: var(--color-success); }
.h-tag--warning { background: var(--color-warning-bg); color: var(--color-warning); }
.h-tag--danger { background: var(--color-danger-bg); color: var(--color-danger); }
.h-tag__close { cursor: pointer; font-size: 10px; opacity: 0.7; position: relative; z-index: 1; }
.h-tag__close:hover { opacity: 1; }
</style>

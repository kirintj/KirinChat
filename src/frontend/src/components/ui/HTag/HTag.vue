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
  display: inline-flex; align-items: center; gap: var(--harmony-padding-level4);
  padding: var(--harmony-padding-level2) var(--harmony-padding-level6); border-radius: var(--harmony-corner-radius-level18);
  font-size: var(--harmony-font-size-body-s); font-weight: 500; line-height: 20px;
}
.h-tag__overlay {
  position: absolute; inset: 0;
  pointer-events: none; opacity: 0;
  transition: opacity var(--harmony-duration-fast) var(--harmony-motion-standard);
}
.h-tag:hover .h-tag__overlay { opacity: 1; background: var(--harmony-interactive-hover); }
.h-tag--default { background: var(--harmony-comp-background-tertiary); color: var(--harmony-font-secondary); border: 1px solid var(--harmony-comp-divider); }
.h-tag--primary { background: var(--harmony-comp-emphasize-tertiary); color: var(--harmony-brand); }
.h-tag--success { background: var(--harmony-confirm-bg); color: var(--harmony-confirm); }
.h-tag--warning { background: var(--harmony-alert-bg); color: var(--harmony-alert); }
.h-tag--danger { background: var(--harmony-warning-bg); color: var(--harmony-warning); }
.h-tag__close { cursor: pointer; font-size: 10px; opacity: 0.7; position: relative; z-index: 1; }
.h-tag__close:hover { opacity: 1; }
</style>

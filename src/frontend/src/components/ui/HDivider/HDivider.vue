<script setup lang="ts">
interface Props {
  variant?: 'horizontal' | 'inset' | 'block' | 'vertical'
}

withDefaults(defineProps<Props>(), {
  variant: 'horizontal',
})
</script>

<template>
  <div
    class="h-divider"
    :class="`h-divider--${variant}`"
  />
</template>

<style scoped>
.h-divider {
  flex-shrink: 0;
}

/* 线条变体：0.5px */
.h-divider--horizontal,
.h-divider--inset {
  width: 100%;
  height: 0.5px;
  background: rgba(0, 0, 0, 0.2);
}

.h-divider--inset {
  margin-left: var(--harmony-padding-level6);
  width: calc(100% - var(--harmony-padding-level6));
}

.h-divider--vertical {
  width: 0.5px;
  height: 100%;
  background: rgba(0, 0, 0, 0.2);
}

/* block 变体：8px 分隔条 */
.h-divider--block {
  width: 100%;
  height: 8px;
  background: rgba(0, 0, 0, 0.0471);
}

[data-theme="dark"] .h-divider--horizontal,
[data-theme="dark"] .h-divider--inset,
[data-theme="dark"] .h-divider--vertical {
  background: rgba(255, 255, 255, 0.2);
}

[data-theme="dark"] .h-divider--block {
  background: rgba(255, 255, 255, 0.0471);
}
</style>

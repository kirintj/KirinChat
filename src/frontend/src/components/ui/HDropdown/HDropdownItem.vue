<script setup lang="ts">
interface Props { command?: string }
defineProps<Props>()
defineEmits<{ click: [command: string | undefined] }>()
</script>

<template>
  <div class="h-dropdown-item" @click="$emit('click', command)">
    <span class="h-dropdown-item__overlay"></span>
    <slot />
  </div>
</template>

<style scoped>
.h-dropdown-item {
  position: relative; overflow: hidden;
  padding: 10px 16px; font-size: var(--font-size-base);
  color: var(--color-text-primary); cursor: pointer;
}
.h-dropdown-item__overlay {
  position: absolute; inset: 0; pointer-events: none;
  background: transparent;
  transition: background var(--duration-fast) var(--easing);
}
.h-dropdown-item:hover .h-dropdown-item__overlay { background: var(--color-bg-hover); }
.h-dropdown-item:active .h-dropdown-item__overlay { background: var(--color-bg-active); }
</style>

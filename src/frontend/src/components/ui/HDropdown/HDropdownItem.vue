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
  padding: 10px 16px; font-size: var(--harmony-font-size-body-m);
  color: var(--harmony-font-primary); cursor: pointer;
}
.h-dropdown-item__overlay {
  position: absolute; inset: 0; pointer-events: none;
  background: transparent;
  transition: background var(--harmony-duration-fast) var(--harmony-motion-standard);
}
.h-dropdown-item:hover .h-dropdown-item__overlay { background: var(--harmony-interactive-hover); }
.h-dropdown-item:active .h-dropdown-item__overlay { background: var(--harmony-interactive-pressed); }
</style>

<script setup lang="ts">
interface Props { command?: string }
defineProps<Props>()
defineEmits<{ click: [command: string | undefined] }>()
</script>

<template>
  <div class="h-dropdown-item" @click="$emit('click', command)">
    <slot />
  </div>
</template>

<style scoped>
.h-dropdown-item {
  padding: 10px 16px; font-size: var(--font-size-base);
  color: var(--color-text-primary); cursor: pointer;
  transition: background var(--duration-fast) var(--easing);
}
.h-dropdown-item:hover { background: var(--color-bg-tertiary); }
</style>

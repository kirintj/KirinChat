<script setup lang="ts">
interface Props { rows?: number; animated?: boolean }
withDefaults(defineProps<Props>(), { rows: 3, animated: true })
</script>

<template>
  <div class="h-skeleton">
    <div v-for="i in rows" :key="i" class="h-skeleton__line" :class="{ 'h-skeleton--animated': animated }"></div>
  </div>
</template>

<style scoped>
.h-skeleton__line { height: 16px; background: var(--harmony-comp-background-tertiary); border-radius: var(--harmony-corner-radius-level4); margin-bottom: 12px; }
.h-skeleton__line:last-child { width: 60%; }
.h-skeleton--animated { animation: skeleton-pulse 1.5s ease-in-out infinite; }
@keyframes skeleton-pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
</style>

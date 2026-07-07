<script setup lang="ts">
interface Props { src?: string; size?: number | string; shape?: 'circle' | 'square' }
withDefaults(defineProps<Props>(), { size: 40, shape: 'circle' })
</script>

<template>
  <div class="h-avatar" :class="`h-avatar--${shape}`" :style="{ width: typeof size === 'number' ? `${size}px` : size, height: typeof size === 'number' ? `${size}px` : size }">
    <img v-if="src" :src="src" class="h-avatar__img" />
    <slot v-else />
  </div>
</template>

<style scoped>
.h-avatar { display: inline-flex; align-items: center; justify-content: center; background: var(--harmony-comp-emphasize-tertiary); color: var(--harmony-brand); overflow: hidden; flex-shrink: 0; }
.h-avatar--circle { border-radius: 50%; }
.h-avatar--square { border-radius: var(--harmony-corner-radius-level8); }
.h-avatar__img { width: 100%; height: 100%; object-fit: cover; }
</style>

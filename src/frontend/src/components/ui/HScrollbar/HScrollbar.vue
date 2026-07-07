<script setup lang="ts">
interface Props { maxHeight?: string }
withDefaults(defineProps<Props>(), { maxHeight: '100%' })
</script>

<template>
  <div class="h-scrollbar" :style="{ maxHeight }">
    <div class="h-scrollbar__view"><slot /></div>
  </div>
</template>

<style scoped>
.h-scrollbar { overflow: auto; }
.h-scrollbar::-webkit-scrollbar { width: 6px; height: 6px; }
.h-scrollbar::-webkit-scrollbar-track { background: transparent; }
.h-scrollbar::-webkit-scrollbar-thumb { background: var(--harmony-comp-divider); border-radius: 3px; }
.h-scrollbar::-webkit-scrollbar-thumb:hover { background: var(--harmony-font-fourth); }
</style>

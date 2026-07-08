<script setup lang="ts">
import { provide } from 'vue'
import { useBreakpoint } from '@/composables/useBreakpoint'

const { isMobile } = useBreakpoint()

provide('isMobile', isMobile)
</script>

<template>
  <div class="h-app-shell" :class="{ 'h-app-shell--mobile': isMobile }">
    <slot :is-mobile="isMobile" />
  </div>
</template>

<style scoped>
.h-app-shell {
  width: 100%;
  min-height: 100vh;
  min-height: 100dvh;
  display: flex;
  overflow-x: hidden;
  overflow-y: auto;
  background: var(--harmony-comp-background-primary);
}

.h-app-shell--mobile {
  flex-direction: column;
  align-items: center;
}
</style>

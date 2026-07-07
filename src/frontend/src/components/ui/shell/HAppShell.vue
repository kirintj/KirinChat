<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const BREAKPOINT = 768
const isMobile = ref(window.innerWidth < BREAKPOINT)

const onResize = () => {
  isMobile.value = window.innerWidth < BREAKPOINT
}

onMounted(() => window.addEventListener('resize', onResize))
onUnmounted(() => window.removeEventListener('resize', onResize))
</script>

<template>
  <div class="h-app-shell" :class="{ 'h-app-shell--mobile': isMobile }">
    <slot :is-mobile="isMobile" />
  </div>
</template>

<style scoped>
.h-app-shell {
  width: 100vw;
  height: 100vh;
  display: flex;
  overflow: hidden;
  background: var(--harmony-comp-background-primary);
}

.h-app-shell--mobile {
  flex-direction: column;
  align-items: center;
}
</style>

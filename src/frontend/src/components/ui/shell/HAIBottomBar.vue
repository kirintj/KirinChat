<script setup lang="ts">
interface Props {
  theme?: 'light' | 'dark' | 'transparent'
}

withDefaults(defineProps<Props>(), {
  theme: 'light',
})
</script>

<template>
  <div class="harmony-aibottombar" :class="`harmony-aibottombar--${theme}`">
    <div class="harmony-aibottombar__indicator" />
  </div>
</template>

<style scoped>
.harmony-aibottombar {
  width: 100%;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.harmony-aibottombar__indicator {
  width: 112px;
  height: 5px;
  border-radius: 2.5px;
  flex: 0 0 auto;
}

.harmony-aibottombar--light .harmony-aibottombar__indicator {
  background: rgba(0, 0, 0, 0.2);
}

.harmony-aibottombar--dark .harmony-aibottombar__indicator {
  background: rgba(255, 255, 255, 0.5);
}

.harmony-aibottombar--transparent .harmony-aibottombar__indicator {
  background: rgba(255, 255, 255, 0.7);
}
</style>

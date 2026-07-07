<script setup lang="ts">
interface Props {
  split?: boolean
}

withDefaults(defineProps<Props>(), {
  split: false,
})
</script>

<template>
  <hr v-if="split" class="h-divider h-divider--split" />
  <div v-else class="h-divider" />
</template>

<style scoped>
.h-divider {
  height: 1px;
  background: var(--harmony-comp-divider);
  border: none;
  margin: 0;
  flex-shrink: 0;
}

.h-divider--split {
  height: 8px;
  background: var(--harmony-comp-background-tertiary);
  border: none;
  margin: 0;
}
</style>

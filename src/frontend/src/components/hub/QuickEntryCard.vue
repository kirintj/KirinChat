<script setup lang="ts">
import { HCardView } from '@/components/ui'

defineProps<{
  icon: string
  title: string
  description: string
}>()

const emit = defineEmits<{ click: [] }>()
</script>

<template>
  <HCardView size="medium" clickable @click="emit('click')">
    <div class="quick-entry-content">
      <div class="card-icon"><Icon :icon="icon" :width="28" :height="28" /></div>
      <div class="card-title">{{ title }}</div>
      <div class="card-desc">{{ description }}</div>
    </div>
  </HCardView>
</template>

<style lang="scss" scoped>
.quick-entry-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--harmony-padding-level4);
  text-align: center;
}

.card-icon {
  font-size: var(--harmony-font-size-title-l);
  line-height: 1;
}

.card-title {
  font-size: var(--harmony-font-size-subtitle-m);
  font-weight: 600;
  color: var(--harmony-font-primary);
}

.card-desc {
  font-size: var(--harmony-font-size-body-s);
  color: var(--harmony-font-secondary);
  line-height: 1.4;
}
</style>

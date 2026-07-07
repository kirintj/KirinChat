<script setup lang="ts">
import { HCardView } from '@/components/ui'

defineProps<{
  skillName: string
  progress: { current: number; total: number }
}>()

const emit = defineEmits<{ click: [] }>()

const progressPercent = (current: number, total: number) => {
  if (total === 0) return 0
  return Math.round((current / total) * 100)
}
</script>

<template>
  <HCardView size="medium" clickable @click="emit('click')">
    <template #header>
      <div class="card-header">
        <span class="skill-name">{{ skillName }}</span>
        <span class="status-badge">进行中</span>
      </div>
    </template>
    <div class="progress-section">
      <div class="progress-bar">
        <div
          class="progress-fill"
          :style="{ width: progressPercent(progress.current, progress.total) + '%' }"
        />
      </div>
      <span class="progress-text">{{ progress.current }}/{{ progress.total }} 题</span>
    </div>
  </HCardView>
</template>

<style lang="scss" scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.skill-name {
  font-size: var(--harmony-font-size-body-m);
  font-weight: 600;
  color: var(--harmony-font-primary);
}

.status-badge {
  font-size: var(--harmony-font-size-caption-l);
  padding: var(--harmony-padding-level1) var(--harmony-padding-level4);
  border-radius: var(--harmony-corner-radius-level5);
  background: var(--harmony-comp-emphasize-tertiary);
  color: var(--harmony-brand);
}

.progress-section {
  display: flex;
  align-items: center;
  gap: var(--harmony-padding-level5);
}

.progress-bar {
  flex: 1;
  height: var(--harmony-padding-level3);
  border-radius: var(--harmony-corner-radius-level2);
  background: var(--harmony-comp-background-tertiary);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: var(--harmony-corner-radius-level2);
  background: var(--harmony-brand);
  transition: width var(--harmony-duration-normal) var(--harmony-motion-standard);
}

.progress-text {
  font-size: var(--harmony-font-size-body-s);
  color: var(--harmony-font-secondary);
  white-space: nowrap;
}
</style>

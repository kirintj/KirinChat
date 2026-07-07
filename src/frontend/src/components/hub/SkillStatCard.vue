<script setup lang="ts">
import { HList } from '@/components/ui'

defineProps<{
  skillName: string
  count: number
  avgScore: number
}>()

const barColor = (score: number) => {
  if (score >= 80) return 'var(--harmony-confirm)'
  if (score >= 60) return 'var(--harmony-alert)'
  return 'var(--harmony-warning)'
}
</script>

<template>
  <HList variant="2lines">
    <span>{{ skillName }}</span>
    <template #description>
      <div class="stat-bar-section">
        <div class="stat-bar">
          <div
            class="stat-bar-fill"
            :style="{ width: avgScore + '%', background: barColor(avgScore) }"
          />
        </div>
        <span class="stat-score" :style="{ color: barColor(avgScore) }">{{ avgScore }}分</span>
      </div>
    </template>
    <template #suffix>
      <span class="stat-count">{{ count }} 次</span>
    </template>
  </HList>
</template>

<style lang="scss" scoped>
.stat-bar-section {
  display: flex;
  align-items: center;
  gap: var(--harmony-padding-level5);
}

.stat-bar {
  flex: 1;
  height: var(--harmony-padding-level3);
  border-radius: var(--harmony-corner-radius-level2);
  background: var(--harmony-comp-background-tertiary);
  overflow: hidden;
}

.stat-bar-fill {
  height: 100%;
  border-radius: var(--harmony-corner-radius-level2);
  transition: width var(--harmony-duration-normal) var(--harmony-motion-standard);
}

.stat-score {
  font-size: var(--harmony-font-size-subtitle-s);
  font-weight: 600;
  white-space: nowrap;
}

.stat-count {
  font-size: var(--harmony-font-size-body-s);
  color: var(--harmony-font-tertiary);
  white-space: nowrap;
}
</style>

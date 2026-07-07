<script setup lang="ts">
import { HList } from '@/components/ui'

defineProps<{
  skillName: string
  score: number
  timeLabel: string
}>()

const emit = defineEmits<{ click: [] }>()

const scoreColor = (score: number) => {
  if (score >= 80) return 'var(--harmony-confirm)'
  if (score >= 60) return 'var(--harmony-alert)'
  return 'var(--harmony-warning)'
}
</script>

<template>
  <HList variant="2lines" clickable @click="emit('click')">
    <span>{{ skillName }}</span>
    <template #description>
      <span>{{ timeLabel }}</span>
    </template>
    <template #suffix>
      <span class="item-score" :style="{ color: scoreColor(score) }">
        {{ score }}分
      </span>
    </template>
  </HList>
</template>

<style lang="scss" scoped>
.item-score {
  font-size: var(--harmony-font-size-body-l);
  font-weight: 700;
}
</style>

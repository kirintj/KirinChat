<script setup lang="ts">
import { HIcon } from '@/components/ui'

interface Props {
  icon?: string
  text?: string
  description?: string
}

withDefaults(defineProps<Props>(), {
  icon: 'search',
  text: '暂无数据',
  description: '',
})
</script>

<template>
  <div class="h-empty">
    <HIcon :name="icon" :size="48" class="h-empty__icon" />
    <p class="h-empty__text">{{ text }}</p>
    <p v-if="description" class="h-empty__desc">{{ description }}</p>
    <div class="h-empty__action">
      <slot name="action" />
    </div>
  </div>
</template>

<style scoped>
.h-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--harmony-padding-level16) var(--harmony-padding-level8);
  color: var(--harmony-font-tertiary);
}

.h-empty__icon {
  color: var(--harmony-font-fourth);
  margin-bottom: var(--harmony-padding-level4);
}

.h-empty__text {
  font-size: var(--harmony-font-size-body-m);
  color: var(--harmony-font-tertiary);
  margin: 0;
}

.h-empty__desc {
  font-size: var(--harmony-font-size-body-s);
  color: var(--harmony-font-fourth);
  margin-top: var(--harmony-padding-level2);
}

.h-empty__action {
  margin-top: var(--harmony-padding-level8);
}
</style>

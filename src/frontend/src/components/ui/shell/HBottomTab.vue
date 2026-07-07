<script setup lang="ts">
import { computed } from 'vue'
import { HIcon } from '@/components/ui'

interface TabItem {
  key: string
  label: string
  icon: string
  badge?: number | string
}

interface Props {
  variant?: '2' | '3' | '4' | '5'
  items?: TabItem[]
  activeKey?: string
}

const props = withDefaults(defineProps<Props>(), {
  variant: '4',
  items: () => [],
  activeKey: '',
})

const emit = defineEmits<{ 'update:activeKey': [key: string] }>()

const barWidth = computed(() => {
  const widths: Record<string, number> = { '2': 160, '3': 236, '4': 328, '5': 328 }
  return widths[props.variant] || 328
})
</script>

<template>
  <div class="harmony-bottomtab">
    <div class="harmony-bottomtab__bar" :style="{ width: barWidth + 'px' }">
      <div class="harmony-bottomtab__tabs">
        <div
          v-for="item in items"
          :key="item.key"
          class="harmony-bottomtab__tab"
          :class="{ 'harmony-bottomtab__tab--active': item.key === activeKey }"
          @click="emit('update:activeKey', item.key)"
        >
          <div class="harmony-bottomtab__icon-wrap">
            <HIcon :svg="item.icon" :size="24" />
            <span v-if="item.badge" class="harmony-bottomtab__badge">{{ item.badge }}</span>
          </div>
          <span class="harmony-bottomtab__label">{{ item.label }}</span>
        </div>
      </div>
    </div>
    <div class="harmony-bottomtab__indicator" />
  </div>
</template>

<style scoped>
.harmony-bottomtab {
  width: 100%;
  height: 100px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
  flex-shrink: 0;
  position: relative;
  z-index: 100;
  padding-bottom: 8px;
}

.harmony-bottomtab__bar {
  height: 56px;
  border-radius: 100px;
  padding: 4px 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(80px) blur(8px) saturate(1.8);
  -webkit-backdrop-filter: blur(80px) blur(8px) saturate(1.8);
  background: rgba(255, 255, 255, 0.15);
  box-shadow: 0 4px 48px rgba(0, 0, 0, 0.08),
              0 4px 8px rgba(0, 0, 0, 0.25);
  mix-blend-mode: plus-lighter;
}

.harmony-bottomtab__tabs {
  display: flex;
  align-items: center;
  justify-content: space-around;
  width: 100%;
  height: 100%;
}

.harmony-bottomtab__tab {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  cursor: pointer;
  min-width: 48px;
  height: 48px;
  border-radius: var(--harmony-corner-radius-level8);
  transition: background var(--harmony-duration-fast) var(--harmony-motion-standard);
}

.harmony-bottomtab__tab:hover {
  background: var(--harmony-interactive-hover);
}

.harmony-bottomtab__icon-wrap {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  color: var(--harmony-font-secondary);
}

.harmony-bottomtab__tab--active .harmony-bottomtab__icon-wrap {
  color: var(--harmony-brand);
}

.harmony-bottomtab__badge {
  position: absolute;
  top: -4px;
  right: -8px;
  min-width: 16px;
  height: 16px;
  padding: 0 4px;
  font-size: var(--harmony-font-size-caption-m);
  line-height: 16px;
  text-align: center;
  color: #fff;
  background: var(--harmony-warning);
  border-radius: var(--harmony-corner-radius-level4);
}

.harmony-bottomtab__label {
  font-size: var(--harmony-font-size-caption-m);
  font-weight: 500;
  color: var(--harmony-font-secondary);
  line-height: 14px;
}

.harmony-bottomtab__tab--active .harmony-bottomtab__label {
  color: var(--harmony-brand);
}

.harmony-bottomtab__indicator {
  width: 112px;
  height: 5px;
  border-radius: 2.5px;
  background: rgba(0, 0, 0, 0.2);
  margin-top: 6px;
  flex-shrink: 0;
}

/* 暗色模式 */
[data-theme="dark"] .harmony-bottomtab__bar {
  background: rgba(0, 0, 0, 0.15);
}

[data-theme="dark"] .harmony-bottomtab__indicator {
  background: rgba(255, 255, 255, 0.5);
}
</style>

<script setup lang="ts">
interface Props {
  variant?: 'big' | 'normal' | 'secondary' | 'drawer'
  title?: string
  subtitle?: string
  showBack?: boolean
  scrolled?: boolean
}

defineProps<Props>()
const emit = defineEmits<{ back: [] }>()
</script>

<template>
  <div
    class="harmony-titlebar"
    :class="[`harmony-titlebar--${variant || 'normal'}`, { 'is-scrolled': scrolled }]"
  >
    <div class="harmony-titlebar__content">
      <!-- 返回按钮 -->
      <div v-if="showBack" class="harmony-titlebar__leading" @click="emit('back')">
        <Icon icon="mdi:arrow-left" :width="20" :height="20" />
      </div>

      <!-- big 变体：大标题 -->
      <template v-if="variant === 'big'">
        <div class="harmony-titlebar__titles">
          <h1 class="harmony-titlebar__title">{{ title }}</h1>
          <p v-if="subtitle" class="harmony-titlebar__subtitle">{{ subtitle }}</p>
        </div>
      </template>

      <!-- normal/secondary/drawer 变体：左对齐标题 -->
      <template v-else>
        <div class="harmony-titlebar__center">
          <span class="harmony-titlebar__title">{{ title }}</span>
        </div>
      </template>

      <!-- 操作按钮插槽 -->
      <div class="harmony-titlebar__actions">
        <slot name="actions" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.harmony-titlebar {
  position: sticky;
  top: 0;
  width: 100%;
  height: 56px;
  flex-shrink: 0;
  z-index: var(--z-dropdown);
  background: transparent;
}

.harmony-titlebar__content {
  position: relative;
  z-index: var(--z-dropdown);
  height: 100%;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  box-sizing: border-box;
}

.harmony-titlebar__titles {
  display: flex;
  flex-direction: column;
  gap: var(--harmony-padding-level1);
  min-width: 0;
}

.harmony-titlebar__title {
  font-size: var(--harmony-font-size-body-l);
  font-weight: 700;
  color: var(--harmony-font-primary);
  margin: 0;
  line-height: 1.3;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.harmony-titlebar__subtitle {
  font-size: var(--harmony-font-size-body-s);
  color: var(--harmony-font-secondary);
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.harmony-titlebar__center {
  flex: 1;
  display: flex;
  align-items: center;
  min-width: 0;
}

.harmony-titlebar__leading {
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  flex-shrink: 0;
  border-radius: var(--harmony-corner-radius-level8);
  transition: background var(--harmony-duration-fast) var(--harmony-motion-standard);
}

.harmony-titlebar__leading:hover {
  background: var(--harmony-interactive-hover);
}

.harmony-titlebar__actions {
  display: flex;
  align-items: center;
  gap: var(--harmony-padding-level3);
  flex-shrink: 0;
}
</style>

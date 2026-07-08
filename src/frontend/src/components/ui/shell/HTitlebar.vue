<script setup lang="ts">
interface Props {
  variant?: 'big' | 'normal' | 'secondary' | 'drawer'
  title?: string
  subtitle?: string
  showBack?: boolean
}

defineProps<Props>()
const emit = defineEmits<{ back: [] }>()
</script>

<template>
  <div class="harmony-titlebar" :class="`harmony-titlebar--${variant || 'normal'}`">
    <!-- 渐隐背板 -->
    <div class="harmony-titlebar__backdrop" />

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

      <!-- normal/secondary 变体：居中标题 -->
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
  position: relative;
  width: 100%;
  overflow: hidden;
  flex-shrink: 0;
  z-index: 10;
}

.harmony-titlebar__backdrop {
  position: absolute;
  inset: 0;
  background: var(--harmony-comp-background-secondary);
  backdrop-filter: blur(12px) saturate(1.2);
  -webkit-backdrop-filter: blur(12px) saturate(1.2);
}

.harmony-titlebar__content {
  position: relative;
  z-index: 1;
}

/* big 变体 */
.harmony-titlebar--big {
  height: 205px;
}

.harmony-titlebar--big .harmony-titlebar__content {
  padding: 56px 24px 20px;
}

.harmony-titlebar__titles {
  display: flex;
  flex-direction: column;
  gap: var(--harmony-padding-level2);
}

.harmony-titlebar__title {
  font-size: var(--harmony-font-size-title-l);
  font-weight: 700;
  color: var(--harmony-font-primary);
  margin: 0;
  line-height: 1.3;
}

.harmony-titlebar__subtitle {
  font-size: var(--harmony-font-size-body-m);
  color: var(--harmony-font-secondary);
  margin: 0;
}

/* normal 变体 */
.harmony-titlebar--normal {
  height: 124px;
}

.harmony-titlebar--normal .harmony-titlebar__content {
  height: 100%;
  display: flex;
  align-items: flex-end;
  padding: 0 24px 16px;
}

.harmony-titlebar__leading {
  cursor: pointer;
  display: flex;
  align-items: center;
  padding: var(--harmony-padding-level2);
  border-radius: var(--harmony-corner-radius-level8);
  transition: background var(--harmony-duration-fast) var(--harmony-motion-standard);
}

.harmony-titlebar__leading:hover {
  background: var(--harmony-interactive-hover);
}

.harmony-titlebar__center {
  flex: 1;
  display: flex;
  align-items: center;
}

.harmony-titlebar--normal .harmony-titlebar__title {
  font-size: var(--harmony-font-size-title-m);
  font-weight: 700;
}

.harmony-titlebar__actions {
  display: flex;
  align-items: center;
  gap: var(--harmony-padding-level4);
}

/* secondary 变体 */
.harmony-titlebar--secondary {
  height: 124px;
}

.harmony-titlebar--secondary .harmony-titlebar__content {
  height: 100%;
  display: flex;
  align-items: flex-end;
  padding: 0 24px 16px;
  gap: var(--harmony-padding-level4);
}

/* drawer 变体 */
.harmony-titlebar--drawer {
  height: 124px;
}

.harmony-titlebar--drawer .harmony-titlebar__content {
  height: 100%;
  display: flex;
  align-items: flex-end;
  padding: 0 24px 16px;
  gap: var(--harmony-padding-level4);
}
</style>

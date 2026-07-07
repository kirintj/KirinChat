<script setup lang="ts">
/**
 * QuickEntryCard 组件
 *
 * 用于展示快捷入口卡片，支持图标、标题和描述。
 * 点击时触发 'click' 事件，由父组件处理路由跳转。
 *
 * @param icon - 展示用的 emoji 或图标字符
 * @param title - 入口名称，如"文字面试"
 * @param description - 简短的功能描述
 *
 * 用于 Interview Hub 页面的快捷入口网格布局。
 */
defineProps<{
  icon: string       // 展示用的 emoji 或图标字符
  title: string      // 入口名称，如"文字面试"
  description: string // 简短的功能描述
}>()

const emit = defineEmits<{
  click: []  // 点击事件，由父组件处理路由跳转
}>()
</script>

<template>
  <div class="quick-entry-card" @click="emit('click')">
    <div class="card-icon">{{ icon }}</div>
    <div class="card-title">{{ title }}</div>
    <div class="card-desc">{{ description }}</div>
  </div>
</template>

<style lang="scss" scoped>
/**
 * 快捷入口卡片样式
 *
 * 设计要点：
 * - 垂直布局，图标在上，标题和描述在下
 * - 使用 CSS 变量支持主题切换
 * - hover 时的上浮效果增强可点击感
 * - 过渡动画提供平滑的交互体验
 */
.quick-entry-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 24px 16px;
  border-radius: 12px;
  border: 1px solid var(--border-color, #e5e7eb);
  background: var(--bg-primary, #ffffff);
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;

  // hover 上浮效果，增强可点击感
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    border-color: var(--primary-color, #6366f1);
  }
}

.card-icon {
  font-size: 32px;
  line-height: 1;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--harmony-font-primary);
}

.card-desc {
  font-size: 12px;
  color: var(--harmony-font-secondary);
  line-height: 1.4;
}
</style>

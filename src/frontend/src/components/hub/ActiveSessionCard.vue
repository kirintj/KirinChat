<script setup lang="ts">
// 进行中的面试卡片：展示技能名称和答题进度，点击继续面试
defineProps<{
  skillName: string                    // 技能方向的中文名称
  progress: { current: number; total: number }  // 已答/总题数
}>()

const emit = defineEmits<{
  click: []  // 点击跳转到对应面试的聊天页
}>()

// 计算进度百分比，用于进度条宽度
const progressPercent = (current: number, total: number) => {
  if (total === 0) return 0
  return Math.round((current / total) * 100)
}
</script>

<template>
  <div class="active-session-card" @click="emit('click')">
    <div class="card-header">
      <span class="skill-name">{{ skillName }}</span>
      <span class="status-badge">进行中</span>
    </div>
    <div class="progress-section">
      <!-- 进度条：通过内联样式动态设置填充宽度 -->
      <div class="progress-bar">
        <div
          class="progress-fill"
          :style="{ width: progressPercent(progress.current, progress.total) + '%' }"
        />
      </div>
      <span class="progress-text">{{ progress.current }}/{{ progress.total }} 题</span>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.active-session-card {
  padding: 16px;
  border-radius: 10px;
  border: 1px solid var(--border-color, #e5e7eb);
  background: var(--bg-primary, #ffffff);
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 200px;  // 保证卡片在水平滚动中有最小宽度

  &:hover {
    border-color: var(--primary-color, #6366f1);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.skill-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--harmony-font-primary);
}

.status-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 10px;
  background: var(--primary-light, #eef2ff);
  color: var(--primary-color, #6366f1);
}

.progress-section {
  display: flex;
  align-items: center;
  gap: 10px;
}

.progress-bar {
  flex: 1;
  height: 6px;
  border-radius: 3px;
  background: var(--bg-secondary, #f3f4f6);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 3px;
  background: var(--primary-color, #6366f1);
  transition: width 0.3s ease;  // 平滑过渡，避免进度突变
}

.progress-text {
  font-size: 12px;
  color: var(--harmony-font-secondary);
  white-space: nowrap;  // 防止"X/Y 题"文字换行
}
</style>

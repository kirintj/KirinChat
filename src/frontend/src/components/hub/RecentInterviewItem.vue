<script setup lang="ts">
// RecentInterviewItem 组件：最近面试列表项
// 展示技能名称、得分和完成时间，用于"最近面试"部分
// 点击可跳转到对应的评估报告页

// 定义组件接收的 props
defineProps<{
  skillName: string  // 技能方向中文名（如"前端开发"）
  score: number      // 面试得分（0-100 制）
  timeLabel: string  // 显示的时间标签，如"已完成"或"3小时前"
}>()

// 定义组件可触发的事件
const emit = defineEmits<{
  click: []  // 点击事件，用于跳转到评估报告
}>()

// 根据分数返回对应颜色：绿色(>=80)、黄色(>=60)、红色(<60)
// 与 reportPage 的颜色逻辑保持一致，提供直观的表现水平指示
const scoreColor = (score: number) => {
  if (score >= 80) return '#22c55e'  // 优秀 - 绿色
  if (score >= 60) return '#f59e0b'  // 良好 - 黄色
  return '#ef4444'                    // 待改进 - 红色
}
</script>

<template>
  <!-- 列表项容器，点击时触发 click 事件 -->
  <div class="recent-item" @click="emit('click')">
    <!-- 左侧信息：技能名称和时间 -->
    <div class="item-left">
      <span class="item-skill">{{ skillName }}</span>
      <span class="item-time">{{ timeLabel }}</span>
    </div>
    <!-- 右侧分数，使用动态颜色直观反映表现水平 -->
    <div class="item-score" :style="{ color: scoreColor(score) }">
      {{ score }}分
    </div>
  </div>
</template>

<style lang="scss" scoped>
.recent-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid var(--border-light, var(--harmony-comp-background-tertiary));
  cursor: pointer;
  transition: background 0.15s ease;

  &:hover {
    background: var(--bg-hover, var(--harmony-comp-background-tertiary));
  }

  &:last-child {
    border-bottom: none;  // 最后一项不需要底部分割线
  }
}

.item-left {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.item-skill {
  font-size: 14px;
  font-weight: 500;
  color: var(--harmony-font-primary);
}

.item-time {
  font-size: 12px;
  color: var(--harmony-font-tertiary);
}

.item-score {
  font-size: 16px;
  font-weight: 700;
}
</style>

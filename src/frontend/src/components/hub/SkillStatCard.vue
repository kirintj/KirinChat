<script setup lang="ts">
// 技能统计卡片：展示某技能方向的面试次数和平均分进度条
// 用于 Hub 页面底部的"技能统计"区块，按面试次数排序
// 设计决策：使用进度条直观展示平均分，颜色编码提供快速反馈
defineProps<{
  skillName: string  // 技能方向中文名（如"前端开发"）
  count: number      // 该技能的面试总次数
  avgScore: number   // 平均分（0-100 制）
}>()

// 根据平均分返回进度条颜色，与 RecentInterviewItem 颜色逻辑一致
// 颜色编码：绿色(>=80)优秀、黄色(>=60)及格、红色(<60)需提升
// 这种一致性帮助用户快速识别表现水平
const barColor = (score: number) => {
  if (score >= 80) return '#22c55e'   // 绿色：优秀
  if (score >= 60) return '#f59e0b'   // 黄色：及格
  return '#ef4444'                     // 红色：需提升
}
</script>

<template>
  <div class="skill-stat-card">
    <div class="stat-header">
      <span class="stat-name">{{ skillName }}</span>
      <span class="stat-count">{{ count }} 次面试</span>
    </div>
    <div class="stat-bar-section">
      <!-- 平均分进度条：宽度直接用分数百分比，颜色根据分值变化 -->
      <div class="stat-bar">
        <div
          class="stat-bar-fill"
          :style="{ width: avgScore + '%', background: barColor(avgScore) }"
        />
      </div>
      <span class="stat-score" :style="{ color: barColor(avgScore) }">{{ avgScore }}分</span>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.skill-stat-card {
  padding: 12px 0;
  border-bottom: 1px solid var(--border-light, #f3f4f6);

  &:last-child {
    border-bottom: none;
  }
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.stat-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--harmony-font-primary);
}

.stat-count {
  font-size: 12px;
  color: var(--harmony-font-tertiary);
}

.stat-bar-section {
  display: flex;
  align-items: center;
  gap: 10px;
}

.stat-bar {
  flex: 1;
  height: 6px;
  border-radius: 3px;
  background: var(--bg-secondary, #f3f4f6);
  overflow: hidden;
}

.stat-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
}

.stat-score {
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
}
</style>
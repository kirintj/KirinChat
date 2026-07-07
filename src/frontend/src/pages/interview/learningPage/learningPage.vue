<template>
  <div class="learning-page">
    <!-- Header -->
    <div class="learning-header">
      <button class="back-btn" @click="goBack">← 返回</button>
      <h2>学习路径 - {{ path?.skill_name || '' }}</h2>
    </div>

    <div v-if="loading" class="loading-state">加载中...</div>

    <div v-else-if="!path" class="empty-state">
      <p>暂无学习数据，完成面试后即可查看学习路径。</p>
      <button class="primary-btn" @click="goToInterview">去面试</button>
    </div>

    <template v-else>
      <!-- Overview -->
      <div class="section overview-section">
        <h3>📊 学习概览</h3>
        <div class="overview-stats">
          <div class="stat-item">
            <span class="stat-value">{{ path.total_sessions }}</span>
            <span class="stat-label">面试次数</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ path.overall_avg_score }}</span>
            <span class="stat-label">平均分</span>
          </div>
          <div class="stat-item">
            <span class="stat-value level-badge" :class="path.overall_level">{{ path.overall_level_label }}</span>
            <span class="stat-label">整体水平</span>
          </div>
        </div>
      </div>

      <!-- Weak categories -->
      <div v-if="path.weak_categories.length" class="section">
        <h3>🎯 各分类得分</h3>
        <div class="category-grid">
          <div
            v-for="cat in path.weak_categories"
            :key="cat.category"
            class="category-card"
            :class="{ weak: cat.avg_score < 6, medium: cat.avg_score >= 6 && cat.avg_score < 8, strong: cat.avg_score >= 8 }"
          >
            <div class="cat-label">{{ cat.label }}</div>
            <div class="cat-score">{{ cat.avg_score }}</div>
            <div class="cat-count">{{ cat.session_count }} 次面试</div>
          </div>
        </div>
      </div>

      <!-- Recommended resources -->
      <div v-if="Object.keys(path.resources).length" class="section">
        <h3>📖 推荐学习资料</h3>
        <p class="section-desc">按薄弱程度排序，优先学习得分最低的分类</p>
        <div v-for="catKey in path.study_order" :key="catKey" class="resource-block">
          <div
            class="resource-header"
            @click="toggleResource(catKey)"
          >
            <span class="resource-title">{{ path.resources[catKey]?.label || catKey }}</span>
            <span class="resource-score">平均 {{ path.resources[catKey]?.label ? getCategoryScore(catKey) : '-' }} 分</span>
            <span class="expand-icon">{{ expandedResources.has(catKey) ? '▼' : '▶' }}</span>
          </div>
          <div v-if="expandedResources.has(catKey)" class="resource-content">
            <pre>{{ path.resources[catKey]?.reference }}</pre>
          </div>
        </div>
      </div>

      <div v-if="!Object.keys(path.resources).length && path.weak_categories.length" class="section">
        <p class="no-resources">暂无推荐学习资料，请先在 Skill 中配置参考资料。</p>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getLearningPathAPI } from '../../../apis/interview'
import type { LearningPath } from '../../../apis/interview'

const router = useRouter()
const route = useRoute()

const loading = ref(true)
const path = ref<LearningPath | null>(null)
const expandedResources = ref(new Set<string>())

const fetchPath = async () => {
  const skillId = route.query.skillId as string
  if (!skillId) {
    loading.value = false
    return
  }

  try {
    const res = await getLearningPathAPI(skillId)
    if (res.data.status_code === 200 && res.data.data) {
      path.value = res.data.data
    }
  } catch {
    // ignore
  } finally {
    loading.value = false
  }
}

const toggleResource = (catKey: string) => {
  if (expandedResources.value.has(catKey)) {
    expandedResources.value.delete(catKey)
  } else {
    expandedResources.value.add(catKey)
  }
}

const getCategoryScore = (catKey: string): number => {
  const cat = path.value?.weak_categories.find(c => c.category === catKey)
  return cat?.avg_score ?? 0
}

const goBack = () => {
  router.push('/interview')
}

const goToInterview = () => {
  router.push('/interview')
}

onMounted(fetchPath)
</script>

<style scoped>
.learning-page {
  padding: 24px;
  max-width: 900px;
  margin: 0 auto;
  height: 100%;
  overflow-y: auto;
}

.learning-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.back-btn {
  background: none;
  border: 1px solid var(--harmony-brand);
  color: var(--harmony-brand);
  padding: 6px 16px;
  border-radius: var(--harmony-corner-radius-level4);
  cursor: pointer;
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 48px;
  color: var(--harmony-font-tertiary);
}

.primary-btn {
  background: var(--harmony-brand);
  color: var(--harmony-comp-background-primary);
  border: none;
  padding: 8px 24px;
  border-radius: var(--harmony-corner-radius-level4);
  cursor: pointer;
  margin-top: 16px;
}

.section {
  background: var(--harmony-comp-background-secondary);
  border-radius: var(--harmony-corner-radius-level8);
  padding: 20px;
  margin-bottom: 16px;
}

.section h3 {
  margin: 0 0 16px;
}

.section-desc {
  color: var(--harmony-font-tertiary);
  font-size: var(--harmony-font-size-body-m);
  margin: -8px 0 16px;
}

.overview-stats {
  display: flex;
  gap: 24px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.stat-value {
  font-size: var(--harmony-font-size-title-m);
  font-weight: 700;
}

.stat-label {
  font-size: var(--harmony-font-size-subtitle-s);
  color: var(--harmony-font-tertiary);
}

.level-badge {
  font-size: var(--harmony-font-size-body-l);
  padding: 4px 12px;
  border-radius: var(--harmony-corner-radius-level10);
  color: var(--harmony-comp-background-primary);
}

.level-badge.excellent { background: var(--harmony-confirm); }
.level-badge.intermediate { background: var(--harmony-brand); }
.level-badge.beginner { background: var(--harmony-alert); }
.level-badge.needs_work { background: var(--harmony-warning); }

.category-grid {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.category-card {
  flex: 1;
  min-width: 100px;
  padding: 16px;
  border-radius: var(--harmony-corner-radius-level6);
  text-align: center;
  border: 2px solid transparent;
}

.category-card.weak { border-color: var(--harmony-warning); background: var(--harmony-warning-bg); }
.category-card.medium { border-color: var(--harmony-alert); background: var(--harmony-alert-bg); }
.category-card.strong { border-color: var(--harmony-confirm); background: var(--harmony-confirm-bg); }

.cat-label {
  font-size: var(--harmony-font-size-body-m);
  font-weight: 600;
}

.cat-score {
  font-size: var(--harmony-font-size-title-l);
  font-weight: 700;
  margin: 8px 0;
}

.cat-count {
  font-size: var(--harmony-font-size-body-s);
  color: var(--harmony-font-tertiary);
}

.resource-block {
  border: 1px solid var(--harmony-comp-divider);
  border-radius: var(--harmony-corner-radius-level4);
  margin-bottom: 8px;
  overflow: hidden;
}

.resource-header {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  cursor: pointer;
  transition: background 0.2s;
}

.resource-header:hover {
  background: var(--harmony-comp-background-secondary);
}

.resource-title {
  font-weight: 600;
  flex: 1;
}

.resource-score {
  color: var(--harmony-font-tertiary);
  font-size: var(--harmony-font-size-body-m);
  margin-right: 12px;
}

.expand-icon {
  font-size: var(--harmony-font-size-body-s);
  color: var(--harmony-font-tertiary);
}

.resource-content {
  padding: 0 16px 16px;
  border-top: 1px solid var(--harmony-comp-divider);
}

.resource-content pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: var(--harmony-font-family);
  font-size: var(--harmony-font-size-body-m);
  line-height: 1.6;
  color: var(--harmony-font-primary);
  margin: 0;
}

.no-resources {
  color: var(--harmony-font-tertiary);
  text-align: center;
}
</style>

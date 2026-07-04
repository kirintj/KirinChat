<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { HButton, HMessage } from '@/components/ui'
import { useInterviewStore } from '../../../store/interview'
import { getEvaluationReportAPI, getEvaluationBySessionAPI } from '../../../apis/interview'
import type { EvaluationReport } from '../../../apis/interview'

const router = useRouter()
const interviewStore = useInterviewStore()
const report = ref<EvaluationReport | null>(null)
const loading = ref(false)

const scoreColor = computed(() => {
  if (!report.value) return '#999'
  const s = report.value.total_score
  if (s >= 80) return '#4caf50'
  if (s >= 60) return '#ff9800'
  return '#f44336'
})

const scoreLabel = computed(() => {
  if (!report.value) return ''
  const s = report.value.total_score
  if (s >= 90) return '优秀'
  if (s >= 80) return '良好'
  if (s >= 60) return '及格'
  return '需努力'
})

const categoryEntries = computed(() => {
  if (!report.value?.category_scores) return []
  return Object.entries(report.value.category_scores)
})

const fetchReport = async () => {
  loading.value = true
  try {
    const evalId = interviewStore.evaluationId || (router.currentRoute.value.query.evaluationId as string)
    const sessionId = router.currentRoute.value.query.sessionId as string

    if (evalId) {
      // Fetch by evaluation ID
      const res = await getEvaluationReportAPI(evalId)
      if (res.data.status_code === 200 && res.data.data) {
        report.value = res.data.data
      } else {
        HMessage.error('获取评估报告失败')
      }
    } else if (sessionId) {
      // Fetch by session ID (from history list)
      const res = await getEvaluationBySessionAPI(sessionId)
      if (res.data.status_code === 200 && res.data.data) {
        report.value = res.data.data
      } else {
        HMessage.error('该面试尚未生成评估报告')
        router.replace('/interview')
      }
    } else {
      HMessage.error('未找到评估报告')
      router.replace('/interview')
    }
  } catch {
    HMessage.error('获取评估报告失败')
  } finally {
    loading.value = false
  }
}

const startNewInterview = () => {
  interviewStore.reset()
  router.push('/interview')
}

const goBack = () => {
  router.push('/interview')
}

onMounted(() => {
  fetchReport()
})
</script>

<template>
  <div class="report-page">
    <div v-if="loading" class="loading-state">正在加载评估报告...</div>

    <div v-else-if="!report" class="empty-state">
      <div class="empty-icon">📭</div>
      <div class="empty-text">未找到评估报告</div>
      <HButton type="primary" @click="goBack">返回列表</HButton>
    </div>

    <div v-else class="report-content">
      <!-- Header -->
      <div class="report-header">
        <button class="back-btn" @click="goBack">← 返回列表</button>
        <h2 class="report-title">面试评估报告</h2>
      </div>

      <!-- Score section -->
      <div class="score-section">
        <div class="score-circle" :style="{ borderColor: scoreColor }">
          <div class="score-number" :style="{ color: scoreColor }">
            {{ report.total_score }}
          </div>
          <div class="score-max">/100</div>
        </div>
        <div class="score-meta">
          <div class="score-label" :style="{ color: scoreColor }">{{ scoreLabel }}</div>
          <div class="score-skill">{{ interviewStore.skillName || '综合面试' }}</div>
        </div>
      </div>

      <!-- Category scores -->
      <div v-if="categoryEntries.length > 0" class="section">
        <h3 class="section-title">分类得分</h3>
        <div class="category-list">
          <div v-for="[key, score] in categoryEntries" :key="key" class="category-item">
            <div class="category-header">
              <span class="category-name">{{ key }}</span>
              <span class="category-score">{{ score }}/100</span>
            </div>
            <div class="category-bar">
              <div
                class="category-fill"
                :style="{
                  width: score + '%',
                  background: score >= 80 ? '#4caf50' : score >= 60 ? '#ff9800' : '#f44336'
                }"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Summary -->
      <div v-if="report.summary" class="section">
        <h3 class="section-title">总结</h3>
        <div class="summary-text">{{ report.summary }}</div>
      </div>

      <!-- Strengths -->
      <div v-if="report.strengths?.length" class="section">
        <h3 class="section-title">💪 优势</h3>
        <div class="tag-list">
          <span v-for="(s, i) in report.strengths" :key="i" class="tag tag-strength">
            {{ s }}
          </span>
        </div>
      </div>

      <!-- Improvements -->
      <div v-if="report.improvements?.length" class="section">
        <h3 class="section-title">📈 改进方向</h3>
        <div class="tag-list">
          <span v-for="(s, i) in report.improvements" :key="i" class="tag tag-improve">
            {{ s }}
          </span>
        </div>
      </div>

      <!-- Actions -->
      <div class="report-actions">
        <HButton type="primary" size="large" @click="startNewInterview">
          重新面试
        </HButton>
        <HButton
          v-if="interviewStore.skillId"
          type="secondary"
          size="large"
          @click="router.push({ path: '/interview/learning', query: { skillId: interviewStore.skillId } })"
        >
          查看学习路径
        </HButton>
        <HButton type="secondary" size="large" @click="goBack">
          返回列表
        </HButton>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.report-page {
  height: 100%;
  overflow-y: auto;
  padding: 32px 40px;
}

.loading-state {
  text-align: center;
  padding: 80px 0;
  color: var(--color-text-secondary);
}

.empty-state {
  text-align: center;
  padding: 80px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;

  .empty-icon {
    font-size: 48px;
    opacity: 0.4;
  }

  .empty-text {
    color: var(--color-text-tertiary);
  }
}

.report-content {
  max-width: 720px;
}

.report-header {
  margin-bottom: 32px;

  .back-btn {
    background: none;
    border: none;
    color: var(--color-primary);
    cursor: pointer;
    font-size: 14px;
    font-family: inherit;
    padding: 0;
    margin-bottom: 16px;

    &:hover {
      text-decoration: underline;
    }
  }

  .report-title {
    font-size: 24px;
    font-weight: 600;
    color: var(--color-text-primary);
    margin: 0;
  }
}

// Score
.score-section {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 32px;
  background: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
  margin-bottom: 32px;

  .score-circle {
    width: 100px;
    height: 100px;
    border: 4px solid;
    border-radius: 50%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;

    .score-number {
      font-size: 36px;
      font-weight: 700;
      line-height: 1;
    }

    .score-max {
      font-size: 12px;
      color: var(--color-text-tertiary);
    }
  }

  .score-meta {
    .score-label {
      font-size: 20px;
      font-weight: 600;
      margin-bottom: 4px;
    }

    .score-skill {
      font-size: 14px;
      color: var(--color-text-secondary);
    }
  }
}

// Sections
.section {
  margin-bottom: 28px;

  .section-title {
    font-size: 16px;
    font-weight: 600;
    color: var(--color-text-primary);
    margin: 0 0 16px;
  }
}

// Category bars
.category-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.category-item {
  .category-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 4px;

    .category-name {
      font-size: 13px;
      font-weight: 500;
      color: var(--color-text-primary);
    }

    .category-score {
      font-size: 13px;
      color: var(--color-text-secondary);
    }
  }

  .category-bar {
    height: 8px;
    background: var(--color-bg-secondary);
    border-radius: 4px;
    overflow: hidden;

    .category-fill {
      height: 100%;
      border-radius: 4px;
      transition: width 0.6s ease;
    }
  }
}

// Summary
.summary-text {
  font-size: 14px;
  line-height: 1.8;
  color: var(--color-text-secondary);
  background: var(--color-bg-secondary);
  padding: 16px 20px;
  border-radius: var(--radius-md);
  white-space: pre-wrap;
}

// Tags
.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;

  &.tag-strength {
    background: #e8f5e9;
    color: #2e7d32;
  }

  &.tag-improve {
    background: #fff3e0;
    color: #e65100;
  }
}

// Actions
.report-actions {
  display: flex;
  gap: 12px;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid var(--color-border);
}
</style>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { HButton, HMessage } from '@/components/ui'
import { useInterviewStore } from '../../../store/interview'
import { getEvaluationReportAPI, getEvaluationBySessionAPI } from '../../../apis/interview'
import type { EvaluationReport } from '../../../apis/interview'
import * as echarts from 'echarts'

const router = useRouter()
const interviewStore = useInterviewStore()
const report = ref<EvaluationReport | null>(null)
const loading = ref(false)
const downloadLoading = ref(false)

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

// --- 雷达图 ---
const radarChartRef = ref<HTMLElement | null>(null)
let radarChart: echarts.ECharts | null = null

// 是否有足够分类展示雷达图（至少 2 个分类才有意义）
const hasEnoughCategories = computed(() => categoryEntries.value.length >= 2)

// 初始化雷达图
const initRadarChart = () => {
  if (!radarChartRef.value || !report.value?.category_scores) return
  if (!hasEnoughCategories.value) return
  const scores = report.value.category_scores
  const indicator = Object.keys(scores).map(name => ({ name, max: 100 }))
  const values = Object.values(scores)

  radarChart = echarts.init(radarChartRef.value)
  radarChart.setOption({
    radar: {
      indicator,
      shape: 'polygon',
      splitNumber: 5,
      axisName: {
        color: '#6b7280',
        fontSize: 12,
      },
      splitLine: { lineStyle: { color: '#e5e7eb' } },
      splitArea: { show: false },
    },
    series: [{
      type: 'radar',
      data: [{
        value: values,
        areaStyle: { opacity: 0.15 },
        lineStyle: { width: 2 },
      }],
    }],
  })
}

// 窗口 resize 时重绘图表
const handleResize = () => { radarChart?.resize() }

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
        nextTick(initRadarChart)
      } else {
        HMessage.error('获取评估报告失败')
      }
    } else if (sessionId) {
      // Fetch by session ID (from history list)
      const res = await getEvaluationBySessionAPI(sessionId)
      if (res.data.status_code === 200 && res.data.data) {
        report.value = res.data.data
        nextTick(initRadarChart)
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

const downloadPDF = async () => {
  if (!report.value || downloadLoading.value) return
  downloadLoading.value = true
  try {
    const token = localStorage.getItem('token') || ''
    const url = `/api/v1/interview/evaluation/${report.value.id}/pdf`
    const res = await fetch(url, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!res.ok) {
      HMessage.error(`PDF 下载失败 (${res.status})`)
      return
    }
    const blob = await res.blob()
    const blobUrl = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = blobUrl
    a.download = `evaluation_${report.value.id}.pdf`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(blobUrl)
  } catch {
    HMessage.error('PDF 下载失败')
  } finally {
    downloadLoading.value = false
  }
}

const goToQuestionDetail = (questionId: string) => {
  router.push({ path: `/interview/question/${questionId}` })
}

onMounted(() => {
  fetchReport()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  radarChart?.dispose()
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

      <!-- 雷达图 -->
      <div v-if="hasEnoughCategories" class="section">
        <h3 class="section-title">能力雷达图</h3>
        <div ref="radarChartRef" class="radar-chart"></div>
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

      <!-- Question Details List -->
      <div v-if="report.question_details?.length" class="section">
        <h3 class="section-title">题目详情</h3>
        <div class="question-list">
          <div
            v-for="(q, index) in report.question_details"
            :key="q.question_id"
            class="question-item"
            @click="goToQuestionDetail(q.question_id)"
          >
            <div class="question-left">
              <span class="question-index">Q{{ index + 1 }}</span>
              <span class="question-text">{{ q.content }}</span>
            </div>
            <div class="question-right">
              <span
                class="question-score-badge"
                :class="{
                  'score-high': q.score >= 8,
                  'score-mid': q.score >= 6 && q.score < 8,
                  'score-low': q.score < 6,
                }"
              >
                {{ q.score }}/10
              </span>
              <span class="question-arrow">→</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="report-actions">
        <HButton type="secondary" size="large" :loading="downloadLoading" @click="downloadPDF">
          下载 PDF
        </HButton>
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
  color: var(--harmony-font-secondary);
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
    color: var(--harmony-font-tertiary);
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
    color: var(--harmony-brand);
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
    color: var(--harmony-font-primary);
    margin: 0;
  }
}

// Score
.score-section {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 32px;
  background: var(--harmony-comp-background-secondary);
  border-radius: var(--harmony-corner-radius-level8);
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
      color: var(--harmony-font-tertiary);
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
      color: var(--harmony-font-secondary);
    }
  }
}

// Sections
.section {
  margin-bottom: 28px;

  .section-title {
    font-size: 16px;
    font-weight: 600;
    color: var(--harmony-font-primary);
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
      color: var(--harmony-font-primary);
    }

    .category-score {
      font-size: 13px;
      color: var(--harmony-font-secondary);
    }
  }

  .category-bar {
    height: 8px;
    background: var(--harmony-comp-background-secondary);
    border-radius: 4px;
    overflow: hidden;

    .category-fill {
      height: 100%;
      border-radius: 4px;
      transition: width 0.6s ease;
    }
  }
}

// 雷达图
.radar-chart {
  width: 100%;
  height: 300px;
}

// Summary
.summary-text {
  font-size: 14px;
  line-height: 1.8;
  color: var(--harmony-font-secondary);
  background: var(--harmony-comp-background-secondary);
  padding: 16px 20px;
  border-radius: var(--harmony-corner-radius-level6);
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
    background: var(--harmony-confirm-bg);
    color: var(--harmony-confirm);
  }

  &.tag-improve {
    background: var(--harmony-alert-bg);
    color: var(--harmony-alert);
  }
}

// Question list
.question-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.question-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: var(--harmony-comp-background-secondary);
  border-radius: var(--harmony-corner-radius-level6);
  cursor: pointer;
  transition: background var(--harmony-duration-fast) var(--harmony-motion-standard);

  &:hover {
    background: var(--harmony-comp-emphasize-tertiary);
  }

  .question-left {
    display: flex;
    align-items: center;
    gap: 12px;
    flex: 1;
    min-width: 0;

    .question-index {
      font-size: 12px;
      font-weight: 600;
      color: var(--harmony-brand);
      flex-shrink: 0;
    }

    .question-text {
      font-size: 14px;
      color: var(--harmony-font-primary);
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
  }

  .question-right {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-shrink: 0;

    .question-score-badge {
      font-size: 12px;
      font-weight: 600;
      padding: 2px 8px;
      border-radius: 10px;

      &.score-high {
        background: var(--harmony-confirm-bg);
        color: var(--harmony-confirm);
      }

      &.score-mid {
        background: var(--harmony-alert-bg);
        color: var(--harmony-alert);
      }

      &.score-low {
        background: rgba(244, 67, 54, 0.1);
        color: #f44336;
      }
    }

    .question-arrow {
      font-size: 14px;
      color: var(--harmony-font-tertiary);
    }
  }
}

// Actions
.report-actions {
  display: flex;
  gap: 12px;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid var(--harmony-comp-divider);
}
</style>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { HButton, HMessage } from '@/components/ui'
import { getQuestionDetailAPI } from '../../../apis/interview'
import type { QuestionDetailData } from '../../../apis/interview'
import { marked } from 'marked'

const router = useRouter()
const detail = ref<QuestionDetailData | null>(null)
const loading = ref(false)

// 得分颜色
const scoreColor = computed(() => {
  if (!detail.value) return '#999'
  const s = detail.value.score
  if (s >= 8) return '#4caf50'
  if (s >= 6) return '#ff9800'
  return '#f44336'
})

// 渲染 Markdown
const renderMarkdown = (text: string) => {
  if (!text) return ''
  return marked.parse(text) as string
}

// 返回报告页
const goBack = () => {
  router.back()
}

onMounted(async () => {
  const questionId = router.currentRoute.value.params.questionId as string
  if (!questionId) {
    HMessage.error('题目ID不存在')
    router.replace('/interview')
    return
  }

  loading.value = true
  try {
    const res = await getQuestionDetailAPI(questionId)
    if (res.data.status_code === 200 && res.data.data) {
      detail.value = res.data.data
    } else {
      HMessage.error('获取题目详情失败')
    }
  } catch {
    HMessage.error('获取题目详情失败')
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="question-detail-page">
    <div v-if="loading" class="loading-state">正在加载题目详情...</div>

    <div v-else-if="!detail" class="empty-state">
      <div class="empty-icon">📭</div>
      <div class="empty-text">未找到题目详情</div>
      <HButton type="primary" @click="goBack">返回报告</HButton>
    </div>

    <div v-else class="detail-content">
      <!-- Header -->
      <div class="detail-header">
        <button class="back-btn" @click="goBack">← 返回报告</button>
        <h2 class="detail-title">题目详情</h2>
        <div v-if="detail.skill_name" class="detail-skill">{{ detail.skill_name }}</div>
      </div>

      <!-- Question content -->
      <div class="section">
        <h3 class="section-label">题目</h3>
        <div class="section-body question-text">{{ detail.content }}</div>
      </div>

      <!-- User answer -->
      <div class="section">
        <h3 class="section-label">我的答案</h3>
        <div class="section-body user-answer">
          {{ detail.user_answer || '未作答' }}
        </div>
      </div>

      <!-- Score and feedback -->
      <div class="section score-section">
        <div class="score-header">
          <h3 class="section-label">AI 评分</h3>
          <div class="score-badge" :style="{ background: scoreColor }">
            {{ detail.score }}/10
          </div>
        </div>
        <div class="section-body feedback-text" v-html="renderMarkdown(detail.feedback)"></div>
      </div>

      <!-- Reference answer -->
      <div v-if="detail.reference_answer" class="section">
        <h3 class="section-label">参考答案</h3>
        <div class="section-body reference-text" v-html="renderMarkdown(detail.reference_answer)"></div>
      </div>

      <!-- Back button -->
      <div class="detail-actions">
        <HButton type="primary" size="large" @click="goBack">返回报告</HButton>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.question-detail-page {
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

.detail-content {
  max-width: 720px;
}

.detail-header {
  margin-bottom: 32px;

  .back-btn {
    background: none;
    border: none;
    color: var(--harmony-brand));
    cursor: pointer;
    font-size: 14px;
    font-family: inherit;
    padding: 0;
    margin-bottom: 16px;

    &:hover {
      text-decoration: underline;
    }
  }

  .detail-title {
    font-size: 24px;
    font-weight: 600;
    color: var(--harmony-font-primary);
    margin: 0 0 8px;
  }

  .detail-skill {
    font-size: 14px;
    color: var(--harmony-font-secondary);
  }
}

.section {
  margin-bottom: 24px;

  .section-label {
    font-size: 14px;
    font-weight: 600;
    color: var(--harmony-font-secondary);
    margin: 0 0 8px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .section-body {
    font-size: 15px;
    line-height: 1.8;
    color: var(--harmony-font-primary);
    background: var(--harmony-comp-background-secondary);
    padding: 16px 20px;
    border-radius: var(--harmony-corner-radius-level6);
    white-space: pre-wrap;
  }
}

.score-section {
  .score-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
  }

  .score-badge {
    font-size: 14px;
    font-weight: 700;
    color: white;
    padding: 4px 12px;
    border-radius: 16px;
  }

  .feedback-text {
    :deep(p) {
      margin: 0 0 8px;
      &:last-child { margin-bottom: 0; }
    }
  }
}

.reference-text {
  border-left: 3px solid var(--harmony-brand));
  :deep(p) {
    margin: 0 0 8px;
    &:last-child { margin-bottom: 0; }
  }
}

.detail-actions {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid var(--harmony-comp-divider);
}
</style>

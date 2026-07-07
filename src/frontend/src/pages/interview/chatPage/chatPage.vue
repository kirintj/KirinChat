<script setup lang="ts">
import { ref, nextTick, onMounted, onUnmounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { HButton, HMessage } from '@/components/ui'
import { useInterviewStore } from '../../../store/interview'
import { getSessionDetailAPI } from '../../../apis/interview'
import { marked } from 'marked'

const router = useRouter()
const interviewStore = useInterviewStore()
const answerInput = ref('')

// --- 草稿自动保存：localStorage 按 sessionId + questionId 存取 ---
const DRAFT_PREFIX = 'interview_draft_'

// 生成草稿 key：interview_draft_{sessionId}_{questionId}
const getDraftKey = () => {
  const qId = interviewStore.currentQuestion?.id
  if (!interviewStore.sessionId || !qId) return null
  return `${DRAFT_PREFIX}${interviewStore.sessionId}_${qId}`
}

// 保存草稿到 localStorage（空内容时删除 key）
const saveDraft = () => {
  const key = getDraftKey()
  if (!key) return
  const value = answerInput.value.trim()
  if (value) {
    localStorage.setItem(key, value)
  } else {
    localStorage.removeItem(key)
  }
}

// 从 localStorage 恢复草稿
const restoreDraft = () => {
  const key = getDraftKey()
  if (!key) return
  const saved = localStorage.getItem(key)
  if (saved) {
    answerInput.value = saved
  }
}

// 清除当前题目的草稿
const clearDraft = () => {
  const key = getDraftKey()
  if (key) {
    localStorage.removeItem(key)
  }
}

// debounce 工具：延迟执行，重复调用时重置计时器
let draftTimer: ReturnType<typeof setTimeout> | null = null
const debounceSaveDraft = () => {
  if (draftTimer) clearTimeout(draftTimer)
  draftTimer = setTimeout(saveDraft, 500)
}

// 监听输入变化，debounce 500ms 自动保存草稿
watch(answerInput, debounceSaveDraft)

// 监听当前题目变化，恢复新题目的草稿（提交答案后 currentQuestion 会更新）
watch(() => interviewStore.currentQuestion, () => {
  questionSeconds.value = 0 // 新题目重置题目计时
  nextTick(restoreDraft)
})

// 自动完成场景：最后一个问题回答后，store 自动触发评估，完成后跳转报告页
watch(() => interviewStore.evaluationId, (newId) => {
  if (newId && interviewStore.isCompleted) {
    router.replace({ path: '/interview/report', query: { evaluationId: newId } })
  }
})

// --- 答题计时器：当前题目耗时 + 总面试时长 ---
const questionSeconds = ref(0)
const totalSeconds = ref(0)
let timerInterval: ReturnType<typeof setInterval> | null = null

// 格式化秒数为 mm:ss
const formatTime = (seconds: number) => {
  const m = String(Math.floor(seconds / 60)).padStart(2, '0')
  const s = String(seconds % 60).padStart(2, '0')
  return `${m}:${s}`
}

// 启动计时器，每秒递增
const startTimer = () => {
  if (timerInterval) return
  timerInterval = setInterval(() => {
    questionSeconds.value += 1
    totalSeconds.value += 1
  }, 1000)
}

// 停止计时器
const stopTimer = () => {
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
}

const messagesContainer = ref<HTMLElement | null>(null)

const isTyping = computed(() => interviewStore.loading)
const canSubmit = computed(() =>
  !!answerInput.value.trim() && !interviewStore.loading && interviewStore.isActive
)

const renderMarkdown = (text: string) => {
  if (!text) return ''
  return marked.parse(text) as string
}

const scrollBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const submitAnswer = async () => {
  const answer = answerInput.value.trim()
  if (!answer || !canSubmit.value) return

  answerInput.value = ''
  clearDraft() // 提交成功后清除草稿
  const success = await interviewStore.submitAnswerStream(answer)
  scrollBottom()

  if (!success) {
    HMessage.error('提交答案失败，请重试')
  }
}

const handleKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    submitAnswer()
  }
}

const endInterview = async () => {
  const evalId = await interviewStore.endInterview()
  if (evalId) {
    router.push({ path: '/interview/report', query: { evaluationId: evalId } })
  } else {
    HMessage.error('评估报告生成超时，可在历史记录中查看')
    router.push('/interview')
  }
}

const goBack = () => {
  router.push('/interview')
}

onMounted(async () => {
  // 如果没有活跃面试，尝试从 URL sessionId 恢复
  if (!interviewStore.isActive && !interviewStore.isCompleted) {
    const sessionId = router.currentRoute.value.query.sessionId as string
    if (sessionId) {
      try {
        const res = await getSessionDetailAPI(sessionId)
        if (res.data.status_code === 200 && res.data.data) {
          const { session, questions } = res.data.data

          // 已完成的面试跳转到报告页
          if (session.status === 'COMPLETED') {
            router.replace({ path: '/interview/report', query: { sessionId } })
            return
          }

          // 从后端数据重建面试状态（服务端恢复）
          interviewStore.sessionId = session.id
          interviewStore.skillId = session.skill_id
          interviewStore.difficulty = session.difficulty || 'MEDIUM'
          interviewStore.questionCount = session.progress.total
          interviewStore.status = 'IN_PROGRESS'

          // 重建对话历史：遍历题目，已回答的生成 interviewer+candidate 消息对
          const restoredMessages: { role: 'interviewer' | 'candidate'; content: string }[] = []
          let restoredQuestion = null
          for (const q of questions) {
            restoredMessages.push({ role: 'interviewer', content: q.content })
            if (q.user_answer) {
              restoredMessages.push({ role: 'candidate', content: q.user_answer })
            } else if (!restoredQuestion) {
              restoredQuestion = q // 第一个未回答的题目作为当前题
            }
          }
          interviewStore.messages = restoredMessages
          interviewStore.currentQuestion = restoredQuestion
          interviewStore.progress = session.progress

          // 根据 session 创建时间恢复总计时
          if (session.create_time) {
            const created = new Date(session.create_time)
            const now = new Date()
            totalSeconds.value = Math.floor((now.getTime() - created.getTime()) / 1000)
          }
        }
      } catch { /* ignore */ }
    }
    // 恢复失败，回到选择页
    if (!interviewStore.isActive) {
      router.replace('/interview')
      return
    }
  }

  restoreDraft() // 页面加载时恢复草稿
  scrollBottom()
  startTimer() // 启动答题计时器
})

onUnmounted(() => {
  stopTimer()
})
</script>

<template>
  <div class="chat-page">
    <!-- Progress bar -->
    <div class="progress-bar-container">
      <div class="progress-info">
        <span class="progress-label">
          第 {{ interviewStore.progress.current + (interviewStore.isActive ? 1 : 0) }} / {{ interviewStore.progress.total }} 题
        </span>
        <span class="progress-skill">
          {{ interviewStore.skillName }}
          <span class="timer-display">⏱ {{ formatTime(questionSeconds) }} | 总 {{ formatTime(totalSeconds) }}</span>
        </span>
      </div>
      <div class="progress-track">
        <div
          class="progress-fill"
          :style="{ width: interviewStore.progressPercent + '%' }"
        ></div>
      </div>
    </div>

    <!-- Messages -->
    <div ref="messagesContainer" class="messages-container">
      <div
        v-for="(msg, index) in interviewStore.messages"
        :key="index"
        class="message-group"
      >
        <!-- Interviewer (AI) message -->
        <div v-if="msg.role === 'interviewer'" class="message-row ai">
          <div class="avatar ai-avatar">🤖</div>
          <div class="bubble ai-bubble markdown-body" v-html="renderMarkdown(msg.content)"></div>
        </div>

        <!-- Candidate (user) message -->
        <div v-else class="message-row user">
          <div class="bubble user-bubble">{{ msg.content }}</div>
        </div>
      </div>

      <!-- Typing indicator -->
      <div v-if="isTyping && interviewStore.isActive" class="message-row ai">
        <div class="avatar ai-avatar">🤖</div>
        <div class="bubble ai-bubble typing-indicator">
          <span class="dot"></span>
          <span class="dot"></span>
          <span class="dot"></span>
        </div>
      </div>
    </div>

    <!-- Input area -->
    <div v-if="interviewStore.isActive" class="input-area">
      <textarea
        v-model="answerInput"
        class="answer-input"
        placeholder="输入你的回答，按 Enter 发送..."
        rows="3"
        @keydown="handleKeydown"
      ></textarea>
      <div class="input-actions">
        <HButton
          type="text"
          size="small"
          class="end-btn"
          :loading="isTyping"
          :disabled="isTyping"
          @click="endInterview"
        >
          {{ isTyping ? '生成评估中...' : '结束面试' }}
        </HButton>
        <HButton
          type="primary"
          size="medium"
          :disabled="!canSubmit"
          :loading="isTyping"
          @click="submitAnswer"
        >
          发送
        </HButton>
      </div>
    </div>

    <!-- Completed state -->
    <div v-else-if="interviewStore.isCompleted" class="completed-bar">
      <span>面试已结束</span>
      <HButton type="primary" size="small" @click="goBack">返回列表</HButton>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.chat-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--harmony-comp-background-primary);
}

// Progress
.progress-bar-container {
  padding: 12px 24px;
  border-bottom: 1px solid var(--harmony-comp-divider);
  flex-shrink: 0;

  .progress-info {
    display: flex;
    justify-content: space-between;
    margin-bottom: 6px;

    .progress-label {
      font-size: 13px;
      font-weight: 600;
      color: var(--harmony-font-primary);
    }

    .progress-skill {
      font-size: 12px;
      color: var(--harmony-font-secondary);
    }

    .timer-display {
      margin-left: 12px;
      font-size: 12px;
      color: var(--harmony-font-tertiary);
      font-variant-numeric: tabular-nums; // 等宽数字，避免计时跳动导致布局偏移
    }
  }

  .progress-track {
    height: 4px;
    background: var(--harmony-comp-background-secondary);
    border-radius: 2px;
    overflow: hidden;

    .progress-fill {
      height: 100%;
      background: var(--harmony-brand);
      border-radius: 2px;
      transition: width 0.3s ease;
    }
  }
}

// Messages
.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message-group {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message-row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  max-width: 80%;

  &.ai {
    align-self: flex-start;
  }

  &.user {
    align-self: flex-end;
    flex-direction: row-reverse;
  }
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;

  &.ai-avatar {
    background: var(--harmony-comp-emphasize-tertiary);
  }

  &.user-avatar {
    background: var(--harmony-comp-background-secondary);
  }
}

.bubble {
  padding: 12px 16px;
  border-radius: 18px;
  font-size: 14px;
  line-height: 1.6;
  word-break: break-word;

  &.ai-bubble {
    background: var(--harmony-comp-background-secondary);
    color: var(--harmony-font-primary);
    border-top-left-radius: 4px;
  }

  &.user-bubble {
    background: var(--harmony-comp-emphasize-tertiary);
    color: var(--harmony-font-primary);
    border-top-right-radius: 4px;
  }
}

// Typing indicator
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 16px 20px;

  .dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--harmony-font-tertiary);
    animation: typingBounce 1.4s infinite ease-in-out both;

    &:nth-child(1) { animation-delay: 0s; }
    &:nth-child(2) { animation-delay: 0.16s; }
    &:nth-child(3) { animation-delay: 0.32s; }
  }
}

@keyframes typingBounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}

// Input area
.input-area {
  flex-shrink: 0;
  border-top: 1px solid var(--harmony-comp-divider);
  padding: 16px 24px;
}

.answer-input {
  width: 100%;
  border: 1px solid var(--harmony-comp-divider);
  border-radius: var(--harmony-corner-radius-level6);
  padding: 12px 16px;
  font-size: 14px;
  font-family: inherit;
  resize: none;
  background: var(--harmony-comp-background-primary);
  color: var(--harmony-font-primary);
  transition: border-color var(--harmony-duration-fast) var(--harmony-motion-standard);

  &:focus {
    border-color: var(--harmony-brand);
  }

  &::placeholder {
    color: var(--harmony-font-tertiary);
  }
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;

  .end-btn {
    color: var(--harmony-warning) !important;
  }
}

// Completed bar
.completed-bar {
  flex-shrink: 0;
  padding: 16px 24px;
  border-top: 1px solid var(--harmony-comp-divider);
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
  color: var(--harmony-font-secondary);
}

// Markdown rendering inside AI bubbles
:deep(.markdown-body) {
  p {
    margin: 0 0 6px 0;
    &:last-child { margin-bottom: 0; }
  }

  h1, h2, h3, h4 {
    margin: 10px 0 6px 0;
    font-weight: 600;
    font-size: 15px;
  }

  ul, ol {
    padding-left: 20px;
    margin: 6px 0;
  }

  li { margin: 3px 0; }

  code {
    background: rgba(128, 128, 128, 0.15);
    padding: 2px 5px;
    border-radius: 4px;
    font-family: var(--harmony-font-family);
    font-size: 13px;
  }

  pre {
    background: rgba(0, 0, 0, 0.2);
    padding: 12px;
    border-radius: 8px;
    overflow-x: auto;
    margin: 8px 0;

    code {
      background: none;
      padding: 0;
    }
  }

  strong { font-weight: 600; }
  em { font-style: italic; }
}
</style>

<script setup lang="ts">
import { ref, nextTick, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { HButton, HMessage } from '@/components/ui'
import { useInterviewStore } from '../../../store/interview'
import { getSessionDetailAPI } from '../../../apis/interview'
import { marked } from 'marked'

const router = useRouter()
const interviewStore = useInterviewStore()
const answerInput = ref('')
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
  const success = await interviewStore.submitAnswer(answer)
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
    HMessage.error('结束面试失败')
  }
}

const goBack = () => {
  router.push('/interview')
}

onMounted(async () => {
  // If no active interview, try to restore from route query
  if (!interviewStore.isActive && !interviewStore.isCompleted) {
    const sessionId = router.currentRoute.value.query.sessionId as string
    if (sessionId) {
      try {
        const res = await getSessionDetailAPI(sessionId)
        if (res.data.status_code === 200 && res.data.data) {
          // Redirect to report if completed
          const session = res.data.data.session
          if (session.status === 'COMPLETED') {
            router.replace({ path: '/interview/report', query: { sessionId } })
            return
          }
        }
      } catch { /* ignore */ }
    }
    // No active session, go back to selection
    router.replace('/interview')
    return
  }

  scrollBottom()
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
        <span class="progress-skill">{{ interviewStore.skillName }}</span>
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
          <div class="avatar user-avatar">👤</div>
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
          @click="endInterview"
        >
          结束面试
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
  background: var(--color-bg);
}

// Progress
.progress-bar-container {
  padding: 12px 24px;
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;

  .progress-info {
    display: flex;
    justify-content: space-between;
    margin-bottom: 6px;

    .progress-label {
      font-size: 13px;
      font-weight: 600;
      color: var(--color-text-primary);
    }

    .progress-skill {
      font-size: 12px;
      color: var(--color-text-secondary);
    }
  }

  .progress-track {
    height: 4px;
    background: var(--color-bg-secondary);
    border-radius: 2px;
    overflow: hidden;

    .progress-fill {
      height: 100%;
      background: var(--color-primary);
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
    background: var(--color-primary-bg);
  }

  &.user-avatar {
    background: var(--color-bg-secondary);
  }
}

.bubble {
  padding: 12px 16px;
  border-radius: 18px;
  font-size: 14px;
  line-height: 1.6;
  word-break: break-word;

  &.ai-bubble {
    background: var(--color-bg-secondary);
    color: var(--color-text-primary);
    border-top-left-radius: 4px;
  }

  &.user-bubble {
    background: linear-gradient(135deg, #6e8efb, #a777e3);
    color: #fff;
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
    background: var(--color-text-tertiary);
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
  border-top: 1px solid var(--color-border);
  padding: 16px 24px;
}

.answer-input {
  width: 100%;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 12px 16px;
  font-size: 14px;
  font-family: inherit;
  resize: none;
  background: var(--color-bg);
  color: var(--color-text-primary);
  outline: none;
  transition: border-color var(--duration-fast) var(--easing);

  &:focus {
    border-color: var(--color-primary);
  }

  &::placeholder {
    color: var(--color-text-tertiary);
  }
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;

  .end-btn {
    color: var(--color-danger) !important;
  }
}

// Completed bar
.completed-bar {
  flex-shrink: 0;
  padding: 16px 24px;
  border-top: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
  color: var(--color-text-secondary);
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
    font-family: 'Courier New', monospace;
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

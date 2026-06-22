<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { HMessage } from '@/components/ui'
import { getInterviewHistoryAPI } from '../../apis/interview'
import type { InterviewSession } from '../../apis/interview'
import { useInterviewStore } from '../../store/interview'

const router = useRouter()
const interviewStore = useInterviewStore()
const sessions = ref<InterviewSession[]>([])
const loading = ref(false)
const selectedSession = ref('')

const formatTime = (timeStr: string) => {
  try {
    if (!timeStr) return '未知时间'
    const date = new Date(timeStr)
    if (isNaN(date.getTime())) return '未知时间'
    const now = new Date()
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60)
    if (diffInHours < 1) return '刚刚'
    if (diffInHours < 24) return `${Math.floor(diffInHours)}小时前`
    if (diffInHours < 24 * 7) return `${Math.floor(diffInHours / 24)}天前`
    return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
  } catch {
    return '未知时间'
  }
}

const statusLabel = (status: string) => {
  const map: Record<string, string> = {
    CREATED: '已创建',
    IN_PROGRESS: '进行中',
    COMPLETED: '已完成',
  }
  return map[status] || status
}

const statusClass = (status: string) => {
  if (status === 'COMPLETED') return 'status-done'
  if (status === 'IN_PROGRESS') return 'status-active'
  return 'status-default'
}

const fetchHistory = async () => {
  loading.value = true
  try {
    const res = await getInterviewHistoryAPI()
    if (res.data.status_code === 200 && res.data.data) {
      sessions.value = res.data.data.sessions || []
    }
  } catch {
    HMessage.error('获取面试历史失败')
  } finally {
    loading.value = false
  }
}

const startNewInterview = () => {
  interviewStore.reset()
  router.push('/interview')
}

const selectSession = (session: InterviewSession) => {
  selectedSession.value = session.id
  if (session.status === 'COMPLETED') {
    router.push({ path: '/interview/report', query: { sessionId: session.id } })
  } else {
    router.push({ path: '/interview/chat', query: { sessionId: session.id } })
  }
}

onMounted(() => {
  fetchHistory()
})
</script>

<template>
  <div class="interview-container">
    <div class="sidebar">
      <div class="create-section">
        <button class="create-btn" @click="startNewInterview">
          <span>＋</span>
          <span>开始新面试</span>
        </button>
      </div>

      <div class="session-list">
        <div v-if="loading" class="empty-state">
          <div class="empty-text">加载中...</div>
        </div>

        <div v-else-if="sessions.length === 0" class="empty-state">
          <div class="empty-icon">📝</div>
          <div class="empty-text">暂无面试记录</div>
        </div>

        <div
          v-for="session in sessions"
          :key="session.id"
          :class="['session-card', { active: selectedSession === session.id }]"
          @click="selectSession(session)"
        >
          <div class="session-icon">📝</div>
          <div class="session-info">
            <div class="session-title">{{ session.skill_id }}</div>
            <div class="session-meta">
              <span :class="['status-tag', statusClass(session.status)]">
                {{ statusLabel(session.status) }}
              </span>
              <span class="session-progress">
                {{ session.progress?.current || 0 }}/{{ session.progress?.total || 0 }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="content">
      <router-view />
    </div>
  </div>
</template>

<style lang="scss" scoped>
.interview-container {
  width: 100%;
  height: 100%;
  display: flex;
  background: var(--color-bg);
}

.sidebar {
  height: 100%;
  width: 280px;
  background: var(--color-bg);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;

  .create-section {
    padding: 16px;
    flex-shrink: 0;

    .create-btn {
      width: 100%;
      height: 44px;
      border-radius: var(--radius-sm);
      background: var(--color-bg);
      color: var(--color-primary);
      border: 1px solid var(--color-border);
      cursor: pointer;
      font-size: 14px;
      font-weight: 500;
      font-family: inherit;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      transition: all var(--duration-fast) var(--easing);

      &:hover {
        border-color: var(--color-primary);
        background: var(--color-primary-bg);
      }
    }
  }

  .session-list {
    flex: 1;
    padding: 0 8px 8px;
    overflow-y: auto;

    .empty-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 200px;

      .empty-icon {
        font-size: 32px;
        margin-bottom: 12px;
        opacity: 0.4;
      }

      .empty-text {
        font-size: var(--font-size-base);
        color: var(--color-text-tertiary);
      }
    }

    .session-card {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 12px;
      margin-bottom: 4px;
      background: var(--color-bg);
      border: 1px solid transparent;
      border-radius: var(--radius-md);
      cursor: pointer;
      transition: all var(--duration-fast) var(--easing);

      &:hover {
        background: var(--color-bg-secondary);
        border-color: var(--color-border);
      }

      &.active {
        background: var(--color-primary-bg);
        border-color: var(--color-primary);
      }

      .session-icon {
        width: 28px;
        height: 28px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--color-primary-bg);
        border-radius: var(--radius-sm);
        flex-shrink: 0;
        font-size: 14px;
      }

      .session-info {
        flex: 1;
        min-width: 0;

        .session-title {
          font-size: var(--font-size-base);
          font-weight: 500;
          color: var(--color-text-primary);
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
          margin-bottom: 4px;
        }

        .session-meta {
          display: flex;
          align-items: center;
          gap: 8px;

          .status-tag {
            font-size: 11px;
            padding: 1px 6px;
            border-radius: 4px;
          }

          .status-done {
            background: var(--color-success-bg, #e8f5e9);
            color: var(--color-success, #4caf50);
          }

          .status-active {
            background: var(--color-primary-bg);
            color: var(--color-primary);
          }

          .status-default {
            background: var(--color-bg-secondary);
            color: var(--color-text-tertiary);
          }

          .session-progress {
            font-size: var(--font-size-xs);
            color: var(--color-text-tertiary);
          }
        }
      }
    }
  }
}

.content {
  flex: 1;
  min-width: 0;
  min-height: 0;
  background: var(--color-bg);
  overflow: hidden;
}
</style>

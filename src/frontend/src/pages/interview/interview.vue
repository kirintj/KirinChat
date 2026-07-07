<script setup lang="ts">
import { ref, onMounted, inject } from 'vue'
import { useRouter } from 'vue-router'
import { HMessage } from '@/components/ui'
import { getInterviewHistoryAPI, deleteInterviewSessionAPI } from '../../apis/interview'
import type { InterviewSession } from '../../apis/interview'
import { useInterviewStore } from '../../store/interview'

const isMobile = inject<import('vue').Ref<boolean>>('isMobile', ref(false))
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

const deleteSession = async (sessionId: string, event: Event) => {
  event.stopPropagation()
  try {
    const res = await deleteInterviewSessionAPI(sessionId)
    if (res.data.status_code === 200) {
      HMessage.success('已删除')
      await fetchHistory()
      if (selectedSession.value === sessionId) {
        selectedSession.value = ''
        router.push('/interview')
      }
    } else {
      HMessage.error('删除失败')
    }
  } catch {
    HMessage.error('删除失败')
  }
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
  <!-- Desktop: sidebar + content layout -->
  <div v-if="!isMobile" class="interview-container">
    <div class="sidebar">
      <div class="hub-nav">
        <!-- 面试中心导航按钮，点击跳转到面试中心仪表盘页面 -->
        <button class="hub-btn" @click="router.push('/interview/hub')">
          <span class="hub-icon">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/>
            </svg>
          </span>
          <span>面试中心</span>
        </button>
      </div>

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
          <button class="delete-btn" @click="deleteSession(session.id, $event)" title="删除">×</button>
        </div>
      </div>
    </div>

    <div class="content">
      <router-view />
    </div>
  </div>

  <!-- Mobile: hmos mobile-list -->
  <div v-else class="interview-mobile">
    <!-- Create button -->
    <div class="im-header">
      <button class="im-create-btn" @click="startNewInterview">+ 新建面试</button>
    </div>

    <!-- Session list -->
    <div class="im-list" v-if="sessions.length > 0">
      <div
        v-for="session in sessions"
        :key="session.id"
        class="im-item"
        @click="selectSession(session)"
      >
        <div class="im-item__icon">📋</div>
        <div class="im-item__content">
          <h3 class="im-item__name">{{ session.skill_name || session.skill_id || '面试会话' }}</h3>
          <p class="im-item__time">{{ formatTime(session.create_time || '') }}</p>
        </div>
        <button class="im-item__delete" @click.stop="deleteSession(session.id, $event)">×</button>
      </div>
    </div>

    <div v-else class="im-empty">
      <p>暂无面试记录</p>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.interview-container {
  width: 100%;
  height: 100%;
  display: flex;
  background: var(--harmony-comp-background-primary);
}

.sidebar {
  height: 100%;
  width: 280px;
  background: var(--harmony-comp-background-primary);
  border-right: 1px solid var(--harmony-comp-divider);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;

  /* 面试中心导航按钮样式 */
  .hub-nav {
    padding: 12px 16px 0;
  }

  .hub-btn {
    display: flex;
    align-items: center;
    gap: 8px;
    width: 100%;
    padding: 10px 14px;
    border: 1px solid var(--harmony-comp-divider);
    border-radius: var(--harmony-corner-radius-level4);
    background: var(--harmony-comp-background-tertiary);
    color: var(--harmony-font-primary);
    cursor: pointer;
    font-size: var(--harmony-font-size-body-m);
    font-family: inherit;
    transition: all 0.2s ease;

    &:hover {
      background: var(--bg-hover, var(--harmony-comp-background-tertiary));
      border-color: var(--harmony-brand);
      color: var(--harmony-brand);
    }

    /* SVG图标容器，保持图标垂直居中 */
    .hub-icon {
      display: flex;
      align-items: center;
    }
  }

  .create-section {
    padding: 16px;
    flex-shrink: 0;

    .create-btn {
      width: 100%;
      height: 44px;
      border-radius: var(--harmony-corner-radius-level4);
      background: var(--harmony-comp-background-primary);
      color: var(--harmony-brand);
      border: 1px solid var(--harmony-comp-divider);
      cursor: pointer;
      font-size: var(--harmony-font-size-body-m);
      font-weight: 500;
      font-family: inherit;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      transition: all var(--harmony-duration-fast) var(--harmony-motion-standard);

      &:hover {
        border-color: var(--harmony-brand);
        background: var(--harmony-comp-emphasize-tertiary);
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
        font-size: var(--harmony-font-size-title-l);
        margin-bottom: 12px;
        opacity: 0.4;
      }

      .empty-text {
        font-size: var(--harmony-font-size-body-m);
        color: var(--harmony-font-tertiary);
      }
    }

    .session-card {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 12px;
      margin-bottom: 4px;
      background: var(--harmony-comp-background-primary);
      border: 1px solid transparent;
      border-radius: var(--harmony-corner-radius-level6);
      cursor: pointer;
      transition: all var(--harmony-duration-fast) var(--harmony-motion-standard);
      position: relative;

      &:hover {
        background: var(--harmony-comp-background-secondary);
        border-color: var(--harmony-comp-divider);

        .delete-btn {
          opacity: 1;
        }
      }

      &.active {
        background: var(--harmony-comp-emphasize-tertiary);
        border-color: var(--harmony-brand);
      }

      .session-icon {
        width: 28px;
        height: 28px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--harmony-comp-emphasize-tertiary);
        border-radius: var(--harmony-corner-radius-level4);
        flex-shrink: 0;
        font-size: var(--harmony-font-size-body-m);
      }

      .session-info {
        flex: 1;
        min-width: 0;

        .session-title {
          font-size: var(--harmony-font-size-body-m);
          font-weight: 500;
          color: var(--harmony-font-primary);
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
            font-size: var(--harmony-font-size-caption-l);
            padding: 1px 6px;
            border-radius: var(--harmony-corner-radius-level2);
          }

          .status-done {
            background: var(--harmony-confirm-bg);
            color: var(--harmony-confirm);
          }

          .status-active {
            background: var(--harmony-comp-emphasize-tertiary);
            color: var(--harmony-brand);
          }

          .status-default {
            background: var(--harmony-comp-background-secondary);
            color: var(--harmony-font-tertiary);
          }

          .session-progress {
            font-size: var(--harmony-font-size-body-s);
            color: var(--harmony-font-tertiary);
          }
        }
      }

      .delete-btn {
        position: absolute;
        top: 6px;
        right: 6px;
        width: 22px;
        height: 22px;
        padding: 0;
        background: var(--harmony-comp-background-primary);
        border: 1px solid var(--harmony-comp-divider);
        cursor: pointer;
        border-radius: var(--harmony-corner-radius-level4);
        font-size: var(--harmony-font-size-body-m);
        opacity: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--harmony-font-secondary);
        transition: all var(--harmony-duration-fast) var(--harmony-motion-standard);

        &:hover {
          background: var(--harmony-warning-bg);
          color: var(--harmony-warning);
          border-color: var(--harmony-warning);
        }
      }
    }
  }
}

.content {
  flex: 1;
  min-width: 0;
  min-height: 0;
  background: var(--harmony-comp-background-primary);
  overflow: hidden;
}

/* ==================== MOBILE: hmos mobile-list ==================== */
.interview-mobile {
  display: flex;
  flex-direction: column;
  gap: var(--harmony-section-gap-mobile, 16px);
  padding-top: var(--harmony-padding-level8, 16px);
}

.im-header {
  display: flex;
  justify-content: flex-end;
}

.im-create-btn {
  height: var(--harmony-control-height-40, 40px);
  padding: 0 var(--harmony-padding-level8, 16px);
  background: var(--harmony-brand);
  color: white;
  border: none;
  border-radius: var(--harmony-corner-radius-level6, 12px);
  font-size: var(--harmony-font-size-body-m);
  font-weight: 500;
  cursor: pointer;
}

.im-list {
  display: flex;
  flex-direction: column;
  gap: var(--harmony-card-gap-mobile, 12px);
}

.im-item {
  display: flex;
  align-items: center;
  gap: var(--harmony-padding-level6, 12px);
  padding: var(--harmony-padding-level6, 12px);
  background: var(--harmony-comp-background-primary);
  border: 1px solid var(--harmony-comp-divider);
  border-radius: var(--harmony-corner-radius-level8, 16px);
  cursor: pointer;
  transition: background 0.15s ease;

  &:active {
    background: var(--harmony-interactive-pressed);
  }

  &__icon {
    width: var(--harmony-control-height-40, 40px);
    height: var(--harmony-control-height-40, 40px);
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--harmony-comp-background-secondary);
    border-radius: var(--harmony-corner-radius-level6, 12px);
    flex-shrink: 0;
    font-size: 20px;
  }

  &__content {
    flex: 1;
    min-width: 0;
  }

  &__name {
    font-size: var(--harmony-font-size-body-m);
    font-weight: 600;
    color: var(--harmony-font-primary);
    margin: 0 0 var(--harmony-padding-level1, 2px) 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  &__time {
    font-size: var(--harmony-font-size-body-s);
    color: var(--harmony-font-tertiary);
    margin: 0;
  }

  &__delete {
    width: var(--harmony-control-height-36, 36px);
    height: var(--harmony-control-height-36, 36px);
    display: flex;
    align-items: center;
    justify-content: center;
    background: transparent;
    border: none;
    border-radius: var(--harmony-corner-radius-level4, 8px);
    color: var(--harmony-font-tertiary);
    font-size: 20px;
    cursor: pointer;
    flex-shrink: 0;

    &:active {
      background: var(--harmony-interactive-pressed);
      color: var(--harmony-warning);
    }
  }
}

.im-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 80px 0;

  p {
    font-size: var(--harmony-font-size-body-m);
    color: var(--harmony-font-tertiary);
    margin: 0;
  }
}
</style>

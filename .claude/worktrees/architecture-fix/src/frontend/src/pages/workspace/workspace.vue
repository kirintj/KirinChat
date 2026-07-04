<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { HButton, HInput, HMessage } from '@/components/ui'
import {
  getWorkspaceSessionsAPI,
  deleteWorkspaceSessionAPI
} from '../../apis/workspace'

const router = useRouter()
const selectedSession = ref('')
const sessions = ref<any[]>([])
const loading = ref(false)

// 格式化时间
const formatTime = (timeStr: string) => {
  try {
    if (!timeStr) return '未知时间'

    const date = new Date(timeStr)
    if (isNaN(date.getTime())) {
      return '未知时间'
    }

    const now = new Date()
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60)

    if (diffInHours < 1) return '刚刚'
    if (diffInHours < 24) return `${Math.floor(diffInHours)}小时前`
    if (diffInHours < 24 * 7) return `${Math.floor(diffInHours / 24)}天前`
    return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
  } catch (error) {
    return '未知时间'
  }
}

// 获取会话列表
const fetchSessions = async () => {
  try {
    loading.value = true
    const response = await getWorkspaceSessionsAPI()
    if (response.data.status_code === 200) {
      sessions.value = response.data.data.map((session: any) => ({
        sessionId: session.session_id || session.id,
        title: session.title || '未命名会话',
        createTime: session.create_time || session.created_at || new Date().toISOString(),
        agent: session.agent || 'lingseek', // 保存agent类型，默认为lingseek
        contexts: session.contexts || [] // 保存上下文
      }))
      console.log('工作区会话列表:', sessions.value)
    } else {
      HMessage.error('获取会话列表失败')
    }
  } catch (error) {
    console.error('获取会话列表出错:', error)
    HMessage.error('获取会话列表失败')
  } finally {
    loading.value = false
  }
}

// 删除会话
const deleteSession = async (sessionId: string, event: Event) => {
  event.stopPropagation()

  try {
    const response = await deleteWorkspaceSessionAPI(sessionId)
    if (response.data.status_code === 200) {
      HMessage.success('会话删除成功')
      await fetchSessions()

      if (selectedSession.value === sessionId) {
        selectedSession.value = ''
        router.push('/workspace')
      }
    } else {
      HMessage.error('删除会话失败')
    }
  } catch (error) {
    console.error('删除会话出错:', error)
    HMessage.error('删除会话失败')
  }
}

// 选择会话 - 根据agent类型跳转到不同页面
const selectSession = (sessionId: string) => {
  selectedSession.value = sessionId

  // 找到对应的会话
  const session = sessions.value.find(s => s.sessionId === sessionId)

  if (!session) {
    console.error('未找到会话:', sessionId)
    return
  }

  console.log('选择会话:', sessionId, '类型:', session.agent)

  // 根据agent类型判断跳转页面
  if (session.agent === 'simple') {
    // 日常模式，跳转到日常对话页面，并传递session_id
    router.push({
      name: 'workspaceDefaultPage',
      query: {
        session_id: sessionId
      }
    })
  } else {
    // lingseek模式，跳转到三列布局页面
    router.push({
      name: 'taskGraphPage',
      query: {
        session_id: sessionId
      }
    })
  }
}

onMounted(async () => {
  await fetchSessions()
})
</script>

<template>
  <div class="workspace-container">
    <div class="sidebar">
      <div class="create-section">
        <button @click="router.push('/homepage')" class="create-btn">
          <img src="../../assets/application-center.svg" width="18" height="18" />
          <span>应用中心</span>
        </button>
      </div>

      <div class="session-list">
        <div v-if="loading" class="loading-state">
          <div class="loading-icon">⏳</div>
          <div class="loading-text">正在加载会话列表...</div>
        </div>

        <div v-else-if="sessions.length === 0" class="empty-state">
          <img src="../../assets/workspace-session.svg" alt="暂无会话" class="empty-icon-img" />
          <div class="empty-text">暂无会话记录</div>
        </div>

        <div
          v-for="session in sessions"
          :key="session.sessionId"
          :class="['session-card', { active: selectedSession === session.sessionId }]"
          @click="selectSession(session.sessionId)"
        >
          <div class="session-icon">
            <img src="../../assets/workspace-session.svg" width="18" height="18" />
          </div>
          <div class="session-info">
            <div class="session-title">{{ session.title }}</div>
            <div class="session-time">{{ formatTime(session.createTime) }}</div>
          </div>
          <button class="delete-btn" @click="deleteSession(session.sessionId, $event)" title="删除会话">×</button>
        </div>
      </div>
    </div>

    <div class="content">
      <router-view />
    </div>
  </div>
</template>

<style lang="scss" scoped>
.workspace-container {
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

    .loading-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 200px;

      .loading-icon {
        font-size: 32px;
        margin-bottom: 12px;
        animation: spin 1s linear infinite;
      }

      .loading-text {
        font-size: var(--font-size-sm);
        color: var(--color-text-secondary);
      }
    }

    .empty-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 200px;

      .empty-icon-img {
        width: 48px;
        height: 48px;
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
      position: relative;

      &:hover {
        background: var(--color-bg-secondary);
        border-color: var(--color-border);

        .delete-btn {
          opacity: 1;
        }
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
          margin-bottom: 2px;
        }

        .session-time {
          font-size: var(--font-size-xs);
          color: var(--color-text-tertiary);
        }
      }

      .delete-btn {
        position: absolute;
        top: 6px;
        right: 6px;
        width: 22px;
        height: 22px;
        padding: 0;
        background: var(--color-bg);
        border: 1px solid var(--color-border);
        cursor: pointer;
        border-radius: var(--radius-sm);
        transition: all var(--duration-fast) var(--easing);
        font-size: 14px;
        opacity: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--color-text-secondary);

        &:hover {
          background: var(--color-danger-bg);
          color: var(--color-danger);
          border-color: var(--color-danger);
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

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .sidebar {
    width: 240px;
  }
}

@media (max-width: 480px) {
  .workspace-container {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    height: auto;
    max-height: 240px;
  }
}
</style>

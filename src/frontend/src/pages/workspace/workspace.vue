<script setup lang="ts">
import { ref, computed, onMounted, inject } from 'vue'
import { useRouter } from 'vue-router'
import { HButton, HInput, HMessage } from '@/components/ui'
import {
  getWorkspaceSessionsAPI,
  deleteWorkspaceSessionAPI
} from '../../apis/workspace'

const router = useRouter()
const isMobile = inject<import('vue').Ref<boolean>>('isMobile', ref(false))
const selectedSession = ref('')
const sessions = ref<any[]>([])
const loading = ref(false)
const searchQuery = ref('')

// 格式化时间
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

// 获取Agent图标
const getAgentIcon = (agent: string) => {
  const map: Record<string, string> = {
    simple: 'mdi:message-text',
    lingseek: 'mdi:sparkles',
  }
  return map[agent] || 'mdi:robot'
}

// 获取Agent标签
const getAgentLabel = (agent: string) => {
  const map: Record<string, string> = {
    simple: '日常模式',
    lingseek: '深思模式',
  }
  return map[agent] || '未知'
}

// 过滤后的会话
const filteredSessions = computed(() => {
  if (!searchQuery.value.trim()) return sessions.value
  const q = searchQuery.value.toLowerCase()
  return sessions.value.filter(s => 
    s.title.toLowerCase().includes(q)
  )
})

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
        agent: session.agent || 'lingseek',
        contexts: session.contexts || []
      }))
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
      HMessage.success('会话已删除')
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

// 选择会话
const selectSession = (sessionId: string) => {
  selectedSession.value = sessionId
  const session = sessions.value.find(s => s.sessionId === sessionId)
  if (!session) return

  if (session.agent === 'simple') {
    router.push({
      name: 'workspaceDefaultPage',
      query: { session_id: sessionId }
    })
  } else {
    router.push({
      name: 'taskGraphPage',
      query: { session_id: sessionId }
    })
  }
}

// 创建新会话
const createNewSession = () => {
  router.push('/workspace')
}

onMounted(async () => {
  await fetchSessions()
})
</script>

<template>
  <!-- Desktop -->
  <div v-if="!isMobile" class="workspace-root">
    <!-- 左侧面板 -->
    <aside class="sidebar-panel">
      <!-- 顶部操作区 -->
      <div class="sidebar-header">
        <div class="header-top">
          <h2 class="panel-title">会话列表</h2>
          <span class="session-count">{{ sessions.length }}</span>
        </div>
        <button class="new-session-btn" @click="createNewSession">
          <Icon icon="mdi:plus" :width="16" :height="16" />
          <span>新建会话</span>
        </button>
      </div>

      <!-- 搜索 -->
      <div class="search-box">
        <Icon class="search-icon" icon="mdi:magnify" :width="14" :height="14" />
        <input
          v-model="searchQuery"
          type="text"
          placeholder="搜索会话"
          class="search-input"
        />
      </div>

      <!-- 会话列表 -->
      <div class="session-list">
        <!-- 加载态 -->
        <div v-if="loading" class="state-box">
          <div class="spinner"></div>
          <p class="state-text">加载中...</p>
        </div>

        <!-- 搜索无结果 -->
        <div v-else-if="searchQuery && filteredSessions.length === 0" class="state-box">
          <Icon icon="mdi:magnify" :width="36" :height="36" style="opacity: 0.3;" />
          <p class="state-text">未找到匹配会话</p>
        </div>

        <!-- 空态 -->
        <div v-else-if="sessions.length === 0" class="state-box">
          <Icon icon="mdi:plus-box-outline" :width="36" :height="36" style="opacity: 0.3;" />
          <p class="state-text">暂无会话记录</p>
          <p class="state-hint">点击上方按钮创建新会话</p>
        </div>

        <!-- 会话卡片列表 -->
        <div
          v-for="session in filteredSessions"
          :key="session.sessionId"
          :class="['session-card', { active: selectedSession === session.sessionId }]"
          @click="selectSession(session.sessionId)"
        >
          <div class="card-avatar" :class="session.agent">
            <Icon :icon="getAgentIcon(session.agent)" :width="18" :height="18" />
          </div>
          <div class="card-body">
            <div class="card-title-row">
              <span class="card-title">{{ session.title }}</span>
              <span class="card-badge" :class="session.agent">{{ getAgentLabel(session.agent) }}</span>
            </div>
            <div class="card-time">{{ formatTime(session.createTime) }}</div>
          </div>
          <button class="card-delete" @click="deleteSession(session.sessionId, $event)" title="删除会话">
            <Icon icon="mdi:close" :width="14" :height="14" />
          </button>
        </div>
      </div>
    </aside>

    <!-- 右侧内容区 -->
    <main class="content-area">
      <router-view />
    </main>
  </div>

  <!-- Mobile -->
  <div v-else class="workspace-mobile">
    <div class="wm-header">
      <button class="wm-create-btn" @click="createNewSession">+ 新建会话</button>
    </div>

    <div class="wm-list" v-if="filteredSessions.length > 0">
      <div
        v-for="session in filteredSessions"
        :key="session.sessionId"
        class="wm-item"
        @click="selectSession(session.sessionId)"
      >
        <div class="wm-item__icon"><Icon :icon="getAgentIcon(session.agent)" :width="20" :height="20" /></div>
        <div class="wm-item__content">
          <h3 class="wm-item__name">{{ session.title }}</h3>
          <p class="wm-item__time">{{ formatTime(session.createTime) }}</p>
        </div>
        <span class="wm-item__badge" :class="session.agent">{{ getAgentLabel(session.agent) }}</span>
      </div>
    </div>

    <div v-else-if="loading" class="wm-empty">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else class="wm-empty">
      <p>暂无会话记录</p>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@use '../../styles/breakpoints.scss' as *;

.workspace-root {
  width: 100%;
  height: 100%;
  display: flex;
  background: transparent;
}

/* ===== 左侧面板 ===== */
.sidebar-panel {
  width: 280px;
  min-width: 280px;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: transparent;
  border-right: 1px solid var(--harmony-comp-divider);
}

/* 顶部 */
.sidebar-header {
  padding: 16px 16px 0;
  flex-shrink: 0;

  .header-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12px;

    .panel-title {
      font-size: var(--harmony-font-size-body-l);
      font-weight: 600;
      color: var(--harmony-font-primary);
      margin: 0;
    }

    .session-count {
      font-size: var(--harmony-font-size-body-s);
      color: var(--harmony-font-tertiary);
      background: var(--harmony-comp-background-secondary);
      padding: 2px 8px;
      border-radius: var(--harmony-corner-radius-level18);
      font-weight: 500;
    }
  }

  .new-session-btn {
    width: 100%;
    height: 38px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    border: 1px dashed var(--harmony-comp-divider);
    border-radius: var(--harmony-corner-radius-level6);
    background: var(--harmony-comp-background-primary);
    color: var(--harmony-font-secondary);
    font-size: var(--harmony-font-size-subtitle-s);
    font-weight: 500;
    cursor: pointer;
    transition: all var(--harmony-duration-fast) var(--harmony-motion-standard);
    font-family: inherit;

    &:hover {
      border-color: var(--harmony-brand);
      color: var(--harmony-brand);
      background: var(--harmony-comp-emphasize-tertiary);
      border-style: solid;
    }
  }
}

/* 搜索 */
.search-box {
  position: relative;
  margin: 12px 16px;
  flex-shrink: 0;

  .search-icon {
    position: absolute;
    left: 10px;
    top: 50%;
    transform: translateY(-50%);
    color: var(--harmony-font-tertiary);
    pointer-events: none;
  }

  .search-input {
    width: 100%;
    height: 34px;
    padding: 0 10px 0 32px;
    border: 1px solid var(--harmony-comp-divider);
    border-radius: var(--harmony-corner-radius-level4);
    color: var(--harmony-font-primary);
    font-size: var(--harmony-font-size-subtitle-s);
    transition: all var(--harmony-duration-fast) var(--harmony-motion-standard);
    font-family: inherit;

    &::placeholder {
      color: var(--harmony-font-tertiary);
    }
  }
}

/* 会话列表容器 */
.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 16px 8px;
}

/* 通用状态 */
.state-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 20px;
  text-align: center;
  gap: 8px;

  .state-text {
    font-size: var(--harmony-font-size-subtitle-s);
    color: var(--harmony-font-tertiary);
    margin: 0;
  }

  .state-hint {
    font-size: var(--harmony-font-size-body-s);
    color: var(--harmony-font-fourth);
    margin: 0;
  }
}

/* 加载旋转 */
.spinner {
  width: 24px;
  height: 24px;
  border: 2px solid var(--harmony-comp-divider);
  border-top-color: var(--harmony-brand);
  border-radius: 50%;
  animation: h-spin 0.7s linear infinite;
}



/* ===== 会话卡片 ===== */
.session-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  margin-bottom: 4px;
  border-radius: var(--harmony-corner-radius-level6);
  cursor: pointer;
  transition: all var(--harmony-duration-fast) var(--harmony-motion-standard);
  position: relative;
  border: 1px solid transparent;

  &:hover {
    background: var(--harmony-comp-background-secondary);
    border-color: var(--harmony-comp-divider);

    .card-delete {
      opacity: 1;
    }
  }

  &.active {
    background: var(--harmony-comp-emphasize-tertiary);
    border-color: var(--harmony-brand);
  }

  .card-avatar {
    width: 34px;
    height: 34px;
    border-radius: var(--harmony-corner-radius-level4);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: var(--harmony-font-size-body-l);
    flex-shrink: 0;
    background: var(--harmony-comp-background-secondary);
    border: 1px solid var(--harmony-comp-divider);

    &.simple {
      background: var(--harmony-comp-emphasize-tertiary);
      border-color: #c7d2fe;
    }

    &.lingseek {
      background: var(--harmony-alert-bg);
      border-color: #fde68a;
    }
  }

  .card-body {
    flex: 1;
    min-width: 0;

    .card-title-row {
      display: flex;
      align-items: center;
      gap: 6px;
      margin-bottom: 2px;

      .card-title {
        font-size: var(--harmony-font-size-subtitle-s);
        font-weight: 500;
        color: var(--harmony-font-primary);
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      .card-badge {
        font-size: var(--harmony-font-size-caption-m);
        padding: 1px 6px;
        border-radius: var(--harmony-corner-radius-level18);
        font-weight: 500;
        flex-shrink: 0;
        line-height: 1.4;

        &.simple {
          background: var(--harmony-comp-emphasize-tertiary);
          color: var(--harmony-brand);
        }

        &.lingseek {
          background: var(--harmony-alert-bg);
          color: var(--harmony-alert);
        }
      }
    }

    .card-time {
      font-size: var(--harmony-font-size-body-s);
      color: var(--harmony-font-tertiary);
    }
  }

  .card-delete {
    position: absolute;
    top: 6px;
    right: 6px;
    width: 24px;
    height: 24px;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid var(--harmony-comp-divider);
    border-radius: var(--harmony-corner-radius-level4);
    background: var(--harmony-comp-background-primary);
    color: var(--harmony-font-tertiary);
    cursor: pointer;
    opacity: 0;
    transition: all var(--harmony-duration-fast) var(--harmony-motion-standard);

    &:hover {
      background: var(--harmony-warning-bg);
      color: var(--harmony-warning);
      border-color: var(--harmony-warning);
    }
  }
}

/* ===== 右侧内容区 ===== */
.content-area {
  flex: 1;
  min-width: 0;
  min-height: 0;
  overflow: hidden;
  background: transparent;
}

/* 响应式 */
@include mobile {
  .sidebar-panel {
    width: 240px;
    min-width: 240px;
  }
}

@include mobile {
  .workspace-root {
    flex-direction: column;
  }
  .sidebar-panel {
    width: 100%;
    min-width: 0;
    height: auto;
    max-height: 240px;
  }
}

/* ===== Mobile hmos list ===== */
.workspace-mobile {
  width: 100%;
  min-height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--harmony-comp-background-primary);
}

.wm-header {
  display: flex;
  padding: 16px 0 12px;

  .wm-create-btn {
    width: 100%;
    height: var(--harmony-control-height-40, 40px);
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px dashed var(--harmony-comp-divider);
    border-radius: var(--harmony-corner-radius-level6);
    background: var(--harmony-comp-background-secondary);
    color: var(--harmony-font-secondary);
    font-size: var(--harmony-font-size-body-l);
    font-weight: 500;
    font-family: inherit;
    cursor: pointer;
    transition: all var(--harmony-duration-fast) var(--harmony-motion-standard);

    &:active {
      background: var(--harmony-comp-emphasize-tertiary);
      border-color: var(--harmony-brand);
      color: var(--harmony-brand);
    }
  }
}

.wm-list {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--harmony-inline-gap-tight-mobile, 4px);
}

.wm-item {
  display: flex;
  align-items: center;
  gap: var(--harmony-inline-gap-mobile, 12px);
  padding: 14px 0;
  cursor: pointer;
  border-bottom: 1px solid var(--harmony-comp-divider);
  transition: background var(--harmony-duration-fast) var(--harmony-motion-standard);

  &:active {
    background: var(--harmony-comp-emphasize-tertiary);
  }

  &:last-child {
    border-bottom: none;
  }

  &__icon {
    width: var(--harmony-control-height-40, 40px);
    height: var(--harmony-control-height-40, 40px);
    border-radius: var(--harmony-corner-radius-level6);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: var(--harmony-font-size-title-s, 20px);
    background: var(--harmony-comp-background-secondary);
    flex-shrink: 0;
  }

  &__content {
    flex: 1;
    min-width: 0;
  }

  &__name {
    margin: 0;
    font-size: var(--harmony-font-size-body-l);
    font-weight: 500;
    color: var(--harmony-font-primary);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  &__time {
    margin: 4px 0 0;
    font-size: var(--harmony-font-size-body-s);
    color: var(--harmony-font-tertiary);
  }

  &__badge {
    font-size: var(--harmony-font-size-caption-m);
    padding: 2px 8px;
    border-radius: var(--harmony-corner-radius-level18);
    font-weight: 500;
    flex-shrink: 0;

    &.simple {
      background: var(--harmony-comp-emphasize-tertiary);
      color: var(--harmony-brand);
    }

    &.lingseek {
      background: var(--harmony-alert-bg);
      color: var(--harmony-alert);
    }
  }
}

.wm-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--harmony-padding-level16, 32px) 0;
  gap: 12px;

  p {
    margin: 0;
    font-size: var(--harmony-font-size-body-l);
    color: var(--harmony-font-tertiary);
  }
}
</style>

<script setup lang="ts">
import { ref, onMounted, computed, inject } from "vue"
import { useRouter } from "vue-router"
import { HMessage } from "@/components/ui"
import { getAgentsAPI } from "../../apis/agent"
import { createDialogAPI, getDialogListAPI, deleteDialogAPI } from "../../apis/history"
import type { AgentResponse, ApiResponse } from "../../apis/agent"
import type { HistoryListType, DialogCreateType } from "../../type"
import histortCard from '../../components/historyCard/histortCard.vue'
import { useHistoryChatStore } from "../../store/history_chat_msg"

const isMobile = inject<import('vue').Ref<boolean>>('isMobile', ref(false))
const router = useRouter()
const historyChatStore = useHistoryChatStore()
const searchKeyword = ref('')
const selectedDialog = ref('')
const showCreateDialog = ref(false)
const selectedAgent = ref('')
const agentSearchKeyword = ref('')

// 真实数据
const dialogs = ref<HistoryListType[]>([])
const agents = ref<AgentResponse[]>([])
const loading = ref(false)
const agentsLoading = ref(false)

// 过滤后的会话数据
const filteredDialogs = computed(() => {
  if (!searchKeyword.value) return dialogs.value
  return dialogs.value.filter(dialog =>
    dialog.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
    dialog.agent.toLowerCase().includes(searchKeyword.value.toLowerCase())
  )
})

// 过滤后的智能体数据
const filteredAgents = computed(() => {
  if (!agentSearchKeyword.value) return agents.value
  return agents.value.filter(agent =>
    agent.name.toLowerCase().includes(agentSearchKeyword.value.toLowerCase()) ||
    agent.description.toLowerCase().includes(agentSearchKeyword.value.toLowerCase())
  )
})

// 格式化时间
const formatTime = (timeStr: string) => {
  try {
    if (!timeStr) return '未知时间'

    // 处理不同的时间格式
    let date: Date
    if (typeof timeStr === 'string') {
      // 如果是ISO格式字符串
      if (timeStr.includes('T') || timeStr.includes('Z')) {
        date = new Date(timeStr)
      } else {
        // 尝试解析其他格式
        date = new Date(timeStr)
      }
    } else {
      date = new Date(timeStr)
    }

    // 检查日期是否有效
    if (isNaN(date.getTime())) {
      console.warn('无效的时间格式:', timeStr)
      return '未知时间'
    }

    const now = new Date()
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60)

    if (diffInHours < 1) return '刚刚'
    if (diffInHours < 24) return `${Math.floor(diffInHours)}小时前`
    if (diffInHours < 24 * 7) return `${Math.floor(diffInHours / 24)}天前`
    return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
  } catch (error) {
    console.error('时间格式化错误:', error, '时间字符串:', timeStr)
    return '未知时间'
  }
}

// 获取智能体列表
const fetchAgents = async () => {
  try {
    agentsLoading.value = true
    const response = await getAgentsAPI()
    if (response.data.status_code === 200) {
      agents.value = response.data.data
      console.log('智能体列表获取成功:', agents.value)
      console.log('智能体ID详情:', agents.value.map(a => ({
        name: a.name,
        agent_id: a.agent_id,
        id: (a as any).id,
        agent_id_type: typeof a.agent_id,
        id_type: typeof (a as any).id
      })))
    } else {
      HMessage.error(`获取智能体列表失败: ${response.data.status_message}`)
    }
  } catch (error) {
    console.error('获取智能体列表出错:', error)
    HMessage.error('获取智能体列表失败，请检查网络连接')
  } finally {
    agentsLoading.value = false
  }
}

// 获取对话列表
const fetchDialogs = async () => {
  try {
    loading.value = true
    const response = await getDialogListAPI()
    if (response.data.status_code === 200) {
      // 处理返回的数据，确保字段名称正确
      console.log('原始对话数据:', response.data.data)
      dialogs.value = response.data.data.map((dialog: any) => {
        const processedDialog = {
          dialogId: dialog.dialog_id,
          name: dialog.name,
          agent: dialog.name, // 使用智能体名称作为显示
          createTime: dialog.create_time || dialog.update_time || new Date().toISOString(),
          logo: dialog.logo_url || 'https://via.placeholder.com/40x40/3b82f6/ffffff?text=AI'
        }
        console.log('处理后的对话数据:', processedDialog)
        return processedDialog
      })
      console.log('对话列表获取成功:', dialogs.value)

      // 如果会话列表不为空且当前路由是默认页面，立即自动打开第一个会话
      if (dialogs.value.length > 0 && router.currentRoute.value.name === 'defaultPage') {
        const firstDialog = dialogs.value[0]
        console.log('立即自动打开第一个会话:', firstDialog.dialogId, firstDialog.name)

        // 设置选中的会话
        selectedDialog.value = firstDialog.dialogId

        // 设置聊天store的状态
        historyChatStore.dialogId = firstDialog.dialogId
        historyChatStore.name = firstDialog.name
        historyChatStore.logo = firstDialog.logo

        // 立即跳转到聊天页面
        router.push({
          path: '/conversation/chatPage',
          query: {
            dialog_id: firstDialog.dialogId
          }
        })
      }
    } else {
      HMessage.error(`获取对话列表失败: ${response.data.status_message}`)
    }
  } catch (error) {
    console.error('获取对话列表出错:', error)
    HMessage.error('获取对话列表失败，请检查网络连接')
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  console.log('会话页面已加载')
  // 如果当前是会话主页面，先获取对话列表检查是否需要跳转
  if (router.currentRoute.value.path === '/conversation') {
    await fetchDialogs()
    // 如果没有自动跳转（说明没有会话），再获取智能体列表
    if (router.currentRoute.value.name === 'defaultPage') {
      await fetchAgents()
    }
  } else {
    // 如果是其他子页面，正常加载
    await Promise.all([fetchAgents(), fetchDialogs()])
  }
  // HMessage.success('页面加载成功')
})

// 创建新会话
const createDialog = async () => {
  if (!selectedAgent.value) {
    HMessage.warning('请选择一个智能体')
    return
  }

  // 支持多种ID字段查找
  const agent = agents.value.find(a => {
    const agentIdMatch = a.agent_id === selectedAgent.value || String(a.agent_id) === String(selectedAgent.value)
    const idMatch = (a as any).id === selectedAgent.value || String((a as any).id) === String(selectedAgent.value)
    return agentIdMatch || idMatch
  })

  if (agent) {
    try {
      const dialogData: DialogCreateType = {
        name: `与${agent.name}的对话`,
        agent_id: (agent as any).id || agent.agent_id, // 优先使用 id 字段
        agent_type: "Agent" // 默认为普通Agent类型
      }

      console.log('创建会话数据:', dialogData)
      console.log('发送到后端的数据:', {
        name: dialogData.name,
        agent_id: dialogData.agent_id,
        agent_type: dialogData.agent_type
      })
      const response = await createDialogAPI(dialogData)
      if (response.data.status_code === 200) {
        HMessage.success('会话创建成功')

        // 获取新创建的会话ID
        const dialogId = response.data.data.dialog_id
        console.log('获取到的 dialogId:', dialogId)
        console.log('完整的 response.data.data:', response.data.data)

        // 重新获取对话列表
        await fetchDialogs()
        showCreateDialog.value = false
        selectedAgent.value = ''
        agentSearchKeyword.value = ''

        // 跳转到新创建的会话页面
        if (dialogId) {
          console.log('准备跳转到会话页面，dialogId:', dialogId)

          // 更新选中的会话状态
          selectedDialog.value = dialogId

          // 设置聊天store的状态
          historyChatStore.dialogId = dialogId
          historyChatStore.name = dialogData.name
          historyChatStore.logo = agent.logo_url || 'https://via.placeholder.com/40x40/3b82f6/ffffff?text=AI'

          router.push({
            path: '/conversation/chatPage',
            query: {
              dialog_id: dialogId
            }
          })
        } else {
          console.error('dialogId 为空，无法跳转')
        }
      } else {
        HMessage.error(`创建会话失败: ${response.data.status_message}`)
      }
    } catch (error) {
      console.error('创建会话出错:', error)
      HMessage.error('创建会话失败，请检查网络连接')
    }
  } else {
    HMessage.error('未找到选中的智能体')
  }
}

// 删除会话
const deleteDialog = async (dialogId: string) => {
  console.log('删除会话被调用，dialogId:', dialogId)
  try {
    const response = await deleteDialogAPI(dialogId)
    if (response.data.status_code === 200) {
      HMessage.success('会话删除成功')
      // 重新获取对话列表
      await fetchDialogs()
      if (selectedDialog.value === dialogId) {
        selectedDialog.value = ''
      }
    } else {
      HMessage.error(`删除会话失败: ${response.data.status_message}`)
    }
  } catch (error) {
    console.error('删除会话出错:', error)
    HMessage.error('删除会话失败，请检查网络连接')
  }
}

// 选择会话
const selectDialog = (dialogId: string) => {
  const dialog = dialogs.value.find(d => d.dialogId === dialogId)
  if (!dialog) {
    console.error('未找到会话:', dialogId)
    return
  }

  console.log('选择会话:', dialogId, dialog.name)
  selectedDialog.value = dialogId

  // 设置聊天store的状态
  historyChatStore.dialogId = dialogId
  historyChatStore.name = dialog.name
  historyChatStore.logo = dialog.logo

  // 跳转到聊天页面
  router.push({
    path: '/conversation/chatPage',
    query: {
      dialog_id: dialogId
    }
  })
}

// 打开创建对话框
const openCreateDialog = async () => {
  showCreateDialog.value = true
  selectedAgent.value = ''
  agentSearchKeyword.value = ''

  // 如果智能体列表为空，重新获取
  if (agents.value.length === 0) {
    await fetchAgents()
  }

  // HMessage.info('正在打开创建会话对话框...')
}

// 选择智能体
const selectAgent = (agentId: string) => {
  console.log('选择智能体:', agentId)
  console.log('当前智能体列表:', agents.value.map(a => ({
    agent_id: a.agent_id,
    id: (a as any).id,
    name: a.name
  })))

  // 支持多种ID字段
  const agent = agents.value.find(a => {
    const agentIdMatch = a.agent_id === agentId || String(a.agent_id) === String(agentId)
    const idMatch = (a as any).id === agentId || String((a as any).id) === String(agentId)
    return agentIdMatch || idMatch
  })

  if (agent) {
    // 优先使用 id 字段作为选中值
    selectedAgent.value = (agent as any).id || agent.agent_id
    console.log('选中智能体:', agent.name, 'ID:', selectedAgent.value)
  } else {
    console.error('未找到智能体:', agentId)
  }
}

// 关闭创建对话框
const closeCreateDialog = () => {
  showCreateDialog.value = false
  selectedAgent.value = ''
  agentSearchKeyword.value = ''
}
</script>

<template>
  <!-- Desktop -->
  <div v-if="!isMobile" class="conversation-main page">
    <!-- 左侧边栏 -->
    <div class="sidebar">
      <!-- 新建会话按钮 -->
      <div class="create-section">
        <button
          @click="openCreateDialog"
          class="create-btn-native"
        >
          <div class="btn-content">
            <span class="icon">+</span>
            <span>新建会话</span>
          </div>
        </button>
      </div>



      <!-- 会话列表标题 -->
      <div class="list-header">
        <span class="title">会话列表</span>
        <span class="count">({{ filteredDialogs.length }})</span>
      </div>

      <!-- 会话列表 -->
      <div class="dialog-list">
        <!-- 加载状态 -->
        <div v-if="loading" class="loading-state">
          <div class="loading-icon">
            <Icon icon="mdi:loading" :width="24" :height="24" class="spinning" />
          </div>
          <div class="loading-text">正在加载会话列表...</div>
        </div>
        <!-- 空状态 -->
        <div v-else-if="filteredDialogs.length === 0" class="empty-state">
          <div class="empty-icon">
            <Icon icon="mdi:message-text" :width="24" :height="24" />
          </div>
          <div class="empty-text">
            {{ searchKeyword ? '没有找到相关会话' : '暂无会话记录' }}
          </div>
          <div v-if="!searchKeyword" class="empty-hint">
            点击上方按钮开始新的对话
          </div>
        </div>
        <!-- 用 histortCard 渲染会话卡片 -->
        <histortCard
          v-for="dialog in filteredDialogs"
          :key="dialog.dialogId"
          :item="dialog"
          :class="{ active: selectedDialog === dialog.dialogId }"
          @select="selectDialog(dialog.dialogId)"
          @delete="deleteDialog(dialog.dialogId)"
        />
      </div>
    </div>

    <!-- 右侧内容区域，改为路由驱动 -->
    <div class="content">
      <router-view />
    </div>

  </div>

  <!-- Mobile -->
  <div v-else class="conv-mobile">
    <!-- Dialog list (when no dialog selected) -->
    <div v-if="!selectedDialog" class="cm-list">
      <div class="cm-list__header">
        <button class="cm-create-btn" @click="openCreateDialog">+ 新建会话</button>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="cm-loading">加载中...</div>

      <!-- Empty -->
      <div v-else-if="filteredDialogs.length === 0" class="cm-empty">
        <p>暂无会话记录</p>
      </div>

      <!-- Dialog items -->
      <div v-else class="cm-items">
        <div
          v-for="dialog in filteredDialogs"
          :key="dialog.dialogId"
          class="cm-item"
          @click="selectDialog(dialog.dialogId)"
        >
          <div class="cm-item__avatar">
            <img :src="dialog.logo" alt="" />
          </div>
          <div class="cm-item__content">
            <h3 class="cm-item__name">{{ dialog.name }}</h3>
            <p class="cm-item__time">{{ formatTime(dialog.createTime) }}</p>
          </div>
          <button class="cm-item__delete" @click.stop="deleteDialog(dialog.dialogId)">&times;</button>
        </div>
      </div>
    </div>

    <!-- Chat content (when dialog selected) -->
    <div v-else class="cm-chat">
      <div class="cm-chat__back" @click="selectedDialog = ''">&larr; 返回列表</div>
      <div class="cm-chat__content">
        <router-view />
      </div>
    </div>
  </div>

  <!-- 创建会话对话框 (shared desktop/mobile) -->
  <div v-if="showCreateDialog" class="create-dialog-overlay" @click="closeCreateDialog">
    <div class="create-dialog" @click.stop>
      <div class="dialog-body">
        <!-- 智能体搜索框 -->
        <div class="search-section">
          <div class="search-wrapper">
            <Icon icon="mdi:magnify" :width="18" :height="18" class="search-icon" />
            <input
              v-model="agentSearchKeyword"
              placeholder="搜索智能体名称或描述..."
              class="search-input"
            />
            <div v-if="agentSearchKeyword" class="clear-btn" @click="agentSearchKeyword = ''">
              <Icon icon="mdi:close" :width="16" :height="16" />
            </div>
          </div>
        </div>

        <!-- 智能体列表 -->
        <div class="agents-section">
          <div class="section-header">
            <div class="header-left">
              <Icon icon="mdi:robot" :width="20" :height="20" class="section-icon" />
              <span class="title">可用智能体</span>
              <span class="count">{{ filteredAgents.length }}</span>
            </div>
          </div>

          <!-- 加载状态 -->
          <div v-if="agentsLoading" class="loading-state">
            <div class="loading-spinner">
              <svg class="spinner" width="40" height="40" viewBox="0 0 40 40">
                <circle cx="20" cy="20" r="16" stroke="currentColor" stroke-width="4" fill="none" opacity="0.2"/>
                <circle cx="20" cy="20" r="16" stroke="currentColor" stroke-width="4" fill="none" stroke-dasharray="80" stroke-dashoffset="60"/>
              </svg>
            </div>
            <div class="loading-text">正在加载智能体列表...</div>
          </div>

          <!-- 空状态 -->
          <div v-else-if="filteredAgents.length === 0" class="empty-state">
            <div class="empty-illustration">
              <svg width="80" height="80" viewBox="0 0 80 80" fill="none">
                <circle cx="40" cy="40" r="35" fill="var(--harmony-comp-background-tertiary)"/>
                <rect x="25" y="25" width="30" height="30" rx="6" stroke="#9ca3af" stroke-width="2"/>
                <circle cx="33" cy="35" r="2" fill="#9ca3af"/>
                <circle cx="47" cy="35" r="2" fill="#9ca3af"/>
                <path d="M32 45C32 45 35 48 40 48C45 48 48 45 48 45" stroke="#9ca3af" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </div>
            <div class="empty-text">
              {{ agentSearchKeyword ? '没有找到相关智能体' : '暂无可用智能体' }}
            </div>
            <div v-if="!agentSearchKeyword" class="empty-hint">
              请联系管理员添加智能体
            </div>
          </div>

          <div v-else class="agents-grid">
            <div
              v-for="agent in filteredAgents"
              :key="(agent as any).id || agent.agent_id"
              :class="['agent-card', selectedAgent === ((agent as any).id || agent.agent_id) ? 'active' : '']"
              @click="selectAgent((agent as any).id || agent.agent_id)"
            >
              <div class="card-inner">
                <div class="agent-avatar">
                  <img :src="agent.logo_url" alt="" />
                  <div v-if="selectedAgent === ((agent as any).id || agent.agent_id)" class="avatar-badge">
                    <Icon icon="mdi:check-circle" :width="20" :height="20" />
                  </div>
                </div>
                <div class="agent-info">
                  <div class="agent-name">{{ agent.name }}</div>
                  <div class="agent-description">{{ agent.description }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="dialog-footer">
        <div class="footer-info">
          <Icon icon="mdi:information" :width="16" :height="16" class="info-icon" />
          <span v-if="selectedAgent">
            已选择: {{ agents.find(a => (a.agent_id === selectedAgent || (a as any).id === selectedAgent))?.name || '未知' }}
          </span>
          <span v-else>请选择一个智能体</span>
        </div>
        <div class="footer-actions">
          <button @click="closeCreateDialog" class="btn-cancel">
            <span>取消</span>
          </button>
          <button
            @click="createDialog"
            :disabled="!selectedAgent"
            class="btn-confirm"
          >
            <Icon icon="mdi:plus" :width="16" :height="16" />
            <span>创建会话</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@use '../../styles/breakpoints.scss' as *;

.conversation-main {
  display: flex;
  height: calc(100vh - 60px);
  background: transparent;

  .sidebar {
    display: flex;
    flex-direction: column;
    height: 100%;
    width: 280px;
    background: transparent;
    border-right: 1px solid var(--harmony-comp-divider);
    box-shadow: var(--harmony-shadow-card);

    .create-section {
      padding: 20px 16px 16px;
      border-bottom: 1px solid var(--harmony-comp-divider);

      .create-btn-native {
        width: 100%;
        height: 48px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--harmony-brand);
        color: var(--harmony-comp-background-primary);
        border: none;
        border-radius: var(--harmony-corner-radius-level6);
        font-size: var(--harmony-font-size-body-m);
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;

        &:hover {
          background: var(--harmony-interactive-hover);
          transform: translateY(-1px);
          box-shadow: var(--harmony-shadow-card-hover);
        }

        &:active {
        }

        .btn-content {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;

          .icon {
            font-size: var(--harmony-font-size-subtitle-l);
            font-weight: bold;
          }
        }
      }
    }

    .search-section {
      padding: 16px;
      border-bottom: 1px solid var(--harmony-comp-divider);

      .search-input-wrapper {
        position: relative;
        display: flex;
        align-items: center;

        .search-icon {
          position: absolute;
          left: 12px;
          color: var(--harmony-font-tertiary);
          font-size: var(--harmony-font-size-body-m);
          z-index: var(--z-dropdown);
        }

        .search-input {
          width: 100%;
          padding: 8px 12px 8px 36px;
          background: var(--harmony-comp-background-secondary);
          border: 1px solid var(--harmony-comp-divider);
          border-radius: var(--harmony-corner-radius-level4);
          font-size: var(--harmony-font-size-body-m);
          transition: all 0.2s ease;

          &:focus {
            border-color: var(--harmony-brand);
            background: var(--harmony-comp-background-primary);
            box-shadow: 0 0 0 2px var(--harmony-comp-emphasize-tertiary);
          }

          &::placeholder {
            color: var(--harmony-font-tertiary);
          }
        }
      }
    }

    .list-header {
      display: flex;
      align-items: center;
      gap: 4px;
      padding: 16px 16px 8px;

      .title {
        font-size: var(--harmony-font-size-body-m);
        font-weight: 600;
        color: var(--harmony-font-primary);
      }

      .count {
        font-size: var(--harmony-font-size-body-s);
        color: var(--harmony-font-tertiary);
      }
    }

    .dialog-list {
      flex: 1;
      padding: 0 8px;
      overflow-y: auto;

      .loading-state,
      .empty-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 200px;
      }

      .loading-state {
        color: var(--harmony-brand);

        .loading-icon {
          width: 32px;
          height: 32px;
          margin-bottom: 14px;
          color: var(--harmony-brand);
          animation: h-spin 0.8s linear infinite;

          svg {
            width: 100%;
            height: 100%;
          }
        }

        .loading-text {
          font-size: var(--harmony-font-size-body-m);
          color: var(--harmony-font-secondary);
        }
      }

      .empty-state {
        color: var(--harmony-font-tertiary);

        .empty-icon {
          font-size: 48px;
          margin-bottom: 16px;
        }

        .empty-text {
          font-size: var(--harmony-font-size-body-m);
          margin-bottom: 8px;
        }

        .empty-hint {
          font-size: var(--harmony-font-size-body-s);
          color: var(--harmony-font-tertiary);
        }
      }

      .dialog-card {
        position: relative;
        min-height: 80px;
        padding: var(--harmony-padding-level8);
        margin-bottom: var(--harmony-padding-level4);
        background: var(--harmony-comp-background-primary);
        border: 1px solid var(--harmony-comp-divider);
        border-radius: var(--harmony-corner-radius-level8);
        cursor: pointer;
        transition: all 0.3s ease;

        &:hover {
          border-color: var(--harmony-brand);
          transform: translateY(-2px);
          box-shadow: var(--harmony-shadow-card-hover);

          .delete-btn {
          }
        }

        &.active {
          border-color: var(--harmony-brand);
          background: var(--harmony-comp-background-secondary);
        }

        .avatar {
          position: absolute;
          top: 16px;
          left: 16px;
          width: 40px;
          height: 40px;
          border-radius: var(--harmony-corner-radius-level4);
          overflow: hidden;

          img {
            width: 100%;
            height: 100%;
            object-fit: cover;
          }
        }

        .title {
          position: absolute;
          top: 16px;
          left: 68px;
          right: 60px;
          font-size: var(--harmony-font-size-body-m);
          font-weight: 600;
          color: var(--harmony-font-primary);
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .delete-btn {
          position: absolute;
          top: 16px;
          right: 16px;
          width: 32px;
          height: 32px;
          padding: 4px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: var(--harmony-comp-background-primary);
          border: 1px solid var(--harmony-comp-divider);
          border-radius: var(--harmony-corner-radius-level4);
          font-size: var(--harmony-font-size-body-m);
          cursor: pointer;
          user-select: none;
          pointer-events: auto;
          opacity: 0;
          z-index: var(--z-dropdown);
          transition: all 0.2s ease;

          &:hover {
            background: var(--harmony-comp-background-secondary);
            color: var(--harmony-brand);
            border-color: var(--harmony-brand);
          }

          &:active {
            transform: scale(0.95);
          }
        }

        .time {
          position: absolute;
          bottom: 8px;
          right: 16px;
          font-size: var(--harmony-font-size-caption-l);
          color: var(--harmony-font-tertiary);
        }
      }
    }
  }

  .content {
    flex: 1;
    background: transparent;
    margin: 0;
    overflow: hidden;

    .welcome-content {
      flex: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100%;
      text-align: center;
      color: var(--harmony-font-tertiary);

      .welcome-icon {
        margin-bottom: 24px;

        .icon {
          font-size: 48px;
          color: var(--harmony-brand);
        }
      }

      h2 {
        font-size: 1.5rem;
        margin: 0 0 12px;
        color: var(--harmony-font-primary);
      }

      p {
        font-size: 1rem;
        margin: 0;
      }
    }

    .chat-content {
      flex: 1;
      display: flex;
      flex-direction: column;

      .chat-header {
        padding: 20px;
        border-bottom: 1px solid var(--harmony-comp-divider);
        background: var(--harmony-comp-background-secondary);

        h3 {
          margin: 0;
          color: var(--harmony-font-primary);
        }
      }

      .chat-messages {
        flex: 1;
        padding: 20px;

        .message {
          padding: 12px 16px;
          margin-bottom: 12px;
          border-radius: var(--harmony-corner-radius-level6);

          &.system {
            background: var(--harmony-comp-background-secondary);
            color: var(--harmony-font-secondary);
          }
        }
      }
    }
  }
}

.dialog-content {
  .search-section {
    margin-bottom: 20px;
  }

  .agents-section {
    .section-header {
      display: flex;
      align-items: center;
      gap: 4px;
      margin-bottom: 16px;

      .title {
        font-size: var(--harmony-font-size-body-m);
        font-weight: 600;
        color: var(--harmony-font-primary);
      }

      .count {
        font-size: var(--harmony-font-size-body-m);
        color: var(--harmony-font-secondary);
      }
    }

    .empty-state {
      padding: 40px 20px;
      text-align: center;
      color: var(--harmony-font-tertiary);

      .empty-icon {
        font-size: 48px;
        margin-bottom: 16px;
      }

      .empty-text {
        font-size: var(--harmony-font-size-body-m);
        margin-bottom: 8px;
      }

      .empty-hint {
        font-size: var(--harmony-font-size-body-s);
        color: var(--harmony-font-tertiary);
      }
    }

    .agents-grid {
      display: grid;
      gap: 12px;
      max-height: 400px;
      overflow-y: auto;

      .agent-card {
        position: relative;
        display: flex;
        align-items: center;
        gap: 12px;
        padding: var(--harmony-padding-level8);
        border: 2px solid transparent;
        border-radius: var(--harmony-corner-radius-level6);
        cursor: pointer;
        transition: all 0.2s ease;

        &:hover {
          background: var(--harmony-comp-background-secondary);
          border-color: var(--harmony-comp-divider);
        }

        &.active {
          border-color: var(--harmony-brand);
          background: var(--harmony-comp-background-secondary);
        }

        .agent-avatar {
          width: 48px;
          height: 48px;
          flex-shrink: 0;
          border-radius: var(--harmony-corner-radius-level4);
          overflow: hidden;

          img {
            width: 100%;
            height: 100%;
            object-fit: cover;
          }
        }

        .agent-info {
          flex: 1;

          .agent-name {
            margin-bottom: 4px;
            font-size: var(--harmony-font-size-body-m);
            font-weight: 600;
            color: var(--harmony-font-primary);
          }

          .agent-description {
            font-size: var(--harmony-font-size-body-m);
            color: var(--harmony-font-secondary);
            line-height: 1.4;
          }
        }

        .agent-status {
          flex-shrink: 0;

          .selected-icon {
            width: 24px;
            height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: var(--harmony-comp-background-secondary);
            border-radius: 50%;
          }
        }
      }
    }
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

@include mobile {
  .conversation-main {
    flex-direction: column;

    .sidebar {
      width: 100%;
      height: auto;
      max-height: 300px;
    }

    .content {
      flex: 1;
      margin: 0;
    }
  }
}

.create-dialog-overlay {
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--harmony-overlay-heavy);
  z-index: var(--z-dialog);
  animation: harmony-fade-in 0.2s ease;
}

.create-dialog {
  display: flex;
  flex-direction: column;
  width: 85vw;
  max-width: 1200px;
  height: 75vh;
  max-height: 675px;
  overflow: hidden;
  background: var(--harmony-comp-background-primary);
  border-radius: var(--harmony-corner-radius-level12);
  box-shadow: var(--harmony-shadow-card-hover);
  animation: harmony-slide-up 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);

  .dialog-body {
    flex: 1;
    padding: 40px;
    overflow-y: auto;
    background: var(--harmony-comp-background-secondary);
    border-radius: var(--harmony-corner-radius-level12) 24px 0 0;

    .search-section {
      margin-bottom: 28px;

      .search-wrapper {
        position: relative;
        display: flex;
        align-items: center;

        .search-icon {
          position: absolute;
          left: 18px;
          color: var(--harmony-font-tertiary);
          pointer-events: none;
          z-index: var(--z-dropdown);
        }

        .search-input {
          width: 100%;
          padding: 16px 56px 16px 52px;
          background: var(--harmony-comp-background-primary);
          border: 1px solid var(--harmony-comp-divider);
          border-radius: var(--harmony-corner-radius-level6);
          color: var(--harmony-font-primary);
          font-size: var(--harmony-font-size-subtitle-s);
          font-weight: 500;
          transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);

          &:focus {
            border-color: var(--harmony-brand);
            background: var(--harmony-comp-background-primary);
            box-shadow: 0 0 0 4px var(--harmony-comp-emphasize-tertiary);
          }

          &::placeholder {
            color: var(--harmony-font-tertiary);
            font-weight: 400;
          }
        }

        .clear-btn {
          position: absolute;
          right: 14px;
          padding: 6px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: var(--harmony-font-tertiary);
          border-radius: var(--harmony-corner-radius-level6);
          cursor: pointer;
          transition: all 0.2s ease;

          &:hover {
            color: var(--harmony-font-primary);
            background: var(--harmony-comp-background-secondary);
          }
        }
      }
    }

    .agents-section {
      .section-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 20px;

        .header-left {
          display: flex;
          align-items: center;
          gap: 12px;

          .section-icon {
            color: var(--harmony-font-secondary);
          }

          .title {
            font-size: var(--harmony-font-size-subtitle-l);
            font-weight: 700;
            letter-spacing: -0.01em;
            color: var(--harmony-font-primary);
          }

          .count {
            padding: 5px 12px;
            border: 1px solid var(--harmony-comp-divider);
            border-radius: var(--harmony-corner-radius-level10);
            background: var(--harmony-comp-background-primary);
            font-size: var(--harmony-font-size-body-m);
            font-weight: 600;
            color: var(--harmony-font-secondary);
          }
        }
      }

      .loading-state,
      .empty-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 80px 20px;
      }

      .loading-state {
        .loading-spinner {
          margin-bottom: 24px;

          .spinner {
            color: var(--harmony-brand);
            animation: h-spin 1s linear infinite;
          }
        }

        .loading-text {
          font-size: var(--harmony-font-size-subtitle-s);
          font-weight: 600;
          color: var(--harmony-font-secondary);
        }
      }

      .empty-state {
        .empty-illustration {
          margin-bottom: 24px;
          animation: float 3s ease-in-out infinite;
        }

        .empty-text {
          margin-bottom: 10px;
          font-size: var(--harmony-font-size-body-m);
          font-weight: 600;
          color: var(--harmony-font-primary);
        }

        .empty-hint {
          font-size: var(--harmony-font-size-body-m);
          color: var(--harmony-font-tertiary);
        }
      }

      .agents-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
        gap: 20px;
        max-height: 450px;
        padding: 6px;
        overflow-y: auto;

        .agent-card {
          position: relative;
          display: flex;
          flex-direction: column;
          aspect-ratio: 1;
          overflow: hidden;
          background: var(--harmony-comp-background-primary);
          border: 1px solid var(--harmony-comp-divider);
          border-radius: var(--harmony-corner-radius-level8);
          cursor: pointer;
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

          &::before {
            content: '';
            position: absolute;
            inset: 0;
            background: var(--harmony-comp-background-secondary);
            opacity: 0;
            transition: opacity 0.3s ease;
          }

          &:hover,
          &.active {
            border-color: var(--harmony-brand);
            background: var(--harmony-comp-background-secondary);
            transform: translateY(-6px) scale(1.02);
            box-shadow: var(--harmony-shadow-card-hover);

            &::before {
            }
          }

          &.active {
            .agent-avatar {
              border-color: var(--harmony-brand);
              box-shadow: var(--harmony-shadow-card-hover);
            }

            .agent-name {
              color: var(--harmony-font-primary);
            }
          }

          .card-inner {
            position: relative;
            display: flex;
            flex-direction: column;
            align-items: center;
            height: 100%;
            padding: 24px 18px;
            text-align: center;
            z-index: var(--z-dropdown);
          }

          .agent-avatar {
            position: relative;
            width: 80px;
            height: 80px;
            margin-bottom: 14px;
            flex-shrink: 0;
            overflow: hidden;
            border: 2px solid var(--harmony-comp-divider);
            border-radius: var(--harmony-corner-radius-level8);
            box-shadow: var(--harmony-shadow-card);
            transition: all 0.3s ease;

            img {
              width: 100%;
              height: 100%;
              object-fit: cover;
            }

            .avatar-badge {
              position: absolute;
              right: -8px;
              bottom: -8px;
              width: 32px;
              height: 32px;
              display: flex;
              align-items: center;
              justify-content: center;
              background: var(--harmony-comp-background-primary);
              border: 2px solid var(--harmony-brand);
              border-radius: 50%;
              box-shadow: var(--harmony-shadow-card);
              animation: harmony-scale-in 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
            }
          }

          .agent-info {
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            width: 100%;

            .agent-name {
              margin-bottom: 8px;
              font-size: var(--harmony-font-size-body-m);
              font-weight: 700;
              line-height: 1.3;
              letter-spacing: -0.01em;
              color: var(--harmony-font-primary);
              text-align: center;
              overflow: hidden;
              text-overflow: ellipsis;
              white-space: nowrap;
            }

            .agent-description {
              font-size: var(--harmony-font-size-subtitle-s);
              font-weight: 500;
              line-height: 1.5;
              color: var(--harmony-font-secondary);
              text-align: left;
              display: -webkit-box;
              -webkit-line-clamp: 2;
              -webkit-box-orient: vertical;
              overflow: hidden;
            }
          }
        }
      }
    }
  }

  .dialog-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
    padding: 24px 40px;
    border-top: 1px solid var(--harmony-comp-divider);
    background: var(--harmony-comp-background-primary);

    .footer-info {
      display: flex;
      align-items: center;
      gap: 10px;
      flex: 1;
      font-size: var(--harmony-font-size-body-m);
      color: var(--harmony-font-secondary);

      .info-icon {
        flex-shrink: 0;
        color: var(--harmony-font-tertiary);
      }

      span {
        font-weight: 600;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
    }

    .footer-actions {
      display: flex;
      gap: 14px;
    }

    .btn-cancel,
    .btn-confirm {
      padding: 10px 18px;
      display: flex;
      align-items: center;
      border: none;
      border-radius: var(--harmony-corner-radius-level6);
      font-size: var(--harmony-font-size-subtitle-s);
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .btn-cancel {
      gap: 8px;
      background: var(--harmony-comp-background-secondary);
      color: var(--harmony-font-primary);

      &:hover {
        background: var(--harmony-comp-divider);
        transform: translateY(-2px);
        box-shadow: var(--harmony-shadow-card);
      }

      &:active {
      }
    }

    .btn-confirm {
      gap: 10px;
      background: var(--harmony-brand);
      color: var(--harmony-comp-background-primary);
      box-shadow: var(--harmony-shadow-card);

      svg {
        transition: transform 0.2s ease;
      }

      &:hover:not(:disabled) {
        background: var(--harmony-interactive-hover);
        transform: translateY(-2px);
        box-shadow: var(--harmony-shadow-card-hover);

        svg {
          transform: rotate(90deg);
        }
      }

      &:active:not(:disabled) {
      }

      &:disabled {
        background: var(--harmony-font-tertiary);
        cursor: not-allowed;
        opacity: 0.6;
      }
    }
  }
}

@keyframes float {
  0%, 100% {
  }
}

.conv-mobile {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.cm-list {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: var(--harmony-card-gap-mobile, 12px);
  padding-top: var(--harmony-padding-level8, 16px);

  &__header {
    display: flex;
    justify-content: flex-end;
  }
}

.cm-create-btn {
  height: var(--harmony-control-height-40, 40px);
  padding: 0 var(--harmony-padding-level8, 16px);
  background: var(--harmony-brand);
  color: var(--harmony-comp-common-contrary, white);
  border: none;
  border-radius: var(--harmony-corner-radius-level6, 12px);
  font-size: var(--harmony-font-size-body-m);
  font-weight: 500;
  cursor: pointer;
}

.cm-loading, .cm-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--harmony-padding-level16, 32px) 0;
  font-size: var(--harmony-font-size-body-m);
  color: var(--harmony-font-tertiary);
}

.cm-items {
  display: flex;
  flex-direction: column;
  gap: var(--harmony-card-gap-mobile, 12px);
}

.cm-item {
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

  &__avatar {
    width: var(--harmony-control-height-40, 40px);
    height: var(--harmony-control-height-40, 40px);
    flex-shrink: 0;
    border-radius: var(--harmony-corner-radius-level6, 12px);
    overflow: hidden;
    background: var(--harmony-comp-background-secondary);

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  }

  &__content {
    flex: 1;
    min-width: 0;
  }

  &__name {
    margin: 0 0 var(--harmony-padding-level1, 2px);
    font-size: var(--harmony-font-size-body-m);
    font-weight: 600;
    color: var(--harmony-font-primary);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  &__time {
    margin: 0;
    font-size: var(--harmony-font-size-body-s);
    color: var(--harmony-font-tertiary);
  }

  &__delete {
    width: var(--harmony-control-height-36, 36px);
    height: var(--harmony-control-height-36, 36px);
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background: transparent;
    border: none;
    border-radius: var(--harmony-corner-radius-level4, 8px);
    color: var(--harmony-font-tertiary);
    font-size: var(--harmony-font-size-title-s, 20px);
    cursor: pointer;

    &:active {
      background: var(--harmony-interactive-pressed);
      color: var(--harmony-warning);
    }
  }
}

.cm-chat {
  display: flex;
  flex-direction: column;
  height: 100%;

  &__back {
    padding: var(--harmony-padding-level4, 8px) 0;
    flex-shrink: 0;
    font-size: var(--harmony-font-size-body-m);
    color: var(--harmony-brand);
    cursor: pointer;
  }

  &__content {
    flex: 1;
    overflow: hidden;
  }
}
</style>

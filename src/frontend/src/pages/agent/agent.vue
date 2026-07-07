<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { HButton, HInput, HMessage } from '@/components/ui'
import {
  getAgentsAPI,
  deleteAgentAPI,
  searchAgentsAPI,
} from '../../apis/agent'

const router = useRouter()
const agents = ref<any[]>([])
const loading = ref(false)
const searchLoading = ref(false)
const searchKeyword = ref('')
const showConfirmDialog = ref(false)
const agentToDelete = ref<any | null>(null)

const fetchAgents = async () => {
  loading.value = true
  try {
    const response = await getAgentsAPI()
    const responseCode = response.data.status_code
    if (responseCode === 200) {
      agents.value = response.data.data || []
    } else {
      HMessage.error(response.data.status_message || '获取智能体列表失败')
    }
  } catch (error: any) {
    if (error.response) {
      HMessage.error(`请求失败: ${error.response.status}`)
    } else if (error.request) {
      HMessage.error('网络错误：无法连接到服务器')
    } else {
      HMessage.error('获取智能体列表失败：' + error.message)
    }
  } finally {
    loading.value = false
  }
}

const searchAgents = async () => {
  if (!searchKeyword.value.trim()) {
    await fetchAgents()
    return
  }
  searchLoading.value = true
  try {
    const response = await searchAgentsAPI({ name: searchKeyword.value.trim() })
    if (response.data.status_code === 200) {
      agents.value = response.data.data || []
    } else {
      HMessage.error(response.data.status_message || '搜索失败')
    }
  } catch (error: any) {
    HMessage.error('搜索智能体失败')
  } finally {
    searchLoading.value = false
  }
}

const clearSearch = () => {
  searchKeyword.value = ''
  fetchAgents()
}

const createAgent = () => {
  router.push('/agent/editor')
}

const editAgent = (agent: any) => {
  if (agent.is_custom === false) {
    HMessage.warning(`"${agent.name}" 是官方智能体，无法编辑。`)
    return
  }
  router.push({
    path: '/agent/editor',
    query: { id: agent.agent_id || agent.id }
  })
}

const handleCardClick = (agent: any) => {
  if (agent.is_custom === false) {
    HMessage.warning(`"${agent.name}" 是官方智能体，无法编辑。`)
    return
  }
  editAgent(agent)
}

const deleteAgent = (agent: any) => {
  if (agent.is_custom === false) {
    HMessage.error('官方智能体不能删除')
    return
  }
  agentToDelete.value = agent
  showConfirmDialog.value = true
}

const confirmDelete = async () => {
  if (!agentToDelete.value) return
  try {
    const response = await deleteAgentAPI({ agent_id: agentToDelete.value.agent_id || agentToDelete.value.id })
    if (response.data.status_code === 200) {
      HMessage.success('删除成功')
      await fetchAgents()
    } else {
      HMessage.error(response.data.status_message || '删除失败')
    }
  } catch (error: any) {
    HMessage.error('删除失败，请稍后重试')
  } finally {
    showConfirmDialog.value = false
    agentToDelete.value = null
  }
}

const cancelDelete = () => {
  showConfirmDialog.value = false
  agentToDelete.value = null
}

const handleImageError = (event: Event) => {
  const target = event.target as HTMLImageElement
  if (target) {
    target.style.display = 'none'
  }
}

const getAgentMeta = (agent: any) => ({
  tools: agent.tool_ids?.length || 0,
  knowledge: agent.knowledge_ids?.length || 0,
  mcp: agent.mcp_ids?.length || 0,
  skills: agent.agent_skill_ids?.length || 0
})

onMounted(() => {
  fetchAgents()
})
</script>

<template>
  <div class="agent-page">
    <!-- ===== 页面头部 ===== -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <rect x="3" y="8" width="18" height="12" rx="2" stroke="currentColor" stroke-width="1.5"/>
            <circle cx="9" cy="14" r="1.5" fill="currentColor"/>
            <circle cx="15" cy="14" r="1.5" fill="currentColor"/>
            <path d="M12 3v5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            <circle cx="12" cy="2.5" r="1.5" fill="currentColor"/>
            <path d="M3 14H1.5M22.5 14H21M12 20v2.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
        </div>
        <div class="header-text">
          <h1 class="header-title">智能体管理</h1>
          <p class="header-desc">创建和管理您的智能体</p>
        </div>
      </div>

      <div class="header-right">
        <div class="search-box">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" class="search-icon">
            <circle cx="6" cy="6" r="4.5" stroke="currentColor" stroke-width="1.3"/>
            <path d="M9.5 9.5L13 13" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
          </svg>
          <input
            v-model="searchKeyword"
            class="search-input"
            placeholder="搜索智能体名称..."
            @keyup.enter="searchAgents"
          />
          <button v-if="searchKeyword" class="search-clear" @click="clearSearch" title="清空">
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
              <path d="M3 3L9 9M9 3L3 9" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
          </button>
        </div>

        <button class="btn-refresh" @click="fetchAgents" :disabled="loading" title="刷新">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" :class="{ spinning: loading }">
            <path d="M13.5 5.5H8V0" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M2.5 10.5H8V16" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M13 4.5C11.8 2.5 9.6 1.2 7 1.2C2.9 1.2 -0.3 4.5 0.5 8.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            <path d="M3 11.5C4.2 13.5 6.4 14.8 9 14.8C13.1 14.8 16.3 11.5 15.5 7.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
        </button>

        <button class="btn-primary" @click="createAgent">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <path d="M7 3V11M3 7H11" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
          </svg>
          <span>创建智能体</span>
        </button>
      </div>
    </div>

    <!-- ===== 智能体列表 ===== -->
    <div class="agent-list">
      <!-- 加载状态 -->
      <div v-if="loading && agents.length === 0" class="empty-state">
        <div class="empty-avatar">
          <svg width="48" height="48" viewBox="0 0 48 48" fill="none" class="spinner-sm">
            <circle cx="24" cy="24" r="20" stroke="var(--harmony-comp-divider)" stroke-width="3"/>
            <path d="M24 4A20 20 0 0 1 44 24" stroke="var(--harmony-brand)" stroke-width="3" stroke-linecap="round"/>
          </svg>
        </div>
        <h3>加载中...</h3>
      </div>

      <!-- 智能体卡片网格 -->
      <div v-else-if="agents.length > 0" class="agent-grid">
        <div
          v-for="agent in agents"
          :key="agent.agent_id || agent.id"
          class="agent-card"
          :class="{ 'is-official': agent.is_custom === false }"
          @click="handleCardClick(agent)"
        >
          <!-- 官方标识 -->
          <div v-if="agent.is_custom === false" class="official-badge">
            <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
              <path d="M5 0L6.2 3.8L10 3.8L7 6.2L8.2 10L5 7.8L1.8 10L3 6.2L0 3.8L3.8 3.8L5 0Z" fill="currentColor"/>
            </svg>
            <span>官方</span>
          </div>

          <!-- 删除按钮（仅自定义智能体） -->
          <button
            v-if="agent.is_custom !== false"
            class="delete-btn"
            @click.stop="deleteAgent(agent)"
            title="删除"
          >
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
              <path d="M2.5 3H9.5M8.5 3V10.5C8.5 10.8 8.3 11 8 11H4C3.7 11 3.5 10.8 3.5 10.5V3M4 3V2C4 1.7 4.2 1.5 4.5 1.5H7.5C7.8 1.5 8 1.7 8 2V3M5 5.5V9.5M7 5.5V9.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>

          <!-- 卡片主体 -->
          <div class="card-body">
            <!-- 头像 -->
            <div class="agent-avatar">
              <img
                v-if="agent.logo_url"
                :src="agent.logo_url"
                :alt="agent.name"
                @error="handleImageError"
              />
              <svg v-else width="28" height="28" viewBox="0 0 28 28" fill="none">
                <rect x="4" y="9" width="20" height="14" rx="2" stroke="currentColor" stroke-width="1.5"/>
                <circle cx="11" cy="16" r="1.8" fill="currentColor"/>
                <circle cx="17" cy="16" r="1.8" fill="currentColor"/>
                <path d="M14 4v5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                <circle cx="14" cy="3.5" r="1.5" fill="currentColor"/>
              </svg>
            </div>

            <!-- 信息 -->
            <div class="agent-info">
              <h3 class="agent-name" :title="agent.name">{{ agent.name }}</h3>
              <p class="agent-desc" :title="agent.description">
                {{ agent.description || '暂无描述' }}
              </p>
            </div>
          </div>

          <!-- 元数据 -->
          <div class="agent-meta">
            <div class="meta-item" title="工具">
              <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                <path d="M3.5 2.5L8.5 7.5L7.5 8.5L2.5 3.5L3.5 2.5Z" stroke="currentColor" stroke-width="1"/>
                <path d="M2 4L4 2L10 8L8 10L2 4Z" stroke="currentColor" stroke-width="1" stroke-linejoin="round"/>
                <circle cx="9.5" cy="9.5" r="1.5" stroke="currentColor" stroke-width="1"/>
              </svg>
              <span>{{ getAgentMeta(agent).tools }}</span>
            </div>
            <div class="meta-item" title="知识库">
              <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                <rect x="2" y="2" width="3" height="8" rx="0.5" stroke="currentColor" stroke-width="1"/>
                <rect x="5.5" y="2" width="3" height="8" rx="0.5" stroke="currentColor" stroke-width="1"/>
                <path d="M9 2.5H10C10.3 2.5 10.5 2.7 10.5 3V9.5C10.5 9.8 10.3 10 10 10H9" stroke="currentColor" stroke-width="1" stroke-linecap="round"/>
              </svg>
              <span>{{ getAgentMeta(agent).knowledge }}</span>
            </div>
            <div class="meta-item" title="MCP">
              <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                <rect x="2" y="2" width="8" height="8" rx="1" stroke="currentColor" stroke-width="1"/>
                <path d="M4 6H8M6 4V8" stroke="currentColor" stroke-width="1" stroke-linecap="round"/>
              </svg>
              <span>{{ getAgentMeta(agent).mcp }}</span>
            </div>
            <div class="meta-item" title="技能">
              <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                <path d="M6 1L7.5 4.5L11 5L8.5 7.5L9 11L6 9.5L3 11L3.5 7.5L1 5L4.5 4.5L6 1Z" stroke="currentColor" stroke-width="1" stroke-linejoin="round"/>
              </svg>
              <span>{{ getAgentMeta(agent).skills }}</span>
            </div>
          </div>

          <!-- hover 提示 -->
          <div class="card-hover-tip">
            <span v-if="agent.is_custom === false">官方智能体不可编辑</span>
            <span v-else>点击编辑</span>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else class="empty-state">
        <div class="empty-avatar">
          <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
            <rect x="8" y="16" width="32" height="22" rx="3" stroke="currentColor" stroke-width="1.5"/>
            <circle cx="18" cy="27" r="2.5" fill="currentColor" opacity="0.6"/>
            <circle cx="30" cy="27" r="2.5" fill="currentColor" opacity="0.6"/>
            <path d="M24 8v8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            <circle cx="24" cy="6" r="2.5" fill="currentColor" opacity="0.6"/>
          </svg>
        </div>
        <h3 v-if="searchKeyword">未找到相关智能体</h3>
        <h3 v-else>暂无智能体</h3>
        <p v-if="searchKeyword">试试其他关键词</p>
        <p v-else>创建您的第一个智能体，开始智能对话体验</p>
        <button v-if="searchKeyword" class="btn-primary empty-cta" @click="clearSearch">
          查看所有智能体
        </button>
        <button v-else class="btn-primary empty-cta" @click="createAgent">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <path d="M7 3V11M3 7H11" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
          </svg>
          <span>创建智能体</span>
        </button>
      </div>
    </div>

    <!-- ===== 确认删除弹窗 ===== -->
    <div v-if="showConfirmDialog" class="dialog-overlay" @click.self="cancelDelete">
      <div class="dialog-card">
        <div class="dialog-icon danger">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path d="M12 2L13.5 8.5L20 10L14.5 11.5L12 18L9.5 11.5L4 10L10.5 8.5L12 2Z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
          </svg>
        </div>
        <h3 class="dialog-title">确认删除</h3>
        <p class="dialog-body">
          确定要删除智能体 "<strong>{{ agentToDelete?.name }}</strong>" 吗？此操作不可撤销。
        </p>
        <div class="dialog-actions">
          <button class="btn-secondary" @click="cancelDelete">取消</button>
          <button class="btn-danger" @click="confirmDelete">确认删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
/* ===== 页面容器 ===== */
.agent-page {
  min-height: 100vh;
  padding: 32px;
  background: var(--harmony-comp-background-secondary);
}

/* ===== 页面头部 ===== */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 24px;
  margin-bottom: 24px;
  padding: 20px 24px;
  background: var(--harmony-comp-background-primary);
  border: 1px solid var(--harmony-comp-divider);
  border-radius: var(--harmony-corner-radius-level8);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.header-icon {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--harmony-comp-emphasize-tertiary);
  color: var(--harmony-brand);
  border-radius: var(--harmony-corner-radius-level6);
  flex-shrink: 0;
}

.header-text {
  .header-title {
    font-size: 20px;
    font-weight: 600;
    color: var(--harmony-font-primary);
    margin: 0 0 2px 0;
    letter-spacing: -0.2px;
  }
  .header-desc {
    font-size: 13px;
    color: var(--harmony-font-tertiary);
    margin: 0;
  }
}

.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

/* ===== 搜索框 ===== */
.search-box {
  position: relative;
  display: flex;
  align-items: center;
  width: 280px;
  height: 38px;
  padding: 0 34px 0 34px;
  background: var(--harmony-comp-background-secondary);
  border: 1px solid var(--harmony-comp-divider);
  border-radius: var(--harmony-corner-radius-level6);
  transition: all 0.15s ease;

  &:focus-within {
    border-color: var(--harmony-brand);
    background: var(--harmony-comp-background-primary);
    box-shadow: 0 0 0 3px var(--harmony-comp-emphasize-tertiary);
  }

  .search-icon {
    position: absolute;
    left: 12px;
    color: var(--harmony-font-tertiary);
  }

  .search-input {
    flex: 1;
    border: none;
    background: transparent;
    font-size: 13px;
    color: var(--harmony-font-primary);
    font-family: inherit;

    &::placeholder {
      color: var(--harmony-font-tertiary);
    }
  }

  .search-clear {
    position: absolute;
    right: 8px;
    width: 22px;
    height: 22px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: none;
    background: transparent;
    color: var(--harmony-font-tertiary);
    border-radius: var(--harmony-corner-radius-level4);
    cursor: pointer;
    transition: all 0.15s ease;

    &:hover {
      color: var(--harmony-font-secondary);
      background: var(--harmony-comp-divider);
    }
  }
}

/* ===== 按钮 ===== */
.btn-refresh {
  width: 38px;
  height: 38px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--harmony-comp-background-secondary);
  border: 1px solid var(--harmony-comp-divider);
  color: var(--harmony-font-secondary);
  border-radius: var(--harmony-corner-radius-level6);
  cursor: pointer;
  transition: all 0.15s ease;
  font-family: inherit;

  &:hover:not(:disabled) {
    border-color: var(--harmony-brand);
    color: var(--harmony-brand);
    background: var(--harmony-comp-emphasize-tertiary);
  }

  &:disabled {
    cursor: not-allowed;
    opacity: 0.6;
  }

  .spinning {
    animation: h-spin 1s linear infinite;
  }
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 6px;
  height: 38px;
  padding: 0 14px;
  background: var(--harmony-brand);
  border: none;
  color: white;
  border-radius: var(--harmony-corner-radius-level6);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  font-family: inherit;

  &:hover {
    box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
    transform: translateY(-1px);
  }

  &:active {
    transform: translateY(0);
  }
}

.btn-secondary {
  padding: 8px 16px;
  background: var(--harmony-comp-background-secondary);
  border: 1px solid var(--harmony-comp-divider);
  color: var(--harmony-font-primary);
  border-radius: var(--harmony-corner-radius-level6);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  font-family: inherit;

  &:hover {
    background: var(--harmony-comp-divider);
  }
}

.btn-danger {
  padding: 8px 16px;
  background: var(--harmony-warning);
  border: 1px solid var(--harmony-warning);
  color: white;
  border-radius: var(--harmony-corner-radius-level6);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  font-family: inherit;

  &:hover {
    box-shadow: 0 2px 8px rgba(239, 68, 68, 0.3);
  }
}

/* ===== 智能体列表 ===== */
.agent-list {
  position: relative;
}

.agent-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
}

/* ===== 智能体卡片 ===== */
.agent-card {
  position: relative;
  display: flex;
  flex-direction: column;
  padding: 18px;
  background: var(--harmony-comp-background-primary);
  border: 1px solid var(--harmony-comp-divider);
  border-radius: var(--harmony-corner-radius-level8);
  cursor: pointer;
  transition: all 0.2s ease;
  overflow: hidden;

  &:hover {
    border-color: var(--harmony-brand);
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);

    .card-hover-tip {
      opacity: 1;
      transform: translateY(0);
    }

    .delete-btn {
      opacity: 1;
    }
  }

  &.is-official {
    background: var(--harmony-comp-background-tertiary);
    border-style: solid;

    &:hover {
      border-color: var(--harmony-font-tertiary);
      cursor: default;
      transform: translateY(-2px);
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
    }

    .agent-avatar {
      background: var(--harmony-comp-emphasize-tertiary);
      color: var(--harmony-brand);
    }
  }
}

.official-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  background: var(--harmony-comp-emphasize-tertiary);
  color: var(--harmony-brand);
  border-radius: var(--harmony-corner-radius-level4);
  font-size: 11px;
  font-weight: 500;
}

.delete-btn {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 26px;
  height: 26px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--harmony-comp-background-primary);
  border: 1px solid var(--harmony-comp-divider);
  color: var(--harmony-font-tertiary);
  border-radius: var(--harmony-corner-radius-level4);
  cursor: pointer;
  opacity: 0;
  transition: all 0.15s ease;
  font-family: inherit;

  &:hover {
    background: #fef2f2;
    border-color: var(--harmony-warning);
    color: var(--harmony-warning);
  }
}

.card-body {
  display: flex;
  gap: 12px;
  margin-bottom: 14px;
}

.agent-avatar {
  width: 48px;
  height: 48px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--harmony-comp-background-secondary);
  color: var(--harmony-font-secondary);
  border-radius: var(--harmony-corner-radius-level6);
  overflow: hidden;

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
}

.agent-info {
  flex: 1;
  min-width: 0;

  .agent-name {
    font-size: 15px;
    font-weight: 600;
    color: var(--harmony-font-primary);
    margin: 0 0 4px 0;
    line-height: 1.3;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .agent-desc {
    font-size: 12px;
    color: var(--harmony-font-tertiary);
    margin: 0;
    line-height: 1.5;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
}

/* ===== 元数据标签 ===== */
.agent-meta {
  display: flex;
  gap: 6px;
  padding-top: 12px;
  border-top: 1px solid var(--harmony-comp-divider);

  .meta-item {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 4px 8px;
    background: var(--harmony-comp-background-secondary);
    border-radius: var(--harmony-corner-radius-level4);
    color: var(--harmony-font-secondary);
    font-size: 11px;
    font-weight: 500;

    svg {
      opacity: 0.7;
    }
  }
}

.card-hover-tip {
  margin-top: 10px;
  text-align: center;
  font-size: 11px;
  color: var(--harmony-font-tertiary);
  opacity: 0;
  transform: translateY(4px);
  transition: all 0.2s ease;
}

/* ===== 空状态 ===== */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 24px;
  text-align: center;

  .empty-avatar {
    width: 80px;
    height: 80px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--harmony-comp-background-primary);
    color: var(--harmony-font-tertiary);
    border-radius: 50%;
    margin-bottom: 20px;
    border: 1px solid var(--harmony-comp-divider);
  }

  h3 {
    font-size: 17px;
    font-weight: 600;
    color: var(--harmony-font-primary);
    margin: 0 0 8px 0;
  }

  p {
    font-size: 13px;
    color: var(--harmony-font-tertiary);
    margin: 0 0 20px 0;
  }

  .empty-cta {
    margin-top: 4px;
  }
}

/* ===== 弹窗 ===== */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: harmony-fade-in 0.15s ease;
}

.dialog-card {
  width: 400px;
  max-width: calc(100% - 48px);
  padding: 28px 24px 20px;
  background: var(--harmony-comp-background-primary);
  border-radius: var(--harmony-corner-radius-level8);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
  text-align: center;
  animation: harmony-scale-in 0.15s ease;
}

.dialog-icon {
  width: 56px;
  height: 56px;
  margin: 0 auto 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;

  &.danger {
    background: #fef2f2;
    color: var(--harmony-warning);
  }
}

.dialog-title {
  font-size: 17px;
  font-weight: 600;
  color: var(--harmony-font-primary);
  margin: 0 0 8px 0;
}

.dialog-body {
  font-size: 13px;
  color: var(--harmony-font-secondary);
  margin: 0 0 20px 0;
  line-height: 1.6;

  strong {
    color: var(--harmony-font-primary);
    font-weight: 600;
  }
}

.dialog-actions {
  display: flex;
  gap: 10px;
  justify-content: center;

  button {
    min-width: 100px;
  }
}

/* ===== 动画 ===== */

.spinner-sm {
  animation: h-spin 1s linear infinite;
}

/* ===== 响应式 ===== */
@media (max-width: 900px) {
  .agent-page {
    padding: 20px 16px;
  }

  .page-header {
    flex-direction: column;
    align-items: stretch;
    padding: 16px;
    gap: 16px;
  }

  .header-right {
    width: 100%;
    justify-content: flex-start;
    flex-wrap: wrap;
  }

  .search-box {
    flex: 1;
    min-width: 200px;
  }

  .agent-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  }
}

@media (max-width: 600px) {
  .agent-grid {
    grid-template-columns: 1fr;
  }

  .header-text .header-title {
    font-size: 18px;
  }

  .btn-primary span {
    display: inline;
  }
}
</style>

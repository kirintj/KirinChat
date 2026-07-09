<script setup lang="ts">
import { ref, onMounted, inject } from 'vue'
import { useRouter } from 'vue-router'
import { HButton, HInput, HMessage } from '@/components/ui'
import {
  getAgentsAPI,
  deleteAgentAPI,
  searchAgentsAPI,
} from '../../apis/agent'

const router = useRouter()
const isMobile = inject<import('vue').Ref<boolean>>('isMobile', ref(false))
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
    <!-- ===== Desktop: original layout ===== -->
    <template v-if="!isMobile">
    <!-- ===== 页面头部 ===== -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-text">
          <h1 class="header-title">智能体管理</h1>
          <p class="header-desc">创建和管理您的智能体</p>
        </div>
      </div>

      <div class="header-right">
        <div class="search-box">
          <Icon icon="mdi:magnify" :width="14" :height="14" class="search-icon" />
          <input
            v-model="searchKeyword"
            class="search-input"
            placeholder="搜索智能体名称..."
            @keyup.enter="searchAgents"
          />
          <button v-if="searchKeyword" class="search-clear" @click="clearSearch" title="清空">
            <Icon icon="mdi:close" :width="12" :height="12" />
          </button>
        </div>

        <button class="btn-refresh" @click="fetchAgents" :disabled="loading" title="刷新">
          <Icon icon="mdi:refresh" :width="16" :height="16" :class="{ spinning: loading }" />
        </button>

        <button class="btn-primary" @click="createAgent">
          <Icon icon="mdi:plus" :width="14" :height="14" />
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
            <Icon icon="mdi:delete" :width="12" :height="12" />
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
              <Icon icon="mdi:wrench" :width="12" :height="12" />
              <span>{{ getAgentMeta(agent).tools }}</span>
            </div>
            <div class="meta-item" title="知识库">
              <Icon icon="mdi:book-open-page-variant" :width="12" :height="12" />
              <span>{{ getAgentMeta(agent).knowledge }}</span>
            </div>
            <div class="meta-item" title="MCP">
              <Icon icon="mdi:plus-box" :width="12" :height="12" />
              <span>{{ getAgentMeta(agent).mcp }}</span>
            </div>
            <div class="meta-item" title="技能">
              <Icon icon="mdi:star" :width="12" :height="12" />
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
          <Icon icon="mdi:plus" :width="14" :height="14" />
          <span>创建智能体</span>
        </button>
      </div>
    </div>

    <!-- ===== 确认删除弹窗 ===== -->
    <div v-if="showConfirmDialog" class="dialog-overlay" @click.self="cancelDelete">
      <div class="dialog-card">
        <div class="dialog-icon danger">
          <Icon icon="mdi:alert" :width="24" :height="24" />
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
    </template>

    <!-- ===== Mobile: hmos mobile-card layout ===== -->
    <div v-else class="agent-mobile">
      <!-- Search + Create row -->
      <div class="am-toolbar">
        <div class="am-search">
          <input v-model="searchKeyword" placeholder="搜索智能体..." @keyup.enter="searchAgents" />
        </div>
        <button class="am-create-btn" @click="createAgent">+ 创建</button>
      </div>

      <!-- Agent cards grid -->
      <div class="am-grid" v-if="agents.length > 0">
        <div
          v-for="agent in agents"
          :key="agent.agent_id || agent.id"
          class="am-card"
          :class="{ 'is-official': agent.is_custom === false }"
          @click="handleCardClick(agent)"
        >
          <div class="am-card__avatar">
            <img v-if="agent.logo_url" :src="agent.logo_url" :alt="agent.name" @error="handleImageError" />
          </div>
          <div class="am-card__info">
            <h3 class="am-card__name">{{ agent.name }}</h3>
            <p class="am-card__desc">{{ agent.description || '暂无描述' }}</p>
          </div>
          <div class="am-card__meta">
            <span class="am-tag">工具 {{ getAgentMeta(agent).tools }}</span>
            <span class="am-tag">知识库 {{ getAgentMeta(agent).knowledge }}</span>
          </div>
        </div>
      </div>

      <!-- Empty state -->
      <div v-else-if="!loading" class="am-empty">
        <p>暂无智能体</p>
        <button class="am-create-btn" @click="createAgent">创建智能体</button>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@use '../../styles/breakpoints.scss' as *;
/* ===== 页面容器 ===== */
.agent-page {
  min-height: 100%;
  padding: 32px;
  background: transparent;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
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
  border-radius: var(--harmony-corner-radius-level8);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.header-text {
  .header-title {
    font-size: var(--harmony-font-size-title-s);
    font-weight: 600;
    color: var(--harmony-font-primary);
    margin: 0 0 2px 0;
    letter-spacing: -0.2px;
  }
  .header-desc {
    font-size: var(--harmony-font-size-subtitle-s);
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
  border-radius: var(--harmony-corner-radius-level6);
  transition: all 0.15s ease;

  &:focus-within {
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
    font-size: var(--harmony-font-size-subtitle-s);
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
  font-size: var(--harmony-font-size-subtitle-s);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  font-family: inherit;

  &:hover {
    box-shadow: var(--harmony-shadow-md);
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
  font-size: var(--harmony-font-size-subtitle-s);
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
  font-size: var(--harmony-font-size-subtitle-s);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  font-family: inherit;

  &:hover {
    box-shadow: var(--harmony-shadow-md);
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
  border-radius: var(--harmony-corner-radius-level8);
  cursor: pointer;
  transition: all 0.2s ease;
  overflow: hidden;

  &:hover {
    transform: translateY(-2px);
    box-shadow: var(--harmony-shadow-md);

    .card-hover-tip {
      opacity: 1;
      transform: translateY(0);
    }

    .delete-btn {
      opacity: 1;
    }
  }

  &.is-official {

    &:hover {
      border-color: var(--harmony-font-tertiary);
      cursor: default;
      transform: translateY(-2px);
      box-shadow: var(--harmony-shadow-sm);
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
  font-size: var(--harmony-font-size-caption-l);
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
  color: var(--harmony-font-tertiary);
  border-radius: var(--harmony-corner-radius-level4);
  cursor: pointer;
  opacity: 0;
  transition: all 0.15s ease;
  font-family: inherit;

  &:hover {
    background: var(--harmony-warning-bg);
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
    font-size: var(--harmony-font-size-subtitle-m);
    font-weight: 600;
    color: var(--harmony-font-primary);
    margin: 0 0 4px 0;
    line-height: 1.3;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .agent-desc {
    font-size: var(--harmony-font-size-body-s);
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

  .meta-item {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 4px 8px;
    background: var(--harmony-comp-background-secondary);
    border-radius: var(--harmony-corner-radius-level4);
    color: var(--harmony-font-secondary);
    font-size: var(--harmony-font-size-caption-l);
    font-weight: 500;

    svg {
      opacity: 0.7;
    }
  }
}

.card-hover-tip {
  margin-top: 10px;
  text-align: center;
  font-size: var(--harmony-font-size-caption-l);
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
  }

  h3 {
    font-size: 17px;
    font-weight: 600;
    color: var(--harmony-font-primary);
    margin: 0 0 8px 0;
  }

  p {
    font-size: var(--harmony-font-size-subtitle-s);
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
  background: var(--harmony-overlay-light);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-dialog);
  animation: harmony-fade-in 0.15s ease;
}

.dialog-card {
  width: 400px;
  max-width: calc(100% - 48px);
  padding: 28px 24px 20px;
  background: var(--harmony-comp-background-primary);
  border-radius: var(--harmony-corner-radius-level8);
  box-shadow: var(--harmony-shadow-dialog);
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
    background: var(--harmony-warning-bg);
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
  font-size: var(--harmony-font-size-subtitle-s);
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
@include tablet-and-below {
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
    max-width: 100%;
  }

  .agent-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  }
}

@include mobile {
  .agent-grid {
    grid-template-columns: 1fr;
  }

  .header-text .header-title {
    font-size: var(--harmony-font-size-subtitle-l);
  }

  .btn-primary span {
    display: inline;
  }
}

/* ==================== MOBILE: hmos mobile-card ==================== */
.agent-mobile {
  display: flex;
  flex-direction: column;
  gap: var(--harmony-section-gap-mobile, 16px);
  padding-top: var(--harmony-padding-level8, 16px);
}

.am-toolbar {
  display: flex;
  gap: var(--harmony-padding-level4, 8px);
  align-items: center;
}

.am-search {
  flex: 1;

  input {
    width: 100%;
    height: var(--harmony-control-height-40, 40px);
    padding: 0 var(--harmony-padding-level6, 12px);
    border: 1px solid var(--harmony-comp-divider);
    border-radius: var(--harmony-corner-radius-level6, 12px);
    font-size: var(--harmony-font-size-body-m);
    background: var(--harmony-comp-background-primary);
    color: var(--harmony-font-primary);
    box-sizing: border-box;

    &:focus {
      border-color: var(--harmony-brand);
      outline: none;
    }

    &::placeholder {
      color: var(--harmony-font-tertiary);
    }
  }
}

.am-create-btn {
  height: var(--harmony-control-height-40, 40px);
  padding: 0 var(--harmony-padding-level8, 16px);
  background: var(--harmony-brand);
  color: white;
  border: none;
  border-radius: var(--harmony-corner-radius-level6, 12px);
  font-size: var(--harmony-font-size-body-m);
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  flex-shrink: 0;
}

.am-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--harmony-card-gap-mobile, 12px);
}

.am-card {
  display: flex;
  flex-direction: column;
  gap: var(--harmony-padding-level4, 8px);
  padding: var(--harmony-padding-level8, 16px);
  background: var(--harmony-comp-background-primary);
  border-radius: var(--harmony-corner-radius-level8, 16px);
  cursor: pointer;
  transition: background 0.15s ease;

  &:active {
    background: var(--harmony-interactive-pressed);
  }

  &.is-official {
    opacity: 0.7;
  }

  &__avatar {
    width: var(--harmony-control-height-48, 48px);
    height: var(--harmony-control-height-48, 48px);
    border-radius: var(--harmony-corner-radius-level6, 12px);
    overflow: hidden;
    background: var(--harmony-comp-background-secondary);
    flex-shrink: 0;

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  }

  &__info {
    flex: 1;
    min-width: 0;
  }

  &__name {
    font-size: var(--harmony-font-size-body-m);
    font-weight: 600;
    color: var(--harmony-font-primary);
    margin: 0 0 var(--harmony-padding-level2, 4px) 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  &__desc {
    font-size: var(--harmony-font-size-body-s);
    color: var(--harmony-font-secondary);
    margin: 0;
    line-height: 1.4;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  &__meta {
    display: flex;
    gap: var(--harmony-padding-level2, 4px);
    flex-wrap: wrap;
    padding-top: var(--harmony-padding-level4, 8px);
  }
}

.am-tag {
  font-size: var(--harmony-font-size-caption-l, 12px);
  color: var(--harmony-font-tertiary);
  background: var(--harmony-comp-background-secondary);
  padding: var(--harmony-padding-level1, 2px) var(--harmony-padding-level4, 8px);
  border-radius: var(--harmony-corner-radius-level4, 8px);
}

.am-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
  gap: var(--harmony-padding-level8, 16px);

  p {
    font-size: var(--harmony-font-size-body-m);
    color: var(--harmony-font-tertiary);
    margin: 0;
  }
}
</style>

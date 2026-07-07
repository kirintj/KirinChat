<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { HMessage } from '@/components/ui'
import { MdPreview } from "md-editor-v3"
import "md-editor-v3/lib/style.css"
import { getWorkspacePluginsAPI, workspaceSimpleChatStreamAPI, type WorkSpaceSimpleTask } from '../../../apis/workspace'
import { getVisibleLLMsAPI, type LLMResponse } from '../../../apis/llm'
import { useUserStore } from '../../../store/user'

const userStore = useUserStore()
const router = useRouter()
const route = useRoute()
const inputMessage = ref('')
const selectedMode = ref('normal')
const plugins = ref<any[]>([])
const showModelSelector = ref(false)
const showToolSelector = ref(false)
const showSearchSelector = ref(false)
const selectedModel = ref<string>('')
const selectedModelId = ref<string>('')
const selectedTools = ref<string[]>([])
const showMcpSelector = ref(false)
const selectedMcpServers = ref<string[]>([])
const mcpServers = ref<any[]>([])
const webSearchEnabled = ref(false)
const toolDropdownRef = ref<HTMLElement | null>(null)
const mcpDropdownRef = ref<HTMLElement | null>(null)
const fileInputRef = ref<HTMLInputElement | null>(null)
const currentSessionId = ref<string>('')
const chatConversationRef = ref<HTMLElement | null>(null)
const isGenerating = ref(false)

const modelOptions = ref<LLMResponse[]>([])
const modelsLoading = ref(false)
const modelsError = ref('')
const modelsRetryable = ref(false)

const messages = ref<Array<{ role: 'user' | 'assistant'; content: string }>>([])

const pluginsError = ref('')
const pluginsRetryable = ref(false)
const pluginsLoading = ref(false)

const handleAvatarError = (event: Event) => {
  const target = event.target as HTMLImageElement
  if (target) target.src = '/user.svg'
}

const modes = [
  {
    id: 'normal',
    label: '日常模式',
    icon: '💬',
    desc: '快速问答、日常对话'
  },
  {
    id: 'lingseek',
    label: '灵寻LingSeek',
    icon: '✨',
    desc: '复杂任务规划与执行'
  }
]

const fetchModels = async () => {
  modelsLoading.value = true
  modelsError.value = ''
  modelsRetryable.value = false
  try {
    const res = await getVisibleLLMsAPI()
    if (res.data && res.data.status_code === 200) {
      const grouped = res.data.data || {}
      const list: LLMResponse[] = []
      Object.values(grouped).forEach((arr: any) => {
        if (Array.isArray(arr)) list.push(...arr)
      })
      modelOptions.value = list.filter(m => (m.llm_type || '').toUpperCase() === 'LLM')
      if (!selectedModelId.value && modelOptions.value.length > 0) {
        selectedModelId.value = modelOptions.value[0].llm_id
        selectedModel.value = modelOptions.value[0].model
      }
    }
  } catch (e: any) {
    const msg = e?.friendlyMessage || '获取模型失败'
    console.error(msg, e)
    modelsError.value = msg
    modelsRetryable.value = e?.code === 'ECONNABORTED' || !e?.response
  } finally {
    modelsLoading.value = false
  }
}

const fetchPlugins = async () => {
  pluginsLoading.value = true
  pluginsError.value = ''
  pluginsRetryable.value = false
  try {
    const response = await getWorkspacePluginsAPI()
    if (response.data.status_code === 200) {
      plugins.value = response.data.data || []
    }
  } catch (error: any) {
    const msg = error?.friendlyMessage || '获取插件列表失败'
    console.error(msg, error)
    pluginsError.value = msg
    pluginsRetryable.value = error?.code === 'ECONNABORTED' || !error?.response
  } finally {
    pluginsLoading.value = false
  }
}

const selectMode = (modeId: string) => {
  selectedMode.value = modeId
}

const selectModel = (llmId: string) => {
  const model = modelOptions.value.find(m => m.llm_id === llmId)
  if (model) {
    selectedModelId.value = model.llm_id
    selectedModel.value = model.model
  }
  showModelSelector.value = false
}

const toggleTool = (toolId: string) => {
  const index = selectedTools.value.indexOf(toolId)
  if (index > -1) {
    selectedTools.value.splice(index, 1)
  } else {
    selectedTools.value.push(toolId)
  }
}

const toggleWebSearch = () => {
  webSearchEnabled.value = !webSearchEnabled.value
  showSearchSelector.value = false
}

const handleClickOutside = (e: MouseEvent) => {
  const target = e.target as Node
  if (showToolSelector.value && toolDropdownRef.value && !toolDropdownRef.value.contains(target)) {
    showToolSelector.value = false
  }
  if (showMcpSelector.value && mcpDropdownRef.value && !mcpDropdownRef.value.contains(target)) {
    showMcpSelector.value = false
  }
}

const triggerFileInput = () => {
  fileInputRef.value?.click()
}

const onFileChange = (e: Event) => {
  const input = e.target as HTMLInputElement
  const files = input.files
  if (files && files.length > 0) {
    HMessage.success(`已选择 ${files.length} 个文件`)
  }
  if (input) input.value = ''
}

const toggleMcp = (serverId: string) => {
  const index = selectedMcpServers.value.indexOf(serverId)
  if (index > -1) {
    selectedMcpServers.value.splice(index, 1)
  } else {
    selectedMcpServers.value.push(serverId)
  }
}

const generateSessionId = (): string => {
  return crypto.randomUUID().replace(/-/g, '')
}

const scrollToBottom = () => {
  if (chatConversationRef.value) {
    setTimeout(() => {
      if (chatConversationRef.value) {
        chatConversationRef.value.scrollTop = chatConversationRef.value.scrollHeight
      }
    }, 100)
  }
}

const handleSend = async () => {
  if (!inputMessage.value.trim()) {
    HMessage.warning('请输入消息内容')
    return
  }
  if (isGenerating.value) {
    HMessage.warning('请等待当前回复完成')
    return
  }

  const query = inputMessage.value.trim()

  if (selectedMode.value === 'lingseek') {
    inputMessage.value = ''
    router.push({
      name: 'taskGraphPage',
      query: {
        query: query,
        tools: JSON.stringify(selectedTools.value),
        webSearch: webSearchEnabled.value.toString(),
        mcp_servers: JSON.stringify(selectedMcpServers.value)
      }
    })
  } else {
    if (!selectedModelId.value) {
      HMessage.warning('请先选择模型')
      return
    }
    if (!currentSessionId.value) {
      currentSessionId.value = generateSessionId()
    }
    inputMessage.value = ''
    isGenerating.value = true
    messages.value.push({ role: 'user' as const, content: query })
    scrollToBottom()

    const aiMsgIndex = messages.value.length
    messages.value.push({ role: 'assistant', content: '' })

    try {
      const payload: WorkSpaceSimpleTask = {
        query,
        model_id: selectedModelId.value,
        plugins: selectedTools.value,
        mcp_servers: selectedMcpServers.value,
        session_id: currentSessionId.value
      }
      await workspaceSimpleChatStreamAPI(
        payload,
        (chunk) => {
          messages.value[aiMsgIndex].content += chunk
          scrollToBottom()
        },
        (err) => {
          console.error('流式出错', err)
          HMessage.error('对话失败，请稍后重试')
          isGenerating.value = false
        },
        () => {
          isGenerating.value = false
        }
      )
    } catch (e) {
      console.error('对话异常', e)
      HMessage.error('对话异常')
      isGenerating.value = false
    }
  }
}

const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    if (!isGenerating.value) {
      handleSend()
    }
  }
}

const loadSessionHistory = async (sessionId: string) => {
  try {
    const { getWorkspaceSessionsAPI } = await import('../../../apis/workspace')
    const response = await getWorkspaceSessionsAPI()
    if (response.data.status_code === 200) {
      const session = response.data.data.find((s: any) => s.session_id === sessionId)
      if (session && session.contexts && Array.isArray(session.contexts)) {
        messages.value = session.contexts.map((ctx: any) => [
          { role: 'user' as const, content: ctx.query || '' },
          { role: 'assistant' as const, content: ctx.answer || '' }
        ]).flat().filter((msg: any) => msg.content)
        scrollToBottom()
      }
    }
  } catch (error) {
    console.error('加载会话历史失败:', error)
    HMessage.error('加载会话历史失败')
  }
}

onMounted(async () => {
  fetchPlugins()
  fetchModels()
  const sessionId = route.query.session_id as string
  if (sessionId) {
    currentSessionId.value = sessionId
    await loadSessionHistory(sessionId)
  } else {
    currentSessionId.value = generateSessionId()
  }
  import('../../../apis/mcp-server').then(async ({ getMCPServersAPI }) => {
    try {
      const res = await getMCPServersAPI()
      if (res.data && res.data.status_code === 200 && Array.isArray(res.data.data)) {
        mcpServers.value = res.data.data
      }
    } catch (e) {
      console.error('加载MCP服务器失败', e)
    }
  })
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})

watch(
  () => route.query.session_id,
  async (newSessionId, oldSessionId) => {
    if (newSessionId && newSessionId !== oldSessionId) {
      currentSessionId.value = newSessionId as string
      messages.value = []
      await loadSessionHistory(newSessionId as string)
    } else if (!newSessionId && oldSessionId) {
      currentSessionId.value = generateSessionId()
      messages.value = []
    }
  }
)
</script>

<template>
  <div class="dp-root" :class="{ 'has-messages': messages.length > 0 }">
    <div class="dp-inner">
      <!-- ===== 欢迎区域（无对话时） ===== -->
      <template v-if="messages.length === 0">
        <div class="welcome-section">
          <div class="welcome-avatar">
            <svg width="56" height="56" viewBox="0 0 56 56" fill="none">
              <circle cx="28" cy="28" r="28" fill="var(--harmony-comp-emphasize-tertiary)"/>
              <path d="M20 22C20 20.8954 20.8954 20 22 20H34C35.1046 20 36 20.8954 36 22V30C36 31.1046 35.1046 32 34 32H24L20 36V22Z" fill="var(--harmony-brand)" opacity="0.85"/>
              <circle cx="24" cy="26" r="1.5" fill="white"/>
              <circle cx="28" cy="26" r="1.5" fill="white"/>
              <circle cx="32" cy="26" r="1.5" fill="white"/>
            </svg>
          </div>
          <h1 class="welcome-title">你好，我是麒麟智聊</h1>
          <p class="welcome-desc">选择一种模式，开始对话吧</p>

          <!-- 模式选择卡片 -->
          <div class="mode-cards">
            <div
              v-for="mode in modes"
              :key="mode.id"
              :class="['mode-card', { active: selectedMode === mode.id }]"
              @click="selectMode(mode.id)"
            >
              <div class="mode-card-icon">{{ mode.icon }}</div>
              <div class="mode-card-body">
                <div class="mode-card-title">{{ mode.label }}</div>
                <div class="mode-card-desc">{{ mode.desc }}</div>
              </div>
              <div v-if="selectedMode === mode.id" class="mode-card-check">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <path d="M4 8L7 11L12 5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- ===== 对话区域（有对话时） ===== -->
      <div v-if="messages.length > 0" class="chat-area" ref="chatConversationRef">
        <div v-for="(msg, idx) in messages" :key="idx" class="msg-row" :class="msg.role">
          <!-- AI消息 -->
          <template v-if="msg.role === 'assistant'">
            <div class="msg-avatar ai">
              <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                <circle cx="9" cy="9" r="9" fill="var(--harmony-brand)"/>
                <path d="M5.5 7C5.5 6.17157 6.17157 5.5 7 5.5H11C11.8284 5.5 12.5 6.17157 12.5 7V10C12.5 10.8284 11.8284 11.5 11 11.5H7.5L5.5 13.5V7Z" fill="white" opacity="0.9"/>
              </svg>
            </div>
            <div class="msg-bubble ai">
              <div v-if="!msg.content && isGenerating && idx === messages.length - 1" class="msg-loading">
                <span class="dot-pulse"></span>
              </div>
              <MdPreview v-if="msg.content" :editorId="'dp-ai-' + idx" :modelValue="msg.content" />
            </div>
          </template>

          <!-- 用户消息 -->
          <template v-else>
            <div class="msg-bubble user">{{ msg.content }}</div>
            <div class="msg-avatar user">
              <img
                :src="userStore.userInfo?.avatar || '/user.svg'"
                alt="avatar"
                @error="handleAvatarError"
              />
            </div>
          </template>
        </div>
      </div>

      <!-- ===== 底部输入区 ===== -->
      <div class="input-section" :class="{ fixed: messages.length > 0 }">
        <div class="input-box" :class="{ 'lingseek-glow': selectedMode === 'lingseek' }">
          <textarea
            v-model="inputMessage"
            placeholder="输入消息，按 Enter 发送..."
            class="input-field"
            rows="1"
            @keydown="handleKeydown"
            @input="autoResize"
          ></textarea>

          <div class="input-actions">
            <div class="action-group">
              <!-- 模型选择（日常模式） -->
              <div v-if="selectedMode === 'normal'" class="action-dropdown">
                <button class="action-btn" @click="showModelSelector = !showModelSelector" :title="selectedModel || '选择模型'">
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <rect x="2" y="2" width="10" height="10" rx="2" stroke="currentColor" stroke-width="1.2"/>
                    <circle cx="7" cy="7" r="2" stroke="currentColor" stroke-width="1.2"/>
                  </svg>
                  <span class="action-label">{{ selectedModel || (modelsLoading ? '...' : '模型') }}</span>
                </button>
                <transition name="drop-up">
                  <div v-if="showModelSelector" class="dropdown">
                    <div v-if="modelsLoading" class="dropdown-item disabled">加载中...</div>
                    <div v-else-if="modelsError" class="dropdown-item error">
                      <span>{{ modelsError }}</span>
                      <button v-if="modelsRetryable" @click.stop="fetchModels">重试</button>
                    </div>
                    <div v-else-if="modelOptions.length === 0" class="dropdown-item disabled">暂无可用模型</div>
                    <div
                      v-for="m in modelOptions"
                      :key="m.llm_id"
                      :class="['dropdown-item', { selected: selectedModelId === m.llm_id }]"
                      @click="selectModel(m.llm_id)"
                    >{{ m.model }}</div>
                  </div>
                </transition>
              </div>

              <!-- 联网搜索（灵寻模式） -->
              <div v-if="selectedMode === 'lingseek'" class="action-dropdown">
                <button :class="['action-btn', { active: webSearchEnabled }]" @click="toggleWebSearch">
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <circle cx="7" cy="7" r="5" stroke="currentColor" stroke-width="1.2"/>
                    <path d="M7 2V12M2 7H12" stroke="currentColor" stroke-width="1.2" opacity="0.4"/>
                  </svg>
                  <span class="action-label">联网</span>
                </button>
              </div>

              <!-- 工具选择 -->
              <div class="action-dropdown" ref="toolDropdownRef">
                <button class="action-btn" @click="showToolSelector = !showToolSelector">
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <path d="M3 3.5L7 2L11 3.5V6.5L7 8L3 6.5V3.5Z" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/>
                    <path d="M3 6.5L7 8L11 6.5" stroke="currentColor" stroke-width="1.2"/>
                    <path d="M7 8V11" stroke="currentColor" stroke-width="1.2"/>
                    <path d="M4.5 10L7 11L9.5 10" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/>
                  </svg>
                  <span class="action-label">{{ selectedTools.length > 0 ? `工具(${selectedTools.length})` : '工具' }}</span>
                </button>
                <transition name="drop-up">
                  <div v-if="showToolSelector" class="dropdown wide">
                    <div class="dropdown-hd">
                      <span>选择工具</span>
                      <span class="count">{{ plugins.length }}</span>
                    </div>
                    <div class="dropdown-list">
                      <div v-if="pluginsLoading" class="dropdown-item disabled">加载中...</div>
                      <div v-else-if="plugins.length === 0" class="dropdown-item disabled">暂无可用工具</div>
                      <div
                        v-for="plugin in plugins"
                        :key="plugin.id || plugin.tool_id"
                        :class="['dropdown-item', { selected: selectedTools.includes(plugin.id || plugin.tool_id) }]"
                        @click="toggleTool(plugin.id || plugin.tool_id)"
                      >
                        <span class="item-text">{{ plugin.display_name }}</span>
                        <span v-if="selectedTools.includes(plugin.id || plugin.tool_id)" class="item-check">✓</span>
                      </div>
                    </div>
                    <div v-if="selectedTools.length > 0" class="dropdown-ft">
                      <button class="clear-btn" @click.stop="selectedTools = []">清空</button>
                      <span>已选 {{ selectedTools.length }}</span>
                    </div>
                  </div>
                </transition>
              </div>

              <!-- MCP选择 -->
              <div class="action-dropdown" ref="mcpDropdownRef">
                <button class="action-btn" @click="showMcpSelector = !showMcpSelector">
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <rect x="2" y="2" width="10" height="10" rx="2" stroke="currentColor" stroke-width="1.2"/>
                    <path d="M5 7H9M7 5V9" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
                  </svg>
                  <span class="action-label">{{ selectedMcpServers.length > 0 ? `MCP(${selectedMcpServers.length})` : 'MCP' }}</span>
                </button>
                <transition name="drop-up">
                  <div v-if="showMcpSelector" class="dropdown wide">
                    <div class="dropdown-hd">
                      <span>选择MCP服务器</span>
                      <span class="count">{{ mcpServers.length }}</span>
                    </div>
                    <div class="dropdown-list">
                      <div v-if="mcpServers.length === 0" class="dropdown-item disabled">暂无可用MCP</div>
                      <div
                        v-for="mcp in mcpServers"
                        :key="mcp.mcp_server_id"
                        :class="['dropdown-item', { selected: selectedMcpServers.includes(mcp.mcp_server_id) }]"
                        @click="toggleMcp(mcp.mcp_server_id)"
                      >
                        <span class="item-text">{{ mcp.server_name }}</span>
                        <span v-if="selectedMcpServers.includes(mcp.mcp_server_id)" class="item-check">✓</span>
                      </div>
                    </div>
                    <div v-if="selectedMcpServers.length > 0" class="dropdown-ft">
                      <button class="clear-btn" @click.stop="selectedMcpServers = []">清空</button>
                      <span>已选 {{ selectedMcpServers.length }}</span>
                    </div>
                  </div>
                </transition>
              </div>
            </div>

            <div class="action-group">
              <!-- 附件 -->
              <button class="action-btn" @click="triggerFileInput" title="上传附件">
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                  <path d="M7 4V10M4 7H10" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
                  <rect x="2" y="2" width="10" height="10" rx="3" stroke="currentColor" stroke-width="1.2"/>
                </svg>
              </button>
              <input type="file" ref="fileInputRef" class="hidden" multiple @change="onFileChange" />

              <!-- 发送 -->
              <button :class="['send-btn', { disabled: isGenerating }]" :disabled="isGenerating" @click="handleSend">
                <svg v-if="!isGenerating" width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <path d="M3 8H13M13 8L9 4M13 8L9 12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <span v-else class="spinner-sm"></span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.dp-root {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  background: var(--harmony-comp-background-primary);

  &.has-messages {
    background: var(--harmony-comp-background-secondary);
    overflow: hidden;
  }
}

.dp-inner {
  width: 100%;
  max-width: 780px;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 48px 24px 32px;

  .has-messages & {
    max-width: 100%;
    height: 100%;
    padding: 0;
  }
}

/* ===== 欢迎区 ===== */
.welcome-section {
  text-align: center;
  animation: harmony-slide-up 0.5s ease both;
  width: 100%;
  max-width: 460px;

  .welcome-avatar {
    margin-bottom: 20px;
    display: flex;
    justify-content: center;
  }

  .welcome-title {
    font-size: 26px;
    font-weight: 700;
    color: var(--harmony-font-primary);
    margin: 0 0 6px;
    letter-spacing: -0.3px;
  }

  .welcome-desc {
    font-size: var(--harmony-font-size-body-m);
    color: var(--harmony-font-tertiary);
    margin: 0 0 32px;
  }
}

/* ===== 模式卡片 ===== */
.mode-cards {
  display: flex;
  gap: 12px;
  width: 100%;

  .mode-card {
    flex: 1;
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px;
    border: 1px solid var(--harmony-comp-divider);
    border-radius: var(--harmony-corner-radius-level8);
    cursor: pointer;
    transition: all var(--harmony-duration-fast) var(--harmony-motion-standard);
    background: var(--harmony-comp-background-primary);
    text-align: left;

    &:hover {
      border-color: var(--harmony-brand);
      background: var(--harmony-comp-emphasize-tertiary);
    }

    &.active {
      border-color: var(--harmony-brand);
      background: var(--harmony-comp-emphasize-tertiary);
    }

    .mode-card-icon {
      font-size: 24px;
      flex-shrink: 0;
      width: 40px;
      height: 40px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: var(--harmony-comp-background-secondary);
      border-radius: var(--harmony-corner-radius-level4);
      border: 1px solid var(--harmony-comp-divider);
    }

    .mode-card-body {
      flex: 1;
      min-width: 0;

      .mode-card-title {
        font-size: var(--harmony-font-size-subtitle-s);
        font-weight: 600;
        color: var(--harmony-font-primary);
        margin-bottom: 2px;
      }

      .mode-card-desc {
        font-size: var(--harmony-font-size-body-s);
        color: var(--harmony-font-tertiary);
      }
    }

    .mode-card-check {
      width: 22px;
      height: 22px;
      border-radius: 50%;
      background: var(--harmony-brand);
      color: white;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }
  }
}

/* ===== 对话区域 ===== */
.chat-area {
  flex: 1;
  width: 100%;
  overflow-y: auto;
  padding: 20px 24px;
  scroll-behavior: smooth;
}

.msg-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 20px;

  &.user {
    justify-content: flex-end;
  }

  &.assistant {
    justify-content: flex-start;
  }
}

.msg-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  border: 1px solid var(--harmony-comp-divider);

  &.ai {
    border: none;
  }

  &.user img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
}

.msg-bubble {
  max-width: 68%;
  padding: 10px 14px;
  border-radius: 16px;
  font-size: var(--harmony-font-size-subtitle-s);
  line-height: 1.6;
  word-break: break-word;

  &.user {
    background: var(--harmony-brand);
    color: white;
    border-bottom-right-radius: 4px;
  }

  &.ai {
    background: var(--harmony-comp-background-primary);
    border: 1px solid var(--harmony-comp-divider);
    border-bottom-left-radius: 4px;

    :deep(.md-editor-preview-wrapper) {
      background: transparent !important;
    }
  }
}

.msg-loading {
  padding: 4px 0;
  
  .dot-pulse {
    display: inline-block;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--harmony-font-tertiary);
    animation: harmony-pulse 1.4s infinite ease-in-out both;
  }
}




/* ===== 输入区 ===== */
.input-section {
  width: 100%;
  max-width: 680px;
  padding: 16px 0;
  animation: harmony-slide-up 0.5s ease 0.15s both;

  &.fixed {
    max-width: 100%;
    padding: 8px 24px 16px;
    background: var(--harmony-comp-background-secondary);
    animation: none;
  }

  .input-box {
    background: var(--harmony-comp-background-primary);
    border: 1px solid var(--harmony-comp-divider);
    border-radius: 16px;
    padding: 10px 14px;
    transition: all var(--harmony-duration-fast) var(--harmony-motion-standard);
    box-shadow: var(--harmony-shadow-sm);

    &:focus-within {
      border-color: var(--harmony-brand);
      box-shadow: 0 0 0 3px var(--harmony-comp-emphasize-tertiary);
    }

    &.lingseek-glow {
      border-color: rgba(102, 126, 234, 0.3);
      box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.08);
    }

    .input-field {
      width: 100%;
      border: none;
      background: transparent;
      font-size: var(--harmony-font-size-subtitle-s);
      line-height: 1.5;
      color: var(--harmony-font-primary);
      resize: none;
      font-family: inherit;
      min-height: 24px;
      max-height: 120px;

      &::placeholder {
        color: var(--harmony-font-tertiary);
      }
    }

    .input-actions {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 8px;
      padding-top: 8px;
      border-top: 1px solid var(--harmony-comp-divider);
    }

    .action-group {
      display: flex;
      align-items: center;
      gap: 4px;
    }
  }
}

/* ===== 操作按钮 ===== */
.action-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 5px 8px;
  border: 1px solid transparent;
  border-radius: var(--harmony-corner-radius-level4);
  background: transparent;
  color: var(--harmony-font-tertiary);
  font-size: 11px;
  cursor: pointer;
  transition: all var(--harmony-duration-fast) var(--harmony-motion-standard);
  white-space: nowrap;
  font-family: inherit;

  &:hover {
    background: var(--harmony-comp-background-secondary);
    color: var(--harmony-font-secondary);
    border-color: var(--harmony-comp-divider);
  }

  &.active {
    background: var(--harmony-comp-emphasize-tertiary);
    color: var(--harmony-brand);
    border-color: var(--harmony-brand);
  }

  .action-label {
    font-weight: 500;
  }
}

/* ===== 下拉菜单 ===== */
.action-dropdown {
  position: relative;
}

.dropdown {
  position: absolute;
  bottom: calc(100% + 6px);
  left: 0;
  min-width: 140px;
  background: var(--harmony-comp-background-primary);
  border: 1px solid var(--harmony-comp-divider);
  border-radius: var(--harmony-corner-radius-level6);
  box-shadow: var(--harmony-shadow-md);
  z-index: 100;
  max-height: 300px;
  overflow: hidden;
  display: flex;
  flex-direction: column;

  &.wide {
    min-width: 240px;
  }

  .dropdown-hd {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 12px;
    font-size: var(--harmony-font-size-body-s);
    color: var(--harmony-font-secondary);
    font-weight: 600;
    border-bottom: 1px solid var(--harmony-comp-divider);

    .count {
      font-weight: 400;
      color: var(--harmony-font-tertiary);
      font-size: 11px;
    }
  }

  .dropdown-list {
    flex: 1;
    overflow-y: auto;
  }

  .dropdown-item {
    padding: 8px 12px;
    font-size: var(--harmony-font-size-body-s);
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: center;
    transition: background var(--harmony-duration-fast) var(--harmony-motion-standard);

    &:hover {
      background: var(--harmony-comp-background-secondary);
    }

    &.selected {
      color: var(--harmony-brand);
      font-weight: 500;
    }

    &.disabled {
      color: var(--harmony-font-tertiary);
      cursor: default;
    }

    &.error {
      flex-direction: column;
      align-items: flex-start;
      gap: 6px;
      color: var(--harmony-warning);

      button {
        font-size: 11px;
        padding: 2px 10px;
        border: 1px solid var(--harmony-brand);
        border-radius: var(--harmony-corner-radius-level4);
        background: transparent;
        color: var(--harmony-brand);
        cursor: pointer;
      }
    }

    .item-text {
      flex: 1;
      min-width: 0;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .item-check {
      color: var(--harmony-brand);
      font-weight: 600;
      margin-left: 8px;
    }
  }

  .dropdown-ft {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 6px 12px;
    border-top: 1px solid var(--harmony-comp-divider);
    font-size: 11px;
    color: var(--harmony-font-tertiary);

    .clear-btn {
      border: none;
      background: transparent;
      color: var(--harmony-warning);
      font-size: 11px;
      cursor: pointer;
      padding: 2px 6px;

      &:hover {
        text-decoration: underline;
      }
    }
  }
}

/* 下拉动画（向上） */
.drop-up-enter-active,
.drop-up-leave-active {
  transition: all 0.15s ease;
}
.drop-up-enter-from,
.drop-up-leave-to {
  opacity: 0;
  transform: translateY(6px);
}

/* ===== 发送按钮 ===== */
.send-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: var(--harmony-corner-radius-level4);
  background: var(--harmony-brand);
  color: white;
  cursor: pointer;
  transition: all var(--harmony-duration-fast) var(--harmony-motion-standard);

  &:hover:not(.disabled) {
    box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
  }

  &.disabled {
    background: var(--harmony-comp-divider);
    color: var(--harmony-font-tertiary);
    cursor: not-allowed;
  }
}

.spinner-sm {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: h-spin 0.6s linear infinite;
}


.hidden {
  display: none;
}

/* ===== 动画 ===== */
</style>
<script lang="ts">
// 自动调整textarea高度
function autoResize(e) {
  const el = e.target
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 120) + 'px'
}
</script>
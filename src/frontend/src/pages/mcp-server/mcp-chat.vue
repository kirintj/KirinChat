<template>
  <div class="mcp-chat-container">
    <!-- 历史会话抽屉（覆盖层） -->
    <transition name="drawer">
      <div v-if="sidebarOpen" class="sidebar-overlay" @click.self="sidebarOpen = false">
        <div class="sidebar">
          <div class="sidebar-header">
            <div class="sidebar-title">对话历史</div>
            <HButton type="secondary" size="small" @click="sidebarOpen = false" style="width:32px;height:32px;border-radius:50%;padding:0;">✕</HButton>
          </div>
          <div class="task-list" v-loading="loadingTasks">
            <div v-if="!loadingTasks && tasks.length === 0" class="empty-tasks">
              暂无对话
            </div>
            <div
              v-for="task in tasks"
              :key="task.id"
              :class="['task-item', { active: task.id === currentTaskId }]"
              @click="selectTask(task.id); sidebarOpen = false"
            >
              <div class="task-item-header">
                <div class="task-item-title">{{ task.messages?.length || 0 }} 条消息</div>
                <div class="task-item-time">{{ formatTime(task.created_time) }}</div>
              </div>
              <div class="task-item-preview">
                {{ getLastMessage(task) }}
              </div>
              <div class="task-item-actions">
                <HButton
                  class="task-delete-btn"
                  size="small"
                  type="danger"
                  @click.stop="deleteTask(task.id)"
                  style="width:28px;height:28px;border-radius:50%;padding:0;font-size:12px;"
                >🗑</HButton>
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <!-- 主聊天区域 -->
    <div class="main-content">
      <!-- 顶部操作栏 -->
      <div class="chat-toolbar">
        <div class="toolbar-left"></div>
        <div class="toolbar-right">
          <HButton type="secondary" @click="sidebarOpen = true" size="medium" style="border-radius:20px;font-weight:600;">
            <span style="margin-right: 4px;">📋</span>历史会话
          </HButton>
          <HButton type="primary" @click="createNewTask" size="medium" style="border-radius:20px;background:linear-gradient(135deg,#3b82f6 0%,#8b5cf6 100%);border:none;font-weight:600;">
            ➕ 新建对话
          </HButton>
        </div>
      </div>

      <div class="chat-messages" ref="chatMessagesRef">
        <div v-if="!currentTaskId" class="empty-state">
          <div class="empty-state-icon">📋</div>
          <div class="empty-state-text">开始新的任务</div>
          <div class="empty-state-hint">选择或创建一个任务开始聊天</div>
        </div>
        
        <template v-else>
          <div v-for="(msg, index) in displayMessages" :key="`msg-${index}-${renderKey}`">
            <!-- 用户消息 -->
            <div class="message-group user">
              <div class="message-content-wrapper">
                <div class="message-content">{{ msg.query }}</div>
              </div>
              <div class="message-avatar">
                <HAvatar :size="36" :src="userAvatar" />
              </div>
            </div>
            
            <!-- AI 回复 -->
            <div class="message-group assistant">
              <div class="message-avatar">
                <HAvatar :size="36" src="/src/assets/robot.svg" />
              </div>
              <div class="message-content-wrapper">
                <div class="message-content markdown-body">
                  <!-- 如果是最后一条消息且正在流式输出，且没有内容，显示加载图标 -->
                  <div v-if="isStreaming && index === displayMessages.length - 1 && !msg.content.length" class="loading-spinner">
                    <span class="h-loading-spinner" style="display:inline-block;width:20px;height:20px;border:2px solid #e0e0e0;border-top-color:#6e8efb;border-radius:50%;animation:h-spin 0.6s linear infinite;"></span>
                  </div>
                  <template v-for="(block, bi) in buildBlocks(msg.content)" :key="bi">
                    <!-- 文本块 -->
                    <div v-if="block.type === 'text'" class="text-container" v-html="renderMarkdown(block.data)"></div>
                    <!-- 事件块 -->
                    <div v-else-if="block.type === 'event'" :class="['event-item', block.ev.is_error ? 'ERROR' : (block.ev.status || 'END')]">
                      <div class="event-header" @click="toggleEvent(`${index}-${bi}`)">
                        <span class="event-icon"></span>
                        <span class="event-title">{{ block.ev.title || '事件' }}</span>
                        <span class="event-status">{{ block.ev.is_error ? '失败' : block.ev.status === 'START' ? '进行中' : '已完成' }}</span>
                      </div>
                      <div v-if="block.ev.content && expandedEvents.has(`${index}-${bi}`)" class="event-message">{{ block.ev.content }}</div>
                    </div>
                    <!-- Interrupt 块 -->
                    <div v-else-if="block.type === 'interrupt'" :class="['interrupt-container', { 'processed': block.data.status !== false }]">
                      <div class="interrupt-description" v-html="renderMarkdown(block.data.action_requests?.[0]?.description || '')"></div>
                      <!-- 未处理：显示操作按钮 -->
                      <template v-if="block.data.status === false">
                        <div class="interrupt-buttons">
                          <HButton
                            v-if="block.data.allowed_decisions?.includes('approve')"
                            type="primary"
                            @click="handleApprove"
                            :disabled="isStreaming"
                          >确认创建</HButton>
                          <HButton
                            v-if="block.data.allowed_decisions?.includes('reject')"
                            type="danger"
                            @click="showRejectInput = true"
                            :disabled="isStreaming"
                          >取消并修改</HButton>
                        </div>
                        <!-- 修改意见输入框 -->
                        <div v-if="showRejectInput" class="interrupt-feedback">
                          <textarea
                            v-model="rejectFeedback"
                            :rows="3"
                            placeholder="请输入修改意见（留空则直接取消）"
                            class="interrupt-feedback-input"
                            style="width:100%;padding:10px;border:1px solid var(--color-border);border-radius:var(--radius-md);font-family:inherit;font-size:14px;resize:vertical;background:var(--color-bg-tertiary);color:var(--color-text-primary);"
                          ></textarea>
                          <div class="interrupt-feedback-buttons">
                            <HButton type="secondary" @click="showRejectInput = false; rejectFeedback = ''">取消</HButton>
                            <HButton type="primary" @click="handleReject" :disabled="isStreaming">提交</HButton>
                          </div>
                        </div>
                      </template>
                      <!-- 已处理 -->
                      <div v-else class="processed-hint">（已处理）</div>
                    </div>
                  </template>
                </div>
              </div>
            </div>
          </div>
        </template>
      </div>

      <div class="chat-input-wrapper">
        <div class="chat-input-container">
          <div class="input-with-btn">
            <textarea
              v-model="messageInput"
              placeholder="输入消息... (Enter 发送，Shift+Enter 换行)"
              @keydown="handleKeyDown"
              :disabled="isStreaming"
              class="chat-input"
              style="width:100%;min-height:80px;max-height:200px;padding:14px 56px 14px 16px;border-radius:12px;font-size:15px;line-height:1.6;resize:none;border:1px solid var(--color-border);background:var(--color-bg-secondary);box-shadow:0 2px 8px rgba(0,0,0,0.06);font-family:inherit;color:var(--color-text-primary);"
            ></textarea>
            <HButton
              type="primary"
              @click="sendMessage"
              :disabled="!messageInput.trim() || isStreaming"
              class="send-btn"
              style="position:absolute;right:8px;top:50%;transform:translateY(-50%);width:36px;height:36px;border-radius:50%;padding:0;font-size:16px;box-shadow:0 2px 6px rgba(64,158,255,0.3);"
            >➤</HButton>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>


<script setup lang="ts">
import { ref, onMounted, nextTick, computed } from 'vue'
import { HButton, HAvatar, HMessage } from '@/components/ui'
import { marked } from 'marked'
import {
  getTaskListAPI,
  createTaskAPI,
  deleteTaskAPI,
  sendMessageAPI,
  hitlApproveAPI,
  hitlRejectAPI,
  type MCPTask,
  type MCPMessage,
  type MCPContent
} from '../../apis/mcp-chat'
import { useUserStore } from '../../store/user'

const userStore = useUserStore()
const userAvatar = computed(() => userStore.userInfo?.avatar || '/user.svg')

const tasks = ref<MCPTask[]>([])
const currentTaskId = ref<string | null>(null)
const currentMessages = ref<MCPMessage[]>([])
const streamingContent = ref<MCPContent[]>([])
const streamingQuery = ref<string>('')
const messageInput = ref('')
const isStreaming = ref(false)
const loadingTasks = ref(false)
const chatMessagesRef = ref<HTMLElement>()
const renderKey = ref(0) // 用于强制重新渲染
const showRejectInput = ref(false)
const rejectFeedback = ref('')
const expandedEvents = ref(new Set<string>())
const sidebarOpen = ref(false)

const toggleEvent = (key: string) => {
  if (expandedEvents.value.has(key)) {
    expandedEvents.value.delete(key)
  } else {
    expandedEvents.value.add(key)
  }
  expandedEvents.value = new Set(expandedEvents.value) // 触发响应式更新
}

// 计算属性：合并历史消息和流式消息
const displayMessages = computed(() => {
  if (isStreaming.value && streamingQuery.value) {
    return [...currentMessages.value, {
      query: streamingQuery.value,
      content: streamingContent.value
    }]
  }
  return currentMessages.value
})

// 格式化时间
const formatTime = (dateStr: string) => {
  if (!dateStr) return '刚刚'
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return Math.floor(diff / 60000) + '分钟前'
  if (diff < 86400000) return Math.floor(diff / 3600000) + '小时前'
  if (diff < 604800000) return Math.floor(diff / 86400000) + '天前'
  
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

// 获取最后一条消息
const getLastMessage = (task: MCPTask) => {
  if (!task.messages || task.messages.length === 0) return '新对话'
  return task.messages[task.messages.length - 1].query || '新对话'
}

// 加载任务列表
const loadTaskList = async () => {
  loadingTasks.value = true
  try {
    const response = await getTaskListAPI()
    if (response.data.status_code === 200) {
      tasks.value = response.data.data || []
    } else {
      HMessage.error(response.data.status_message || '加载任务列表失败')
    }
  } catch (error) {
    console.error('加载任务列表失败:', error)
    HMessage.error('加载任务列表失败')
  } finally {
    loadingTasks.value = false
  }
}


// 创建新任务
const createNewTask = async () => {
  try {
    const response = await createTaskAPI()
    if (response.data.status_code === 200 && response.data.data) {
      currentTaskId.value = response.data.data.id
      currentMessages.value = []
      await loadTaskList()
      HMessage.success('创建新对话成功')
    } else {
      HMessage.error(response.data.status_message || '创建对话失败')
    }
  } catch (error) {
    console.error('创建任务失败:', error)
    HMessage.error('创建对话失败')
  }
}

// 选择任务
const selectTask = async (taskId: string) => {
  currentTaskId.value = taskId
  const task = tasks.value.find(t => t.id === taskId)
  if (task) {
    currentMessages.value = task.messages || []
    await nextTick()
    scrollToBottom()
  }
}

// 删除任务
const deleteTask = async (taskId: string) => {
  try {
    const response = await deleteTaskAPI(taskId)
    if (response.data.status_code === 200) {
      if (taskId === currentTaskId.value) {
        currentTaskId.value = null
        currentMessages.value = []
      }
      await loadTaskList()
      HMessage.success('删除成功')
    } else {
      HMessage.error(response.data.status_message || '删除失败')
    }
  } catch (error) {
    console.error('删除任务失败:', error)
    HMessage.error('删除失败')
  }
}

// 将 content 数组构建为渲染块列表
const buildBlocks = (content: MCPContent[]) => {
  if (!content || content.length === 0) return []
  const blocks: any[] = []
  const eventMap = new Map()
  content.forEach(item => {
    if (item.type === 'text') {
      const last = blocks[blocks.length - 1]
      if (last && last.type === 'text') {
        last.data += item.data
      } else {
        blocks.push({ type: 'text', data: item.data })
      }
    } else if (item.type === 'event') {
      const ev = item.data
      const title = ev.title || '事件'
      const existingIdx = eventMap.get(title)
      if (existingIdx !== undefined) {
        blocks[existingIdx].ev = ev
      } else {
        eventMap.set(title, blocks.length)
        blocks.push({ type: 'event', ev })
      }
    } else if (item.type === 'interrupt') {
      blocks.push({ type: 'interrupt', data: item.data })
    }
  })
  return blocks
}

// 渲染 markdown
const renderMarkdown = (text: string) => {
  if (!text) return ''
  return marked.parse(text) as string
}

const escapeHtml = (text: string) => {
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}

// 处理流式响应的通用函数
const processStream = async (response: Response) => {
  const reader = response.body?.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  if (!reader) throw new Error('无法获取响应流')
  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() || ''
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const dataContent = line.substring(6).trim()
        if (dataContent === 'DONE') continue
        try {
          const data = JSON.parse(dataContent)
          if (data.type === 'text') {
            streamingContent.value.push({ type: 'text', data: data.content })
            renderKey.value++
          } else if (data.type === 'event') {
            streamingContent.value.push({ type: 'event', data: data.event || data })
            renderKey.value++
          } else if (data.type === 'interrupt') {
            streamingContent.value.push({ type: 'interrupt', data: data.event || data })
            renderKey.value++
          }
          await nextTick()
          scrollToBottom()
        } catch (e) {
          // ignore parse errors
        }
      }
    }
  }
}

// HITL Approve
const handleApprove = async () => {
  if (isStreaming.value || !currentTaskId.value) return
  isStreaming.value = true
  try {
    const response = await hitlApproveAPI(currentTaskId.value)
    // 把当前 interrupt 标记为已处理
    const lastInterrupt = [...streamingContent.value].reverse().find(c => c.type === 'interrupt')
    if (lastInterrupt) lastInterrupt.data.status = true
    // 把 streaming 内容追加到当前消息的 content 里（找最后一条消息）
    const task = tasks.value.find(t => t.id === currentTaskId.value)
    const lastMsg = task?.messages?.[task.messages.length - 1]
    if (lastMsg) {
      // 更新 interrupt status
      const interruptItem = [...lastMsg.content].reverse().find(c => c.type === 'interrupt')
      if (interruptItem) interruptItem.data.status = true
      streamingQuery.value = lastMsg.query
      streamingContent.value = [...lastMsg.content]
    }
    renderKey.value++
    await processStream(response)
    await loadTaskList()
    const updatedTask = tasks.value.find(t => t.id === currentTaskId.value)
    if (updatedTask) currentMessages.value = updatedTask.messages || []
  } catch (error) {
    console.error('Approve 失败:', error)
    HMessage.error('操作失败')
  } finally {
    isStreaming.value = false
    streamingQuery.value = ''
    streamingContent.value = []
    await nextTick()
    scrollToBottom()
  }
}

// HITL Reject
const handleReject = async () => {
  if (isStreaming.value || !currentTaskId.value) return
  isStreaming.value = true
  showRejectInput.value = false
  const feedback = rejectFeedback.value
  rejectFeedback.value = ''
  try {
    const response = await hitlRejectAPI(currentTaskId.value, feedback)
    const task = tasks.value.find(t => t.id === currentTaskId.value)
    const lastMsg = task?.messages?.[task.messages.length - 1]
    if (lastMsg) {
      const interruptItem = [...lastMsg.content].reverse().find(c => c.type === 'interrupt')
      if (interruptItem) interruptItem.data.status = true
      streamingQuery.value = lastMsg.query
      streamingContent.value = [...lastMsg.content]
    }
    renderKey.value++
    await processStream(response)
    await loadTaskList()
    const updatedTask = tasks.value.find(t => t.id === currentTaskId.value)
    if (updatedTask) currentMessages.value = updatedTask.messages || []
  } catch (error) {
    console.error('Reject 失败:', error)
    HMessage.error('操作失败')
  } finally {
    isStreaming.value = false
    streamingQuery.value = ''
    streamingContent.value = []
    await nextTick()
    scrollToBottom()
  }
}


// 发送消息
const sendMessage = async () => {
  const query = messageInput.value.trim()
  if (!query || isStreaming.value) return
  
  // 如果没有当前任务，自动创建
  if (!currentTaskId.value) {
    try {
      const response = await createTaskAPI()
      if (response.data.status_code === 200 && response.data.data) {
        currentTaskId.value = response.data.data.id
        await loadTaskList()
      } else {
        HMessage.error('创建对话失败')
        return
      }
    } catch (error) {
      console.error('创建任务失败:', error)
      HMessage.error('创建对话失败')
      return
    }
  }
  
  const userQuery = query
  messageInput.value = ''
  isStreaming.value = true
  
  // 初始化流式状态
  streamingQuery.value = userQuery
  streamingContent.value = []
  renderKey.value = 0
  
  await nextTick()
  scrollToBottom()
  
  try {
    const response = await sendMessageAPI(userQuery, currentTaskId.value)
    await processStream(response)
    
    // 流式完成后，重新加载任务列表
    await loadTaskList()
    
    // 重新选择当前任务以刷新消息
    const task = tasks.value.find(t => t.id === currentTaskId.value)
    if (task) {
      currentMessages.value = task.messages || []
    }
    
  } catch (error) {
    console.error('发送消息失败:', error)
    HMessage.error('发送消息失败')
  } finally {
    // 清空流式状态
    isStreaming.value = false
    streamingQuery.value = ''
    streamingContent.value = []
    await nextTick()
    scrollToBottom()
  }
}

// 处理键盘事件
const handleKeyDown = (event: KeyboardEvent) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    sendMessage()
  }
}

// 滚动到底部
const scrollToBottom = () => {
  if (chatMessagesRef.value) {
    chatMessagesRef.value.scrollTop = chatMessagesRef.value.scrollHeight
  }
}

onMounted(() => {
  loadTaskList()
})
</script>


<style lang="scss" scoped>
.mcp-chat-container {
  display: flex;
  height: 100%;
  background: var(--color-bg);
  overflow: hidden;
}

// 抽屉覆盖层
.sidebar-overlay {
  position: fixed;
  inset: 0;
  background: var(--shadow-lg);
  z-index: 100;
  display: flex;
}

.sidebar {
  width: 280px;
  height: 100%;
  background: var(--color-bg);
  display: flex;
  flex-direction: column;
  box-shadow: 4px 0 24px var(--shadow-md);

  .sidebar-header {
    padding: 16px;
    border-bottom: 1px solid var(--color-border);
    display: flex;
    align-items: center;
    justify-content: space-between;

    .sidebar-title {
      font-size: var(--font-size-lg);
      font-weight: 600;
      color: var(--color-text-primary);
    }
  }

  .task-list {
    flex: 1;
    overflow-y: auto;
    padding: 8px;

    .empty-tasks {
      text-align: center;
      padding: 20px;
      color: var(--color-text-secondary);
      font-size: var(--font-size-base);
    }

    .task-item {
      padding: 12px;
      margin-bottom: 4px;
      background: transparent;
      border-radius: var(--radius-md);
      cursor: pointer;
      transition: all 0.2s;
      border: 1px solid transparent;
      position: relative;

      &:hover {
        background: var(--color-bg-tertiary);

        .task-item-actions {
          opacity: 1;
        }
      }

      &.active {
        background: var(--color-bg-secondary);
        border-color: var(--color-primary);
      }

      .task-item-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 6px;

        .task-item-title {
          font-size: var(--font-size-base);
          font-weight: 500;
          color: var(--color-text-primary);
        }

        .task-item-time {
          font-size: 11px;
          color: var(--color-text-secondary);
        }
      }

      .task-item-preview {
        font-size: var(--font-size-xs);
        color: var(--color-text-secondary);
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        margin-bottom: 8px;
      }

      .task-item-actions {
        display: flex;
        justify-content: flex-end;
        opacity: 0;
        transition: opacity 0.2s;
      }
    }
  }
}

// 抽屉动画
.drawer-enter-active,
.drawer-leave-active {
  transition: opacity 0.25s ease;
  .sidebar {
    transition: transform 0.25s ease;
  }
}
.drawer-enter-from,
.drawer-leave-to {
  opacity: 0;
  .sidebar {
    transform: translateX(-100%);
  }
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--color-bg);
  position: relative;

  .chat-toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--spacing-lg) var(--spacing-2xl);
    background: transparent;
    border-bottom: none;

    .toolbar-left {
      display: flex;
      align-items: center;
      gap: 10px;

      .toolbar-icon {
        width: 28px;
        height: 28px;
      }

      .toolbar-title {
        font-size: var(--font-size-xl);
        font-weight: 600;
        background: var(--color-primary);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
      }
    }

    .toolbar-right {
      display: flex;
      gap: 12px;
    }
  }
  
  .chat-messages {
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
    padding: 24px 24px 120px;
    
    .empty-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100%;
      color: var(--color-text-secondary);
      
      .empty-state-icon {
        font-size: 64px;
        margin-bottom: 16px;
        opacity: 0.5;
      }
      
      .empty-state-text {
        font-size: var(--font-size-xl);
        margin-bottom: 8px;
        font-weight: 500;
      }
      
      .empty-state-hint {
        font-size: var(--font-size-base);
        opacity: 0.7;
      }
    }
    
    .message-group {
      margin-bottom: 24px;
      display: flex;
      gap: 12px;
      min-width: 0;
      width: 100%;
      
      &.user {
        justify-content: flex-end;
        
        .message-avatar {
          order: 2;
        }
      }
      
      &.assistant {
        justify-content: flex-start;
      }
      
      .message-avatar {
        flex-shrink: 0;
      }
      
      .message-content-wrapper {
        max-width: 65%;
        min-width: 0;
        display: flex;
        flex-direction: column;
        gap: 8px;
      }
      
      .message-content {
        padding: var(--spacing-md) var(--spacing-lg);
        border-radius: var(--radius-lg);
        line-height: 1.5;
        font-size: var(--font-size-lg);
        word-wrap: break-word;
        overflow-wrap: break-word;
        word-break: break-word;
        overflow: hidden;
      }
      
      &.user .message-content {
        background: var(--color-primary);
        color: white;
        border-bottom-right-radius: 4px;
      }
      
      &.assistant .message-content {
        background: var(--color-bg-tertiary);
        color: var(--color-text-primary);
        border-bottom-left-radius: 4px;
      }
    }
  }

  .loading-spinner {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 28px;
    color: var(--color-primary);
  }
  
  .chat-input-wrapper {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    padding: var(--spacing-lg) var(--spacing-2xl) 24px;
    background: transparent;
    border-top: none;
    
    .chat-input-container {
      width: 66.67%;
      margin: 0 auto;

      .input-with-btn {
        position: relative;

        .chat-input {
          &:focus {
            border-color: var(--color-primary);
            box-shadow: 0 2px 12px var(--color-primary-bg);
          }
        }

        .send-btn {
          transition: transform 0.15s, box-shadow 0.15s;

          &:not(:disabled):hover {
            transform: translateY(-50%) scale(1.08);
            box-shadow: 0 4px 10px var(--color-primary-bg);
          }
        }
      }
    }
  }
}

// 事件样式
:deep(.event-item) {
  margin: 0 0 4px 0;
  padding: 8px 12px;
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  border-left: 3px solid;
  
  &.START {
    background: var(--color-primary-bg);
    border-left-color: var(--color-primary);
  }
  
  &.END {
    background: var(--color-success-bg);
    border-left-color: var(--color-success);
  }
  
  &.ERROR {
    background: var(--color-danger-bg);
    border-left-color: var(--color-danger);
  }
  
  .event-header {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    user-select: none;
  }
  
  .event-icon {
    width: 16px;
    height: 16px;
    border-radius: var(--radius-full);
    flex-shrink: 0;
  }
  
  &.START .event-icon {
    background: var(--color-primary);
    animation: pulse 1.5s ease-in-out infinite;
  }
  
  &.END .event-icon {
    background: var(--color-success);
  }
  
  &.ERROR .event-icon {
    background: var(--color-danger);
  }
  
  .event-title {
    font-weight: 600;
    flex: 1;
  }
  
  &.START .event-title {
    color: var(--color-primary);
  }
  
  &.END .event-title {
    color: var(--color-success);
  }
  
  &.ERROR .event-title {
    color: var(--color-danger);
  }
  
  .event-status {
    font-size: 11px;
    padding: 2px 8px;
    border-radius: var(--radius-md);
    font-weight: 500;
  }
  
  &.START .event-status {
    background: var(--color-primary-bg);
    color: var(--color-primary);
  }
  
  &.END .event-status {
    background: var(--color-success-bg);
    color: var(--color-success);
  }
  
  &.ERROR .event-status {
    background: var(--color-danger-bg);
    color: var(--color-danger);
  }
  
  .event-message {
    margin-top: 8px;
    padding: 8px;
    background: var(--color-bg-overlay);
    border-radius: var(--radius-sm);
    font-size: var(--font-size-xs);
    line-height: 1.5;
  }
}

.interrupt-buttons {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 12px;
}

.interrupt-feedback {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--color-primary-bg);
  
  .interrupt-feedback-input {
    margin-bottom: 10px;
  }
  
  .interrupt-feedback-buttons {
    display: flex;
    gap: 10px;
    justify-content: flex-end;
  }
}

.processed-hint {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  margin-top: 8px;
}

// Interrupt 样式
:deep(.interrupt-container) {
  margin: 8px 0;
  padding: 16px;
  background: var(--color-primary-bg);
  border: 1px solid var(--color-primary-bg);
  border-radius: var(--radius-lg);
  
  &.processed {
    opacity: 0.6;
  }
  
  .interrupt-description {
    font-size: var(--font-size-base);
    line-height: 1.5;
    margin-bottom: 12px;
    
    p { margin: 0 0 8px 0; &:last-child { margin-bottom: 0; } }
    code { background: var(--color-border); padding: 2px 5px; border-radius: var(--radius-sm); font-family: var(--font-family); font-size: var(--font-size-sm); }
    pre { background: var(--shadow-lg); padding: 12px; border-radius: var(--radius-md); overflow-x: auto; margin: 8px 0; code { background: none; padding: 0; } }
  }
}

// Markdown 样式
:deep(.markdown-body) {
  p {
    margin: 0 0 4px 0;
    
    &:last-child {
      margin-bottom: 0;
    }
  }
  
  h1, h2, h3, h4 {
    margin: 12px 0 6px 0;
    font-weight: 600;
  }
  
  ul, ol {
    padding-left: 20px;
    margin: 6px 0;
  }
  
  li {
    margin: 3px 0;
  }
  
  code {
    background: var(--color-border);
    padding: 2px 5px;
    border-radius: var(--radius-sm);
    font-family: var(--font-family);
    font-size: var(--font-size-sm);
  }
  
  pre {
    background: var(--shadow-lg);
    padding: 12px;
    border-radius: var(--radius-md);
    overflow-x: auto;
    margin: 8px 0;
    
    code {
      background: none;
      padding: 0;
    }
  }
  
  blockquote {
    border-left: 3px solid var(--color-border);
    padding-left: 12px;
    margin: 8px 0;
    color: var(--color-text-secondary);
  }
  
  table {
    border-collapse: collapse;
    width: 100%;
    margin: 8px 0;
    
    th, td {
      border: 1px solid var(--color-border);
      padding: 6px 10px;
      text-align: center;
    }
    
    th {
      font-weight: 600;
    }
  }
  
  a {
    color: var(--color-primary);
    text-decoration: underline;
  }
  
  hr {
    border: none;
    border-top: 1px solid var(--color-border);
    margin: 10px 0;
  }
}
</style>


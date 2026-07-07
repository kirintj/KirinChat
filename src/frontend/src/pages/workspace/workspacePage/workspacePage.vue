<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { HMessage } from '@/components/ui'
import { MdPreview } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import { 
  generateLingSeekGuidePromptAPI, 
  regenerateLingSeekGuidePromptAPI
} from '../../../apis/lingseek'
import { getWorkspaceSessionInfoAPI } from '../../../apis/workspace'

const route = useRoute()
const router = useRouter()

// 历史记录相关
interface HistoryContext {
  query: string
  guide_prompt?: string
  task?: any[]
  answer: string
}

const historyContexts = ref<HistoryContext[]>([])
const showHistory = ref(false)
const isExistingSession = ref(false)  // 标记是否为已有会话
const expandedItems = ref<Set<number>>(new Set())  // 记录展开的项目

// 切换展开/收起
const toggleExpand = (index: number) => {
  if (expandedItems.value.has(index)) {
    expandedItems.value.delete(index)
  } else {
    expandedItems.value.add(index)
  }
}

// Markdown 渲染函数（增强版）
const parseMarkdown = (text: string): string => {
  if (!text) return ''
  
  let html = text
  
  // 1. 先处理代码块（避免代码块内容被误处理）
  html = html.replace(/```([\s\S]*?)```/gim, (match, code) => {
    return `<pre><code>${code}</code></pre>`
  })
  
  // 2. 处理标题（按从多到少的顺序）
  html = html.replace(/^#### (.*$)/gim, '<h4>$1</h4>')
  html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>')
  html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>')
  html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>')
  
  // 3. 处理嵌套列表（支持多级缩进）
  // 先标记所有列表项的层级（根据缩进）
  const lines = html.split('\n')
  const processedLines = lines.map(line => {
    // 三级列表（6个空格或3个tab + -）
    if (/^      - (.*)$/.test(line) || /^\t\t\t- (.*)$/.test(line)) {
      return line.replace(/^      - (.*)$/, '<li-ul-3>$1</li-ul-3>')
                 .replace(/^\t\t\t- (.*)$/, '<li-ul-3>$1</li-ul-3>')
    }
    // 二级列表（4个空格或2个tab + -）
    if (/^    - (.*)$/.test(line) || /^\t\t- (.*)$/.test(line)) {
      return line.replace(/^    - (.*)$/, '<li-ul-2>$1</li-ul-2>')
                 .replace(/^\t\t- (.*)$/, '<li-ul-2>$1</li-ul-2>')
    }
    // 二级列表（2个空格或1个tab + -）
    if (/^  - (.*)$/.test(line) || /^\t- (.*)$/.test(line)) {
      return line.replace(/^  - (.*)$/, '<li-ul-2>$1</li-ul-2>')
                 .replace(/^\t- (.*)$/, '<li-ul-2>$1</li-ul-2>')
    }
    // 一级无序列表
    if (/^- (.*)$/.test(line)) {
      return line.replace(/^- (.*)$/, '<li-ul-1>$1</li-ul-1>')
    }
    // 有序列表
    if (/^\d+\. (.*)$/.test(line)) {
      return line.replace(/^\d+\. (.*)$/, '<li-ol>$1</li-ol>')
    }
    return line
  })
  html = processedLines.join('\n')
  
  // 4. 处理三级列表
  html = html.replace(/(<li-ul-3>.*?<\/li-ul-3>(\n)*)+/gim, (match) => {
    const items = match.replace(/<li-ul-3>/g, '<li>').replace(/<\/li-ul-3>/g, '</li>')
    return '<ul class="list-level-3">' + items + '</ul>'
  })
  
  // 5. 处理二级列表
  html = html.replace(/(<li-ul-2>.*?<\/li-ul-2>(\n)*)+/gim, (match) => {
    const items = match.replace(/<li-ul-2>/g, '<li>').replace(/<\/li-ul-2>/g, '</li>')
    return '<ul class="list-level-2">' + items + '</ul>'
  })
  
  // 6. 处理一级无序列表
  html = html.replace(/(<li-ul-1>.*?<\/li-ul-1>(\n)*)+/gim, (match) => {
    const items = match.replace(/<li-ul-1>/g, '<li>').replace(/<\/li-ul-1>/g, '</li>')
    return '<ul class="list-level-1">' + items + '</ul>'
  })
  
  // 7. 处理有序列表
  html = html.replace(/(<li-ol>.*?<\/li-ol>(\n)*)+/gim, (match) => {
    const items = match.replace(/<li-ol>/g, '<li>').replace(/<\/li-ol>/g, '</li>')
    return '<ol>' + items + '</ol>'
  })
  
  // 8. 处理粗体（** 或 __）
  html = html.replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
  html = html.replace(/__(.*?)__/gim, '<strong>$1</strong>')
  
  // 9. 处理斜体（* 或 _，但要避免与粗体冲突）
  html = html.replace(/(?<!\*)\*(?!\*)([^\*]+)\*(?!\*)/gim, '<em>$1</em>')
  html = html.replace(/(?<!_)_(?!_)([^_]+)_(?!_)/gim, '<em>$1</em>')
  
  // 10. 处理行内代码
  html = html.replace(/`([^`]+)`/gim, '<code>$1</code>')
  
  // 11. 处理链接 [text](url)
  html = html.replace(/\[([^\]]+)\]\(([^\)]+)\)/gim, '<a href="$2" target="_blank">$1</a>')
  
  // 12. 处理引用（> 开头）
  html = html.replace(/^> (.*$)/gim, '<blockquote>$1</blockquote>')
  
  // 13. 处理分隔线（--- 或 ***）
  html = html.replace(/^(---|\*\*\*)$/gim, '<hr>')
  
  // 14. 处理换行（两个空格+换行 或 单独的换行）
  html = html.replace(/  \n/g, '<br>')
  html = html.replace(/\n\n+/g, '</p><p>')  // 双换行或多换行才分段
  html = html.replace(/\n/g, '<br>')
  
  // 15. 包裹段落
  html = '<p>' + html + '</p>'
  
  // 16. 清理多余的空段落
  html = html.replace(/<p><\/p>/g, '')
  html = html.replace(/<p>(<h[1-6]>)/g, '$1')
  html = html.replace(/(<\/h[1-6]>)<\/p>/g, '$1')
  html = html.replace(/<p>(<ul>)/g, '$1')
  html = html.replace(/(<\/ul>)<\/p>/g, '$1')
  html = html.replace(/<p>(<ol>)/g, '$1')
  html = html.replace(/(<\/ol>)<\/p>/g, '$1')
  html = html.replace(/<p>(<pre>)/g, '$1')
  html = html.replace(/(<\/pre>)<\/p>/g, '$1')
  html = html.replace(/<p>(<blockquote>)/g, '$1')
  html = html.replace(/(<\/blockquote>)<\/p>/g, '$1')
  html = html.replace(/<p>(<hr>)<\/p>/g, '$1')
  
  return html
}

// 状态管理
const userQuery = ref('')
const guidePrompt = ref('')
const isStreaming = ref(false)
const isEditable = ref(false)
const selectedTools = ref<string[]>([])
const webSearchEnabled = ref(false)
const showFeedbackDialog = ref(false)
const feedbackText = ref('')

// 保存第一次生成的参数，用于重新生成
const originalParams = ref({
  query: '',
  tools: [] as string[],
  web_search: false,
  plugins: [] as string[],
  mcp_servers: [] as string[]
})

// 计算属性：实时渲染 Markdown
const renderedMarkdown = computed(() => {
  if (!guidePrompt.value) {
    return '<p class="placeholder">正在生成指导手册...</p>'
  }
  return parseMarkdown(guidePrompt.value)
})

// 监听 guidePrompt 变化，用于调试
watch(guidePrompt, (newVal) => {
  console.log('📝 guidePrompt 已更新，长度:', newVal.length)
})

// 初始化
onMounted(async () => {
  console.log('=== workspacePage onMounted 开始 ===')
  console.log('路由参数:', route.query)
  
  // 检查是否是打开已有会话
  const sessionId = route.query.session_id as string
  
  if (sessionId) {
    // 打开已有会话，获取会话信息
    console.log('打开已有会话:', sessionId)
    isExistingSession.value = true
    await loadSessionInfo(sessionId)
  } else {
    // 标记为新会话
    isExistingSession.value = false
    // 新建会话
    // 从路由参数获取信息
    userQuery.value = route.query.query as string || ''
    console.log('userQuery:', userQuery.value)
    
    const tools = route.query.tools as string
    selectedTools.value = tools ? JSON.parse(tools) : []
    console.log('selectedTools:', selectedTools.value)
    
    webSearchEnabled.value = route.query.webSearch === 'true'
    console.log('webSearchEnabled:', webSearchEnabled.value)

    const mcpQuery = route.query.mcp_servers as string
    const selectedMcpServers = mcpQuery ? JSON.parse(mcpQuery) : []
    console.log('mcp_servers:', selectedMcpServers)

    // 如果有查询内容，立即开始生成（后端会创建会话）
    if (userQuery.value) {
      console.log('检测到 userQuery，开始调用接口')
      
      // 保存第一次生成的参数
      originalParams.value = {
        query: userQuery.value,
        tools: selectedTools.value,
        web_search: webSearchEnabled.value,
        plugins: selectedTools.value, // plugins 和 tools 是同一个字段
        mcp_servers: selectedMcpServers
      }
      
      startGenerateGuidePrompt()
    } else {
      console.warn('⚠️ userQuery 为空，不会调用接口')
    }
  }
  
  console.log('=== workspacePage onMounted 结束 ===')
})

// 加载会话信息
const loadSessionInfo = async (sessionId: string) => {
  try {
    const response = await getWorkspaceSessionInfoAPI(sessionId)
    if (response.data.status_code === 200) {
      const sessionData = response.data.data
      console.log('会话信息:', sessionData)
      
      // 提取历史记录
      if (sessionData.contexts && Array.isArray(sessionData.contexts)) {
        historyContexts.value = sessionData.contexts
        showHistory.value = historyContexts.value.length > 0
        console.log('历史记录数量:', historyContexts.value.length)
      }
    } else {
      HMessage.error('获取会话信息失败')
    }
  } catch (error) {
    console.error('加载会话信息出错:', error)
    HMessage.error('加载会话信息失败')
  }
}

// 开始生成指导手册（后端会创建会话）
const startGenerateGuidePrompt = async () => {
  console.log('=== startGenerateGuidePrompt 开始 ===')
  console.log('用户问题:', userQuery.value)
  console.log('选中工具:', selectedTools.value)
  console.log('联网搜索:', webSearchEnabled.value)
  
  guidePrompt.value = ''
  isStreaming.value = true
  isEditable.value = false

  try {
    await generateLingSeekGuidePromptAPI(
      {
        query: userQuery.value,
        tools: selectedTools.value,
        web_search: webSearchEnabled.value,
        mcp_servers: originalParams.value.mcp_servers
      },
      (data) => {
        // 处理流式数据（纯文本），立即更新
        console.log('📨 接收到数据块:', data)
        guidePrompt.value = guidePrompt.value + data
        console.log('📝 当前 guidePrompt 总长度:', guidePrompt.value.length)
      },
      (error) => {
        console.error('❌ 生成过程出错:', error)
        HMessage.error('生成指导手册失败')
        isStreaming.value = false
        isEditable.value = true
      },
      () => {
        // 流结束
        console.log('✅ 流式传输结束')
        isStreaming.value = false
        isEditable.value = true
        HMessage.success('指导手册生成完成，您可以进行修改')
      }
    )
  } catch (error) {
    console.error('生成指导手册出错:', error)
    HMessage.error('请求失败，请检查网络连接')
    isStreaming.value = false
    isEditable.value = true
  }
}

// 打开重新生成对话框
const handleRegenerate = () => {
  if (!guidePrompt.value.trim()) {
    HMessage.warning('请先生成或编辑指导手册')
    return
  }
  
  feedbackText.value = ''
  showFeedbackDialog.value = true
}

// 取消重新生成
const handleCancelRegenerate = () => {
  showFeedbackDialog.value = false
  feedbackText.value = ''
}

// 确认重新生成
const handleConfirmRegenerate = async () => {
  if (!feedbackText.value.trim()) {
    HMessage.warning('请输入您的想法或修改意见')
    return
  }

  console.log('开始重新生成，用户反馈:', feedbackText.value)
  
  const currentPrompt = guidePrompt.value
  const feedback = feedbackText.value
  
  // 关闭对话框
  showFeedbackDialog.value = false
  
  // 清空文本框，准备重新输出
  guidePrompt.value = ''
  isStreaming.value = true
  isEditable.value = false

  try {
    await regenerateLingSeekGuidePromptAPI(
      {
        query: originalParams.value.query,
        guide_prompt: currentPrompt,
        feedback: feedback,
        web_search: originalParams.value.web_search,
        plugins: originalParams.value.plugins,
        mcp_servers: originalParams.value.mcp_servers
      },
      (data) => {
        // 处理流式数据（纯文本），立即更新
        console.log('📨 接收到数据块:', data)
        guidePrompt.value = guidePrompt.value + data
      },
      (error) => {
        console.error('❌ 重新生成过程出错:', error)
        HMessage.error('重新生成失败')
        isStreaming.value = false
        isEditable.value = true
      },
      () => {
        console.log('✅ 重新生成完成')
        isStreaming.value = false
        isEditable.value = true
        HMessage.success('重新生成完成')
      }
    )
  } catch (error) {
    console.error('重新生成出错:', error)
    HMessage.error('请求失败，请检查网络连接')
    isStreaming.value = false
    isEditable.value = true
  }
}

// 开始执行任务 - 跳转到任务流程图页面
const handleStartTask = () => {
  if (!guidePrompt.value.trim()) {
    HMessage.warning('请先生成指导手册')
    return
  }

  console.log('跳转到任务流程图页面')
  console.log('用户问题:', originalParams.value.query)
  console.log('指导手册:', guidePrompt.value)
  console.log('联网搜索:', originalParams.value.web_search)
  console.log('插件列表:', originalParams.value.plugins)

  // 跳转到任务流程图页面，并传递参数
  router.push({
    name: 'taskGraphPage',
    query: {
      query: originalParams.value.query,
      guide_prompt: guidePrompt.value,
      webSearch: String(originalParams.value.web_search),
      plugins: JSON.stringify(originalParams.value.plugins),
      mcp_servers: JSON.stringify(originalParams.value.mcp_servers)
    }
  })
}
</script>

<template>
  <div class="workspace-chat-page">
    <div class="chat-container">
      <!-- 历史记录展示区（占满整个区域） -->
      <div v-if="showHistory" class="history-section-fullscreen">
        <div class="history-header">
          <div class="header-left">
            <span class="history-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <path d="M4 4H20C21.1046 4 22 4.89543 22 6V16C22 17.1046 21.1046 18 20 18H8L4 21V6C4 4.89543 4.89543 4 4 4Z" stroke="currentColor" stroke-width="1.5"/>
                <line x1="8" y1="10" x2="16" y2="10" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
                <line x1="8" y1="13" x2="14" y2="13" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
              </svg>
            </span>
            <h2 class="history-title">对话历史</h2>
          </div>
          <div class="header-right">
            <span class="history-count">共 {{ historyContexts.length }} 条对话</span>
          </div>
        </div>
        
        <div class="history-content">
          <div 
            v-for="(context, index) in historyContexts" 
            :key="index"
            class="conversation-item"
            :class="{ 'expanded': expandedItems.has(index) }"
          >
            <!-- 对话头部（可点击展开/收起） -->
            <div class="conversation-header" @click="toggleExpand(index)">
              <div class="header-info">
                <span class="conversation-number">#{{ index + 1 }}</span>
                <span class="conversation-preview">{{ context.query.substring(0, 100) }}{{ context.query.length > 100 ? '...' : '' }}</span>
              </div>
              <div :class="['expand-icon', { expanded: expandedItems.has(index) }]">
                <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                  <path d="M4 2L8 6L4 10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </div>
            </div>
            
            <!-- 对话内容（可展开） -->
            <div v-show="expandedItems.has(index)" class="conversation-content">
              <!-- 用户问题 -->
              <div class="message-block user-block">
                <div class="message-header">
                  <span class="message-icon">
                    <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                      <circle cx="9" cy="6" r="3" stroke="currentColor" stroke-width="1.3"/>
                      <path d="M3 16C3 13.2386 5.68629 11 9 11C12.3137 11 15 13.2386 15 16" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
                    </svg>
                  </span>
                  <span class="message-title">用户提问</span>
                </div>
                <div class="message-body">
                  <MdPreview 
                    :editorId="`user-query-${index}`"
                    :modelValue="context.query"
                  />
                </div>
              </div>
              
              <!-- AI回答 -->
              <div class="message-block ai-block">
                <div class="message-header">
                  <span class="message-icon">
                    <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                      <rect x="2" y="5" width="14" height="10" rx="2" stroke="currentColor" stroke-width="1.3"/>
                      <circle cx="6" cy="10" r="1.5" fill="currentColor"/>
                      <circle cx="12" cy="10" r="1.5" fill="currentColor"/>
                      <path d="M9 5V2" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
                      <path d="M6 2H12" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
                      <line x1="4" y1="13" x2="14" y2="13" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
                    </svg>
                  </span>
                  <span class="message-title">AI回答</span>
                </div>
                <div class="message-body">
                  <MdPreview 
                    :editorId="`ai-answer-${index}`"
                    :modelValue="context.answer"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 指导手册编辑器（仅在新建会话时显示） -->
      <div v-if="!isExistingSession" class="editor-section">
        <div class="editor-header">
          <div class="header-left">
            <span class="editor-icon">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M4 2H11L16 7V17C16 17.5523 15.5523 18 15 18H4C3.44772 18 3 17.5523 3 17V3C3 2.44772 3.44772 2 4 2Z" stroke="currentColor" stroke-width="1.3"/>
              <path d="M11 2V7H16" stroke="currentColor" stroke-width="1.3"/>
              <line x1="6" y1="10" x2="13" y2="10" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
              <line x1="6" y1="13" x2="13" y2="13" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
            </svg>
          </span>
          <span class="editor-title">麒麟智聊指导手册</span>
          </div>
          <div class="header-right">
            <span v-if="isStreaming" class="streaming-indicator">
              <span class="loading-dot"></span>
              <span class="loading-text">生成中...</span>
            </span>
            <span v-else-if="isEditable" class="editable-indicator">
              <span class="edit-icon">
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                    <path d="M2 12L10 4L12 6L4 14L2 12Z" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/>
                    <path d="M8 2L14 8" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
                  </svg>
                </span>
                <span class="edit-text">可编辑</span>
            </span>
          </div>
        </div>

        <div class="editor-wrapper">
          <!-- 双栏布局：左边原始文本，右边实时预览 -->
          <div class="editor-content">
            <!-- 左侧：Markdown 原始文本编辑区 -->
            <div class="editor-pane">
              <div class="pane-header">原始文本</div>
              <textarea
                v-model="guidePrompt"
                :readonly="!isEditable"
                class="markdown-editor"
                placeholder="正在生成指导手册..."
              ></textarea>
            </div>
            
            <!-- 右侧：Markdown 预览区 -->
            <div class="preview-pane">
              <div class="pane-header">预览</div>
              <div 
                class="markdown-preview" 
                v-html="renderedMarkdown"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <!-- 操作按钮区（仅在新建会话时显示） -->
      <div v-if="!isExistingSession" class="action-section">
        <div class="action-buttons">
          <button
            @click="handleRegenerate"
            :disabled="isStreaming"
            class="action-btn regenerate-btn"
          >
            <span class="btn-icon">
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                    <path d="M2 8C2 4.68629 4.68629 2 8 2C10.5 2 12.6424 3.54029 13.5 5.5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
                    <path d="M14 8C14 11.3137 11.3137 14 8 14C5.5 14 3.35758 12.4597 2.5 10.5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
                    <path d="M14 2V5.5H10.5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M2 14V10.5H5.5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </span>
                <span class="btn-text">重新生成</span>
          </button>
          
          <button
            @click="handleStartTask"
            :disabled="isStreaming || !guidePrompt.trim()"
            class="action-btn start-btn"
          >
            <span class="btn-icon">
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                    <path d="M3 2L12.5 8L3 14V2Z" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/>
                  </svg>
                </span>
                <span class="btn-text">开始执行</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 自定义重新生成反馈弹窗 -->
    <div v-if="showFeedbackDialog" class="feedback-modal-overlay" @click="handleCancelRegenerate">
      <div class="feedback-modal" @click.stop>
        <div class="modal-header">
          <h3 class="modal-title">重新生成指导手册</h3>
          <button @click="handleCancelRegenerate" class="close-btn">
            <span>×</span>
          </button>
        </div>
        
        <div class="modal-body">
          <p class="feedback-tip">请告诉我您希望如何优化这个指导手册：</p>
          <div class="input-wrapper">
            <textarea
              v-model="feedbackText"
              placeholder="例如：更加详细一些、更简洁、调整某个步骤等..."
              maxlength="500"
              class="feedback-textarea"
              rows="4"
            ></textarea>
            <div class="char-count">{{ feedbackText.length }}/500</div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button @click="handleCancelRegenerate" class="cancel-btn">
            取消
          </button>
          <button @click="handleConfirmRegenerate" class="confirm-btn">
            确认重新生成
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
/* =============================
   workspacePage — 指导手册编辑器
   ============================= */

.workspace-chat-page {
  width: 100%;
  height: 100%;
  background: var(--harmony-comp-background-secondary);
  padding: 0;
  overflow: hidden;
}

.chat-container {
  max-width: 1400px;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: 0;
}

/* 历史记录区域 */
.history-section-fullscreen {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--harmony-comp-background-primary);
  border: 1px solid var(--harmony-comp-divider);
  border-radius: 14px;
  overflow: hidden;

  .history-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    background: var(--harmony-comp-background-primary);
    border-bottom: 1px solid var(--harmony-comp-divider);

    .header-left {
      display: flex;
      align-items: center;
      gap: 10px;

      .history-icon {
        width: 36px;
        height: 36px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--harmony-brand));
        color: var(--harmony-comp-background-primary);
        border-radius: 10px;

        svg {
          width: 20px;
          height: 20px;
        }
      }

      .history-title {
        margin: 0;
        font-size: var(--harmony-font-size-body-m);
        font-weight: 700;
        color: var(--harmony-font-primary);
      }
    }

    .header-right {
      .history-count {
        font-size: var(--harmony-font-size-body-s);
        color: var(--harmony-font-secondary);
        background: var(--harmony-comp-background-secondary);
        padding: 6px 14px;
        border-radius: 999px;
        border: 1px solid var(--harmony-comp-divider);
      }
    }
  }

  .history-content {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
    background: var(--harmony-comp-background-secondary);

    scrollbar-width: none;
    -ms-overflow-style: none;
    &::-webkit-scrollbar { display: none; }

    .conversation-item {
      background: var(--harmony-comp-background-primary);
      border: 1px solid var(--harmony-comp-divider);
      border-radius: var(--harmony-corner-radius-level8);
      margin-bottom: 12px;
      overflow: hidden;
      transition: box-shadow 0.2s ease;

      &:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
      }

      &:last-child {
        margin-bottom: 0;
      }

      .conversation-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 14px 16px;
        background: var(--harmony-comp-background-primary);
        cursor: pointer;
        border-bottom: 1px solid var(--harmony-comp-divider);

        &:hover {
          background: var(--harmony-comp-background-secondary);
        }

        .header-info {
          display: flex;
          align-items: center;
          gap: 10px;
          flex: 1;
          min-width: 0;

          .conversation-number {
            font-size: var(--harmony-font-size-body-s);
            font-weight: 700;
            color: var(--harmony-brand));
            background: var(--harmony-comp-emphasize-tertiary);
            padding: 3px 10px;
            border-radius: 999px;
            flex-shrink: 0;
          }

          .conversation-preview {
            font-size: var(--harmony-font-size-subtitle-s);
            color: var(--harmony-font-primary);
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
          }
        }

        .expand-icon {
          display: flex;
          align-items: center;
          color: var(--harmony-font-tertiary);
          margin-left: 10px;
          transition: transform 0.2s ease;

          &.expanded {
            transform: rotate(90deg);
          }
        }
      }

      .conversation-content {
        padding: 16px;
        background: var(--harmony-comp-background-primary);

        .message-block {
          margin-bottom: 16px;

          &:last-child {
            margin-bottom: 0;
          }

          .message-header {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 10px;
            padding-bottom: 8px;
            border-bottom: 1px solid var(--harmony-comp-divider);

            .message-icon {
              width: 28px;
              height: 28px;
              display: flex;
              align-items: center;
              justify-content: center;
              border-radius: 50%;
              color: var(--harmony-font-primary);

              svg {
                width: 16px;
                height: 16px;
              }
            }

            .message-title {
              font-size: var(--harmony-font-size-body-s);
              font-weight: 600;
              color: var(--harmony-font-secondary);
            }
          }

          .message-body {
            background: var(--harmony-comp-background-secondary);
            border-radius: var(--harmony-corner-radius-level6);
            padding: 14px;
            border: 1px solid var(--harmony-comp-divider);

            :deep(.md-editor-preview) {
              background: transparent;
              padding: 0;

              p {
                margin: 8px 0;
                line-height: 1.8;
                color: var(--harmony-font-primary);
              }

              h1, h2, h3, h4, h5, h6 {
                margin: 16px 0 8px;
                font-weight: 600;
                color: var(--harmony-font-primary);
              }

              ul, ol {
                margin: 10px 0;
                padding-left: 24px;

                li {
                  margin: 4px 0;
                  line-height: 1.6;
                  color: var(--harmony-font-primary);
                }
              }

              code {
                background: var(--harmony-comp-background-secondary);
                padding: 2px 6px;
                border-radius: 4px;
                font-family: var(--harmony-font-family);
                font-size: 0.9em;
                color: var(--harmony-warning);
              }

              pre {
                background: var(--harmony-font-primary);
                color: var(--harmony-comp-background-primary);
                padding: 14px;
                border-radius: var(--harmony-corner-radius-level4);
                overflow-x: auto;
                margin: 10px 0;

                code {
                  background: none;
                  color: inherit;
                  padding: 0;
                }
              }

              blockquote {
                border-left: 4px solid var(--harmony-brand));
                padding-left: 14px;
                margin: 10px 0;
                color: var(--harmony-font-secondary);
                font-style: italic;
              }

              table {
                border-collapse: collapse;
                width: 100%;
                margin: 10px 0;

                th, td {
                  border: 1px solid var(--harmony-comp-divider);
                  padding: 8px 12px;
                  text-align: left;
                }

                th {
                  background: var(--harmony-comp-background-secondary);
                  font-weight: 600;
                }
              }
            }
          }

          &.user-block {
            .message-header .message-icon {
              background: var(--harmony-comp-emphasize-tertiary);
            }
            .message-body {
              border-left: 3px solid var(--harmony-brand));
            }
          }

          &.ai-block {
            .message-header .message-icon {
              background: var(--harmony-confirm-bg);
            }
            .message-body {
              border-left: 3px solid var(--harmony-confirm);
            }
          }
        }
      }
    }
  }
}

/* 编辑器区域 */
.editor-section {
  flex: 1;
  display: flex;
  flex-direction: column;

  .editor-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
    padding: 0 4px;

    .header-left {
      display: flex;
      align-items: center;
      gap: 10px;

      .editor-icon {
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--harmony-brand));
        color: var(--harmony-comp-background-primary);
        border-radius: 8px;

        svg {
          width: 18px;
          height: 18px;
        }
      }

      .editor-title {
        font-size: var(--harmony-font-size-body-m);
        font-weight: 600;
        color: var(--harmony-font-primary);
      }
    }

    .header-right {
      display: flex;
      align-items: center;
      gap: 10px;

      .streaming-indicator {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 5px 12px;
        background: var(--harmony-comp-emphasize-tertiary);
        border-radius: 999px;
        border: 1px solid var(--harmony-brand));

        .loading-dot {
          width: 7px;
          height: 7px;
          background: var(--harmony-brand));
          border-radius: 50%;
          animation: pulse 1.5s ease-in-out infinite;
        }

        .loading-text {
          font-size: var(--harmony-font-size-body-s);
          color: var(--harmony-brand));
          font-weight: 500;
        }
      }

      .editable-indicator {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 5px 12px;
        background: var(--harmony-confirm-bg);
        border-radius: 999px;
        border: 1px solid var(--harmony-confirm);

        .edit-icon {
          display: flex;
          color: var(--harmony-confirm);
        }

        .edit-text {
          font-size: var(--harmony-font-size-body-s);
          color: var(--harmony-confirm);
          font-weight: 500;
        }
      }
    }
  }

  .editor-wrapper {
    flex: 1;
    background: var(--harmony-comp-background-primary);
    border: 1px solid var(--harmony-comp-divider);
    border-radius: 14px;
    overflow: hidden;
    transition: border-color 0.2s ease;

    &:focus-within {
      border-color: var(--harmony-brand));
    }

    .editor-content {
      height: 100%;
      display: flex;

      .editor-pane {
        width: 50%;
        height: 100%;
        border-right: 1px solid var(--harmony-comp-divider);
        overflow: hidden;
        display: flex;
        flex-direction: column;
        background: var(--harmony-comp-background-primary);

        .pane-header {
          padding: 10px 14px;
          background: var(--harmony-comp-background-secondary);
          border-bottom: 1px solid var(--harmony-comp-divider);
          font-size: var(--harmony-font-size-body-s);
          font-weight: 600;
          color: var(--harmony-font-secondary);
        }

        .markdown-editor {
          flex: 1;
          width: 100%;
          border: none;
          outline: none;
          resize: none;
          padding: 14px;
          font-family: var(--harmony-font-family);
          font-size: var(--harmony-font-size-subtitle-s);
          line-height: 1.6;
          color: var(--harmony-font-primary);
          background: var(--harmony-comp-background-primary);

          &::placeholder {
            color: var(--harmony-font-tertiary);
          }

          &:read-only {
            background: var(--harmony-comp-background-secondary);
            cursor: default;
          }
        }
      }

      .preview-pane {
        width: 50%;
        height: 100%;
        display: flex;
        flex-direction: column;
        background: var(--harmony-comp-background-secondary);

        .pane-header {
          padding: 10px 14px;
          background: var(--harmony-comp-background-secondary);
          border-bottom: 1px solid var(--harmony-comp-divider);
          font-size: var(--harmony-font-size-body-s);
          font-weight: 600;
          color: var(--harmony-font-secondary);
        }

        .markdown-preview {
          flex: 1;
          overflow-y: auto;
          padding: 14px 20px;

          scrollbar-width: none;
          -ms-overflow-style: none;
          &::-webkit-scrollbar { display: none; }

          :deep(h1), :deep(h2), :deep(h3), :deep(h4), :deep(h5), :deep(h6) {
            margin-top: 6px;
            margin-bottom: 0;
            font-weight: 600;
            line-height: 1.2;
            color: var(--harmony-font-primary);
          }
          :deep(h1) { font-size: 1.8em; border-bottom: 1px solid var(--harmony-comp-divider); padding-bottom: 1px; }
          :deep(h2) { font-size: 1.5em; border-bottom: 1px solid var(--harmony-comp-divider); padding-bottom: 1px; }
          :deep(h3) { font-size: 1.25em; }
          :deep(h4) { font-size: 1.1em; }
          :deep(h5) { font-size: 1em; }
          :deep(h6) { font-size: 0.9em; color: var(--harmony-font-secondary); }

          :deep(p) {
            margin-top: 0;
            margin-bottom: 2px;
            line-height: 1.5;
            color: var(--harmony-font-primary);
          }

          :deep(ul), :deep(ol) {
            padding-left: 1.8em;
            margin-top: 2px;
            margin-bottom: 2px;
            li { margin-bottom: 0; line-height: 1.4; color: var(--harmony-font-primary); }
          }

          :deep(ul.list-level-1) { list-style-type: disc; margin-left: 0; }
          :deep(ul.list-level-2) { list-style-type: circle; margin-left: 1.5em; }
          :deep(ul.list-level-3) { list-style-type: square; margin-left: 3em; }

          :deep(code) {
            background: var(--harmony-comp-background-secondary);
            padding: 2px 6px;
            border-radius: 4px;
            font-family: var(--harmony-font-family);
            font-size: 0.9em;
            color: var(--harmony-warning);
          }

          :deep(pre) {
            background: var(--harmony-font-primary);
            color: var(--harmony-comp-background-primary);
            padding: 10px;
            border-radius: 6px;
            overflow-x: auto;
            margin-top: 3px;
            margin-bottom: 4px;
            code { background: none; color: inherit; padding: 0; line-height: 1.4; }
          }

          :deep(blockquote) {
            border-left: 4px solid var(--harmony-brand));
            padding-left: 12px;
            margin: 2px 0;
            color: var(--harmony-font-secondary);
            font-style: italic;
            line-height: 1.4;
          }

          :deep(table) {
            border-collapse: collapse;
            width: 100%;
            margin-top: 3px;
            margin-bottom: 4px;
            th, td { border: 1px solid var(--harmony-comp-divider); padding: 5px 8px; text-align: left; line-height: 1.4; }
            th { background: var(--harmony-comp-background-secondary); font-weight: 600; }
          }

          :deep(a) { color: var(--harmony-brand)); text-decoration: none; &:hover { text-decoration: underline; } }
          :deep(hr) { border: none; border-top: 1px solid var(--harmony-comp-divider); margin: 6px 0; }
          :deep(.placeholder) { color: var(--harmony-font-tertiary); font-style: italic; }
        }
      }
    }
  }
}

/* 操作按钮区域 */
.action-section {
  .action-buttons {
    display: flex;
    gap: 12px;
    justify-content: flex-end;

    .action-btn {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 12px 24px;
      border: none;
      border-radius: 10px;
      font-size: var(--harmony-font-size-subtitle-s);
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s ease;

      .btn-icon svg {
        width: 16px;
        height: 16px;
      }

      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
    }

    .regenerate-btn {
      background: var(--harmony-comp-background-primary);
      color: var(--harmony-font-secondary);
      border: 1px solid var(--harmony-comp-divider);

      &:not(:disabled):hover {
        background: var(--harmony-comp-background-secondary);
        border-color: var(--harmony-comp-divider);
      }
    }

    .start-btn {
      background: var(--harmony-brand));
      color: var(--harmony-comp-background-primary);

      &:not(:disabled):hover {
        background: var(--harmony-interactive-hover);
      }
    }
  }
}

/* 反馈弹窗 */
.feedback-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

.feedback-modal {
  background: var(--harmony-comp-background-primary);
  border-radius: 14px;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15);
  width: 420px;
  max-width: 90vw;
  animation: slideUp 0.2s ease;
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--harmony-comp-divider);
  background: var(--harmony-comp-background-primary);

  .modal-title {
    margin: 0;
    font-size: var(--harmony-font-size-body-m);
    font-weight: 700;
    color: var(--harmony-font-primary);
  }

  .close-btn {
    width: 28px;
    height: 28px;
    border: none;
    background: var(--harmony-comp-background-secondary);
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    color: var(--harmony-font-secondary);
    font-size: 18px;
    transition: background 0.15s ease;

    &:hover {
      background: var(--harmony-comp-divider);
      color: var(--harmony-font-primary);
    }
  }
}

.modal-body {
  padding: 20px;

  .feedback-tip {
    margin: 0 0 14px;
    font-size: var(--harmony-font-size-subtitle-s);
    color: var(--harmony-font-secondary);
    line-height: 1.6;
  }

  .input-wrapper {
    position: relative;

    .feedback-textarea {
      width: 100%;
      min-height: 100px;
      padding: 12px 14px;
      border: 1px solid var(--harmony-comp-divider);
      border-radius: var(--harmony-corner-radius-level6);
      font-family: var(--harmony-font-family);
      font-size: var(--harmony-font-size-subtitle-s);
      line-height: 1.6;
      color: var(--harmony-font-primary);
      background: var(--harmony-comp-background-primary);
      resize: none;
      outline: none;
      box-sizing: border-box;

      &:focus {
        border-color: var(--harmony-brand));
      }

      &::placeholder {
        color: var(--harmony-font-tertiary);
      }
    }

    .char-count {
      position: absolute;
      bottom: 8px;
      right: 10px;
      font-size: var(--harmony-font-size-body-s);
      color: var(--harmony-font-tertiary);
      pointer-events: none;
    }
  }
}

.modal-footer {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  padding: 16px 20px;
  border-top: 1px solid var(--harmony-comp-divider);
  background: var(--harmony-comp-background-primary);

  button {
    padding: 10px 18px;
    border: none;
    border-radius: 8px;
    font-size: var(--harmony-font-size-subtitle-s);
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .cancel-btn {
    background: var(--harmony-comp-background-primary);
    color: var(--harmony-font-secondary);
    border: 1px solid var(--harmony-comp-divider);

    &:hover {
      background: var(--harmony-comp-background-secondary);
    }
  }

  .confirm-btn {
    background: var(--harmony-brand));
    color: var(--harmony-comp-background-primary);

    &:hover {
      background: var(--harmony-interactive-hover);
    }
  }
}

/* 动画 */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* 响应式 */
@media (max-width: 768px) {
  .chat-container { gap: 16px; }

  .editor-content {
    flex-direction: column !important;

    .editor-pane, .preview-pane {
      width: 100% !important;
      height: 50% !important;
    }

    .editor-pane {
      border-right: none !important;
      border-bottom: 1px solid var(--harmony-comp-divider);
    }
  }

  .action-section .action-buttons {
    flex-direction: column;
    .action-btn { width: 100%; justify-content: center; }
  }
}
</style>

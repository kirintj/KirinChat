import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { HMessage } from '@/components/ui'
import { MdPreview } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import {
  generateLingSeekGuidePromptAPI,
  regenerateLingSeekGuidePromptAPI
} from '@/apis/lingseek'
import { getWorkspaceSessionInfoAPI } from '@/apis/workspace'

export interface HistoryContext {
  query: string
  guide_prompt?: string
  task?: any[]
  answer: string
}

export function useWorkspaceGuide() {
  const route = useRoute()
  const router = useRouter()

  // 历史记录相关
  const historyContexts = ref<HistoryContext[]>([])
  const showHistory = ref(false)
  const isExistingSession = ref(false) // 标记是否为已有会话
  const expandedItems = ref<Set<number>>(new Set()) // 记录展开的项目

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
    html = html.replace(/\n\n+/g, '</p><p>') // 双换行或多换行才分段
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

  return {
    historyContexts,
    showHistory,
    isExistingSession,
    expandedItems,
    userQuery,
    guidePrompt,
    isStreaming,
    isEditable,
    selectedTools,
    webSearchEnabled,
    showFeedbackDialog,
    feedbackText,
    originalParams,
    renderedMarkdown,
    toggleExpand,
    parseMarkdown,
    loadSessionInfo,
    startGenerateGuidePrompt,
    handleRegenerate,
    handleCancelRegenerate,
    handleConfirmRegenerate,
    handleStartTask
  }
}

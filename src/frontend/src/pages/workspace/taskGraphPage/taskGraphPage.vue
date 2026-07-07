<script setup lang="ts">
import { ref, onMounted, computed, nextTick, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { HMessage } from '@/components/ui'
import { MdPreview, MdEditor } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import { 
  generateLingSeekGuidePromptAPI, 
  regenerateLingSeekGuidePromptAPI,
  startLingSeekTaskAPI 
} from '../../../apis/lingseek'
import { getWorkspaceSessionInfoAPI } from '../../../apis/workspace'

const route = useRoute()
const router = useRouter()

interface GraphNode {
  start: string
  end: string
}

interface NodeStatus {
  status: 'pending' | 'executing' | 'completed'
  message?: string
}

interface HistoryContext {
  query: string
  guide_prompt?: string
  task_graph?: GraphNode[]
  answer: string
}

// 状态管理
const taskGraph = ref<GraphNode[]>([])
const isStreaming = ref(false)
const showGraph = ref(false)
const nodeStatusMap = ref<Map<string, NodeStatus>>(new Map())
const selectedNode = ref<string | null>(null)
const showNodeDetail = ref(false)
const taskResultContent = ref('')
const showTaskResult = ref(false)
const resultContainer = ref<HTMLElement>()
// 结果接收控制（任务流程结束后才开始）
const isReceivingResult = ref(false)
const resultBuffer = ref('')
const isDraining = ref(false)
let drainTimer: number | null = null
const drainChunkSize = 120  // 增大块大小减少渲染频率
const drainIntervalMs = 80  // 降低刷新频率，减少抖动
let scrollPending = false

// 指导手册滚动容器引用
const guideScrollContainer = ref<HTMLElement | null>(null)

// 启动结果接收并流式回放缓冲
const startReceivingResults = () => {
  console.log('🚀 [startReceivingResults] 被调用')
  console.log('  - isReceivingResult:', isReceivingResult.value)
  console.log('  - showTaskResult:', showTaskResult.value)
  console.log('  - resultBuffer 长度:', resultBuffer.value.length)
  console.log('  - resultBuffer 前100字符:', resultBuffer.value.substring(0, 100))
  
  if (isReceivingResult.value) {
    console.log('⚠️ [startReceivingResults] 已在接收中，跳过')
    return
  }
  isReceivingResult.value = true
  if (!showTaskResult.value) {
    showTaskResult.value = true
  }
  // HMessage.success('开始接收任务结果')
  console.log('✅ [startReceivingResults] 状态已更新，准备启动排空')
  // 启动排空
  startDrain()
}

const startDrain = () => {
  console.log('🔄 [startDrain] 被调用')
  console.log('  - isDraining:', isDraining.value)
  console.log('  - drainTimer:', drainTimer)
  console.log('  - resultBuffer 长度:', resultBuffer.value.length)
  
  if (isDraining.value) {
    console.log('⚠️ [startDrain] 已在排空中，跳过')
    return
  }
  isDraining.value = true
  if (drainTimer !== null) {
    window.clearInterval(drainTimer)
    drainTimer = null
  }
  
  console.log('✅ [startDrain] 开始设置定时器，间隔:', drainIntervalMs, 'ms，块大小:', drainChunkSize)
  const tick = () => {
    if (!resultBuffer.value.length) {
      // 缓冲已空，结束接收
      console.log('⏹️ [tick] 缓冲已空，结束接收')
      if (drainTimer !== null) {
        window.clearInterval(drainTimer)
        drainTimer = null
      }
      isDraining.value = false
      isReceivingResult.value = false
      //HMessage.success('任务执行完成')
      return
    }
    const chunk = resultBuffer.value.slice(0, drainChunkSize)
    resultBuffer.value = resultBuffer.value.slice(drainChunkSize)
    taskResultContent.value += chunk
    console.log('📤 [tick] 输出块:', chunk.length, '字符，剩余缓冲:', resultBuffer.value.length, '，当前总内容:', taskResultContent.value.length)
    scrollResultToBottom()
  }
  drainTimer = window.setInterval(tick, drainIntervalMs)
  console.log('✅ [startDrain] 定时器已启动，ID:', drainTimer)
}

// 指导手册编辑/预览切换（默认预览）
const isEditingGuide = ref(false)

// 指导手册相关
const guidePrompt = ref('')
const isGeneratingGuide = ref(false)
const showFeedbackDialog = ref(false)
const feedbackText = ref('')

// 历史记录相关
const isHistoryMode = ref(false)
const historyContexts = ref<HistoryContext[]>([])

// 保存任务参数
const taskParams = ref({
  query: '',
  guide_prompt: '',
  web_search: false,
  plugins: [] as string[],
  mcp_servers: [] as string[]
})

// 保存原始参数（用于重新生成）
const originalParams = ref({
  query: '',
  tools: [] as string[],
  web_search: false,
  plugins: [] as string[],
  mcp_servers: [] as string[]
})

// 获取当前选中节点的详情
const selectedNodeDetail = computed(() => {
  if (!selectedNode.value) return null
  const status = nodeStatusMap.value.get(selectedNode.value)
  return {
    title: selectedNode.value,
    status: status?.status || 'pending',
    message: status?.message || '该节点尚未执行'
  }
})

// 构建图形节点和边的数据结构（竖向布局）
const graphData = computed(() => {
  if (taskGraph.value.length === 0) {
    return { nodes: [], edges: [] }
  }

  const nodeSet = new Set<string>()
  const edges: { from: string; to: string }[] = []

  // 提取所有节点和边
  taskGraph.value.forEach((item) => {
    nodeSet.add(item.start)
    nodeSet.add(item.end)
    edges.push({ from: item.start, to: item.end })
  })

  const nodes = Array.from(nodeSet).map((node, index) => {
    const status = nodeStatusMap.value.get(node)?.status || 'pending'
    return {
      id: node,
      label: node,
      x: 0,
      y: 0,
      level: 0,
      status
    }
  })

  // 计算节点层级（用于竖向布局）
  const calculateLevels = () => {
    const levelMap = new Map<string, number>()
    const visited = new Set<string>()

    const dfs = (node: string, level: number) => {
      if (visited.has(node)) return
      visited.add(node)
      
      const currentLevel = levelMap.get(node) || 0
      levelMap.set(node, Math.max(currentLevel, level))

      edges.forEach(edge => {
        if (edge.from === node) {
          dfs(edge.to, level + 1)
        }
      })
    }

    // 找到所有起始节点（没有入边的节点）
    const startNodes = nodes.filter(node => 
      !edges.some(edge => edge.to === node.id)
    )

    startNodes.forEach(node => dfs(node.id, 0))

    // 更新节点层级
    nodes.forEach(node => {
      node.level = levelMap.get(node.id) || 0
    })
  }

  calculateLevels()

  // 按层级分组布局（竖向）
  const levelGroups = new Map<number, string[]>()
  nodes.forEach(node => {
    const level = node.level
    if (!levelGroups.has(level)) {
      levelGroups.set(level, [])
    }
    levelGroups.get(level)!.push(node.id)
  })

  // 设置节点位置（竖向布局：Y轴表示层级，X轴表示同层级的位置）
  const verticalSpacing = 120  // 层级之间的垂直间距（减小）
  const horizontalSpacing = 200  // 同层级节点的水平间距（减小）
  const nodeHeight = 50

  nodes.forEach(node => {
    const levelNodes = levelGroups.get(node.level)!
    const indexInLevel = levelNodes.indexOf(node.id)
    const totalInLevel = levelNodes.length

    // X轴：居中排列同层级节点
    node.x = (indexInLevel - (totalInLevel - 1) / 2) * horizontalSpacing
    // Y轴：根据层级垂直排列
    node.y = node.level * verticalSpacing + 60
  })

  return { nodes, edges }
})

// 计算 SVG 视图框（竖向适配）
const svgViewBox = computed(() => {
  if (graphData.value.nodes.length === 0) {
    return '0 0 600 800'
  }

  const xs = graphData.value.nodes.map(n => n.x)
  const ys = graphData.value.nodes.map(n => n.y)
  
  const minX = Math.min(...xs) - 120
  const maxX = Math.max(...xs) + 120
  const minY = Math.min(...ys) - 60
  const maxY = Math.max(...ys) + 80

  const width = maxX - minX
  const height = maxY - minY

  return `${minX} ${minY} ${width} ${height}`
})

// 生成箭头路径（竖向）
const getEdgePath = (edge: { from: string; to: string }) => {
  const fromNode = graphData.value.nodes.find(n => n.id === edge.from)
  const toNode = graphData.value.nodes.find(n => n.id === edge.to)
  
  if (!fromNode || !toNode) return ''

  const x1 = fromNode.x
  const y1 = fromNode.y + 25  // 从节点底部出发（调整为25）
  const x2 = toNode.x
  const y2 = toNode.y - 25    // 到节点顶部（调整为25）

  // 使用贝塞尔曲线创建平滑的连接线（竖向）
  const midY = (y1 + y2) / 2
  
  return `M ${x1} ${y1} C ${x1} ${midY}, ${x2} ${midY}, ${x2} ${y2}`
}

// 生成指导手册
const generateGuidePrompt = async () => {
  console.log('=== 开始生成指导手册 ===')
  console.log('用户问题:', originalParams.value.query)
  console.log('选中工具:', originalParams.value.tools)
  console.log('联网搜索:', originalParams.value.web_search)
  
  guidePrompt.value = ''
  isGeneratingGuide.value = true

  try {
    await generateLingSeekGuidePromptAPI(
      {
        query: originalParams.value.query,
        tools: originalParams.value.tools,
        web_search: originalParams.value.web_search,
        mcp_servers: originalParams.value.mcp_servers
      },
      (data) => {
        // 处理流式数据
        console.log('📨 接收到指导手册数据块')
        guidePrompt.value += data
        // 自动滚动到底部
        scrollGuideToBottom()
      },
      (error) => {
        console.error('❌ 生成指导手册出错:', error)
        HMessage.error('生成指导手册失败')
        isGeneratingGuide.value = false
      },
      () => {
        console.log('✅ 指导手册生成完成')
        isGeneratingGuide.value = false
        HMessage.success('指导手册生成完成')
      }
    )
  } catch (error) {
    console.error('生成指导手册异常:', error)
    HMessage.error('生成指导手册失败')
    isGeneratingGuide.value = false
  }
}

// 打开重新生成对话框
const handleRegenerate = () => {
  showFeedbackDialog.value = true
  feedbackText.value = ''
}

// 取消重新生成
const handleCancelRegenerate = () => {
  showFeedbackDialog.value = false
  feedbackText.value = ''
}

// 确认重新生成
const handleConfirmRegenerate = async () => {
  if (!feedbackText.value.trim()) {
    HMessage.warning('请输入您的优化建议')
    return
  }

  console.log('=== 开始重新生成指导手册 ===')
  console.log('反馈内容:', feedbackText.value)

  // 保存当前的指导手册
  const currentGuidePrompt = guidePrompt.value
  
  guidePrompt.value = ''
  isGeneratingGuide.value = true
  showFeedbackDialog.value = false

  try {
    await regenerateLingSeekGuidePromptAPI(
      {
        query: originalParams.value.query,
        plugins: originalParams.value.plugins,
        web_search: originalParams.value.web_search,
        mcp_servers: originalParams.value.mcp_servers,
        feedback: feedbackText.value,
        guide_prompt: currentGuidePrompt
      },
      (data) => {
        // 处理流式数据
        guidePrompt.value += data
        // 自动滚动到底部
        scrollGuideToBottom()
      },
      (error) => {
        console.error('❌ 重新生成指导手册出错:', error)
        HMessage.error('重新生成失败')
        isGeneratingGuide.value = false
      },
      () => {
        console.log('✅ 指导手册重新生成完成')
        isGeneratingGuide.value = false
        feedbackText.value = ''
        HMessage.success('指导手册重新生成完成')
      }
    )
  } catch (error) {
    console.error('重新生成指导手册异常:', error)
    HMessage.error('重新生成失败')
    isGeneratingGuide.value = false
  }
}

// 开始执行任务
const handleStartTask = () => {
  if (!guidePrompt.value.trim()) {
    HMessage.warning('请先生成指导手册')
    return
  }

  console.log('🚀 开始执行任务')
  // 将当前指导手册内容同步到任务参数
  taskParams.value.guide_prompt = guidePrompt.value
  console.log('✅ 已同步指导手册到任务参数，长度:', taskParams.value.guide_prompt.length)
  startTask()
}

// 初始化
onMounted(async () => {
  console.log('=== taskGraphPage onMounted ===')
  console.log('路由参数:', route.query)
  
  const sessionId = route.query.session_id as string
  
  if (sessionId) {
    // 历史会话模式：加载历史数据
    console.log('历史会话模式，session_id:', sessionId)
    isHistoryMode.value = true
    await loadSessionInfo(sessionId)
    
    // 历史会话模式保留 session_id 参数在 URL 中
    // 不清理 URL，方便用户分享和刷新
  } else {
    // 新任务模式：生成指导手册
    console.log('新任务模式')
    
    // 保存参数
    originalParams.value.query = route.query.query as string || ''
    originalParams.value.web_search = route.query.webSearch === 'true'
    
    const tools = route.query.tools as string
    originalParams.value.tools = tools ? JSON.parse(tools) : []
    originalParams.value.plugins = originalParams.value.tools
    const mcpQuery = route.query.mcp_servers as string
    originalParams.value.mcp_servers = mcpQuery ? JSON.parse(mcpQuery) : []
    
    taskParams.value.query = originalParams.value.query
    taskParams.value.web_search = originalParams.value.web_search
    taskParams.value.plugins = originalParams.value.plugins
    taskParams.value.mcp_servers = originalParams.value.mcp_servers
    
    console.log('✅ 用户问题:', originalParams.value.query)
    console.log('✅ 选中工具:', originalParams.value.tools)
    console.log('✅ 联网搜索:', originalParams.value.web_search)
    
    // 清理 URL 参数（保留功能，隐藏参数）
    router.replace({ path: '/workspace/taskGraph' })
    
    // 自动开始生成指导手册
    if (originalParams.value.query) {
      console.log('🚀 开始自动生成指导手册...')
      await generateGuidePrompt()
    } else {
      console.warn('⚠️ 缺少用户问题，无法生成指导手册')
    }
  }
  
  console.log('=== taskGraphPage onMounted 结束 ===')
})

// 加载历史会话信息
const loadSessionInfo = async (sessionId: string) => {
  try {
    isHistoryMode.value = true
    const response = await getWorkspaceSessionInfoAPI(sessionId)
    
    console.log('📦 会话信息响应:', response.data)
    
    if (response.data.status_code === 200) {
      const sessionData = response.data.data
      console.log('📦 会话数据:', sessionData)
      
      // 加载历史上下文
      if (sessionData.contexts && Array.isArray(sessionData.contexts) && sessionData.contexts.length > 0) {
        historyContexts.value = sessionData.contexts
        console.log('📦 contexts 数组:', historyContexts.value)
        
        // 获取第一个context（最新的数据）
        const context = historyContexts.value[0]
        console.log('📦 当前 context:', context)
        
        // 显示指导手册（对应第一列）
        if (context.guide_prompt) {
          guidePrompt.value = context.guide_prompt
          console.log('✅ 指导手册已加载，长度:', guidePrompt.value.length)
        } else {
          console.warn('⚠️ 未找到 guide_prompt 字段')
        }
        
        // 显示任务图（对应第二列）- 使用 task_graph 字段
        console.log('🔍 检查 task_graph 字段:', context.task_graph)
        console.log('🔍 task_graph 类型:', typeof context.task_graph)
        console.log('🔍 是否为数组:', Array.isArray(context.task_graph))
        
        if (context.task_graph && Array.isArray(context.task_graph) && context.task_graph.length > 0) {
          console.log('✅ 任务图数据 (task_graph):', JSON.stringify(context.task_graph, null, 2))
          
          // task_graph 已经是 { start, end } 格式，直接使用
          taskGraph.value = context.task_graph
          console.log('✅ 加载的任务图:', taskGraph.value)
          
          // 初始化节点状态（历史模式下所有节点都是已完成）
          const nodeSet = new Set<string>()
          context.task_graph.forEach((edge: GraphNode) => {
            nodeSet.add(edge.start)
            nodeSet.add(edge.end)
          })
          
          console.log('✅ 提取的节点集合:', Array.from(nodeSet))
          
          // 所有节点标记为已完成
          nodeSet.forEach((nodeId: string) => {
            updateNodeStatus(nodeId, 'completed', '已执行完成')
          })
          
          showGraph.value = true
          console.log('✅ 任务图已显示，showGraph:', showGraph.value)
        } else {
          console.warn('⚠️ 未找到 task_graph 字段或为空数组')
          console.warn('⚠️ context 完整内容:', JSON.stringify(context, null, 2))
        }
        
        // 显示执行结果（对应第三列）
        if (context.answer) {
          taskResultContent.value = context.answer
          showTaskResult.value = true
          console.log('✅ 执行结果已加载，长度:', taskResultContent.value.length)
        } else {
          console.warn('⚠️ 未找到 answer 字段')
        }
      } else {
        console.warn('⚠️ contexts 为空或不是数组')
        HMessage.warning('该会话暂无历史数据')
      }
    } else {
      HMessage.error('获取会话信息失败')
    }
  } catch (error) {
    console.error('❌ 加载会话信息出错:', error)
    HMessage.error('加载会话信息出错')
  }
}

// 更新节点状态
const updateNodeStatus = (title: string, status: 'pending' | 'executing' | 'completed', message?: string) => {
  nodeStatusMap.value.set(title, { status, message })
}

// 处理节点点击
const handleNodeClick = (nodeId: string) => {
  selectedNode.value = nodeId
  const nodeStatus = nodeStatusMap.value.get(nodeId)
  
  if (nodeStatus && nodeStatus.status === 'completed' && nodeStatus.message) {
    showNodeDetail.value = true
  } else if (nodeStatus && nodeStatus.status === 'executing') {
    HMessage.info('该节点正在执行中...')
  } else {
    HMessage.info('该节点尚未执行')
  }
}

// 关闭节点详情弹窗
const closeNodeDetail = () => {
  showNodeDetail.value = false
  selectedNode.value = null
}

onBeforeUnmount(() => {
  if (drainTimer !== null) {
    window.clearInterval(drainTimer)
    drainTimer = null
  }
})

// 滚动结果区域到底部（优化：使用 requestAnimationFrame 防抖）
const scrollResultToBottom = () => {
  if (scrollPending) return
  scrollPending = true
  requestAnimationFrame(() => {
    if (resultContainer.value) {
      resultContainer.value.scrollTop = resultContainer.value.scrollHeight
    }
    scrollPending = false
  })
}

// 滚动指导手册到底部
const scrollGuideToBottom = () => {
  nextTick(() => {
    if (guideScrollContainer.value) {
      guideScrollContainer.value.scrollTop = guideScrollContainer.value.scrollHeight
    }
  })
}

// 开始执行任务
const startTask = async () => {
  console.log('开始执行任务')
  
  taskGraph.value = []
  nodeStatusMap.value.clear()
  taskResultContent.value = ''
  resultBuffer.value = ''
  showTaskResult.value = false
  isReceivingResult.value = false
  isStreaming.value = true
  showGraph.value = false
  // 清理可能遗留的回放定时器
  if (drainTimer !== null) {
    window.clearInterval(drainTimer)
    drainTimer = null
  }
  isDraining.value = false
  // 保持结果区“接收中”指示关闭，直到流程完成

  try {
    await startLingSeekTaskAPI(
      taskParams.value,
      (data) => {
        // 通用文本 chunk：统一进入缓冲；若处于接收阶段，确保排空
        console.log('📨 接收到文本数据:', data)
        if (typeof data === 'string' && data) {
          resultBuffer.value += data
          if (isReceivingResult.value && !isDraining.value) {
            startDrain()
          }
        }
      },
      (graph) => {
        // 处理任务图数据
        console.log('📊 接收到任务图数据:', graph)
        taskGraph.value = graph
        
        // 初始化所有节点状态
        const nodeSet = new Set<string>()
        const endNodes = new Set<string>()
        
        graph.forEach((item: GraphNode) => {
          nodeSet.add(item.start)
          nodeSet.add(item.end)
          endNodes.add(item.end)
        })
        
        // 找出所有起始节点（没有入边的节点，通常是用户问题）
        const startNodes = new Set<string>()
        nodeSet.forEach(node => {
          if (!endNodes.has(node)) {
            startNodes.add(node)
          }
        })
        
        // 设置节点状态：起始节点默认已完成，其他节点待执行
        nodeSet.forEach(node => {
          if (startNodes.has(node)) {
            // 起始节点（用户问题）默认已完成
            updateNodeStatus(node, 'completed', '用户问题已提交')
          } else {
            // 其他节点待执行
            updateNodeStatus(node, 'pending')
          }
        })
        
        showGraph.value = true
        HMessage.success('任务图生成成功，开始执行任务')
      },
      (stepData) => {
        // 处理步骤执行结果
        console.log('✅ 收到步骤结果:', stepData)
        updateNodeStatus(stepData.title, 'completed', stepData.message)
        HMessage.success(`节点「${stepData.title}」执行完成`)
      },
      (messageChunk) => {
        // 统一写入缓冲。若尚未开始接收（通常为首个 task_result 到达），立即启动接收与排空
        console.log('📄 收到任务结果数据块:', messageChunk)
        if (typeof messageChunk === 'string') {
          resultBuffer.value += messageChunk
        }
        if (!isReceivingResult.value) {
          startReceivingResults()
          return
        }
        if (isReceivingResult.value && !isDraining.value) {
          startDrain()
        }
      },
      (error) => {
        console.error('❌ 任务执行出错:', error)
        HMessage.error('任务执行失败')
        isStreaming.value = false
      },
      () => {
        console.log('✅ 任务执行完成')
        isStreaming.value = false
        // 任务流程结束时，开启接收阶段并以流式回放缓冲
        startReceivingResults()
      }
    )
  } catch (error) {
    console.error('任务执行异常:', error)
    HMessage.error('请求失败，请检查网络连接')
    isStreaming.value = false
  }
}

// 获取节点颜色
const getNodeColor = (status: string) => {
  switch (status) {
    case 'completed':
      return 'var(--harmony-confirm)' // 绿色 - 已完成
    case 'executing':
      return 'var(--harmony-alert)' // 橙色 - 执行中
    case 'pending':
    default:
      return 'var(--harmony-comp-divider)' // 灰色 - 待执行
  }
}
</script>

<template>
  <div class="task-graph-page" :key="String(route.query.session_id || route.query.query || Date.now())">
    <!-- 三列布局容器 -->
    <div class="three-column-layout">
      <!-- 第一列：指导手册 -->
      <div class="column column-guide">
        <div class="column-header">
          <span class="header-icon">
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
              <path d="M4 2H10L14 6V16C14 16.5523 13.5523 17 13 17H4C3.44772 17 3 16.5523 3 16V3C3 2.44772 3.44772 2 4 2Z" stroke="currentColor" stroke-width="1.3"/>
              <path d="M10 2V6H14" stroke="currentColor" stroke-width="1.3"/>
              <line x1="6" y1="9" x2="12" y2="9" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
              <line x1="6" y1="12" x2="12" y2="12" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
            </svg>
          </span>
          <h2 class="header-title">指导手册</h2>
          <!-- 编辑/预览切换 -->
          <div class="mode-toggle" role="tablist" aria-label="Guide mode">
            <button
              class="mode-btn"
              :class="{ active: isEditingGuide }"
              @click="isEditingGuide = true"
              role="tab"
              :aria-selected="isEditingGuide"
            >编辑</button>
            <button
              class="mode-btn"
              :class="{ active: !isEditingGuide }"
              @click="isEditingGuide = false"
              role="tab"
              :aria-selected="!isEditingGuide"
            >预览</button>
          </div>
          <span v-if="isGeneratingGuide" class="status-badge streaming">
            <span class="status-dot"></span>
            <span>生成中</span>
          </span>
        </div>
        <div class="column-content">
          <div class="guide-content-wrapper">
            <div class="guide-scroll-area">
              <div class="guide-editor" v-if="isEditingGuide">
                <MdEditor
                  v-model="guidePrompt"
                  language="zh-CN"
                  :preview="false"
                  :toolbars-exclude="['save', 'fullscreen', 'github']"
                  :footers="[]"
                  style="height: 100%"
                />
              </div>
              <div v-else ref="guideScrollContainer">
                <div v-if="guidePrompt">
                  <MdPreview
                    editorId="guide-preview"
                    :modelValue="guidePrompt"
                  />
                </div>
                <div v-else class="empty-placeholder">
                  <span class="empty-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <rect x="5" y="3" width="14" height="18" rx="2" stroke="currentColor" stroke-width="1.3"/>
                <line x1="9" y1="8" x2="15" y2="8" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
                <line x1="9" y1="12" x2="15" y2="12" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
                <line x1="9" y1="16" x2="12" y2="16" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
                <path d="M9 2H12C13.1046 2 14 2.89543 14 4V4H9V2Z" stroke="currentColor" stroke-width="1.3"/>
              </svg>
            </span>
                  <p v-if="isGeneratingGuide">正在生成指导手册...</p>
                  <p v-else-if="isHistoryMode">正在加载历史数据...</p>
                  <p v-else>等待生成指导手册</p>
                </div>
              </div>
            </div>
            
            <!-- 操作按钮区 -->
            <div v-if="!isHistoryMode" class="guide-actions">
              <button
                @click="handleRegenerate"
                :disabled="isGeneratingGuide || !guidePrompt"
                class="action-btn regenerate-btn"
              >
                <span class="btn-icon">
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <path d="M1 7C1 3.68629 3.68629 1 7 1C9.5 1 11.6424 2.54029 12.5 4.5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
                    <path d="M13 7C13 10.3137 10.3137 13 7 13C4.5 13 2.35758 11.4597 1.5 9.5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
                    <path d="M12.5 1V4.5H9" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M1.5 13V9.5H5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </span>
                <span class="btn-text">重新生成</span>
              </button>
              
              <button
                @click="handleStartTask"
                :disabled="isGeneratingGuide || !guidePrompt || isStreaming"
                class="action-btn start-btn"
              >
                <span class="btn-icon">
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <path d="M3 1.5L11.5 7L3 12.5V1.5Z" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/>
                  </svg>
                </span>
                <span class="btn-text">开始执行</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 第二列：任务流程图 -->
      <div class="column column-graph">
        <div class="column-header">
          <span class="header-icon">
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
              <circle cx="5" cy="5" r="2.5" stroke="currentColor" stroke-width="1.3"/>
              <circle cx="13" cy="9" r="2.5" stroke="currentColor" stroke-width="1.3"/>
              <circle cx="5" cy="13" r="2.5" stroke="currentColor" stroke-width="1.3"/>
              <path d="M7 5H10.5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
              <path d="M13 9L7 13" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
            </svg>
          </span>
          <h2 class="header-title">任务流程</h2>
          <span v-if="isStreaming" class="status-badge streaming">
            <span class="status-dot"></span>
            <span>执行中</span>
          </span>
          <span v-else-if="showGraph" class="status-badge completed">
            <span class="status-icon">✓</span>
            <span>已完成</span>
          </span>
        </div>
        
        <div class="column-content">
          <div v-if="showGraph" class="graph-wrapper">
            <!-- 状态说明 -->
            <div class="legend-bar">
              <div class="legend-item">
                <span class="legend-dot pending"></span>
                <span class="legend-text">待执行</span>
              </div>
              <div class="legend-item">
                <span class="legend-dot executing"></span>
                <span class="legend-text">执行中</span>
              </div>
              <div class="legend-item">
                <span class="legend-dot completed"></span>
                <span class="legend-text">已完成</span>
              </div>
            </div>

            <!-- SVG流程图（竖向） -->
            <div class="graph-container">
              <svg :viewBox="svgViewBox" class="graph-svg" preserveAspectRatio="xMidYMin meet">
                <!-- 定义箭头标记 -->
                <defs>
                  <marker
                    id="arrowhead"
                    markerWidth="8"
                    markerHeight="8"
                    refX="7"
                    refY="2.5"
                    orient="auto"
                    markerUnits="strokeWidth"
                  >
                    <path d="M0,0 L0,5 L7,2.5 z" fill="#667eea" />
                  </marker>
                  
                  <!-- 定义不同状态的渐变 -->
                  <linearGradient id="completedGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" style="stop-color:var(--harmony-confirm-bg);stop-opacity:1" />
                    <stop offset="100%" style="stop-color:var(--harmony-confirm);stop-opacity:1" />
                  </linearGradient>
                  
                  <linearGradient id="executingGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" style="stop-color:var(--harmony-alert-bg);stop-opacity:1" />
                    <stop offset="100%" style="stop-color:var(--harmony-alert);stop-opacity:1" />
                  </linearGradient>
                </defs>

                <!-- 绘制边（连接线） -->
                <g class="edges">
                  <path
                    v-for="(edge, index) in graphData.edges"
                    :key="`edge-${index}`"
                    :d="getEdgePath(edge)"
                    class="edge-path"
                    marker-end="url(#arrowhead)"
                  />
                </g>

                <!-- 绘制节点 -->
                <g class="nodes">
              <g
                v-for="node in graphData.nodes"
                :key="node.id"
                :transform="`translate(${node.x}, ${node.y})`"
                class="node-group"
                :class="[`node-${node.status}`, { 'node-clickable': node.status === 'completed' }]"
                @click="handleNodeClick(node.id)"
              >
                <rect
                  x="-80"
                  y="-25"
                  width="160"
                  height="50"
                  rx="10"
                  class="node-rect"
                  :fill="node.status === 'completed' ? 'url(#completedGradient)' : node.status === 'executing' ? 'url(#executingGradient)' : '#ffffff'"
                  :stroke="getNodeColor(node.status)"
                  stroke-width="2"
                />
                
                <!-- 节点状态图标 -->
                <text
                  x="-68"
                  y="5"
                  class="node-icon"
                  font-size="16"
                >
                  {{ node.status === 'completed' ? '✓' : node.status === 'executing' ? '⟳' : '○' }}
                </text>
                
                <!-- 节点文本 -->
                <text
                  x="-48"
                  y="5"
                  class="node-label"
                  text-anchor="start"
                  dominant-baseline="middle"
                >
                  {{ node.label.length > 12 ? node.label.substring(0, 12) + '...' : node.label }}
                </text>
              </g>
                </g>
              </svg>
            </div>
          </div>

          <div v-else class="empty-placeholder">
            <span class="empty-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <circle cx="7" cy="7" r="3.5" stroke="currentColor" stroke-width="1.3"/>
                <circle cx="17" cy="12" r="3.5" stroke="currentColor" stroke-width="1.3"/>
                <circle cx="7" cy="17" r="3.5" stroke="currentColor" stroke-width="1.3"/>
                <path d="M10 7H14.5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
                <path d="M17 12L10 17" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
              </svg>
            </span>
            <p>等待任务图生成...</p>
          </div>
        </div>
      </div>

      <!-- 第三列：任务执行结果 -->
      <div class="column column-result">
        <div class="column-header">
          <span class="header-icon">
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
              <rect x="2" y="2" width="14" height="14" rx="2" stroke="currentColor" stroke-width="1.3"/>
              <path d="M5 9L7.5 11.5L13 6" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </span>
          <h2 class="header-title">任务结果</h2>
          <span v-if="isReceivingResult" class="status-badge streaming">
            <span class="status-dot"></span>
            <span>接收中</span>
          </span>
        </div>
        <div class="column-content">
          <div v-if="showTaskResult" class="result-wrapper" ref="resultContainer">
            <MdPreview
              editorId="task-result-preview"
              :modelValue="taskResultContent"
              :showCodeRowNumber="true"
            />
            <div v-if="isReceivingResult" class="typing-indicator">
              <span class="typing-dot"></span>
              <span class="typing-dot"></span>
              <span class="typing-dot"></span>
            </div>
          </div>
          <div v-else class="empty-placeholder">
            <span class="empty-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <rect x="3" y="3" width="18" height="18" rx="3" stroke="currentColor" stroke-width="1.3"/>
                <path d="M7 12L10.5 15.5L17 9" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </span>
            <p>等待任务结果...</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 节点详情弹窗 -->
    <div v-if="showNodeDetail" class="node-detail-modal" @click="closeNodeDetail">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3 class="modal-title">节点详情</h3>
          <button class="modal-close" @click="closeNodeDetail">✕</button>
        </div>
        <div class="modal-body">
          <div class="detail-item">
            <label class="detail-label">节点名称：</label>
            <div class="detail-value">{{ selectedNodeDetail?.title }}</div>
          </div>
          <div class="detail-item">
            <label class="detail-label">执行状态：</label>
            <div class="detail-value">
              <span class="status-tag" :class="selectedNodeDetail?.status">
                {{ selectedNodeDetail?.status === 'completed' ? '已完成' : selectedNodeDetail?.status === 'executing' ? '执行中' : '待执行' }}
              </span>
            </div>
          </div>
          <div class="detail-item">
            <label class="detail-label">执行结果：</label>
            <div class="detail-value message-content">
              <MdPreview
                editorId="node-detail-preview"
                :modelValue="selectedNodeDetail?.message || '该节点尚未执行'"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 重新生成反馈弹窗 -->
    <div v-if="showFeedbackDialog" class="feedback-modal-overlay" @click.self="handleCancelRegenerate">
      <div class="feedback-modal">
        <div class="modal-header">
          <h3 class="modal-title">重新生成指导手册</h3>
          <button @click="handleCancelRegenerate" class="modal-close">✕</button>
        </div>
        
        <div class="modal-body">
          <p class="feedback-tip">请告诉我您希望如何优化这个指导手册：</p>
          <div class="input-wrapper">
            <textarea
              v-model="feedbackText"
              placeholder="例如：更加详细一些、更简洁、调整某个步骤等..."
              maxlength="500"
              class="feedback-textarea"
              rows="6"
              autofocus
            ></textarea>
          </div>
          <div class="char-count-bottom">{{ feedbackText.length }}/500</div>
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
   taskGraphPage — 简洁统一风格
   ============================= */

.task-graph-page {
  --bg: var(--harmony-comp-background-secondary);
  --panel: var(--harmony-comp-background-primary);
  --border: var(--harmony-comp-divider);
  --text: var(--harmony-font-primary);
  --muted: var(--harmony-font-secondary);
  --primary: var(--harmony-brand);
  --success: var(--harmony-confirm);
  --warning: var(--harmony-alert);
  --pending: var(--harmony-comp-divider);

  width: 100%;
  height: 100%;
  background: var(--bg);
  overflow: hidden;
}

/* 三列布局 */
.three-column-layout {
  display: flex;
  width: 100%;
  height: 100%;
  gap: 12px;
  padding: 12px;
}

.column {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: box-shadow 0.2s ease;

  &:hover {
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
  }

  .column-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px 20px;
    background: var(--panel);
    border-bottom: 1px solid var(--border);
    flex-shrink: 0;

    .header-icon {
      width: 36px;
      height: 36px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: var(--primary);
      color: var(--harmony-comp-background-primary);
      border-radius: 10px;
      flex-shrink: 0;

      svg {
        width: 18px;
        height: 18px;
      }
    }

    .header-title {
      margin: 0;
      font-size: var(--harmony-font-size-body-m);
      font-weight: 700;
      color: var(--text);
      flex: 1;
    }

    .status-badge {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: var(--harmony-font-size-body-s);
      padding: 6px 12px;
      border-radius: 999px;
      font-weight: 600;
      background: var(--harmony-comp-background-secondary);
      color: var(--muted);
      border: 1px solid var(--border);

      &.streaming {
        background: var(--harmony-alert-bg);
        border-color: var(--harmony-alert);
        color: var(--harmony-alert);

        .status-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: var(--harmony-alert);
          animation: harmony-pulse 1.5s ease-in-out infinite;
        }
      }

      &.completed {
        background: var(--harmony-confirm-bg);
        border-color: var(--harmony-confirm);
        color: var(--harmony-confirm);

        .status-icon {
          font-weight: 700;
        }
      }
    }

    .mode-toggle {
      display: flex;
      align-items: center;
      gap: 4px;
      margin-left: auto;
      margin-right: 8px;
    }

    .mode-btn {
      appearance: none;
      border: 1px solid var(--harmony-comp-divider);
      background: var(--harmony-comp-background-primary);
      color: var(--harmony-font-primary);
      font-size: var(--harmony-font-size-body-s);
      font-weight: 600;
      padding: 5px 10px;
      border-radius: var(--harmony-corner-radius-level4);
      cursor: pointer;
      transition: all 0.15s ease;

      &.active {
        background: var(--harmony-brand);
        border-color: var(--harmony-brand);
        color: var(--harmony-comp-background-primary);
      }
    }
  }

  .column-content {
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
    background: var(--panel);

    scrollbar-width: none;
    -ms-overflow-style: none;

    &::-webkit-scrollbar {
      display: none;
    }
  }
}

/* 第一列：指导手册 */
.column-guide {
  .guide-content-wrapper {
    display: flex;
    flex-direction: column;
    height: 100%;

    .guide-scroll-area {
      flex: 1;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      padding: 16px;

      > div:not(.guide-editor) {
        flex: 1;
        overflow-y: auto;
        min-height: 0;
        scrollbar-width: none;
        -ms-overflow-style: none;

        &::-webkit-scrollbar {
          display: none;
        }
      }

      .guide-editor {
        flex: 1;
        min-height: 0;

        :deep(.md-editor) {
          border: 1px solid var(--harmony-comp-divider);
          border-radius: var(--harmony-corner-radius-level8);
          height: 100% !important;
          display: flex;
          flex-direction: column;
        }
        :deep(.md-editor-toolbar) {
          border-bottom: 1px solid var(--harmony-comp-divider);
        }
        :deep(.md-editor-content-editor),
        :deep(.md-editor-content-preview) {
          font-family: var(--harmony-font-family);
          height: 100% !important;
        }
        :deep(.md-editor-content) {
          height: 100% !important;
        }
      }
    }

    .guide-actions {
      display: flex;
      gap: 10px;
      padding: 16px 20px;
      background: var(--harmony-comp-background-primary);
      border-top: 1px solid var(--border);
      flex-shrink: 0;

      .action-btn {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        padding: 12px 16px;
        border: none;
        border-radius: 10px;
        font-size: var(--harmony-font-size-subtitle-s);
        font-weight: 600;
        cursor: pointer;
        transition: all 0.15s ease;

        .btn-icon svg {
          width: 14px;
          height: 14px;
        }

        &:disabled {
          opacity: 0.4;
          cursor: not-allowed;
        }

        &.regenerate-btn {
          background: var(--harmony-comp-background-primary);
          color: var(--muted);
          border: 1px solid var(--border);

          &:hover:not(:disabled) {
            background: var(--harmony-comp-background-secondary);
            border-color: var(--harmony-comp-divider);
          }
        }

        &.start-btn {
          background: var(--primary);
          color: var(--harmony-comp-background-primary);

          &:hover:not(:disabled) {
            background: var(--harmony-interactive-hover);
          }
        }
      }
    }
  }
}

/* 第二列：任务流程图 */
.column-graph {
  .graph-wrapper {
    display: flex;
    flex-direction: column;
    height: 100%;
    padding: 12px;

    .legend-bar {
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 16px;
      padding: 10px 16px;
      background: var(--harmony-comp-background-primary);
      border: 1px solid var(--border);
      border-radius: var(--harmony-corner-radius-level6);
      margin-bottom: 12px;

      .legend-item {
        display: flex;
        align-items: center;
        gap: 6px;

        .legend-dot {
          width: 10px;
          height: 10px;
          border-radius: 50%;

          &.pending {
            background: var(--pending);
          }

          &.executing {
            background: var(--warning);
            animation: harmony-pulse 1.5s ease-in-out infinite;
          }

          &.completed {
            background: var(--success);
          }
        }

        .legend-text {
          font-size: var(--harmony-font-size-body-s);
          color: var(--muted);
        }
      }
    }

    .graph-container {
      flex: 1;
      background: var(--harmony-comp-background-primary);
      border: 1px solid var(--border);
      border-radius: var(--harmony-corner-radius-level8);
      padding: 16px;
      overflow: auto;
      display: flex;
      justify-content: center;
      align-items: flex-start;

      scrollbar-width: none;
      -ms-overflow-style: none;

      &::-webkit-scrollbar {
        display: none;
      }

      .graph-svg {
        width: 100%;
        height: auto;
        min-height: 400px;

        .edge-path {
          fill: none;
          stroke: var(--harmony-brand);
          stroke-width: 1.5;
          opacity: 0.6;
          transition: opacity 0.2s ease;

          &:hover {
            opacity: 1;
          }
        }

        .node-group {
          transition: opacity 0.2s ease;

          &.node-clickable {
            cursor: pointer;
          }

          .node-rect {
            transition: stroke-width 0.2s ease;
          }

          .node-label {
            font-size: var(--harmony-font-size-body-s);
            font-weight: 600;
            fill: var(--text);
            pointer-events: none;
          }

          .node-icon {
            font-size: 14px;
            pointer-events: none;
          }
        }
      }
    }
  }
}

/* 第三列：执行结果 */
.column-result {
  .result-wrapper {
    padding: 20px;
    height: 100%;
    overflow-y: auto;

    :deep(.md-editor-preview) {
      background: var(--harmony-comp-background-primary);
      border: 1px solid var(--border);
      padding: 20px;
      border-radius: var(--harmony-corner-radius-level6);

      p {
        margin: 12px 0;
        line-height: 1.8;
        color: var(--text);
      }

      h1, h2, h3, h4, h5, h6 {
        margin: 20px 0 12px;
        font-weight: 600;
        color: var(--text);
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
        padding: 16px;
        border-radius: var(--harmony-corner-radius-level4);
        overflow-x: auto;
        margin: 16px 0;

        code {
          background: none;
          color: inherit;
          padding: 0;
        }
      }
    }

    .typing-indicator {
      display: flex;
      justify-content: center;
      gap: 6px;
      padding: 20px;
      margin-top: 16px;

      .typing-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--primary);
        animation: typingBounce 1.4s infinite ease-in-out;

        &:nth-child(1) { animation-delay: -0.32s; }
        &:nth-child(2) { animation-delay: -0.16s; }
        &:nth-child(3) { animation-delay: 0s; }
      }
    }
  }
}

/* 空状态占位符 */
.empty-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 40px 20px;

  .empty-icon {
    margin-bottom: 16px;
    opacity: 0.25;

    svg {
      width: 32px;
      height: 32px;
    }
  }

  p {
    font-size: var(--harmony-font-size-subtitle-s);
    color: var(--muted);
    margin: 0;
  }
}

/* 节点详情弹窗 */
.node-detail-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  animation: harmony-fade-in 0.2s ease;

  .modal-content {
    background: var(--harmony-comp-background-primary);
    border-radius: 14px;
    width: 90%;
    max-width: 700px;
    max-height: 80vh;
    overflow: hidden;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
    animation: harmony-slide-up 0.2s ease;

    .modal-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 16px 20px;
      background: var(--harmony-comp-background-primary);
      border-bottom: 1px solid var(--harmony-comp-divider);

      .modal-title {
        margin: 0;
        font-size: var(--harmony-font-size-body-m);
        font-weight: 700;
        color: var(--text);
      }

      .modal-close {
        background: none;
        border: none;
        color: var(--muted);
        font-size: 20px;
        cursor: pointer;
        width: 28px;
        height: 28px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 6px;
        transition: background 0.15s ease;

        &:hover {
          background: var(--harmony-comp-background-secondary);
        }
      }
    }

    .modal-body {
      padding: 20px;
      overflow-y: auto;
      max-height: calc(80vh - 64px);

      .detail-item {
        margin-bottom: 16px;

        &:last-child {
          margin-bottom: 0;
        }

        .detail-label {
          display: block;
          font-size: var(--harmony-font-size-body-s);
          font-weight: 600;
          color: var(--muted);
          margin-bottom: 6px;
        }

        .detail-value {
          font-size: var(--harmony-font-size-subtitle-s);
          color: var(--text);
          line-height: 1.6;

          &.message-content {
            background: var(--harmony-comp-background-secondary);
            padding: 12px;
            border-radius: var(--harmony-corner-radius-level4);
            border: 1px solid var(--harmony-comp-divider);
            max-height: 300px;
            overflow-y: auto;
          }

          .status-tag {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 999px;
            font-size: var(--harmony-font-size-body-s);
            font-weight: 600;

            &.completed {
              background: var(--harmony-confirm-bg);
              color: var(--harmony-confirm);
            }

            &.executing {
              background: var(--harmony-alert-bg);
              color: var(--harmony-alert);
            }

            &.pending {
              background: var(--harmony-comp-background-secondary);
              color: var(--muted);
            }
          }
        }
      }
    }
  }
}

/* 重新生成反馈弹窗 */
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
  z-index: 10000;
  animation: harmony-fade-in 0.2s ease;

  .feedback-modal {
    background: var(--harmony-comp-background-primary);
    border-radius: 14px;
    width: 90%;
    max-width: 600px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
    animation: harmony-slide-up 0.2s ease;
    overflow: hidden;

    .modal-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 16px 20px;
      background: var(--harmony-comp-background-primary);
      border-bottom: 1px solid var(--harmony-comp-divider);

      .modal-title {
        margin: 0;
        font-size: var(--harmony-font-size-body-m);
        font-weight: 700;
        color: var(--text);
      }

      .modal-close {
        background: none;
        border: none;
        color: var(--muted);
        font-size: 20px;
        cursor: pointer;
        width: 28px;
        height: 28px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 6px;
        transition: background 0.15s ease;

        &:hover {
          background: var(--harmony-comp-background-secondary);
        }
      }
    }

    .modal-body {
      padding: 20px;

      .feedback-tip {
        font-size: var(--harmony-font-size-subtitle-s);
        color: var(--muted);
        margin: 0 0 12px;
        line-height: 1.6;
      }

      .feedback-textarea {
        width: 100%;
        padding: 10px 12px;
        border: 1px solid var(--harmony-comp-divider);
        border-radius: var(--harmony-corner-radius-level4);
        font-size: var(--harmony-font-size-subtitle-s);
        line-height: 1.6;
        color: var(--text);
        resize: vertical;
        font-family: var(--harmony-font-family);
        box-sizing: border-box;
        display: block;

        &:focus {
          border-color: var(--harmony-brand);
        }
        &::placeholder {
          color: var(--harmony-font-tertiary);
        }
      }

      .char-count-bottom {
        font-size: var(--harmony-font-size-body-s);
        color: var(--harmony-font-tertiary);
        text-align: right;
        padding: 4px 4px 0;
      }
    }

    .modal-footer {
      display: flex;
      gap: 10px;
      padding: 16px 20px;
      background: var(--harmony-comp-background-primary);
      border-top: 1px solid var(--harmony-comp-divider);

      button {
        flex: 1;
        padding: 10px 16px;
        border: none;
        border-radius: var(--harmony-corner-radius-level4);
        font-size: var(--harmony-font-size-subtitle-s);
        font-weight: 600;
        cursor: pointer;
        transition: all 0.15s ease;

        &.cancel-btn {
          background: var(--harmony-comp-background-primary);
          color: var(--muted);
          border: 1px solid var(--border);

          &:hover {
            background: var(--harmony-comp-background-secondary);
          }
        }

        &.confirm-btn {
          background: var(--primary);
          color: var(--harmony-comp-background-primary);

          &:hover {
            background: var(--harmony-interactive-hover);
          }
        }
      }
    }
  }
}

/* 动画 */

@keyframes typingBounce {
  0%, 80%, 100% { transform: scale(0); opacity: 0.5; }

}
</style>

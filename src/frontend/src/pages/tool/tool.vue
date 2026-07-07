<script setup lang="ts">
import { ref, onMounted, computed, watch, inject } from 'vue'
import { HButton, HTabs, HTabPane, HTooltip, HMessage } from '@/components/ui'
import pluginIcon from '../../assets/plugin.svg'
import { 
  getAllToolsAPI, 
  getOwnToolsAPI, 
  createToolAPI, 
  updateToolAPI, 
  deleteToolAPI,
  getDefaultToolLogoAPI,
  uploadFileAPI,
  type ToolResponse 
} from '../../apis/tool'
import { useUserStore } from '../../store/user'

const isMobile = inject<import('vue').Ref<boolean>>('isMobile', ref(false))

// 工具类型定义
interface Tool extends ToolResponse {
  user_id: string
  create_time?: string
  update_time?: string
}

// 创建工具表单类型
interface CreateToolForm {
  display_name: string  // 名称
  description: string
  logo_url: string
  openapi_schema?: any  // OpenAPI Schema
  auth_config?: {
    type: '' | 'bearer' | 'basic'
    token?: string
  }
}

// 更新工具表单类型
interface UpdateToolForm {
  tool_id: string
  display_name: string  // 名称
  description: string
  logo_url: string
  openapi_schema?: any
  auth_config?: {
    type: '' | 'bearer' | 'basic'
    token?: string
  }
}

// OpenAPI 工具接口
interface OpenAPITool {
  name: string
  description: string
  method: string
  path: string
}

// 响应式数据
const tools = ref<Tool[]>([])
const loading = ref(false)
const activeTab = ref('all') // all, own
const showCreateDrawer = ref(false)
const showEditDrawer = ref(false)
const showDeleteDialog = ref(false)
const toolToDelete = ref<Tool | null>(null)
const currentTool = ref<Tool | null>(null)
const userStore = useUserStore()

// OpenAPI Schema 相关
const defaultSchema = JSON.stringify({
  "openapi": "3.1.0",
  "info": {
    "title": "Untitled",
    "description": "Your OpenAPI specification",
    "version": "v1.0.0"
  },
  "servers": [{ "url": "" }],
  "paths": {},
  "components": { "schemas": {} }
}, null, 2)
// 创建表单相关
const schemaContent = ref(defaultSchema)
const authMethod = ref<'' | 'bearer' | 'basic'>('')
const apiKeyValue = ref('')
const availableTools = ref<OpenAPITool[]>([])
const logoPreview = ref('')
const logoUploading = ref(false)

// 编辑表单相关
const editSchemaContent = ref('')
const editAuthMethod = ref<'' | 'bearer' | 'basic'>('')
const editApiKeyValue = ref('')
const editAvailableTools = ref<OpenAPITool[]>([])
const editLogoPreview = ref('')
const editLogoUploading = ref(false)

// 示例 OpenAPI Schema
const exampleSchemas = [
  {
    label: '天气查询 API',
    value: JSON.stringify({
      "openapi": "3.1.0",
      "info": {
        "title": "Weather API",
        "description": "查询天气信息",
        "version": "v1.0.0"
      },
      "servers": [
        { "url": "https://api.weather.com" }
      ],
      "paths": {
        "/weather": {
          "get": {
            "summary": "获取天气",
            "description": "根据城市名称获取天气信息",
            "parameters": [
              {
                "name": "city",
                "in": "query",
                "required": true,
                "schema": { "type": "string" }
              }
            ]
          }
        }
      }
    }, null, 2)
  },
  {
    label: '空白模板',
    value: JSON.stringify({
      "openapi": "3.1.0",
      "info": {
        "title": "Untitled",
        "description": "Your OpenAPI specification",
        "version": "v1.0.0"
      },
      "servers": [{ "url": "" }],
      "paths": {},
      "components": { "schemas": {} }
    }, null, 2)
  }
]

// 表单数据
const createForm = ref<CreateToolForm>({
  display_name: '',
  description: '',
  logo_url: '',
  openapi_schema: null,
  auth_config: {
    type: ''
  }
})

const editForm = ref<UpdateToolForm>({
  tool_id: '',
  display_name: '',
  description: '',
  logo_url: '',
  openapi_schema: null,
  auth_config: {
    type: ''
  }
})



// 判断是否为用户自己的工具（可以删除的工具）
const isOwnTool = (tool: Tool) => {
  // 系统提供的工具（user_id = '0'）不能删除
  if (tool.user_id === '0') {
    return false
  }
  
  // 在"我的工具"标签页中，所有非系统工具都可以删除
  if (activeTab.value === 'own') {
    return true
  }
  
  // 在"全部工具"标签页中，只有当前用户创建的工具可以删除
  const isOwn = tool.user_id === userStore.userInfo?.id
  console.log('工具判断:', {
    toolId: tool.tool_id,
    toolUserId: tool.user_id,
    currentUserId: userStore.userInfo?.id,
    isOwn: isOwn,
    activeTab: activeTab.value,
    isSystemTool: tool.user_id === '0'
  })
  return isOwn
}

// 解析 OpenAPI Schema 获取可用工具
const parseOpenAPISchema = () => {
  try {
    const schema = JSON.parse(schemaContent.value)
    const tools: OpenAPITool[] = []
    
    if (schema.paths) {
      Object.entries(schema.paths).forEach(([path, methods]: [string, any]) => {
        Object.entries(methods).forEach(([method, details]: [string, any]) => {
          if (['get', 'post', 'put', 'delete', 'patch'].includes(method.toLowerCase())) {
            tools.push({
              name: details.operationId || `${method}_${path.replace(/\//g, '_')}`,
              description: details.summary || details.description || '',
              method: method.toUpperCase(),
              path: path
            })
          }
        })
      })
    }
    
    availableTools.value = tools
    createForm.value.openapi_schema = schema
  } catch (error) {
    HMessage.error('OpenAPI Schema 格式错误')
    availableTools.value = []
  }
}

// 获取默认头像
const getDefaultLogo = async () => {
  try {
    const response = await getDefaultToolLogoAPI()
    if (response.data.status_code === 200) {
      logoPreview.value = response.data.data.logo_url
      createForm.value.logo_url = response.data.data.logo_url
    }
  } catch (error) {
    console.error('获取默认头像失败:', error)
  }
}

// 处理头像上传
const handleLogoUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (!file) return
  
  // 验证文件类型
  const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
  if (!validTypes.includes(file.type)) {
    HMessage.error('请上传图片文件（支持 JPG、PNG、GIF、WebP）')
    return
  }
  
  // 验证文件大小（最大 5MB）
  if (file.size > 5 * 1024 * 1024) {
    HMessage.error('图片大小不能超过 5MB')
    return
  }
  
  logoUploading.value = true
  
  try {
    const response = await uploadFileAPI(file)
    if (response.data.status_code === 200) {
      // 上传接口返回的 data 直接是 URL 字符串
      const uploadedUrl = response.data.data as any as string
      logoPreview.value = uploadedUrl
      createForm.value.logo_url = uploadedUrl
      HMessage.success('头像上传成功')
    } else {
      HMessage.error(response.data.status_message || '头像上传失败')
    }
  } catch (error) {
    console.error('头像上传失败:', error)
    HMessage.error('头像上传失败')
  } finally {
    logoUploading.value = false
    // 清空 input，以便可以再次上传同一文件
    target.value = ''
  }
}

// 触发文件选择
const triggerLogoUpload = () => {
  const input = document.getElementById('logoUpload') as HTMLInputElement
  input?.click()
}

// 处理编辑头像上传
const handleEditLogoUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (!file) return
  
  // 验证文件类型
  const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
  if (!validTypes.includes(file.type)) {
    HMessage.error('请上传图片文件（支持 JPG、PNG、GIF、WebP）')
    return
  }
  
  // 验证文件大小（最大 5MB）
  if (file.size > 5 * 1024 * 1024) {
    HMessage.error('图片大小不能超过 5MB')
    return
  }
  
  editLogoUploading.value = true
  
  try {
    const response = await uploadFileAPI(file)
    if (response.data.status_code === 200) {
      const uploadedUrl = response.data.data as any as string
      editLogoPreview.value = uploadedUrl
      editForm.value.logo_url = uploadedUrl
      HMessage.success('头像上传成功')
    } else {
      HMessage.error(response.data.status_message || '头像上传失败')
    }
  } catch (error) {
    console.error('头像上传失败:', error)
    HMessage.error('头像上传失败')
  } finally {
    editLogoUploading.value = false
    target.value = ''
  }
}

// 触发编辑文件选择
const triggerEditLogoUpload = () => {
  const input = document.getElementById('editLogoUpload') as HTMLInputElement
  input?.click()
}

// 解析编辑的 OpenAPI Schema
const parseEditOpenAPISchema = () => {
  try {
    const schema = JSON.parse(editSchemaContent.value)
    const tools: OpenAPITool[] = []
    
    if (schema.paths) {
      Object.entries(schema.paths).forEach(([path, methods]: [string, any]) => {
        Object.entries(methods).forEach(([method, details]: [string, any]) => {
          if (['get', 'post', 'put', 'delete', 'patch'].includes(method.toLowerCase())) {
            tools.push({
              name: details.operationId || `${method}_${path.replace(/\//g, '_')}`,
              description: details.summary || details.description || '',
              method: method.toUpperCase(),
              path: path
            })
          }
        })
      })
    }
    
    editAvailableTools.value = tools
    editForm.value.openapi_schema = schema
  } catch (error) {
    HMessage.error('OpenAPI Schema 格式错误')
    editAvailableTools.value = []
  }
}

// 监听编辑 Schema 内容变化
const handleEditSchemaChange = () => {
  if (editSchemaContent.value) {
    parseEditOpenAPISchema()
  }
}

// 选择示例 Schema
const selectExample = (example: string) => {
  schemaContent.value = example
  parseOpenAPISchema()
}

// 监听 Schema 内容变化
const handleSchemaChange = () => {
  if (schemaContent.value) {
    parseOpenAPISchema()
  }
}

// 获取工具列表
const fetchTools = async () => {
  loading.value = true
  try {
    let response
    switch (activeTab.value) {
      case 'own':
        response = await getOwnToolsAPI()
        break
      default:
        response = await getAllToolsAPI()
        break
    }
    
    if (response.data.status_code === 200) {
      tools.value = response.data.data || []
      console.log('获取到的工具数据:', tools.value)
    } else {
      HMessage.error(response.data.status_message || '获取工具列表失败')
    }
  } catch (error) {
    console.error('获取工具列表失败:', error)
    HMessage.error('获取工具列表失败')
  } finally {
    loading.value = false
  }
}

// 创建工具
const handleCreateTool = async () => {
  try {
    // 构建鉴权配置
    let auth_config: any = undefined
    if (authMethod.value && authMethod.value !== '') {
      auth_config = {
        type: authMethod.value,
        token: apiKeyValue.value
      }
    }
    
    const requestData = {
      display_name: createForm.value.display_name,
      description: createForm.value.description,
      logo_url: createForm.value.logo_url,
      auth_config: auth_config,
      openapi_schema: createForm.value.openapi_schema || undefined
    }
    
    const response = await createToolAPI(requestData)
    if (response.data.status_code === 200) {
      HMessage.success('工具创建成功')
      showCreateDrawer.value = false
      resetCreateForm()
      fetchTools()
    } else {
      HMessage.error(response.data.status_message || '创建工具失败')
    }
  } catch (error) {
    console.error('创建工具失败:', error)
    HMessage.error('创建工具失败')
  }
}

// 编辑工具
const handleEditTool = async () => {
  try {
    // 构建鉴权配置
    let auth_config: any = undefined
    if (editAuthMethod.value && editAuthMethod.value !== '') {
      auth_config = {
        type: editAuthMethod.value,
        token: editApiKeyValue.value
      }
    }
    
    const requestData = {
      tool_id: editForm.value.tool_id,
      display_name: editForm.value.display_name,
      description: editForm.value.description,
      logo_url: editForm.value.logo_url,
      auth_config: auth_config,
      openapi_schema: editForm.value.openapi_schema || undefined
    }
    
    const response = await updateToolAPI(requestData)
    if (response.data.status_code === 200) {
      HMessage.success('工具更新成功')
      showEditDrawer.value = false
      resetEditForm()
      fetchTools()
    } else {
      HMessage.error(response.data.status_message || '更新工具失败')
    }
  } catch (error) {
    console.error('更新工具失败:', error)
    HMessage.error('更新工具失败')
  }
}

// 删除工具
const handleDeleteTool = (tool: Tool) => {
  // 系统工具不能删除
  if (tool.user_id === '0') {
    HMessage.warning('系统工具不能删除')
    return
  }
  
  // 只有工具的创建者可以删除
  if (!isOwnTool(tool)) {
    HMessage.warning('只能删除自己创建的工具')
    return
  }
  
  toolToDelete.value = tool
  showDeleteDialog.value = true
}

// 确认删除工具
const confirmDeleteTool = async () => {
  if (!toolToDelete.value) return
  
  try {
    const response = await deleteToolAPI({ tool_id: toolToDelete.value.tool_id })
    if (response.data.status_code === 200) {
      HMessage.success('工具删除成功')
      showDeleteDialog.value = false
      toolToDelete.value = null
      fetchTools()
    } else {
      HMessage.error(response.data.status_message || '删除工具失败')
    }
  } catch (error) {
    console.error('删除工具失败:', error)
    HMessage.error('删除工具失败')
  }
}

// 取消删除
const cancelDelete = () => {
  showDeleteDialog.value = false
  toolToDelete.value = null
}

// 判断工具是否可编辑（只有用户自定义的工具可以编辑）
const isToolEditable = (tool: Tool) => {
  // 系统工具（user_id = '0'）不可编辑
  if (tool.user_id === '0') {
    return false
  }
  // 只有工具的创建者可以编辑
  return tool.user_id === userStore.userInfo?.id
}

// 打开编辑抽屉
const openEditDrawer = (tool: Tool) => {
  // 检查是否可编辑
  if (!isToolEditable(tool)) {
    HMessage.warning('系统工具不可编辑')
    return
  }
  
  currentTool.value = tool
  editForm.value = {
    tool_id: tool.tool_id,
    display_name: tool.display_name,
    description: tool.description,
    logo_url: tool.logo_url,
    openapi_schema: tool.openapi_schema,
    auth_config: tool.auth_config
  }
  
  // 设置头像预览
  editLogoPreview.value = tool.logo_url || ''
  
  // 设置 OpenAPI Schema
  if (tool.openapi_schema) {
    editSchemaContent.value = JSON.stringify(tool.openapi_schema, null, 2)
    parseEditOpenAPISchema()
  } else {
    editSchemaContent.value = defaultSchema
    editAvailableTools.value = []
  }
  
  // 设置鉴权信息
  if (tool.auth_config && tool.auth_config.type) {
    editAuthMethod.value = tool.auth_config.type
    editApiKeyValue.value = tool.auth_config.token || ''
  } else {
    editAuthMethod.value = ''
    editApiKeyValue.value = ''
  }
  
  showEditDrawer.value = true
}

// 重置创建表单
const resetCreateForm = () => {
  createForm.value = {
    display_name: '',
    description: '',
    logo_url: '',
    openapi_schema: null,
    auth_config: {
      type: ''
    }
  }
  schemaContent.value = defaultSchema
  authMethod.value = ''
  apiKeyValue.value = ''
  availableTools.value = []
  // 重新获取默认头像
  getDefaultLogo()
}

// 重置编辑表单
const resetEditForm = () => {
  editForm.value = {
    tool_id: '',
    display_name: '',
    description: '',
    logo_url: '',
    openapi_schema: null,
    auth_config: {
      type: ''
    }
  }
  editSchemaContent.value = ''
  editAuthMethod.value = ''
  editApiKeyValue.value = ''
  editAvailableTools.value = []
  editLogoPreview.value = ''
  currentTool.value = null
}

// 切换标签页
const handleTabChange = () => {
  fetchTools()
}

// 监听标签页变化
watch(activeTab, () => {
  handleTabChange()
})

// 刷新数据
const handleRefresh = () => {
  fetchTools()
}

// 格式化时间
const formatTime = (timeStr?: string) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  return date.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
}

// 格式化相对时间
const formatRelativeTime = (timeStr?: string) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  if (days === 0) return '今天'
  if (days === 1) return '昨天'
  if (days < 7) return `${days}天前`
  if (days < 30) return `${Math.floor(days / 7)}周前`
  return formatTime(timeStr)
}

onMounted(() => {
  userStore.initUserState()
  console.log('用户信息:', userStore.userInfo)
  console.log('是否登录:', userStore.isLoggedIn)
  fetchTools()
  getDefaultLogo()
})
</script>

<template>
  <!-- Desktop -->
  <div v-if="!isMobile" class="tool-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-title">
        <img :src="pluginIcon" alt="工具" class="title-icon" />
        <h2>工具管理</h2>
      </div>
      <div class="header-actions">
        <HButton type="secondary" @click="handleRefresh" :loading="loading">
          🔄 刷新
        </HButton>
        <HButton type="primary" @click="showCreateDrawer = true">
          ➕ 创建工具
        </HButton>
      </div>
    </div>

    <!-- 标签页 -->
    <div class="tool-controls">
      <HTabs v-model="activeTab" class="tool-tabs">
        <HTabPane label="全部工具" name="all">
          <!-- content rendered below -->
        </HTabPane>
        <HTabPane label="我的工具" name="own">
          <!-- content rendered below -->
        </HTabPane>
      </HTabs>
    </div>

    <!-- 工具列表 -->
    <div class="tool-container" v-h-loading="loading">
      <!-- 列表头部 -->
      <div class="list-header" v-if="tools.length > 0">
        <div class="col-icon"></div>
        <div class="col-name">名称</div>
        <div class="col-desc">描述</div>
        <div class="col-type">类型</div>
        <div class="col-time">创建时间</div>
        <div class="col-actions">操作</div>
      </div>
      
      <!-- 列表内容 -->
      <div class="tool-list" v-if="tools.length > 0">
        <div 
          v-for="tool in tools" 
          :key="tool.tool_id" 
          class="tool-row"
          @click="isToolEditable(tool) ? openEditDrawer(tool) : null"
          :class="{ 'clickable': isToolEditable(tool) }"
        >
          <div class="col-icon">
            <div class="tool-avatar">
              <img 
                :src="tool.logo_url || '/src/assets/tool/default.png'" 
                :alt="tool.display_name"
                @error="(e) => { const target = e.target as HTMLImageElement; target.src = '/src/assets/tool/default.png' }"
              />
            </div>
          </div>
          <div class="col-name">
            <span class="tool-name">{{ tool.display_name }}</span>
          </div>
          <div class="col-desc">
            <span class="tool-desc">{{ tool.description }}</span>
          </div>
          <div class="col-type">
            <span v-if="tool.user_id === '0'" class="type-badge system">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
              </svg>
              系统工具
            </span>
            <span v-else class="type-badge custom">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"></path>
                <circle cx="9" cy="7" r="4"></circle>
              </svg>
              自定义
            </span>
          </div>
          <div class="col-time">
            <span class="time-text">{{ formatRelativeTime(tool.create_time) }}</span>
          </div>
          <div class="col-actions" @click.stop>
            <HTooltip content="编辑" placement="top" v-if="isToolEditable(tool)">
              <button class="action-btn edit-btn" @click="openEditDrawer(tool)">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <path d="M11 2L14 5L7 12H4V9L11 2Z" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/>
                  <line x1="9" y1="4" x2="12" y2="7" stroke="currentColor" stroke-width="1.3"/>
                </svg>
              </button>
            </HTooltip>
            <HTooltip content="系统工具不可编辑" placement="top" v-else>
              <button class="action-btn view-btn" disabled>
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <path d="M11 2L14 5L7 12H4V9L11 2Z" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/>
                  <line x1="9" y1="4" x2="12" y2="7" stroke="currentColor" stroke-width="1.3"/>
                </svg>
              </button>
            </HTooltip>
            <HTooltip content="删除" placement="top" v-if="isOwnTool(tool)">
              <button class="action-btn delete-btn" @click="handleDeleteTool(tool)">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M2 4H14L12.5 14H3.5L2 4Z" stroke="currentColor" stroke-width="1.2"/>
                <line x1="6" y1="4" x2="6" y2="2" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
                <line x1="10" y1="4" x2="10" y2="2" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
              </svg>
              </button>
            </HTooltip>
            <HTooltip content="系统工具不可删除" placement="top" v-else>
              <button class="action-btn view-btn" disabled>
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M2 4H14L12.5 14H3.5L2 4Z" stroke="currentColor" stroke-width="1.2"/>
                <line x1="6" y1="4" x2="6" y2="2" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
                <line x1="10" y1="4" x2="10" y2="2" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
              </svg>
              </button>
            </HTooltip>
          </div>
        </div>
      </div>
      
      <!-- 空状态 -->
      <div v-if="tools.length === 0 && !loading" class="empty-state">
        <div class="empty-visual">
          <div class="empty-icon-wrapper">
            <img :src="pluginIcon" alt="No Tools" class="empty-icon" />
          </div>
        </div>
        <div class="empty-content">
          <h3>{{ activeTab === 'own' ? '还没有创建任何工具' : '暂无工具' }}</h3>
          <p>添加工具可以让您的智能体拥有更多能力，开始创建你的第一个工具吧！</p>
          <HButton
            type="primary"
            @click="showCreateDrawer = true"
            class="empty-btn"
          >
            ➕ 创建第一个工具
          </HButton>
        </div>
      </div>
    </div>

    <!-- 创建工具侧边栏 -->
    <transition name="drawer">
      <div
        v-if="showCreateDrawer"
        role="dialog"
        aria-labelledby="dialog-title"
        class="drawer-overlay"
        @click="showCreateDrawer = false"
      >
        <div
          class="drawer-content"
          @click.stop
        >
          <!-- 头部 -->
          <div class="drawer-header">
            <h2 id="dialog-title" class="drawer-title">创建API工具</h2>
          </div>

          <!-- 内容区域 -->
          <div class="drawer-body">
            <!-- 工具头像 -->
            <div class="drawer-form-group">
              <label class="drawer-label">工具头像</label>
              <div class="logo-upload-area">
                <div 
                  class="logo-preview"
                  :class="{ 'uploading': logoUploading }"
                  @click="triggerLogoUpload"
                >
                  <img 
                    v-if="logoPreview" 
                    :src="logoPreview" 
                    alt="工具头像" 
                    class="logo-image"
                  />
                  <div v-else class="logo-placeholder">
                    <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <rect width="18" height="18" x="3" y="3" rx="2" ry="2"/>
                      <circle cx="9" cy="9" r="2"/>
                      <path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/>
                    </svg>
                  </div>
                  <div v-if="logoUploading" class="logo-loading">
                    <div class="spinner"></div>
                  </div>
                  <div class="logo-overlay">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                      <polyline points="17 8 12 3 7 8"/>
                      <line x1="12" x2="12" y1="3" y2="15"/>
                    </svg>
                    <span>点击上传</span>
                  </div>
                </div>
                <input
                  type="file"
                  id="logoUpload"
                  accept="image/jpeg,image/jpg,image/png,image/gif,image/webp"
                  @change="handleLogoUpload"
                  style="display: none"
                />
                <p class="logo-hint">支持 JPG、PNG、GIF、WebP 格式，大小不超过 5MB</p>
              </div>
            </div>

            <!-- 工具名称 -->
            <div class="drawer-form-group">
              <label for="toolName" class="drawer-label">名称</label>
              <input
                v-model="createForm.display_name"
                type="text"
                id="toolName"
                name="toolName"
                placeholder="输入工具名称"
                class="drawer-input"
              />
            </div>

            <!-- 工具描述 -->
            <div class="drawer-form-group">
              <label for="toolDescription" class="drawer-label">描述</label>
              <textarea
                v-model="createForm.description"
                rows="3"
                id="toolDescription"
                name="toolDescription"
                placeholder="描述工具的功能和用途"
                class="drawer-textarea"
              ></textarea>
            </div>

            <!-- OpenAPI Schema -->
            <div class="drawer-form-group">
              <div class="drawer-field-header">
                <label for="schemaContent" class="drawer-label">OpenAPI Schema</label>
                <div class="drawer-field-actions">
                  <select
                    v-model="schemaContent"
                    @change="handleSchemaChange"
                    class="drawer-select-small"
                  >
                    <option
                      v-for="example in exampleSchemas"
                      :key="example.label"
                      :value="example.value"
                    >
                      {{ example.label }}
                    </option>
                  </select>
                </div>
              </div>
              <textarea
                v-model="schemaContent"
                id="schemaContent"
                name="schemaContent"
                placeholder="输入您的 OpenAPI schema"
                @blur="handleSchemaChange"
                class="drawer-code-textarea"
              ></textarea>
            </div>

            <!-- 可用工具列表 -->
            <div class="drawer-form-group">
              <label for="toolsTable" class="drawer-label">可用工具</label>
              <div class="drawer-table-wrapper">
                <table class="drawer-table" id="toolsTable">
                  <thead class="drawer-table-header">
                    <tr>
                      <th>名称</th>
                      <th>描述</th>
                      <th>方法</th>
                      <th>路径</th>
                    </tr>
                  </thead>
                  <tbody class="drawer-table-body">
                    <tr v-if="availableTools.length === 0">
                      <td colspan="4" class="drawer-table-empty">无</td>
                    </tr>
                    <tr
                      v-for="(tool, index) in availableTools"
                      :key="index"
                      class="drawer-table-row"
                    >
                      <td class="drawer-table-cell">{{ tool.name }}</td>
                      <td class="drawer-table-cell">{{ tool.description }}</td>
                      <td class="drawer-table-cell">
                        <span class="drawer-badge">{{ tool.method }}</span>
                      </td>
                      <td class="drawer-table-cell drawer-table-path">{{ tool.path }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- 鉴权方式 -->
            <div class="drawer-form-group">
              <label for="authMethod" class="drawer-label">鉴权方式</label>
              <select
                v-model="authMethod"
                id="authMethod"
                class="drawer-select"
              >
                <option value="">无鉴权</option>
                <option value="bearer">Bearer Token</option>
                <option value="basic">Basic Auth</option>
              </select>
            </div>

            <!-- Token 输入 -->
            <div v-if="authMethod && authMethod !== ''" class="drawer-form-group">
              <label for="authToken" class="drawer-label">
                {{ authMethod === 'bearer' ? 'Bearer Token' : 'Basic Auth Token' }}
              </label>
              <input
                v-model="apiKeyValue"
                type="password"
                id="authToken"
                :placeholder="authMethod === 'bearer' ? '输入 Bearer Token' : '输入 Basic Auth Token'"
                class="drawer-input"
              />
              <p class="drawer-hint">
                {{ authMethod === 'bearer' ? '请输入 Bearer Token，将自动添加 "Bearer " 前缀' : '请输入 Basic Auth Token（格式：username:password 的 Base64 编码）' }}
              </p>
            </div>
          </div>

          <!-- 底部按钮 -->
          <div class="drawer-footer">
            <div class="drawer-footer-buttons">
              <button
                @click="showCreateDrawer = false"
                class="drawer-footer-button drawer-footer-button-cancel"
              >
                取消
              </button>
              <button
                @click="handleCreateTool"
                class="drawer-footer-button drawer-footer-button-save"
              >
                保存
              </button>
            </div>
          </div>

          <!-- 关闭按钮 -->
          <button
            type="button"
            @click="showCreateDrawer = false"
            class="drawer-close"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="drawer-close-icon">
              <path d="M18 6 6 18"></path>
              <path d="m6 6 12 12"></path>
            </svg>
            <span class="sr-only">Close</span>
          </button>
        </div>
      </div>
    </transition>

    <!-- 编辑工具侧边栏 -->
    <transition name="drawer">
      <div
        v-if="showEditDrawer"
        role="dialog"
        aria-labelledby="edit-dialog-title"
        class="drawer-overlay"
        @click="showEditDrawer = false"
      >
        <div
          class="drawer-content"
          @click.stop
        >
          <!-- 头部 -->
          <div class="drawer-header">
            <h2 id="edit-dialog-title" class="drawer-title">编辑工具</h2>
          </div>

          <!-- 内容区域 -->
          <div class="drawer-body">
            <!-- 工具头像 -->
            <div class="drawer-form-group">
              <label class="drawer-label">工具头像</label>
              <div class="logo-upload-area">
                <div 
                  class="logo-preview"
                  :class="{ 'uploading': editLogoUploading }"
                  @click="triggerEditLogoUpload"
                >
                  <img 
                    v-if="editLogoPreview" 
                    :src="editLogoPreview" 
                    alt="工具头像" 
                    class="logo-image"
                  />
                  <div v-else class="logo-placeholder">
                    <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <rect width="18" height="18" x="3" y="3" rx="2" ry="2"/>
                      <circle cx="9" cy="9" r="2"/>
                      <path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/>
                    </svg>
                  </div>
                  <div v-if="editLogoUploading" class="logo-loading">
                    <div class="spinner"></div>
                  </div>
                  <div class="logo-overlay">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                      <polyline points="17 8 12 3 7 8"/>
                      <line x1="12" x2="12" y1="3" y2="15"/>
                    </svg>
                    <span>点击上传</span>
                  </div>
                </div>
                <input
                  type="file"
                  id="editLogoUpload"
                  accept="image/jpeg,image/jpg,image/png,image/gif,image/webp"
                  @change="handleEditLogoUpload"
                  style="display: none"
                />
                <p class="logo-hint">支持 JPG、PNG、GIF、WebP 格式，大小不超过 5MB</p>
              </div>
            </div>

            <!-- 工具名称 -->
            <div class="drawer-form-group">
              <label for="editToolName" class="drawer-label">名称</label>
              <input
                v-model="editForm.display_name"
                type="text"
                id="editToolName"
                name="editToolName"
                placeholder="输入工具名称"
                class="drawer-input"
              />
            </div>

            <!-- 工具描述 -->
            <div class="drawer-form-group">
              <label for="editToolDescription" class="drawer-label">描述</label>
              <textarea
                v-model="editForm.description"
                rows="3"
                id="editToolDescription"
                name="editToolDescription"
                placeholder="描述工具的功能和用途"
                class="drawer-textarea"
              ></textarea>
            </div>

            <!-- OpenAPI Schema -->
            <div class="drawer-form-group">
              <div class="drawer-field-header">
                <label for="editSchemaContent" class="drawer-label">OpenAPI Schema</label>
                <div class="drawer-field-actions">
                  <select
                    v-model="editSchemaContent"
                    @change="handleEditSchemaChange"
                    class="drawer-select-small"
                  >
                    <option
                      v-for="example in exampleSchemas"
                      :key="example.label"
                      :value="example.value"
                    >
                      {{ example.label }}
                    </option>
                  </select>
                </div>
              </div>
              <textarea
                v-model="editSchemaContent"
                id="editSchemaContent"
                name="editSchemaContent"
                placeholder="输入您的 OpenAPI schema"
                @blur="handleEditSchemaChange"
                class="drawer-code-textarea"
              ></textarea>
            </div>

            <!-- 可用工具列表 -->
            <div class="drawer-form-group">
              <label for="editToolsTable" class="drawer-label">可用工具</label>
              <div class="drawer-table-wrapper">
                <table class="drawer-table" id="editToolsTable">
                  <thead class="drawer-table-header">
                    <tr>
                      <th>名称</th>
                      <th>描述</th>
                      <th>方法</th>
                      <th>路径</th>
                    </tr>
                  </thead>
                  <tbody class="drawer-table-body">
                    <tr v-if="editAvailableTools.length === 0">
                      <td colspan="4" class="drawer-table-empty">无</td>
                    </tr>
                    <tr
                      v-for="(tool, index) in editAvailableTools"
                      :key="index"
                      class="drawer-table-row"
                    >
                      <td class="drawer-table-cell">{{ tool.name }}</td>
                      <td class="drawer-table-cell">{{ tool.description }}</td>
                      <td class="drawer-table-cell">
                        <span class="drawer-badge">{{ tool.method }}</span>
                      </td>
                      <td class="drawer-table-cell drawer-table-path">{{ tool.path }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- 鉴权方式 -->
            <div class="drawer-form-group">
              <label for="editAuthMethod" class="drawer-label">鉴权方式</label>
              <select
                v-model="editAuthMethod"
                id="editAuthMethod"
                class="drawer-select"
              >
                <option value="">无鉴权</option>
                <option value="bearer">Bearer Token</option>
                <option value="basic">Basic Auth</option>
              </select>
            </div>

            <!-- Token 输入 -->
            <div v-if="editAuthMethod && editAuthMethod !== ''" class="drawer-form-group">
              <label for="editAuthToken" class="drawer-label">
                {{ editAuthMethod === 'bearer' ? 'Bearer Token' : 'Basic Auth Token' }}
              </label>
              <input
                v-model="editApiKeyValue"
                type="password"
                id="editAuthToken"
                :placeholder="editAuthMethod === 'bearer' ? '输入 Bearer Token' : '输入 Basic Auth Token'"
                class="drawer-input"
              />
              <p class="drawer-hint">
                {{ editAuthMethod === 'bearer' ? '请输入 Bearer Token，将自动添加 "Bearer " 前缀' : '请输入 Basic Auth Token（格式：username:password 的 Base64 编码）' }}
              </p>
            </div>
          </div>

          <!-- 底部按钮 -->
          <div class="drawer-footer">
            <div class="drawer-footer-buttons">
              <button
                @click="showEditDrawer = false"
                class="drawer-footer-button drawer-footer-button-cancel"
              >
                取消
              </button>
              <button
                @click="handleEditTool"
                class="drawer-footer-button drawer-footer-button-save"
              >
                保存
              </button>
            </div>
          </div>

          <!-- 关闭按钮 -->
          <button
            type="button"
            @click="showEditDrawer = false"
            class="drawer-close"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="drawer-close-icon">
              <path d="M18 6 6 18"></path>
              <path d="m6 6 12 12"></path>
            </svg>
            <span class="sr-only">Close</span>
          </button>
        </div>
      </div>
    </transition>

    <!-- 删除确认弹窗 -->
    <transition name="modal">
      <div
        v-if="showDeleteDialog"
        class="delete-modal-overlay"
        @click="cancelDelete"
      >
        <div
          class="delete-modal"
          @click.stop
        >
          <!-- 图标 -->
          <div class="delete-modal-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M3 6h18"/>
              <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/>
              <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/>
              <line x1="10" x2="10" y1="11" y2="17"/>
              <line x1="14" x2="14" y1="11" y2="17"/>
            </svg>
          </div>
          
          <!-- 标题 -->
          <h3 class="delete-modal-title">确认删除工具</h3>
          
          <!-- 内容 -->
          <p class="delete-modal-content">
            确定要删除工具 <strong>"{{ toolToDelete?.display_name }}"</strong> 吗？
            <br>
            <span class="delete-modal-warning">此操作不可恢复，请谨慎操作。</span>
          </p>
          
          <!-- 按钮 -->
          <div class="delete-modal-actions">
            <button
              @click="cancelDelete"
              class="delete-modal-button delete-modal-button-cancel"
            >
              取消
            </button>
            <button
              @click="confirmDeleteTool"
              class="delete-modal-button delete-modal-button-confirm"
            >
              确定删除
            </button>
          </div>
        </div>
      </div>
    </transition>
  </div>

  <!-- Mobile: hmos mobile-list -->
  <div v-else class="tool-mobile">
    <div class="tm-header">
      <button class="tm-create-btn" @click="showCreateDrawer = true">+ 添加工具</button>
    </div>

    <div class="tm-list" v-if="tools.length > 0">
      <div v-for="tool in tools" :key="tool.tool_id" class="tm-item">
        <div class="tm-item__icon">
          <img
            :src="tool.logo_url || '/src/assets/tool/default.png'"
            :alt="tool.display_name"
            @error="(e) => { const target = e.target as HTMLImageElement; target.src = '/src/assets/tool/default.png' }"
            style="width:100%;height:100%;object-fit:cover;border-radius:inherit;"
          />
        </div>
        <div class="tm-item__content">
          <h3 class="tm-item__name">
            {{ tool.display_name }}
            <span v-if="tool.user_id === '0'" class="tm-official-tag">系统</span>
          </h3>
          <p class="tm-item__desc">{{ tool.description }}</p>
        </div>
        <div class="tm-item__actions">
          <button
            v-if="isToolEditable(tool)"
            class="tm-action"
            @click="openEditDrawer(tool)"
            title="编辑"
          >&#9998;</button>
          <button
            v-if="isOwnTool(tool)"
            class="tm-action tm-action--danger"
            @click="handleDeleteTool(tool)"
            title="删除"
          >&#128465;</button>
        </div>
      </div>
    </div>

    <div v-else-if="!loading" class="tm-empty"><p>暂无工具</p></div>
  </div>
</template>

<style lang="scss" scoped>
.tool-page {
  padding: 32px;
  min-height: 100vh;
  background: var(--harmony-comp-background-primary);
  
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    background: var(--harmony-comp-background-primary);
    padding: var(--harmony-padding-level16) var(--harmony-padding-level16);
    border-radius: var(--harmony-corner-radius-level8);
    box-shadow: 0 6px 24px var(--harmony-shadow-sm);
    border: 1px solid var(--harmony-comp-divider);
    
    .header-title {
      display: flex;
      align-items: center;
      gap: 14px;
      
      .title-icon {
        width: 36px;
        height: 36px;
      }
      
      h2 {
        margin: 0;
        font-size: var(--harmony-font-size-title-m);
        font-weight: 600;
        background: var(--harmony-brand);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
      }
    }
    
    .header-actions {
      display: flex;
      gap: 12px;

      .h-button {
        border-radius: var(--harmony-corner-radius-level8);
        font-weight: 600;
        padding: var(--harmony-padding-level8) var(--harmony-padding-level16);
        font-size: var(--harmony-font-size-body-m);
        transition: all 0.3s ease;

        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 6px 20px var(--harmony-comp-emphasize-tertiary);
        }
      }
    }
  }
  
  .tool-controls {
    margin-bottom: 0;
    padding: 0;
    background: var(--harmony-comp-background-primary);
    border-radius: var(--harmony-corner-radius-level8) 16px 0 0;
    box-shadow: none;
    border: 1px solid var(--harmony-comp-divider);
    border-bottom: none;
    overflow: hidden;
    
    .tool-tabs {
      .h-tabs__header {
        margin: 0;
        border-bottom: 1px solid var(--harmony-comp-divider);
        background: var(--harmony-comp-background-primary);
        padding: 0 24px;
      }

      .h-tabs__item {
        font-weight: 500;
        font-size: var(--harmony-font-size-body-m);
        padding: 0 20px;
        height: 48px;
        line-height: 48px;
        color: var(--harmony-font-secondary);
        transition: all 0.3s;
        border: none;

        &.h-tabs__item--active {
          color: var(--harmony-brand);
          font-weight: 600;
          border-bottom: 3px solid;
          border-image: linear-gradient(90deg, var(--harmony-brand), var(--harmony-brand)) 1;
        }

        &:hover {
          color: var(--harmony-brand);
          background: var(--harmony-comp-emphasize-tertiary);
        }
      }

      .tab-label {
        display: flex;
        align-items: center;
        gap: 8px;

        svg {
          transition: transform 0.3s;
        }

        &:hover svg {
          transform: scale(1.1);
        }
      }
    }
  }
  
  .tool-container {
    background: var(--harmony-comp-background-primary);
    border: 1px solid var(--harmony-comp-divider);
    border-top: none;
    border-radius: 0 0 16px 16px;
    overflow: hidden;
    box-shadow: 0 2px 8px var(--harmony-shadow-sm);
  }
  
  .list-header {
    display: grid;
    grid-template-columns: 60px 1.5fr 2fr 120px 140px 120px;
    gap: 16px;
    padding: var(--harmony-padding-level10) var(--harmony-padding-level16);
    background: var(--harmony-comp-background-primary);
    font-weight: 600;
    font-size: var(--harmony-font-size-subtitle-s);
    color: var(--harmony-font-secondary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    
    > div {
      display: flex;
      align-items: center;
    }
  }
  
  .tool-list {
    .tool-row {
      display: grid;
      grid-template-columns: 60px 1.5fr 2fr 120px 140px 120px;
      gap: 16px;
      padding: var(--harmony-padding-level10) var(--harmony-padding-level16);
      border-bottom: 1px solid var(--harmony-comp-divider);
      transition: all 0.2s ease;
      cursor: default;
      
      &.clickable {
        cursor: pointer;
      }
      
      &:hover {
        background: linear-gradient(to right, var(--harmony-comp-emphasize-tertiary), var(--harmony-comp-emphasize-tertiary));
        
        .tool-avatar {
          transform: scale(1.08);
        }
        
        .tool-name {
          color: var(--harmony-brand);
        }
      }
      
      &:last-child {
        border-bottom: none;
      }
      
      > div {
        display: flex;
        align-items: center;
      }
      
      .col-icon {
        .tool-avatar {
          width: 44px;
          height: 44px;
          border-radius: var(--harmony-corner-radius-level6);
          overflow: hidden;
          transition: all 0.3s ease;
          
          img {
            width: 100%;
            height: 100%;
            object-fit: contain;
          }
        }
      }
      
      .col-name {
        .tool-name {
          font-size: var(--harmony-font-size-body-l);
          font-weight: 600;
          color: var(--harmony-font-primary);
          transition: color 0.2s;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }
      }
      
      .col-desc {
        .tool-desc {
          font-size: var(--harmony-font-size-subtitle-s);
          color: var(--harmony-font-secondary);
          line-height: 1.5;
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }
      }
      
      .col-type {
        .type-badge {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          padding: 6px 12px;
          border-radius: var(--harmony-corner-radius-level18);
          font-size: var(--harmony-font-size-body-s);
          font-weight: 600;
          letter-spacing: 0.3px;
          
          &.system {
            background: var(--harmony-comp-emphasize-tertiary);
            color: var(--harmony-brand);
            border: 1px solid var(--harmony-comp-emphasize-tertiary);
          }
          
          &.custom {
            background: var(--harmony-comp-emphasize-tertiary);
            color: var(--harmony-brand);
            border: 1px solid var(--harmony-comp-emphasize-tertiary);
          }
          
          svg {
            flex-shrink: 0;
          }
        }
      }
      
      .col-time {
        .time-text {
          font-size: var(--harmony-font-size-subtitle-s);
          color: var(--harmony-font-tertiary);
          font-weight: 500;
        }
      }
      
      .col-actions {
        display: flex;
        gap: 8px;
        justify-content: flex-end;
        
        .action-btn {
          width: 36px;
          height: 36px;
          border-radius: var(--harmony-corner-radius-level6);
          border: none;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          transition: all 0.2s ease;
          opacity: 1;
          
          &.edit-btn {
            background: var(--harmony-brand);
            color: white;
            
            &:hover {
              transform: translateY(-1px);
              box-shadow: 0 2px 8px rgba(0,0,0,0.12);
            }
          }
          
          &.delete-btn {
            background: var(--harmony-warning);
            color: white;
            
            &:hover {
              transform: translateY(-1px);
              box-shadow: 0 2px 8px rgba(0,0,0,0.12);
            }
          }
          
          &.view-btn {
            background: var(--harmony-comp-divider);
            color: var(--harmony-font-tertiary);
            cursor: not-allowed;
            
            &:hover {
              transform: none;
              box-shadow: none;
            }
          }
        }
      }
    }
  }
}

/* 空状态样式 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 40px;
  text-align: center;
  
  .empty-visual {
    margin-bottom: 24px;
    display: flex;
    justify-content: center;
    align-items: center;
    
    .empty-icon-wrapper {
      width: 100px;
      height: 100px;
      display: flex;
      justify-content: center;
      align-items: center;
      background: var(--harmony-comp-emphasize-tertiary);
      border-radius: var(--harmony-corner-radius-level18);
      position: relative;
      
      &::before {
        content: '';
        position: absolute;
        inset: -3px;
        background: var(--harmony-brand);
        border-radius: var(--harmony-corner-radius-level18);
        opacity: 0.15;
        z-index: -1;
      }
      
      .empty-icon {
        width: 56px;
        height: 56px;
        opacity: 0.8;
        border-radius: 0;
        object-fit: contain;
        display: block;
      }
    }
  }
  
  .empty-content {
    h3 {
      font-size: var(--harmony-font-size-title-s);
      font-weight: 600;
      color: var(--harmony-font-primary);
      margin: 0 0 8px;
      letter-spacing: -0.3px;
    }
    
    p {
      margin: 0 0 24px;
      font-size: var(--harmony-font-size-body-m);
      color: var(--harmony-font-secondary);
      max-width: 400px;
      line-height: 1.6;
    }
    
    .empty-btn {
      border-radius: var(--harmony-corner-radius-level8);
      padding: 14px 32px;
      font-weight: 600;
      font-size: var(--harmony-font-size-body-l);
      transition: all 0.3s ease;
      
      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px var(--harmony-comp-emphasize-tertiary);
      }
    }
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .tool-page {
    .list-header,
    .tool-list .tool-row {
      grid-template-columns: 50px 1.2fr 1.8fr 100px 120px 100px;
      gap: 12px;
    }
  }
}

@media (max-width: 768px) {
  .tool-page {
    padding: 20px;
    
    .page-header {
      flex-direction: column;
      gap: 20px;
      align-items: stretch;
      padding: 24px;
      
      .header-title {
        .title-icon {
          width: 32px;
          height: 32px;
        }
        
        h2 {
          font-size: var(--harmony-font-size-title-s);
        }
      }
      
      .header-actions {
        justify-content: stretch;

        .h-button {
          flex: 1;
        }
      }
    }

    .tool-controls {
      .tool-tabs {
        .h-tabs__item {
          padding: 0 16px;
          font-size: var(--harmony-font-size-body-m);
        }
      }
    }
    
    .list-header {
      display: none;
    }
    
    .tool-list .tool-row {
      grid-template-columns: 1fr;
      gap: 12px;
      padding: 20px;
      border-radius: var(--harmony-corner-radius-level8);
      margin: 12px;
      background: var(--harmony-comp-background-primary);
      border: 1px solid var(--harmony-comp-divider);
      
      .col-icon {
        justify-content: center;
        
        .tool-avatar {
          width: 60px;
          height: 60px;
        }
      }
      
      .col-name,
      .col-desc,
      .col-type,
      .col-time {
        justify-content: center;
        text-align: center;
        
        .tool-name {
          font-size: var(--harmony-font-size-body-l);
        }
      }
      
      .col-actions {
        justify-content: center;
        
        .action-btn {
          opacity: 1;
          transform: translateX(0);
        }
      }
    }
    
    .drawer-content {
      width: 100vw !important;
      max-width: 100vw !important;
    }
  }
}

/* 侧边栏过渡动画 */
.drawer-enter-active,
.drawer-leave-active {
  transition: opacity 0.3s ease;
}

.drawer-enter-from,
.drawer-leave-to {
  opacity: 0;
}

.drawer-enter-active .drawer-content,
.drawer-leave-active .drawer-content {
  transition: transform 0.5s ease-in-out;
}

.drawer-enter-from .drawer-content {
  transform: translateX(100%);
}

.drawer-leave-to .drawer-content {
  transform: translateX(100%);
}

/* 侧边栏样式 */
.drawer-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background-color: var(--harmony-comp-background-secondary);
  pointer-events: auto;
}

.drawer-content {
  position: fixed;
  top: 0;
  right: 0;
  height: 100%;
  width: 800px;
  max-width: 800px;
  background-color: var(--harmony-comp-background-primary);
  box-shadow: -4px 0 20px var(--harmony-shadow-md);
  display: flex;
  flex-direction: column;
  pointer-events: auto;
}

.dark .drawer-content {
  background-color: rgb(3, 7, 18);
}

.drawer-header {
  padding: 1.75rem 1.5rem;
  border-bottom: 1px solid var(--harmony-comp-divider);
  flex-shrink: 0;
  background: linear-gradient(to bottom, var(--harmony-comp-background-primary), var(--harmony-comp-background-primary));
}

.dark .drawer-header {
  border-bottom-color: rgb(38, 38, 38);
  background: linear-gradient(to bottom, rgb(3, 7, 18), rgb(10, 12, 20));
}

.drawer-title {
  font-size: var(--harmony-font-size-title-m);
  font-weight: 700;
  color: var(--harmony-font-primary);
  margin: 0;
  letter-spacing: -0.025em;
}

.dark .drawer-title {
  color: rgb(243, 244, 246);
}

.drawer-body {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem 0;
  padding-bottom: 10rem;
  background-color: var(--harmony-comp-background-primary);
}

.dark .drawer-body {
  background-color: rgb(10, 12, 20);
}

.drawer-form-group {
  padding: 0 1.5rem;
  margin-bottom: 1.5rem;
}

.drawer-label {
  display: block;
  margin-bottom: 0.5rem;
  font-size: var(--harmony-font-size-body-m);
  font-weight: 600;
  color: var(--harmony-font-primary);
}

.dark .drawer-label {
  color: rgb(209, 213, 219);
}

.drawer-hint {
  margin-top: 0.5rem;
  font-size: var(--harmony-font-size-body-s);
  color: var(--harmony-font-secondary);
  line-height: 1.4;
}

.dark .drawer-hint {
  color: rgb(156, 163, 175);
}

/* 头像上传样式 */
.logo-upload-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

.logo-preview {
  width: 120px;
  height: 120px;
  border: 2px dashed var(--harmony-comp-divider);
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  overflow: hidden;
  position: relative;
  transition: all 0.3s;
  background-color: var(--harmony-comp-background-primary);
}

.logo-preview:hover {
  border-color: var(--harmony-brand);
  background-color: var(--harmony-comp-emphasize-tertiary);
}

.dark .logo-preview {
  border-color: rgb(64, 64, 64);
  background-color: rgb(31, 31, 31);
}

.dark .logo-preview:hover {
  border-color: var(--harmony-brand);
  background-color: rgb(23, 37, 84);
}

.logo-preview.uploading {
  pointer-events: none;
  opacity: 0.6;
}

.logo-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.logo-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--harmony-font-tertiary);
}

.logo-overlay {
  position: absolute;
  inset: 0;
  background-color: var(--harmony-comp-background-secondary);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  opacity: 0;
  transition: opacity 0.3s;
  color: white;
}

.logo-preview:hover .logo-overlay {
  opacity: 1;
}

.logo-overlay span {
  font-size: var(--harmony-font-size-body-m);
  font-weight: 500;
}

.logo-loading {
  position: absolute;
  inset: 0;
  background-color: var(--harmony-comp-background-primary);
  display: flex;
  align-items: center;
  justify-content: center;
}

.dark .logo-loading {
  background-color: var(--harmony-font-primary);
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--harmony-comp-divider);
  border-top-color: var(--harmony-brand);
  border-radius: var(--harmony-corner-radius-level18);
  animation: h-spin 0.8s linear infinite;
}



.logo-hint {
  margin: 0;
  font-size: var(--harmony-font-size-body-s);
  color: var(--harmony-font-secondary);
  text-align: center;
}

.dark .logo-hint {
  color: rgb(156, 163, 175);
}

.drawer-field-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.drawer-field-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.drawer-input {
  display: block;
  height: 2.5rem;
  width: 100%;
  border-radius: 0.5rem;
  border: 1px solid var(--harmony-comp-divider);
  background-color: var(--harmony-comp-background-primary);
  padding: 0.5rem 0.875rem;
  font-size: var(--harmony-font-size-body-m);
  color: var(--harmony-font-primary);
  box-shadow: 0 1px 2px 0 var(--harmony-shadow-xs);
  transition: all 0.2s;
}

.drawer-input::placeholder {
  color: var(--harmony-font-tertiary);
}

.drawer-input:focus {
  border-color: var(--harmony-brand);
  box-shadow: 0 0 0 3px var(--harmony-comp-emphasize-tertiary);
}

.drawer-input:hover {
  border-color: var(--harmony-comp-divider);
}

.dark .drawer-input {
  border-color: rgb(64, 64, 64);
  background-color: rgb(23, 23, 23);
  color: rgb(229, 231, 235);
}

.dark .drawer-input:focus {
  border-color: var(--harmony-brand);
  box-shadow: 0 0 0 3px var(--harmony-comp-emphasize-tertiary);
}

.drawer-textarea {
  display: block;
  width: 100%;
  border-radius: 0.5rem;
  border: 1px solid var(--harmony-comp-divider);
  background-color: var(--harmony-comp-background-primary);
  padding: 0.75rem 0.875rem;
  font-size: var(--harmony-font-size-body-m);
  color: var(--harmony-font-primary);
  box-shadow: 0 1px 2px 0 var(--harmony-shadow-xs);
  transition: all 0.2s;
  resize: vertical;
  line-height: 1.5;
}

.drawer-textarea::placeholder {
  color: var(--harmony-font-tertiary);
}

.drawer-textarea:focus {
  border-color: var(--harmony-brand);
  box-shadow: 0 0 0 3px var(--harmony-comp-emphasize-tertiary);
}

.drawer-textarea:hover {
  border-color: var(--harmony-comp-divider);
}

.dark .drawer-textarea {
  border-color: rgb(64, 64, 64);
  background-color: rgb(23, 23, 23);
  color: rgb(229, 231, 235);
}

.dark .drawer-textarea:focus {
  border-color: var(--harmony-brand);
  box-shadow: 0 0 0 3px var(--harmony-comp-emphasize-tertiary);
}

.drawer-code-textarea {
  display: block;
  width: 100%;
  min-height: 13rem;
  border-radius: 0.5rem;
  border: 1px solid var(--harmony-comp-divider);
  background-color: var(--harmony-comp-background-primary);
  padding: 0.875rem;
  font-size: var(--harmony-font-size-body-s);
  color: var(--harmony-font-primary);
  font-family: var(--harmony-font-family);
  box-shadow: 0 1px 2px 0 var(--harmony-shadow-xs);
  transition: all 0.2s;
  resize: vertical;
  line-height: 1.6;
}

.drawer-code-textarea::placeholder {
  color: var(--harmony-font-tertiary);
}

.drawer-code-textarea:focus {
  border-color: var(--harmony-brand);
  box-shadow: 0 0 0 3px var(--harmony-comp-emphasize-tertiary);
}

.drawer-code-textarea:hover {
  border-color: var(--harmony-comp-divider);
}

.dark .drawer-code-textarea {
  border-color: rgb(64, 64, 64);
  background-color: rgb(23, 23, 23);
  color: rgb(229, 231, 235);
}

.dark .drawer-code-textarea:focus {
  border-color: var(--harmony-brand);
  box-shadow: 0 0 0 3px var(--harmony-comp-emphasize-tertiary);
}

.drawer-action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  white-space: nowrap;
  border-radius: 0.375rem;
  font-size: var(--harmony-font-size-body-s);
  font-weight: 500;
  border: 1px solid var(--harmony-comp-divider);
  background-color: var(--harmony-comp-background-primary);
  box-shadow: 0 1px 2px 0 var(--harmony-shadow-xs);
  height: 2rem;
  padding: 0 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
  gap: 0.375rem;
  color: var(--harmony-font-primary);
}

.drawer-action-btn:hover {
  background-color: var(--harmony-comp-background-primary);
  border-color: var(--harmony-comp-divider);
}

.dark .drawer-action-btn {
  border-color: rgb(64, 64, 64);
  background-color: rgb(40, 40, 40);
  color: rgb(229, 231, 235);
}

.dark .drawer-action-btn:hover {
  background-color: rgb(50, 50, 50);
}

.drawer-select {
  display: block;
  width: 100%;
  height: 2.5rem;
  border-radius: 0.5rem;
  border: 1px solid var(--harmony-comp-divider);
  background-color: var(--harmony-comp-background-primary);
  padding: 0 0.875rem;
  font-size: var(--harmony-font-size-body-m);
  box-shadow: 0 1px 2px 0 var(--harmony-shadow-xs);
  cursor: pointer;
  transition: all 0.2s;
  color: var(--harmony-font-primary);
}

.drawer-select:focus {
  border-color: var(--harmony-brand);
  box-shadow: 0 0 0 3px var(--harmony-comp-emphasize-tertiary);
}

.drawer-select:hover {
  border-color: var(--harmony-comp-divider);
}

.dark .drawer-select {
  border-color: rgb(64, 64, 64);
  background-color: rgb(23, 23, 23);
  color: rgb(229, 231, 235);
}

.dark .drawer-select:focus {
  border-color: var(--harmony-brand);
  box-shadow: 0 0 0 3px var(--harmony-comp-emphasize-tertiary);
}

.drawer-select-small {
  display: block;
  height: 2rem;
  border-radius: 0.375rem;
  border: 1px solid var(--harmony-comp-divider);
  background-color: var(--harmony-comp-background-primary);
  padding: 0 0.75rem;
  font-size: var(--harmony-font-size-body-s);
  box-shadow: 0 1px 2px 0 var(--harmony-shadow-xs);
  cursor: pointer;
  transition: all 0.2s;
  color: var(--harmony-font-primary);
}

.drawer-select-small:focus {
  border-color: var(--harmony-brand);
}

.drawer-select-small:hover {
  border-color: var(--harmony-comp-divider);
}

.dark .drawer-select-small {
  border-color: rgb(64, 64, 64);
  background-color: rgb(40, 40, 40);
  color: rgb(229, 231, 235);
}

.drawer-table-wrapper {
  width: 100%;
  overflow: auto;
  position: relative;
  border: 1px solid var(--harmony-comp-divider);
  border-radius: 0.5rem;
  background-color: var(--harmony-comp-background-primary);
}

.dark .drawer-table-wrapper {
  border-color: rgb(64, 64, 64);
  background-color: rgb(23, 23, 23);
}

.drawer-table {
  width: 100%;
  caption-side: bottom;
  font-size: var(--harmony-font-size-body-s);
  border-collapse: collapse;
}

.drawer-table-header tr {
  background-color: var(--harmony-comp-background-primary);
  border-bottom: 1px solid var(--harmony-comp-divider);
}

.dark .drawer-table-header tr {
  background-color: rgb(31, 31, 31);
  border-bottom-color: rgb(64, 64, 64);
}

.drawer-table-header th {
  height: 2.5rem;
  padding: 0.75rem 1rem;
  text-align: left;
  font-weight: 600;
  color: var(--harmony-font-primary);
  font-size: var(--harmony-font-size-body-s);
}

.dark .drawer-table-header th {
  color: rgb(209, 213, 219);
}

.drawer-table-body {
}

.drawer-table-row {
  transition: background-color 0.2s;
  border-bottom: 1px solid var(--harmony-comp-divider);
}

.dark .drawer-table-row {
  border-bottom-color: rgb(50, 50, 50);
}

.drawer-table-row:last-child {
  border-bottom: none;
}

.drawer-table-row:hover .drawer-table-cell {
  background-color: var(--harmony-comp-background-primary);
}

.dark .drawer-table-row:hover .drawer-table-cell {
  background-color: rgb(31, 31, 31);
}

.drawer-table-cell {
  padding: 0.875rem 1rem;
  background-color: var(--harmony-comp-background-primary);
  color: var(--harmony-font-primary);
}

.dark .drawer-table-cell {
  background-color: rgb(23, 23, 23);
  color: rgb(209, 213, 219);
}

.drawer-table-empty {
  padding: 2rem 1rem;
  background-color: var(--harmony-comp-background-primary);
  text-align: center;
  color: var(--harmony-font-tertiary);
  font-size: var(--harmony-font-size-body-m);
}

.dark .drawer-table-empty {
  background-color: rgb(23, 23, 23);
  color: rgb(115, 115, 115);
}

.drawer-table-path {
  font-family: var(--harmony-font-family);
  font-size: var(--harmony-font-size-body-s);
  color: var(--harmony-font-secondary);
}

.dark .drawer-table-path {
  color: rgb(156, 163, 175);
}

.drawer-badge {
  display: inline-block;
  padding: 0.25rem 0.625rem;
  font-size: var(--harmony-font-size-body-s);
  font-weight: 600;
  border-radius: 0.375rem;
  background-color: var(--harmony-comp-emphasize-tertiary);
  color: var(--harmony-brand);
  letter-spacing: 0.025em;
}

.drawer-footer {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  width: 100%;
  padding: 1.5rem;
  border-top: 1px solid var(--harmony-comp-divider);
  background-color: var(--harmony-comp-background-primary);
  display: flex;
  justify-content: center;
  align-items: center;
}

.dark .drawer-footer {
  border-top-color: rgb(38, 38, 38);
  background-color: rgb(3, 7, 18);
}

.drawer-footer-buttons {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.drawer-footer-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  white-space: nowrap;
  font-weight: 500;
  height: 2.5rem;
  border-radius: 0.5rem;
  padding: 0 2rem;
  font-size: var(--harmony-font-size-body-m);
  cursor: pointer;
  transition: all 0.2s;
  min-width: 100px;
}

.drawer-footer-button-cancel {
  border: 1px solid var(--harmony-comp-divider);
  background-color: var(--harmony-comp-background-primary);
  box-shadow: 0 1px 2px 0 var(--harmony-shadow-xs);
  color: var(--harmony-font-primary);
}

.drawer-footer-button-cancel:hover {
  background-color: var(--harmony-comp-background-primary);
  border-color: var(--harmony-comp-divider);
}

.dark .drawer-footer-button-cancel {
  border-color: rgb(64, 64, 64);
  background-color: rgb(40, 40, 40);
  color: rgb(229, 231, 235);
}

.dark .drawer-footer-button-cancel:hover {
  background-color: rgb(50, 50, 50);
}

.drawer-footer-button-save {
  border: none;
  background: var(--harmony-brand);
  box-shadow: 0 2px 8px var(--harmony-comp-emphasize-tertiary);
  color: var(--harmony-comp-background-primary);
}

.drawer-footer-button-save:hover {
  background: var(--harmony-brand);
  box-shadow: 0 4px 12px var(--harmony-comp-emphasize-tertiary);
  transform: translateY(-1px);
}

.drawer-close {
  position: absolute;
  right: 1.5rem;
  top: 1.75rem;
  border-radius: 0.375rem;
  opacity: 0.7;
  transition: all 0.2s;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0.375rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.drawer-close:hover {
  opacity: 1;
  background-color: var(--harmony-comp-background-primary);
}

.dark .drawer-close:hover {
  background-color: rgb(38, 38, 38);
}

.drawer-close:focus {
  box-shadow: 0 0 0 2px var(--harmony-brand);
}

.drawer-close-icon {
  width: 1.125rem;
  height: 1.125rem;
  color: var(--harmony-font-secondary);
}

.dark .drawer-close-icon {
  color: rgb(156, 163, 175);
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}

/* 删除确认弹窗样式 */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .delete-modal,
.modal-leave-active .delete-modal {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.modal-enter-from .delete-modal {
  transform: scale(0.9) translateY(-20px);
  opacity: 0;
}

.modal-leave-to .delete-modal {
  transform: scale(0.9) translateY(-20px);
  opacity: 0;
}

.delete-modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 10000;
  background-color: var(--harmony-comp-background-secondary);
  /* removed backdrop-filter */
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.delete-modal {
  background: var(--harmony-comp-background-primary);
  border-radius: var(--harmony-corner-radius-level8);
  box-shadow: 0 8px 24px rgba(0,0,0,0.15);
  max-width: 420px;
  width: 100%;
  padding: 32px;
  text-align: center;
  position: relative;
}

.dark .delete-modal {
  background: rgb(23, 23, 23);
  border: 1px solid rgb(64, 64, 64);
}

.delete-modal-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--harmony-warning-bg) 0%, var(--harmony-warning-bg) 100%);
  border-radius: var(--harmony-corner-radius-level18);
  color: var(--harmony-warning);
  
  svg {
    width: 48px;
    height: 48px;
  }
}

.delete-modal-title {
  font-size: var(--harmony-font-size-title-s);
  font-weight: 700;
  color: var(--harmony-font-primary);
  margin: 0 0 16px;
  letter-spacing: -0.3px;
}

.dark .delete-modal-title {
  color: rgb(243, 244, 246);
}

.delete-modal-content {
  font-size: var(--harmony-font-size-body-l);
  color: var(--harmony-font-secondary);
  line-height: 1.6;
  margin: 0 0 28px;
  
  strong {
    color: var(--harmony-font-primary);
    font-weight: 600;
  }
  
  .delete-modal-warning {
    display: block;
    margin-top: 8px;
    font-size: var(--harmony-font-size-subtitle-s);
    color: var(--harmony-warning);
    font-weight: 500;
  }
}

.dark .delete-modal-content {
  color: rgb(209, 213, 219);
  
  strong {
    color: rgb(243, 244, 246);
  }
}

.delete-modal-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.delete-modal-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  white-space: nowrap;
  font-weight: 600;
  height: 44px;
  border-radius: var(--harmony-corner-radius-level6);
  padding: 0 24px;
  font-size: var(--harmony-font-size-body-l);
  cursor: pointer;
  transition: all 0.2s;
  min-width: 120px;
  border: none;
}

.delete-modal-button-cancel {
  background-color: var(--harmony-comp-background-primary);
  color: var(--harmony-font-primary);
  border: 1px solid var(--harmony-comp-divider);
}

.delete-modal-button-cancel:hover {
  background-color: var(--harmony-comp-divider);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px var(--harmony-shadow-md);
}

.dark .delete-modal-button-cancel {
  background-color: rgb(40, 40, 40);
  color: rgb(229, 231, 235);
  border-color: rgb(64, 64, 64);
}

.dark .delete-modal-button-cancel:hover {
  background-color: rgb(50, 50, 50);
}

.delete-modal-button-confirm {
  background: var(--harmony-warning);
  color: var(--harmony-comp-background-primary);
  box-shadow: 0 2px 8px rgba(0,0,0,0.12);
}

.delete-modal-button-confirm:hover {
  background: var(--harmony-warning);
  box-shadow: 0 3px 12px rgba(0,0,0,0.15);
  transform: translateY(-1px);
}

.delete-modal-button-confirm:active {
  transform: translateY(0);
}

/* ==================== MOBILE: hmos mobile-list ==================== */
.tool-mobile {
  display: flex;
  flex-direction: column;
  gap: var(--harmony-section-gap-mobile, 16px);
  padding-top: var(--harmony-padding-level8, 16px);
}

.tm-header {
  display: flex;
  justify-content: flex-end;
}

.tm-create-btn {
  height: var(--harmony-control-height-40, 40px);
  padding: 0 var(--harmony-padding-level8, 16px);
  background: var(--harmony-brand);
  color: white;
  border: none;
  border-radius: var(--harmony-corner-radius-level6, 12px);
  font-size: var(--harmony-font-size-body-m);
  font-weight: 500;
  cursor: pointer;
}

.tm-list {
  display: flex;
  flex-direction: column;
  gap: var(--harmony-card-gap-mobile, 12px);
}

.tm-item {
  display: flex;
  align-items: center;
  gap: var(--harmony-padding-level6, 12px);
  padding: var(--harmony-padding-level6, 12px);
  background: var(--harmony-comp-background-primary);
  border: 1px solid var(--harmony-comp-divider);
  border-radius: var(--harmony-corner-radius-level8, 16px);
  transition: background 0.15s ease;

  &__icon {
    width: var(--harmony-control-height-40, 40px);
    height: var(--harmony-control-height-40, 40px);
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--harmony-comp-background-secondary);
    border-radius: var(--harmony-corner-radius-level6, 12px);
    flex-shrink: 0;
    font-size: 20px;
    overflow: hidden;
  }

  &__content {
    flex: 1;
    min-width: 0;
  }

  &__name {
    font-size: var(--harmony-font-size-body-m);
    font-weight: 600;
    color: var(--harmony-font-primary);
    margin: 0 0 var(--harmony-padding-level1, 2px) 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    display: flex;
    align-items: center;
    gap: 6px;
  }

  &__desc {
    font-size: var(--harmony-font-size-body-s);
    color: var(--harmony-font-secondary);
    margin: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  &__actions {
    display: flex;
    gap: var(--harmony-padding-level2, 4px);
    flex-shrink: 0;
  }
}

.tm-official-tag {
  font-size: var(--harmony-font-size-caption-l, 11px);
  padding: 1px 6px;
  background: var(--harmony-comp-emphasize-tertiary);
  color: var(--harmony-brand);
  border-radius: var(--harmony-corner-radius-level4, 8px);
  font-weight: 600;
  flex-shrink: 0;
}

.tm-action {
  width: var(--harmony-control-height-36, 36px);
  height: var(--harmony-control-height-36, 36px);
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--harmony-comp-background-secondary);
  border: none;
  border-radius: var(--harmony-corner-radius-level4, 8px);
  cursor: pointer;
  font-size: 16px;
  &:active { background: var(--harmony-interactive-pressed); }
  &--danger:active { background: rgba(232, 64, 38, 0.1); }
}

.tm-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
  p { font-size: var(--harmony-font-size-body-m); color: var(--harmony-font-tertiary); margin: 0; }
}
</style>
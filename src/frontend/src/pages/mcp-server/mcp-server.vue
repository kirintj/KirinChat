<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, reactive, inject } from 'vue'
import { HButton, HTag, HMessage } from '@/components/ui'
import * as monaco from 'monaco-editor'
import mcpIcon from '../../assets/mcp.svg'
import { 
  createMCPServerAPI, 
  getMCPServersAPI, 
  deleteMCPServerAPI, 
  updateMCPServerAPI,
  updateMCPUserConfigAPI,
  getDefaultMCPLogoAPI,
  type MCPServer, 
  type CreateMCPServerRequest, 
  type UpdateMCPServerRequest,
  type MCPServerTool,
  type MCPUserConfigUpdateRequest
} from '../../apis/mcp-server'

const isMobile = inject<import('vue').Ref<boolean>>('isMobile', ref(false))

const servers = ref<MCPServer[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const toolsDialogVisible = ref(false)
const configDialogVisible = ref(false)
const deleteDialogVisible = ref(false)
const formLoading = ref(false)
const editingServer = ref<MCPServer | null>(null)
const configuringServer = ref<MCPServer | null>(null)
const deletingServer = ref<MCPServer | null>(null)
const selectedServerTools = ref<MCPServerTool[]>([])
const selectedServerName = ref('')
const expandedToolIndex = ref<number | null>(null) // 当前展开的工具索引
let jsonEditor: monaco.editor.IStandaloneCodeEditor | null = null

// 配置状态
const configStatus = reactive({
  valid: true,
  message: '',
})

// 示例配置JSON
const exampleConfig = `{
  "mcpServers": {
    "amap-maps": {
      "type": "sse",
      "url": "Your_URL",
      "headers": {
        "Authorization": "Bearer Your_Token"
      }
    }
  }
}`

// 表单数据
const formData = ref<CreateMCPServerRequest>({
  server_name: '',
  logo_url: '',
  imported_config: {}
})

// 用于表单输入的字符串版本
const configString = ref('')

// Logo 上传相关
const uploadingLogo = ref(false)

const handleLogoUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isImage) {
    HMessage.error('只能上传图片文件作为 Logo')
    return
  }
  if (!isLt2M) {
    HMessage.error('图片大小不能超过 2MB')
    return
  }

  uploadingLogo.value = true
  try {
    const uploadFormData = new FormData()
    uploadFormData.append('file', file)
    const response = await fetch('/api/v1/upload', { method: 'POST', body: uploadFormData })
    const result = await response.json()
    const imageUrl = typeof result === 'string' ? result : result?.data
    if (imageUrl) {
      formData.value.logo_url = imageUrl
      HMessage.success('Logo 上传成功')
    } else {
      HMessage.error('上传失败，未获取到图片链接')
    }
  } catch (err) {
    console.error('Logo 上传失败:', err)
    HMessage.error('Logo 上传失败，请重试')
  } finally {
    uploadingLogo.value = false
    target.value = ''
  }
}

// 用户配置相关数据
const userConfigData = ref<string>('{}') // 仅保留配置数据，编辑时不预加载

// 表单验证
const formErrors = ref<Record<string, string>>({})

const validateForm = () => {
  formErrors.value = {}
  
  // 服务器名称为可选字段，仅在用户填写时做长度校验
  if (formData.value.server_name && formData.value.server_name.trim() !== '') {
    if (formData.value.server_name.length < 2 || formData.value.server_name.length > 50) {
      formErrors.value.server_name = '服务器名称长度在 2 到 50 个字符'
    }
  }
  
  // Logo为可选字段，不需要验证
  
  // 服务器配置验证：必须是有效的JSON格式才能提交
  if (configString.value && configString.value.trim() !== '') {
    // 验证JSON格式
    try {
      const parsed = JSON.parse(configString.value.trim())
      // 验证通过
    } catch (error) {
      formErrors.value.imported_config = '配置信息格式不正确，请输入有效的JSON格式'
    }
  } else if (!editingServer.value) {
    // 仅创建模式下配置为必填
    formErrors.value.imported_config = '请输入服务器配置'
  }
  
  return Object.keys(formErrors.value).length === 0
}

const fetchServers = async () => {
  loading.value = true
  try {
    const response = await getMCPServersAPI()
    
    if (response?.data?.status_code === 200) {
      const serverList = response.data.data || []
      // 排序：官方服务器（user_id = 0）在前，其他服务器在后
      servers.value = serverList.sort((a: MCPServer, b: MCPServer) => {
        const aIsOfficial = String(a.user_id) === '0'
        const bIsOfficial = String(b.user_id) === '0'
        
        // 如果一个是官方，一个不是，官方的排在前面
        if (aIsOfficial && !bIsOfficial) return -1
        if (!aIsOfficial && bIsOfficial) return 1
        
        // 如果都是官方或都不是官方，按创建时间排序（新的在前）
        return new Date(b.create_time).getTime() - new Date(a.create_time).getTime()
      })
    } else {
      HMessage.error(response?.data?.status_message || '获取MCP服务器列表失败')
      servers.value = []
    }
  } catch (error) {
    console.error('获取MCP服务器列表失败:', error)
    HMessage.error('网络错误：无法获取MCP服务器列表')
    servers.value = []
  } finally {
    loading.value = false
  }
}

const handleCreate = async () => {
  editingServer.value = null
  dialogVisible.value = true
  formErrors.value = {}
  // 阻止背景滚动
  document.body.style.overflow = 'hidden'
  // 重置表单
  formData.value = {
    server_name: '',
    logo_url: '',
    imported_config: {}
  }
  configString.value = ''
  
  // 获取默认logo
  try {
    const response = await getDefaultMCPLogoAPI()
    if (response.data.status_code === 200) {
      formData.value.logo_url = response.data.data.logo_url
    }
  } catch (error) {
    console.error('获取默认logo失败:', error)
  }
}

const handleEdit = (server: MCPServer) => {
  // 检查是否为官方服务器
  if (String(server.user_id) === '0') {
    HMessage.warning(`${server.server_name} MCP Server 为官方所有，不能编辑`)
    return
  }
  
  editingServer.value = server
  dialogVisible.value = true
  formErrors.value = {}
  // 阻止背景滚动
  document.body.style.overflow = 'hidden'
  
  // 填充服务器信息到表单，包括配置
  formData.value = {
    server_name: server.server_name,
    logo_url: server.logo_url || '',
    imported_config: {}
  }
  
  // 直接使用服务器的imported_config
  if (server.imported_config) {
    configString.value = JSON.stringify(server.imported_config, null, 2)
  } else {
    // 如果没有imported_config，使用url和type重构（兼容旧数据）
    const importedConfig = {
      mcpServers: {
        [server.server_name]: {
          type: server.type,
          url: server.url
        }
      }
    }
    configString.value = JSON.stringify(importedConfig, null, 2)
  }
}

const closeDialog = () => {
  dialogVisible.value = false
  editingServer.value = null
  formErrors.value = {}
  userConfigData.value = '[]'
  // 恢复背景滚动
  document.body.style.overflow = 'auto'
}

// 移除加载用户配置的函数，编辑时直接使用服务器信息

const handleSubmit = async () => {
  if (!validateForm()) {
    return
  }
  
  formLoading.value = true
  try {
    if (editingServer.value) {
      // 编辑模式：更新服务器信息（包括配置）
      // 处理配置字段：解析JSON
      let configData = undefined
      if (configString.value && configString.value.trim() !== '') {
        try {
          const parsed = JSON.parse(configString.value.trim())
          configData = parsed
        } catch (error) {
          formErrors.value.imported_config = '配置信息格式不正确，请输入有效的JSON格式'
          formLoading.value = false
          return
        }
      }
      
      const updateData: UpdateMCPServerRequest = {
        server_id: editingServer.value.mcp_server_id,
        name: formData.value.server_name,
        logo_url: formData.value.logo_url,
        imported_config: configData
      }
      
      const response = await updateMCPServerAPI(updateData)
      if (response.data.status_code === 200) {
        HMessage.success('更新MCP服务器成功')
        closeDialog()
        await fetchServers()
      } else {
        HMessage.error(response.data.status_message || '更新失败')
      }
    } else {
      // 创建模式：创建服务器
      // 处理配置字段：解析JSON，如果用户清空了，使用空对象 {}
      let configData = {}
      if (configString.value && configString.value.trim() !== '') {
        try {
          const parsed = JSON.parse(configString.value.trim())
          configData = parsed
        } catch (error) {
          formErrors.value.imported_config = '配置信息格式不正确，请输入有效的JSON格式'
          formLoading.value = false
          return
        }
      } else {
        // 如果为空或未填写，使用空对象
        configData = {}
      }
      
      const submitData = {
        server_name: formData.value.server_name,
        logo_url: formData.value.logo_url,
        imported_config: configData
      }
      
      const response = await createMCPServerAPI(submitData)
      if (response.data.status_code === 200) {
        HMessage.success('创建MCP服务器成功')
        closeDialog()
        await fetchServers()
      } else {
        HMessage.error(response.data.status_message || '创建失败')
      }
    }
  } catch (error) {
    console.error('操作失败:', error)
    HMessage.error('操作失败')
  } finally {
    formLoading.value = false
  }
}

// 更新用户配置
const updateUserConfig = async () => {
  if (!editingServer.value) return
  
  try {
    // 获取编辑器的最新内容
    const jsonContent = jsonEditor ? jsonEditor.getValue() : userConfigData.value
    
    // 解析用户配置JSON
    let parsedUserConfig = {}
    try {
      parsedUserConfig = JSON.parse(jsonContent.trim() || '[]')
    } catch (error) {
      HMessage.error('用户配置JSON格式错误')
      return
    }

    // 直接调用更新接口（后端会自动判断是创建还是更新）
    const serverId = editingServer.value?.mcp_server_id || configuringServer.value?.mcp_server_id
    if (!serverId) {
      HMessage.error('服务器ID不存在')
      return
    }
    
    const response = await updateMCPUserConfigAPI({
      server_id: serverId,
      config: parsedUserConfig
    })
    
    if (response.data.status_code === 200) {
      HMessage.success('用户配置保存成功')
    } else {
      HMessage.error(response.data.status_message || '保存失败')
      return
    }
    
    closeConfigDialog()
    await fetchServers()
  } catch (error: any) {
    console.error('保存用户配置失败:', error)
    throw error
  }
}

const handleDelete = async (server: MCPServer) => {
  // 检查是否为官方服务器
  if (String(server.user_id) === '0') {
    HMessage.warning(`${server.server_name} MCP Server 为官方所有，不能删除`)
    return
  }
  
  // 显示自定义删除确认对话框
  deletingServer.value = server
  deleteDialogVisible.value = true
  // 阻止背景滚动
  document.body.style.overflow = 'hidden'
}

const closeDeleteDialog = () => {
  deleteDialogVisible.value = false
  deletingServer.value = null
  // 恢复背景滚动
  document.body.style.overflow = 'auto'
}

const confirmDelete = async () => {
  if (!deletingServer.value) return
  
  formLoading.value = true
  try {
    const response = await deleteMCPServerAPI(deletingServer.value.mcp_server_id)
    if (response.data.status_code === 200) {
      HMessage.success('删除成功')
      closeDeleteDialog()
      await fetchServers() // 刷新列表
    } else {
      HMessage.error(response.data.status_message || '删除失败')
    }
  } catch (error) {
    console.error('删除MCP服务器失败:', error)
    HMessage.error('删除失败')
  } finally {
    formLoading.value = false
  }
}

// 查看工具详情
const viewTools = (server: MCPServer) => {
  selectedServerTools.value = server.params || []
  selectedServerName.value = server.server_name
  toolsDialogVisible.value = true
  // 阻止背景滚动
  document.body.style.overflow = 'hidden'
}

const closeToolsDialog = () => {
  toolsDialogVisible.value = false
  expandedToolIndex.value = null // 重置展开状态
  // 恢复背景滚动
  document.body.style.overflow = 'auto'
}

// 切换工具详情展开/收起
const toggleToolDetail = (index: number) => {
  if (expandedToolIndex.value === index) {
    expandedToolIndex.value = null
  } else {
    expandedToolIndex.value = index
  }
}

// 处理个人配置
const handleConfig = (server: MCPServer) => {
  configuringServer.value = server
  configDialogVisible.value = true
  // 阻止背景滚动
  document.body.style.overflow = 'hidden'
  
  // 初始化用户配置数据，使用服务器的config字段作为基础
  userConfigData.value = typeof server.config === 'object' 
    ? JSON.stringify(server.config, null, 2) 
    : server.config || '[]'
    
  // 初始化JSON编辑器
  nextTick(() => {
    initJsonEditor()
  })
}

// 初始化Monaco编辑器
const initJsonEditor = () => {
  const editorContainer = document.getElementById('jsonEditor')
  if (editorContainer && !jsonEditor) {
    // 注册JSON语言
    monaco.languages.json.jsonDefaults.setDiagnosticsOptions({
      validate: true,
      schemas: [{
        uri: 'http://myserver/mcp-config-schema.json',
        fileMatch: ['*'],
        schema: {
          type: 'array',
          items: {
            type: 'object',
            required: ['key', 'label', 'value'],
            properties: {
              key: {
                type: 'string',
                description: '配置项的唯一标识符'
              },
              label: {
                type: 'string',
                description: '配置项的显示名称'
              },
              value: {
                description: '配置项的值'
              }
            }
          }
        }
      }]
    })
    
    // 创建编辑器
    jsonEditor = monaco.editor.create(editorContainer, {
      value: userConfigData.value,
      language: 'json',
      theme: 'vs',
      automaticLayout: true,
      minimap: { enabled: false },
      lineNumbers: 'on',
      roundedSelection: true,
      scrollBeyondLastLine: false,
      fontSize: 14,
      tabSize: 2,
      renderLineHighlight: 'all',
      scrollbar: {
        vertical: 'auto',
        horizontal: 'auto',
      }
    })
    
    // 添加编辑器验证
    jsonEditor.onDidChangeModelContent(() => {
      validateJsonConfig()
    })
    
    // 初始验证
    validateJsonConfig()
  }
}

// 验证JSON配置
const validateJsonConfig = () => {
  if (!jsonEditor) return
  
  const content = jsonEditor.getValue()
  configStatus.valid = true
  configStatus.message = ''
  
  try {
    const parsed = JSON.parse(content)
    if (!Array.isArray(parsed)) {
      configStatus.valid = false
      configStatus.message = '配置必须是JSON数组格式'
      return
    }
    
    // 验证每个项目结构
    for (let i = 0; i < parsed.length; i++) {
      const item = parsed[i]
      if (!item.key || !item.label || item.value === undefined) {
        configStatus.valid = false
        configStatus.message = `第${i+1}项缺少必要字段，请确保包含key、label和value`
        return
      }
    }
  } catch (e) {
    configStatus.valid = false
    configStatus.message = '无效的JSON格式'
  }
}

const closeConfigDialog = () => {
  configDialogVisible.value = false
  configuringServer.value = null
  
  // 销毁编辑器
  if (jsonEditor) {
    jsonEditor.dispose()
    jsonEditor = null
  }
  
  // 恢复背景滚动
  document.body.style.overflow = 'auto'
}

// 更新个人配置
const handleConfigSubmit = async () => {
  if (!configuringServer.value) {
    HMessage.error('服务器信息缺失，请重试')
    return
  }
  
  // 检查JSON是否有效
  if (!configStatus.valid) {
    HMessage.error(configStatus.message || 'JSON格式无效')
    return
  }
  
  formLoading.value = true
  try {
    // 获取编辑器的最新内容
    const jsonContent = jsonEditor ? jsonEditor.getValue() : userConfigData.value
    
    // 解析用户配置JSON
    let parsedUserConfig = {}
    try {
      parsedUserConfig = JSON.parse(jsonContent.trim() || '[]')
    } catch (error) {
      HMessage.error('用户配置JSON格式错误: ' + (error as Error).message)
      formLoading.value = false
      return
    }

    // 准备请求参数
    const requestData: MCPUserConfigUpdateRequest = {
      server_id: configuringServer.value.mcp_server_id,
      config: parsedUserConfig
    }

    console.log('准备发送配置更新请求:', requestData)
    
    // 调用API更新配置
    const response = await updateMCPUserConfigAPI(requestData)
    console.log('配置更新响应:', response)
    
    if (response.data.status_code === 200) {
      HMessage.success('个人配置更新成功')
      closeConfigDialog()
      await fetchServers()
    } else {
      HMessage.error(response.data.status_message || '保存失败')
    }
  } catch (error) {
    console.error('配置更新失败:', error)
    HMessage.error('配置更新失败: ' + (error as Error).message)
  } finally {
    formLoading.value = false
  }
}

// 插入示例配置
const insertExampleConfig = () => {
  if (!jsonEditor) return
  
  const exampleConfig = [
    {
      "key": "api_key",
      "label": "API密钥",
      "value": "your_api_key_here"
    },
    {
      "key": "timeout",
      "label": "超时时间(毫秒)",
      "value": 30000
    },
    {
      "key": "model",
      "label": "模型名称",
      "value": "gpt-4"
    }
  ]
  
  jsonEditor.setValue(JSON.stringify(exampleConfig, null, 2))
}

// 处理图片加载错误
const handleImageError = (event: Event) => {
  const target = event.target as HTMLImageElement
  if (target) {
    target.src = '/src/assets/robot.svg'
  }
}

onMounted(async () => {
  try {
    await fetchServers()
  } catch (error) {
    console.error('MCP Server 页面初始化失败:', error)
    HMessage.error('页面初始化失败，请刷新重试')
  }
})

onUnmounted(() => {
  // 页面卸载时恢复背景滚动，防止影响其他页面
  document.body.style.overflow = 'auto'
  
  // 销毁编辑器
  if (jsonEditor) {
    jsonEditor.dispose()
    jsonEditor = null
  }
})

// 保存用户配置
const saveUserConfig = async () => {
  if (!configuringServer.value || !jsonEditor) return
  
  try {
    // 更新用户配置
    const configContent = jsonEditor.getValue()
    
    // 验证JSON格式
    if (!configStatus.valid) {
      HMessage.error('配置格式错误，无法保存')
      return
    }
    
    // 准备请求数据
    const requestData: MCPUserConfigUpdateRequest = {
      mcp_server_id: configuringServer.value.mcp_server_id,
      user_config: configContent
    }
    
    // 发送请求
    // console.log('准备发送配置更新请求:', requestData)
    const response = await updateMCPUserConfigAPI(requestData)
    // console.log('配置更新响应:', response)
    
    if (response.data.status_code === 200) {
      HMessage.success('配置保存成功')
      configDialogVisible.value = false
      await fetchServers() // 刷新列表
    } else {
      HMessage.error(response.data.status_message || '保存配置失败')
    }
  } catch (error) {
    console.error('保存MCP用户配置失败:', error)
    HMessage.error('保存失败')
  }
}
</script>

<template>
  <div class="mcp-server-page">
    <div v-if="!isMobile" class="page-header">
      <div class="header-title">
        <h2>MCP Server管理</h2>
      </div>
      <div class="header-actions">
        <HButton type="primary" @click="handleCreate">
          ➕ 添加服务器
        </HButton>
      </div>
    </div>

    <div v-if="!isMobile" class="server-list">
      <div v-if="servers.length > 0" class="server-table-wrapper">
        <table class="server-table">
          <thead>
            <tr>
              <th style="width:80px;text-align:center;">头像</th>
              <th style="min-width:150px;text-align:center;">服务器名称</th>
              <th style="width:110px;text-align:center;">创建用户</th>
              <th style="width:110px;text-align:center;">连接类型</th>
              <th style="width:140px;text-align:center;">可用工具</th>
              <th style="width:110px;text-align:center;">配置状态</th>
              <th style="min-width:180px;text-align:center;">创建时间</th>
              <th style="width:180px;text-align:center;">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in servers" :key="row.mcp_server_id">
              <td style="text-align:center;">
                <div class="server-avatar">
                  <img
                    :src="row.logo_url || '/src/assets/robot.svg'"
                    :alt="row.server_name"
                    @error="handleImageError"
                  />
                </div>
              </td>
              <td style="text-align:center;">
                <div class="server-name" :class="{ 'official-server': String(row.user_id) === '0' }">
                  <span class="name">{{ row.server_name }}</span>
                  <HTag v-if="String(row.user_id) === '0'" type="warning" class="official-tag">
                    官方
                  </HTag>
                </div>
              </td>
              <td style="text-align:center;">
                <div class="user-info">
                  <HTag type="default">{{ row.user_name }}</HTag>
                </div>
              </td>
              <td style="text-align:center;">
                <HTag :type="row.type === 'sse' ? 'primary' : 'success'">
                  {{ row.type.toUpperCase() }}
                </HTag>
              </td>
              <td style="text-align:center;">
                <div class="tools-count">
                  <HButton
                    type="primary"
                    size="small"
                    @click="viewTools(row)"
                    :disabled="!row.params || row.params.length === 0"
                    style="border-radius:20px;"
                  >
                    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" style="vertical-align:-2px;margin-right:4px;">
                      <rect x="1.5" y="2.5" width="11" height="9" rx="1.5" stroke="currentColor" stroke-width="1.2"/>
                      <circle cx="7" cy="7" r="2" stroke="currentColor" stroke-width="1.1"/>
                      <line x1="1.5" y1="5.5" x2="12.5" y2="5.5" stroke="currentColor" stroke-width="1.1"/>
                    </svg>
                    {{ row.params?.length || 0 }} 个工具
                  </HButton>
                </div>
              </td>
              <td style="text-align:center;">
                <div class="config-status">
                  <HTag
                    :type="row.config_enabled ? 'warning' : 'success'"
                    :class="{ 'clickable-tag': row.config_enabled }"
                    @click="row.config_enabled ? handleConfig(row) : null"
                    :title="row.config_enabled ? '点击配置个人参数' : '配置已完成'"
                    style="cursor:pointer;"
                  >
                    {{ row.config_enabled ? '需配置' : '已就绪' }}
                  </HTag>
                </div>
              </td>
              <td style="text-align:center;">
                <div class="create-time">
                  <span>{{ new Date(row.create_time).toLocaleString() }}</span>
                </div>
              </td>
              <td style="text-align:center;">
                <div class="action-buttons">
                  <HButton
                    v-if="String(row.user_id) !== '0'"
                    size="small"
                    type="primary"
                    @click="handleEdit(row)"
                    title="编辑"
                  >
                    ✏️ 编辑
                  </HButton>
                  <HButton
                    v-else
                    size="small"
                    type="secondary"
                    disabled
                    :title="`${row.server_name} MCP Server 为官方所有，不能编辑`"
                  >
                    ✏️ 编辑
                  </HButton>

                  <HButton
                    v-if="String(row.user_id) !== '0'"
                    size="small"
                    type="danger"
                    @click="handleDelete(row)"
                    title="删除"
                  >
                    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" style="vertical-align:-2px;margin-right:4px;">
                      <path d="M2 4H12L10.5 12H3.5L2 4Z" stroke="currentColor" stroke-width="1.2"/>
                      <line x1="5" y1="4" x2="5" y2="2" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
                      <line x1="9" y1="4" x2="9" y2="2" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
                    </svg>
                    删除
                  </HButton>
                  <HButton
                    v-else
                    size="small"
                    type="secondary"
                    disabled
                    :title="`${row.server_name} MCP Server 为官方所有，不能删除`"
                  >
                    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" style="vertical-align:-2px;margin-right:4px;">
                      <path d="M2 4H12L10.5 12H3.5L2 4Z" stroke="currentColor" stroke-width="1.2"/>
                      <line x1="5" y1="4" x2="5" y2="2" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
                      <line x1="9" y1="4" x2="9" y2="2" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
                    </svg>
                    删除
                  </HButton>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="servers.length === 0 && !loading" class="empty-state">
        <div class="empty-icon">
          <i class="empty-icon-symbol">📡</i>
        </div>
        <h3>暂无MCP服务</h3>
        <p>添加MCP服务器以增强智能体的能力</p>
        <HButton type="primary" @click="handleCreate()" class="create-btn">
          ➕ 添加服务器
        </HButton>
      </div>
    </div>

    <!-- Mobile: hmos mobile-list -->
    <div v-else class="mcp-mobile">
      <div class="mcpm-header">
        <button class="mcpm-create-btn" @click="handleCreate">+ 添加服务</button>
      </div>

      <div class="mcpm-list" v-if="servers.length > 0">
        <div v-for="server in servers" :key="server.mcp_server_id" class="mcpm-item">
          <div class="mcpm-item__icon">
            <img
              :src="server.logo_url || '/src/assets/robot.svg'"
              :alt="server.server_name"
              @error="handleImageError"
              class="mcpm-item__img"
            />
          </div>
          <div class="mcpm-item__content">
            <h3 class="mcpm-item__name">
              {{ server.server_name }}
              <span v-if="String(server.user_id) === '0'" class="mcpm-official-tag">官方</span>
            </h3>
            <p class="mcpm-item__url">{{ server.type?.toUpperCase() }} | {{ server.user_name }}</p>
          </div>
          <div class="mcpm-item__status">
            <span :class="['mcpm-status', server.config_enabled ? 'inactive' : 'active']">
              {{ server.config_enabled ? '需配置' : '已就绪' }}
            </span>
          </div>
          <div class="mcpm-item__actions">
            <button
              v-if="String(server.user_id) !== '0'"
              class="mcpm-action"
              @click="handleEdit(server)"
              title="编辑"
            >&#9998;</button>
            <button
              v-if="String(server.user_id) !== '0'"
              class="mcpm-action mcpm-action--danger"
              @click="handleDelete(server)"
              title="删除"
            >&#128465;</button>
          </div>
        </div>
      </div>

      <div v-else-if="!loading" class="mcpm-empty"><p>暂无MCP服务</p></div>
    </div>

    <!-- 纯HTML创建/编辑弹窗 -->
    <Teleport to="body">
      <div v-if="dialogVisible" class="modal-overlay" @click.self="closeDialog">
        <div class="modal-dialog">
          <div class="modal-header">
            <h3>{{ editingServer ? '编辑MCP服务器' : '创建MCP服务器' }}</h3>
            <button class="close-btn" @click="closeDialog">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>
          
          <div class="modal-body">
            <!-- 服务器配置向导 -->
            <div class="config-wizard">
              <div class="wizard-header">
                <div class="wizard-icon">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2L2 7V17L12 22L22 17V7L12 2Z" stroke="#409eff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M12 12L2 7L12 2L22 7L12 12Z" stroke="#409eff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </div>
                <div class="wizard-text">
                  <h4>{{ editingServer ? '更新服务器配置' : '配置新的MCP服务器' }}</h4>
                  <p>{{ editingServer ? '修改现有服务器的连接参数和配置' : '填写以下信息来添加新的MCP服务器' }}</p>
                </div>
              </div>

              <form @submit.prevent="handleSubmit" class="mcp-form">
                <!-- 统一表单区域 -->
                <div class="form-section">
                  <div class="form-layout">
                    <!-- 服务器名称 -->
                    <div class="form-group">
                      <label for="server_name">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path d="M12 2L2 7V17L12 22L22 17V7L12 2Z" stroke="currentColor" stroke-width="2"/>
                        </svg>
                        服务器名称
                      </label>
                      <input 
                        id="server_name"
                        v-model="formData.server_name" 
                        type="text"
                        placeholder="例如：Weather-Server"
                        :class="{ 'error': formErrors.server_name }"
                      />
                      <span v-if="formErrors.server_name" class="error-text">{{ formErrors.server_name }}</span>
                    </div>

                    <!-- Logo -->
                    <div class="form-group">
                      <label>
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path d="M4 4h16v16H4z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                          <path d="M4 15l4-4 4 4 4-5 4 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                        </svg>
                        Logo
                      </label>
                      <div class="logo-upload-square" @click="$refs.logoFileInput?.click()" style="cursor:pointer;">
                        <input ref="logoFileInput" type="file" accept="image/*" style="display:none;" @change="handleLogoUpload" />
                        <div v-if="formData.logo_url" class="logo-preview-square">
                          <img :src="formData.logo_url" alt="logo 预览" />
                          <div class="logo-overlay">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                              <path d="M12 5v14M5 12h14" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            </svg>
                          </div>
                        </div>
                        <div v-else class="logo-upload-placeholder" :class="{ 'uploading': uploadingLogo }">
                          <svg v-if="!uploadingLogo" width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M12 5v14M5 12h14" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
                          </svg>
                          <span v-else class="uploading-text">上传中...</span>
                        </div>
                      </div>
                      <span v-if="formErrors.logo_url" class="error-text">{{ formErrors.logo_url }}</span>
                    </div>

                    <!-- 服务配置 -->
                    <div class="form-group form-group-full">
                      <label for="imported_config">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                          <polyline points="14,2 14,8 20,8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                          <line x1="16" y1="13" x2="8" y2="13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                          <line x1="16" y1="17" x2="8" y2="17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                          <polyline points="10,9 9,9 8,9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                        服务配置 <span v-if="!editingServer" class="required-mark">*</span>
                      </label>
                      <div class="textarea-wrapper">
                        <textarea 
                          id="imported_config"
                          v-model="configString" 
                          rows="8"
                          :placeholder="exampleConfig"
                          :class="{ 'error': formErrors.imported_config }"
                        ></textarea>
                        <div class="json-indicator">
                          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M16 3l4 4-4 4" stroke="#909399" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M8 21l-4-4 4-4" stroke="#909399" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M15 14l-6-6" stroke="#909399" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                          </svg>
                          JSON
                        </div>
                      </div>
                      <span v-if="formErrors.imported_config" class="error-text">{{ formErrors.imported_config }}</span>
                      <span v-if="editingServer" class="help-text">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <circle cx="12" cy="12" r="10" stroke="#909399" stroke-width="2"/>
                          <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" stroke="#909399" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                          <line x1="12" y1="17" x2="12.01" y2="17" stroke="#909399" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                        编辑模式下，如果不修改配置可以保持原样，只修改需要更新的字段
                      </span>
                    </div>
                  </div>
                </div>
              </form>
            </div>
          </div>
          
          <div class="modal-footer">
            <button type="button" @click="closeDialog" class="btn btn-cancel">
              取消
            </button>
            <button 
              type="button" 
              @click="handleSubmit"
              :disabled="formLoading"
              class="btn btn-primary"
            >
              <span v-if="formLoading" class="loading-spinner"></span>
              {{ editingServer ? '保存修改' : '添加服务器' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 纯HTML工具详情弹窗 -->
    <Teleport to="body">
      <div v-if="toolsDialogVisible" class="modal-overlay" @click.self="closeToolsDialog">
        <div class="modal-dialog tools-dialog">
          <div class="modal-header">
            <h3>{{ selectedServerName }} - 可用工具</h3>
            <button class="close-btn" @click="closeToolsDialog">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>
          
          <div class="modal-body tools-content">
            <div v-if="selectedServerTools.length === 0" class="no-tools">
              <div class="empty-icon">
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.77 3.77z" stroke="#c0c4cc" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </div>
              <div class="empty-text">
                <h3>暂无可用工具</h3>
                <p>该服务器尚未提供任何工具，或者服务器连接异常</p>
              </div>
            </div>
            <div v-else class="tools-overview">
              <!-- 工具统计 -->
              <div class="tools-stats">
                <div class="stat-card">
                  <div class="stat-icon">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.77 3.77z" stroke="#409eff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                  </div>
                  <div class="stat-info">
                    <span class="stat-number">{{ selectedServerTools.length }}</span>
                    <span class="stat-label">可用工具</span>
                  </div>
                </div>
              </div>

              <!-- 工具列表 -->
              <div class="tools-list">
                <div 
                  v-for="(tool, index) in selectedServerTools" 
                  :key="index"
                  class="tool-item"
                  :class="{ 'expanded': expandedToolIndex === index }"
                  @click="toggleToolDetail(index)"
                >
                  <div class="tool-summary">
                    <div class="tool-info">
                      <div class="tool-icon">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.77 3.77z" stroke="#409eff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                      </div>
                      <div class="tool-text">
                        <h4 class="tool-name">{{ tool.name }}</h4>
                        <p class="tool-description">{{ tool.description || '暂无描述' }}</p>
                      </div>
                    </div>
                    <div class="tool-expand-icon">
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <polyline points="6 9 12 15 18 9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                      </svg>
                    </div>
                  </div>
                  
                  <!-- 展开的详细信息 -->
                  <transition name="expand">
                    <div v-if="expandedToolIndex === index" class="tool-details" @click.stop>
                      <div class="tool-schema" v-if="tool.input_schema">
                        <div class="schema-header">
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <polyline points="16 18 22 12 16 6" stroke="#409eff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            <polyline points="8 6 2 12 8 18" stroke="#409eff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                          </svg>
                          <span>参数结构</span>
                        </div>
                        
                        <div class="schema-content">
                          <div class="schema-meta">
                            <div class="meta-item" v-if="tool.input_schema.type">
                              <span class="meta-label">类型:</span>
                              <span class="meta-value type">{{ tool.input_schema.type }}</span>
                            </div>
                            <div class="meta-item" v-if="tool.input_schema.title">
                              <span class="meta-label">标题:</span>
                              <span class="meta-value">{{ tool.input_schema.title }}</span>
                            </div>
                          </div>
                          
                          <div v-if="tool.input_schema.required?.length" class="required-section">
                            <div class="section-title">
                              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" stroke="#f56c6c" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                                <path d="M9 12l2 2 4-4" stroke="#f56c6c" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                              </svg>
                              <span>必填参数</span>
                            </div>
                            <div class="required-params">
                              <span 
                                v-for="param in tool.input_schema.required" 
                                :key="param"
                                class="required-param"
                              >
                                {{ param }}
                              </span>
                            </div>
                          </div>
                          
                          <div v-if="tool.input_schema.properties" class="properties-section">
                            <div class="section-title">
                              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <rect x="3" y="3" width="18" height="18" rx="2" ry="2" stroke="#67c23a" stroke-width="2"/>
                                <circle cx="8.5" cy="8.5" r="1.5" stroke="#67c23a" stroke-width="2"/>
                                <path d="M21 15l-5-5L5 21l5-5z" stroke="#67c23a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                              </svg>
                              <span>参数详情</span>
                            </div>
                            <div class="properties-grid">
                              <div 
                                v-for="(prop, propName) in tool.input_schema.properties" 
                                :key="propName"
                                class="property-card"
                              >
                                <div class="property-header">
                                  <span class="property-name">{{ propName }}</span>
                                  <span class="property-type">{{ prop.type }}</span>
                                </div>
                                <div class="property-body">
                                  <p v-if="prop.description" class="property-desc">{{ prop.description }}</p>
                                  <div v-if="prop.default !== undefined" class="property-default">
                                    <span class="default-label">默认值:</span>
                                    <code class="default-value">{{ prop.default }}</code>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </transition>
                </div>
              </div>
            </div>
          </div>
          
          <div class="modal-footer">
            <button type="button" @click="closeToolsDialog" class="btn btn-primary">关闭</button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 个人配置弹窗 -->
    <Teleport to="body">
      <div v-if="configDialogVisible" class="modal-overlay" @click.self="closeConfigDialog">
        <div class="modal-dialog config-dialog">
          <div class="modal-header">
            <h3>
              <span class="config-server-name">{{ configuringServer?.server_name }}</span>
              <span class="config-title">个人配置</span>
            </h3>
            <button class="close-btn" @click="closeConfigDialog">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>
          
          <div class="modal-body">
            <!-- 配置指引卡片 -->
            <div class="config-info">
              <div class="info-card">
                <div class="info-icon">
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="12" cy="12" r="10" stroke="#409eff" stroke-width="2"/>
                    <path d="M9 12l2 2 4-4" stroke="#409eff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </div>
                <div class="info-text">
                  <h4>个人配置</h4>
                  <p>为此MCP服务配置您的个人参数，这些设置将仅对您的账户有效，不会影响其他用户。</p>
                </div>
              </div>
            </div>
            
            <!-- 顶部工具栏 -->
            <div class="editor-toolbar">
              <div class="toolbar-left">
                <button 
                  class="toolbar-btn" 
                  @click="insertExampleConfig" 
                  title="插入示例配置"
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  <span>插入示例</span>
                </button>
              </div>
              <div class="toolbar-right">
                <span class="validation-status" :class="{ 'is-valid': configStatus.valid, 'is-invalid': !configStatus.valid }">
                  <svg v-if="configStatus.valid" width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M9 12l2 2 4-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                  </svg>
                  <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                    <path d="M12 8v4M12 16h.01" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  <span>{{ configStatus.valid ? 'JSON有效' : configStatus.message }}</span>
                </span>
              </div>
            </div>
            
            <!-- JSON编辑器 -->
            <div class="editor-container">
              <div id="jsonEditor" class="json-editor"></div>
            </div>
            
            <!-- 帮助说明 -->
            <div class="config-help">
              <h4 class="help-title">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="12" cy="12" r="10" stroke="#409eff" stroke-width="2"/>
                  <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" stroke="#409eff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <line x1="12" y1="17" x2="12.01" y2="17" stroke="#409eff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                配置说明
              </h4>
              <div class="help-content">
                <div class="help-item">
                  <h5>配置格式</h5>
                  <p>配置必须是有效的JSON数组格式，每个配置项包含以下必填字段：</p>
                  <ul>
                    <li><code>key</code>: 配置项的唯一标识符</li>
                    <li><code>label</code>: 配置项的显示名称</li>
                    <li><code>value</code>: 配置项的值（可以是字符串、数字或布尔值）</li>
                  </ul>
                </div>
                <div class="help-item">
                  <h5>使用方法</h5>
                  <p>点击"插入示例"按钮可快速添加示例配置。完成编辑后点击"保存配置"按钮进行保存。</p>
                </div>
                <div class="help-item">
                  <h5>编辑器快捷键</h5>
                  <ul class="shortcut-list">
                    <li><span class="key">Ctrl+Space</span> 触发自动完成</li>
                    <li><span class="key">Ctrl+S</span> 格式化文档</li>
                    <li><span class="key">Alt+↑/↓</span> 移动行</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
          
          <div class="modal-footer">
            <button type="button" @click="closeConfigDialog" class="btn btn-cancel">
              取消
            </button>
            <button 
              type="button" 
              @click="handleConfigSubmit"
              :disabled="formLoading || !configStatus.valid"
              class="btn btn-primary"
              :title="!configStatus.valid ? configStatus.message : ''"
            >
              <span v-if="formLoading" class="loading-spinner"></span>
              保存配置
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 删除确认弹窗 -->
    <Teleport to="body">
      <div v-if="deleteDialogVisible" class="modal-overlay" @click.self="closeDeleteDialog">
        <div class="modal-dialog delete-dialog">
          <div class="modal-header delete-header">
            <div class="warning-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" stroke="#f56c6c" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="rgba(245, 108, 108, 0.1)"/>
                <line x1="12" y1="9" x2="12" y2="13" stroke="#f56c6c" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <line x1="12" y1="17" x2="12.01" y2="17" stroke="#f56c6c" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <h3>确认删除</h3>
            <button class="close-btn" @click="closeDeleteDialog">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>
          
          <div class="modal-body delete-body">
            <div class="delete-warning">
              <p class="warning-text">
                您确定要删除MCP服务器 
                <strong class="server-name-highlight">{{ deletingServer?.server_name }}</strong> 
                吗？
              </p>
              <div class="warning-details">
                <div class="detail-item">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="12" cy="12" r="10" stroke="#e6a23c" stroke-width="2"/>
                    <path d="M12 8v4" stroke="#e6a23c" stroke-width="2" stroke-linecap="round"/>
                    <path d="M12 16h.01" stroke="#e6a23c" stroke-width="2" stroke-linecap="round"/>
                  </svg>
                  <span>此操作将永久删除该服务器配置</span>
                </div>
                <div class="detail-item">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="12" cy="12" r="10" stroke="#e6a23c" stroke-width="2"/>
                    <path d="M12 8v4" stroke="#e6a23c" stroke-width="2" stroke-linecap="round"/>
                    <path d="M12 16h.01" stroke="#e6a23c" stroke-width="2" stroke-linecap="round"/>
                  </svg>
                  <span>相关的工具和配置也将被移除</span>
                </div>
                <div class="detail-item">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="12" cy="12" r="10" stroke="#e6a23c" stroke-width="2"/>
                    <path d="M12 8v4" stroke="#e6a23c" stroke-width="2" stroke-linecap="round"/>
                    <path d="M12 16h.01" stroke="#e6a23c" stroke-width="2" stroke-linecap="round"/>
                  </svg>
                  <span>此操作不可恢复，请谨慎操作</span>
                </div>
              </div>
            </div>
          </div>
          
          <div class="modal-footer delete-footer">
            <button type="button" @click="closeDeleteDialog" class="btn btn-cancel">
              取消
            </button>
            <button 
              type="button" 
              @click="confirmDelete"
              :disabled="formLoading"
              class="btn btn-danger"
            >
              <span v-if="formLoading" class="loading-spinner"></span>
              <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <polyline points="3 6 5 6 21 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <line x1="10" y1="11" x2="10" y2="17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <line x1="14" y1="11" x2="14" y2="17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              确认删除
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style lang="scss" scoped>
@use '../../styles/breakpoints.scss' as *;

// 弹窗样式 - 移除scoped，因为使用了Teleport
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  width: 100vw;
  height: 100vh;
  background-color: var(--harmony-comp-background-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-dialog) !important;
  /* removed backdrop-filter */
  pointer-events: auto;
  overflow: hidden;
}

.modal-dialog {
  background: var(--harmony-comp-background-primary);
  border-radius: var(--harmony-corner-radius-level8);
  box-shadow: var(--harmony-shadow-dialog);
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  
  &.tools-dialog {
    max-width: 800px;
  }
  
  &.delete-dialog {
    max-width: 480px;
  }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--harmony-padding-level16) var(--harmony-padding-level16);
  border-bottom: 1px solid var(--harmony-comp-divider);
  background: var(--harmony-comp-background-primary);
  
  h3 {
    margin: 0;
    font-size: var(--harmony-font-size-title-s);
    font-weight: 600;
    color: var(--harmony-font-primary);
  }
  
  .close-btn {
    width: 28px;
    height: 28px;
    border: none;
    background: none;
    color: var(--harmony-font-tertiary);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: var(--harmony-corner-radius-level4);
    transition: all 0.2s ease;
    
    &:hover {
      background: var(--harmony-comp-background-primary);
      color: var(--harmony-font-secondary);
    }
  }
}

.modal-body {
  padding: 24px;
  overflow: hidden;
  flex: 1;
  background: var(--harmony-comp-background-primary);
  
  &.tools-content {
    overflow-y: auto;
    max-height: calc(90vh - 140px);
  }
}

.modal-footer {
  padding: var(--harmony-padding-level10) var(--harmony-padding-level16);
  border-top: 1px solid var(--harmony-comp-divider);
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  background: var(--harmony-comp-background-primary);
}

// 删除对话框样式
.delete-dialog {
  .delete-header {
    background: var(--harmony-warning-bg);
    border-bottom-color: var(--harmony-warning-bg);
    position: relative;
    padding-left: 60px;
    
    .warning-icon {
      position: absolute;
      left: 20px;
      top: 50%;
      transform: translateY(-50%);
    }
    
    h3 {
      color: var(--harmony-warning);
    }
  }
  
  .delete-body {
    padding: 24px;
  }
  
  .delete-warning {
    .warning-text {
      font-size: var(--harmony-font-size-body-l);
      color: var(--harmony-font-primary);
      margin: 0 0 20px 0;
      line-height: 1.6;
      
      .server-name-highlight {
        color: var(--harmony-warning);
        font-weight: 600;
        padding: 2px 6px;
        background: var(--harmony-warning-bg);
        border-radius: var(--harmony-corner-radius-level4);
      }
    }
    
    .warning-details {
      background: var(--harmony-warning-bg);
      border: 1px solid var(--harmony-warning-bg);
      border-radius: var(--harmony-corner-radius-level6);
      padding: 16px;
      
      .detail-item {
        display: flex;
        align-items: flex-start;
        gap: 10px;
        margin-bottom: 12px;
        
        &:last-child {
          margin-bottom: 0;
        }
        
        svg {
          flex-shrink: 0;
          margin-top: 2px;
        }
        
        span {
          font-size: var(--harmony-font-size-body-m);
          color: var(--harmony-font-secondary);
          line-height: 1.5;
        }
      }
    }
  }
  
  .delete-footer {
    background: var(--harmony-comp-background-primary);
    
    .btn-danger {
      background: var(--harmony-warning);
      color: white;
      border: none;
      padding: 10px 20px;
      border-radius: var(--harmony-corner-radius-level4);
      font-size: var(--harmony-font-size-body-m);
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s ease;
      display: flex;
      align-items: center;
      gap: 6px;
      
      &:hover:not(:disabled) {
        background: var(--harmony-warning);
        transform: translateY(-1px);
        box-shadow: var(--harmony-shadow-sm);
      }
      
      &:active:not(:disabled) {
        transform: translateY(0);
      }
      
      &:disabled {
        opacity: 0.6;
        cursor: not-allowed;
      }
      
      .loading-spinner {
        width: 14px;
        height: 14px;
        border: 2px solid var(--harmony-comp-background-secondary);
        border-top-color: white;
        border-radius: var(--harmony-corner-radius-level18);
        animation: h-spin 0.6s linear infinite;
      }
    }
  }
}



// 表单样式
// 配置向导样式
.config-wizard {
  .wizard-header {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 20px;
    background: var(--harmony-comp-emphasize-tertiary);
    border: 1px solid var(--harmony-comp-emphasize-tertiary);
    border-radius: var(--harmony-corner-radius-level8);
    margin-bottom: 24px;
    
    .wizard-icon {
      flex-shrink: 0;
      width: 48px;
      height: 48px;
      background: var(--harmony-comp-background-primary);
      border-radius: var(--harmony-corner-radius-level8);
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 2px 8px var(--harmony-comp-emphasize-tertiary);
    }
    
    .wizard-text {
      h4 {
        margin: 0 0 6px 0;
        font-size: var(--harmony-font-size-title-s);
        font-weight: 600;
        color: var(--harmony-font-primary);
      }
      
      p {
        margin: 0;
        font-size: var(--harmony-font-size-body-m);
        color: var(--harmony-font-secondary);
        line-height: 1.5;
      }
    }
  }
}

.mcp-form {
  .form-section {
    background: var(--harmony-comp-background-primary);
    border-radius: var(--harmony-corner-radius-level8);
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 2px 8px var(--harmony-shadow-xs);
    
    .section-title {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 20px;
      padding-bottom: 12px;
      font-weight: 600;
      color: var(--harmony-font-primary);
      font-size: var(--harmony-font-size-body-l);
      
      .required-mark {
        color: var(--harmony-warning);
        margin-left: 4px;
      }
    }
  }
  
  .form-layout {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
    
    @include mobile {
      grid-template-columns: 1fr;
    }
  }
  
  .form-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    
    @include mobile {
      grid-template-columns: 1fr;
    }
  }
  
  .form-group {
    margin-bottom: 0;
    
    &.form-group-full {
      grid-column: 1 / -1;
      margin-bottom: 0;
    }
    
    label {
      display: flex;
      align-items: center;
      gap: 8px;
      font-weight: 600;
      color: var(--harmony-font-primary);
      margin-bottom: 12px;
      font-size: var(--harmony-font-size-body-m);
      
      .required-mark {
        color: var(--harmony-warning);
        margin-left: 2px;
      }
      
      svg {
        opacity: 0.7;
      }
    }
    
    input, select, textarea {
      width: 100%;
      padding: var(--harmony-padding-level8) var(--harmony-padding-level10);
      border: 1px solid var(--harmony-comp-divider);
      border-radius: var(--harmony-corner-radius-level4);
      font-size: var(--harmony-font-size-body-m);
      transition: all 0.2s ease;
      background: var(--harmony-comp-background-primary);
      box-sizing: border-box;
      font-family: var(--harmony-font-family);
      
      &:focus {
        border-color: var(--harmony-brand);
        box-shadow: 0 0 0 2px var(--harmony-comp-emphasize-tertiary);
      }
      
      &:hover {
        border-color: var(--harmony-font-tertiary);
      }
      
      &.error {
        border-color: var(--harmony-warning);
        background-color: var(--harmony-warning-bg);
      }
      
      &::placeholder {
        color: var(--harmony-font-tertiary);
        font-size: var(--harmony-font-size-subtitle-s);
      }
      
      &:disabled,
      &[readonly] {
        background-color: var(--harmony-comp-background-primary);
        border-color: var(--harmony-comp-divider);
        color: var(--harmony-font-tertiary);
        cursor: not-allowed;
        
        &::placeholder {
          color: var(--harmony-font-tertiary);
        }
      }
    }
    
    textarea {
      resize: vertical;
      min-height: 100px;
      font-family: var(--harmony-font-family);
      line-height: 1.6;
      font-size: var(--harmony-font-size-body-l);
    }
    
    select {
      cursor: pointer;
      appearance: none;
      background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6,9 12,15 18,9'%3e%3c/polyline%3e%3c/svg%3e");
      background-repeat: no-repeat;
      background-position: right 12px center;
      background-size: 16px;
      padding-right: 40px;
    }
    
    .error-text {
      display: block;
      color: var(--harmony-warning);
      font-size: var(--harmony-font-size-body-s);
      margin-top: 6px;
      font-weight: 500;
    }
    
    .help-text {
      display: flex;
      align-items: flex-start;
      gap: 6px;
      font-size: var(--harmony-font-size-body-s);
      color: var(--harmony-font-tertiary);
      margin-top: 8px;
      line-height: 1.5;
      padding: 8px 12px;
      background: var(--harmony-comp-background-primary);
      border-radius: var(--harmony-corner-radius-level4);
      border-left: 3px solid var(--harmony-brand);
      
      svg {
        flex-shrink: 0;
        margin-top: 2px;
      }
    }
    
    .input-help {
      display: flex;
      align-items: flex-start;
      gap: 8px;
      font-size: var(--harmony-font-size-body-s);
      color: var(--harmony-font-tertiary);
      margin-top: 8px;
      line-height: 1.5;
      padding: 8px 12px;
      background: var(--harmony-comp-background-primary);
      border-radius: var(--harmony-corner-radius-level4);
      border-left: 3px solid var(--harmony-confirm);
      
      svg {
        flex-shrink: 0;
        margin-top: 2px;
      }
    }
    
    .textarea-wrapper {
      position: relative;
      
      .json-indicator {
        position: absolute;
        top: 12px;
        right: 12px;
        display: flex;
        align-items: center;
        gap: 4px;
        background: var(--harmony-comp-background-primary);
        padding: 4px 8px;
        border-radius: var(--harmony-corner-radius-level4);
        font-size: var(--harmony-font-size-caption-l);
        color: var(--harmony-font-tertiary);
        font-weight: 500;
        /* removed backdrop-filter */
      }
    }
    
    // 方形加号上传按钮样式
    .logo-upload-square {
      margin-left: 20px;
      width: 100px;
      height: 100px;
      border: 2px solid var(--harmony-brand);
      border-radius: var(--harmony-corner-radius-level6);
      cursor: pointer;
      position: relative;
      overflow: hidden;
      transition: all 0.3s ease;
      background: var(--harmony-comp-emphasize-tertiary);
      display: block;
      box-sizing: border-box;

      &:hover {
        background: var(--harmony-brand);
        border-color: var(--harmony-brand);

        .logo-upload-placeholder {
          svg path {
            stroke: white !important;
          }
        }
      }

      .logo-upload-placeholder {
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--harmony-brand);
        transition: all 0.3s ease;
        background: transparent;

        svg {
          width: 32px;
          height: 32px;
          display: block;

          path {
            stroke: var(--harmony-brand) !important;
            stroke-width: 2.5;
          }
        }

        &.uploading {
          .uploading-text {
            font-size: var(--harmony-font-size-body-s);
            color: var(--harmony-brand);
            font-weight: 500;
          }
        }
      }

      &:hover .logo-upload-placeholder {
        color: white;

        svg path {
          stroke: white !important;
        }
      }
      
      .logo-preview-square {
        width: 100%;
        height: 100%;
        position: relative;
        border-radius: var(--harmony-corner-radius-level6);
        overflow: hidden;
        display: flex;
        align-items: center;
        justify-content: center;
        
        img {
          width: 50px;
          height: 50px;
          object-fit: cover;
          border-radius: var(--harmony-corner-radius-level4);
        }
        
        .logo-overlay {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: var(--harmony-comp-background-secondary);
          display: flex;
          align-items: center;
          justify-content: center;
          opacity: 0;
          transition: opacity 0.3s ease;
          
          &:hover {
            opacity: 1;
          }
        }
      }
    }
  }
}

// 按钮样式
.btn {
  padding: 10px 20px;
  border-radius: var(--harmony-corner-radius-level4);
  font-size: var(--harmony-font-size-body-m);
  font-weight: 500;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 78px;
  line-height: 1;
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  &.btn-cancel {
    background: var(--harmony-comp-background-primary);
    border-color: var(--harmony-comp-divider);
    color: var(--harmony-font-secondary);
    
    &:hover:not(:disabled) {
      color: var(--harmony-brand);
      border-color: var(--harmony-comp-emphasize-tertiary);
      background-color: var(--harmony-comp-emphasize-tertiary);
    }
  }
  
  &.btn-primary {
    background: var(--harmony-brand);
    border-color: var(--harmony-brand);
    color: var(--harmony-comp-background-primary);
    
    &:hover:not(:disabled) {
      background: var(--harmony-brand);
      border-color: var(--harmony-brand);
    }
    
    &:active:not(:disabled) {
      background: var(--harmony-brand);
      border-color: var(--harmony-brand);
    }
  }
}

.loading-spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid var(--harmony-comp-background-secondary);
  border-radius: var(--harmony-corner-radius-level18);
  border-top-color: white;
  animation: h-spin 1s ease-in-out infinite;
  margin-right: 8px;
}


// 页面样式已移至底部scoped样式中，避免重复

// 工具详情样式
.tools-content {
  background: var(--harmony-comp-background-primary);
  
  .no-tools {
    text-align: center;
    padding: 80px 40px;
    
    .empty-icon {
      margin-bottom: 20px;
      opacity: 0.6;
    }
    
    .empty-text {
      h3 {
        margin: 0 0 8px 0;
        font-size: var(--harmony-font-size-title-s);
        font-weight: 600;
        color: var(--harmony-font-tertiary);
      }
      
      p {
        color: var(--harmony-font-tertiary);
        font-size: var(--harmony-font-size-body-m);
        margin: 0;
        line-height: 1.5;
      }
    }
  }
  
  .tools-overview {
    .tools-stats {
      margin-bottom: 24px;
      
      .stat-card {
        background: var(--harmony-comp-background-primary);
        border-radius: var(--harmony-corner-radius-level8);
        padding: 20px;
        display: flex;
        align-items: center;
        gap: 16px;
        box-shadow: 0 2px 8px var(--harmony-shadow-xs);
        
        .stat-icon {
          width: 48px;
          height: 48px;
          background: var(--harmony-comp-emphasize-tertiary);
          border-radius: var(--harmony-corner-radius-level8);
          display: flex;
          align-items: center;
          justify-content: center;
        }
        
        .stat-info {
          display: flex;
          flex-direction: column;
          gap: 4px;
          
          .stat-number {
            font-size: var(--harmony-font-size-title-m);
            font-weight: 700;
            color: var(--harmony-brand);
            line-height: 1;
          }
          
          .stat-label {
            font-size: var(--harmony-font-size-body-m);
            color: var(--harmony-font-secondary);
            font-weight: 500;
          }
        }
      }
    }
    
    .tools-list {
      .tool-item {
        background: var(--harmony-comp-background-primary);
        border-radius: var(--harmony-corner-radius-level8);
        margin-bottom: 12px;
        overflow: hidden;
        transition: all 0.2s ease;
        cursor: pointer;
        
        &:hover {
          box-shadow: var(--harmony-shadow-sm);
        }
        
        &.expanded {
          box-shadow: var(--harmony-shadow-sm);
          
          .tool-expand-icon svg {
            transform: rotate(180deg);
          }
        }
        
        .tool-summary {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: var(--harmony-padding-level16) var(--harmony-padding-level16);
          
          .tool-info {
            display: flex;
            align-items: flex-start;
            gap: 12px;
            flex: 1;
            
            .tool-icon {
              width: 40px;
              height: 40px;
              background: var(--harmony-comp-emphasize-tertiary);
              border-radius: var(--harmony-corner-radius-level6);
              display: flex;
              align-items: center;
              justify-content: center;
              flex-shrink: 0;
            }
            
            .tool-text {
              flex: 1;
              
              .tool-name {
                margin: 0 0 6px 0;
                font-size: var(--harmony-font-size-body-l);
                font-weight: 600;
                color: var(--harmony-font-primary);
              }
              
              .tool-description {
                margin: 0;
                color: var(--harmony-font-secondary);
                font-size: var(--harmony-font-size-body-m);
                line-height: 1.5;
              }
            }
          }
          
          .tool-expand-icon {
            flex-shrink: 0;
            color: var(--harmony-font-tertiary);
            transition: all 0.3s ease;
            
            svg {
              transition: transform 0.3s ease;
            }
          }
        }
        
        .tool-details {
          padding: 0 24px 20px 24px;
          
          .tool-schema {
            background: var(--harmony-comp-background-primary);
            border-radius: var(--harmony-corner-radius-level6);
            padding: 20px;
            margin-top: 20px;
            
            .schema-header {
              display: flex;
              align-items: center;
              gap: 8px;
              margin-bottom: 16px;
              padding-bottom: 12px;
              font-weight: 600;
              color: var(--harmony-font-primary);
              font-size: var(--harmony-font-size-body-m);
            }
            
            .schema-content {
              .schema-meta {
                margin-bottom: 16px;
                
                .meta-item {
                  display: flex;
                  align-items: center;
                  gap: 8px;
                  margin-bottom: 8px;
                  
                  .meta-label {
                    font-weight: 500;
                    color: var(--harmony-font-secondary);
                    min-width: 60px;
                  }
                  
                  .meta-value {
                    color: var(--harmony-font-primary);
                    
                    &.type {
                      background: var(--harmony-comp-background-primary);
                      padding: 2px 8px;
                      border-radius: var(--harmony-corner-radius-level4);
                      font-size: var(--harmony-font-size-body-s);
                      font-weight: 500;
                    }
                  }
                }
              }
              
              .required-section {
                margin-bottom: 16px;
                
                .section-title {
                  display: flex;
                  align-items: center;
                  gap: 6px;
                  margin-bottom: 12px;
                  font-weight: 600;
                  color: var(--harmony-warning);
                  font-size: var(--harmony-font-size-body-m);
                }
                
                .required-params {
                  display: flex;
                  flex-wrap: wrap;
                  gap: 8px;
                  
                  .required-param {
                    background: var(--harmony-warning-bg);
                    color: var(--harmony-warning);
                    border: 1px solid var(--harmony-warning-bg);
                    padding: 4px 8px;
                    border-radius: var(--harmony-corner-radius-level4);
                    font-size: var(--harmony-font-size-body-s);
                    font-weight: 500;
                  }
                }
              }
              
              .properties-section {
                .section-title {
                  display: flex;
                  align-items: center;
                  gap: 6px;
                  margin-bottom: 12px;
                  font-weight: 600;
                  color: var(--harmony-confirm);
                  font-size: var(--harmony-font-size-body-m);
                }
                
                .properties-grid {
                  display: grid;
                  gap: 12px;
                  
                  .property-card {
                    background: var(--harmony-comp-background-primary);
                    border-radius: var(--harmony-corner-radius-level4);
                    padding: 16px;
                    
                    .property-header {
                      display: flex;
                      justify-content: space-between;
                      align-items: center;
                      margin-bottom: 8px;
                      
                      .property-name {
                        font-weight: 600;
                        color: var(--harmony-font-primary);
                        font-size: var(--harmony-font-size-body-m);
                      }
                      
                      .property-type {
                        background: var(--harmony-comp-emphasize-tertiary);
                        color: var(--harmony-brand);
                        padding: 2px 8px;
                        border-radius: var(--harmony-corner-radius-level4);
                        font-size: var(--harmony-font-size-body-s);
                        font-weight: 500;
                      }
                    }
                    
                    .property-body {
                      .property-desc {
                        color: var(--harmony-font-secondary);
                        font-size: var(--harmony-font-size-subtitle-s);
                        line-height: 1.5;
                        margin: 0 0 8px 0;
                      }
                      
                      .property-default {
                        display: flex;
                        align-items: center;
                        gap: 6px;
                        
                        .default-label {
                          font-size: var(--harmony-font-size-body-s);
                          color: var(--harmony-font-tertiary);
                        }
                        
                        .default-value {
                          background: var(--harmony-comp-background-primary);
                          color: var(--harmony-font-primary);
                          padding: 2px 6px;
                          border-radius: var(--harmony-corner-radius-level2);
                          font-size: var(--harmony-font-size-body-s);
                          font-family: var(--harmony-font-family);
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
    
    // 展开动画
    .expand-enter-active,
    .expand-leave-active {
      transition: all 0.3s ease;
      max-height: 2000px;
      overflow: hidden;
    }
    
    .expand-enter-from,
    .expand-leave-to {
      max-height: 0;
      opacity: 0;
    }
  }
}

.mcp-server-page {
  padding: 32px;
  min-height: 100%;
  background: var(--harmony-comp-background-primary);
  
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    background: var(--harmony-comp-background-primary);
    padding: var(--harmony-padding-level16) var(--harmony-padding-level16);
    border-radius: var(--harmony-corner-radius-level8);
    box-shadow: var(--harmony-shadow-xs);
    
    .header-title {
      display: flex;
      align-items: center;
      gap: 14px;
      
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
      .h-button {
        font-weight: 600;
        letter-spacing: 0.025em;
        border-radius: var(--harmony-corner-radius-level8);
        padding: var(--harmony-padding-level8) var(--harmony-padding-level16);
        transition: all 0.2s ease;
        
        &:hover {
          transform: translateY(-1px);
          box-shadow: var(--harmony-shadow-sm);
        }
      }
    }
  }
  
  .server-list {
    min-height: 400px;
    background: var(--harmony-comp-background-primary);
    border-radius: var(--harmony-corner-radius-level8);
    box-shadow: var(--harmony-shadow-xs);
    overflow: auto;
    
    :deep(.server-table-wrapper) {
      border-radius: var(--harmony-corner-radius-level8);
      overflow: hidden;
    }

    .server-table {
      width: 100%;
      border-collapse: collapse;
      font-family: var(--harmony-font-family);

      thead {
        th {
          background: var(--harmony-comp-background-primary);
          color: var(--harmony-font-primary);
          font-weight: 700;
          font-size: var(--harmony-font-size-subtitle-s);
          padding: 18px 12px;
          border-bottom: 2px solid var(--harmony-comp-divider);
          letter-spacing: 0.025em;
          text-transform: uppercase;
        }
      }

      tbody {
        tr {
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

          &:hover {
            background: var(--harmony-comp-background-primary);
            transform: translateY(-1px);
            box-shadow: 0 4px 12px var(--harmony-shadow-xs);
          }

          td {
            padding: 20px 12px;
            border-bottom: 1px solid var(--harmony-comp-divider);
            font-size: var(--harmony-font-size-body-m);
            font-weight: 500;
            color: var(--harmony-font-primary);
            font-family: var(--harmony-font-family);
            line-height: 1.5;
          }
        }
      }
    }
    
    .server-avatar {
      width: 40px;
      height: 40px;
      border-radius: var(--harmony-corner-radius-level6);
      overflow: hidden;
      margin: 0 auto;
      
      img {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }
    }
    
    .server-name {
      text-align: center;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 8px;
      
      .name {
        font-weight: 600;
        color: var(--harmony-font-primary);
        font-size: var(--harmony-font-size-body-l);
        display: block;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        font-family: var(--harmony-font-family);
        letter-spacing: -0.01em;
      }
      
      &.official-server {
        opacity: 0.8;
        
        .name {
          color: var(--harmony-font-secondary);
          font-weight: 500;
        }
      }
      
      .official-tag {
        margin-top: 2px;
        font-weight: 600;
        font-size: var(--harmony-font-size-caption-l);
        letter-spacing: 0.025em;
      }
    }
    
    .config-status {
      display: flex;
      justify-content: center;
      align-items: center;
      
      .h-tag {
        font-weight: 600;
        letter-spacing: 0.025em;
        border-radius: var(--harmony-corner-radius-level6);
        font-family: var(--harmony-font-family);
      }
      
      .clickable-tag {
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        font-weight: 700;
        
        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 20px var(--harmony-alert-bg);
          background: linear-gradient(135deg, var(--harmony-alert) 0%, var(--harmony-alert) 100%);
          border-color: var(--harmony-alert);
          color: white;
        }
        
        &:active {
          transform: translateY(0);
        }
        
        &::before {
          content: '';
          display: inline-block;
          width: 12px;
          height: 12px;
          margin-right: 6px;
          background: currentColor;
          -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath d='M8 0C7.4 0 6.9 0.4 6.7 1L6.3 2.3C5.8 2.5 5.3 2.8 4.9 3.1L3.7 2.5C3.1 2.2 2.4 2.5 2.2 3.1L1.1 5.1C0.9 5.7 1.1 6.4 1.7 6.7L2.9 7.3C2.8 7.8 2.8 8.2 2.9 8.7L1.7 9.3C1.1 9.6 0.9 10.3 1.1 10.9L2.2 12.9C2.4 13.5 3.1 13.8 3.7 13.5L4.9 12.9C5.3 13.2 5.8 13.5 6.3 13.7L6.7 15C6.9 15.6 7.4 16 8 16C8.6 16 9.1 15.6 9.3 15L9.7 13.7C10.2 13.5 10.7 13.2 11.1 12.9L12.3 13.5C12.9 13.8 13.6 13.5 13.8 12.9L14.9 10.9C15.1 10.3 14.9 9.6 14.3 9.3L13.1 8.7C13.2 8.2 13.2 7.8 13.1 7.3L14.3 6.7C14.9 6.4 15.1 5.7 14.9 5.1L13.8 3.1C13.6 2.5 12.9 2.2 12.3 2.5L11.1 3.1C10.7 2.8 10.2 2.5 9.7 2.3L9.3 1C9.1 0.4 8.6 0 8 0Z' fill='%23000'/%3E%3C/svg%3E") no-repeat center/contain;
          -webkit-mask-size: contain;
          mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath d='M8 0C7.4 0 6.9 0.4 6.7 1L6.3 2.3C5.8 2.5 5.3 2.8 4.9 3.1L3.7 2.5C3.1 2.2 2.4 2.5 2.2 3.1L1.1 5.1C0.9 5.7 1.1 6.4 1.7 6.7L2.9 7.3C2.8 7.8 2.8 8.2 2.9 8.7L1.7 9.3C1.1 9.6 0.9 10.3 1.1 10.9L2.2 12.9C2.4 13.5 3.1 13.8 3.7 13.5L4.9 12.9C5.3 13.2 5.8 13.5 6.3 13.7L6.7 15C6.9 15.6 7.4 16 8 16C8.6 16 9.1 15.6 9.3 15L9.7 13.7C10.2 13.5 10.7 13.2 11.1 12.9L12.3 13.5C12.9 13.8 13.6 13.5 13.8 12.9L14.9 10.9C15.1 10.3 14.9 9.6 14.3 9.3L13.1 8.7C13.2 8.2 13.2 7.8 13.1 7.3L14.3 6.7C14.9 6.4 15.1 5.7 14.9 5.1L13.8 3.1C13.6 2.5 12.9 2.2 12.3 2.5L11.1 3.1C10.7 2.8 10.2 2.5 9.7 2.3L9.3 1C9.1 0.4 8.6 0 8 0Z' fill='%23000'/%3E%3C/svg%3E") no-repeat center/contain;
          mask-size: contain;
        }
      }
    }
    
    .user-info {
      display: flex;
      justify-content: center;
      
      .h-tag {
        font-size: var(--harmony-font-size-body-s);
        padding: 6px 12px;
        font-weight: 600;
        letter-spacing: 0.025em;
        border-radius: var(--harmony-corner-radius-level6);
      }
    }
    
    .tools-count {
      .h-button {
        font-size: var(--harmony-font-size-body-s);
        padding: 8px 14px;
        font-weight: 600;
        letter-spacing: 0.025em;
        border-radius: var(--harmony-corner-radius-level6);
        transition: all 0.3s ease;

        &:hover {
          transform: translateY(-1px);
          box-shadow: 0 4px 12px var(--harmony-comp-emphasize-tertiary);
        }
      }
    }
    
    .create-time {
      font-size: var(--harmony-font-size-subtitle-s);
      color: var(--harmony-font-secondary);
      font-weight: 500;
      font-family: var(--harmony-font-family);
    }
    
    .action-buttons {
      display: flex;
      gap: 8px;
      justify-content: center;
      align-items: center;
      
      .h-button {
        padding: 8px 16px;
        font-size: var(--harmony-font-size-subtitle-s);
        font-weight: 600;
        border-radius: var(--harmony-corner-radius-level6);
        transition: all 0.3s ease;

        &:hover {
          transform: translateY(-1px);
        }
      }
    }

        .empty-state {
      text-align: center;
      padding: 80px 20px;

      p {
        margin-top: 24px;
        font-size: var(--harmony-font-size-body-l);
        color: var(--harmony-font-secondary);
        font-weight: 500;
        font-family: var(--harmony-font-family);
        letter-spacing: -0.01em;
      }
    }
  }
}

// 响应式设计
@include mobile {
  .mcp-server-page {
    padding: 16px;
    
    .page-header {
      flex-direction: column;
      gap: 16px;
      align-items: stretch;
    }
  }
  
  // 配置对话框样式
  .config-dialog {
    max-width: 600px;
    
    .config-info {
      margin-bottom: 24px;
      
      .info-card {
        background: linear-gradient(135deg, var(--harmony-comp-emphasize-tertiary) 0%, var(--harmony-comp-emphasize-tertiary) 100%);
        border: 1px solid var(--harmony-comp-emphasize-tertiary);
        border-radius: var(--harmony-corner-radius-level8);
        padding: 16px;
        display: flex;
        align-items: flex-start;
        gap: 12px;
        
        .info-icon {
          flex-shrink: 0;
          width: 40px;
          height: 40px;
          background: var(--harmony-comp-emphasize-tertiary);
          border-radius: var(--harmony-corner-radius-level18);
          display: flex;
          align-items: center;
          justify-content: center;
        }
        
        .info-text {
          flex: 1;
          
          h4 {
            margin: 0 0 6px 0;
            font-size: var(--harmony-font-size-body-l);
            font-weight: 600;
            color: var(--harmony-font-primary);
          }
          
          p {
            margin: 0;
            font-size: var(--harmony-font-size-body-m);
            color: var(--harmony-font-secondary);
            line-height: 1.6;
          }
        }
      }
    }
    
    .form-section .form-group textarea {
      min-height: 240px;
    }
    
    .json-indicator {
      span {
        color: var(--harmony-alert);
        font-weight: 500;
      }
    }
  }
}

// 配置对话框样式改进
.config-dialog {
  max-width: 800px;
  
  .modal-header h3 {
    display: flex;
    align-items: center;
    gap: 8px;
    
    .config-server-name {
      font-weight: 700;
      color: var(--harmony-font-primary);
    }
    
    .config-title {
      color: var(--harmony-font-secondary);
      font-weight: 500;
    }
    
    &::before {
      content: '';
      display: inline-block;
      width: 4px;
      height: 18px;
      background: var(--harmony-brand);
      border-radius: var(--harmony-corner-radius-level1);
      margin-right: 8px;
    }
  }
  
  .config-info {
    margin-bottom: 20px;
    
    .info-card {
      background: linear-gradient(135deg, var(--harmony-comp-emphasize-tertiary) 0%, var(--harmony-comp-emphasize-tertiary) 100%);
      border: 1px solid var(--harmony-comp-emphasize-tertiary);
      border-radius: var(--harmony-corner-radius-level8);
      padding: 16px;
      display: flex;
      align-items: flex-start;
      gap: 12px;
      
      .info-icon {
        flex-shrink: 0;
        width: 40px;
        height: 40px;
        background: var(--harmony-comp-emphasize-tertiary);
        border-radius: var(--harmony-corner-radius-level18);
        display: flex;
        align-items: center;
        justify-content: center;
      }
      
      .info-text {
        flex: 1;
        
        h4 {
          margin: 0 0 6px 0;
          font-size: var(--harmony-font-size-body-l);
          font-weight: 600;
          color: var(--harmony-font-primary);
        }
        
        p {
          margin: 0;
          font-size: var(--harmony-font-size-body-m);
          color: var(--harmony-font-secondary);
          line-height: 1.6;
        }
      }
    }
  }
  
  // 编辑器工具栏
  .editor-toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: var(--harmony-comp-background-primary);
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    padding: 8px 12px;
    
    .toolbar-btn {
      display: flex;
      align-items: center;
      gap: 6px;
      border: none;
      background: var(--harmony-comp-background-primary);
      color: var(--harmony-font-secondary);
      padding: 6px 12px;
      border-radius: var(--harmony-corner-radius-level4);
      font-size: var(--harmony-font-size-subtitle-s);
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s ease;
      
      &:hover {
        background: var(--harmony-comp-divider);
        color: var(--harmony-font-primary);
      }
      
      svg {
        width: 16px;
        height: 16px;
      }
    }
    
    .validation-status {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: var(--harmony-font-size-subtitle-s);
      padding: 6px 12px;
      border-radius: var(--harmony-corner-radius-level4);
      
      &.is-valid {
        background: var(--harmony-confirm-bg);
        color: var(--harmony-confirm);
      }
      
      &.is-invalid {
        background: var(--harmony-warning-bg);
        color: var(--harmony-warning);
      }
    }
  }
  
  // 编辑器容器
  .editor-container {
    height: 300px;
    border-bottom-left-radius: 8px;
    border-bottom-right-radius: 8px;
    overflow: hidden;
    
    .json-editor {
      height: 100%;
      width: 100%;
    }
  }
  
  // 帮助说明
  .config-help {
    margin-top: 24px;
    background: var(--harmony-comp-background-primary);
    border-radius: var(--harmony-corner-radius-level6);
    overflow: hidden;
    
    .help-title {
      display: flex;
      align-items: center;
      gap: 8px;
      margin: 0;
      padding: var(--harmony-padding-level8) var(--harmony-padding-level10);
      background: var(--harmony-comp-background-primary);
      color: var(--harmony-font-primary);
      font-size: var(--harmony-font-size-body-m);
      font-weight: 600;
    }
    
    .help-content {
      padding: 16px;
      
      .help-item {
        margin-bottom: 16px;
        
        &:last-child {
          margin-bottom: 0;
        }
        
        h5 {
          margin: 0 0 8px 0;
          font-size: var(--harmony-font-size-body-m);
          color: var(--harmony-font-primary);
          font-weight: 600;
        }
        
        p {
          margin: 0 0 8px 0;
          font-size: var(--harmony-font-size-subtitle-s);
          color: var(--harmony-font-secondary);
          line-height: 1.5;
        }
        
        ul {
          margin: 0;
          padding-left: 20px;
          
          li {
            font-size: var(--harmony-font-size-subtitle-s);
            color: var(--harmony-font-secondary);
            margin-bottom: 4px;
            
            code {
              background: var(--harmony-comp-divider);
              padding: 2px 4px;
              border-radius: var(--harmony-corner-radius-level4);
              color: var(--harmony-font-primary);
              font-family: var(--harmony-font-family);
              font-size: var(--harmony-font-size-body-s);
            }
          }
        }
        
        .shortcut-list {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
          gap: 8px;
          list-style-type: none;
          padding: 0;
          
          li {
            display: flex;
            align-items: center;
            gap: 8px;
            
            .key {
              background: var(--harmony-comp-divider);
              padding: 2px 6px;
              border-radius: var(--harmony-corner-radius-level4);
              color: var(--harmony-font-secondary);
              font-family: var(--harmony-font-family);
              font-size: var(--harmony-font-size-body-s);
              box-shadow: 0 1px 2px var(--harmony-shadow-xs);
            }
          }
        }
      }
    }
  }
  
  .modal-footer {
    .btn-primary {
      &:disabled {
        opacity: 0.7;
        cursor: not-allowed;
      }
    }
  }
}

@include mobile {
  .config-dialog {
    .editor-container {
      height: 250px;
    }
    
    .config-help {
      .help-content {
        .help-item {
          .shortcut-list {
            grid-template-columns: 1fr;
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
  padding: 60px 20px;
  text-align: center;
  margin: 20px auto;
  max-width: 600px;
  
  .empty-icon {
    width: 120px;
    height: 120px;
    display: flex;
    justify-content: center;
    align-items: center;
    background: var(--harmony-comp-emphasize-tertiary);
    border-radius: var(--harmony-corner-radius-level18);
    margin-bottom: 20px;
    
    .empty-icon-symbol {
      font-size: 60px;
    }
  }
  
  h3 {
    font-size: var(--harmony-font-size-title-s);
    color: var(--harmony-font-primary);
    margin: 0 0 16px;
  }
  
  p {
    margin: 0 0 20px;
    font-size: var(--harmony-font-size-body-l);
    color: var(--harmony-font-tertiary);
    max-width: 300px;
  }
  
  .create-btn {
    padding: var(--harmony-padding-level8) var(--harmony-padding-level16);
    font-size: var(--harmony-font-size-body-l);
  }
}
</style>

<!-- 页面本身的样式使用scoped -->
<style lang="scss" scoped>
.mcp-server-page {
  display: flex;
  flex-direction: column;
  min-height: 100%;
  width: 100%;
  background: transparent;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--harmony-padding-level16) var(--harmony-padding-level16);
  background: var(--harmony-comp-background-primary);
  
  .header-title {
    display: flex;
    align-items: center;
    gap: 12px;
    
    h2 {
      margin: 0;
      font-size: var(--harmony-font-size-title-s);
      font-weight: 600;
      color: var(--harmony-font-primary);
    }
  }
  
  .header-actions {
    display: flex;
    gap: 12px;
  }
}

.server-list {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  
  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: var(--harmony-font-secondary);
    
    .empty-icon {
      font-size: 64px;
      margin-bottom: 16px;
      opacity: 0.5;
      
      .empty-icon-symbol {
        font-style: normal;
      }
    }
    
    h3 {
      font-size: var(--harmony-font-size-title-s);
      margin: 0 0 8px 0;
      font-weight: 500;
    }
    
    p {
      font-size: var(--harmony-font-size-body-m);
      margin: 0 0 24px 0;
      opacity: 0.7;
    }
  }
}

.server-avatar {
  width: 48px;
  height: 48px;
  border-radius: var(--harmony-corner-radius-level6);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--harmony-comp-background-tertiary);
  
  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
}

.server-name {
  display: flex;
  align-items: center;
  gap: 8px;
  
  .name {
    font-weight: 500;
  }
  
  &.official-server {
    .name {
      color: var(--harmony-alert);
    }
  }
}

.config-status {
  .clickable-tag {
    cursor: pointer;
    transition: all 0.2s;
    
    &:hover {
      opacity: 0.8;
      transform: scale(1.05);
    }
  }
}

.create-time {
  font-size: var(--harmony-font-size-subtitle-s);
  color: var(--harmony-font-secondary);
}

.action-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
}

/* ==================== MOBILE: hmos mobile-list ==================== */
.mcp-mobile {
  display: flex;
  flex-direction: column;
  gap: var(--harmony-section-gap-mobile, 16px);
  padding-top: var(--harmony-padding-level8, 16px);
}

.mcpm-header {
  display: flex;
  justify-content: flex-end;
}

.mcpm-create-btn {
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

.mcpm-list {
  display: flex;
  flex-direction: column;
  gap: var(--harmony-card-gap-mobile, 12px);
}

.mcpm-item {
  display: flex;
  align-items: center;
  gap: var(--harmony-padding-level6, 12px);
  padding: var(--harmony-padding-level6, 12px);
  background: var(--harmony-comp-background-primary);
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

  &__img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: inherit;
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

  &__url {
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

.mcpm-official-tag {
  font-size: var(--harmony-font-size-caption-l, 11px);
  padding: 1px 6px;
  background: var(--harmony-warning-bg, rgba(230, 162, 60, 0.12));
  color: var(--harmony-warning, #e6a23c);
  border-radius: var(--harmony-corner-radius-level4, 8px);
  font-weight: 600;
  flex-shrink: 0;
}

.mcpm-status {
  font-size: var(--harmony-font-size-caption-l, 12px);
  padding: var(--harmony-padding-level1, 2px) var(--harmony-padding-level4, 8px);
  border-radius: var(--harmony-corner-radius-level4, 8px);
  flex-shrink: 0;

  &.active, &.online {
    background: var(--harmony-confirm-bg, rgba(100, 187, 92, 0.15));
    color: var(--harmony-confirm);
  }
  &.inactive, &.offline {
    background: var(--harmony-comp-background-secondary);
    color: var(--harmony-font-tertiary);
  }
}

.mcpm-action {
  width: var(--harmony-control-height-36, 36px);
  height: var(--harmony-control-height-36, 36px);
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--harmony-comp-background-secondary);
  border: none;
  border-radius: var(--harmony-corner-radius-level4, 8px);
  cursor: pointer;
  font-size: var(--harmony-font-size-body-l, 16px);
  &:active { background: var(--harmony-interactive-pressed); }
  &--danger:active { background: rgba(232, 64, 38, 0.1); }
}

.mcpm-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--harmony-padding-level16, 32px) 0;
  p { font-size: var(--harmony-font-size-body-m); color: var(--harmony-font-tertiary); margin: 0; }
}
</style>
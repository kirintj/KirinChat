<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { HButton, HInput, HSelect, HOption, HForm, HFormItem, HTag, HMessage } from '@/components/ui'
import { createAgentAPI, updateAgentAPI, getAgentByIdAPI } from '../../apis/agent'
import { getVisibleLLMsAPI, getAgentModelsAPI } from '../../apis/llm'
import { getVisibleToolsAPI } from '../../apis/tool'
import { getMCPServersAPI } from '../../apis/mcp-server'
import { getKnowledgeListAPI } from '../../apis/knowledge'
import { getAgentSkillsAPI } from '../../apis/agent-skill'
import { uploadFileAPI } from '../../apis/file'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const formRef = ref()
const isEditing = ref(false)
const avatarFileInput = ref<HTMLInputElement | null>(null)

const formData = reactive({
  name: '',
  description: '',
  logo_url: '',
  tool_ids: [] as string[],
  llm_id: '',
  mcp_ids: [] as string[],
  system_prompt: '',
  knowledge_ids: [] as string[],
  agent_skill_ids: [] as string[],
  enable_memory: false
})

// 折叠面板状态 - 默认展开AI模型，其余折叠
const collapseItems = ref({
  basic: true,
  aiModel: true,
  memory: true,
  knowledge: false,
  tools: false,
  mcp: false,
  skills: false
})

const dataLoading = ref({
  llm: false,
  tool: false,
  mcp: false,
  agentSkill: false,
  knowledge: false
})

const rules = {
  name: [{ required: true, message: '请输入智能体名称', trigger: 'blur' }],
  description: [{ required: true, message: '请输入智能体描述', trigger: 'blur' }],
  system_prompt: [{ required: true, message: '请输入系统提示词', trigger: 'blur' }],
  llm_id: [{ required: true, message: '请选择大模型', trigger: 'change' }]
}

const llmOptions = ref<any[]>([])
const toolOptions = ref<any[]>([])
const mcpOptions = ref<any[]>([])
const agentSkillOptions = ref<any[]>([])
const knowledgeOptions = ref<any[]>([])

// ============ 折叠面板 ============
const toggleCollapse = (key: keyof typeof collapseItems.value) => {
  collapseItems.value[key] = !collapseItems.value[key]
}

// ============ 文件上传 ============
const handleAvatarClick = () => {
  avatarFileInput.value?.click()
}

const handleFileChange = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  const isLt2M = file.size / 1024 / 1024 < 2
  if (!isLt2M) {
    HMessage.error('上传头像图片大小不能超过 2MB!')
    return
  }
  const isJpgOrPng = file.type === 'image/jpeg' || file.type === 'image/png'
  if (!isJpgOrPng) {
    HMessage.error('上传头像图片只能是 JPG/PNG 格式!')
    return
  }

  try {
    const uploadFormData = new FormData()
    uploadFormData.append('file', file)
    const response = await uploadFileAPI(uploadFormData)
    if (response.data.status_code === 200) {
      formData.logo_url = response.data.data
      HMessage.success('头像上传成功')
    } else {
      HMessage.error(response.data.status_message || '头像上传失败')
    }
  } catch (error) {
    HMessage.error('头像上传失败')
  } finally {
    target.value = ''
  }
}

const handleAvatarRemove = () => {
  formData.logo_url = ''
}

// ============ 保存 ============
const saveAgent = async () => {
  try {
    const valid = await formRef.value?.validate()
    if (!valid) {
      HMessage.warning('请完善必填信息后再提交')
      return
    }
    loading.value = true

    const requestData = { ...formData }

    if (isEditing.value) {
      const agentId = route.query.id as string
      const updateData = { agent_id: agentId, ...requestData }
      const response = await updateAgentAPI(updateData)
      if (response.data.status_code === 200) {
        HMessage.success('智能体更新成功')
        router.push('/agent')
      } else {
        HMessage.error(response.data.status_message || '更新失败')
      }
    } else {
      const response = await createAgentAPI(requestData)
      if (response.data.status_code === 200) {
        HMessage.success('智能体创建成功')
        router.push('/agent')
      } else {
        HMessage.error(response.data.status_message || '创建失败')
      }
    }
  } catch (error: any) {
    if (error.response?.data?.status_message) {
      HMessage.error(error.response.data.status_message)
    } else if (error.response?.data?.message) {
      HMessage.error(error.response.data.message)
    } else {
      HMessage.error(isEditing.value ? '智能体更新失败' : '智能体创建失败')
    }
  } finally {
    loading.value = false
  }
}

// ============ 返回 ============
const goBack = () => {
  router.push('/agent')
}

// ============ 加载选项 ============
const loadLLMOptions = async () => {
  dataLoading.value.llm = true
  try {
    let response
    try {
      response = await getAgentModelsAPI()
    } catch {
      response = await getVisibleLLMsAPI()
    }
    if (response.data.status_code === 200) {
      const rawData = response.data.data
      let arr: any[] = []
      if (Array.isArray(rawData)) {
        arr = rawData
      } else if (typeof rawData === 'object' && rawData !== null) {
        if (rawData.LLM && Array.isArray(rawData.LLM)) {
          arr = rawData.LLM
        } else {
          arr = Object.values(rawData).flat() as any[]
        }
      }
      llmOptions.value = arr.map(llm => ({
        ...llm,
        name: `${llm.model} (${llm.provider})`
      }))
      if (!isEditing.value && !formData.llm_id && llmOptions.value.length > 0) {
        formData.llm_id = llmOptions.value[0].llm_id
      }
    }
  } catch {
    HMessage.error('加载大模型列表失败')
  } finally {
    dataLoading.value.llm = false
  }
}

const loadToolOptions = async () => {
  dataLoading.value.tool = true
  try {
    const response = await getVisibleToolsAPI()
    if (response.data.status_code === 200) {
      toolOptions.value = response.data.data.map((t: any) => ({
        ...t, name: t.display_name || t.name
      }))
    }
  } catch {
    HMessage.error('加载工具列表失败')
  } finally {
    dataLoading.value.tool = false
  }
}

const loadMCPOptions = async () => {
  dataLoading.value.mcp = true
  try {
    const response = await getMCPServersAPI()
    if (response.data.status_code === 200 && Array.isArray(response.data.data)) {
      mcpOptions.value = response.data.data.map((m: any) => ({
        ...m, name: m.server_name || m.name
      }))
    }
  } catch {
    HMessage.error('加载MCP服务器列表失败')
  } finally {
    dataLoading.value.mcp = false
  }
}

const loadAgentSkillOptions = async () => {
  dataLoading.value.agentSkill = true
  try {
    const response = await getAgentSkillsAPI()
    if (response.data.status_code === 200) {
      agentSkillOptions.value = response.data.data || []
    }
  } catch {
    HMessage.error('加载技能列表失败')
  } finally {
    dataLoading.value.agentSkill = false
  }
}

const loadKnowledgeOptions = async () => {
  dataLoading.value.knowledge = true
  try {
    const response = await getKnowledgeListAPI()
    if (response.data.status_code === 200) {
      knowledgeOptions.value = response.data.data.map((k: any) => ({
        ...k,
        knowledge_id: k.id,
        knowledge_name: k.name,
        name: k.name
      }))
    }
  } catch {
    HMessage.error('加载知识库列表失败')
  } finally {
    dataLoading.value.knowledge = false
  }
}

// ============ 加载智能体数据 ============
const loadAgentFromAPI = async (agentId: string) => {
  try {
    loading.value = true
    const response = await getAgentByIdAPI(agentId)
    if (response.data.status_code === 200 && response.data.data) {
      const d = response.data.data
      isEditing.value = true
      Object.assign(formData, {
        name: d.name || '',
        description: d.description || '',
        logo_url: d.logo_url || '',
        tool_ids: Array.isArray(d.tool_ids) ? d.tool_ids : [],
        llm_id: d.llm_id || '',
        mcp_ids: Array.isArray(d.mcp_ids) ? d.mcp_ids : [],
        system_prompt: d.system_prompt || '',
        knowledge_ids: Array.isArray(d.knowledge_ids) ? d.knowledge_ids : [],
        agent_skill_ids: Array.isArray(d.agent_skill_ids) ? d.agent_skill_ids : [],
        enable_memory: !!d.enable_memory
      })
    } else {
      HMessage.error(response.data.status_message || '智能体不存在')
      goBack()
    }
  } catch {
    HMessage.error('加载智能体数据失败')
    goBack()
  } finally {
    loading.value = false
  }
}

// ============ 初始化 ============
onMounted(async () => {
  await Promise.all([
    loadLLMOptions(),
    loadToolOptions(),
    loadMCPOptions(),
    loadAgentSkillOptions(),
    loadKnowledgeOptions()
  ])

  const agentId = route.query.id as string
  if (agentId) {
    await loadAgentFromAPI(agentId)
  } else {
    if (!formData.llm_id && llmOptions.value.length > 0) {
      formData.llm_id = llmOptions.value[0].llm_id
    }
  }
})
</script>

<template>
  <div class="agent-editor">
    <!-- ===== 页面头部 ===== -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="2" stroke="currentColor" stroke-width="1.5"/>
            <path d="M12 2V5M12 19V22M2 12H5M19 12H22M4.93 4.93L7.05 7.05M16.95 16.95L19.07 19.07M4.93 19.07L7.05 16.95M16.95 7.05L19.07 4.93" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
        </div>
        <div class="header-text">
          <h1 class="header-title">{{ isEditing ? '编辑智能体' : '创建智能体' }}</h1>
          <p class="header-desc">{{ isEditing ? '更新智能体配置信息' : '配置您的专属智能体' }}</p>
        </div>
      </div>
      <div class="header-right">
        <button class="btn-secondary" @click="goBack" :disabled="loading">
          取消
        </button>
        <button class="btn-primary" @click="saveAgent" :disabled="loading">
          <svg v-if="loading" width="14" height="14" viewBox="0 0 14 14" fill="none" class="spinner-sm">
            <circle cx="7" cy="7" r="5" stroke="currentColor" stroke-width="2" stroke-opacity="0.25"/>
            <path d="M7 2A5 5 0 0 1 12 7" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
          <span>{{ isEditing ? '保存更改' : '创建智能体' }}</span>
        </button>
      </div>
    </div>

    <!-- ===== 主内容区 ===== -->
    <div class="page-content">
      <HForm ref="formRef" :model="formData" :rules="rules" label-width="0" class="editor-form">

        <!-- ===== 左栏：基础信息 + 系统提示词 ===== -->
        <div class="column column-left">
          <!-- 基本信息卡片 -->
          <div class="card">
            <div class="card-header">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <rect x="2" y="2" width="12" height="12" rx="2" stroke="currentColor" stroke-width="1.3"/>
                <circle cx="10" cy="6" r="1.5" fill="currentColor"/>
                <path d="M4 10L8 6" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
              </svg>
              <span class="card-title">基本信息</span>
            </div>
            <div class="card-body">
              <!-- 头像 -->
              <div class="avatar-section">
                <div class="avatar-uploader" @click="handleAvatarClick">
                  <img v-if="formData.logo_url" :src="formData.logo_url" class="avatar-preview" />
                  <div v-else class="avatar-placeholder">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                      <rect x="5" y="7" width="14" height="12" rx="2" stroke="currentColor" stroke-width="1.5"/>
                      <circle cx="10" cy="13" r="1.5" fill="currentColor"/>
                      <circle cx="14" cy="13" r="1.5" fill="currentColor"/>
                      <path d="M12 3v4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                      <circle cx="12" cy="3" r="1.5" fill="currentColor"/>
                    </svg>
                    <span>上传头像</span>
                  </div>
                </div>
                <input ref="avatarFileInput" type="file" accept="image/jpeg,image/png" class="hidden-input" @change="handleFileChange" />
                <div class="avatar-meta">
                  <span class="avatar-hint">JPG/PNG，不超过 2MB</span>
                  <button v-if="formData.logo_url" class="avatar-remove" @click="handleAvatarRemove">移除头像</button>
                </div>
              </div>

              <!-- 名称 -->
              <div class="form-row">
                <label class="form-label">
                  <span class="required">*</span>名称
                </label>
                <HInput v-model="formData.name" placeholder="给您的智能体起个名字" class="form-input" />
              </div>

              <!-- 描述 -->
              <div class="form-row">
                <label class="form-label">
                  <span class="required">*</span>描述
                </label>
                <textarea
                  v-model="formData.description"
                  rows="2"
                  placeholder="简短描述这个智能体的作用"
                  class="form-textarea"
                ></textarea>
              </div>
            </div>
          </div>

          <!-- 系统提示词卡片 -->
          <div class="card card-grow">
            <div class="card-header">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <rect x="2" y="2" width="12" height="12" rx="2" stroke="currentColor" stroke-width="1.3"/>
                <path d="M5 6H11M5 8.5H11M5 11H8" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
              </svg>
              <span class="card-title">系统提示词</span>
              <span class="card-subtitle">定义智能体的角色、能力和行为规范</span>
            </div>
            <div class="card-body">
              <textarea
                v-model="formData.system_prompt"
                placeholder="例如：你是一个专业的技术顾问，擅长回答编程相关的问题..."
                class="prompt-textarea"
              ></textarea>
              <div class="prompt-footer">
                <span class="prompt-count">{{ formData.system_prompt.length }} 字符</span>
              </div>
            </div>
          </div>
        </div>

        <!-- ===== 右栏：配置项 ===== -->
        <div class="column column-right">
          <!-- AI模型（始终展开） -->
          <div class="card config-card">
            <div class="card-header collapsible" @click="toggleCollapse('aiModel')">
              <div class="header-group">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="1.3"/>
                  <circle cx="8" cy="8" r="2" fill="currentColor"/>
                </svg>
                <span class="card-title">AI模型</span>
                <HTag type="warning" size="small">核心</HTag>
              </div>
              <svg
                class="chevron"
                :class="{ 'is-open': collapseItems.aiModel }"
                width="14" height="14" viewBox="0 0 14 14" fill="none"
              >
                <path d="M3 5L7 9L11 5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div v-show="collapseItems.aiModel" class="card-body">
              <HFormItem label="" prop="llm_id" class="form-item">
                <HSelect
                  v-model="formData.llm_id"
                  placeholder="选择大语言模型"
                  class="form-select"
                  filterable
                  clearable
                  :loading="dataLoading.llm"
                >
                  <HOption
                    v-for="llm in llmOptions"
                    :key="llm.llm_id"
                    :label="llm.name"
                    :value="llm.llm_id"
                  />
                </HSelect>
              </HFormItem>
            </div>
          </div>

          <!-- 记忆功能 -->
          <div class="card config-card">
            <div class="card-header collapsible" @click="toggleCollapse('memory')">
              <div class="header-group">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <path d="M8 2C5.5 2 3.5 4 3.5 6.5C3.5 9 8 13 8 13C8 13 12.5 9 12.5 6.5C12.5 4 10.5 2 8 2Z" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M8 6V9M6 7.5H10" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
                </svg>
                <span class="card-title">记忆功能</span>
                <HTag :type="formData.enable_memory ? 'success' : 'default'" size="small">
                  {{ formData.enable_memory ? '已开启' : '已关闭' }}
                </HTag>
              </div>
              <svg
                class="chevron"
                :class="{ 'is-open': collapseItems.memory }"
                width="14" height="14" viewBox="0 0 14 14" fill="none"
              >
                <path d="M3 5L7 9L11 5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div v-show="collapseItems.memory" class="card-body">
              <div class="memory-section">
                <button
                  type="button"
                  class="memory-switch"
                  :class="{ active: formData.enable_memory }"
                  @click="formData.enable_memory = !formData.enable_memory"
                >
                  <span class="switch-thumb"></span>
                </button>
                <div class="memory-info">
                  <span class="memory-status">{{ formData.enable_memory ? '长期记忆已开启' : '长期记忆已关闭' }}</span>
                  <span class="memory-desc">
                    {{ formData.enable_memory ? '智能体将记忆对话历史和偏好，提供更连贯的交互体验' : '智能体仅保留当前会话上下文，适合临时任务' }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- 知识库 -->
          <div class="card config-card">
            <div class="card-header collapsible" @click="toggleCollapse('knowledge')">
              <div class="header-group">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <rect x="2" y="2" width="4" height="12" rx="1" stroke="currentColor" stroke-width="1.3"/>
                  <rect x="6" y="2" width="4" height="12" rx="1" stroke="currentColor" stroke-width="1.3"/>
                  <path d="M11 3H12.5C12.78 3 13 3.22 13 3.5V12.5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
                  <path d="M11 13H12.5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
                </svg>
                <span class="card-title">知识库</span>
                <span v-if="formData.knowledge_ids.length > 0" class="count-badge">{{ formData.knowledge_ids.length }}</span>
              </div>
              <svg
                class="chevron"
                :class="{ 'is-open': collapseItems.knowledge }"
                width="14" height="14" viewBox="0 0 14 14" fill="none"
              >
                <path d="M3 5L7 9L11 5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div v-show="collapseItems.knowledge" class="card-body">
              <HFormItem label="" prop="knowledge_ids" class="form-item">
                <HSelect
                  v-model="formData.knowledge_ids"
                  multiple
                  placeholder="选择知识库"
                  class="form-select"
                  :loading="dataLoading.knowledge"
                  filterable
                  clearable
                >
                  <HOption
                    v-for="kb in knowledgeOptions"
                    :key="kb.knowledge_id"
                    :label="kb.name"
                    :value="kb.knowledge_id"
                  />
                </HSelect>
              </HFormItem>
              <p class="option-hint">共 {{ knowledgeOptions.length }} 个知识库可用</p>
            </div>
          </div>

          <!-- 工具 -->
          <div class="card config-card">
            <div class="card-header collapsible" @click="toggleCollapse('tools')">
              <div class="header-group">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <path d="M4 2L14 12L12 14L2 4L4 2Z" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/>
                  <path d="M2 4L6 8M10 12L14 8" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
                </svg>
                <span class="card-title">工具</span>
                <span v-if="formData.tool_ids.length > 0" class="count-badge">{{ formData.tool_ids.length }}</span>
              </div>
              <svg
                class="chevron"
                :class="{ 'is-open': collapseItems.tools }"
                width="14" height="14" viewBox="0 0 14 14" fill="none"
              >
                <path d="M3 5L7 9L11 5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div v-show="collapseItems.tools" class="card-body">
              <HFormItem label="" prop="tool_ids" class="form-item">
                <HSelect
                  v-model="formData.tool_ids"
                  multiple
                  placeholder="选择工具"
                  class="form-select"
                  :loading="dataLoading.tool"
                  filterable
                  clearable
                >
                  <HOption
                    v-for="tool in toolOptions"
                    :key="tool.tool_id"
                    :label="tool.name"
                    :value="tool.tool_id"
                  />
                </HSelect>
              </HFormItem>
              <p class="option-hint">共 {{ toolOptions.length }} 个工具可用</p>
            </div>
          </div>

          <!-- MCP -->
          <div class="card config-card">
            <div class="card-header collapsible" @click="toggleCollapse('mcp')">
              <div class="header-group">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <rect x="2" y="2" width="12" height="12" rx="2" stroke="currentColor" stroke-width="1.3"/>
                  <path d="M5 7H11M8 4V10" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
                </svg>
                <span class="card-title">MCP服务</span>
                <span v-if="formData.mcp_ids.length > 0" class="count-badge">{{ formData.mcp_ids.length }}</span>
              </div>
              <svg
                class="chevron"
                :class="{ 'is-open': collapseItems.mcp }"
                width="14" height="14" viewBox="0 0 14 14" fill="none"
              >
                <path d="M3 5L7 9L11 5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div v-show="collapseItems.mcp" class="card-body">
              <HFormItem label="" prop="mcp_ids" class="form-item">
                <HSelect
                  v-model="formData.mcp_ids"
                  multiple
                  placeholder="选择MCP服务器"
                  class="form-select"
                  :loading="dataLoading.mcp"
                  filterable
                  clearable
                >
                  <HOption
                    v-for="mcp in mcpOptions"
                    :key="mcp.mcp_server_id"
                    :label="mcp.name"
                    :value="mcp.mcp_server_id"
                  />
                </HSelect>
              </HFormItem>
              <p class="option-hint">共 {{ mcpOptions.length }} 个MCP服务可用</p>
            </div>
          </div>

          <!-- 技能 -->
          <div class="card config-card">
            <div class="card-header collapsible" @click="toggleCollapse('skills')">
              <div class="header-group">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <path d="M8 1L9.5 5L14 5.5L10.5 8.5L11.5 13L8 11L4.5 13L5.5 8.5L2 5.5L6.5 5L8 1Z" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/>
                </svg>
                <span class="card-title">技能</span>
                <span v-if="formData.agent_skill_ids.length > 0" class="count-badge">{{ formData.agent_skill_ids.length }}</span>
              </div>
              <svg
                class="chevron"
                :class="{ 'is-open': collapseItems.skills }"
                width="14" height="14" viewBox="0 0 14 14" fill="none"
              >
                <path d="M3 5L7 9L11 5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div v-show="collapseItems.skills" class="card-body">
              <HFormItem label="" prop="agent_skill_ids" class="form-item">
                <HSelect
                  v-model="formData.agent_skill_ids"
                  multiple
                  placeholder="选择技能"
                  class="form-select"
                  :loading="dataLoading.agentSkill"
                  filterable
                  clearable
                >
                  <HOption
                    v-for="skill in agentSkillOptions"
                    :key="skill.id"
                    :label="skill.name"
                    :value="skill.id"
                  />
                </HSelect>
              </HFormItem>
              <p class="option-hint">共 {{ agentSkillOptions.length }} 个技能可用</p>
            </div>
          </div>
        </div>
      </HForm>
    </div>
  </div>
</template>

<style lang="scss" scoped>
/* ============ 页面容器 ============ */
.agent-editor {
  min-height: 100vh;
  background: var(--harmony-comp-background-secondary);
  display: flex;
  flex-direction: column;
}

/* ============ 页面头部 ============ */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 32px;
  background: var(--harmony-comp-background-primary);
  border-bottom: 1px solid var(--harmony-comp-divider);
  position: sticky;
  top: 0;
  z-index: 10;
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
    font-size: 18px;
    font-weight: 600;
    color: var(--harmony-font-primary);
    margin: 0;
    letter-spacing: -0.2px;
  }
  .header-desc {
    font-size: 12px;
    color: var(--harmony-font-tertiary);
    margin: 2px 0 0 0;
  }
}

.header-right {
  display: flex;
  gap: 10px;
}

.btn-secondary {
  padding: 9px 18px;
  background: var(--harmony-comp-background-primary);
  border: 1px solid var(--harmony-comp-divider);
  color: var(--harmony-font-secondary);
  border-radius: var(--harmony-corner-radius-level6);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  font-family: inherit;

  &:hover:not(:disabled) {
    border-color: var(--harmony-brand);
    color: var(--harmony-brand);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 9px 18px;
  background: var(--harmony-brand);
  border: none;
  color: white;
  border-radius: var(--harmony-corner-radius-level6);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  font-family: inherit;

  &:hover:not(:disabled) {
    box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
    transform: translateY(-1px);
  }

  &:disabled {
    opacity: 0.7;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
  }
}

.spinner-sm {
  animation: h-spin 1s linear infinite;
}


}

/* ============ 主内容区 ============ */
.page-content {
  flex: 1;
  padding: 24px 32px 32px;
  overflow-x: hidden;
}

.editor-form {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.column {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.column-left {
  width: 45%;
  position: sticky;
  top: 92px;
}

.column-right {
  flex: 1;
  min-width: 0;
}

/* ============ 卡片 ============ */
.card {
  background: var(--harmony-comp-background-primary);
  border: 1px solid var(--harmony-comp-divider);
  border-radius: var(--harmony-corner-radius-level8);
  overflow: hidden;
  transition: border-color 0.15s ease;

  &:hover {
    border-color: rgba(99, 102, 241, 0.3);
  }

  &.card-grow {
    flex: 1;
    min-height: 300px;
    display: flex;
    flex-direction: column;
  }
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 16px 20px;
  background: var(--harmony-comp-background-primary);
  border-bottom: 1px solid var(--harmony-comp-divider);

  .card-title {
    font-size: 14px;
    font-weight: 600;
    color: var(--harmony-font-primary);
  }

  .card-subtitle {
    font-size: 12px;
    color: var(--harmony-font-tertiary);
    margin-left: auto;
  }

  &.collapsible {
    cursor: pointer;
    user-select: none;
    border-bottom: none;

    &:hover {
      background: var(--harmony-comp-background-secondary);
    }

    .chevron {
      margin-left: auto;
      color: var(--harmony-font-tertiary);
      transition: transform 0.2s ease;

      &.is-open {
        transform: rotate(180deg);
      }
    }
  }

  .header-group {
    display: flex;
    align-items: center;
    gap: 8px;
  }
}

.count-badge {
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  background: var(--harmony-comp-emphasize-tertiary);
  color: var(--harmony-brand);
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-body {
  padding: 20px;

  & > * + * {
    margin-top: 16px;
  }
}

/* ============ 头像区 ============ */
.avatar-section {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--harmony-comp-divider);
}

.avatar-uploader {
  width: 72px;
  height: 72px;
  border-radius: var(--harmony-corner-radius-level6);
  background: var(--harmony-comp-background-secondary);
  border: 2px dashed var(--harmony-comp-divider);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.15s ease;
  flex-shrink: 0;

  &:hover {
    border-color: var(--harmony-brand);
    background: var(--harmony-comp-emphasize-tertiary);
    color: var(--harmony-brand);
  }

  .avatar-preview {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .avatar-placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    color: var(--harmony-font-tertiary);

    svg {
      opacity: 0.7;
    }

    span {
      font-size: 11px;
      font-weight: 500;
    }
  }
}

.hidden-input {
  display: none;
}

.avatar-meta {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.avatar-hint {
  font-size: 12px;
  color: var(--harmony-font-tertiary);
}

.avatar-remove {
  font-size: 12px;
  color: var(--harmony-warning);
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
  font-family: inherit;
  text-align: left;

  &:hover {
    text-decoration: underline;
  }
}

/* ============ 表单行 ============ */
.form-row {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-size: 12px;
  font-weight: 500;
  color: var(--harmony-font-secondary);

  .required {
    color: var(--harmony-warning);
    margin-right: 2px;
  }
}

.form-input {
  :deep(.h-input__inner) {
    height: 40px !important;
    border-radius: var(--harmony-corner-radius-level6) !important;
    border: 1px solid var(--harmony-comp-divider) !important;
    background: var(--harmony-comp-background-secondary) !important;
    padding: 0 14px !important;
    font-size: 13px !important;
    transition: all 0.15s ease !important;
  }

  :deep(.h-input__inner:hover) {
    border-color: rgba(99, 102, 241, 0.4) !important;
  }

  :deep(.h-input__inner:focus) {
    border-color: var(--harmony-brand) !important;
    background: var(--harmony-comp-background-primary) !important;
    box-shadow: 0 0 0 3px var(--harmony-comp-emphasize-tertiary) !important;
  }
}

.form-textarea {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid var(--harmony-comp-divider);
  border-radius: var(--harmony-corner-radius-level6);
  background: var(--harmony-comp-background-secondary);
  font-size: 13px;
  color: var(--harmony-font-primary);
  font-family: inherit;
  line-height: 1.6;
  resize: vertical;
  transition: all 0.15s ease;

  &:hover {
    border-color: rgba(99, 102, 241, 0.4);
  }

  &:focus {
    border-color: var(--harmony-brand);
    background: var(--harmony-comp-background-primary);
    box-shadow: 0 0 0 3px var(--harmony-comp-emphasize-tertiary);
  }

  &::placeholder {
    color: var(--harmony-font-tertiary);
  }
}

/* ============ 系统提示词 ============ */
.prompt-textarea {
  width: 100%;
  min-height: 260px;
  padding: 16px;
  border: 1px solid var(--harmony-comp-divider);
  border-radius: var(--harmony-corner-radius-level6);
  background: var(--harmony-comp-background-secondary);
  font-size: 13px;
  color: var(--harmony-font-primary);
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  line-height: 1.7;
  resize: vertical;
  transition: all 0.15s ease;

  &:hover {
    border-color: rgba(99, 102, 241, 0.4);
  }

  &:focus {
    border-color: var(--harmony-brand);
    background: var(--harmony-comp-background-primary);
    box-shadow: 0 0 0 3px var(--harmony-comp-emphasize-tertiary);
  }

  &::placeholder {
    color: var(--harmony-font-tertiary);
    font-family: inherit;
  }
}

.prompt-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 8px;
}

.prompt-count {
  font-size: 11px;
  color: var(--harmony-font-tertiary);
}

/* ============ 配置卡中的表单 ============ */
.form-item {
  margin: 0 !important;
}

.form-select {
  :deep(.h-select__input) {
    min-height: 40px !important;
    border-radius: var(--harmony-corner-radius-level6) !important;
    border: 1px solid var(--harmony-comp-divider) !important;
    background: var(--harmony-comp-background-secondary) !important;
    padding: 4px 14px !important;
    font-size: 13px !important;
  }

  :deep(.h-select__input:hover) {
    border-color: rgba(99, 102, 241, 0.4) !important;
  }

  :deep(.h-select__input.is-focus) {
    border-color: var(--harmony-brand) !important;
    background: var(--harmony-comp-background-primary) !important;
    box-shadow: 0 0 0 3px var(--harmony-comp-emphasize-tertiary) !important;
  }
}

.option-hint {
  margin: 8px 0 0 0 !important;
  font-size: 11px;
  color: var(--harmony-font-tertiary);
}

/* ============ 记忆开关 ============ */
.memory-section {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.memory-switch {
  position: relative;
  width: 44px;
  height: 26px;
  border: none;
  border-radius: 13px;
  background: var(--harmony-comp-divider);
  cursor: pointer;
  transition: background 0.2s ease;
  padding: 0;
  flex-shrink: 0;
  margin-top: 2px;

  &.active {
    background: var(--harmony-brand);

    .switch-thumb {
      transform: translateX(18px);
    }
  }

  .switch-thumb {
    position: absolute;
    top: 3px;
    left: 3px;
    width: 20px;
    height: 20px;
    background: white;
    border-radius: 50%;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
    transition: transform 0.2s ease;
  }
}

.memory-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.memory-status {
  font-size: 13px;
  font-weight: 500;
  color: var(--harmony-font-primary);
}

.memory-desc {
  font-size: 12px;
  color: var(--harmony-font-tertiary);
  line-height: 1.5;
}

/* ============ 响应式 ============ */
@media (max-width: 1100px) {
  .editor-form {
    flex-direction: column;
  }

  .column-left {
    width: 100%;
    position: static;
  }

  .column-right {
    width: 100%;
  }
}

@media (max-width: 768px) {
  .page-header {
    padding: 16px;
    flex-wrap: wrap;
    gap: 12px;
  }

  .page-content {
    padding: 16px;
  }

  .header-right {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>

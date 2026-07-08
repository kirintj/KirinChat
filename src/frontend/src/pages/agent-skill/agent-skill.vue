<script setup lang="ts">
import { ref, inject, onMounted, computed, nextTick, reactive } from 'vue'
import { HMessage, HButton, HTooltip, HForm, HFormItem, HInput, HSelect, HOption, HIcon } from '@/components/ui'
import * as monaco from 'monaco-editor'
import { 
  getAgentSkillsAPI, 
  createAgentSkillAPI, 
  deleteAgentSkillAPI,
  updateAgentSkillFileAPI,
  addAgentSkillFileAPI,
  deleteAgentSkillFileAPI,
  type AgentSkill,
  type AgentSkillFile,
  type AgentSkillFolder
} from '../../apis/agent-skill'

// Monaco 编辑器实例
const isMobile = inject<import('vue').Ref<boolean>>('isMobile', ref(false))
let monacoEditor: monaco.editor.IStandaloneCodeEditor | null = null

// 响应式数据
const skills = ref<AgentSkill[]>([])
const loading = ref(false)
const showCreateDialog = ref(false)
const showDetailDialog = ref(false)
const currentSkill = ref<AgentSkill | null>(null)
const selectedFile = ref<AgentSkillFile | null>(null)
const fileContent = ref('')
const editMode = ref(false)
const showAddFileDialog = ref(false)
const savingFile = ref(false)

// 手写确认弹窗（替代 HMessageBox / window.confirm）
type ConfirmDialogOptions = {
  title?: string
  message: string
  confirmText?: string
  cancelText?: string
  variant?: 'default' | 'danger'
}

const confirmDialog = reactive({
  visible: false,
  title: '确认',
  message: '',
  confirmText: '确定',
  cancelText: '取消',
  variant: 'default' as 'default' | 'danger',
  resolve: null as null | ((ok: boolean) => void),
})

const openConfirmDialog = (options: ConfirmDialogOptions) => {
  confirmDialog.title = options.title ?? '确认'
  confirmDialog.message = options.message
  confirmDialog.confirmText = options.confirmText ?? '确定'
  confirmDialog.cancelText = options.cancelText ?? '取消'
  confirmDialog.variant = options.variant ?? 'default'
  confirmDialog.visible = true

  return new Promise<boolean>((resolve) => {
    confirmDialog.resolve = resolve
  })
}

const closeConfirmDialog = (ok: boolean) => {
  confirmDialog.visible = false
  const r = confirmDialog.resolve
  confirmDialog.resolve = null
  r?.(ok)
}
// 表单数据
const createForm = ref({
  name: '',
  description: ''
})

const addFileForm = ref({
  path: '',
  name: ''
})

// 表单验证规则
const createFormRules = {
  name: [
    { required: true, message: '请输入 Skill 名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入 Skill 描述', trigger: 'blur' },
    { max: 500, message: '描述不能超过 500 个字符', trigger: 'blur' }
  ]
}

// 获取文件数量
const getFileCount = (skill: AgentSkill) => {
  if (!skill.folder?.folder) return 0
  let count = 0
  const countFiles = (items: any[]) => {
    items.forEach(item => {
      if (item.type === 'file') count++
      if (item.folder) countFiles(item.folder)
    })
  }
  countFiles(skill.folder.folder)
  return count
}

// 获取 Skill 列表
const fetchSkills = async () => {
  loading.value = true
  try {
    const response = await getAgentSkillsAPI()
    if (response.data.status_code === 200) {
      skills.value = response.data.data || []
    } else {
      HMessage.error(response.data.status_message || '获取 Skill 列表失败')
    }
  } catch (error) {
    console.error('获取 Skill 列表失败:', error)
    HMessage.error('获取 Skill 列表失败')
  } finally {
    loading.value = false
  }
}

// 创建 Skill
const handleCreateSkill = async () => {
  if (!createForm.value.name || !createForm.value.description) {
    HMessage.warning('请填写完整信息')
    return
  }
  
  try {
    const response = await createAgentSkillAPI(createForm.value)
    if (response.data.status_code === 200) {
      HMessage.success('Skill 创建成功')
      showCreateDialog.value = false
      resetCreateForm()
      fetchSkills()
    } else {
      HMessage.error(response.data.status_message || '创建 Skill 失败')
    }
  } catch (error) {
    console.error('创建 Skill 失败:', error)
    HMessage.error('创建 Skill 失败')
  }
}

// 删除 Skill
const handleDeleteSkill = async (skill: AgentSkill, event?: Event) => {
  event?.stopPropagation()
  const confirmed = await openConfirmDialog({
    title: '确认删除',
    message: `确定要删除 Skill "${skill.name}" 吗？此操作不可恢复。`,
    confirmText: '确定删除',
    cancelText: '取消',
    variant: 'danger',
  })
  if (!confirmed) return

  try {
    const response = await deleteAgentSkillAPI({ agent_skill_id: skill.id })
    if (response.data.status_code === 200) {
      HMessage.success('Skill 删除成功')
      fetchSkills()
    } else {
      HMessage.error(response.data.status_message || '删除 Skill 失败')
    }
  } catch (error) {
    console.error('删除 Skill 失败:', error)
    HMessage.error('删除 Skill 失败')
  }
}

// 打开详情弹窗
const openDetailDialog = (skill: AgentSkill) => {
  currentSkill.value = skill
  selectedFile.value = null
  fileContent.value = ''
  editMode.value = false
  showDetailDialog.value = true
  document.body.style.overflow = 'hidden'
}

// 关闭详情弹窗
const closeDetailDialog = () => {
  showDetailDialog.value = false
  currentSkill.value = null
  selectedFile.value = null
  fileContent.value = ''
  editMode.value = false
  document.body.style.overflow = 'auto'
  
  // 销毁编辑器
  if (monacoEditor) {
    monacoEditor.dispose()
    monacoEditor = null
  }
}

// 初始化 Monaco 编辑器
const initMonacoEditor = () => {
  nextTick(() => {
    const container = document.getElementById('skill-monaco-editor')
    if (container && !monacoEditor) {
      monacoEditor = monaco.editor.create(container, {
        value: fileContent.value,
        language: getFileLanguage(selectedFile.value?.name || ''),
        theme: 'vs',
        automaticLayout: true,
        minimap: { enabled: false },
        lineNumbers: 'on',
        roundedSelection: true,
        scrollBeyondLastLine: false,
        fontSize: 14,
        tabSize: 2,
        renderLineHighlight: 'all',
        padding: { top: 16, bottom: 16 },
        scrollbar: {
          vertical: 'auto',
          horizontal: 'auto',
        }
      })
    } else if (monacoEditor) {
      monacoEditor.setValue(fileContent.value)
      monaco.editor.setModelLanguage(
        monacoEditor.getModel()!,
        getFileLanguage(selectedFile.value?.name || '')
      )
    }
  })
}

// 获取文件语言
const getFileLanguage = (filename: string) => {
  const ext = filename.split('.').pop()?.toLowerCase()
  const languageMap: Record<string, string> = {
    'py': 'python',
    'js': 'javascript',
    'ts': 'typescript',
    'json': 'json',
    'md': 'markdown',
    'yaml': 'yaml',
    'yml': 'yaml',
    'html': 'html',
    'css': 'css',
    'sh': 'shell',
    'bash': 'shell',
    'txt': 'plaintext'
  }
  return languageMap[ext || ''] || 'plaintext'
}

// 判断是否可以删除文件（只有 scripts 和 reference 目录下的文件可以删除）
const canDeleteFile = (file: AgentSkillFile, parentPath: string) => {
  // 根目录的文件（如 SKILL.md）不能删除
  if (parentPath === currentSkill.value?.folder?.path) {
    return false
  }
  // scripts 和 reference 目录下的文件可以删除
  return parentPath.includes('/scripts') || parentPath.includes('/reference')
}

// 判断文件夹是否可以添加文件（只有 scripts 和 reference 可以）
const canAddToFolder = (folderName: string) => {
  return folderName === 'scripts' || folderName === 'reference'
}

// 获取可添加文件的目录列表
const getAddableFolders = computed(() => {
  if (!currentSkill.value?.folder?.folder) return []
  return currentSkill.value.folder.folder.filter(
    item => item.type === 'folder' && canAddToFolder(item.name)
  )
})

// 选择文件
const selectFile = (file: AgentSkillFile) => {
  selectedFile.value = file
  fileContent.value = file.content
  editMode.value = false
  
  // 销毁旧编辑器
  if (monacoEditor) {
    monacoEditor.dispose()
    monacoEditor = null
  }
}

// 进入编辑模式
const enterEditMode = () => {
  editMode.value = true
  nextTick(() => {
    initMonacoEditor()
  })
}

// 取消编辑
const cancelEdit = () => {
  editMode.value = false
  fileContent.value = selectedFile.value?.content || ''
  if (monacoEditor) {
    monacoEditor.dispose()
    monacoEditor = null
  }
}

// 保存文件内容
const saveFileContent = async () => {
  if (!currentSkill.value || !selectedFile.value) return
  
  savingFile.value = true
  try {
    const content = monacoEditor ? monacoEditor.getValue() : fileContent.value
    const response = await updateAgentSkillFileAPI({
      agent_skill_id: currentSkill.value.id,
      path: selectedFile.value.path,
      content: content
    })
    
    if (response.data.status_code === 200) {
      HMessage.success('文件保存成功')
      editMode.value = false
      fileContent.value = content
      if (selectedFile.value) {
        selectedFile.value.content = content
      }
      currentSkill.value = response.data.data
      fetchSkills()
      
      if (monacoEditor) {
        monacoEditor.dispose()
        monacoEditor = null
      }
    } else {
      HMessage.error(response.data.status_message || '保存失败')
    }
  } catch (error) {
    console.error('保存文件失败:', error)
    HMessage.error('保存文件失败')
  } finally {
    savingFile.value = false
  }
}

// 关闭添加文件对话框
const closeAddFileDialog = () => {
  showAddFileDialog.value = false
  addFileForm.value = { path: '', name: '' }
}

// 添加文件
const addingFile = ref(false)
const handleAddFile = async () => {
  if (!currentSkill.value) {
    HMessage.warning('请先选择一个 Skill')
    return
  }
  
  if (!addFileForm.value.path) {
    HMessage.warning('请选择目标目录')
    return
  }
  
  if (!addFileForm.value.name) {
    HMessage.warning('请输入文件名称')
    return
  }
  
  addingFile.value = true
  try {
    const response = await addAgentSkillFileAPI({
      agent_skill_id: currentSkill.value.id,
      path: addFileForm.value.path,
      name: addFileForm.value.name
    })

    if (response.data.status_code === 200) {
      HMessage.success('文件添加成功')
      closeAddFileDialog()
      currentSkill.value = response.data.data
      fetchSkills()
    } else {
      HMessage.error(response.data.status_message || '添加文件失败')
    }
  } catch (error: any) {
    console.error('添加文件失败:', error)
    HMessage.error(error?.response?.data?.status_message || error?.message || '添加文件失败')
  } finally {
    addingFile.value = false
  }
}

// 删除文件
const handleDeleteFile = async (file: AgentSkillFile, parentPath: string) => {
  if (!currentSkill.value) return
  const confirmed = await openConfirmDialog({
    title: '确认删除',
    message: `确定要删除文件 "${file.name}" 吗？`,
    confirmText: '确定删除',
    cancelText: '取消',
    variant: 'danger',
  })
  if (!confirmed) return
  
  try {
    const response = await deleteAgentSkillFileAPI({
      agent_skill_id: currentSkill.value.id,
      path: parentPath,
      name: file.name
    })
    
    if (response.data.status_code === 200) {
      HMessage.success('文件删除成功')
      currentSkill.value = response.data.data
      if (selectedFile.value?.path === file.path) {
        selectedFile.value = null
        fileContent.value = ''
      }
      fetchSkills()
    } else {
      HMessage.error(response.data.status_message || '删除文件失败')
    }
  } catch (error) {
    console.error('删除文件失败:', error)
    HMessage.error('删除文件失败')
  }
}

// 重置创建表单
const resetCreateForm = () => {
  createForm.value = {
    name: '',
    description: ''
  }
}

// 刷新数据
const handleRefresh = () => {
  fetchSkills()
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
  fetchSkills()
})
</script>

<template>
  <div class="skill-page" v-if="!isMobile">
    <!-- 页面头部 - 增强设计 -->
    <div class="page-header">
      <div class="header-title">
        <h2>Agent Skill</h2>
      </div>
      <div class="header-actions">
        <HButton
          @click="handleRefresh"
          :loading="loading"
          class="refresh-btn"
          type="secondary"
        >
          &#x21BB; 刷新
        </HButton>
        <HButton
          type="primary"
          @click="showCreateDialog = true"
          class="create-btn"
        >
          + 创建 Skill
        </HButton>
      </div>
    </div>

    <!-- Skill 列表 -->
    <div class="skill-container" v-h-loading="loading">
      <!-- 列表头部 -->
      <div class="list-header" v-if="skills.length > 0">
        <div class="col-name">名称</div>
        <div class="col-desc">描述</div>
        <div class="col-files">文件数</div>
        <div class="col-time">创建时间</div>
        <div class="col-actions">操作</div>
      </div>
      
      <!-- 列表内容 -->
      <div class="skill-list" v-if="skills.length > 0">
        <div 
          v-for="(skill, index) in skills" 
          :key="skill.id" 
          class="skill-row"
          @click="openDetailDialog(skill)"
        >
          <div class="col-name">
            <div class="skill-info">
              <div class="skill-avatar">
                <HIcon svg="skill" :size="20" />
              </div>
              <span class="skill-name">{{ skill.name }}</span>
            </div>
          </div>
          <div class="col-desc">
            <span class="skill-desc">{{ skill.description }}</span>
          </div>
          <div class="col-files">
            <span class="file-badge">
              &#128196; {{ getFileCount(skill) }}
            </span>
          </div>
          <div class="col-time">
            <span class="time-text">{{ formatRelativeTime(skill.create_time) }}</span>
          </div>
          <div class="col-actions" @click.stop>
            <HTooltip content="查看详情" placement="top">
              <button class="action-btn view-btn" @click="openDetailDialog(skill)">
                &#128065;
              </button>
            </HTooltip>
            <HTooltip content="删除" placement="top">
              <button class="action-btn delete-btn" @click="handleDeleteSkill(skill, $event)">
                &#128465;
              </button>
            </HTooltip>
          </div>
        </div>
      </div>
      
      <!-- 空状态 -->
      <div v-if="skills.length === 0 && !loading" class="empty-state">
        <div class="empty-visual">
          <div class="empty-icon-wrapper">
            <HIcon svg="skill" :size="48" class="empty-icon" />
          </div>
        </div>
        <div class="empty-content">
          <h3>还没有创建任何 Skill</h3>
          <p>Agent Skill 可以让智能体拥有更专业的能力，开始创建你的第一个 Skill 吧！</p>
          <HButton
            type="primary"
            @click="showCreateDialog = true"
            class="empty-btn"
          >
            + 创建第一个 Skill
          </HButton>
        </div>
      </div>
    </div>

    <!-- 创建 Skill 对话框 - 增强设计 (desktop only) -->
    <Teleport to="body">
      <div v-if="!isMobile && showCreateDialog" class="modal-overlay create-modal" @click.self="showCreateDialog = false">
        <div class="modal-dialog create-dialog">
          <div class="dialog-header">
            <div class="dialog-icon">
              <HIcon svg="skill" :size="20" />
            </div>
            <div class="dialog-title-wrapper">
              <h3>创建新 Skill</h3>
              <p>为智能体添加一项新的专业技能</p>
            </div>
            <button class="close-btn" @click="showCreateDialog = false">
              &#10005;
            </button>
          </div>

          <div class="dialog-body">
            <div class="form-tip">
              <div class="tip-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z" stroke="#1B7CE4" stroke-width="2"/>
                  <path d="M12 16v-4M12 8h.01" stroke="#1B7CE4" stroke-width="2" stroke-linecap="round"/>
                </svg>
              </div>
              <p>Skill 包含一组预定义的文件和脚本，用于赋予智能体特定的专业能力</p>
            </div>

            <HForm class="create-form">
              <HFormItem label="Skill 名称">
                <HInput
                  v-model="createForm.name"
                  placeholder="例如：数据分析专家、代码审查助手"
                />
              </HFormItem>

              <HFormItem label="Skill 描述">
                <textarea
                  v-model="createForm.description"
                  :rows="4"
                  placeholder="详细描述这个 Skill 的功能、适用场景和特点..."
                  class="skill-textarea"
                ></textarea>
              </HFormItem>
            </HForm>
          </div>

          <div class="dialog-footer">
            <HButton @click="showCreateDialog = false" size="large" type="secondary">取消</HButton>
            <HButton type="primary" @click="handleCreateSkill" size="large">
              + 创建 Skill
            </HButton>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Skill 详情对话框 - 代码编辑器风格 (desktop only) -->
    <Teleport to="body">
      <div v-if="!isMobile && showDetailDialog" class="modal-overlay detail-modal" @click.self="closeDetailDialog">
        <div class="modal-dialog detail-dialog">
          <!-- IDE 风格头部 -->
          <div class="ide-header">
            <div class="ide-tabs">
              <div class="ide-tab active">
                <HIcon svg="skill" :size="16" class="tab-icon" />
                <span class="tab-name">{{ currentSkill?.name }}</span>
              </div>
            </div>
            <div class="ide-actions">
              <button class="ide-btn" @click="closeDetailDialog">
                &#10005;
              </button>
            </div>
          </div>
          
          <!-- IDE 内容区 -->
          <div class="ide-body">
            <!-- 侧边栏 - 文件资源管理器 -->
            <div class="ide-sidebar">
              <div class="sidebar-header">
                <span class="sidebar-title">资源管理器</span>
                <HTooltip content="只能在 scripts 或 reference 目录下添加文件" placement="bottom">
                  <span class="sidebar-hint">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                      <path d="M12 16v-4M12 8h.01" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                  </span>
                </HTooltip>
              </div>
              
              <div class="file-explorer">
                <template v-if="currentSkill?.folder">
                  <!-- 项目根目录 -->
                  <div class="explorer-item project-root">
                    <span class="item-icon folder-icon">&#128193;</span>
                    <span class="item-name">{{ currentSkill.folder.name }}</span>
                  </div>
                  
                  <!-- 文件和文件夹 -->
                  <div class="explorer-tree">
                    <template v-for="item in currentSkill.folder.folder" :key="item.path">
                      <!-- 根目录文件（如 SKILL.md）- 只能查看编辑，不能删除 -->
                      <div
                        v-if="item.type === 'file'"
                        class="explorer-item file-item"
                        :class="{ active: selectedFile?.path === item.path }"
                        @click="selectFile(item as AgentSkillFile)"
                      >
                        <span class="item-icon file-icon">&#128196;</span>
                        <span class="item-name">{{ item.name }}</span>
                        <span class="item-badge readonly">只读</span>
                      </div>
                      
                      <!-- 文件夹（scripts / reference） -->
                      <template v-else>
                        <div class="explorer-item folder-item" :class="{ 'can-add': canAddToFolder(item.name) }">
                          <span class="item-icon folder-icon">&#128193;</span>
                          <span class="item-name">{{ item.name }}</span>
                          <!-- 只有 scripts 和 reference 可以添加文件 -->
                          <HTooltip v-if="canAddToFolder(item.name)" content="添加文件" placement="right">
                            <button
                              class="item-add"
                              @click.stop="addFileForm.path = item.path; showAddFileDialog = true"
                            >
                              +
                            </button>
                          </HTooltip>
                        </div>
                        
                        <!-- 子文件 - 可以增删改 -->
                        <div
                          v-for="subItem in (item as AgentSkillFolder).folder"
                          :key="subItem.path"
                          class="explorer-item file-item nested"
                          :class="{ active: selectedFile?.path === subItem.path }"
                          @click="selectFile(subItem as AgentSkillFile)"
                        >
                          <span class="item-icon file-icon">&#128196;</span>
                          <span class="item-name">{{ subItem.name }}</span>
                          <button
                            v-if="canDeleteFile(subItem as AgentSkillFile, item.path)"
                            class="item-delete"
                            @click.stop="handleDeleteFile(subItem as AgentSkillFile, item.path)"
                          >
                            &#128465;
                          </button>
                        </div>
                        
                        <!-- 空文件夹提示 -->
                        <div 
                          v-if="!(item as AgentSkillFolder).folder?.length && canAddToFolder(item.name)"
                          class="explorer-item empty-hint nested"
                        >
                          <span>暂无文件，点击 + 添加</span>
                        </div>
                      </template>
                    </template>
                  </div>
                </template>
              </div>
              
              <!-- Skill 信息面板 -->
              <div class="skill-info-panel">
                <h4>Skill 信息</h4>
                <p class="info-desc">{{ currentSkill?.description }}</p>
                <div class="info-meta">
                  <span>
                    &#128336; 创建于 {{ formatTime(currentSkill?.create_time) }}
                  </span>
                </div>
              </div>
            </div>
            
            <!-- 主内容区 - 代码编辑器 -->
            <div class="ide-main">
              <template v-if="selectedFile">
                <!-- 编辑器标签栏 -->
                <div class="editor-tabs">
                  <div class="editor-tab active">
                    &#128196;
                    <span>{{ selectedFile.name }}</span>
                  </div>
                  <div class="editor-actions">
                    <template v-if="!editMode">
                      <HButton
                        class="editor-btn editor-btn--ghost"
                        size="small"
                        @click="enterEditMode"
                        type="secondary"
                      >
                        &#9998; 编辑文件
                      </HButton>
                    </template>
                    <template v-else>
                      <HButton
                        class="editor-btn editor-btn--cancel"
                        size="small"
                        @click="cancelEdit"
                        type="secondary"
                      >
                        取消
                      </HButton>
                      <HButton
                        class="editor-btn editor-btn--primary"
                        size="small"
                        @click="saveFileContent"
                        :loading="savingFile"
                        type="primary"
                      >
                        保存更改
                      </HButton>
                    </template>
                  </div>
                </div>
                
                <!-- 代码内容 -->
                <div class="editor-content">
                  <div v-if="editMode" id="skill-monaco-editor" class="monaco-container"></div>
                  <pre v-else class="code-preview"><code>{{ fileContent }}</code></pre>
                </div>
              </template>
              
              <!-- 无文件选中状态 -->
              <div v-else class="no-file-state">
                <div class="no-file-visual">
                  <span class="no-file-icon">&#128196;</span>
                </div>
                <h3>选择一个文件开始编辑</h3>
                <p>从左侧文件资源管理器中选择文件，或创建新文件</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 添加文件对话框 - 使用 Teleport 确保显示在最上层 (desktop only) -->
    <Teleport to="body">
      <div v-if="!isMobile && showAddFileDialog" class="modal-overlay add-file-modal" @click.self="closeAddFileDialog">
        <div class="modal-dialog add-file-dialog">
          <div class="dialog-header">
            <div class="dialog-icon add-icon">
              &#128196;
            </div>
            <div class="dialog-title-wrapper">
              <h3>新建文件</h3>
              <p>在 {{ addFileForm.path || '选择的目录' }} 中创建新文件</p>
            </div>
            <button class="close-btn" @click="closeAddFileDialog">
              &#10005;
            </button>
          </div>

          <div class="dialog-body">
            <div class="add-file-tip">
              &#128196;
              <span>文件只能添加到 <strong>scripts</strong> 或 <strong>reference</strong> 目录下</span>
            </div>

            <div class="form-group">
              <label>目标目录</label>
              <HSelect v-model="addFileForm.path" placeholder="选择文件存放目录" style="width: 100%">
                <template v-if="currentSkill?.folder?.folder">
                  <HOption
                    v-for="item in getAddableFolders"
                    :key="item.path"
                    :value="item.path"
                    :label="item.name"
                  />
                </template>
              </HSelect>
            </div>

            <div class="form-group">
              <label>文件名称</label>
              <HInput
                v-model="addFileForm.name"
                placeholder="例如：my_script.py, data.json, README.md"
                size="large"
                @keyup.enter="handleAddFile"
              />
              <div class="file-name-hint">
                支持的文件类型：.py, .js, .ts, .json, .md, .yaml, .sh 等
              </div>
            </div>
          </div>

          <div class="dialog-footer">
            <HButton @click="closeAddFileDialog" size="large" type="secondary">取消</HButton>
            <HButton
              type="primary"
              @click="handleAddFile"
              :disabled="!addFileForm.path || !addFileForm.name"
              :loading="addingFile"
              size="large"
            >
              {{ addingFile ? '创建中...' : '创建文件' }}
            </HButton>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 手写确认弹窗（Element 风格，但不依赖 Element 组件）(desktop only) -->
    <Teleport to="body">
      <div
        v-if="!isMobile && confirmDialog.visible"
        class="modal-overlay confirm-modal"
        @click.self="closeConfirmDialog(false)"
      >
        <div class="modal-dialog confirm-dialog" role="dialog" aria-modal="true">
          <div class="dialog-header">
            <div class="dialog-title">{{ confirmDialog.title }}</div>
            <button class="dialog-close" type="button" @click="closeConfirmDialog(false)" aria-label="关闭">
              ×
            </button>
          </div>
          <div class="dialog-body">
            <p class="dialog-message">{{ confirmDialog.message }}</p>
          </div>
          <div class="dialog-footer">
            <button class="btn btn-default" type="button" @click="closeConfirmDialog(false)">
              {{ confirmDialog.cancelText }}
            </button>
            <button
              class="btn"
              :class="confirmDialog.variant === 'danger' ? 'btn-danger' : 'btn-primary'"
              type="button"
              @click="closeConfirmDialog(true)"
            >
              {{ confirmDialog.confirmText }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>

  <div v-else class="skill-mobile">
    <!-- Create button -->
    <div class="sm-header">
      <button class="sm-create-btn" @click="showCreateDialog = true">+ 创建技能</button>
    </div>

    <!-- Skill list as cards -->
    <div class="sm-list" v-if="skills.length > 0">
      <div
        v-for="skill in skills"
        :key="skill.id"
        class="sm-item"
        @click="openDetailDialog(skill)"
      >
        <div class="sm-item__icon">
          <HIcon svg="skill" :size="20" />
        </div>
        <div class="sm-item__content">
          <h3 class="sm-item__name">{{ skill.name }}</h3>
          <p class="sm-item__desc">{{ skill.description || '-' }}</p>
        </div>
        <div class="sm-item__actions" @click.stop>
          <button class="sm-action sm-action--danger" @click="handleDeleteSkill(skill, $event)" title="删除">🗑️</button>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else-if="!loading" class="sm-empty">
      <HIcon svg="skill" :size="48" />
      <p>暂无技能</p>
      <button class="sm-create-btn" @click="showCreateDialog = true">创建技能</button>
    </div>

    <!-- Mobile create dialog -->
    <div v-if="showCreateDialog" class="dialog-overlay">
      <div class="dialog-container">
        <div class="dialog-header">
          <h3>创建新 Skill</h3>
          <button class="close-btn" @click="showCreateDialog = false">×</button>
        </div>
        <div class="dialog-body">
          <div class="form-item">
            <label>Skill 名称 <span class="sm-required">*</span></label>
            <input
              v-model="createForm.name"
              type="text"
              placeholder="例如：数据分析专家、代码审查助手"
            />
          </div>
          <div class="form-item">
            <label>Skill 描述 <span class="sm-required">*</span></label>
            <textarea
              v-model="createForm.description"
              placeholder="详细描述这个 Skill 的功能、适用场景和特点..."
              rows="4"
            ></textarea>
          </div>
        </div>
        <div class="dialog-footer">
          <button @click="showCreateDialog = false">取消</button>
          <button
            class="primary-btn"
            @click="handleCreateSkill"
          >
            + 创建 Skill
          </button>
        </div>
      </div>
    </div>

    <!-- Mobile delete confirm dialog -->
    <div
      v-if="confirmDialog.visible"
      class="dialog-overlay"
      @click.self="closeConfirmDialog(false)"
    >
      <div class="dialog-container">
        <div class="dialog-header">
          <h3>{{ confirmDialog.title }}</h3>
          <button class="close-btn" @click="closeConfirmDialog(false)">×</button>
        </div>
        <div class="dialog-body">
          <p class="dialog-message">{{ confirmDialog.message }}</p>
        </div>
        <div class="dialog-footer">
          <button @click="closeConfirmDialog(false)">{{ confirmDialog.cancelText }}</button>
          <button
            :class="confirmDialog.variant === 'danger' ? 'danger-btn' : 'primary-btn'"
            @click="closeConfirmDialog(true)"
          >
            {{ confirmDialog.confirmText }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@use '../../styles/breakpoints.scss' as *;
// 全局弹窗样式
.modal-overlay {
  position: fixed;
  inset: 0;
  background: var(--harmony-comp-background-secondary);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 99999;
  animation: harmony-fade-in 0.2s ease;
}



// 手写确认弹窗样式（Element MessageBox 观感）
.confirm-modal {
  z-index: 1000000 !important;

  .confirm-dialog {
    width: 90%;
    max-width: 420px;
    background: var(--harmony-comp-background-primary);
    border-radius: var(--harmony-corner-radius-level8);
    box-shadow: 0 24px 60px rgba(0, 0, 0, 0.25);
    overflow: hidden;
    animation: harmony-slide-up 0.22s ease;
    border: 1px solid var(--harmony-shadow-sm);
  }

  .dialog-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 16px;
    border-bottom: 1px solid var(--harmony-comp-divider);
    background: var(--harmony-comp-background-primary);

    .dialog-title {
      font-size: var(--harmony-font-size-body-l);
      font-weight: 600;
      color: var(--harmony-font-primary);
    }

    .dialog-close {
      width: 28px;
      height: 28px;
      border: none;
      background: transparent;
      color: var(--harmony-font-tertiary);
      cursor: pointer;
      border-radius: var(--harmony-corner-radius-level4);
      font-size: var(--harmony-font-size-title-s);
      line-height: 28px;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.15s ease;

      &:hover {
        background: var(--harmony-font-fourth);
        color: var(--harmony-font-secondary);
      }
    }
  }

  .dialog-body {
    padding: 18px 16px 6px;

    .dialog-message {
      margin: 0;
      font-size: var(--harmony-font-size-body-m);
      color: var(--harmony-font-secondary);
      line-height: 1.6;
      white-space: pre-wrap;
      word-break: break-word;
    }
  }

  .dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    padding: var(--harmony-padding-level8) var(--harmony-padding-level10) 16px;
    background: var(--harmony-comp-background-primary);

    .btn {
      height: 32px;
      padding: 0 14px;
      border-radius: var(--harmony-corner-radius-level4);
      border: 1px solid transparent;
      font-size: var(--harmony-font-size-body-m);
      cursor: pointer;
      transition: all 0.15s ease;
      user-select: none;
    }

    .btn-default {
      background: var(--harmony-comp-background-primary);
      border-color: var(--harmony-comp-divider);
      color: var(--harmony-font-secondary);

      &:hover {
        border-color: var(--harmony-font-tertiary);
        color: var(--harmony-brand);
      }
    }

    .btn-primary {
      background: var(--harmony-brand);
      border-color: var(--harmony-brand);
      color: var(--harmony-comp-background-primary);

      &:hover {
        filter: brightness(1.03);
      }
    }

    .btn-danger {
      background: var(--harmony-warning);
      border-color: var(--harmony-warning);
      color: var(--harmony-comp-background-primary);

      &:hover {
        filter: brightness(1.03);
      }
    }
  }
}

// 创建弹窗样式
.create-modal {
  .create-dialog {
    background: var(--harmony-comp-background-primary);
    border-radius: var(--harmony-corner-radius-level18);
    width: 90%;
    max-width: 520px;
    box-shadow: 0 32px 64px rgba(0, 0, 0, 0.2);
    animation: harmony-slide-up 0.3s ease;
    overflow: hidden;
    
    .dialog-header {
      display: flex;
      align-items: center;
      gap: 16px;
      padding: 24px 24px 20px;
      background: linear-gradient(135deg, var(--harmony-comp-emphasize-tertiary) 0%, var(--harmony-comp-emphasize-tertiary) 100%);
      border-bottom: 1px solid var(--harmony-comp-emphasize-tertiary);
      position: relative;
      
      .dialog-icon {
        width: 56px;
        height: 56px;
        background: var(--harmony-comp-background-primary);
        border-radius: var(--harmony-corner-radius-level8);
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 12px var(--harmony-comp-emphasize-tertiary);
        
        img {
          width: 36px;
          height: 36px;
        }
      }
      
      .dialog-title-wrapper {
        flex: 1;
        
        h3 {
          margin: 0 0 4px;
          font-size: var(--harmony-font-size-title-s);
          font-weight: 600;
          color: var(--harmony-font-primary);
        }
        
        p {
          margin: 0;
          font-size: var(--harmony-font-size-body-m);
          color: var(--harmony-font-secondary);
        }
      }
      
      .close-btn {
        position: absolute;
        top: 16px;
        right: 16px;
        width: 32px;
        height: 32px;
        border: none;
        background: var(--harmony-shadow-xs);
        border-radius: var(--harmony-corner-radius-level6);
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--harmony-font-secondary);
        transition: all 0.2s ease;
        
        &:hover {
          background: var(--harmony-shadow-md);
          color: var(--harmony-font-primary);
        }
      }
    }
    
    .dialog-body {
      padding: 24px;
      
      .form-tip {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        padding: 16px;
        background: linear-gradient(135deg, var(--harmony-comp-emphasize-tertiary) 0%, var(--harmony-comp-emphasize-tertiary) 100%);
        border: 1px solid var(--harmony-comp-emphasize-tertiary);
        border-radius: var(--harmony-corner-radius-level8);
        margin-bottom: 24px;
        
        .tip-icon {
          flex-shrink: 0;
          margin-top: 2px;
        }
        
        p {
          margin: 0;
          font-size: var(--harmony-font-size-body-m);
          color: var(--harmony-brand);
          line-height: 1.6;
        }
      }
      
      .create-form {
        .skill-textarea {
          width: 100%;
          font-family: var(--harmony-font-family);
          font-size: var(--harmony-font-size-body-m);
          line-height: 1.5;
          border-radius: var(--harmony-corner-radius-level6);
          padding: 12px;
          border: 1px solid var(--harmony-comp-divider);
          background: var(--harmony-comp-background-secondary);
          color: var(--harmony-font-primary);
          resize: vertical;
          box-sizing: border-box;

          &:focus {
            border-color: var(--harmony-brand);
          }
        }
      }
    }

    .dialog-footer {
      padding: var(--harmony-padding-level10) var(--harmony-padding-level16) 24px;
      display: flex;
      justify-content: flex-end;
      gap: 12px;
    }
  }
}


// 添加文件弹窗样式
.add-file-modal {
  z-index: 999999 !important;
  
  .add-file-dialog {
    background: var(--harmony-comp-background-primary);
    border-radius: var(--harmony-corner-radius-level8);
    width: 90%;
    max-width: 480px;
    box-shadow: 0 32px 64px rgba(0, 0, 0, 0.25);
    animation: harmony-slide-up 0.3s ease;
    overflow: hidden;
    
    .dialog-header {
      display: flex;
      align-items: center;
      gap: 16px;
      padding: var(--harmony-padding-level16) var(--harmony-padding-level16);
      background: linear-gradient(135deg, var(--harmony-comp-emphasize-tertiary) 0%, var(--harmony-comp-emphasize-tertiary) 100%);
      border-bottom: 1px solid var(--harmony-comp-emphasize-tertiary);
      position: relative;
      
      .dialog-icon.add-icon {
        width: 48px;
        height: 48px;
        background: var(--harmony-comp-background-primary);
        border-radius: var(--harmony-corner-radius-level8);
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 12px var(--harmony-comp-emphasize-tertiary);
        color: var(--harmony-brand);
        font-size: var(--harmony-font-size-title-m);
      }
      
      .dialog-title-wrapper {
        flex: 1;
        
        h3 {
          margin: 0 0 4px;
          font-size: var(--harmony-font-size-title-s);
          font-weight: 600;
          color: var(--harmony-font-primary);
        }
        
        p {
          margin: 0;
          font-size: var(--harmony-font-size-subtitle-s);
          color: var(--harmony-font-secondary);
        }
      }
      
      .close-btn {
        position: absolute;
        top: 12px;
        right: 12px;
        width: 32px;
        height: 32px;
        border: none;
        background: var(--harmony-shadow-xs);
        border-radius: var(--harmony-corner-radius-level6);
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--harmony-font-secondary);
        transition: all 0.2s ease;
        
        &:hover {
          background: var(--harmony-shadow-md);
          color: var(--harmony-font-primary);
        }
      }
    }
    
    .dialog-body {
      padding: 24px;
      
      .add-file-tip {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 14px 16px;
        background: linear-gradient(135deg, var(--harmony-comp-emphasize-tertiary) 0%, var(--harmony-comp-emphasize-tertiary) 100%);
        border: 1px solid var(--harmony-comp-emphasize-tertiary);
        border-radius: var(--harmony-corner-radius-level6);
        margin-bottom: 20px;
        color: var(--harmony-brand);
        font-size: var(--harmony-font-size-body-m);

        strong {
          color: var(--harmony-brand);
          font-weight: 600;
        }
      }
      
      .form-group {
        margin-bottom: 20px;
        
        &:last-child {
          margin-bottom: 0;
        }
        
        label {
          display: block;
          font-size: var(--harmony-font-size-body-m);
          font-weight: 600;
          color: var(--harmony-font-primary);
          margin-bottom: 8px;
        }
        
        .file-name-hint {
          margin-top: 8px;
          font-size: var(--harmony-font-size-body-s);
          color: var(--harmony-font-tertiary);
        }
      }
      
      .folder-option {
        display: flex;
        align-items: center;
        gap: 8px;
        
        .folder-option-icon {
          color: var(--harmony-alert);
        }
        
        .folder-option-path {
          margin-left: auto;
          color: var(--harmony-font-tertiary);
          font-size: var(--harmony-font-size-body-s);
        }
      }
    }
    
    .dialog-footer {
      padding: var(--harmony-padding-level10) var(--harmony-padding-level16);
      display: flex;
      justify-content: flex-end;
      gap: 12px;
      border-top: 1px solid var(--harmony-comp-divider);
      background: var(--harmony-comp-background-primary);
    }
  }
}

// 详情弹窗 - IDE 风格
.detail-modal {
  .detail-dialog {
    background: var(--harmony-comp-background-primary);
    border-radius: var(--harmony-corner-radius-level8);
    width: 95%;
    max-width: 1400px;
    height: 80vh;
    border: 1px solid var(--harmony-comp-divider);
    box-shadow: 0 24px 48px var(--harmony-shadow-md);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    animation: harmony-slide-up 0.3s ease;
    
    // IDE 头部
    .ide-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: var(--harmony-comp-background-primary);
      height: 40px;
      padding: 0 12px;
      
      .ide-tabs {
        display: flex;
        align-items: center;
        height: 100%;
        
        .ide-tab {
          display: flex;
          align-items: center;
          gap: 8px;
          height: 100%;
          padding: 0 16px;
          background: var(--harmony-comp-background-primary);
          border-top: 2px solid var(--harmony-brand);
          color: var(--harmony-font-primary);
          font-size: var(--harmony-font-size-subtitle-s);
          
          .tab-icon {
            width: 16px;
            height: 16px;
          }
        }
      }
      
      .ide-actions {
        .ide-btn {
          width: 32px;
          height: 32px;
          border: none;
          background: transparent;
          color: var(--harmony-font-secondary);
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: var(--harmony-corner-radius-level4);
          transition: all 0.2s ease;
          
          &:hover {
            background: var(--harmony-comp-divider);
            color: var(--harmony-font-primary);
          }
        }
      }
    }
    
    // IDE 内容区
    .ide-body {
      flex: 1;
      display: flex;
      overflow: hidden;
      
      // 侧边栏
      .ide-sidebar {
        width: 260px;
        background: var(--harmony-comp-background-primary);
        display: flex;
        flex-direction: column;
        
        .sidebar-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: var(--harmony-padding-level8) var(--harmony-padding-level10);
          color: var(--harmony-font-secondary);
          font-size: var(--harmony-font-size-caption-l);
          font-weight: 700;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          
          .sidebar-hint {
            color: var(--harmony-font-tertiary);
            cursor: help;
            display: flex;
            align-items: center;
            
            &:hover {
              color: var(--harmony-font-secondary);
            }
          }
        }
        
        .file-explorer {
          flex: 1;
          overflow-y: auto;
          padding: 8px 0;
          
          .explorer-item {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 6px 16px;
            color: var(--harmony-font-primary);
            font-size: var(--harmony-font-size-subtitle-s);
            cursor: pointer;
            position: relative;
            
            &:hover {
              background: var(--harmony-comp-background-primary);
              
              .item-delete {
                opacity: 1;
              }
            }
            
            &.active {
              background: var(--harmony-comp-emphasize-tertiary);
              color: var(--harmony-font-primary);
              
              &::before {
                content: '';
                position: absolute;
                left: 0;
                top: 0;
                bottom: 0;
                width: 2px;
                background: var(--harmony-brand);
              }
            }
            
            &.project-root {
              color: var(--harmony-font-primary);
              font-weight: 500;
              padding-top: 8px;
              padding-bottom: 8px;
            }
            
            &.folder-item {
              color: var(--harmony-alert);
              
              &.can-add:hover {
                .item-add {
                  opacity: 1;
                }
              }
            }
            
            &.nested {
              padding-left: 40px;
            }
            
            &.empty-hint {
              color: var(--harmony-font-tertiary);
              font-size: var(--harmony-font-size-body-s);
              font-style: italic;
              cursor: default;
              
              &:hover {
                background: transparent;
              }
            }
            
            .item-badge {
              font-size: var(--harmony-font-size-caption-m);
              padding: 2px 6px;
              border-radius: var(--harmony-corner-radius-level4);
              margin-left: auto;
              
              &.readonly {
                background: var(--harmony-font-fourth);
                color: var(--harmony-font-tertiary);
              }
            }
            
            .item-add {
              opacity: 0;
              width: 20px;
              height: 20px;
              border: none;
              background: transparent;
              color: var(--harmony-confirm);
              cursor: pointer;
              display: flex;
              align-items: center;
              justify-content: center;
              border-radius: var(--harmony-corner-radius-level4);
              transition: all 0.2s ease;
              margin-left: auto;
              
              &:hover {
                background: var(--harmony-confirm-bg);
                color: var(--harmony-confirm);
              }
            }
            
            .item-icon {
              font-size: var(--harmony-font-size-body-l);
              flex-shrink: 0;
              
              &.folder-icon {
                color: var(--harmony-alert);
              }
              
              &.file-icon {
                color: var(--harmony-brand);
              }
            }
            
            .item-name {
              flex: 1;
              overflow: hidden;
              text-overflow: ellipsis;
              white-space: nowrap;
            }
            
            .item-delete {
              opacity: 0;
              width: 20px;
              height: 20px;
              border: none;
              background: transparent;
              color: var(--harmony-warning);
              cursor: pointer;
              display: flex;
              align-items: center;
              justify-content: center;
              border-radius: var(--harmony-corner-radius-level4);
              transition: opacity 0.2s ease;
              
              &:hover {
                background: var(--harmony-warning-bg);
              }
            }
          }
        }
        
        .skill-info-panel {
          padding: 16px;
          background: var(--harmony-comp-background-primary);
          
          h4 {
            margin: 0 0 8px;
            font-size: var(--harmony-font-size-body-s);
            font-weight: 600;
            color: var(--harmony-font-secondary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
          }
          
          .info-desc {
            margin: 0 0 12px;
            font-size: var(--harmony-font-size-subtitle-s);
            color: var(--harmony-font-secondary);
            line-height: 1.5;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
          }
          
          .info-meta {
            font-size: var(--harmony-font-size-body-s);
            color: var(--harmony-font-tertiary);
            
            span {
              display: flex;
              align-items: center;
              gap: 6px;
            }
          }
        }
      }
      
      // 主编辑区
      .ide-main {
        flex: 1;
        display: flex;
        flex-direction: column;
        background: var(--harmony-comp-background-primary);
        
        .editor-tabs {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 0 16px;
          height: 48px;
          background: var(--harmony-comp-background-primary);
          
          .editor-tab {
            display: flex;
            align-items: center;
            gap: 8px;
            color: var(--harmony-font-primary);
            font-size: var(--harmony-font-size-subtitle-s);
          }
          
          .editor-actions {
            display: flex;
            gap: 8px;

            .editor-btn {
              display: inline-flex;
              align-items: center;
              gap: 6px;
              height: 30px;
              padding: 0 14px;
              border-radius: var(--harmony-corner-radius-level18);
              font-size: var(--harmony-font-size-body-s);
              font-weight: 500;
              border: 1px solid transparent;
              background: transparent;
              color: var(--harmony-font-secondary);
              transition: all 0.18s ease;

              &--ghost {
                border-color: var(--harmony-comp-emphasize-tertiary);
                background: var(--harmony-comp-emphasize-tertiary);
                color: var(--harmony-brand);

                &:hover {
                  background: var(--harmony-comp-emphasize-tertiary);
                  border-color: var(--harmony-comp-emphasize-tertiary);
                  box-shadow: 0 0 0 1px var(--harmony-comp-emphasize-tertiary);
                  transform: translateY(-0.5px);
                }
              }

              &--cancel {
                background: transparent;
                color: var(--harmony-font-secondary);
                border-color: var(--harmony-comp-divider);

                &:hover {
                  background: var(--harmony-comp-background-primary);
                  border-color: var(--harmony-comp-divider);
                }
              }

              &--primary {
                background: var(--harmony-brand);
                border-color: transparent;
                color: var(--harmony-comp-background-primary);
                box-shadow: 0 4px 10px var(--harmony-comp-emphasize-tertiary);

                &:hover {
                  filter: brightness(1.05);
                  box-shadow: 0 6px 14px var(--harmony-comp-emphasize-tertiary);
                  transform: translateY(-0.5px);
                }

                &.is-loading {
                  opacity: 0.8;
                  box-shadow: none;
                  transform: none;
                }
              }
            }
          }
        }
        
        .editor-content {
          flex: 1;
          overflow: hidden;
          
          .monaco-container {
            width: 100%;
            height: 100%;
          }
          
          .code-preview {
            margin: 0;
            padding: 20px;
            height: 100%;
            overflow: auto;
            background: var(--harmony-comp-background-primary);
            
            code {
              font-family: var(--harmony-font-family);
              font-size: var(--harmony-font-size-body-m);
              line-height: 1.6;
              color: var(--harmony-font-primary);
              white-space: pre-wrap;
              word-wrap: break-word;
            }
          }
        }
        
        .no-file-state {
          flex: 1;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          color: var(--harmony-font-secondary);
          
          .no-file-icon {
            color: var(--harmony-comp-divider);
            margin-bottom: 16px;
          }
          
          h3 {
            margin: 0 0 8px;
            font-size: var(--harmony-font-size-title-s);
            color: var(--harmony-font-primary);
          }
          
          p {
            margin: 0;
            font-size: var(--harmony-font-size-body-m);
          }
        }
      }
    }
  }
}
</style>

<style lang="scss" scoped>
@use '../../styles/breakpoints.scss' as *;
.skill-page {
  padding: 32px;
  min-height: 100%;
  background: transparent;
  
  // 页面头部
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    background: var(--harmony-comp-background-primary);
    padding: var(--harmony-padding-level16) var(--harmony-padding-level16);
    border-radius: var(--harmony-corner-radius-level8);
    box-shadow: 0 6px 24px var(--harmony-shadow-sm);
    
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
      display: flex;
      gap: 12px;
    }
  }

  // 列表容器
  .skill-container {
    background: var(--harmony-comp-background-primary);
    border-radius: var(--harmony-corner-radius-level8);
    overflow: hidden;
    box-shadow: 0 4px 6px -1px var(--harmony-shadow-xs);
    
    // 列表头部
    .list-header {
      display: flex;
      align-items: center;
      padding: var(--harmony-padding-level10) var(--harmony-padding-level16);
      background: var(--harmony-comp-background-primary);
      font-size: var(--harmony-font-size-body-s);
      font-weight: 600;
      color: var(--harmony-font-secondary);
      text-transform: uppercase;
      letter-spacing: 0.5px;
      
      .col-name { flex: 0 0 240px; }
      .col-desc { flex: 1; min-width: 200px; }
      .col-files { flex: 0 0 100px; text-align: center; }
      .col-time { flex: 0 0 120px; }
      .col-actions { flex: 0 0 100px; text-align: right; }
    }
    
    // 列表内容
    .skill-list {
      .skill-row {
        display: flex;
        align-items: center;
        padding: var(--harmony-padding-level10) var(--harmony-padding-level16);
        cursor: pointer;
        transition: all 0.2s ease;
        
        &:last-child {
          border-bottom: none;
        }
        
        &:hover {
          background: var(--harmony-comp-background-primary);
          
          .col-name .skill-info .skill-avatar {
            transform: scale(1.05);
            box-shadow: 0 0 0 3px var(--harmony-comp-emphasize-tertiary);
          }
          
          .col-actions .action-btn {
            opacity: 1;
          }
        }
        
        .col-name {
          flex: 0 0 240px;
          
          .skill-info {
            display: flex;
            align-items: center;
            gap: 14px;
            
            .skill-avatar {
              width: 40px;
              height: 40px;
              background: linear-gradient(135deg, var(--harmony-comp-emphasize-tertiary) 0%, var(--harmony-comp-emphasize-tertiary) 100%);
              border-radius: var(--harmony-corner-radius-level6);
              display: flex;
              align-items: center;
              justify-content: center;
              border: 1px solid var(--harmony-comp-emphasize-tertiary);
              transition: all 0.2s ease;
              flex-shrink: 0;
              
              img {
                width: 22px;
                height: 22px;
              }
            }
            
            .skill-name {
              font-size: var(--harmony-font-size-body-l);
              font-weight: 600;
              color: var(--harmony-font-primary);
              white-space: nowrap;
              overflow: hidden;
              text-overflow: ellipsis;
            }
          }
        }
        
        .col-desc {
          flex: 1;
          min-width: 200px;
          padding-right: 24px;
          
          .skill-desc {
            font-size: var(--harmony-font-size-body-m);
            color: var(--harmony-font-secondary);
            line-height: 1.5;
            display: -webkit-box;
            -webkit-line-clamp: 1;
            -webkit-box-orient: vertical;
            overflow: hidden;
          }
        }
        
        .col-files {
          flex: 0 0 100px;
          text-align: center;
          
          .file-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 12px;
            background: var(--harmony-comp-emphasize-tertiary);
            color: var(--harmony-brand);
            border-radius: var(--harmony-corner-radius-level18);
            font-size: var(--harmony-font-size-subtitle-s);
            font-weight: 500;
          }
        }
        
        .col-time {
          flex: 0 0 120px;
          
          .time-text {
            font-size: var(--harmony-font-size-subtitle-s);
            color: var(--harmony-font-tertiary);
          }
        }
        
        .col-actions {
          flex: 0 0 100px;
          display: flex;
          justify-content: flex-end;
          gap: 8px;
          
          .action-btn {
            width: 32px;
            height: 32px;
            border: 1px solid transparent;
            border-radius: var(--harmony-corner-radius-level6);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
            font-size: var(--harmony-font-size-body-m);
            opacity: 0.5;
            
            &.view-btn {
              background: var(--harmony-comp-background-primary);
              color: var(--harmony-font-secondary);
              
              &:hover {
                background: var(--harmony-comp-emphasize-tertiary);
                color: var(--harmony-brand);
                border-color: var(--harmony-comp-emphasize-tertiary);
                opacity: 1;
              }
            }
            
            &.delete-btn {
              background: var(--harmony-comp-background-primary)1f2;
              color: var(--harmony-warning);
              
              &:hover {
                background: var(--harmony-warning-bg);
                color: var(--harmony-warning);
                border-color: var(--harmony-warning-bg);
                opacity: 1;
              }
            }
          }
        }
      }
    }
    
    // 空状态 - 放在 skill-container 内部
    .empty-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 80px 20px;
      
      .empty-visual {
        margin-bottom: 24px;
        
        .empty-icon-wrapper {
          width: 80px;
          height: 80px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: var(--harmony-comp-background-primary);
          border-radius: var(--harmony-corner-radius-level18);
          
          .empty-icon {
            width: 44px;
            height: 44px;
            opacity: 0.4;
          }
        }
      }
      
      .empty-content {
        text-align: center;
        
        h3 {
          margin: 0 0 8px;
          font-size: var(--harmony-font-size-title-s);
          font-weight: 600;
          color: var(--harmony-font-primary);
        }
        
        p {
          margin: 0 0 24px;
          font-size: var(--harmony-font-size-body-m);
          color: var(--harmony-font-secondary);
          max-width: 360px;
        }
        
        .empty-btn {
          height: 40px;
          padding: 0 24px;
          border-radius: var(--harmony-corner-radius-level6);
          font-size: var(--harmony-font-size-body-m);
          font-weight: 600;
        }
      }
    }
  }
}

// 动画




// 卡片列表动画
.card-list-enter-active,
.card-list-leave-active {
  transition: all 0.4s ease;
}

.card-list-enter-from,
.card-list-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

// 响应式
@include mobile {
  .skill-page {
    padding: 16px;
    
    .page-header .header-content {
      flex-direction: column;
      gap: 24px;
      
      .header-right {
        width: 100%;
        flex-direction: column;
        gap: 16px;
        
        .stats-cards {
          width: 100%;
          
          .stat-card {
            width: 100%;
            justify-content: center;
          }
        }
        
        .header-actions {
          width: 100%;
          justify-content: center;
        }
      }
    }
    
    .filter-section {
      flex-direction: column;
      gap: 16px;
      align-items: stretch;
      
      .search-wrapper .search-input {
        width: 100%;
      }
      
      .filter-info {
        justify-content: space-between;
      }
    }
    
    .skill-container .skill-grid {
      grid-template-columns: 1fr;
    }
  }
}

// Mobile layout (hmos pattern)
.skill-mobile {
  display: flex;
  flex-direction: column;
  gap: var(--harmony-section-gap-mobile, 16px);
  padding-top: var(--harmony-padding-level8, 16px);
}

.sm-header {
  display: flex;
  justify-content: flex-end;
}

.sm-create-btn {
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

.sm-list {
  display: flex;
  flex-direction: column;
  gap: var(--harmony-card-gap-mobile, 12px);
}

.sm-item {
  display: flex;
  align-items: center;
  gap: var(--harmony-padding-level6, 12px);
  padding: var(--harmony-padding-level8, 16px);
  background: var(--harmony-comp-background-primary);
  border-radius: var(--harmony-corner-radius-level8, 16px);
  cursor: pointer;
  transition: background 0.15s ease;

  &:active {
    background: var(--harmony-interactive-pressed);
  }

  &__icon {
    width: var(--harmony-control-height-40, 40px);
    height: var(--harmony-control-height-40, 40px);
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--harmony-comp-emphasize-tertiary);
    border-radius: var(--harmony-corner-radius-level6, 12px);
    flex-shrink: 0;
  }

  &__content {
    flex: 1;
    min-width: 0;
  }

  &__name {
    font-size: var(--harmony-font-size-body-l, 16px);
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

.sm-action {
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
  transition: background 0.15s ease;

  &:active {
    background: var(--harmony-interactive-pressed);
  }

  &--danger:active {
    background: var(--harmony-alert-bg, rgba(232, 64, 38, 0.1));
  }
}

.sm-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--harmony-padding-level16, 32px) 0;
  gap: var(--harmony-padding-level8, 16px);

  p {
    font-size: var(--harmony-font-size-body-m);
    color: var(--harmony-font-tertiary);
    margin: 0;
  }
}

.sm-required {
  color: var(--harmony-alert, red);
  font-weight: 700;
}

// Mobile dialog styles (shared)
.dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 99999;
  animation: harmony-fade-in 0.2s ease;
}

.dialog-container {
  width: 90%;
  max-width: 480px;
  background: var(--harmony-comp-background-primary);
  border-radius: var(--harmony-corner-radius-level8, 16px);
  box-shadow: 0 32px 64px rgba(0, 0, 0, 0.25);
  animation: harmony-slide-up 0.3s ease;
  overflow: hidden;
}

.dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--harmony-padding-level8, 16px) var(--harmony-padding-level10, 20px);
  border-bottom: 1px solid var(--harmony-comp-divider);

  h3 {
    margin: 0;
    font-size: var(--harmony-font-size-body-l, 16px);
    font-weight: 600;
    color: var(--harmony-font-primary);
  }

  .close-btn {
    width: 32px;
    height: 32px;
    border: none;
    background: transparent;
    color: var(--harmony-font-secondary);
    cursor: pointer;
    font-size: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: var(--harmony-corner-radius-level4, 8px);

    &:active {
      background: var(--harmony-interactive-pressed);
    }
  }
}

.dialog-body {
  padding: var(--harmony-padding-level8, 16px) var(--harmony-padding-level10, 20px);

  .form-item {
    margin-bottom: var(--harmony-padding-level8, 16px);

    &:last-child {
      margin-bottom: 0;
    }

    label {
      display: block;
      font-size: var(--harmony-font-size-body-m);
      font-weight: 600;
      color: var(--harmony-font-primary);
      margin-bottom: var(--harmony-padding-level4, 8px);
    }

    input,
    textarea {
      width: 100%;
      box-sizing: border-box;
      padding: var(--harmony-padding-level4, 8px) var(--harmony-padding-level6, 12px);
      border: 1px solid var(--harmony-comp-divider);
      border-radius: var(--harmony-corner-radius-level6, 12px);
      font-size: var(--harmony-font-size-body-m);
      color: var(--harmony-font-primary);
      background: var(--harmony-comp-background-secondary);
      font-family: var(--harmony-font-family);
      outline: none;
      transition: border-color 0.15s ease;

      &:focus {
        border-color: var(--harmony-brand);
      }
    }

    textarea {
      resize: vertical;
      line-height: 1.5;
    }
  }

  .dialog-message {
    margin: 0;
    font-size: var(--harmony-font-size-body-m);
    color: var(--harmony-font-secondary);
    line-height: 1.6;
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--harmony-padding-level4, 8px);
  padding: var(--harmony-padding-level8, 16px) var(--harmony-padding-level10, 20px);
  border-top: 1px solid var(--harmony-comp-divider);

  button {
    height: var(--harmony-control-height-40, 40px);
    padding: 0 var(--harmony-padding-level8, 16px);
    border: 1px solid var(--harmony-comp-divider);
    border-radius: var(--harmony-corner-radius-level6, 12px);
    background: var(--harmony-comp-background-primary);
    color: var(--harmony-font-secondary);
    font-size: var(--harmony-font-size-body-m);
    cursor: pointer;
    transition: background 0.15s ease;

    &:active {
      background: var(--harmony-interactive-pressed);
    }
  }

  .primary-btn {
    background: var(--harmony-brand);
    border-color: var(--harmony-brand);
    color: var(--harmony-comp-common-contrary, white);

    &:active {
      filter: brightness(0.95);
    }
  }

  .danger-btn {
    background: var(--harmony-warning);
    border-color: var(--harmony-warning);
    color: var(--harmony-comp-common-contrary, white);

    &:active {
      filter: brightness(0.95);
    }
  }
}

@keyframes harmony-fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes harmony-slide-up {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

</style>

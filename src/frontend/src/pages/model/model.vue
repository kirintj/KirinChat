<script setup lang="ts">
import { ref, inject, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { HMessage, HButton, HInput, HTooltip } from '@/components/ui'
import modelIcon from '../../assets/model.svg'
import { 
  getVisibleLLMsAPI, 
  createLLMAPI, 
  updateLLMAPI,
  deleteLLMAPI,
  searchLLMsAPI,
  type LLMResponse,
  type CreateLLMRequest
} from '../../apis/llm'

const router = useRouter()
const isMobile = inject<import('vue').Ref<boolean>>('isMobile', ref(false))

// 响应式数据
const models = ref<LLMResponse[]>([])
const loading = ref(false)
const searchKeyword = ref('')
const llmTypes = ref<string[]>(['LLM', 'Embedding', 'Rerank'])

// 防抖定时器
let searchTimer: ReturnType<typeof setTimeout> | null = null

// 创建/编辑对话框控制
const createDialogVisible = ref(false)
const createLoading = ref(false)
const isEditMode = ref(false)
const editingModelId = ref('')
const showApiKey = ref(false)

// 删除确认对话框控制
const deleteDialogVisible = ref(false)
const deleteLoading = ref(false)
const modelToDelete = ref<LLMResponse | null>(null)

// 表单相关
const createForm = ref<CreateLLMRequest>({
  model: '',
  api_key: '',
  base_url: '',
  provider: '',
  llm_type: 'LLM'
})

// 获取模型列表
const fetchModels = async () => {
  loading.value = true
  try {
    const response = await getVisibleLLMsAPI()
    
    if (response.data.status_code === 200) {
      const data = response.data.data || {}
      const allModels: LLMResponse[] = []
      
      Object.values(data).forEach((typeModels: any) => {
        if (Array.isArray(typeModels)) {
          allModels.push(...typeModels)
        }
      })
      
      models.value = allModels
    } else {
      HMessage.error(response.data.status_message || '获取模型列表失败')
    }
  } catch (error) {
    HMessage.error('获取模型列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索模型
const searchModels = async () => {
  if (!searchKeyword.value.trim()) {
    // 如果搜索关键词为空，则获取所有模型
    fetchModels()
    return
  }
  
  loading.value = true
  try {
    const response = await searchLLMsAPI({ llm_name: searchKeyword.value.trim() })
    
    if (response.data.status_code === 200) {
      const data = response.data.data || {}
      const allModels: LLMResponse[] = []
      
      Object.values(data).forEach((typeModels: any) => {
        if (Array.isArray(typeModels)) {
          allModels.push(...typeModels)
        }
      })
      
      models.value = allModels
    } else {
      HMessage.error(response.data.status_message || '搜索模型失败')
    }
  } catch (error) {
    HMessage.error('搜索模型失败')
  } finally {
    loading.value = false
  }
}

// 清空搜索
const clearSearch = () => {
  searchKeyword.value = ''
  fetchModels()
}

// 打开创建对话框
const openCreateDialog = () => {
  isEditMode.value = false
  editingModelId.value = ''
  showApiKey.value = false
  createDialogVisible.value = true
  // 重置表单
  Object.assign(createForm.value, {
    model: '',
    api_key: '',
    base_url: '',
    provider: '',
    llm_type: 'LLM'
  })
}

// 打开编辑对话框
const openEditDialog = (model: LLMResponse) => {
  isEditMode.value = true
  editingModelId.value = model.llm_id
  showApiKey.value = false
  createDialogVisible.value = true
  // 填充表单
  Object.assign(createForm.value, {
    model: model.model,
    api_key: model.api_key,
    base_url: model.base_url,
    provider: model.provider,
    llm_type: model.llm_type
  })
}

// 创建或更新模型
const handleCreate = async () => {
  // 检查必填字段
  if (!createForm.value.model || !createForm.value.api_key || !createForm.value.base_url || !createForm.value.provider) {
    HMessage.error('请填写所有必填字段')
    return
  }
  
  createLoading.value = true
  try {
    if (isEditMode.value) {
      // 编辑模式 - 调用更新接口
      const response = await updateLLMAPI({
        llm_id: editingModelId.value,
        model: createForm.value.model,
        api_key: createForm.value.api_key,
        base_url: createForm.value.base_url,
        provider: createForm.value.provider,
        llm_type: createForm.value.llm_type
      })
      
      if (response.data.status_code === 200) {
        HMessage.success('更新成功')
        createDialogVisible.value = false
        fetchModels()
      } else {
        HMessage.error('更新失败: ' + (response.data.status_message || '未知错误'))
      }
    } else {
      // 创建模式
      const response = await createLLMAPI(createForm.value)
      
      if (response.data.status_code === 200) {
        HMessage.success('创建成功')
        createDialogVisible.value = false
        fetchModels()
      } else {
        HMessage.error('创建失败: ' + (response.data.status_message || '未知错误'))
      }
    }
  } catch (error) {
    HMessage.error((isEditMode.value ? '更新' : '创建') + '失败，请检查输入并稍后重试')
  } finally {
    createLoading.value = false
  }
}

// 跳转到模型编辑器
const goToModelEditor = (model: LLMResponse) => {
  router.push({
    name: 'model-editor',
    query: { id: model.llm_id }
  })
}

// 删除模型
const deleteModel = async (model: LLMResponse) => {
  // 检查是否为官方模型
  if (isOfficialModel(model)) {
    HMessage.warning('官方模型不可删除')
    return
  }
  
  // 显示删除确认对话框
  modelToDelete.value = model
  deleteDialogVisible.value = true
}

// 确认删除模型
const confirmDelete = async () => {
  if (!modelToDelete.value) return
  
  deleteLoading.value = true
  try {
    const response = await deleteLLMAPI({ llm_id: modelToDelete.value.llm_id })
    
    if (response.data.status_code === 200) {
      HMessage.success('删除成功')
      deleteDialogVisible.value = false
      fetchModels()
    } else {
      HMessage.error('删除失败: ' + (response.data.status_message || '未知错误'))
    }
  } catch (err) {
    HMessage.error('删除失败，请稍后重试')
  } finally {
    deleteLoading.value = false
  }
}

// 取消删除
const cancelDelete = () => {
  deleteDialogVisible.value = false
  modelToDelete.value = null
}

// 检查是否为官方模型
const isOfficialModel = (model: LLMResponse): boolean => {
  return model.user_id === '0'
}

// 测试模型连接
const testModel = async (model: LLMResponse) => {
  HMessage.info(`正在测试 ${model.model} 连接...`)
  // 这里可以添加实际的测试逻辑
  setTimeout(() => {
    HMessage.success(`${model.model} 连接测试完成`)
  }, 2000)
}

// 获取提供商颜色
const getProviderColor = (provider: string) => {
  const colors: Record<string, string> = {
    'OpenAI': 'primary',
    'Anthropic': 'success',
    '阿里云': 'warning',
    '百度': 'info',
    'Google': 'danger'
  }
  return colors[provider] || 'info'
}

// 获取模型类型颜色
const getTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    'LLM': 'primary',
    'Embedding': 'success',
    'Rerank': 'warning'
  }
  return colors[type] || 'info'
}

// 格式化时间
const formatTime = (timeStr: string) => {
  if (!timeStr) return '-'
  return new Date(timeStr).toLocaleDateString('zh-CN')
}

// 截断URL函数
const truncateUrl = (url: string, maxLength: number): string => {
  if (!url) return '';
  if (url.length <= maxLength) return url;
  
  const protocol = url.includes('://') ? url.split('://')[0] + '://' : '';
  const domainPath = url.replace(protocol, '');
  
  // 如果协议+3个点+最后15个字符超过了最大长度，就只显示开头和结尾
  if (protocol.length + 3 + 15 >= maxLength) {
    const start = protocol + domainPath.substring(0, Math.floor((maxLength - protocol.length - 3) / 2));
    const end = domainPath.substring(domainPath.length - Math.floor((maxLength - protocol.length - 3) / 2));
    return start + '...' + end;
  }
  
  // 否则显示协议+域名开头+...+路径结尾
  const visibleLength = maxLength - protocol.length - 3;
  const start = domainPath.substring(0, Math.floor(visibleLength / 2));
  const end = domainPath.substring(domainPath.length - Math.floor(visibleLength / 2));
  
  return protocol + start + '...' + end;
};

// 改进格式化时间函数，使其更友好
const formatTimeFriendly = (timeStr: string) => {
  if (!timeStr) return '-';
  
  try {
    const date = new Date(timeStr);
    const year = date.getFullYear();
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const day = date.getDate().toString().padStart(2, '0');
    
    return `${year}/${month}/${day}`;
  } catch(e) {
    return timeStr;
  }
}

// 监听搜索关键词变化，实时搜索（带防抖）
watch(searchKeyword, (newValue) => {
  // 清除之前的定时器
  if (searchTimer) {
    clearTimeout(searchTimer)
  }
  
  // 设置新的定时器，300ms后执行搜索
  searchTimer = setTimeout(() => {
    searchModels()
  }, 300)
})

onMounted(() => {
  fetchModels()
})
</script>

<template>
  <!-- Desktop -->
  <div v-if="!isMobile" class="model-page page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-title">
        <h2>模型管理</h2>
      </div>
      <div class="header-actions">
        <div class="search-box">
          <HInput
            v-model="searchKeyword"
            placeholder=" 搜索模型名称..."
            clearable
            @clear="clearSearch"
            style="width: 300px"
          />
        </div>
        
        <div class="action-buttons">
          <HButton
            type="secondary"
            @click="fetchModels"
            :loading="loading"
            class="refresh-btn"
          >
             刷新
          </HButton>
          <HButton
            type="primary"
            @click="openCreateDialog"
            class="add-btn"
          >
             添加模型
          </HButton>
        </div>
      </div>
    </div>

    <!-- 模型列表 -->
    <div class="model-container" style="position: relative;">
      <div v-if="loading" class="loading-overlay">
        <div class="loading-spinner"></div>
      </div>
      <!-- 列表头部 -->
      <div class="list-header" v-if="models.length > 0">
        <div class="col-name">模型名称</div>
        <div class="col-provider">提供商</div>
        <div class="col-type">模型类型</div>
        <div class="col-url">Base URL</div>
        <div class="col-actions">操作</div>
      </div>

      <!-- 列表内容 -->
      <div class="model-list" v-if="models.length > 0">
        <div 
          v-for="model in models" 
          :key="model.llm_id" 
          class="model-row"
        >
          <div class="col-name">
            <div class="name-info">
              <div class="provider-avatar" :class="model.llm_type.toLowerCase()">
                <span>{{ model.model?.[0] || '?' }}</span>
              </div>
              <span class="model-name">{{ model.model }}</span>
              <span class="official-tag" v-if="isOfficialModel(model)">官方</span>
            </div>
          </div>
          <div class="col-provider">
            <span class="provider-name">{{ model.provider }}</span>
          </div>
          <div class="col-type">
            <span class="type-badge" :class="model.llm_type.toLowerCase()">
              {{ model.llm_type }}
            </span>
          </div>
          <div class="col-url">
            <HTooltip
              :content="model.base_url"
              placement="top"
            >
              <span class="url-text">{{ truncateUrl(model.base_url, 40) }}</span>
            </HTooltip>
          </div>
          <div class="col-actions" @click.stop>
            <HTooltip content="编辑" placement="top">
              <button
                class="action-btn edit-btn"
                @click="openEditDialog(model)"
                :disabled="isOfficialModel(model)"
                :class="{ 'disabled': isOfficialModel(model) }"
              >
                <Icon icon="mdi:pencil" :width="16" :height="16" />
              </button>
            </HTooltip>
            <HTooltip content="删除" placement="top">
              <button
                class="action-btn delete-btn"
                @click="deleteModel(model)"
                :disabled="isOfficialModel(model)"
                :class="{ 'disabled': isOfficialModel(model) }"
              >
                <Icon icon="mdi:delete" :width="16" :height="16" />
              </button>
            </HTooltip>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="models.length === 0 && !loading" class="empty-state">
        <div class="empty-icon">
          <span class="empty-emoji"><Icon icon="mdi:robot" :width="56" :height="56" style="opacity:0.6;" /></span>
        </div>
        <h3>暂无模型</h3>
        <p>点击上方按钮添加您的第一个AI模型</p>
        <HButton
          type="primary"
          @click="openCreateDialog"
          size="large"
        >
          添加模型
        </HButton>
      </div>
    </div>

  </div>

  <!-- Shared dialogs (desktop + mobile) -->
  <!-- 创建模型对话框 -->
  <div v-if="createDialogVisible" class="dialog-overlay" @click="createDialogVisible = false">
    <div class="dialog-container" @click.stop>
      <div class="dialog-body">
        <div class="form-row">
          <div class="form-item">
            <label class="form-label">
              <span class="label-text">模型名称</span>
              <span class="required-mark">*</span>
            </label>
            <div class="input-wrapper">
              <input
                v-model="createForm.model"
                type="text"
                placeholder="例如：qwen-max"
                maxlength="50"
                class="form-input"
              />
            </div>
          </div>
          <div class="form-item">
            <label class="form-label">
              <span class="label-text">提供商</span>
              <span class="required-mark">*</span>
            </label>
            <div class="input-wrapper">
              <input
                v-model="createForm.provider"
                type="text"
                placeholder="例如：通义千问"
                maxlength="50"
                class="form-input"
              />
            </div>
          </div>
          <div class="form-item">
            <label class="form-label">
              <span class="label-text">基础URL</span>
              <span class="required-mark">*</span>
            </label>
            <div class="input-wrapper">
              <input
                v-model="createForm.base_url"
                type="text"
                placeholder="例如：https://api.openai.com/v1"
                maxlength="200"
                class="form-input"
              />
            </div>
          </div>
          <div class="form-item">
            <label class="form-label">
              <span class="label-text">API密钥</span>
              <span class="required-mark">*</span>
            </label>
            <div class="input-wrapper api-key-wrapper">
              <input
                v-model="createForm.api_key"
                :type="showApiKey ? 'text' : 'password'"
                placeholder="请输入您的API密钥"
                maxlength="200"
                class="form-input api-key-input"
              />
              <span class="toggle-password" @click="showApiKey = !showApiKey">
                <Icon :icon="showApiKey ? 'mdi:eye' : 'mdi:eye-off'" :width="20" :height="20" />
              </span>
            </div>
          </div>
        </div>
      </div>
      <div class="dialog-footer">
        <button class="dialog-btn cancel-btn" @click.stop="createDialogVisible = false">
          <span class="btn-text">取消</span>
        </button>
        <button
          class="dialog-btn confirm-btn"
          :class="{ 'disabled': !createForm.model || !createForm.api_key || !createForm.base_url || !createForm.provider }"
          :disabled="!createForm.model || !createForm.api_key || !createForm.base_url || !createForm.provider || createLoading"
          @click.stop="handleCreate"
        >
          <span v-if="createLoading" class="btn-icon loading"><Icon icon="mdi:refresh" :width="16" :height="16" /></span>
          <span class="btn-text">{{ createLoading ? '创建中...' : '确定创建' }}</span>
        </button>
      </div>
    </div>
  </div>

  <!-- 删除确认对话框 -->
  <div v-if="deleteDialogVisible" class="dialog-overlay" @click="cancelDelete">
    <div class="delete-dialog-container" @click.stop>
      <div class="delete-dialog-body">
        <p v-if="modelToDelete">
          确定要删除模型 <strong>"{{ modelToDelete.model }}"</strong> 吗？
        </p>
      </div>
      <div class="delete-dialog-footer">
        <button class="delete-dialog-btn cancel-btn" @click="cancelDelete" :disabled="deleteLoading">取消</button>
        <button class="delete-dialog-btn confirm-btn" :disabled="deleteLoading" @click="confirmDelete">
          {{ deleteLoading ? '删除中...' : '确认删除' }}
        </button>
      </div>
    </div>
  </div>

  <!-- Mobile -->
  <div v-else class="model-mobile">
    <!-- Toolbar: search + create -->
    <div class="mm-toolbar">
      <div class="mm-search">
        <input v-model="searchKeyword" placeholder="搜索模型..." @keyup.enter="searchModels" />
      </div>
      <button class="mm-create-btn" @click="openCreateDialog">+ 添加</button>
    </div>

    <!-- Model list -->
    <div class="mm-list" v-if="models.length > 0">
      <div
        v-for="model in models"
        :key="model.llm_id"
        class="mm-item"
      >
        <div class="mm-item__icon"><Icon icon="mdi:brain" :width="20" :height="20" /></div>
        <div class="mm-item__content">
          <h3 class="mm-item__name">{{ model.model }}</h3>
          <p class="mm-item__provider">{{ model.provider }}</p>
        </div>
        <div class="mm-item__actions">
          <button class="mm-action" @click="openEditDialog(model)"><Icon icon="mdi:pencil" :width="16" :height="16" /></button>
          <button class="mm-action mm-action--danger" @click="deleteModel(model)"><Icon icon="mdi:delete" :width="16" :height="16" /></button>
        </div>
      </div>
    </div>

    <div v-else class="mm-empty">
      <p>暂无模型</p>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@use '../../styles/breakpoints.scss' as *;
.model-page {
  padding: 32px;
  min-height: 100%;
  background: transparent;
  
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    background: rgba(255, 255, 255, 0.5);
    backdrop-filter: blur(60px);
    -webkit-backdrop-filter: blur(60px);
    padding: var(--harmony-padding-level16) var(--harmony-padding-level16);
    border-radius: var(--harmony-corner-radius-level8);
    box-shadow: var(--harmony-shadow-lg);
    
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
      align-items: center;
      gap: 16px;
      
      .search-box {
        margin-right: 12px;
      }

      .action-buttons {
        display: flex;
        gap: 12px;

        .h-button {
          border-radius: var(--harmony-corner-radius-level6);
          padding: 12px 20px;
          font-size: var(--harmony-font-size-body-m);
          font-weight: 500;
          transition: all 0.3s;
          
          &:hover {
            transform: translateY(-2px);
          }
          
          &.refresh-btn {
            &:hover {
              background-color: var(--harmony-confirm);
              border-color: var(--harmony-confirm);
              color: white;
            }
          }
          
          &.add-btn {
            background: var(--harmony-brand);
            border: none;
            box-shadow: 0 4px 12px var(--harmony-comp-emphasize-tertiary);
            
            &:hover {
              background: var(--harmony-brand);
              box-shadow: 0 6px 16px var(--harmony-comp-emphasize-tertiary);
            }
          }
        }
      }
    }
  }
  
  // 列表容器
  .model-container {
    background: var(--harmony-comp-background-primary);
    border-radius: var(--harmony-corner-radius-level8);
    overflow: hidden;
    box-shadow: var(--harmony-shadow-sm);
    min-height: 300px;

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
      .col-provider { flex: 0 0 120px; }
      .col-type { flex: 0 0 120px; text-align: center; padding-right: 64px; }
      .col-url { flex: 1; min-width: 200px; padding-left: 32px; }
      .col-actions { flex: 0 0 100px; text-align: right; }
    }

    // 列表内容
    .model-list {
      .model-row {
        display: flex;
        align-items: center;
        padding: var(--harmony-padding-level10) var(--harmony-padding-level16);
        transition: all 0.2s ease;

        &:last-child {
        }

        &:hover {
          background: var(--harmony-comp-background-primary);

          .col-name .name-info .provider-avatar {
            transform: scale(1.05);
            box-shadow: 0 0 0 3px var(--harmony-comp-emphasize-tertiary);
          }

          .col-actions .action-btn {
            opacity: 1;
          }
        }

        .col-name {
          flex: 0 0 240px;

          .name-info {
            display: flex;
            align-items: center;
            gap: 12px;

            .provider-avatar {
              width: 36px;
              height: 36px;
              border-radius: var(--harmony-corner-radius-level6);
              display: flex;
              align-items: center;
              justify-content: center;
              flex-shrink: 0;
              transition: all 0.2s ease;
              color: white;
              font-size: var(--harmony-font-size-body-l);
              font-weight: 700;

              &.llm {
                background: var(--harmony-brand);
              }
              &.embedding {
                background: linear-gradient(135deg, var(--harmony-confirm) 0%, var(--harmony-confirm) 100%);
              }
              &.rerank {
                background: linear-gradient(135deg, var(--harmony-alert) 0%, var(--harmony-alert) 100%);
              }
            }

            .model-name {
              font-size: var(--harmony-font-size-body-l);
              font-weight: 600;
              color: var(--harmony-font-primary);
              white-space: nowrap;
              overflow: hidden;
              text-overflow: ellipsis;
            }

            .official-tag {
              font-size: var(--harmony-font-size-caption-l);
              font-weight: 600;
              color: var(--harmony-alert);
              background: var(--harmony-alert-bg);
              border: 1px solid var(--harmony-alert-bg);
              border-radius: var(--harmony-corner-radius-level18);
              padding: 2px 8px;
              flex-shrink: 0;
            }
          }
        }

        .col-provider {
          flex: 0 0 120px;
          padding-right: 8px;

          .provider-name {
            font-size: var(--harmony-font-size-body-m);
            font-weight: 500;
            color: var(--harmony-font-secondary);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
          }
        }

        .col-type {
          flex: 0 0 120px;
          text-align: center;
          padding-right: 64px;

          .type-badge {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 4px 10px;
            border-radius: var(--harmony-corner-radius-level18);
            font-size: var(--harmony-font-size-subtitle-s);
            font-weight: 500;

            &.llm {
              background: var(--harmony-comp-emphasize-tertiary);
              color: var(--harmony-brand);
            }
            &.embedding {
              background: var(--harmony-confirm-bg);
              color: var(--harmony-confirm);
            }
            &.rerank {
              background: var(--harmony-alert-bg);
              color: var(--harmony-alert);
            }
          }
        }

        .col-url {
          flex: 1;
          min-width: 200px;
          padding-left: 32px;
          padding-right: 16px;

          .url-text {
            font-size: var(--harmony-font-size-subtitle-s);
            color: var(--harmony-font-secondary);
            font-family: var(--harmony-font-family);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            display: block;
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
            opacity: 0.6;
            background: transparent;

            span {
              font-size: var(--harmony-font-size-body-l);
            }

            &.edit-btn {
              color: var(--harmony-brand);

              &:hover:not(.disabled) {
                background: var(--harmony-comp-emphasize-tertiary);
                border-color: var(--harmony-comp-emphasize-tertiary);
                opacity: 1;
              }
            }

            &.delete-btn {
              color: var(--harmony-warning);

              &:hover:not(.disabled) {
                background: var(--harmony-warning-bg);
                border-color: var(--harmony-warning-bg);
                opacity: 1;
              }
            }

            &.disabled {
              opacity: 0.3;
              cursor: not-allowed;
            }
          }
        }
      }
    }

    // 空状态
    .empty-state {
      text-align: center;
      padding: 80px 30px;

      .empty-icon {
        margin-bottom: 16px;

        .empty-emoji {
          font-size: 56px;
          opacity: 0.6;
        }
      }

      h3 {
        font-size: var(--harmony-font-size-title-s);
        font-weight: 600;
        color: var(--harmony-font-secondary);
        margin-bottom: 8px;
      }

      p {
        font-size: var(--harmony-font-size-body-m);
        color: var(--harmony-font-tertiary);
        margin-bottom: 24px;
      }

      .h-button {
        border-radius: var(--harmony-corner-radius-level6);
        background: var(--harmony-brand);
        border: none;
        box-shadow: 0 4px 12px var(--harmony-comp-emphasize-tertiary);
        transition: all 0.3s;

        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 6px 16px var(--harmony-comp-emphasize-tertiary);
          background: var(--harmony-brand);
        }
      }
    }
  }
}

/* 加载中遮罩 */
.loading-overlay {
  position: absolute;
  inset: 0;
  background: var(--harmony-comp-background-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-dropdown);
  border-radius: inherit;
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 3px solid var(--harmony-comp-background-secondary);
  border-top-color: var(--harmony-brand);
  border-radius: var(--harmony-corner-radius-level18);
  animation: h-spin 0.6s linear infinite;
}


// 响应式调整
@include mobile {
  .model-page {
    padding: 20px;

    .page-header {
      flex-direction: column;
      align-items: stretch;
      gap: 16px;
      padding: 20px;

      h2 {
        text-align: center;
        justify-content: center;
      }

      .header-actions {
        flex-direction: column;
        align-items: stretch;

        .search-box {
          margin-right: 0;
          margin-bottom: 12px;
        }

        .action-buttons {
          justify-content: center;
        }
      }
    }

    .model-container {
      .list-header {
        display: none;
      }

      .model-list .model-row {
        flex-wrap: wrap;
        gap: 8px;

        .col-name { flex: 1 1 100%; }
        .col-provider { flex: 1 1 50%; }
        .col-type { flex: 1 1 50%; text-align: left; }
        .col-url { flex: 1 1 100%; }
        .col-actions { flex: 1 1 100%; justify-content: flex-start; }
      }
    }
  }
}

/* 添加模型对话框样式 */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--harmony-comp-background-secondary);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-dialog);
  padding: 20px;
  animation: harmony-fade-in 0.3s ease-out;
}





.dialog-container {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: var(--harmony-comp-background-primary);
  border-radius: var(--harmony-corner-radius-level18);
  box-shadow: 
    0 20px 60px var(--harmony-shadow-dialog),
    0 8px 32px var(--harmony-shadow-md);
  width: 92%;
  max-width: 500px;
  max-height: 88vh;
  overflow: hidden;
  animation: harmony-slide-up 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  border: 1px solid var(--harmony-comp-background-secondary);
}



/* 对话框主体 */
.dialog-body {
  padding: 36px;
  max-height: 65vh;
  overflow-y: auto;
  background: var(--harmony-comp-background-primary);
}

.form-row {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-item {
  flex: 1;
  min-width: 0;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-size: var(--harmony-font-size-body-l);
  font-weight: 600;
  color: var(--harmony-font-primary);
}

.label-text {
  color: var(--harmony-font-primary);
}

.required-mark {
  color: var(--harmony-warning);
  font-weight: 700;
  font-size: var(--harmony-font-size-body-l);
}

.input-wrapper,
.select-wrapper {
  position: relative;
}

.api-key-wrapper {
  display: flex;
  align-items: center;
}

.toggle-password {
  position: absolute;
  right: 14px;
  top: 50%;
  transform: translateY(-50%);
  cursor: pointer;
  color: var(--harmony-font-tertiary);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s ease;

  span {
    font-size: var(--harmony-font-size-title-s);
  }

  &:hover {
    color: var(--harmony-brand);
  }
}

.form-input {
  width: 100%;
  padding: 16px 20px;
  border: 2px solid var(--harmony-comp-divider);
  border-radius: var(--harmony-corner-radius-level8);
  font-size: var(--harmony-font-size-body-l);
  font-weight: 500;
  color: var(--harmony-font-primary);
  background: var(--harmony-comp-background-primary);
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.form-input:focus {
  border-color: var(--harmony-brand);
  box-shadow: 0 0 0 4px var(--harmony-comp-emphasize-tertiary);
  transform: translateY(-1px);
}

.form-input::placeholder {
  color: var(--harmony-font-tertiary);
  font-weight: 400;
}

.char-count {
  position: absolute;
  right: 16px;
  bottom: -24px;
  font-size: var(--harmony-font-size-body-s);
  color: var(--harmony-font-secondary);
  font-weight: 500;
}

/* 对话框底部 */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  padding: 20px 36px;
  background: var(--harmony-comp-background-primary);
}

.dialog-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 28px;
  border: none;
  border-radius: var(--harmony-corner-radius-level8);
  font-size: var(--harmony-font-size-body-l);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 120px;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.dialog-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, var(--harmony-comp-background-secondary), transparent);
  transition: left 0.5s ease;
}

.dialog-btn:hover::before {
  left: 100%;
}

.cancel-btn {
  background: var(--harmony-comp-background-primary);
  color: var(--harmony-font-secondary);
  border: 2px solid var(--harmony-comp-divider);
}

.cancel-btn:hover {
  background: var(--harmony-comp-divider);
  color: var(--harmony-font-secondary);
  transform: translateY(-2px);
  box-shadow: var(--harmony-shadow-lg);
}

.confirm-btn {
  background: var(--harmony-comp-background-primary);
  color: var(--harmony-font-secondary);
  border: 2px solid var(--harmony-comp-divider);
}

.confirm-btn:hover:not(.disabled) {
  background: var(--harmony-comp-divider);
  color: var(--harmony-font-secondary);
  transform: translateY(-2px);
  box-shadow: var(--harmony-shadow-lg);
}

.confirm-btn.disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background: var(--harmony-font-tertiary);
}

.btn-icon {
  font-size: var(--harmony-font-size-body-l);
  display: flex;
  align-items: center;
}

.btn-icon.loading {
  animation: h-spin 1s linear infinite;
}



.btn-text {
  font-weight: 600;
}

/* 对话框响应式设计 */
@include mobile {
  .dialog-container {
    width: 95%;
    margin: 10px;
    max-height: 95vh;
  }
  
  .dialog-body {
    padding: 24px 20px;
  }
  
  .form-row {
    flex-direction: column;
    gap: 16px;
  }
  
  .dialog-footer {
    padding: 16px;
    flex-direction: column;
  }
  
  .dialog-btn {
    width: 100%;
  }
}

/* 删除确认对话框样式 */
.delete-dialog-container {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: var(--harmony-comp-background-primary);
  border-radius: var(--harmony-corner-radius-level8);
  box-shadow: var(--harmony-shadow-lg);
  width: 90%;
  max-width: 400px;
  overflow: hidden;
  animation: harmony-slide-up 0.3s ease-out;
}

.delete-dialog-body {
  padding: 32px 28px 24px;
  text-align: center;
  
  p {
    margin: 0;
    font-size: var(--harmony-font-size-body-l);
    color: var(--harmony-font-primary);
    line-height: 1.5;
    
    strong {
      color: var(--harmony-font-primary);
      font-weight: 600;
    }
  }
}

.delete-dialog-footer {
  display: flex;
  gap: 12px;
  padding: 0 28px 28px;
}

.delete-dialog-btn {
  flex: 1;
  padding: 12px 20px;
  border: none;
  border-radius: var(--harmony-corner-radius-level6);
  font-size: var(--harmony-font-size-body-m);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.delete-dialog-btn.cancel-btn {
  background: var(--harmony-comp-background-primary);
  color: var(--harmony-font-secondary);
  border: 1px solid var(--harmony-comp-divider);
}

.delete-dialog-btn.cancel-btn:hover:not(:disabled) {
  background: var(--harmony-comp-background-primary);
  color: var(--harmony-font-primary);
}

.delete-dialog-btn.confirm-btn {
  background: var(--harmony-brand);
  color: var(--harmony-comp-common-contrary, white);
  border: 1px solid var(--harmony-brand);
}

.delete-dialog-btn.confirm-btn:hover:not(:disabled) {
  background: var(--harmony-brand);
  border-color: var(--harmony-brand);
}

.delete-dialog-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 删除对话框响应式设计 */
@include mobile {
  .delete-dialog-container {
    width: 95%;
    margin: 10px;
  }
  
  .delete-dialog-body {
    padding: 24px 20px 20px;
    
    p {
      font-size: var(--harmony-font-size-body-l);
    }
  }
  
  .delete-dialog-footer {
    padding: 0 20px 24px;
  }
}

/* ==================== MOBILE: hmos mobile-list ==================== */
.model-mobile {
  display: flex;
  flex-direction: column;
  gap: var(--harmony-section-gap-mobile, 16px);
  padding-top: var(--harmony-padding-level8, 16px);
}

.mm-toolbar {
  display: flex;
  gap: var(--harmony-padding-level4, 8px);
  align-items: center;
}

.mm-search {
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
    &:focus { border-color: var(--harmony-brand); outline: none; }
    &::placeholder { color: var(--harmony-font-tertiary); }
  }
}

.mm-create-btn {
  height: var(--harmony-control-height-40, 40px);
  padding: 0 var(--harmony-padding-level8, 16px);
  background: var(--harmony-brand);
  color: var(--harmony-comp-common-contrary, white);
  border: none;
  border-radius: var(--harmony-corner-radius-level6, 12px);
  font-size: var(--harmony-font-size-body-m);
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  flex-shrink: 0;
}

.mm-list {
  display: flex;
  flex-direction: column;
  gap: var(--harmony-card-gap-mobile, 12px);
}

.mm-item {
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
    font-size: var(--harmony-font-size-body-l, 16px);
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
  }

  &__provider {
    font-size: var(--harmony-font-size-body-s);
    color: var(--harmony-font-secondary);
    margin: 0;
  }

  &__actions {
    display: flex;
    gap: var(--harmony-padding-level2, 4px);
    flex-shrink: 0;
  }
}

.mm-action {
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
  &--danger:active { background: var(--harmony-alert-bg, rgba(232, 64, 38, 0.1)); }
}

.mm-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--harmony-padding-level16, 32px) 0;
  p { font-size: var(--harmony-font-size-body-m); color: var(--harmony-font-tertiary); margin: 0; }
}
</style>
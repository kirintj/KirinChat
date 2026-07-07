<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { HButton, HInput, HSelect, HOption, HForm, HFormItem, HMessage } from '@/components/ui'
import { showConfirm } from '@/utils/dialog'
import { 
  getVisibleLLMsAPI, 
  updateLLMAPI, 
  deleteLLMAPI, 
  getLLMSchemaAPI,
  type LLMResponse,
  type UpdateLLMRequest
} from '../../apis/llm'

const router = useRouter()
const route = useRoute()

// 响应式数据
const loading = ref(false)
const currentModel = ref<LLMResponse | null>(null)

// 表单相关
const editFormRef = ref<any>()

const editForm = reactive<UpdateLLMRequest>({
  llm_id: '',
  model: '',
  api_key: '',
  base_url: '',
  provider: '',
  llm_type: ''
})

// 模型类型选项
const llmTypeOptions = [
  { label: 'LLM', value: 'LLM' },
  { label: 'Embedding', value: 'Embedding' },
  { label: 'Rerank', value: 'Rerank' }
]

// 表单验证规则
const formRules: Record<string, any> = {
  model: [
    { required: true, message: '请输入模型名称', trigger: 'blur' }
  ],
  api_key: [
    { required: true, message: '请输入API密钥', trigger: 'blur' }
  ],
  base_url: [
    { required: true, message: '请输入基础URL', trigger: 'blur' }
  ],
  provider: [
    { required: true, message: '请输入提供商', trigger: 'blur' }
  ],
  llm_type: [
    { required: true, message: '请选择模型类型', trigger: 'change' }
  ]
}

// 获取模型详情
const fetchModelDetail = async () => {
  const modelId = route.query.id as string
  if (!modelId) {
    HMessage.error('缺少模型ID参数')
    router.push('/model')
    return
  }

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
      
      const targetModel = allModels.find(model => model.llm_id === modelId)
      if (targetModel) {
        // 检查是否为官方模型
        if (targetModel.user_id === '0') {
          HMessage.warning('官方模型不可编辑，请返回模型列表')
          setTimeout(() => {
            router.push('/model')
          }, 1500)
          return
        }
        
        currentModel.value = targetModel
        // 填充表单
        Object.assign(editForm, {
          llm_id: targetModel.llm_id,
          model: targetModel.model,
          api_key: targetModel.api_key,
          base_url: targetModel.base_url,
          provider: targetModel.provider,
          llm_type: targetModel.llm_type
        })
      } else {
        HMessage.error('未找到指定的模型')
        router.push('/model')
      }
    } else {
      HMessage.error(response.data.status_message || '获取模型详情失败')
      router.push('/model')
    }
  } catch (error) {
    HMessage.error('获取模型详情失败')
    console.error('获取模型详情失败:', error)
    router.push('/model')
  } finally {
    loading.value = false
  }
}

// 返回模型管理页面
const goBack = () => {
  router.push('/model')
}

// 更新模型
const handleUpdate = async () => {
  // Manual validation
  if (!editForm.model) {
    HMessage.warning('请输入模型名称')
    return
  }
  if (!editForm.api_key) {
    HMessage.warning('请输入API密钥')
    return
  }
  if (!editForm.base_url) {
    HMessage.warning('请输入基础URL')
    return
  }
  if (!editForm.provider) {
    HMessage.warning('请输入提供商')
    return
  }
  if (!editForm.llm_type) {
    HMessage.warning('请选择模型类型')
    return
  }

  try {
    const response = await updateLLMAPI(editForm)

    if (response.data.status_code === 200) {
      HMessage.success('更新成功')
      router.push('/model')
    } else {
      HMessage.error(response.data.status_message || '更新失败')
    }
  } catch (error) {
    HMessage.error('更新失败')
    console.error('更新模型失败:', error)
  }
}

// 删除模型
const handleDelete = async () => {
  if (!currentModel.value) return
  
  // 检查是否为官方模型
  if (currentModel.value.user_id === '0') {
    HMessage.warning('⚠️ 官方模型不可删除')
    return
  }
  
  try {
    await showConfirm(
      `确定要删除模型"${currentModel.value.model}"吗？删除后无法恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
      }
    )
    
    const response = await deleteLLMAPI({ llm_id: currentModel.value.llm_id })
    
    if (response.data.status_code === 200) {
      HMessage.success('删除成功')
      router.push('/model')
    } else {
      HMessage.error(response.data.status_message || '删除失败')
    }
  } catch (error: any) {
    if (error?.message !== 'cancel') {
      console.error('删除模型失败:', error)
      HMessage.error('删除失败')
    }
  }
}

// 测试模型连接
const testModel = async () => {
  if (!currentModel.value) return
  
  HMessage.info(`正在测试 ${currentModel.value.model} 连接...`)
  // 这里可以添加实际的测试逻辑
  setTimeout(() => {
    HMessage.success(`${currentModel.value!.model} 连接测试完成`)
  }, 2000)
}

onMounted(() => {
  fetchModelDetail()
})
</script>

<template>
  <div class="model-editor-page" v-h-loading="loading">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <div class="breadcrumb">
          <span class="breadcrumb-item clickable" @click="goBack">模型管理</span>
          <span class="breadcrumb-separator">></span>
          <span class="breadcrumb-item active">编辑模型</span>
        </div>
      </div>
      
      <div class="header-title">
        <div class="title-icon" style="display:flex;align-items:center;justify-content:center;">
          ⚙️
        </div>
        <h2>编辑模型</h2>
      </div>
    </div>

    <!-- 编辑表单 -->
    <div v-if="currentModel" class="edit-form-section">
      <div class="form-container">
        <div class="form-header">
          <div class="form-icon" style="display:flex;align-items:center;justify-content:center;font-size:28px;">
            🤖
          </div>
          <div class="form-title">
            <h3>模型配置</h3>
            <p>修改模型的基本信息和连接配置</p>
          </div>
        </div>
        
        <HForm
          ref="editFormRef"
          :model="editForm"
          :rules="formRules"
          label-width="120px"
          label-position="left"
          class="edit-form"
        >
          <div class="form-section">
            <h4 class="section-title">基本信息</h4>
            <div class="form-row">
              <HFormItem label="模型名称" prop="model">
                <HInput
                  v-model="editForm.model"
                  placeholder="请输入模型名称，如：gpt-4"
                  clearable
                  class="form-input"
                />
              </HFormItem>

              <HFormItem label="提供商" prop="provider">
                <HInput
                  v-model="editForm.provider"
                  placeholder="请输入提供商，如：OpenAI"
                  clearable
                  class="form-input"
                />
              </HFormItem>
            </div>

            <div class="form-row">
              <HFormItem label="模型类型" prop="llm_type">
                <HSelect
                  v-model="editForm.llm_type"
                  placeholder="请选择模型类型"
                  class="form-select"
                  clearable
                >
                  <HOption
                    v-for="option in llmTypeOptions"
                    :key="option.value"
                    :label="option.label"
                    :value="option.value"
                  />
                </HSelect>
              </HFormItem>
            </div>
          </div>

          <div class="form-section">
            <h4 class="section-title">连接配置</h4>
            <div class="form-row">
              <HFormItem label="基础URL" prop="base_url">
                <HInput
                  v-model="editForm.base_url"
                  placeholder="请输入基础URL，如：https://api.openai.com/v1"
                  clearable
                  class="form-input"
                />
              </HFormItem>
            </div>

            <div class="form-row">
              <HFormItem label="API密钥" prop="api_key">
                <HInput
                  v-model="editForm.api_key"
                  placeholder="请输入API密钥"
                  showPassword
                  clearable
                  class="form-input"
                />
              </HFormItem>
            </div>
          </div>

          <HFormItem>
            <div class="form-actions">
              <HButton type="secondary" @click="goBack" class="action-btn cancel-btn">
                ✕ 取消
              </HButton>
              <HButton
                type="primary"
                @click="handleUpdate"
                class="action-btn primary-btn"
              >
                ✓ 保存更改
              </HButton>
            </div>
          </HFormItem>
        </HForm>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else-if="!loading" class="empty-state">
      <div class="empty-icon" style="font-size:80px;color:#cbd5e1;margin-bottom:24px;">
        ✕
      </div>
      <h3>未找到模型</h3>
      <p>请检查模型ID是否正确</p>
      <HButton
        type="primary"
        @click="goBack"
        size="large"
      >
        ← 返回模型管理
      </HButton>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.model-editor-page {
  padding: 24px;
  height: 100%;
  background: var(--harmony-comp-background-primary);
  min-height: 100vh;
  
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 32px;
    background: var(--harmony-comp-background-primary);
    padding: var(--harmony-padding-level16) var(--harmony-padding-level16);
    border-radius: var(--harmony-corner-radius-level8);
    box-shadow: 0 4px 20px var(--harmony-shadow-sm);
    border: 1px solid var(--harmony-comp-divider);

          .header-left {
        display: flex;
        align-items: center;
        gap: 20px;
        
        .breadcrumb {
          display: flex;
          align-items: center;
          gap: 12px;
          font-size: var(--harmony-font-size-body-l);
          color: var(--harmony-font-tertiary);
          
          .breadcrumb-item {
            transition: all 0.3s ease;
            padding: 8px 12px;
            border-radius: var(--harmony-corner-radius-level6);
            cursor: default;
            
            &.clickable {
              cursor: pointer;
              color: var(--harmony-font-secondary);
              font-weight: 500;
              
              &:hover {
                color: var(--harmony-brand));
                background: var(--harmony-comp-emphasize-tertiary);
                transform: translateY(-1px);
              }
              
              &:active {
                transform: translateY(0);
              }
            }
            
            &.active {
              color: var(--harmony-brand));
              font-weight: 600;
              background: var(--harmony-comp-emphasize-tertiary);
            }
          }
          
          .breadcrumb-separator {
            color: var(--harmony-comp-divider);
            font-weight: 500;
          }
        }
      }
    
    .header-title {
      display: flex;
      align-items: center;
      gap: 16px;
      
      .title-icon {
        width: 48px;
        height: 48px;
        background: var(--harmony-brand));
        border-radius: var(--harmony-corner-radius-level8);
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 8px 20px var(--harmony-comp-emphasize-tertiary);
      }
      
      h2 {
        margin: 0;
        font-size: var(--harmony-font-size-title-m);
        font-weight: 700;
        background: linear-gradient(135deg, var(--harmony-font-primary) 0%, var(--harmony-font-secondary) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
      }
    }
  }
  
  .edit-form-section {
    .form-container {
      background: var(--harmony-comp-background-primary);
      border-radius: var(--harmony-corner-radius-level18);
      padding: 32px;
      box-shadow: 0 8px 32px var(--harmony-shadow-sm);
      border: 1px solid var(--harmony-comp-divider);
      
      .form-header {
        display: flex;
        align-items: center;
        gap: 20px;
        margin-bottom: 32px;
        padding-bottom: 24px;
        border-bottom: 2px solid var(--harmony-comp-background-primary);
        
        .form-icon {
          width: 56px;
          height: 56px;
          background: linear-gradient(135deg, var(--harmony-confirm) 0%, var(--harmony-confirm) 100%);
          border-radius: var(--harmony-corner-radius-level8);
          display: flex;
          align-items: center;
          justify-content: center;
          box-shadow: 0 8px 20px var(--harmony-confirm-bg);
        }
        
                  .form-title {
            h3 {
              margin: 0 0 12px 0;
              font-size: var(--harmony-font-size-title-m);
              font-weight: 800;
              background: linear-gradient(135deg, var(--harmony-font-primary) 0%, var(--harmony-font-secondary) 100%);
              -webkit-background-clip: text;
              -webkit-text-fill-color: transparent;
              background-clip: text;
              letter-spacing: -0.5px;
            }
            
            p {
              margin: 0;
              font-size: var(--harmony-font-size-body-l);
              color: var(--harmony-font-secondary);
              line-height: 1.6;
              font-weight: 500;
            }
          }
      }
      
      .edit-form {
        .form-section {
          margin-bottom: 32px;
          
          .section-title {
            font-size: var(--harmony-font-size-title-s);
            font-weight: 600;
            color: var(--harmony-font-primary);
            margin: 0 0 20px 0;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--harmony-comp-divider);
            position: relative;
            
            &::before {
              content: '';
              position: absolute;
              bottom: -1px;
              left: 0;
              width: 40px;
              height: 2px;
              background: var(--harmony-brand));
              border-radius: 1px;
            }
          }
          
          .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
            margin-bottom: 20px;
            
            &:last-child {
              margin-bottom: 0;
            }
            
            .h-form-item {
              margin-bottom: 0;
            }
          }

          .form-input,
          .form-select {
            .h-input {
              background: var(--harmony-comp-background-primary);
              border: 2px solid var(--harmony-comp-divider);
              border-radius: var(--harmony-corner-radius-level8);
              padding: 16px 20px;
              transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
              box-shadow: 0 2px 8px var(--harmony-shadow-xs);
              position: relative;
              overflow: hidden;

              &:hover {
                border-color: var(--harmony-comp-divider);
                background: linear-gradient(135deg, var(--harmony-comp-background-primary) 0%, var(--harmony-comp-divider) 100%);
                box-shadow: 0 4px 12px var(--harmony-shadow-sm);
                transform: translateY(-1px);
              }

              &.h-input--focused {
                border-color: var(--harmony-brand));
                background: var(--harmony-comp-background-primary);
                box-shadow: 0 0 0 4px var(--harmony-comp-emphasize-tertiary), 0 8px 24px var(--harmony-shadow-md);
                transform: translateY(-2px);
              }
            }

            .h-input__inner {
              font-size: var(--harmony-font-size-body-l);
              color: var(--harmony-font-primary);
              font-weight: 500;

              &::placeholder {
                color: var(--harmony-font-tertiary);
                font-weight: 400;
              }
            }
          }

          .h-form-item__label {
            font-weight: 700;
            color: var(--harmony-font-primary);
            font-size: var(--harmony-font-size-body-l);
            position: relative;
            
            &::before {
              content: '*';
              color: var(--harmony-warning);
              margin-right: 4px;
              font-weight: 800;
            }
          }
        }
        
        .form-actions {
          display: flex;
          justify-content: center;
          align-items: center;
          gap: 20px;
          margin-top: 40px;
          padding-top: 32px;
          border-top: 2px solid var(--harmony-comp-background-primary);
          
          .action-btn {
            padding: 16px 32px;
            border-radius: var(--harmony-corner-radius-level8);
            font-weight: 700;
            font-size: var(--harmony-font-size-body-l);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            border: 2px solid transparent;
            min-width: 140px;
            position: relative;
            overflow: hidden;
            
            &::before {
              content: '';
              position: absolute;
              top: 0;
              left: -100%;
              width: 100%;
              height: 100%;
              background: linear-gradient(90deg, transparent, var(--harmony-comp-background-secondary), transparent);
              transition: left 0.5s ease;
            }
            
            &:hover {
              transform: translateY(-3px);
              box-shadow: 0 12px 28px rgba(0, 0, 0, 0.2);
              
              &::before {
                left: 100%;
              }
            }
            
            &:active {
              transform: translateY(-1px);
            }
            
            &.cancel-btn {
              background: var(--harmony-comp-background-primary);
              border-color: var(--harmony-comp-divider);
              color: var(--harmony-font-secondary);
              
              &:hover {
                border-color: var(--harmony-comp-divider);
                background: var(--harmony-comp-background-primary);
                color: var(--harmony-font-secondary);
              }
            }
            
            &.primary-btn {
              background: var(--harmony-brand));
              border-color: transparent;
              color: white;
              
              &:hover {
                background: var(--harmony-brand));
                box-shadow: 0 12px 28px var(--harmony-comp-emphasize-tertiary);
              }
            }
          }
        }
      }
    }
  }
  
  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    text-align: center;
    background: var(--harmony-comp-background-primary);
    border-radius: var(--harmony-corner-radius-level18);
    padding: 80px 40px;
    box-shadow: 0 8px 32px var(--harmony-shadow-sm);
    
    .empty-icon {
      font-size: 80px;
      color: var(--harmony-comp-divider);
      margin-bottom: 24px;
    }
    
    h3 {
      margin: 0 0 12px 0;
      font-size: var(--harmony-font-size-title-m);
      font-weight: 600;
      color: var(--harmony-font-secondary);
    }
    
    p {
      margin: 0 0 32px 0;
      color: var(--harmony-font-secondary);
      font-size: var(--harmony-font-size-body-l);
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .model-editor-page {
    padding: 16px;
    
         .page-header {
       flex-direction: column;
       gap: 20px;
       padding: 20px;
       
       .header-left {
         justify-content: center;
         
         .breadcrumb {
           font-size: var(--harmony-font-size-body-m);
           
           .breadcrumb-item {
             padding: 6px 10px;
           }
         }
       }
     }
    
    .edit-form-section .form-container {
      padding: 24px;
      
      .form-header {
        flex-direction: column;
        text-align: center;
        gap: 16px;
      }
      
      .edit-form .form-section .form-row {
        grid-template-columns: 1fr;
        gap: 16px;
      }
      
             .edit-form .form-actions {
         flex-direction: column;
         gap: 16px;
         
         .action-btn {
           width: 100%;
           max-width: 200px;
         }
       }
    }
  }
}
</style> 
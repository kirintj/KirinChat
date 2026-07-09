<script setup lang="ts">
import { ref, onMounted, inject } from 'vue'
import { useRouter } from 'vue-router'
import { HMessage, HButton, HTooltip } from '@/components/ui'
import {
  getKnowledgeListAPI,
  createKnowledgeAPI,
  updateKnowledgeAPI,
  deleteKnowledgeAPI,
  KnowledgeResponse,
  type KnowledgeDeleteRequest,
  type KnowledgeCreateRequest,
  type KnowledgeUpdateRequest
} from '../../apis/knowledge'
import { KnowledgeListType } from '../../type'

const router = useRouter()
const isMobile = inject<import('vue').Ref<boolean>>('isMobile', ref(false))
const knowledges = ref<KnowledgeListType[]>([])
const loading = ref(false)

// 创建知识库对话框
const createDialogVisible = ref(false)
const createForm = ref({
  knowledge_name: '',
  knowledge_desc: ''
})
const createLoading = ref(false)

// 编辑知识库对话框
const editDialogVisible = ref(false)
const editForm = ref({
  knowledge_id: '',
  knowledge_name: '',
  knowledge_desc: ''
})
const editLoading = ref(false)
const currentEditKnowledge = ref<KnowledgeListType | null>(null)

// 获取知识库列表
const fetchKnowledges = async () => {
  loading.value = true
  try {
         const response = await getKnowledgeListAPI()
     if (response.data.status_code === 200 && response.data.data) {
       knowledges.value = response.data.data.map((item: KnowledgeResponse) => ({
         id: item.id,
         name: item.name,
         description: item.description,
         user_id: item.user_id,
         create_time: item.create_time,
         update_time: item.update_time,
         count: item.count,
         file_size: item.file_size
       }))
     } else {
      HMessage.error('获取知识库列表失败: ' + response.data.status_message)
    }
  } catch (error) {
    console.error('获取知识库列表失败:', error)
    HMessage.error('获取知识库列表失败')
  } finally {
    loading.value = false
  }
}

// 删除知识库对话框控制
const deleteDialogVisible = ref(false)
const deleteLoading = ref(false)
const knowledgeToDelete = ref<KnowledgeListType | null>(null)

// 删除知识库
const handleDelete = async (knowledge: KnowledgeListType) => {
  // 显示删除确认对话框
  knowledgeToDelete.value = knowledge
  deleteDialogVisible.value = true
}

// 确认删除知识库
const confirmDelete = async () => {
  if (!knowledgeToDelete.value) return
  
  deleteLoading.value = true
  try {
    const deleteData: KnowledgeDeleteRequest = {
      knowledge_id: knowledgeToDelete.value.id
    }
    
    const response = await deleteKnowledgeAPI(deleteData)
    if (response.data.status_code === 200) {
      HMessage.success('删除成功')
      deleteDialogVisible.value = false
      await fetchKnowledges() // 刷新列表
    } else {
      HMessage.error('删除失败: ' + response.data.status_message)
    }
  } catch (error: any) {
    console.error('删除知识库失败:', error)
    HMessage.error('删除失败')
  } finally {
    deleteLoading.value = false
  }
}

// 取消删除
const cancelDelete = () => {
  deleteDialogVisible.value = false
  knowledgeToDelete.value = null
}

// 格式化时间
const formatTime = (timeStr: string) => {
  if (!timeStr) return '-'
  return new Date(timeStr).toLocaleDateString('zh-CN')
}

// 跳转到文件管理页面
const goToFileManagement = (knowledge: KnowledgeListType) => {
  router.push({
    name: 'knowledge-file',
    params: { knowledgeId: knowledge.id },
    query: { name: knowledge.name }
  })
}

// 打开创建知识库对话框
const openCreateDialog = () => {
  createDialogVisible.value = true
  resetCreateForm()
}

// 重置创建表单
const resetCreateForm = () => {
  createForm.value = {
    knowledge_name: '',
    knowledge_desc: ''
  }
}

// 创建知识库
const handleCreate = async () => {
  const name = createForm.value.knowledge_name.trim()
  const desc = createForm.value.knowledge_desc.trim()
  
  if (!name) {
    HMessage.error('请输入知识库名称')
    return
  }
  
  if (name.length < 2 || name.length > 10) {
    HMessage.error('知识库名称长度必须在2-10个字符之间')
    return
  }
  
  if (desc && (desc.length < 10 || desc.length > 200)) {
    HMessage.error('知识库描述长度必须在10-200个字符之间')
    return
  }
  
  createLoading.value = true
  try {
    const requestData: KnowledgeCreateRequest = {
      knowledge_name: createForm.value.knowledge_name.trim(),
      ...(desc ? { knowledge_desc: desc } : {})
    }
    const response = await createKnowledgeAPI(requestData)
    if (response.data.status_code === 200) {
      HMessage.success('创建成功')
      createDialogVisible.value = false
      await fetchKnowledges() // 刷新列表
    } else {
      HMessage.error('创建失败: ' + response.data.status_message)
    }
  } catch (error) {
    console.error('创建知识库失败:', error)
    HMessage.error('创建失败')
  } finally {
    createLoading.value = false
  }
}

// 打开编辑知识库对话框
const openEditDialog = (knowledge: KnowledgeListType) => {
  currentEditKnowledge.value = knowledge
  editForm.value = {
    knowledge_id: knowledge.id,
    knowledge_name: knowledge.name,
    knowledge_desc: knowledge.description || ''
  }
  editDialogVisible.value = true
}

// 重置编辑表单
const resetEditForm = () => {
  editForm.value = {
    knowledge_id: '',
    knowledge_name: '',
    knowledge_desc: ''
  }
  currentEditKnowledge.value = null
}

// 编辑知识库
const handleEdit = async () => {
  const name = editForm.value.knowledge_name.trim()
  const desc = editForm.value.knowledge_desc.trim()
  
  if (!name) {
    HMessage.error('请输入知识库名称')
    return
  }
  
  if (name.length < 2 || name.length > 10) {
    HMessage.error('知识库名称长度必须在2-10个字符之间')
    return
  }
  
  if (desc && (desc.length < 10 || desc.length > 200)) {
    HMessage.error('知识库描述长度必须在10-200个字符之间')
    return
  }
  
  editLoading.value = true
  try {
    const updateData: KnowledgeUpdateRequest = {
      knowledge_id: editForm.value.knowledge_id,
      knowledge_name: editForm.value.knowledge_name.trim(),
      ...(desc ? { knowledge_desc: desc } : {})
    }
    
    const response = await updateKnowledgeAPI(updateData)
    if (response.data.status_code === 200) {
      HMessage.success('更新成功')
      editDialogVisible.value = false
      await fetchKnowledges() // 刷新列表
    } else {
      HMessage.error('更新失败: ' + response.data.status_message)
    }
  } catch (error) {
    console.error('更新知识库失败:', error)
    HMessage.error('更新失败')
  } finally {
    editLoading.value = false
  }
}

onMounted(() => {
  fetchKnowledges()
})
</script>

<template>
  <div class="knowledge-page page" v-if="!isMobile">
    <div class="page-header">
      <div class="header-title">
        <h2>知识库管理</h2>
      </div>
      <div class="header-actions">
        <HButton type="primary" @click="openCreateDialog">
          创建知识库
        </HButton>
      </div>
    </div>

    <div class="knowledge-container" style="position: relative;">
      <div v-if="loading" class="loading-overlay">
        <div class="loading-spinner"></div>
      </div>
      <!-- 列表头部 -->
      <div class="list-header" v-if="knowledges.length > 0">
        <div class="col-name">
          <span><Icon icon="mdi:folder" :width="14" :height="14" /></span>
          <span>名称</span>
        </div>
        <div class="col-desc">
          <span><Icon icon="mdi:file-document" :width="14" :height="14" /></span>
          <span>描述</span>
        </div>
        <div class="col-files">
          <span><Icon icon="mdi:file-document" :width="14" :height="14" /></span>
          <span>文件数</span>
        </div>
        <div class="col-size">
          <Icon icon="mdi:folder-plus" :width="14" :height="14" />
          <span>存储大小</span>
        </div>
        <div class="col-time">
          <Icon icon="mdi:clock" :width="14" :height="14" />
          <span>创建时间</span>
        </div>
        <div class="col-actions">
          <Icon icon="mdi:pencil" :width="14" :height="14" />
          <span>操作</span>
        </div>
      </div>

      <!-- 列表内容 -->
      <div class="knowledge-list" v-if="knowledges.length > 0">
        <div
          v-for="knowledge in knowledges"
          :key="knowledge.id"
          class="knowledge-row"
          @click="goToFileManagement(knowledge)"
        >
          <div class="col-name">
            <div class="knowledge-info">
              <div class="knowledge-avatar">
                <Icon icon="mdi:book-open-page-variant" :width="20" :height="20" />
              </div>
              <span class="knowledge-name">{{ knowledge.name }}</span>
            </div>
          </div>
          <div class="col-desc">
            <span class="knowledge-desc">{{ knowledge.description || '-' }}</span>
          </div>
          <div class="col-files">
            <span class="file-badge">
              <Icon icon="mdi:file-document" :width="14" :height="14" />
              {{ knowledge.count }}
            </span>
          </div>
          <div class="col-size">
            <span class="size-text">{{ knowledge.file_size }}</span>
          </div>
          <div class="col-time">
            <span class="time-text">{{ formatTime(knowledge.create_time) }}</span>
          </div>
          <div class="col-actions" @click.stop>
            <HTooltip content="管理文件" placement="top">
              <button class="action-btn view-btn" @click.stop="goToFileManagement(knowledge)">
                <Icon icon="mdi:folder-open" :width="16" :height="16" />
              </button>
            </HTooltip>
            <HTooltip content="编辑" placement="top">
              <button class="action-btn edit-btn" @click.stop="openEditDialog(knowledge)">
                <Icon icon="mdi:pencil" :width="16" :height="16" />
              </button>
            </HTooltip>
            <HTooltip content="删除" placement="top">
              <button class="action-btn delete-btn" @click.stop="handleDelete(knowledge)">
                <Icon icon="mdi:delete" :width="16" :height="16" />
              </button>
            </HTooltip>
          </div>
        </div>
      </div>

      <div v-if="knowledges.length === 0 && !loading" class="empty-state">
        <div class="empty-icon">
          <Icon icon="mdi:book-open-page-variant" :width="48" :height="48" class="empty-icon-img" />
        </div>
        <h3>暂无知识库</h3>
        <p>您可以创建知识库来存储和管理您的文档资料</p>
        <HButton type="primary" @click="createDialogVisible = true" class="create-btn">
          创建知识库
        </HButton>
      </div>
    </div>

    <!-- 创建知识库对话框 -->
    <div v-if="createDialogVisible" class="dialog-overlay">
      <div class="dialog-container">
        <div class="dialog-header">
          <h3>创建知识库</h3>
          <button class="close-btn" @click="createDialogVisible = false">×</button>
        </div>

        <div class="dialog-body">
          <div class="form-item">
            <label>知识库名称 <span style="color: red;">*</span></label>
            <div class="input-with-count">
              <input
                v-model="createForm.knowledge_name"
                type="text"
                placeholder="请输入知识库名称（2-10个字符）"
                maxlength="10"
                :class="{ 'error': createForm.knowledge_name.length > 0 && (createForm.knowledge_name.length < 2 || createForm.knowledge_name.length > 10) }"
              />
              <span class="char-count" :class="{ 'error': createForm.knowledge_name.length < 2 || createForm.knowledge_name.length > 10 }">
                {{ createForm.knowledge_name.length }}/10
              </span>
            </div>
          </div>

          <div class="form-item">
            <label>知识库描述 <span style="color: var(--harmony-font-tertiary); font-size: var(--harmony-font-size-body-s);">(可选，10-200字符)</span></label>
            <div class="textarea-with-count">
              <textarea
                v-model="createForm.knowledge_desc"
                placeholder="请输入知识库描述（可选，10-200字符）"
                rows="4"
                maxlength="200"
                :class="{ 'error': createForm.knowledge_desc.length > 0 && (createForm.knowledge_desc.length < 10 || createForm.knowledge_desc.length > 200) }"
              ></textarea>
              <span class="char-count" :class="{ 'error': createForm.knowledge_desc.length > 0 && (createForm.knowledge_desc.length < 10 || createForm.knowledge_desc.length > 200) }">
                {{ createForm.knowledge_desc.length }}/200
              </span>
            </div>
          </div>
        </div>

        <div class="dialog-footer">
          <button @click="createDialogVisible = false">取消</button>
          <button
            class="primary-btn"
            :disabled="createLoading"
            @click="handleCreate"
          >
            {{ createLoading ? '创建中...' : '确定' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 编辑知识库对话框 -->
    <div v-if="editDialogVisible" class="dialog-overlay">
      <div class="dialog-container">
        <div class="dialog-header">
          <h3>编辑知识库</h3>
          <button class="close-btn" @click="editDialogVisible = false; resetEditForm()">×</button>
        </div>

        <div class="dialog-body">
          <div class="form-item">
            <label>知识库名称 <span style="color: red;">*</span></label>
            <div class="input-with-count">
              <input
                v-model="editForm.knowledge_name"
                type="text"
                placeholder="请输入知识库名称（2-10个字符）"
                maxlength="10"
                :class="{ 'error': editForm.knowledge_name.length > 0 && (editForm.knowledge_name.length < 2 || editForm.knowledge_name.length > 10) }"
              />
              <span class="char-count" :class="{ 'error': editForm.knowledge_name.length < 2 || editForm.knowledge_name.length > 10 }">
                {{ editForm.knowledge_name.length }}/10
              </span>
            </div>
          </div>

          <div class="form-item">
            <label>知识库描述 <span style="color: var(--harmony-font-tertiary); font-size: var(--harmony-font-size-body-s);">(可选，10-200字符)</span></label>
            <div class="textarea-with-count">
              <textarea
                v-model="editForm.knowledge_desc"
                placeholder="请输入知识库描述（可选，10-200字符）"
                rows="4"
                maxlength="200"
                :class="{ 'error': editForm.knowledge_desc.length > 0 && (editForm.knowledge_desc.length < 10 || editForm.knowledge_desc.length > 200) }"
              ></textarea>
              <span class="char-count" :class="{ 'error': editForm.knowledge_desc.length > 0 && (editForm.knowledge_desc.length < 10 || editForm.knowledge_desc.length > 200) }">
                {{ editForm.knowledge_desc.length }}/200
              </span>
            </div>
          </div>
        </div>

        <div class="dialog-footer">
          <button @click="editDialogVisible = false; resetEditForm()">取消</button>
          <button
            class="primary-btn"
            :disabled="editLoading"
            @click="handleEdit"
          >
            {{ editLoading ? '更新中...' : '确定' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 删除确认对话框 -->
    <div v-if="deleteDialogVisible" class="dialog-overlay" @click="cancelDelete">
      <div class="delete-dialog-container" @click.stop>
        <!-- 对话框主体 -->
        <div class="delete-dialog-body">
          <p v-if="knowledgeToDelete">
            确定要删除知识库 <strong>"{{ knowledgeToDelete.name }}"</strong> 吗？删除后无法恢复。
          </p>
        </div>

        <!-- 对话框底部 -->
        <div class="delete-dialog-footer">
          <button
            class="delete-dialog-btn cancel-btn"
            @click="cancelDelete"
            :disabled="deleteLoading"
          >
            取消
          </button>
          <button
            class="delete-dialog-btn confirm-btn"
            :disabled="deleteLoading"
            @click="confirmDelete"
          >
            {{ deleteLoading ? '删除中...' : '确认删除' }}
          </button>
        </div>
      </div>
    </div>
  </div>

  <div v-else class="knowledge-mobile">
    <!-- Create button -->
    <div class="km-header">
      <button class="km-create-btn" @click="openCreateDialog">+ 创建知识库</button>
    </div>

    <!-- Knowledge list as cards -->
    <div class="km-list" v-if="knowledges.length > 0">
      <div
        v-for="knowledge in knowledges"
        :key="knowledge.id"
        class="km-item"
        @click="goToFileManagement(knowledge)"
      >
        <div class="km-item__icon">
          <Icon icon="mdi:book-open-page-variant" :width="20" :height="20" />
        </div>
        <div class="km-item__content">
          <h3 class="km-item__name">{{ knowledge.name }}</h3>
          <p class="km-item__desc">{{ knowledge.description || '-' }}</p>
        </div>
        <div class="km-item__actions" @click.stop>
          <button class="km-action" @click.stop="goToFileManagement(knowledge)" title="管理文件"><Icon icon="mdi:folder" :width="16" :height="16" /></button>
          <button class="km-action" @click.stop="openEditDialog(knowledge)" title="编辑"><Icon icon="mdi:pencil" :width="16" :height="16" /></button>
          <button class="km-action km-action--danger" @click.stop="handleDelete(knowledge)" title="删除"><Icon icon="mdi:delete" :width="16" :height="16" /></button>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else-if="!loading" class="km-empty">
      <Icon icon="mdi:book-open-page-variant" :width="48" :height="48" />
      <p>暂无知识库</p>
      <button class="km-create-btn" @click="createDialogVisible = true">创建知识库</button>
    </div>

    <!-- 创建知识库对话框 -->
    <div v-if="createDialogVisible" class="dialog-overlay">
      <div class="dialog-container">
        <div class="dialog-header">
          <h3>创建知识库</h3>
          <button class="close-btn" @click="createDialogVisible = false">×</button>
        </div>

        <div class="dialog-body">
          <div class="form-item">
            <label>知识库名称 <span style="color: red;">*</span></label>
            <div class="input-with-count">
              <input
                v-model="createForm.knowledge_name"
                type="text"
                placeholder="请输入知识库名称（2-10个字符）"
                maxlength="10"
                :class="{ 'error': createForm.knowledge_name.length > 0 && (createForm.knowledge_name.length < 2 || createForm.knowledge_name.length > 10) }"
              />
              <span class="char-count" :class="{ 'error': createForm.knowledge_name.length < 2 || createForm.knowledge_name.length > 10 }">
                {{ createForm.knowledge_name.length }}/10
              </span>
            </div>
          </div>

          <div class="form-item">
            <label>知识库描述 <span style="color: var(--harmony-font-tertiary); font-size: var(--harmony-font-size-body-s);">(可选，10-200字符)</span></label>
            <div class="textarea-with-count">
              <textarea
                v-model="createForm.knowledge_desc"
                placeholder="请输入知识库描述（可选，10-200字符）"
                rows="4"
                maxlength="200"
                :class="{ 'error': createForm.knowledge_desc.length > 0 && (createForm.knowledge_desc.length < 10 || createForm.knowledge_desc.length > 200) }"
              ></textarea>
              <span class="char-count" :class="{ 'error': createForm.knowledge_desc.length > 0 && (createForm.knowledge_desc.length < 10 || createForm.knowledge_desc.length > 200) }">
                {{ createForm.knowledge_desc.length }}/200
              </span>
            </div>
          </div>
        </div>

        <div class="dialog-footer">
          <button @click="createDialogVisible = false">取消</button>
          <button
            class="primary-btn"
            :disabled="createLoading"
            @click="handleCreate"
          >
            {{ createLoading ? '创建中...' : '确定' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 编辑知识库对话框 -->
    <div v-if="editDialogVisible" class="dialog-overlay">
      <div class="dialog-container">
        <div class="dialog-header">
          <h3>编辑知识库</h3>
          <button class="close-btn" @click="editDialogVisible = false; resetEditForm()">×</button>
        </div>

        <div class="dialog-body">
          <div class="form-item">
            <label>知识库名称 <span style="color: red;">*</span></label>
            <div class="input-with-count">
              <input
                v-model="editForm.knowledge_name"
                type="text"
                placeholder="请输入知识库名称（2-10个字符）"
                maxlength="10"
                :class="{ 'error': editForm.knowledge_name.length > 0 && (editForm.knowledge_name.length < 2 || editForm.knowledge_name.length > 10) }"
              />
              <span class="char-count" :class="{ 'error': editForm.knowledge_name.length < 2 || editForm.knowledge_name.length > 10 }">
                {{ editForm.knowledge_name.length }}/10
              </span>
            </div>
          </div>

          <div class="form-item">
            <label>知识库描述 <span style="color: var(--harmony-font-tertiary); font-size: var(--harmony-font-size-body-s);">(可选，10-200字符)</span></label>
            <div class="textarea-with-count">
              <textarea
                v-model="editForm.knowledge_desc"
                placeholder="请输入知识库描述（可选，10-200字符）"
                rows="4"
                maxlength="200"
                :class="{ 'error': editForm.knowledge_desc.length > 0 && (editForm.knowledge_desc.length < 10 || editForm.knowledge_desc.length > 200) }"
              ></textarea>
              <span class="char-count" :class="{ 'error': editForm.knowledge_desc.length > 0 && (editForm.knowledge_desc.length < 10 || editForm.knowledge_desc.length > 200) }">
                {{ editForm.knowledge_desc.length }}/200
              </span>
            </div>
          </div>
        </div>

        <div class="dialog-footer">
          <button @click="editDialogVisible = false; resetEditForm()">取消</button>
          <button
            class="primary-btn"
            :disabled="editLoading"
            @click="handleEdit"
          >
            {{ editLoading ? '更新中...' : '确定' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 删除确认对话框 -->
    <div v-if="deleteDialogVisible" class="dialog-overlay" @click="cancelDelete">
      <div class="delete-dialog-container" @click.stop>
        <!-- 对话框主体 -->
        <div class="delete-dialog-body">
          <p v-if="knowledgeToDelete">
            确定要删除知识库 <strong>"{{ knowledgeToDelete.name }}"</strong> 吗？删除后无法恢复。
          </p>
        </div>

        <!-- 对话框底部 -->
        <div class="delete-dialog-footer">
          <button
            class="delete-dialog-btn cancel-btn"
            @click="cancelDelete"
            :disabled="deleteLoading"
          >
            取消
          </button>
          <button
            class="delete-dialog-btn confirm-btn"
            :disabled="deleteLoading"
            @click="confirmDelete"
          >
            {{ deleteLoading ? '删除中...' : '确认删除' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.knowledge-page {
  padding: 32px;
  min-height: 100%;
  background: transparent;
  
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    background: var(--harmony-comp-background-primary);
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
      .h-button {
        font-weight: 600;
        letter-spacing: 0.025em;
        border-radius: var(--harmony-corner-radius-level8);
        padding: var(--harmony-padding-level8) var(--harmony-padding-level16);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 25px var(--harmony-comp-emphasize-tertiary);
        }
      }
    }
  }
  
  .knowledge-container {
    background: var(--harmony-comp-background-primary);
    border-radius: var(--harmony-corner-radius-level8);
    box-shadow: var(--harmony-shadow-lg);
    overflow: hidden;
    
    .list-header {
      display: grid;
      grid-template-columns: 2fr 3fr 1fr 1fr 1.2fr 1.5fr;
      gap: 16px;
      padding: var(--harmony-padding-level10) var(--harmony-padding-level16);
      background: var(--harmony-comp-background-primary);
      border-bottom: 2px solid var(--harmony-comp-divider);
      font-weight: 600;
      font-size: var(--harmony-font-size-subtitle-s);
      color: var(--harmony-font-secondary);
      text-transform: uppercase;
      letter-spacing: 0.5px;
      
      > div {
        display: flex;
        align-items: center;
        gap: 6px;

        svg {
          font-size: var(--harmony-font-size-body-m);
          color: var(--harmony-font-tertiary);
        }
      }
    }
    
    .knowledge-list {
      .knowledge-row {
        display: grid;
        grid-template-columns: 2fr 3fr 1fr 1fr 1.2fr 1.5fr;
        gap: 16px;
        padding: var(--harmony-padding-level16) var(--harmony-padding-level16);
        border-bottom: 1px solid var(--harmony-comp-divider);
        transition: all 0.2s ease;
        cursor: pointer;
        align-items: center;
        
        &:hover {
          background: var(--harmony-interactive-hover);
          box-shadow: var(--harmony-shadow-sm);
        }
        
        &:last-child {
          border-bottom: none;
        }
        
        .col-name {
          .knowledge-info {
            display: flex;
            align-items: center;
            gap: 12px;
            
            .knowledge-avatar {
              width: 40px;
              height: 40px;
              border-radius: var(--harmony-corner-radius-level6);
              background: linear-gradient(135deg, var(--harmony-comp-emphasize-tertiary) 0%, var(--harmony-comp-emphasize-tertiary) 100%);
              display: flex;
              align-items: center;
              justify-content: center;
              flex-shrink: 0;
              
              img {
                width: 24px;
                height: 24px;
              }
            }
            
            .knowledge-name {
              font-size: var(--harmony-font-size-body-l);
              font-weight: 600;
              color: var(--harmony-font-primary);
              overflow: hidden;
              text-overflow: ellipsis;
              white-space: nowrap;
            }
          }
        }
        
        .col-desc {
          .knowledge-desc {
            font-size: var(--harmony-font-size-body-m);
            color: var(--harmony-font-secondary);
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            display: block;
          }
        }
        
        .col-files {
          .file-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 6px 12px;
            background: linear-gradient(135deg, var(--harmony-comp-emphasize-tertiary) 0%, var(--harmony-comp-emphasize-tertiary) 100%);
            border-radius: var(--harmony-corner-radius-level6);
            font-size: var(--harmony-font-size-subtitle-s);
            font-weight: 600;
            color: var(--harmony-brand);
          }
        }
        
        .col-size {
          .size-text {
            font-size: var(--harmony-font-size-body-m);
            font-weight: 500;
            color: var(--harmony-font-secondary);
          }
        }
        
        .col-time {
          .time-text {
            font-size: var(--harmony-font-size-subtitle-s);
            color: var(--harmony-font-tertiary);
          }
        }
        
        .col-actions {
          display: flex;
          gap: 8px;
          justify-content: flex-end;
          
          .action-btn {
            width: 36px;
            height: 36px;
            border: 1px solid var(--harmony-comp-divider);
            border-radius: var(--harmony-corner-radius-level6);
            background: var(--harmony-comp-background-primary);
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--harmony-font-secondary);

            span {
              font-size: var(--harmony-font-size-title-s);
            }
            
            &:hover {
              transform: translateY(-2px);
              box-shadow: var(--harmony-shadow-md);
            }
            
            &.view-btn:hover {
              background: var(--harmony-brand);
              border-color: var(--harmony-brand);
              color: white;
            }
            
            &.edit-btn:hover {
              background: var(--harmony-confirm);
              border-color: var(--harmony-confirm);
              color: white;
            }
            
            &.delete-btn:hover {
              background: var(--harmony-warning);
              border-color: var(--harmony-warning);
              color: white;
            }
          }
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


/* 原生对话框样式 */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--harmony-comp-background-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-dialog);
}

.dialog-container {
  background: var(--harmony-comp-background-primary);
  border-radius: var(--harmony-corner-radius-level6);
  box-shadow: var(--harmony-shadow-dialog);
  width: 500px;
  max-width: 90vw;
  max-height: 80vh;
  overflow: hidden;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 20px 0 20px;
  border-bottom: 1px solid var(--harmony-comp-divider);
  margin-bottom: 20px;
  
  h3 {
    margin: 0;
    font-size: var(--harmony-font-size-title-s);
    color: var(--harmony-font-primary);
  }
  
  .close-btn {
    background: none;
    border: none;
    font-size: var(--harmony-font-size-title-m);
    color: var(--harmony-font-tertiary);
    cursor: pointer;
    padding: 0;
    width: 24px;
    height: 24px;
    
    &:hover {
      color: var(--harmony-warning);
    }
  }
}

.dialog-body {
  padding: 0 20px 20px 20px;
  
  .form-item {
    margin-bottom: 20px;
    
    label {
      display: block;
      margin-bottom: 8px;
      font-size: var(--harmony-font-size-body-m);
      color: var(--harmony-font-secondary);
      font-weight: 500;
    }
    
    input, textarea {
      width: 100%;
      padding: 12px;
      border: 1px solid var(--harmony-comp-divider);
      border-radius: var(--harmony-corner-radius-level4);
      font-size: var(--harmony-font-size-body-m);
      box-sizing: border-box;
      transition: border-color 0.2s;
      
      &:focus {
        border-color: var(--harmony-brand);
      }
      
      &::placeholder {
        color: var(--harmony-font-tertiary);
      }
    }
    
    textarea {
      resize: vertical;
      font-family: var(--harmony-font-family);
    }
  }
}

.dialog-footer {
  padding: 20px;
  border-top: 1px solid var(--harmony-comp-divider);
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  
  button {
    padding: 8px 20px;
    border: 1px solid var(--harmony-comp-divider);
    border-radius: var(--harmony-corner-radius-level4);
    font-size: var(--harmony-font-size-body-m);
    cursor: pointer;
    transition: all 0.2s;
    
    &:hover {
      opacity: 0.8;
    }
    
    &:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }
  }
  
  .primary-btn {
    background: var(--harmony-brand);
    color: white;
    border-color: var(--harmony-brand);
    
    &:hover:not(:disabled) {
      background: var(--harmony-brand);
      border-color: var(--harmony-brand);
    }
  }
}

/* 输入框字符计数器样式 */
.input-with-count, .textarea-with-count {
  position: relative;
  
  .char-count {
    position: absolute;
    font-size: var(--harmony-font-size-caption-l);
    color: var(--harmony-font-tertiary);
    background: var(--harmony-comp-background-primary);
    padding: 2px 4px;
    border-radius: var(--harmony-corner-radius-level4);
    font-weight: 500;
    
    &.error {
      color: var(--harmony-warning);
      background: var(--harmony-warning-bg);
    }
  }
}

.input-with-count .char-count {
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
}

.textarea-with-count .char-count {
  right: 8px;
  bottom: 8px;
  box-shadow: var(--harmony-shadow-xs);
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
    
    .empty-icon-img {
      width: 60px;
      height: 60px;
      object-fit: contain;
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

/* 删除确认对话框样式 */
.delete-dialog-container {
  background: var(--harmony-comp-background-primary);
  border-radius: var(--harmony-corner-radius-level8);
  box-shadow: var(--harmony-shadow-dialog);
  width: 400px;
  max-width: 90vw;
  overflow: hidden;
}

.delete-dialog-body {
  padding: 30px;
  
  p {
    margin: 0;
    font-size: var(--harmony-font-size-body-l);
    color: var(--harmony-font-primary);
    line-height: 1.6;
    
    strong {
      color: var(--harmony-warning);
      font-weight: 600;
    }
  }
}

.delete-dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 30px;
  background: var(--harmony-comp-background-primary);
  border-top: 1px solid var(--harmony-comp-divider);
}

.delete-dialog-btn {
  padding: 10px 24px;
  border: none;
  border-radius: var(--harmony-corner-radius-level6);
  font-size: var(--harmony-font-size-body-m);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  &.cancel-btn {
    background: var(--harmony-comp-background-primary);
    color: var(--harmony-font-secondary);
    
    &:hover:not(:disabled) {
      background: var(--harmony-comp-divider);
    }
  }
  
  &.confirm-btn {
    background: var(--harmony-warning);
    color: white;

    &:hover:not(:disabled) {
      background: var(--harmony-warning);
    }
  }
}

/* ==================== MOBILE: hmos mobile-list ==================== */
.knowledge-mobile {
  display: flex;
  flex-direction: column;
  gap: var(--harmony-section-gap-mobile, 16px);
  padding-top: var(--harmony-padding-level8, 16px);
}

.km-header {
  display: flex;
  justify-content: flex-end;
}

.km-create-btn {
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

.km-list {
  display: flex;
  flex-direction: column;
  gap: var(--harmony-card-gap-mobile, 12px);
}

.km-item {
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

.km-action {
  width: var(--harmony-control-height-36, 36px);
  height: var(--harmony-control-height-36, 36px);
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--harmony-comp-background-secondary);
  border: none;
  border-radius: var(--harmony-corner-radius-level4, 8px);
  cursor: pointer;
  font-size: var(--harmony-font-size-body-m, 16px);
  transition: background 0.15s ease;

  &:active {
    background: var(--harmony-interactive-pressed);
  }

  &--danger:active {
    background: color-mix(in srgb, var(--harmony-warning) 10%, transparent);
  }
}

.km-empty {
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
</style>
<script setup lang="ts">
import { ref, onMounted, computed, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { HMessage, HButton } from '@/components/ui'
import {
  getKnowledgeFileListAPI,
  deleteKnowledgeFileAPI,
  createKnowledgeFileAPI,
  formatFileSize,
  getFileType,
  KnowledgeFileResponse,
  KnowledgeFileStatus,
  type KnowledgeFileDeleteRequest,
  type KnowledgeFileCreateRequest
} from '../../apis/knowledge-file'

const route = useRoute()
const router = useRouter()

// 获取知识库ID
const knowledgeId = computed(() => route.params.knowledgeId as string)
const knowledgeName = computed(() => route.query.name as string || '未知知识库')

// 状态管理
const files = ref<KnowledgeFileResponse[]>([])
const loading = ref(false)
const uploading = ref(false)

// 轮询相关
let pollingTimer: NodeJS.Timeout | null = null
const isPolling = ref(false)

// 排序相关
const sortType = ref('time') // 默认按时间排序
const sortOrder = ref('desc') // 默认降序（最新的在前）

// 检查是否有进行中的文件
const hasProcessingFiles = computed(() => {
  return files.value.some(file => 
    String(file.status).includes('🚀') ||
    String(file.status).includes('进行')
  )
})

// 排序后的文件列表
const sortedFiles = computed(() => {
  const filesCopy = [...files.value]
  
  return filesCopy.sort((a, b) => {
    let result = 0
    
    switch (sortType.value) {
      case 'time':
        result = new Date(a.create_time).getTime() - new Date(b.create_time).getTime()
        break
      case 'name':
        result = a.file_name.localeCompare(b.file_name, 'zh-CN')
        break
      case 'size':
        result = a.file_size - b.file_size
        break
      case 'status':
        // 按状态排序：进行中 > 完成 > 失败
        const statusOrder = { 
          '🚀 进行中': 3, 
          '✅ 完成': 2, 
          '❌ 失败': 1 
        }
        const aOrder = Object.entries(statusOrder).find(([key]) => String(a.status).includes(key.split(' ')[0]))?.[1] || 0
        const bOrder = Object.entries(statusOrder).find(([key]) => String(b.status).includes(key.split(' ')[0]))?.[1] || 0
        result = aOrder - bOrder
        break
      default:
        result = 0
    }
    
    // 应用排序顺序
    return sortOrder.value === 'desc' ? -result : result
  })
})

// 处理排序改变
const handleSortChange = (event: Event) => {
  const target = event.target as HTMLSelectElement
  sortType.value = target.value
}

// 开始轮询
const startPolling = () => {
  if (pollingTimer) {
    clearInterval(pollingTimer)
  }
  
  isPolling.value = true
  pollingTimer = setInterval(async () => {
    await fetchFiles(false) // 静默获取，不显示loading
    
    // 如果没有进行中的文件，停止轮询
    if (!hasProcessingFiles.value) {
      stopPolling()
    }
  }, 15000) // 15秒轮询一次
}

// 停止轮询
const stopPolling = () => {
  if (pollingTimer) {
    clearInterval(pollingTimer)
    pollingTimer = null
  }
  isPolling.value = false
}

// 获取文件列表
const fetchFiles = async (showLoading = true) => {
  if (!knowledgeId.value) {
    HMessage.error('知识库ID不能为空')
    return
  }
  
  if (showLoading) {
    loading.value = true
  }
  
  try {
    const response = await getKnowledgeFileListAPI(knowledgeId.value)
    if (response.data.status_code === 200 && response.data.data) {
      // 调试：打印后端返回的状态值
      console.log('后端返回的文件数据:', response.data.data)
      response.data.data.forEach((file: any, index: number) => {
        console.log(`文件${index}: ${file.file_name}, 原状态: "${file.status}", 转换后: "${mapStatusToDisplay(file.status)}"`)
      })
      
      // 转换后端状态为前端显示状态
      const processedFiles = response.data.data.map((file: any) => ({
        ...file,
        status: mapStatusToDisplay(file.status)
      }))
      
      files.value = processedFiles
      
      // 检查是否需要开始或停止轮询
      if (hasProcessingFiles.value && !isPolling.value) {
        startPolling()
      } else if (!hasProcessingFiles.value && isPolling.value) {
        stopPolling()
      }
    } else {
      HMessage.error('获取文件列表失败: ' + response.data.status_message)
    }
  } catch (error) {
    console.error('获取文件列表失败:', error)
    HMessage.error('获取文件列表失败')
  } finally {
    if (showLoading) {
      loading.value = false
    }
  }
}

// 删除文件相关状态
const showConfirmDialog = ref(false)
const fileToDelete = ref<KnowledgeFileResponse | null>(null)

// 删除文件
const handleDelete = (file: KnowledgeFileResponse) => {
  // 显示确认对话框
  fileToDelete.value = file
  showConfirmDialog.value = true
}

// 确认删除
const confirmDelete = async () => {
  if (!fileToDelete.value) return
  
  try {
    const deleteData: KnowledgeFileDeleteRequest = {
      knowledge_file_id: fileToDelete.value.id
    }
    
    const response = await deleteKnowledgeFileAPI(deleteData)
    
    if (response.data.status_code === 200) {
      HMessage.success('删除成功')
      await fetchFiles() // 刷新列表
    } else {
      HMessage.error('删除失败: ' + response.data.status_message)
    }
  } catch (error: any) {
    console.error('删除文件失败:', error)
    HMessage.error('删除失败: ' + (error?.message || error))
  } finally {
    // 关闭确认对话框
    showConfirmDialog.value = false
    fileToDelete.value = null
  }
}

// 取消删除
const cancelDelete = () => {
  showConfirmDialog.value = false
  fileToDelete.value = null
}

// 文件上传前处理
const beforeUpload = (rawFile: File) => {
  // 文件大小限制：100MB
  const maxSize = 100 * 1024 * 1024
  if (rawFile.size > maxSize) {
    HMessage.error('文件大小不能超过100MB')
    return false
  }
  
  // 支持的文件类型
  const supportedTypes = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain',
    'text/markdown',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-powerpoint',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'image/jpeg',
    'image/png',
    'image/gif'
  ]
  
  if (!supportedTypes.includes(rawFile.type)) {
    HMessage.error('不支持的文件类型，请上传PDF、Word、Excel、文本或图片文件')
    return false
  }
  
  // 立即添加文件到列表，显示为处理中状态
  const tempFile: KnowledgeFileResponse = {
    id: `temp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    file_name: rawFile.name,
    knowledge_id: knowledgeId.value,
    status: KnowledgeFileStatus.PROCESS,
    user_id: '',
    oss_url: '',
    file_size: rawFile.size,
    create_time: new Date().toISOString(),
    update_time: new Date().toISOString()
  }
  
  files.value.unshift(tempFile) // 添加到列表顶部
  
  // 开始轮询（如果还没有开始）
  if (!isPolling.value) {
    startPolling()
  }
  
  // 设置上传状态
  uploading.value = true
  return true
}

// 文件上传成功处理
const handleUploadSuccess = async (response: any, file: any, fileList: any) => {
  try {
    // 后端返回的response格式是: { status_code: 200, status_message: "success", data: "file_url" }
    if (response && response.status_code === 200 && response.data) {
      // 找到对应的临时文件，将状态设置为解析中
      const tempFileIndex = files.value.findIndex(f => f.file_name === file.name && f.id.startsWith('temp_'))
      
      if (tempFileIndex !== -1) {
        files.value[tempFileIndex].status = KnowledgeFileStatus.PROCESS // 设置为解析中
      }
      
      // 提示用户文件正在解析
      // HMessage.info('文件上传成功，正在解析中，请稍候...')
      
      const createData: KnowledgeFileCreateRequest = {
        knowledge_id: knowledgeId.value,
        file_url: response.data
      }
      
      // 调用解析接口
      const apiResponse = await createKnowledgeFileAPI(createData)
      
      // 根据解析接口返回的状态码决定最终状态
      if (apiResponse.data.status_code === 200) {
        HMessage.success('文件解析成功')
        
        // 移除临时文件
        if (tempFileIndex !== -1) {
          files.value.splice(tempFileIndex, 1)
        }
        
        // 刷新列表获取真实数据
        await fetchFiles(false)
      } else if (apiResponse.data.status_code === 500) {
        HMessage.error('文件解析失败: ' + apiResponse.data.status_message)
        
        // 解析失败，将临时文件状态改为失败
        if (tempFileIndex !== -1) {
          files.value[tempFileIndex].status = KnowledgeFileStatus.FAIL
        }
      } else {
        HMessage.error('文件处理失败: ' + apiResponse.data.status_message)
        
        // 其他错误，将临时文件状态改为失败
        if (tempFileIndex !== -1) {
          files.value[tempFileIndex].status = KnowledgeFileStatus.FAIL
        }
      }
      
      fileList.value = [] // 清空上传列表
    } else {
      HMessage.error('文件上传失败: ' + (response?.status_message || '未知错误'))
      
      // 上传失败，将临时文件状态改为失败
      const tempFileIndex = files.value.findIndex(f => f.file_name === file.name && f.id.startsWith('temp_'))
      if (tempFileIndex !== -1) {
        files.value[tempFileIndex].status = KnowledgeFileStatus.FAIL
      }
    }
  } catch (error: any) {
    console.error('文件解析异常:', error?.message || error)
    
    // 处理超时情况
    if (error?.code === 'ECONNABORTED' && error?.message?.includes('timeout')) {
      HMessage.warning('文件解析时间较长，请稍后刷新查看结果')
      // 不要将状态设为失败，因为后端可能还在处理中
    } else {
      HMessage.error('文件解析失败: ' + (error?.message || error))
      
      // 其他错误才设置为失败
      const tempFileIndex = files.value.findIndex(f => f.file_name === file.name && f.id.startsWith('temp_'))
      if (tempFileIndex !== -1) {
        files.value[tempFileIndex].status = KnowledgeFileStatus.FAIL
      }
    }
  } finally {
    uploading.value = false
  }
}

// 文件上传失败处理
const handleUploadError = (error: any, file: any) => {
  console.error('文件上传失败:', error)
  HMessage.error('文件上传失败')
  
  // 上传失败，将临时文件状态改为失败
  const tempFileIndex = files.value.findIndex(f => f.file_name === file.name && f.id.startsWith('temp_'))
  if (tempFileIndex !== -1) {
    files.value[tempFileIndex].status = KnowledgeFileStatus.FAIL
  }
  
  uploading.value = false
}

// 获取状态标签类型
const getStatusTagType = (status: KnowledgeFileStatus) => {
  switch (status) {
    case KnowledgeFileStatus.SUCCESS:
      return 'success'
    case KnowledgeFileStatus.PROCESS:
      return 'warning'
    case KnowledgeFileStatus.FAIL:
      return 'danger'
    default:
      return 'info'
  }
}

// 获取状态样式类
const getStatusClass = (status: KnowledgeFileStatus) => {
  switch (status) {
    case KnowledgeFileStatus.SUCCESS:
      return 'status-success'
    case KnowledgeFileStatus.PROCESS:
      return 'status-process'
    case KnowledgeFileStatus.FAIL:
      return 'status-fail'
    default:
      return 'status-default'
  }
}

// 获取状态图标
const getStatusIcon = (status: KnowledgeFileStatus) => {
  switch (status) {
    case KnowledgeFileStatus.SUCCESS:
      return Check
    case KnowledgeFileStatus.PROCESS:
      return Loading
    case KnowledgeFileStatus.FAIL:
      return Close
    default:
      return Document
  }
}

// 格式化时间
const formatTime = (timeStr: string) => {
  if (!timeStr) return '-'
  return new Date(timeStr).toLocaleString('zh-CN')
}

// 获取认证token
const getToken = () => {
  return localStorage.getItem('token') || ''
}

// 原生文件上传处理
const fileInputRef = ref<HTMLInputElement | null>(null)

const handleNativeFileChange = async (event: Event) => {
  const input = event.target as HTMLInputElement
  if (!input.files || input.files.length === 0) return

  const selectedFiles = Array.from(input.files)
  for (const file of selectedFiles) {
    if (!beforeUpload(file)) continue

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch('/api/v1/upload', {
        method: 'POST',
        headers: { Authorization: `Bearer ${getToken()}` },
        body: formData
      })

      if (!response.ok) throw new Error('Upload failed')
      const result = await response.json()
      await handleUploadSuccess(result, { name: file.name }, [])
    } catch (error) {
      handleUploadError(error, { name: file.name })
    }
  }
  input.value = ''
}

// 触发文件选择
const triggerFileUpload = () => {
  fileInputRef.value?.click()
}

// 返回上一页
const goBack = () => {
  router.push('/knowledge')
}

// 刷新当前页面（点击当前知识库名称时的操作）
const refreshCurrentPage = () => {
  // 刷新文件列表，给用户文件夹点击的反馈
  fetchFiles()
}

// 是否为临时文件
const isTempFile = (file: KnowledgeFileResponse) => {
  return file.id.startsWith('temp_')
}

// 状态映射函数 - 将后端英文状态转换为前端显示状态
const mapStatusToDisplay = (backendStatus: string) => {
  const statusMap: { [key: string]: string } = {
    'success': KnowledgeFileStatus.SUCCESS, // '✅ 完成'
    'fail': KnowledgeFileStatus.FAIL,       // '❌ 失败'
    'process': KnowledgeFileStatus.PROCESS  // '🚀 进行中'
  }
  return statusMap[backendStatus] || `❓ ${backendStatus}`
}

// 获取文件图标
const getFileIcon = (fileName: string) => {
  const ext = fileName.split('.').pop()?.toLowerCase()
  const iconMap: { [key: string]: string } = {
    pdf: '📄',
    doc: '📝',
    docx: '📝',
    txt: '📃',
    md: '📋',
    xls: '📊',
    xlsx: '📊',
    ppt: '📊',
    pptx: '📊',
    jpg: '🖼️',
    jpeg: '🖼️',
    png: '🖼️',
    gif: '🖼️',
    bmp: '🖼️',
    zip: '🗜️',
    rar: '🗜️',
    '7z': '🗜️'
  }
  return iconMap[ext || ''] || '📁'
}

// 获取文件大小颜色
const getFileSizeColor = (size: number) => {
  if (size < 1024 * 1024) return '#67c23a' // 绿色 < 1MB
  if (size < 10 * 1024 * 1024) return '#e6a23c' // 橙色 < 10MB  
  return '#f56c6c' // 红色 >= 10MB
}

onMounted(() => {
  // 调试：检查API函数是否正确导入
  console.log('检查API函数导入:')
  console.log('getKnowledgeFileListAPI:', getKnowledgeFileListAPI)
  console.log('deleteKnowledgeFileAPI:', deleteKnowledgeFileAPI)
  console.log('createKnowledgeFileAPI:', createKnowledgeFileAPI)
  
  if (knowledgeId.value) {
    fetchFiles()
  } else {
    HMessage.error('知识库ID参数缺失')
    router.push('/knowledge')
  }
})

// 组件卸载时清理轮询
onUnmounted(() => {
  stopPolling()
})
</script>

<template>
  <div class="knowledge-file-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <!-- 导航面包屑 -->
        <div class="navigation-section">
          <div class="nav-title">
            <span class="title-icon">🗂️</span>
            <span class="title-text">文件管理</span>
          </div>
          <div class="breadcrumb">
            <span class="breadcrumb-item clickable" @click="goBack">
              <span class="breadcrumb-icon">📚</span>
              <span class="breadcrumb-text">知识库管理</span>
            </span>
            <span class="breadcrumb-separator">
              <span class="separator-icon">▶</span>
            </span>
            <span class="breadcrumb-item clickable current" @click="refreshCurrentPage">
              <span class="breadcrumb-icon">📂</span>
              <span class="breadcrumb-text">{{ knowledgeName }}</span>
            </span>
          </div>
        </div>
      </div>
      
      <div class="header-right">
        <!-- 状态与操作区域 -->
        <div class="action-section">
          <!-- 文件统计卡片 -->
          <div class="stat-card total">
            <div class="stat-icon-wrapper">
              <span class="stat-icon">📊</span>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ files.length }}</div>
              <div class="stat-label">文件总数</div>
            </div>
          </div>
          
          <div class="stat-card processing">
            <div class="stat-icon-wrapper">
              <span class="stat-icon processing-icon">🚀</span>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ files.filter((f: KnowledgeFileResponse) => String(f.status).includes('🚀')).length }}</div>
              <div class="stat-label">处理中</div>
            </div>
          </div>
          
          <div class="stat-card success">
            <div class="stat-icon-wrapper">
              <span class="stat-icon">✅</span>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ files.filter((f: KnowledgeFileResponse) => String(f.status).includes('✅')).length }}</div>
              <div class="stat-label">已完成</div>
            </div>
          </div>
          
          <!-- 轮询状态指示器 -->
          <div v-if="isPolling" class="sync-indicator">
            <div class="sync-animation">
              <div class="sync-dot"></div>
              <div class="sync-dot"></div>
              <div class="sync-dot"></div>
            </div>
            <span class="sync-text">实时同步</span>
          </div>
          
          <!-- 上传按钮 -->
          <input
            ref="fileInputRef"
            type="file"
            multiple
            style="display: none"
            @change="handleNativeFileChange"
          />
          <div class="upload-button-wrapper">
            <button class="upload-btn-custom" :class="{ 'uploading': uploading }" @click="triggerFileUpload" :disabled="uploading">
              <div class="btn-icon-wrapper">
                <span v-if="!uploading" class="btn-icon">📤</span>
                <div v-else class="loading-spinner"></div>
              </div>
              <div class="btn-text-wrapper">
                <span class="btn-main-text">{{ uploading ? '上传中...' : '上传文件' }}</span>
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 文件列表 -->
    <div class="file-list" style="position: relative;">
      <div v-if="loading" class="loading-overlay">
        <div class="loading-spinner"></div>
      </div>
      <div v-if="files.length > 0" class="file-table">
        <table class="custom-table">
          <thead>
            <tr>
              <th class="col-name">
                <span class="th-content">
                  文件名
                </span>
              </th>
              <th class="col-type">
                <span class="th-content">
                  类型
                </span>
              </th>
              <th class="col-size">
                <span class="th-content">
                  大小
                </span>
              </th>
              <th class="col-status">
                <span class="th-content">
                  状态
                </span>
              </th>
              <th class="col-time">
                <span class="th-content">
                  时间
                </span>
              </th>
              <th class="col-action">
                <span class="th-content">
                  操作
                </span>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="file in sortedFiles" :key="file.id" class="file-row" :class="{ 'temp-file': isTempFile(file) }">
              <td class="col-name">
                <div class="file-info">
                  <div class="file-icon-wrapper">
                    <span class="file-icon">{{ getFileIcon(file.file_name) }}</span>
                    <div v-if="isTempFile(file)" class="upload-overlay">
                      <div class="upload-progress"></div>
                    </div>
                  </div>
                  <div class="file-details">
                    <span class="file-name">{{ file.file_name }}</span>
                    <span v-if="isTempFile(file)" class="temp-badge">
                      <span class="badge-icon">⬆️</span>
                      上传中
                    </span>
                  </div>
                </div>
              </td>
              <td class="col-type">
                <span class="type-tag">{{ getFileType(file.file_name) }}</span>
              </td>
              <td class="col-size">
                <span class="size-tag" :style="{ color: getFileSizeColor(file.file_size) }">
                  <span class="size-icon">💾</span>
                  {{ formatFileSize(file.file_size) }}
                </span>
              </td>
              <td class="col-status">
                <span class="status-tag" :class="getStatusClass(file.status)">
                  <span class="status-display">{{ file.status }}</span>
                </span>
              </td>
              <td class="col-time">
                <div class="time-info">
                  <span class="time-icon">📅</span>
                  <span class="time-text">{{ formatTime(file.create_time) }}</span>
                </div>
              </td>
              <td class="col-action">
                <div class="action-buttons">
                  <button 
                    v-if="!isTempFile(file)"
                    class="delete-btn"
                    @click="handleDelete(file)"
                    title="删除文件"
                  >
                    <span class="btn-icon">🗑️</span>
                    <span class="btn-text">删除</span>
                  </button>
                  <div v-else class="uploading-indicator">
                    <span class="uploading-icon">⏳</span>
                    <span class="uploading-text">处理中</span>
                  </div>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- 空状态 -->
      <div v-else-if="!loading" class="empty-state">
        <div class="empty-illustration">
          <div class="empty-cloud">
            <span class="cloud-icon">☁️</span>
            <div class="cloud-files">
              <span class="file-float">📄</span>
              <span class="file-float">📊</span>
              <span class="file-float">🖼️</span>
            </div>
          </div>
        </div>
        <h3 class="empty-title">
          <span class="title-icon">📁</span>
          知识库暂无文件
        </h3>
        <p class="empty-description">
          开始构建您的企业知识库，支持多种文件格式
        </p>
        <div class="empty-features">
          <div class="feature-item">
            <span class="feature-icon">📝</span>
            <span class="feature-text">支持 Word、PDF</span>
          </div>
          <div class="feature-item">
            <span class="feature-icon">📊</span>
            <span class="feature-text">支持 Excel、PPT</span>
          </div>
          <div class="feature-item">
            <span class="feature-icon">🖼️</span>
            <span class="feature-text">支持图片格式</span>
          </div>
        </div>
        <HButton type="primary" size="large" class="empty-upload-btn" @click="triggerFileUpload">
          <span class="btn-icon">🚀</span>
          立即上传文件
        </HButton>
      </div>
    </div>

    <!-- 确认删除对话框 -->
    <div v-if="showConfirmDialog" class="custom-confirm-dialog">
      <div class="confirm-dialog-content">
        <h3 class="dialog-title">确认删除</h3>
        <div class="dialog-body">
          确定要删除文件 "{{ fileToDelete?.file_name }}" 吗？删除后无法恢复。
        </div>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="cancelDelete">取消</button>
          <button class="btn-confirm" @click="confirmDelete">确定</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.knowledge-file-page {
  padding: 32px;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--color-bg);
  min-height: 100vh;
  
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    padding: var(--spacing-2xl) var(--spacing-2xl);
    background: var(--color-bg);
    border-radius: var(--radius-lg);
    box-shadow: 0 6px 24px var(--shadow-sm);
    border: 1px solid var(--color-border);
    
    .header-left {
      display: flex;
      align-items: center;
      gap: 20px;
      
      .navigation-section {
        display: flex;
        align-items: center;
        gap: 16px;
        
        .nav-title {
          display: flex;
          align-items: center;
          gap: 10px;
          
          .title-icon {
            font-size: var(--font-size-lg);
          }
          
          .title-text {
            font-size: var(--font-size-xl);
            font-weight: 600;
            color: var(--color-text-primary);
          }
        }
      
        .breadcrumb {
          display: flex;
          align-items: center;
          font-size: var(--font-size-base);
          
          .breadcrumb-item {
            display: flex;
            align-items: center;
            gap: 8px;
            color: var(--color-text-secondary);
            transition: all 0.2s ease;
            padding: 8px 14px;
            border-radius: var(--radius-md);
            
            .breadcrumb-icon {
              font-size: var(--font-size-base);
            }
            
            .breadcrumb-text {
              font-weight: 500;
            }
            
            &.clickable {
              cursor: pointer;
              background: var(--color-bg);
              
              &:hover {
                background: var(--color-border);
                color: var(--color-primary);
              }
            }
            
            &.current {
              color: var(--color-primary);
              font-weight: 600;
              background: var(--color-primary-bg);
            }
          }
          
          .breadcrumb-separator {
            margin: 0 8px;
            
            .separator-icon {
              color: var(--color-text-tertiary);
              font-size: 10px;
            }
          }
        }
      }
    }
    
    .header-right {
      display: flex;
      align-items: center;
      
      .action-section {
        display: flex;
        align-items: center;
        gap: 12px;
        
        .stat-card {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 10px 16px;
          background: var(--color-bg);
          border-radius: var(--radius-md);
          box-shadow: 0 2px 8px var(--shadow-sm);
          border: 1px solid var(--color-border);
          transition: all 0.2s ease;
          min-width: 90px;
            
          &:hover {
            box-shadow: 0 4px 12px var(--shadow-sm);
          }
            
          .stat-icon-wrapper {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 28px;
            height: 28px;
            border-radius: var(--radius-md);
            
            .stat-icon {
              font-size: var(--font-size-base);
            }
          }
          
          .stat-content {
            display: flex;
            flex-direction: column;
            
            .stat-number {
              font-size: var(--font-size-lg);
              font-weight: 600;
              line-height: 1;
              margin-bottom: 2px;
            }
            
            .stat-label {
              font-size: 11px;
              color: var(--color-text-tertiary);
              font-weight: 500;
            }
          }
            
          &.total {
            .stat-icon-wrapper {
              background: var(--color-primary-bg);
            }
            .stat-number {
              color: var(--color-primary);
            }
          }
          
          &.processing {
            .stat-icon-wrapper {
              background: var(--color-bg)3e0;
            }
            .stat-number {
              color: var(--color-warning);
            }
          }
          
          &.success {
            .stat-icon-wrapper {
              background: var(--color-success-bg);
            }
            .stat-number {
              color: var(--color-success);
            }
          }
        }
        
        .sync-indicator {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px 12px;
          background: var(--color-primary-bg);
          border-radius: var(--radius-md);
          border: 1px solid var(--color-primary-bg);
          
          .sync-animation {
            display: flex;
            gap: 3px;
            
            .sync-dot {
              width: 4px;
              height: 4px;
              background: var(--color-primary);
              border-radius: var(--radius-full);
              animation: syncWave 1.5s infinite ease-in-out;
              
              &:nth-child(1) { animation-delay: 0s; }
              &:nth-child(2) { animation-delay: 0.2s; }
              &:nth-child(3) { animation-delay: 0.4s; }
            }
          }
          
          .sync-text {
            font-size: var(--font-size-xs);
            color: var(--color-primary);
            font-weight: 500;
          }
        }
        
        .upload-button-wrapper {
          .upload-btn-custom {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 10px 20px;
            background: var(--color-primary);
            border: none;
            border-radius: var(--radius-md);
            color: white;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            font-size: var(--font-size-base);
            
            &:hover {
              background: var(--color-primary);
            }
            
            .btn-icon-wrapper {
              display: flex;
              align-items: center;
              justify-content: center;
              
              .btn-icon {
                font-size: var(--font-size-base);
              }
              
              .loading-spinner {
                width: 14px;
                height: 14px;
                border: 2px solid var(--color-bg-overlay);
                border-top: 2px solid white;
                border-radius: var(--radius-full);
                animation: spin 1s linear infinite;
              }
            }
            
            .btn-text-wrapper {
              display: flex;
              align-items: center;
              
              .btn-main-text {
                font-size: var(--font-size-base);
                font-weight: 600;
              }
            }
            
            &.uploading {
              background: var(--color-primary);
              cursor: not-allowed;
            }
          }
        }
      }
    }
  }
  
  .file-list {
    flex: 1;
    overflow: hidden;
    
    .file-table {
      height: 100%;
      
      .custom-table {
        width: 100%;
        border-collapse: collapse;
        background: var(--color-bg);
        border-radius: var(--radius-lg);
        overflow: hidden;
        box-shadow: 0 2px 8px var(--shadow-sm);
        border: 1px solid var(--color-border);
        
        th {
          background: var(--color-bg);
          color: var(--color-text-secondary);
          font-weight: 600;
          padding: var(--spacing-lg) var(--spacing-2xl);
          text-align: center;
          border-bottom: 2px solid var(--color-border);
          font-size: var(--font-size-sm);
          text-transform: uppercase;
          letter-spacing: 0.5px;
          
          .th-content {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
          }
        }
        
        .file-row {
          border-bottom: 1px solid var(--color-border);
          transition: all 0.2s ease;
          
          &:hover {
            background: var(--color-bg);
          }
          
          &:last-child {
            border-bottom: none;
          }
          
          &.temp-file {
            background: var(--color-primary-bg);
            border-left: 3px solid var(--color-primary);
          }
        }
        
        td {
          padding: 16px 20px;
          vertical-align: middle;
          font-size: var(--font-size-base);
          color: var(--color-text-secondary);
          text-align: center;
        }
        
        .col-name {
          min-width: 200px;
          text-align: left;
        }
        
        .col-type, .col-size, .col-status {
          width: 120px;
        }
        
        .col-time {
          width: 180px;
        }
        
        .col-action {
          width: 120px;
        }
      }
      
      .file-info {
        display: flex;
        align-items: center;
        gap: 12px;
        
        .file-icon-wrapper {
          position: relative;
          display: flex;
          align-items: center;
          justify-content: center;
          width: 36px;
          height: 36px;
          background: var(--color-primary-bg);
          border-radius: var(--radius-md);
          
          .file-icon {
            font-size: var(--font-size-xl);
          }
          
          .upload-overlay {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: var(--color-primary);
            border-radius: var(--radius-md);
            display: flex;
            align-items: center;
            justify-content: center;
            
            .upload-progress {
              width: 16px;
              height: 16px;
              border: 2px solid white;
              border-top: 2px solid transparent;
              border-radius: var(--radius-full);
              animation: spin 1s linear infinite;
            }
          }
        }
        
        .file-details {
          flex: 1;
          display: flex;
          flex-direction: column;
          gap: 4px;
          
          .file-name {
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            font-weight: 600;
            color: var(--color-text-primary);
            font-size: var(--font-size-base);
          }
          
          .temp-badge {
            display: flex;
            align-items: center;
            gap: 4px;
            background: var(--color-primary);
            color: white;
            padding: 2px 8px;
            border-radius: var(--radius-md);
            font-size: 11px;
            font-weight: 600;
            width: fit-content;
            
            .badge-icon {
              font-size: 10px;
            }
          }
        }
      }
      
      .type-tag {
        display: inline-block;
        padding: 4px 10px;
        background: var(--color-primary-bg);
        color: var(--color-primary);
        border-radius: var(--radius-lg);
        font-size: var(--font-size-xs);
        font-weight: 600;
      }
      
      .size-tag {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 4px;
        font-weight: 500;
        font-size: var(--font-size-sm);
        
        .size-icon {
          font-size: var(--font-size-base);
        }
      }
      
      .time-info {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        
        .time-icon {
          font-size: var(--font-size-base);
          color: var(--color-text-tertiary);
        }
        
        .time-text {
          font-size: var(--font-size-sm);
          color: var(--color-text-secondary);
        }
      }
      
      .status-tag {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 6px 12px;
        border-radius: var(--radius-lg);
        font-size: var(--font-size-xs);
        font-weight: 600;
        min-width: 80px;
        
        .status-display {
          display: flex;
          align-items: center;
          gap: 4px;
        }
        
        &.status-success {
          background: var(--color-success-bg);
          color: var(--color-success);
        }
        
        &.status-process {
          background: var(--color-bg)3e0;
          color: var(--color-warning);
        }
        
        &.status-fail {
          background: var(--color-error-bg);
          color: var(--color-danger);
        }
        
        &.status-default {
          background: var(--color-bg);
          color: var(--color-text-tertiary);
        }
      }
      
      .action-buttons {
        display: flex;
        align-items: center;
        justify-content: center;
        
        .delete-btn {
          display: flex;
          align-items: center;
          gap: 4px;
          padding: 6px 12px;
          background: var(--color-bg);
          color: var(--color-danger);
          border: 1px solid var(--color-danger);
          border-radius: var(--radius-md);
          cursor: pointer;
          font-size: var(--font-size-xs);
          font-weight: 600;
          transition: all 0.2s ease;
          
          .btn-icon {
            font-size: var(--font-size-base);
          }
          
          &:hover {
            background: var(--color-danger);
            color: white;
          }
        }
        
        .uploading-indicator {
          display: flex;
          align-items: center;
          gap: 4px;
          padding: 6px 12px;
          background: var(--color-primary-bg);
          color: var(--color-primary);
          border-radius: var(--radius-md);
          font-size: var(--font-size-xs);
          font-weight: 600;
          
          .uploading-icon {
            font-size: var(--font-size-base);
          }
        }
      }
    }
    
    .empty-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 500px;
      background: var(--color-bg);
      border-radius: var(--radius-lg);
      box-shadow: 0 2px 8px var(--shadow-sm);
      border: 1px solid var(--color-border);
      padding: 40px;
      
      .empty-illustration {
        margin-bottom: 24px;
        
        .empty-cloud {
          position: relative;
          display: flex;
          align-items: center;
          justify-content: center;
          
          .cloud-icon {
            font-size: 60px;
            opacity: 0.6;
          }
          
          .cloud-files {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            
            .file-float {
              font-size: var(--font-size-lg);
              animation: float 3s ease-in-out infinite;
              
              &:nth-child(1) {
                animation-delay: 0s;
              }
              
              &:nth-child(2) {
                animation-delay: 1s;
              }
              
              &:nth-child(3) {
                animation-delay: 2s;
              }
            }
          }
        }
      }
      
      .empty-title {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: var(--font-size-xl);
        font-weight: 600;
        color: var(--color-text-primary);
        margin: 0 0 12px 0;
        
        .title-icon {
          font-size: 22px;
        }
      }
      
      .empty-description {
        font-size: var(--font-size-base);
        color: var(--color-text-tertiary);
        margin: 0 0 24px 0;
        text-align: center;
      }
      
      .empty-features {
        display: flex;
        gap: 16px;
        margin-bottom: 32px;
        
        .feature-item {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 6px;
          padding: 12px;
          background: var(--color-bg);
          border-radius: var(--radius-md);
          min-width: 90px;
          
          .feature-icon {
            font-size: var(--font-size-xl);
          }
          
          .feature-text {
            font-size: var(--font-size-xs);
            color: var(--color-text-secondary);
            font-weight: 500;
            text-align: center;
          }
        }
      }
      
      .empty-upload-btn {
        .btn-icon {
          margin-right: 6px;
          font-size: var(--font-size-lg);
        }
      }
    }
  }
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes float {
  0% {
    transform: translateY(0px);
    opacity: 0.6;
  }
  50% {
    transform: translateY(-8px);
    opacity: 1;
  }
  100% {
    transform: translateY(0px);
    opacity: 0.6;
  }
}

@keyframes syncWave {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.loading-overlay {
  position: absolute;
  inset: 0;
  background: var(--color-overlay);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  border-radius: inherit;
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 3px solid var(--color-bg-overlay);
  border-top-color: var(--color-primary, var(--color-primary));
  border-radius: var(--radius-full);
  animation: h-spin 0.6s linear infinite;
}

@keyframes h-spin {
  to { transform: rotate(360deg); }
}

.custom-confirm-dialog {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: var(--color-overlay);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;

  .confirm-dialog-content {
    background-color: var(--color-bg);
    border-radius: var(--radius-lg);
    padding: 24px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
    text-align: center;
    width: 400px;
    max-width: 90%;

    .dialog-title {
      font-size: var(--font-size-xl);
      font-weight: 600;
      color: var(--color-text-primary);
      margin-bottom: 16px;
    }

    .dialog-body {
      font-size: var(--font-size-base);
      color: var(--color-text-secondary);
      margin-bottom: 24px;
      line-height: 1.6;
    }

    .dialog-footer {
      display: flex;
      justify-content: center;
      gap: 12px;

      .btn-cancel, .btn-confirm {
        padding: 8px 20px;
        border-radius: var(--radius-md);
        font-size: var(--font-size-base);
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
        border: none;
      }

      .btn-cancel {
        background-color: var(--color-bg);
        color: var(--color-text-secondary);
        
        &:hover {
          background-color: var(--color-border);
        }
      }

      .btn-confirm {
        background-color: var(--color-danger);
        color: white;
        
        &:hover {
          background-color: var(--color-danger);
        }
      }
    }
  }
}
</style> 
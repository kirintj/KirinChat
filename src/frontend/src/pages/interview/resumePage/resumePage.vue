<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useResumeStore } from '@/store/resume'
import { uploadResumeAPI, deleteResumeAPI } from '@/apis/resume'

const router = useRouter()
const resumeStore = useResumeStore()
const uploading = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)
const pollTimers = ref<Map<string, number>>(new Map())

onMounted(() => {
  resumeStore.fetchResumes()
})

function triggerUpload() {
  fileInput.value?.click()
}

async function handleFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  uploading.value = true
  try {
    const res = await uploadResumeAPI(file)
    if (res.data.status_code === 200 && res.data.data) {
      resumeStore.fetchResumes()
      startPolling(res.data.data.id)
    }
  } finally {
    uploading.value = false
    input.value = ''
  }
}

function startPolling(resumeId: string) {
  const timer = window.setInterval(async () => {
    const status = await resumeStore.pollStatus(resumeId)
    if (status === 'COMPLETED' || status === 'FAILED') {
      clearInterval(timer)
      pollTimers.value.delete(resumeId)
      resumeStore.fetchResumes()
    }
  }, 3000)
  pollTimers.value.set(resumeId, timer)
}

async function handleDelete(id: string) {
  const res = await deleteResumeAPI(id)
  if (res.data.status_code === 200) {
    resumeStore.fetchResumes()
  }
}

function goToDetail(id: string) {
  router.push(`/interview/resume/${id}`)
}

function getStatusClass(status: string) {
  if (status === 'COMPLETED') return 'status-done'
  if (status === 'PROCESSING') return 'status-active'
  if (status === 'FAILED') return 'status-failed'
  return 'status-pending'
}

function getStatusText(status: string) {
  const map: Record<string, string> = {
    PENDING: '等待分析',
    PROCESSING: '分析中',
    COMPLETED: '已完成',
    FAILED: '分析失败',
  }
  return map[status] || status
}
</script>

<template>
  <div class="resume-page">
    <div class="page-header">
      <h2>简历管理</h2>
      <button class="upload-btn" @click="triggerUpload" :disabled="uploading">
        {{ uploading ? '上传中...' : '上传简历' }}
      </button>
      <input ref="fileInput" type="file" accept=".pdf,.docx,.doc,.txt" style="display: none" @change="handleFileChange" />
    </div>

    <div v-if="resumeStore.loading && resumeStore.resumes.length === 0" class="loading">加载中...</div>
    <div v-else-if="resumeStore.resumes.length === 0" class="empty">暂无简历，点击上方按钮上传</div>

    <div v-else class="resume-list">
      <div v-for="resume in resumeStore.resumes" :key="resume.id" class="resume-card" @click="goToDetail(resume.id)">
        <div class="card-info">
          <span class="filename">{{ resume.filename }}</span>
          <span :class="['status-tag', getStatusClass(resume.status)]">{{ getStatusText(resume.status) }}</span>
        </div>
        <div class="card-meta">
          <span v-if="resume.score !== null" class="score">评分: {{ resume.score }}</span>
          <span class="time">{{ resume.create_time }}</span>
        </div>
        <button class="delete-btn" @click.stop="handleDelete(resume.id)">删除</button>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.resume-page { padding: 24px; }
.page-header {
  display: flex; align-items: center; gap: 16px; margin-bottom: 24px;
  h2 { margin: 0; font-size: 20px; }
  .upload-btn {
    padding: 8px 20px; border-radius: var(--harmony-corner-radius-level4);
    background: var(--harmony-brand); color: var(--harmony-comp-background-primary); border: none; cursor: pointer;
    &:disabled { opacity: 0.6; cursor: not-allowed; }
  }
}
.resume-list { display: flex; flex-direction: column; gap: 12px; }
.resume-card {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px; background: var(--harmony-comp-background-primary); border-radius: var(--harmony-corner-radius-level4);
  border: 1px solid var(--harmony-comp-divider); cursor: pointer; transition: border-color 0.2s;
  &:hover { border-color: var(--harmony-brand); }
  .card-info { display: flex; align-items: center; gap: 12px; .filename { font-weight: 500; } }
  .card-meta { display: flex; gap: 16px; color: var(--harmony-font-tertiary); font-size: 13px; .score { color: var(--harmony-brand); font-weight: 500; } }
  .delete-btn {
    padding: 4px 12px; border: 1px solid var(--harmony-warning); color: var(--harmony-warning);
    background: transparent; border-radius: var(--harmony-corner-radius-level4); cursor: pointer;
    &:hover { background: var(--harmony-warning); color: var(--harmony-comp-background-primary); }
  }
}
.status-tag { padding: 2px 8px; border-radius: 4px; font-size: var(--harmony-font-size-body-s); }
.status-done { background: var(--harmony-confirm-bg); color: var(--harmony-confirm); }
.status-active { background: var(--harmony-comp-emphasize-tertiary); color: var(--harmony-brand); }
.status-failed { background: var(--harmony-warning-bg); color: var(--harmony-warning); }
.status-pending { background: var(--harmony-comp-background-secondary); color: var(--harmony-font-tertiary); }
.loading, .empty { text-align: center; padding: 60px; color: var(--harmony-font-tertiary); }
</style>

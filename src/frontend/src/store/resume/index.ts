import { ref } from 'vue'
import { defineStore } from 'pinia'
import {
  getResumeListAPI,
  getResumeDetailAPI,
  getResumeStatusAPI,
  type ResumeInfo,
  type ResumeDetail,
} from '@/apis/resume'

export const useResumeStore = defineStore('resume', () => {
  const resumes = ref<ResumeInfo[]>([])
  const currentResume = ref<ResumeDetail | null>(null)
  const loading = ref(false)

  async function fetchResumes() {
    loading.value = true
    try {
      const res = await getResumeListAPI()
      if (res.data.status_code === 200 && res.data.data) {
        resumes.value = res.data.data.resumes
      }
    } finally {
      loading.value = false
    }
  }

  async function fetchDetail(id: string) {
    loading.value = true
    try {
      const res = await getResumeDetailAPI(id)
      if (res.data.status_code === 200 && res.data.data) {
        currentResume.value = res.data.data
      }
    } finally {
      loading.value = false
    }
  }

  async function pollStatus(id: string): Promise<string> {
    const res = await getResumeStatusAPI(id)
    if (res.data.status_code === 200 && res.data.data) {
      return res.data.data.status
    }
    return 'UNKNOWN'
  }

  function reset() {
    currentResume.value = null
  }

  return { resumes, currentResume, loading, fetchResumes, fetchDetail, pollStatus, reset }
})

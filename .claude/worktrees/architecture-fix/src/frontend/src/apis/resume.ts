import { request } from '../utils/request'
import type { UnifiedResponse } from './interview'

// ==================== Types ====================

export interface ResumeInfo {
  id: string
  filename: string
  file_size: number
  content_type: string
  status: string
  score: number | null
  create_time: string | null
}

export interface ResumeDetail extends ResumeInfo {
  raw_text: string
  analysis_result: Record<string, any> | null
  error_message: string
}

export interface ResumeListData {
  resumes: ResumeInfo[]
}

export interface ResumeStatusData {
  id: string
  status: string
  score: number | null
}

// ==================== APIs ====================

export const uploadResumeAPI = (file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  return request<UnifiedResponse<ResumeInfo>>({
    url: '/api/v1/resume/upload',
    method: 'POST',
    data: formData,
    timeout: 120000,
  })
}

export const getResumeListAPI = () => {
  return request<UnifiedResponse<ResumeListData>>({
    url: '/api/v1/resume/list',
    method: 'GET',
  })
}

export const getResumeDetailAPI = (id: string) => {
  return request<UnifiedResponse<ResumeDetail>>({
    url: `/api/v1/resume/${id}`,
    method: 'GET',
  })
}

export const deleteResumeAPI = (id: string) => {
  return request<UnifiedResponse<{ success: boolean }>>({
    url: `/api/v1/resume/${id}`,
    method: 'DELETE',
  })
}

export const getResumeStatusAPI = (id: string) => {
  return request<UnifiedResponse<ResumeStatusData>>({
    url: `/api/v1/resume/${id}/status`,
    method: 'GET',
  })
}

export const getResumePdfUrl = (id: string) => {
  return `/api/v1/resume/${id}/pdf`
}

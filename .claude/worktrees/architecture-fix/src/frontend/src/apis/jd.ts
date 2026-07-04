import { request } from '../utils/request'
import type { UnifiedResponse } from './interview'

// ==================== Types ====================

export interface JdCategory {
  key: string
  label: string
  priority: string
  keywords: string[]
}

export interface JdParseData {
  company: string
  position: string
  experience_required: string
  categories: JdCategory[]
  summary: string
}

export interface JdCreateSkillReq {
  company: string
  position: string
  experience_required: string
  categories: JdCategory[]
  summary: string
}

export interface JdSkillData {
  skill_id: string
  name: string
  description: string
  categories: string[]
}

// ==================== APIs ====================

export const parseJdAPI = (jdText: string) => {
  return request<UnifiedResponse<JdParseData>>({
    url: '/api/v1/jd/parse',
    method: 'POST',
    data: { jd_text: jdText },
    timeout: 120000,
  })
}

export const createSkillFromJdAPI = (data: JdCreateSkillReq) => {
  return request<UnifiedResponse<JdSkillData>>({
    url: '/api/v1/jd/create-skill',
    method: 'POST',
    data,
    timeout: 30000,
  })
}

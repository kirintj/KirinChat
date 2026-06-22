import { request } from '../utils/request'

// ---------------------------------------------------------------------------
// Type definitions
// ---------------------------------------------------------------------------

export interface UnifiedResponse<T> {
  status_code: number
  status_message: string
  data: T
}

export interface SkillInfo {
  id: string
  name: string
  description: string
  icon: string
  categories: string[]
}

export interface SkillCategory {
  key: string
  label: string
  priority: number
}

export interface SkillDetail {
  skill: SkillInfo
  categories: SkillCategory[]
  references: string[]
}

export interface SkillListData {
  skills: SkillInfo[]
}

export interface InterviewQuestion {
  id: string
  type: string
  category: string
  content: string
}

export interface InterviewSession {
  id: string
  skill_id: string
  status: string
  progress: { current: number; total: number }
}

export interface InterviewSessionDetail {
  session: InterviewSession
  questions: InterviewQuestion[]
}

export interface InterviewStartData {
  session_id: string
  first_question: InterviewQuestion
}

export interface InterviewAnswerData {
  next_question: InterviewQuestion | null
  is_completed: boolean
}

export interface InterviewCompleteData {
  evaluation_id: string
  status: string
}

export interface EvaluationReport {
  id: string
  total_score: number
  category_scores: Record<string, number>
  summary: string
  strengths: string[]
  improvements: string[]
}

export interface InterviewHistoryData {
  sessions: InterviewSession[]
}

// Request types
export interface InterviewStartRequest {
  skill_id: string
  difficulty: string
  question_count: number
}

export interface InterviewAnswerRequest {
  session_id: string
  question_id: string
  answer: string
}

export interface InterviewCompleteRequest {
  session_id: string
}

// ---------------------------------------------------------------------------
// API functions
// ---------------------------------------------------------------------------

/** Get all available interview skills */
export function getSkillListAPI() {
  return request<UnifiedResponse<SkillListData>>({
    url: '/api/v1/skill/list',
    method: 'GET'
  })
}

/** Get skill detail with categories and references */
export function getSkillDetailAPI(skillId: string) {
  return request<UnifiedResponse<SkillDetail>>({
    url: `/api/v1/skill/${skillId}`,
    method: 'GET'
  })
}

/** Start a new interview session */
export function startInterviewAPI(data: InterviewStartRequest) {
  return request<UnifiedResponse<InterviewStartData>>({
    url: '/api/v1/interview/start',
    method: 'POST',
    data
  })
}

/** Submit an answer and get the next question */
export function submitAnswerAPI(data: InterviewAnswerRequest) {
  return request<UnifiedResponse<InterviewAnswerData>>({
    url: '/api/v1/interview/answer',
    method: 'POST',
    data
  })
}

/** Get interview session detail with questions */
export function getSessionDetailAPI(sessionId: string) {
  return request<UnifiedResponse<InterviewSessionDetail>>({
    url: `/api/v1/interview/session/${sessionId}`,
    method: 'GET'
  })
}

/** Complete an interview session and trigger evaluation */
export function completeInterviewAPI(data: InterviewCompleteRequest) {
  return request<UnifiedResponse<InterviewCompleteData>>({
    url: '/api/v1/interview/complete',
    method: 'POST',
    data
  })
}

/** Get evaluation report by ID */
export function getEvaluationReportAPI(evaluationId: string) {
  return request<UnifiedResponse<EvaluationReport>>({
    url: `/api/v1/interview/evaluation/${evaluationId}`,
    method: 'GET'
  })
}

/** Get interview history for current user */
export function getInterviewHistoryAPI() {
  return request<UnifiedResponse<InterviewHistoryData>>({
    url: '/api/v1/interview/history',
    method: 'GET'
  })
}

import { request } from '../utils/request'
import { fetchEventSource } from '@microsoft/fetch-event-source'

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
  user_answer: string | null
}

export interface InterviewSession {
  id: string
  skill_id: string
  status: string
  difficulty: string | null
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

export interface QuestionDetailItem {
  question_id: string
  content: string
  user_answer: string | null
  type: string
  category: string
  score: number
  feedback: string
  reference_answer: string
}

export interface EvaluationReport {
  id: string
  total_score: number
  category_scores: Record<string, number>
  summary: string
  strengths: string[]
  improvements: string[]
  question_details: QuestionDetailItem[]
}

export interface QuestionDetailData {
  question_id: string
  session_id: string
  content: string
  user_answer: string | null
  type: string
  category: string
  score: number
  feedback: string
  reference_answer: string
  skill_name: string
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
    data,
    timeout: 120000
  })
}

/** Submit an answer and get the next question */
export function submitAnswerAPI(data: InterviewAnswerRequest) {
  return request<UnifiedResponse<InterviewAnswerData>>({
    url: '/api/v1/interview/answer',
    method: 'POST',
    data,
    timeout: 120000
  })
}

/** 提交答案并以 SSE 流式接收（追问 + 下一题） */
export function submitAnswerStreamAPI(
  data: InterviewAnswerRequest,
  callbacks: {
    onFollowUpChunk: (chunk: string, accumulated: string) => void
    onNextQuestionChunk: (chunk: string, accumulated: string) => void
    onDone: (result: { follow_up: { content: string } | null; next_question: { content: string } | null; is_completed: boolean }) => void
    onError: (err: Error) => void
  },
) {
  const ctrl = new AbortController()

  fetchEventSource('/api/v1/interview/answer/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('token') || ''}`,
    },
    body: JSON.stringify(data),
    signal: ctrl.signal,
    openWhenHidden: true,
    async onopen(response: Response) {
      if (response.status !== 200) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }
    },
    onmessage(msg: { data: string }) {
      try {
        const event = JSON.parse(msg.data)
        if (event.type === 'follow_up_chunk') {
          callbacks.onFollowUpChunk(event.data.chunk, event.data.accumulated)
        } else if (event.type === 'next_question_chunk') {
          callbacks.onNextQuestionChunk(event.data.chunk, event.data.accumulated)
        } else if (event.type === 'done') {
          callbacks.onDone(event.data)
        }
      } catch (error) {
        console.error('解析 SSE 消息出错:', error)
      }
    },
    onclose() {
      // 连接关闭
    },
    onerror(err: Error) {
      callbacks.onError(err)
      ctrl.abort()
      throw err
    },
  })

  return ctrl
}

/** 获取面试会话详情（含题目列表） */
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
    data,
    timeout: 180000
  })
}

/** Get evaluation report by ID */
export function getEvaluationReportAPI(evaluationId: string) {
  return request<UnifiedResponse<EvaluationReport>>({
    url: `/api/v1/interview/evaluation/${evaluationId}`,
    method: 'GET'
  })
}

/** Get evaluation report by session ID */
export function getEvaluationBySessionAPI(sessionId: string) {
  return request<UnifiedResponse<EvaluationReport>>({
    url: `/api/v1/interview/evaluation/by-session/${sessionId}`,
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

/** Delete an interview session */
export function deleteInterviewSessionAPI(sessionId: string) {
  return request<UnifiedResponse<null>>({
    url: `/api/v1/interview/session/${sessionId}`,
    method: 'DELETE'
  })
}

// ---------------------------------------------------------------------------
// Learning path types
// ---------------------------------------------------------------------------

export interface WeakCategory {
  category: string
  label: string
  avg_score: number
  session_count: number
}

export interface LearningResource {
  label: string
  reference: string
}

export interface LearningPath {
  skill_id: string
  skill_name: string
  weak_categories: WeakCategory[]
  resources: Record<string, LearningResource>
  study_order: string[]
  total_sessions: number
  overall_avg_score: number
  overall_level: string
  overall_level_label: string
}

/** 获取单题评估详情 */
export function getQuestionDetailAPI(questionId: string) {
  return request<UnifiedResponse<QuestionDetailData>>({
    url: `/api/v1/interview/question-detail/${questionId}`,
    method: 'GET'
  })
}

/** Get personalized learning path for a skill */
export function getLearningPathAPI(skillId: string) {
  return request<UnifiedResponse<LearningPath>>({
    url: `/api/v1/interview/learning-path/${skillId}`,
    method: 'GET'
  })
}

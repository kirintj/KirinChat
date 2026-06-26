import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { InterviewQuestion } from '../../apis/interview'
import {
  startInterviewAPI,
  submitAnswerAPI,
  submitAnswerStreamAPI,
  completeInterviewAPI,
  getEvaluationReportAPI,
} from '../../apis/interview'
import type { EvaluationReport } from '../../apis/interview'

export interface InterviewMessage {
  role: 'interviewer' | 'candidate'
  content: string
}

export const useInterviewStore = defineStore('interview', () => {
  // --- State ---
  const sessionId = ref('')
  const skillId = ref('')
  const skillName = ref('')
  const difficulty = ref('MEDIUM')
  const questionCount = ref(10)
  const currentQuestion = ref<InterviewQuestion | null>(null)
  const messages = ref<InterviewMessage[]>([])
  const progress = ref({ current: 0, total: 0 })
  const status = ref<'IDLE' | 'IN_PROGRESS' | 'COMPLETED'>('IDLE')
  const evaluationId = ref('')
  const loading = ref(false)

  // --- Getters ---
  const isActive = computed(() => status.value === 'IN_PROGRESS')
  const isCompleted = computed(() => status.value === 'COMPLETED')
  const progressPercent = computed(() => {
    if (progress.value.total === 0) return 0
    return Math.round((progress.value.current / progress.value.total) * 100)
  })

  // --- Actions ---

  async function startInterview(skill_id: string, diff: string, count: number) {
    loading.value = true
    try {
      const res = await startInterviewAPI({
        skill_id,
        difficulty: diff,
        question_count: count,
      })
      if (res.data.status_code === 200 && res.data.data) {
        const data = res.data.data
        sessionId.value = data.session_id
        skillId.value = skill_id
        difficulty.value = diff
        questionCount.value = count
        currentQuestion.value = data.first_question
        messages.value = [
          { role: 'interviewer', content: data.first_question.content },
        ]
        progress.value = { current: 0, total: count }
        status.value = 'IN_PROGRESS'
        return true
      }
      return false
    } finally {
      loading.value = false
    }
  }

  async function submitAnswer(answer: string) {
    if (!currentQuestion.value || !sessionId.value) return false
    loading.value = true
    try {
      // Add candidate message
      messages.value.push({ role: 'candidate', content: answer })

      const res = await submitAnswerAPI({
        session_id: sessionId.value,
        question_id: currentQuestion.value.id,
        answer,
      })

      if (res.data.status_code === 200 && res.data.data) {
        const data = res.data.data

        if (data.is_completed || !data.next_question) {
          // Interview is finished
          status.value = 'COMPLETED'
          currentQuestion.value = null
          messages.value.push({
            role: 'interviewer',
            content: '面试已结束！正在为你生成评估报告...',
          })
          return true
        }

        // Got next question
        // Only increment progress when the answered question was a MAIN question
        const answeredType = currentQuestion.value?.type
        if (answeredType === 'MAIN') {
          progress.value.current += 1
        }
        currentQuestion.value = data.next_question
        messages.value.push({
          role: 'interviewer',
          content: data.next_question.content,
        })
        return true
      }
      return false
    } finally {
      loading.value = false
    }
  }

  async function submitAnswerStream(answer: string): Promise<boolean> {
    if (!currentQuestion.value || !sessionId.value) return false
    loading.value = true

    // 添加候选人消息
    messages.value.push({ role: 'candidate', content: answer })
    const answeredQuestionId = currentQuestion.value.id

    return new Promise((resolve) => {
      // 添加空的 AI 消息气泡（用于流式填充）
      const aiMessageIndex = messages.value.length
      messages.value.push({ role: 'interviewer', content: '' })

      submitAnswerStreamAPI(
        {
          session_id: sessionId.value,
          question_id: answeredQuestionId,
          answer,
        },
        {
          onFollowUpChunk(_chunk: string, accumulated: string) {
            // 实时更新追问题消息内容
            messages.value[aiMessageIndex].content = accumulated
          },
          onNextQuestionChunk(_chunk: string, accumulated: string) {
            // 如果追问题已完成，添加新的下一题消息气泡
            if (messages.value.length === aiMessageIndex + 1) {
              messages.value.push({ role: 'interviewer', content: accumulated })
            } else {
              // 已经有下一题消息气泡，更新它
              messages.value[messages.value.length - 1].content = accumulated
            }
          },
          onDone(result) {
            if (result.is_completed) {
              status.value = 'COMPLETED'
              currentQuestion.value = null
              messages.value.push({
                role: 'interviewer',
                content: '面试已结束！正在为你生成评估报告...',
              })
            } else if (result.next_question) {
              // 更新 currentQuestion
              currentQuestion.value = {
                id: '',
                type: 'MAIN',
                category: '',
                content: result.next_question.content,
                user_answer: null,
              }
              // 更新进度（只有 MAIN 类型才计数）
              progress.value.current += 1
            }
            loading.value = false
            resolve(true)
          },
          onError() {
            loading.value = false
            resolve(false)
          },
        },
      )
    })
  }

  async function endInterview(): Promise<string | null> {
    if (!sessionId.value) return null
    loading.value = true
    try {
      const res = await completeInterviewAPI({ session_id: sessionId.value })
      if (res.data.status_code === 200 && res.data.data) {
        evaluationId.value = res.data.data.evaluation_id
        status.value = 'COMPLETED'
        return res.data.data.evaluation_id
      }
      return null
    } finally {
      loading.value = false
    }
  }

  async function fetchReport(evaluationId: string): Promise<EvaluationReport | null> {
    try {
      const res = await getEvaluationReportAPI(evaluationId)
      if (res.data.status_code === 200 && res.data.data) {
        return res.data.data
      }
      return null
    } catch {
      return null
    }
  }

  function reset() {
    sessionId.value = ''
    skillId.value = ''
    skillName.value = ''
    difficulty.value = 'MEDIUM'
    questionCount.value = 10
    currentQuestion.value = null
    messages.value = []
    progress.value = { current: 0, total: 0 }
    status.value = 'IDLE'
    evaluationId.value = ''
    loading.value = false
  }

  return {
    // State
    sessionId,
    skillId,
    skillName,
    difficulty,
    questionCount,
    currentQuestion,
    messages,
    progress,
    status,
    evaluationId,
    loading,
    // Getters
    isActive,
    isCompleted,
    progressPercent,
    // Actions
    startInterview,
    submitAnswer,
    submitAnswerStream,
    endInterview,
    fetchReport,
    reset,
  }
}, { persist: true })

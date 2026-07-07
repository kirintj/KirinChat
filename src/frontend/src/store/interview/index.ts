import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { InterviewQuestion } from '../../apis/interview'
import {
  startInterviewAPI,
  submitAnswerAPI,
  submitAnswerStreamAPI,
  completeInterviewAPI,
  getEvaluationReportAPI,
  getEvaluationBySessionAPI,
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

  // --- 防止并发重复创建面试的锁 ---
  let _creatingLock = false

  async function startInterview(skill_id: string, diff: string, count: number) {
    // 并发防护：防止快速双击创建两个 session
    if (_creatingLock || loading.value) return false
    _creatingLock = true
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
      _creatingLock = false
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
              currentQuestion.value = null
              messages.value.push({
                role: 'interviewer',
                content: '面试已结束！正在为你生成评估报告...',
              })
              // 自动触发评估（异步，含轮询等待）
              loading.value = true
              completeInterviewAPI({ session_id: sessionId.value })
                .then(() => pollEvaluationReport(sessionId.value))
                .then((evalId) => {
                  if (evalId) evaluationId.value = evalId
                  status.value = 'COMPLETED'
                  loading.value = false
                  resolve(true)
                })
                .catch(() => {
                  status.value = 'COMPLETED'
                  loading.value = false
                  resolve(false)
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
              loading.value = false
              resolve(true)
            } else {
              loading.value = false
              resolve(true)
            }
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
        status.value = 'COMPLETED'

        // 后端已改为异步评估，evaluation_id 可能为空
        // 轮询等待评估报告生成完成
        const evalId = await pollEvaluationReport(sessionId.value)
        if (evalId) {
          evaluationId.value = evalId
          return evalId
        }
        return null
      }
      return null
    } finally {
      loading.value = false
    }
  }

  // --- 防止并发评估轮询的锁 ---
  let _pollingLock = false

  async function pollEvaluationReport(sid: string): Promise<string | null> {
    // 防止并发启动多个轮询
    if (_pollingLock) return null
    _pollingLock = true
    try {
      const maxAttempts = 30
      let interval = 2000
      for (let i = 0; i < maxAttempts; i++) {
        try {
          const res = await getEvaluationBySessionAPI(sid)
          if (res.data.status_code === 200 && res.data.data) {
            return res.data.data.id
          }
        } catch {
          // 评估尚未完成，继续轮询
        }
        // 指数退避 + jitter（最大 10 秒）
        const jitter = Math.floor(Math.random() * 1000)
        await new Promise(resolve => setTimeout(resolve, interval + jitter))
        interval = Math.min(interval * 1.5, 10000)
      }
      return null
    } finally {
      _pollingLock = false
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

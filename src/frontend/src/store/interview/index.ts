import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { InterviewQuestion, InterviewSession, SkillInfo, HistoryQueryParams } from '../../apis/interview'
import {
  startInterviewAPI,
  submitAnswerStreamAPI,
  completeInterviewAPI,
  getEvaluationReportAPI,
  getEvaluationBySessionAPI,
  getEvaluationStatusAPI,
  getInterviewHistoryAPI,
  getSkillListAPI,
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
  const evaluationStatus = ref<'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED' | ''>('')
  const evaluationElapsed = ref(0)

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

  async function submitAnswerStream(answer: string): Promise<boolean> {
    if (!currentQuestion.value || !sessionId.value) return false
    loading.value = true

    // 记录当前题目类型，用于后续进度判断
    const answeredType = currentQuestion.value.type

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
                content: '面试已结束！正在为你生成评估报告，请稍候...',
              })
              // 自动触发评估（异步，含轮询等待）
              loading.value = true
              completeInterviewAPI({ session_id: sessionId.value })
                .then(() => pollEvaluationReport(sessionId.value))
                .then((evalId) => {
                  if (evalId) evaluationId.value = evalId
                  status.value = 'COMPLETED'
                  loading.value = false
                  // 清理已结束会话的草稿
                  clearDraftsForSession(sessionId.value)
                  resolve(true)
                })
                .catch(() => {
                  status.value = 'COMPLETED'
                  loading.value = false
                  resolve(false)
                })
            } else if (result.next_question) {
              // 【问题3】只有主题目才累加进度，追问题不改动进度
              if (answeredType === 'MAIN') {
                progress.value.current += 1
              }
              // 【问题2】使用服务端返回的 question ID，禁止硬编码空字符串
              currentQuestion.value = {
                id: result.next_question.id || '',
                type: 'MAIN',
                category: '',
                content: result.next_question.content,
                user_answer: null,
              }
              loading.value = false
              resolve(true)
            } else if (result.follow_up) {
              // 追问题场景：标记为 FOLLOW_UP 类型，避免错误累加进度
              currentQuestion.value = {
                id: '',
                type: 'FOLLOW_UP',
                category: 'follow_up',
                content: result.follow_up.content,
                user_answer: null,
              }
              loading.value = false
              resolve(true)
            } else {
              // 追问题场景：不更新 currentQuestion，等用户继续回答
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
    // 并发场景：等待已有轮询完成后复用结果，而非直接中断
    if (_pollingLock) {
      // 等待已有轮询结束，最多等 60 秒
      for (let i = 0; i < 60; i++) {
        await new Promise(resolve => setTimeout(resolve, 1000))
        if (!_pollingLock) break
      }
      // 锁已释放则直接返回当前 evaluationId
      if (evaluationId.value) return evaluationId.value
      // 锁仍未释放或无结果，尝试自己获取一次
      try {
        const res = await getEvaluationBySessionAPI(sid)
        if (res.data.status_code === 200 && res.data.data) {
          return res.data.data.id
        }
      } catch { /* ignore */ }
      return null
    }
    _pollingLock = true
    evaluationStatus.value = 'PROCESSING'
    evaluationElapsed.value = 0
    const startTime = Date.now()
    try {
      const maxAttempts = 30
      let interval = 2000
      for (let i = 0; i < maxAttempts; i++) {
        evaluationElapsed.value = Math.floor((Date.now() - startTime) / 1000)
        try {
          const res = await getEvaluationStatusAPI(sid)
          if (res.data.status_code === 200 && res.data.data) {
            evaluationStatus.value = res.data.data.status
            if (res.data.data.status === 'COMPLETED' && res.data.data.evaluation_id) {
              return res.data.data.evaluation_id
            }
            if (res.data.data.status === 'FAILED') {
              return null
            }
          }
        } catch {
          // 评估尚未完成，继续轮询
        }
        // 指数退避 + jitter（最大 10 秒）
        const jitter = Math.floor(Math.random() * 1000)
        await new Promise(resolve => setTimeout(resolve, interval + jitter))
        interval = Math.min(interval * 1.5, 10000)
      }
      evaluationStatus.value = 'FAILED'
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

  // --- 草稿清理：清除指定会话的 localStorage 草稿数据 【问题17】 ---
  function clearDraftsForSession(sid: string) {
    const prefix = `interview_draft_${sid}_`
    const keysToRemove: string[] = []
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i)
      if (key && key.startsWith(prefix)) {
        keysToRemove.push(key)
      }
    }
    keysToRemove.forEach(key => localStorage.removeItem(key))
  }

  // ===================== 技能列表缓存 =====================
  // 技能列表很少变化，缓存 5 分钟，多个组件共享同一份数据
  const skills = ref<SkillInfo[]>([])
  const skillsLoadedAt = ref(0)
  const _skillsPromise: { value: Promise<SkillInfo[]> | null } = { value: null }
  const SKILLS_TTL = 5 * 60 * 1000  // 5 分钟

  /** 获取技能列表（带缓存 + 并发去重） */
  async function fetchSkills(force = false): Promise<SkillInfo[]> {
    const now = Date.now()
    if (!force && skills.value.length > 0 && now - skillsLoadedAt.value < SKILLS_TTL) {
      return skills.value
    }
    // 并发去重：如果已有进行中的请求，复用同一个 Promise
    if (_skillsPromise.value) return _skillsPromise.value

    _skillsPromise.value = (async () => {
      try {
        const res = await getSkillListAPI()
        if (res.data.status_code === 200 && res.data.data) {
          skills.value = res.data.data.skills || []
          skillsLoadedAt.value = Date.now()
        }
        return skills.value
      } finally {
        _skillsPromise.value = null
      }
    })()

    return _skillsPromise.value
  }

  /** 根据 skill_id 获取技能名称 */
  function getSkillName(skillId: string): string {
    const skill = skills.value.find(s => s.id === skillId)
    return skill?.name || skillId
  }

  // ===================== 面试历史缓存 =====================
  // 缓存 30 秒，避免父组件和子组件重复请求；支持并发去重
  const historySessions = ref<InterviewSession[]>([])
  const historyLoadedAt = ref(0)
  const _historyPromise: { value: Promise<InterviewSession[]> | null } = { value: null }
  const HISTORY_TTL = 30 * 1000  // 30 秒

  /** 获取面试历史列表（带缓存 + 并发去重） */
  async function fetchHistory(force = false): Promise<InterviewSession[]> {
    const now = Date.now()
    if (!force && historySessions.value.length >= 0 && now - historyLoadedAt.value < HISTORY_TTL && historyLoadedAt.value > 0) {
      return historySessions.value
    }
    if (_historyPromise.value) return _historyPromise.value

    _historyPromise.value = (async () => {
      try {
        const res = await getInterviewHistoryAPI()
        if (res.data.status_code === 200 && res.data.data) {
          historySessions.value = res.data.data.sessions || []
          historyLoadedAt.value = Date.now()
        }
        return historySessions.value
      } finally {
        _historyPromise.value = null
      }
    })()

    return _historyPromise.value
  }

  /** 带筛选参数的历史查询（不走缓存，每次实时查询） */
  async function queryHistory(params?: HistoryQueryParams): Promise<{ sessions: InterviewSession[]; total: number }> {
    const res = await getInterviewHistoryAPI(params)
    if (res.data.status_code === 200 && res.data.data) {
      return {
        sessions: res.data.data.sessions || [],
        total: res.data.data.total || 0,
      }
    }
    return { sessions: [], total: 0 }
  }

  function reset() {
    // 【问题17】重置前清理旧会话的草稿
    if (sessionId.value) {
      clearDraftsForSession(sessionId.value)
    }
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
    evaluationStatus.value = ''
    evaluationElapsed.value = 0
    // 刷新历史缓存（不阻塞 reset）
    historyLoadedAt.value = 0
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
    evaluationStatus,
    evaluationElapsed,
    // Cached state
    skills,
    historySessions,
    // Getters
    isActive,
    isCompleted,
    progressPercent,
    // Actions
    startInterview,
    submitAnswerStream,
    endInterview,
    fetchReport,
    reset,
    // Cached data actions
    fetchSkills,
    getSkillName,
    fetchHistory,
    queryHistory,
  }
}, {
  persist: {
    // 【问题20】排除 messages 数组，减少 LocalStorage 占用
    pick: [
      'sessionId', 'skillId', 'skillName', 'difficulty', 'questionCount',
      'currentQuestion', 'progress', 'status', 'evaluationId',
    ],
  },
})


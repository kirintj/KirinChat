import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'

// Mock the API module before importing the store
vi.mock('../../../apis/interview', () => ({
  startInterviewAPI: vi.fn(),
  submitAnswerAPI: vi.fn(),
  completeInterviewAPI: vi.fn(),
  getEvaluationReportAPI: vi.fn(),
  getSkillListAPI: vi.fn(),
  getSessionDetailAPI: vi.fn(),
  getInterviewHistoryAPI: vi.fn(),
}))

import { useInterviewStore } from '../../../store/interview'
import {
  startInterviewAPI,
  submitAnswerAPI,
  completeInterviewAPI,
  getEvaluationReportAPI,
} from '../../../apis/interview'

const mockStartInterviewAPI = vi.mocked(startInterviewAPI)
const mockSubmitAnswerAPI = vi.mocked(submitAnswerAPI)
const mockCompleteInterviewAPI = vi.mocked(completeInterviewAPI)
const mockGetEvaluationReportAPI = vi.mocked(getEvaluationReportAPI)

describe('useInterviewStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  // -----------------------------------------------------------------
  // Initial state
  // -----------------------------------------------------------------
  describe('initial state', () => {
    it('starts with IDLE status', () => {
      const store = useInterviewStore()
      expect(store.status).toBe('IDLE')
      expect(store.sessionId).toBe('')
      expect(store.messages).toEqual([])
      expect(store.progress).toEqual({ current: 0, total: 0 })
    })

    it('isActive is false when IDLE', () => {
      const store = useInterviewStore()
      expect(store.isActive).toBe(false)
    })

    it('isCompleted is false when IDLE', () => {
      const store = useInterviewStore()
      expect(store.isCompleted).toBe(false)
    })

    it('progressPercent is 0 when total is 0', () => {
      const store = useInterviewStore()
      expect(store.progressPercent).toBe(0)
    })
  })

  // -----------------------------------------------------------------
  // startInterview
  // -----------------------------------------------------------------
  describe('startInterview', () => {
    it('sets status to IN_PROGRESS on success', async () => {
      mockStartInterviewAPI.mockResolvedValue({
        data: {
          status_code: 200,
          status_message: 'ok',
          data: {
            session_id: 'sess-1',
            first_question: {
              id: 'q1',
              type: 'OPEN',
              category: 'java',
              content: '什么是多态？',
            },
          },
        },
      } as any)

      const store = useInterviewStore()
      const result = await store.startInterview('java-backend', 'MEDIUM', 10)

      expect(result).toBe(true)
      expect(store.status).toBe('IN_PROGRESS')
      expect(store.sessionId).toBe('sess-1')
      expect(store.isActive).toBe(true)
    })

    it('populates first question as interviewer message', async () => {
      mockStartInterviewAPI.mockResolvedValue({
        data: {
          status_code: 200,
          status_message: 'ok',
          data: {
            session_id: 'sess-1',
            first_question: {
              id: 'q1',
              type: 'OPEN',
              category: 'java',
              content: '解释 SOLID 原则',
            },
          },
        },
      } as any)

      const store = useInterviewStore()
      await store.startInterview('java-backend', 'HARD', 5)

      expect(store.messages).toHaveLength(1)
      expect(store.messages[0]).toEqual({
        role: 'interviewer',
        content: '解释 SOLID 原则',
      })
      expect(store.currentQuestion?.id).toBe('q1')
    })

    it('sets progress total from question_count', async () => {
      mockStartInterviewAPI.mockResolvedValue({
        data: {
          status_code: 200,
          status_message: 'ok',
          data: {
            session_id: 'sess-1',
            first_question: { id: 'q1', type: 'OPEN', category: 'java', content: 'Q1' },
          },
        },
      } as any)

      const store = useInterviewStore()
      await store.startInterview('java-backend', 'EASY', 15)

      expect(store.progress.total).toBe(15)
      expect(store.progress.current).toBe(0)
    })

    it('returns false on API failure', async () => {
      mockStartInterviewAPI.mockResolvedValue({
        data: { status_code: 500, status_message: 'error', data: null },
      } as any)

      const store = useInterviewStore()
      const result = await store.startInterview('java-backend', 'MEDIUM', 10)

      expect(result).toBe(false)
      expect(store.status).toBe('IDLE')
    })

    it('sets loading during API call', async () => {
      let resolveFn: any
      mockStartInterviewAPI.mockReturnValue(
        new Promise((resolve) => { resolveFn = resolve }) as any
      )

      const store = useInterviewStore()
      const promise = store.startInterview('java-backend', 'MEDIUM', 10)

      expect(store.loading).toBe(true)

      resolveFn({
        data: {
          status_code: 200,
          status_message: 'ok',
          data: {
            session_id: 's1',
            first_question: { id: 'q1', type: 'OPEN', category: 'java', content: 'Q' },
          },
        },
      })
      await promise

      expect(store.loading).toBe(false)
    })
  })

  // -----------------------------------------------------------------
  // submitAnswer
  // -----------------------------------------------------------------
  describe('submitAnswer', () => {
    async function startSession(store: ReturnType<typeof useInterviewStore>) {
      mockStartInterviewAPI.mockResolvedValue({
        data: {
          status_code: 200,
          status_message: 'ok',
          data: {
            session_id: 'sess-1',
            first_question: { id: 'q1', type: 'OPEN', category: 'java', content: 'Q1' },
          },
        },
      } as any)
      await store.startInterview('java-backend', 'MEDIUM', 10)
    }

    it('appends candidate message to messages', async () => {
      const store = useInterviewStore()
      await startSession(store)

      mockSubmitAnswerAPI.mockResolvedValue({
        data: {
          status_code: 200,
          status_message: 'ok',
          data: {
            next_question: { id: 'q2', type: 'OPEN', category: 'java', content: 'Q2' },
            is_completed: false,
          },
        },
      } as any)

      await store.submitAnswer('这是我的答案')

      const candidateMsgs = store.messages.filter((m) => m.role === 'candidate')
      expect(candidateMsgs).toHaveLength(1)
      expect(candidateMsgs[0].content).toBe('这是我的答案')
    })

    it('adds next question as interviewer message', async () => {
      const store = useInterviewStore()
      await startSession(store)

      mockSubmitAnswerAPI.mockResolvedValue({
        data: {
          status_code: 200,
          status_message: 'ok',
          data: {
            next_question: { id: 'q2', type: 'OPEN', category: 'mysql', content: '什么是索引？' },
            is_completed: false,
          },
        },
      } as any)

      await store.submitAnswer('多态是...')

      const interviewerMsgs = store.messages.filter((m) => m.role === 'interviewer')
      expect(interviewerMsgs).toHaveLength(2) // first Q + next Q
      expect(interviewerMsgs[1].content).toBe('什么是索引？')
    })

    it('increments progress on each answer', async () => {
      const store = useInterviewStore()
      await startSession(store)

      mockSubmitAnswerAPI.mockResolvedValue({
        data: {
          status_code: 200,
          status_message: 'ok',
          data: {
            next_question: { id: 'q2', type: 'OPEN', category: 'java', content: 'Q2' },
            is_completed: false,
          },
        },
      } as any)

      await store.submitAnswer('answer 1')
      expect(store.progress.current).toBe(1)

      mockSubmitAnswerAPI.mockResolvedValue({
        data: {
          status_code: 200,
          status_message: 'ok',
          data: {
            next_question: { id: 'q3', type: 'OPEN', category: 'java', content: 'Q3' },
            is_completed: false,
          },
        },
      } as any)

      await store.submitAnswer('answer 2')
      expect(store.progress.current).toBe(2)
    })

    it('sets COMPLETED when is_completed is true', async () => {
      const store = useInterviewStore()
      await startSession(store)

      mockSubmitAnswerAPI.mockResolvedValue({
        data: {
          status_code: 200,
          status_message: 'ok',
          data: {
            next_question: null,
            is_completed: true,
          },
        },
      } as any)

      await store.submitAnswer('final answer')

      expect(store.status).toBe('COMPLETED')
      expect(store.isCompleted).toBe(true)
      expect(store.currentQuestion).toBeNull()
    })

    it('returns false when no active session', async () => {
      const store = useInterviewStore()
      const result = await store.submitAnswer('answer')
      expect(result).toBe(false)
    })
  })

  // -----------------------------------------------------------------
  // endInterview
  // -----------------------------------------------------------------
  describe('endInterview', () => {
    it('returns evaluation_id on success', async () => {
      const store = useInterviewStore()

      // Manually set session state
      store.sessionId = 'sess-1'
      store.status = 'IN_PROGRESS'

      mockCompleteInterviewAPI.mockResolvedValue({
        data: {
          status_code: 200,
          status_message: 'ok',
          data: {
            evaluation_id: 'eval-1',
            status: 'EVALUATED',
          },
        },
      } as any)

      const evalId = await store.endInterview()

      expect(evalId).toBe('eval-1')
      expect(store.evaluationId).toBe('eval-1')
      expect(store.status).toBe('COMPLETED')
    })

    it('returns null when no session', async () => {
      const store = useInterviewStore()
      const evalId = await store.endInterview()
      expect(evalId).toBeNull()
    })
  })

  // -----------------------------------------------------------------
  // fetchReport
  // -----------------------------------------------------------------
  describe('fetchReport', () => {
    it('returns report data on success', async () => {
      mockGetEvaluationReportAPI.mockResolvedValue({
        data: {
          status_code: 200,
          status_message: 'ok',
          data: {
            id: 'eval-1',
            total_score: 85,
            category_scores: { java: 90, mysql: 80 },
            summary: '整体表现良好',
            strengths: ['基础扎实'],
            improvements: ['系统设计'],
          },
        },
      } as any)

      const store = useInterviewStore()
      const report = await store.fetchReport('eval-1')

      expect(report).not.toBeNull()
      expect(report?.total_score).toBe(85)
      expect(report?.category_scores.java).toBe(90)
    })

    it('returns null on failure', async () => {
      mockGetEvaluationReportAPI.mockRejectedValue(new Error('network'))

      const store = useInterviewStore()
      const report = await store.fetchReport('eval-1')
      expect(report).toBeNull()
    })
  })

  // -----------------------------------------------------------------
  // reset
  // -----------------------------------------------------------------
  describe('reset', () => {
    it('clears all state back to initial', async () => {
      const store = useInterviewStore()

      // Set some state
      store.sessionId = 'sess-1'
      store.skillId = 'java-backend'
      store.skillName = 'Java 后端'
      store.status = 'IN_PROGRESS'
      store.messages = [{ role: 'interviewer', content: 'Q1' }]
      store.progress = { current: 3, total: 10 }
      store.evaluationId = 'eval-1'

      store.reset()

      expect(store.sessionId).toBe('')
      expect(store.skillId).toBe('')
      expect(store.skillName).toBe('')
      expect(store.status).toBe('IDLE')
      expect(store.messages).toEqual([])
      expect(store.progress).toEqual({ current: 0, total: 0 })
      expect(store.evaluationId).toBe('')
      expect(store.isActive).toBe(false)
    })
  })
})

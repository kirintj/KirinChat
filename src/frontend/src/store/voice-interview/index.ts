import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  createVoiceSessionAPI,
  endVoiceSessionAPI,
  getVoiceEvaluationAPI,
  triggerVoiceEvaluationAPI,
  type VoiceSession,
  type VoiceEvaluation,
} from '../../apis/voice-interview'

export interface VoiceMessage {
  role: 'user' | 'ai'
  text: string
  phase: string
  timestamp?: number
}

export const useVoiceInterviewStore = defineStore('voice-interview', () => {
  const sessionId = ref<string | null>(null)
  const session = ref<VoiceSession | null>(null)
  const status = ref<'idle' | 'connecting' | 'recording' | 'ai_speaking' | 'paused' | 'completed' | 'processing'>(
    'idle',
  )
  const wsStatus = ref<'connecting' | 'open' | 'closed'>('closed')
  const currentPhase = ref('INTRO')
  const userText = ref('')
  const aiText = ref('')
  const messages = ref<VoiceMessage[]>([])
  const isAiSpeaking = ref(false)
  const isRecording = ref(false)
  const evaluateStatus = ref('PENDING')
  const evaluation = ref<VoiceEvaluation | null>(null)
  const errorMessage = ref('')

  const isActive = computed(() => status.value !== 'idle' && status.value !== 'completed')
  const isConnected = computed(() => wsStatus.value === 'open')

  async function createSession(data: {
    skill_id: string
    difficulty: string
    resume_id?: string
    planned_duration: number
    phases: Record<string, boolean>
  }): Promise<string | null> {
    const res = await createVoiceSessionAPI(data)
    if (res.data.status_code === 200 && res.data.data) {
      session.value = res.data.data
      sessionId.value = res.data.data.id
      currentPhase.value = res.data.data.current_phase
      status.value = 'connecting'
      messages.value = []
      userText.value = ''
      aiText.value = ''
      errorMessage.value = ''
      return res.data.data.id
    }
    return null
  }

  function addMessage(role: 'user' | 'ai', text: string) {
    if (!text || !text.trim()) return
    messages.value.push({
      role,
      text,
      phase: currentPhase.value,
      timestamp: Date.now(),
    })
  }

  async function endSession(): Promise<boolean> {
    if (!sessionId.value) return false
    try {
      // Try REST API as fallback
      await endVoiceSessionAPI(sessionId.value)
    } catch {
      // Ignore — the WebSocket end_interview command may have already succeeded
    }
    status.value = 'completed'
    if (session.value) {
      session.value.status = 'COMPLETED'
    }
    return true
  }

  async function fetchEvaluation() {
    if (!sessionId.value) return
    const res = await getVoiceEvaluationAPI(sessionId.value)
    if (res.data.status_code === 200 && res.data.data) {
      evaluation.value = res.data.data
      evaluateStatus.value = 'COMPLETED'
    }
  }

  async function triggerEvaluation() {
    if (!sessionId.value) return
    evaluateStatus.value = 'PROCESSING'
    try {
      await triggerVoiceEvaluationAPI(sessionId.value)
    } catch {
      // If the trigger task may still run even if this call fails silently — we'll try fetching anyway
    }
    // Poll for evaluation result
    let polls = 0
    while (polls < 12) {
      await new Promise((r) => setTimeout(r, 5000))
      try {
        const res = await getVoiceEvaluationAPI(sessionId.value)
        if (res.data.status_code === 200 && res.data.data) {
          evaluation.value = res.data.data
          evaluateStatus.value = 'COMPLETED'
          break
        }
      } catch {
        // ignore and retry
      }
      polls++
    }
  }

  function setError(msg: string) {
    errorMessage.value = msg
  }

  function clearError() {
    errorMessage.value = ''
  }

  function reset() {
    sessionId.value = null
    session.value = null
    status.value = 'idle'
    wsStatus.value = 'closed'
    currentPhase.value = 'INTRO'
    userText.value = ''
    aiText.value = ''
    messages.value = []
    isAiSpeaking.value = false
    isRecording.value = false
    evaluateStatus.value = 'PENDING'
    evaluation.value = null
    errorMessage.value = ''
  }

  return {
    sessionId,
    session,
    status,
    wsStatus,
    currentPhase,
    userText,
    aiText,
    messages,
    isAiSpeaking,
    isRecording,
    evaluateStatus,
    evaluation,
    errorMessage,
    isActive,
    isConnected,
    createSession,
    addMessage,
    endSession,
    fetchEvaluation,
    triggerEvaluation,
    setError,
    clearError,
    reset,
  }
})

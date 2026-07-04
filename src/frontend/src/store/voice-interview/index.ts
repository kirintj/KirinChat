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
}

export const useVoiceInterviewStore = defineStore('voice-interview', () => {
  const sessionId = ref<string | null>(null)
  const session = ref<VoiceSession | null>(null)
  const status = ref<'idle' | 'connecting' | 'recording' | 'ai_speaking' | 'paused' | 'completed'>('idle')
  const currentPhase = ref('INTRO')
  const userText = ref('')
  const aiText = ref('')
  const messages = ref<VoiceMessage[]>([])
  const isAiSpeaking = ref(false)
  const isRecording = ref(false)
  const evaluateStatus = ref('PENDING')
  const evaluation = ref<VoiceEvaluation | null>(null)

  const isActive = computed(() => status.value !== 'idle' && status.value !== 'completed')

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
      return res.data.data.id
    }
    return null
  }

  function addMessage(role: 'user' | 'ai', text: string) {
    messages.value.push({ role, text, phase: currentPhase.value })
  }

  async function endSession() {
    if (!sessionId.value) return
    await endVoiceSessionAPI(sessionId.value)
    status.value = 'completed'
    if (session.value) {
      session.value.status = 'COMPLETED'
    }
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
    await triggerVoiceEvaluationAPI(sessionId.value)
    evaluateStatus.value = 'PROCESSING'
  }

  function reset() {
    sessionId.value = null
    session.value = null
    status.value = 'idle'
    currentPhase.value = 'INTRO'
    userText.value = ''
    aiText.value = ''
    messages.value = []
    isAiSpeaking.value = false
    isRecording.value = false
    evaluateStatus.value = 'PENDING'
    evaluation.value = null
  }

  return {
    sessionId, session, status, currentPhase,
    userText, aiText, messages,
    isAiSpeaking, isRecording, evaluateStatus, evaluation,
    isActive,
    createSession, addMessage, endSession,
    fetchEvaluation, triggerEvaluation, reset,
  }
})

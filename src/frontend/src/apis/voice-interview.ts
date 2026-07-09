import { request } from '../utils/request'

export interface UnifiedResponse<T> {
  status_code: number
  status_message: string
  data: T
}

export interface VoiceSession {
  id: string
  skill_id: string
  difficulty: string
  resume_id: string | null
  planned_duration: number
  current_phase: string
  status: string
  evaluate_status: string
  phases_enabled: Record<string, boolean>
  start_time: string | null
  end_time: string | null
  actual_duration: number | null
}

export interface VoiceMessage {
  id: string
  session_id: string
  phase: string
  user_text: string | null
  ai_text: string | null
  sequence_num: number
  timestamp: string | null
}

export interface VoiceEvaluation {
  id: string
  session_id: string
  overall_score: number | null
  overall_feedback: string | null
  category_scores: Record<string, number> | null
  question_evaluations: any[] | null
  strengths: string[] | null
  improvements: string[] | null
  reference_answers: any[] | null
  interviewer_role: string | null
  interview_date: string | null
}

// --- REST API ---

export function createVoiceSessionAPI(data: {
  skill_id: string
  difficulty: string
  resume_id?: string
  planned_duration: number
  phases: Record<string, boolean>
}) {
  return request<UnifiedResponse<VoiceSession>>({
    url: '/api/v1/voice-interview/sessions',
    method: 'POST',
    data,
  })
}

export function listVoiceSessionsAPI(status?: string) {
  return request<UnifiedResponse<{ sessions: VoiceSession[]; total: number }>>({
    url: '/api/v1/voice-interview/sessions',
    method: 'GET',
    params: status ? { status } : undefined,
  })
}

export function getVoiceSessionAPI(sessionId: string) {
  return request<UnifiedResponse<VoiceSession>>({
    url: `/api/v1/voice-interview/sessions/${sessionId}`,
    method: 'GET',
  })
}

export function endVoiceSessionAPI(sessionId: string) {
  return request<UnifiedResponse<{ message: string }>>({
    url: `/api/v1/voice-interview/sessions/${sessionId}/end`,
    method: 'POST',
  })
}

export function pauseVoiceSessionAPI(sessionId: string) {
  return request<UnifiedResponse<{ message: string }>>({
    url: `/api/v1/voice-interview/sessions/${sessionId}/pause`,
    method: 'PUT',
  })
}

export function resumeVoiceSessionAPI(sessionId: string) {
  return request<UnifiedResponse<{ message: string }>>({
    url: `/api/v1/voice-interview/sessions/${sessionId}/resume`,
    method: 'PUT',
  })
}

export function getVoiceMessagesAPI(sessionId: string) {
  return request<UnifiedResponse<VoiceMessage[]>>({
    url: `/api/v1/voice-interview/sessions/${sessionId}/messages`,
    method: 'GET',
  })
}

export function getVoiceEvaluationAPI(sessionId: string) {
  return request<UnifiedResponse<VoiceEvaluation | null>>({
    url: `/api/v1/voice-interview/sessions/${sessionId}/evaluation`,
    method: 'GET',
  })
}

export function triggerVoiceEvaluationAPI(sessionId: string) {
  return request<UnifiedResponse<{ message: string }>>({
    url: `/api/v1/voice-interview/sessions/${sessionId}/evaluation`,
    method: 'POST',
  })
}

// --- WebSocket Client ---

export type WsCallbacks = {
  onSubtitle?: (text: string, isFinal: boolean) => void
  onTextResponse?: (content: string, final: boolean) => void
  onAudioChunk?: (base64Wav: string, index: number, isLast: boolean) => void
  onAudioFull?: (base64Wav: string, text: string) => void
  onControl?: (action: string, message?: string, phase?: string) => void
  onError?: (message: string) => void
  onOpen?: () => void
  onClose?: () => void
  onStatusChange?: (status: 'connecting' | 'open' | 'closed') => void
}

export class VoiceInterviewWebSocket {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnects = 3
  private sessionId: string = ''
  private callbacks: WsCallbacks = {}
  private heartbeatTimer: number | null = null
  private pongTimer: number | null = null
  private lastPongAt: number = 0
  private reconnectToken: string = ''
  private _isOpen: boolean = false

  get isOpen(): boolean {
    return this._isOpen
  }

  connect(sessionId: string, callbacks: WsCallbacks): void {
    this.sessionId = sessionId
    this.callbacks = callbacks
    this.reconnectAttempts = 0
    this.reconnectToken = localStorage.getItem('token') || ''
    this._doConnect()
  }

  private _doConnect(): void {
    const token = this.reconnectToken
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const url = `${protocol}//${window.location.host}/api/v1/voice-interview/ws/${this.sessionId}?token=${token}`

    try {
      this.ws = new WebSocket(url)
    } catch (e) {
      this.callbacks.onError?.(`连接失败：${e}`)
      this._tryReconnect()
      return
    }

    this.callbacks.onStatusChange?.('connecting')

    this.ws.onopen = () => {
      this._isOpen = true
      this.reconnectAttempts = 0
      this.lastPongAt = Date.now()
      this._startHeartbeat()
      this.callbacks.onStatusChange?.('open')
      this.callbacks.onOpen?.()
    }

    this.ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data)
        switch (msg.type) {
          case 'subtitle':
            this.callbacks.onSubtitle?.(msg.text, msg.isFinal)
            break
          case 'text':
            this.callbacks.onTextResponse?.(msg.content, msg.final)
            break
          case 'audio_chunk':
            this.callbacks.onAudioChunk?.(msg.data, msg.index, msg.isLast)
            break
          case 'audio':
            this.callbacks.onAudioFull?.(msg.data, msg.text)
            break
          case 'control':
            this.callbacks.onControl?.(msg.action, msg.message, msg.phase)
            break
          case 'error':
            this.callbacks.onError?.(msg.message)
            break
          case 'ping':
            // Server ping — respond with pong
            this._send({ type: 'pong', ts: msg.ts })
            break
          case 'pong':
            // Response to our ping
            this.lastPongAt = Date.now()
            break
        }
      } catch (e) {
        // Ignore malformed messages
      }
    }

    this.ws.onclose = (event) => {
      this._isOpen = false
      this._stopHeartbeat()
      this.callbacks.onStatusChange?.('closed')
      if (!event.wasClean && this.reconnectAttempts < this.maxReconnects) {
        this._tryReconnect()
      } else {
        this.callbacks.onClose?.()
      }
    }

    this.ws.onerror = () => {
      // Error details are not exposed; onclose will fire next
    }
  }

  private _tryReconnect(): void {
    this.reconnectAttempts++
    const delay = Math.min(2000 * this.reconnectAttempts, 10000)
    window.setTimeout(() => this._doConnect(), delay)
  }

  private _startHeartbeat(): void {
    this._stopHeartbeat()
    this.heartbeatTimer = window.setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this._send({ type: 'ping', ts: Date.now() })
      }
    }, 20000)
    // Watchdog: if no pong in 60s, treat connection as dead
    this.pongTimer = window.setInterval(() => {
      if (this._isOpen && Date.now() - this.lastPongAt > 60000) {
        this.callbacks.onError?.('连接超时，正在尝试重新连接…')
        try {
          this.ws?.close()
        } catch {
          // ignore
        }
        this._tryReconnect()
      }
    }, 15000)
  }

  private _stopHeartbeat(): void {
    if (this.heartbeatTimer !== null) {
      clearInterval(this.heartbeatTimer)
      this.heartbeatTimer = null
    }
    if (this.pongTimer !== null) {
      clearInterval(this.pongTimer)
      this.pongTimer = null
    }
  }

  private _send(payload: any): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      try {
        this.ws.send(JSON.stringify(payload))
      } catch {
        // Silently drop if serialization fails
      }
    }
  }

  sendAudio(base64Pcm: string): void {
    this._send({ type: 'audio', data: base64Pcm, timestamp: Date.now() })
  }

  sendControl(action: string, data?: any): void {
    this._send({ type: 'control', action, data, timestamp: Date.now() })
  }

  disconnect(): void {
    this._stopHeartbeat()
    if (this.ws) {
      try {
        this.ws.onclose = null
        this.ws.close()
      } catch {
        // ignore
      }
      this.ws = null
    }
    this._isOpen = false
  }
}

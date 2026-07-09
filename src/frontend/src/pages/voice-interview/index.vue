<script setup lang="ts">
import { ref, onUnmounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { HButton, HMessage } from '@/components/ui'
import { useVoiceInterviewStore } from '../../store/voice-interview'
import { VoiceInterviewWebSocket } from '../../apis/voice-interview'
import AudioRecorder from './components/AudioRecorder.vue'
import RealtimeSubtitle from './components/RealtimeSubtitle.vue'
import VoiceControls from './components/VoiceControls.vue'
import AudioPlayer from './components/AudioPlayer.vue'
import VoiceConfigDialog from './components/VoiceConfigDialog.vue'

const router = useRouter()
const store = useVoiceInterviewStore()

const showConfig = ref(true)
const wsClient = ref<VoiceInterviewWebSocket | null>(null)
const audioRecorder = ref<InstanceType<typeof AudioRecorder>>()
const audioPlayer = ref<InstanceType<typeof AudioPlayer>>()
const isEnding = ref(false)
const subtitlePending = ref(false)

const STATUS_LABEL_MAP: Record<string, string> = {
  idle: '待开始',
  connecting: '连接中',
  recording: '进行中',
  ai_speaking: 'AI 播报',
  paused: '已暂停',
  completed: '已结束',
  processing: '处理中',
}
function statusLabel(status: string): string {
  return STATUS_LABEL_MAP[status] || status
}

watch(
  () => store.status,
  (s) => {
    if (s === 'completed') {
      nextTick(() => {
        // Trigger evaluation in background; UI shows "评估生成中…"
        if (store.evaluateStatus !== 'COMPLETED') {
          store.triggerEvaluation()
        }
      })
    }
  },
)

async function onStartConfig(config: any) {
  // Normalize phases to what backend expects (key-only flags dict)
  const normalizedPhases: Record<string, boolean> = {}
  if (config.phases) {
    for (const key of Object.keys(config.phases)) {
      normalizedPhases[key.toUpperCase()] = !!config.phases[key]
    }
  }
  const sessionId = await store.createSession({
    skill_id: config.skill_id,
    difficulty: config.difficulty,
    resume_id: config.resume_id,
    planned_duration: config.planned_duration,
    phases: normalizedPhases,
  })
  if (!sessionId) {
    HMessage.error('创建面试失败，请重试')
    return
  }
  connectWebSocket(sessionId)
}

function connectWebSocket(sessionId: string) {
  const client = new VoiceInterviewWebSocket()
  client.connect(sessionId, {
    onStatusChange: (s) => {
      store.wsStatus = s
      if (s === 'open' && store.status === 'connecting') {
        store.status = 'recording'
      }
    },
    onOpen: () => {
      store.wsStatus = 'open'
      if (store.status === 'connecting') {
        store.status = 'recording'
      }
    },
    onSubtitle: (text, isFinal) => {
      if (text && text.trim()) {
        store.userText = text
      }
      if (isFinal) {
        subtitlePending.value = false
      }
    },
    onTextResponse: (content, final) => {
      if (!final) {
        store.aiText += content
      } else {
        if (store.aiText) store.addMessage('ai', store.aiText)
        store.aiText = ''
      }
    },
    onAudioChunk: (base64, index, isLast) => {
      audioPlayer.value?.playChunk(base64, index, isLast)
    },
    onAudioFull: (base64, text) => {
      audioPlayer.value?.playFullAudio(base64)
      if (text && text.trim()) {
        store.aiText = text
      }
    },
    onControl: (action, message, phase) => {
      switch (action) {
        case 'asr_ready':
          if (store.status === 'connecting') store.status = 'recording'
          break
        case 'welcome':
          if (message && message.trim()) {
            store.addMessage('ai', message)
            store.aiText = ''
          }
          if (store.status !== 'completed') {
            store.status = 'recording'
          }
          break
        case 'pause_timeout':
          store.status = 'paused'
          HMessage.warning('面试已自动暂停')
          break
        case 'pause_timeout_warning':
          HMessage.warning('长时间未操作，即将自动暂停')
          break
        case 'ended':
          store.status = 'completed'
          break
        case 'phase_changed':
          if (phase) store.currentPhase = phase
          break
      }
    },
    onError: (message) => {
      store.setError(message)
      // Show HMessage once to grab user attention
      if (message) {
        HMessage.error(message)
      }
    },
    onClose: () => {
      if (store.isActive) {
        HMessage.warning('连接已断开，请刷新页面重新开始')
      }
    },
  })
  wsClient.value = client
}

function onAudioData(base64Pcm: string) {
  wsClient.value?.sendAudio(base64Pcm)
}

function onSubmit() {
  const text = store.userText
  if (!text || !text.trim()) {
    HMessage.info('请先说话或手动输入内容后提交')
    return
  }
  store.addMessage('user', text)
  store.userText = ''
  wsClient.value?.sendControl('submit', { text })
  store.aiText = ''
}

function onToggleRecord() {
  audioRecorder.value?.toggle()
}

function onPause() {
  wsClient.value?.sendControl('pause')
  store.status = 'paused'
}

function onResume() {
  wsClient.value?.sendControl('resume')
  store.status = 'recording'
}

async function onEnd() {
  if (isEnding.value) return
  isEnding.value = true

  // Try WebSocket first
  let ended = false
  if (wsClient.value && wsClient.value.isOpen) {
    wsClient.value.sendControl('end_interview')
    // Give server a moment to respond over WebSocket
    await new Promise((r) => setTimeout(r, 800))
    if (store.status === 'completed') {
      ended = true
    }
  }

  // Fallback: use REST API
  if (!ended) {
    const ok = await store.endSession()
    if (ok) {
      ended = true
      store.status = 'completed'
    }
  }

  // Last resort: force local state to completed (even if server unreachable)
  if (!ended) {
    store.status = 'completed'
    HMessage.warning('未能通知服务器，本地已结束面试')
  }

  isEnding.value = false
}

function onChangePhase(phase: string) {
  wsClient.value?.sendControl('start_phase', { phase })
  store.currentPhase = phase
}

onUnmounted(() => {
  wsClient.value?.disconnect()
  store.reset()
})
</script>

<template>
  <div class="voice-interview-page page">
    <VoiceConfigDialog v-model:visible="showConfig" @confirm="onStartConfig" />

    <div v-if="store.sessionId" class="interview-container">
      <div class="header">
        <h2>语音面试 · {{ store.session?.skill_id }}</h2>
        <div class="header-right">
          <span class="ws-tag" :class="store.wsStatus">
            {{ store.wsStatus === 'open' ? '已连接' : store.wsStatus === 'connecting' ? '连接中…' : '已断开' }}
          </span>
          <span class="status-tag" :class="store.status">{{ statusLabel(store.status) }}</span>
        </div>
      </div>

      <RealtimeSubtitle
        :messages="store.messages"
        :userText="store.userText"
        :aiText="store.aiText"
        :isAiSpeaking="store.isAiSpeaking"
        :isRecording="store.isRecording"
      />

      <div v-if="store.errorMessage" class="error-bar">{{ store.errorMessage }}</div>

      <div class="bottom-bar">
        <AudioRecorder
          ref="audioRecorder"
          :disabled="store.isAiSpeaking || store.status === 'completed'"
          @audioData="onAudioData"
          @recordingChange="(v: boolean) => (store.isRecording = v)"
        />
        <AudioPlayer ref="audioPlayer" @playStart="store.isAiSpeaking = true" @playEnd="store.isAiSpeaking = false" />
      </div>

      <VoiceControls
        :isRecording="store.isRecording"
        :isAiSpeaking="store.isAiSpeaking"
        :isProcessing="store.status === 'processing' || isEnding"
        :status="store.status"
        :currentPhase="store.currentPhase"
        :phasesEnabled="store.session?.phases_enabled || {}"
        @toggleRecord="onToggleRecord"
        @submit="onSubmit"
        @pause="onPause"
        @resume="onResume"
        @end="onEnd"
        @changePhase="onChangePhase"
      />
    </div>

    <div v-if="store.status === 'completed'" class="completed-overlay">
      <h3>面试已结束</h3>
      <p v-if="store.evaluateStatus === 'PROCESSING'">评估生成中…</p>
      <p v-else-if="store.evaluation">综合评分：{{ store.evaluation.overall_score }}</p>
      <HButton @click="router.push('/interview')">返回面试中心</HButton>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.voice-interview-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  position: relative;
}

.interview-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid var(--harmony-comp-divider);

  h2 {
    margin: 0;
    font-size: var(--harmony-font-size-subtitle-l);
  }
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.ws-tag {
  font-size: var(--harmony-font-size-body-s);
  padding: 2px 8px;
  border-radius: var(--harmony-corner-level3);
  background: var(--harmony-comp-background-tertiary);
  color: var(--harmony-font-secondary);

  &.open {
    background: var(--harmony-success-bg);
    color: var(--harmony-success);
  }
  &.connecting {
    background: var(--harmony-warning-bg);
    color: var(--harmony-warning);
  }
  &.closed {
    background: var(--harmony-error-bg);
    color: var(--harmony-error);
  }
}

.status-tag {
  font-size: var(--harmony-font-size-body-s);
  padding: 2px 10px;
  border-radius: var(--harmony-corner-radius-level5);

  &.recording {
    background: var(--harmony-confirm-bg);
    color: var(--harmony-confirm);
  }
  &.connecting {
    background: var(--harmony-warning-bg);
    color: var(--harmony-warning);
  }
  &.paused {
    background: var(--harmony-alert-bg);
    color: var(--harmony-alert);
  }
  &.completed {
    background: var(--harmony-comp-emphasize-tertiary);
    color: var(--harmony-brand);
  }
  &.ai_speaking {
    background: var(--harmony-info-bg);
    color: var(--harmony-info);
  }
  &.processing {
    background: var(--harmony-alert-bg);
    color: var(--harmony-alert);
  }
}

.error-bar {
  margin: 8px 16px 0;
  padding: 8px 12px;
  background: var(--harmony-error-bg);
  color: var(--harmony-error);
  font-size: var(--harmony-font-size-body-s);
  border-radius: var(--harmony-corner-radius-level4);
}

.bottom-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 16px;
}

.completed-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  background: var(--harmony-comp-background-primary);
  z-index: var(--z-dropdown);
}
</style>

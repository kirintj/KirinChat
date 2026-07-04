<script setup lang="ts">
import { ref, onUnmounted } from 'vue'
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

async function onStartConfig(config: any) {
  const sessionId = await store.createSession(config)
  if (!sessionId) {
    HMessage.error('创建面试失败')
    return
  }
  connectWebSocket(sessionId)
}

function connectWebSocket(sessionId: string) {
  const client = new VoiceInterviewWebSocket()
  client.connect(sessionId, {
    onOpen: () => { store.status = 'recording' },
    onSubtitle: (text, _isFinal) => { store.userText = text },
    onTextResponse: (content, final) => {
      if (!final) { store.aiText += content }
      else {
        if (store.aiText) store.addMessage('ai', store.aiText)
        store.aiText = ''
      }
    },
    onAudioChunk: (base64, index, isLast) => { audioPlayer.value?.playChunk(base64, index, isLast) },
    onAudioFull: (base64) => { audioPlayer.value?.playFullAudio(base64) },
    onControl: (action, message, phase) => {
      if (action === 'asr_ready') store.status = 'recording'
      else if (action === 'welcome' && message) store.addMessage('ai', message)
      else if (action === 'pause_timeout') { store.status = 'paused'; HMessage.warning('面试已自动暂停') }
      else if (action === 'pause_timeout_warning') HMessage.warning('长时间未操作，即将自动暂停')
      else if (action === 'ended') { store.status = 'completed'; store.triggerEvaluation() }
      else if (action === 'phase_changed' && phase) store.currentPhase = phase
    },
    onError: (message) => HMessage.error(message),
    onClose: () => { if (store.isActive) HMessage.warning('连接断开') },
  })
  wsClient.value = client
}

function onAudioData(base64Pcm: string) { wsClient.value?.sendAudio(base64Pcm) }

function onSubmit() {
  const text = store.userText
  if (text) { store.addMessage('user', text); store.userText = '' }
  wsClient.value?.sendControl('submit', { text })
  store.aiText = ''
}

function onToggleRecord() { audioRecorder.value?.toggle() }
function onPause() { wsClient.value?.sendControl('pause'); store.status = 'paused' }
function onResume() { wsClient.value?.sendControl('resume'); store.status = 'recording' }
function onEnd() { wsClient.value?.sendControl('end_interview') }
function onChangePhase(phase: string) { wsClient.value?.sendControl('start_phase', { phase }); store.currentPhase = phase }

onUnmounted(() => { wsClient.value?.disconnect(); store.reset() })
</script>

<template>
  <div class="voice-interview-page">
    <VoiceConfigDialog v-model:visible="showConfig" @confirm="onStartConfig" />

    <div v-if="store.sessionId" class="interview-container">
      <div class="header">
        <h2>语音面试 - {{ store.session?.skill_id }}</h2>
        <span class="status-tag" :class="store.status">{{ store.status }}</span>
      </div>

      <RealtimeSubtitle
        :messages="store.messages" :userText="store.userText" :aiText="store.aiText"
        :isAiSpeaking="store.isAiSpeaking" :isRecording="store.isRecording"
      />

      <div class="bottom-bar">
        <AudioRecorder ref="audioRecorder" :disabled="store.isAiSpeaking" @audioData="onAudioData" @recordingChange="(v: boolean) => store.isRecording = v" />
        <AudioPlayer ref="audioPlayer" @playStart="store.isAiSpeaking = true" @playEnd="store.isAiSpeaking = false" />
      </div>

      <VoiceControls
        :isRecording="store.isRecording" :isAiSpeaking="store.isAiSpeaking" :isProcessing="false"
        :status="store.status" :currentPhase="store.currentPhase"
        :phasesEnabled="store.session?.phases_enabled || {}"
        @toggleRecord="onToggleRecord" @submit="onSubmit" @pause="onPause" @resume="onResume" @end="onEnd" @changePhase="onChangePhase"
      />
    </div>

    <div v-if="store.status === 'completed'" class="completed-overlay">
      <h3>面试已结束</h3>
      <p v-if="store.evaluateStatus === 'PROCESSING'">评估生成中...</p>
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
  border-bottom: 1px solid var(--color-border, #e5e5e5);

  h2 {
    margin: 0;
    font-size: 18px;
  }
}

.status-tag {
  font-size: 12px;
  padding: 2px 10px;
  border-radius: 10px;

  &.recording {
    background: #e8f5e9;
    color: #2e7d32;
  }

  &.paused {
    background: #fff3e0;
    color: #e65100;
  }

  &.completed {
    background: #e3f2fd;
    color: #1565c0;
  }
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
  background: rgba(255, 255, 255, 0.95);
  z-index: 10;
}
</style>

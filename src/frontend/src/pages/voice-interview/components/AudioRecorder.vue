<script setup lang="ts">
import { ref, onUnmounted, watch } from 'vue'

const props = defineProps<{ disabled: boolean }>()
const emit = defineEmits<{
  (event: 'audioData', data: string): void
  (event: 'volumeChange', volume: number): void
  (event: 'recordingChange', recording: boolean): void
}>()

const isRecording = ref(false)
const analyserData = ref<number[]>(new Array(20).fill(0))
let mediaStream: MediaStream | null = null
let audioContext: AudioContext | null = null
let workletNode: AudioWorkletNode | null = null
let analyserNode: AnalyserNode | null = null
let animFrame: number | null = null

watch(() => props.disabled, (val) => {
  if (val && isRecording.value) stopRecording()
})

async function startRecording() {
  try {
    mediaStream = await navigator.mediaDevices.getUserMedia({
      audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true, sampleRate: 16000 }
    })
    audioContext = new AudioContext({ sampleRate: 16000 })
    await audioContext.audioWorklet.addModule('/audio-worklet/pcm-processor.js')

    const source = audioContext.createMediaStreamSource(mediaStream)
    workletNode = new AudioWorkletNode(audioContext, 'pcm-processor')
    analyserNode = audioContext.createAnalyser()
    analyserNode.fftSize = 64

    const silentGain = audioContext.createGain()
    silentGain.gain.value = 0

    source.connect(analyserNode)
    analyserNode.connect(workletNode)
    workletNode.connect(silentGain)
    silentGain.connect(audioContext.destination)

    workletNode.port.onmessage = (e: MessageEvent) => {
      const buffer = e.data as ArrayBuffer
      const bytes = new Uint8Array(buffer)
      let binary = ''
      for (let i = 0; i < bytes.length; i++) {
        binary += String.fromCharCode(bytes[i])
      }
      emit('audioData', btoa(binary))
    }

    isRecording.value = true
    emit('recordingChange', true)
    updateVolume()
  } catch (err) {
    console.error('Mic access error:', err)
  }
}

function stopRecording() {
  if (!isRecording.value && !workletNode) return
  if (animFrame) cancelAnimationFrame(animFrame)
  animFrame = null

  // Flush remaining audio from worklet buffer before closing
  if (workletNode) {
    workletNode.port.postMessage({ type: 'flush' })
  }

  // Small delay to let the flush message arrive before tearing down
  const ctx = audioContext
  const stream = mediaStream
  const wNode = workletNode
  const aNode = analyserNode
  mediaStream = null; audioContext = null; workletNode = null; analyserNode = null
  isRecording.value = false
  emit('recordingChange', false)
  analyserData.value = new Array(20).fill(0)

  setTimeout(() => {
    wNode?.disconnect()
    aNode?.disconnect()
    ctx?.close()
    stream?.getTracks().forEach(t => t.stop())
  }, 150)
}

function updateVolume() {
  if (!analyserNode || !isRecording.value) return
  const data = new Uint8Array(analyserNode.frequencyBinCount)
  analyserNode.getByteFrequencyData(data)
  const bars = []
  const step = Math.floor(data.length / 20)
  for (let i = 0; i < 20; i++) bars.push(data[i * step] / 255)
  analyserData.value = bars
  emit('volumeChange', Math.max(...bars))
  animFrame = requestAnimationFrame(updateVolume)
}

function toggle() { isRecording.value ? stopRecording() : startRecording() }
onUnmounted(() => stopRecording())
defineExpose({ toggle, isRecording, startRecording, stopRecording })
</script>

<template>
  <div class="audio-recorder">
    <button class="mic-btn" :class="{ active: isRecording, disabled }" @click="toggle" :disabled="disabled">
      <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor">
        <path v-if="!isRecording" d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm-1-9c0-.55.45-1 1-1s1 .45 1 1v6c0 .55-.45 1-1 1s-1-.45-1-1V5zm6 6c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
        <path v-else d="M6 6h12v12H6z"/>
      </svg>
    </button>
    <div class="volume-bars">
      <div v-for="(val, i) in analyserData" :key="i" class="bar" :style="{ height: (val * 100) + '%' }" />
    </div>
  </div>
</template>

<style lang="scss" scoped>
.audio-recorder { display: flex; align-items: center; gap: 12px; }
.mic-btn {
  width: 48px; height: 48px; border-radius: 50%;
  border: 2px solid var(--harmony-brand)); background: transparent;
  color: var(--harmony-brand)); cursor: pointer;
  display: flex; align-items: center; justify-content: center; transition: all 0.2s;
  &.active { background: var(--harmony-brand)); color: white; }
  &.disabled { opacity: 0.5; cursor: not-allowed; }
}
.volume-bars { display: flex; align-items: flex-end; gap: 2px; height: 32px; }
.bar { width: 4px; min-height: 2px; background: var(--harmony-brand)); border-radius: 2px; transition: height 0.1s; }
</style>

<script setup lang="ts">
import { ref, onUnmounted } from 'vue'

const emit = defineEmits<{
  (event: 'playStart'): void
  (event: 'playEnd'): void
}>()

let audioContext: AudioContext | null = null
const playQueue: { source: AudioBufferSourceNode; isLast: boolean }[] = []
const isPlaying = ref(false)
let startedPlaying = false
let fullAudioEl: HTMLAudioElement | null = null

function initContext() {
  if (!audioContext) {
    audioContext = new AudioContext({ sampleRate: 24000 })
  }
  if (audioContext.state === 'suspended') audioContext.resume()
}

function playChunk(base64Wav: string, _index: number, isLast: boolean) {
  initContext()
  if (!audioContext) return

  const raw = atob(base64Wav)
  const bytes = new Uint8Array(raw.length)
  for (let i = 0; i < raw.length; i++) bytes[i] = raw.charCodeAt(i)

  const pcmBytes = bytes.slice(44)
  const samples = pcmBytes.length / 2
  const float32 = new Float32Array(samples)
  const view = new DataView(pcmBytes.buffer, pcmBytes.byteOffset, pcmBytes.byteLength)
  for (let i = 0; i < samples; i++) float32[i] = view.getInt16(i * 2, true) / 32768

  const buffer = audioContext.createBuffer(1, float32.length, 24000)
  buffer.getChannelData(0).set(float32)

  const source = audioContext.createBufferSource()
  source.buffer = buffer
  source.connect(audioContext.destination)
  playQueue.push({ source, isLast })

  if (!isPlaying.value) playNext()
}

function playNext() {
  if (playQueue.length === 0) {
    isPlaying.value = false
    startedPlaying = false
    emit('playEnd')
    return
  }
  isPlaying.value = true
  if (!startedPlaying) emit('playStart')
  startedPlaying = true
  const { source, isLast } = playQueue.shift()!
  source.onended = () => {
    if (isLast) {
      isPlaying.value = false
      startedPlaying = false
      emit('playEnd')
    } else {
      playNext()
    }
  }
  source.start()
}

function playFullAudio(base64Wav: string) {
  stopFullAudio()
  const audio = new Audio(`data:audio/wav;base64,${base64Wav}`)
  fullAudioEl = audio
  isPlaying.value = true
  emit('playStart')
  audio.onended = () => { isPlaying.value = false; emit('playEnd'); fullAudioEl = null }
  audio.play().catch(() => { isPlaying.value = false; fullAudioEl = null })
}

function stopFullAudio() {
  if (fullAudioEl) {
    fullAudioEl.pause()
    fullAudioEl.src = ''
    fullAudioEl = null
  }
}

function stop() {
  playQueue.length = 0
  if (audioContext) { audioContext.close(); audioContext = null }
  stopFullAudio()
  isPlaying.value = false
  startedPlaying = false
}

onUnmounted(() => stop())
defineExpose({ playChunk, playFullAudio, stop, isPlaying })
</script>

<template>
  <div class="audio-player" v-if="isPlaying">
    <div class="playing-indicator"><span class="dot" /><span class="dot" /><span class="dot" /></div>
  </div>
</template>

<style lang="scss" scoped>
.audio-player { display: flex; align-items: center; gap: 8px; }
.playing-indicator { display: flex; gap: 4px; align-items: flex-end; height: 20px; }
.dot {
  width: 4px; height: 4px; border-radius: 50%; background: var(--color-primary);
  animation: bounce 0.6s infinite alternate;
  &:nth-child(2) { animation-delay: 0.2s; }
  &:nth-child(3) { animation-delay: 0.4s; }
}
@keyframes bounce { to { height: 16px; } }
</style>

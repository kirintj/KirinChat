<script setup lang="ts">
defineProps<{
  isRecording: boolean
  isAiSpeaking: boolean
  isProcessing: boolean
  status: string
  currentPhase: string
  phasesEnabled: Record<string, boolean>
}>()

const emit = defineEmits<{
  (event: 'toggleRecord'): void
  (event: 'submit'): void
  (event: 'pause'): void
  (event: 'resume'): void
  (event: 'end'): void
  (event: 'changePhase', phase: string): void
}>()

const phaseLabels: Record<string, string> = { INTRO: '自我介绍', TECH: '技术面试', PROJECT: '项目经验', HR: 'HR面试' }
const nextPhases: Record<string, string> = { INTRO: 'TECH', TECH: 'PROJECT', PROJECT: 'HR' }
</script>

<template>
  <div class="voice-controls">
    <div class="phase-indicator"><span class="phase-label">{{ phaseLabels[currentPhase] || currentPhase }}</span></div>
    <div class="buttons">
      <button class="ctrl-btn record" :class="{ active: isRecording }" @click="emit('toggleRecord')" :disabled="isAiSpeaking || isProcessing">
        {{ isRecording ? '停止录音' : '开始录音' }}
      </button>
      <button class="ctrl-btn submit" @click="emit('submit')" :disabled="isProcessing || isAiSpeaking">提交回答</button>
      <button v-if="status === 'recording'" class="ctrl-btn" @click="emit('pause')">暂停</button>
      <button v-if="status === 'paused'" class="ctrl-btn" @click="emit('resume')">恢复</button>
      <button class="ctrl-btn end" @click="emit('end')">结束面试</button>
    </div>
    <div class="phase-nav" v-if="nextPhases[currentPhase]">
      <button class="phase-btn" @click="emit('changePhase', nextPhases[currentPhase])">
        下一阶段: {{ phaseLabels[nextPhases[currentPhase]] }}
      </button>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.voice-controls { display: flex; flex-direction: column; align-items: center; gap: 12px; padding: 16px; border-top: 1px solid var(--harmony-comp-divider); }
.phase-indicator { font-size: 14px; font-weight: 600; color: var(--harmony-brand)); }
.buttons { display: flex; gap: 10px; flex-wrap: wrap; justify-content: center; }
.ctrl-btn {
  padding: 8px 20px; border-radius: 20px; border: 1px solid var(--harmony-comp-divider); background: white; cursor: pointer; font-size: 13px; transition: all 0.2s;
  &:hover:not(:disabled) { background: var(--harmony-comp-background-secondary); }
  &:disabled { opacity: 0.5; cursor: not-allowed; }
  &.record.active { background: #e74c3c; color: white; border-color: #e74c3c; }
  &.submit { background: var(--harmony-brand)); color: white; border-color: var(--harmony-brand)); }
  &.end { border-color: #e74c3c; color: #e74c3c; }
}
.phase-nav { margin-top: 4px; }
.phase-btn { padding: 6px 16px; border-radius: 16px; border: 1px dashed var(--harmony-brand)); background: transparent; color: var(--harmony-brand)); cursor: pointer; font-size: 12px; }
</style>

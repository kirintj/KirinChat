<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'

interface Message { role: 'user' | 'ai'; text: string }

const props = defineProps<{
  messages: Message[]
  userText: string
  aiText: string
  isAiSpeaking: boolean
  isRecording: boolean
}>()

const scrollContainer = ref<HTMLElement>()

watch(() => [props.messages.length, props.aiText, props.userText], () => {
  nextTick(() => {
    if (scrollContainer.value) scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight
  })
})
</script>

<template>
  <div class="subtitle-panel" ref="scrollContainer">
    <div v-for="(msg, i) in messages" :key="i" class="message" :class="msg.role">
      <div class="bubble">{{ msg.text }}</div>
    </div>
    <div v-if="aiText" class="message ai">
      <div class="bubble streaming">{{ aiText }}<span class="cursor">|</span></div>
    </div>
    <div v-if="userText" class="message user">
      <div class="bubble streaming">{{ userText }}<span class="dots">...</span></div>
    </div>
    <div v-if="isAiSpeaking && !aiText" class="status">AI 播报中...</div>
    <div v-else-if="isRecording && !userText" class="status">正在识别...</div>
  </div>
</template>

<style lang="scss" scoped>
.subtitle-panel { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 12px; }
.message { display: flex; &.ai { justify-content: flex-start; } &.user { justify-content: flex-end; } }
.bubble {
  max-width: 70%; padding: 10px 14px; border-radius: 12px; line-height: 1.5; font-size: 14px;
  .ai & { background: var(--harmony-comp-background-secondary); border-bottom-left-radius: 4px; }
  .user & { background: var(--harmony-brand); color: white; border-bottom-right-radius: 4px; }
}
.cursor { animation: harmony-pulse 0.8s infinite; margin-left: 2px; }

.dots { margin-left: 4px; }
.status { text-align: center; color: var(--harmony-font-secondary); font-size: 12px; }
</style>

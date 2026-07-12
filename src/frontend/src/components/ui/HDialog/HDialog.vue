<script setup lang="ts">
import { ref, toRef, computed } from 'vue'
import { usePopup } from '../shared/usePopup'

type DialogSize = 'sm' | 'md' | 'lg' | 'fullscreen'

interface Props {
  modelValue: boolean
  title?: string
  width?: string
  size?: DialogSize
  closeOnClickModal?: boolean
  alignFooter?: 'left' | 'center' | 'right'
}
const props = withDefaults(defineProps<Props>(), {
  title: '',
  width: '',
  size: 'md',
  closeOnClickModal: true,
  alignFooter: 'right',
})
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'close': []
}>()
function close() {
  emit('update:modelValue', false)
  emit('close')
}

const isFullscreen = computed(() => props.size === 'fullscreen')

const sizeClass = computed(() => `h-dialog--${props.size}`)

const effectiveMaxWidth = computed(() => {
  if (props.width) return props.width
  const map: Record<Exclude<DialogSize, 'fullscreen'>, string> = {
    sm: '400px',
    md: '500px',
    lg: '720px',
  }
  return map[props.size as Exclude<DialogSize, 'fullscreen'>] ?? '500px'
})

const popupRef = ref<HTMLElement | null>(null)
usePopup(toRef(props, 'modelValue'), popupRef, { onClose: close })
</script>

<template>
  <Teleport to="body">
    <Transition name="h-dialog">
      <div
        v-if="modelValue"
        class="h-dialog-overlay"
        :class="{ 'h-dialog-overlay--fullscreen': isFullscreen }"
        @click.self="closeOnClickModal && close()"
      >
        <div
          ref="popupRef"
          class="h-dialog"
          :class="[sizeClass, { 'h-dialog--fullscreen': isFullscreen }]"
          role="dialog"
          aria-modal="true"
          :aria-label="title"
          tabindex="-1"
          :style="isFullscreen ? null : { maxWidth: effectiveMaxWidth }"
        >
          <div class="h-dialog__header">
            <span class="h-dialog__title">{{ title }}</span>
            <span class="h-dialog__close" role="button" aria-label="关闭" @click="close"><Icon icon="mdi:close" :width="18" :height="18" /></span>
          </div>
          <div class="h-dialog__body">
            <slot />
          </div>
          <div v-if="$slots.footer" class="h-dialog__footer" :class="`h-dialog__footer--${alignFooter}`">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.h-dialog-overlay {
  position: fixed; inset: 0;
  background: var(--harmony-overlay-medium);
  display: flex; align-items: center; justify-content: center;
  z-index: var(--z-dialog);
}
.h-dialog-overlay--fullscreen {
  background: var(--harmony-overlay-heavy);
}
.h-dialog {
  width: 100%;
  background: var(--harmony-comp-background-primary);
  backdrop-filter: blur(20px) saturate(1.2);
  border: 1px solid var(--harmony-comp-divider);
  border-radius: var(--harmony-corner-radius-level16);
  box-shadow: var(--harmony-shadow-dialog);
  overflow: hidden;
  outline: none;
  display: flex;
  flex-direction: column;
  max-height: calc(100vh - 64px);
  margin: 0 16px;
}
.h-dialog--fullscreen {
  max-width: none;
  width: 100vw;
  height: 100vh;
  max-height: 100vh;
  margin: 0;
  border-radius: 0;
  border: none;
  box-shadow: none;
}
.h-dialog__header {
  display: flex; justify-content: space-between; align-items: center;
  padding: var(--harmony-padding-level10) var(--harmony-padding-level12) var(--harmony-padding-level6);
  border-bottom: 1px solid var(--harmony-comp-divider);
  flex-shrink: 0;
}
.h-dialog__title { font-size: var(--harmony-font-size-title-s); font-weight: 600; color: var(--harmony-font-primary); }
.h-dialog__close {
  cursor: pointer; color: var(--harmony-font-tertiary); font-size: var(--harmony-font-size-body-m); padding: var(--harmony-padding-level2);
  position: relative; overflow: hidden; border-radius: var(--harmony-corner-radius-level4);
  display: inline-flex; align-items: center; justify-content: center;
}
.h-dialog__close:hover { color: var(--harmony-font-primary); background: var(--harmony-interactive-hover); }
.h-dialog__close:active { background: var(--harmony-interactive-pressed); }
.h-dialog__body {
  padding: var(--harmony-padding-level8) var(--harmony-padding-level12);
  color: var(--harmony-font-secondary);
  overflow-y: auto;
  flex: 1 1 auto;
  min-height: 0;
}
.h-dialog__footer {
  display: flex; gap: var(--harmony-padding-level6);
  padding: var(--harmony-padding-level8) var(--harmony-padding-level12) var(--harmony-padding-level10);
  flex-shrink: 0;
}
.h-dialog__footer--right { justify-content: flex-end; }
.h-dialog__footer--left { justify-content: flex-start; }
.h-dialog__footer--center { justify-content: center; }
.h-dialog-enter-active, .h-dialog-leave-active { transition: opacity var(--harmony-duration-normal) var(--harmony-motion-standard); }
.h-dialog-enter-from, .h-dialog-leave-to { opacity: 0; }
</style>

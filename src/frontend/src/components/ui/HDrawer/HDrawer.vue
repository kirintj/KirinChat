<script setup lang="ts">
import { ref, toRef, computed } from 'vue'
import { usePopup } from '../shared/usePopup'
import { useBreakpoint } from '../../../composables/useBreakpoint'

interface Props {
  modelValue: boolean
  title?: string
  direction?: 'right' | 'left'
  size?: string
  /** Mobile bottom sheet max height (vh). Default 80. */
  mobileMaxHeight?: number
}
const props = withDefaults(defineProps<Props>(), {
  title: '',
  direction: 'right',
  size: '360px',
  mobileMaxHeight: 80,
})
const emit = defineEmits<{ 'update:modelValue': [value: boolean] }>()
const close = () => emit('update:modelValue', false)

const { isMobile } = useBreakpoint()

const sheetStyle = computed(() => ({
  maxHeight: `${props.mobileMaxHeight}vh`,
  transform: dragTransform.value,
}))

const popupRef = ref<HTMLElement | null>(null)
usePopup(toRef(props, 'modelValue'), popupRef, { onClose: close })

// Drag-to-close for mobile bottom sheet
const dragTransform = ref('')
let touchStartY = 0
let touchDelta = 0
let dragging = false

function onTouchStart(e: TouchEvent) {
  if (!isMobile.value) return
  dragging = true
  touchStartY = e.touches[0].clientY
  touchDelta = 0
}
function onTouchMove(e: TouchEvent) {
  if (!dragging) return
  touchDelta = Math.max(0, e.touches[0].clientY - touchStartY)
  dragTransform.value = `translateY(${touchDelta}px)`
}
function onTouchEnd() {
  if (!dragging) return
  dragging = false
  if (touchDelta > 80) {
    close()
  }
  dragTransform.value = ''
  touchDelta = 0
}
</script>

<template>
  <Teleport to="body">
    <!-- Desktop / tablet: side panel -->
    <Transition v-if="!isMobile" name="h-drawer">
      <div v-if="modelValue" class="h-drawer-overlay" @click.self="close">
        <div
          ref="popupRef"
          class="h-drawer"
          :class="[`h-drawer--${direction}`, direction === 'left' ? 'is-left' : '']"
          :style="{ width: size }"
          role="dialog"
          aria-modal="true"
          :aria-label="title"
          tabindex="-1"
        >
          <div class="h-drawer__header">
            <span class="h-drawer__title">{{ title }}</span>
            <span class="h-drawer__close" role="button" aria-label="关闭" @click="close"><Icon icon="mdi:close" :width="18" :height="18" /></span>
          </div>
          <div class="h-drawer__body"><slot /></div>
        </div>
      </div>
    </Transition>

    <!-- Mobile: bottom sheet -->
    <Transition v-else name="h-drawer-sheet">
      <div v-if="modelValue" class="h-drawer-overlay h-drawer-overlay--sheet" @click.self="close">
        <div
          ref="popupRef"
          class="h-drawer-sheet"
          :style="sheetStyle"
          role="dialog"
          aria-modal="true"
          :aria-label="title"
          tabindex="-1"
        >
          <div
            class="h-drawer-sheet__handle"
            @touchstart.passive="onTouchStart"
            @touchmove.passive="onTouchMove"
            @touchend="onTouchEnd"
          >
            <span class="h-drawer-sheet__handle-bar"></span>
          </div>
          <div class="h-drawer-sheet__header">
            <span class="h-drawer-sheet__title">{{ title }}</span>
            <span class="h-drawer-sheet__close" role="button" aria-label="关闭" @click="close"><Icon icon="mdi:close" :width="18" :height="18" /></span>
          </div>
          <div class="h-drawer-sheet__body"><slot /></div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.h-drawer-overlay {
  position: fixed;
  inset: 0;
  background: var(--harmony-overlay-medium);
  z-index: var(--z-dialog);
}

/* ===== Desktop side panel ===== */
.h-drawer {
  position: fixed;
  top: 0;
  bottom: 0;
  background: var(--harmony-comp-background-primary);
  backdrop-filter: blur(20px) saturate(1.2);
  box-shadow: var(--harmony-shadow-dialog);
  display: flex;
  flex-direction: column;
  transition: transform var(--harmony-duration-normal) var(--harmony-motion-standard);
  outline: none;
}

.h-drawer--right {
  right: 0;
  border-radius: var(--harmony-corner-radius-level16) var(--harmony-corner-radius-level16) 0 0;
}

.h-drawer--left {
  left: 0;
  border-radius: 0 var(--harmony-corner-radius-level16) var(--harmony-corner-radius-level16) 0;
}

.h-drawer__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--harmony-comp-divider);
}

.h-drawer__title {
  font-size: var(--harmony-font-size-body-l);
  font-weight: 600;
  color: var(--harmony-font-primary);
}

.h-drawer__close {
  position: relative;
  overflow: hidden;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  cursor: pointer;
  color: var(--harmony-font-tertiary);
  transition: background var(--harmony-duration-fast) var(--harmony-motion-standard);
}

.h-drawer__close:hover {
  color: var(--harmony-font-primary);
  background: var(--harmony-interactive-hover);
}

.h-drawer__close:active {
  background: var(--harmony-interactive-pressed);
}

.h-drawer__body {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

/* Desktop slide transitions */
.h-drawer-enter-active, .h-drawer-leave-active {
  transition: opacity var(--harmony-duration-normal) var(--harmony-motion-standard);
}
.h-drawer-enter-from, .h-drawer-leave-to { opacity: 0; }
.h-drawer-enter-active .h-drawer--right,
.h-drawer-leave-active .h-drawer--right { transition: transform var(--harmony-duration-normal) var(--harmony-motion-standard); }
.h-drawer-enter-from .h-drawer--right,
.h-drawer-leave-to .h-drawer--right { transform: translateX(100%); }
.h-drawer-enter-active .h-drawer--left,
.h-drawer-leave-active .h-drawer--left { transition: transform var(--harmony-duration-normal) var(--harmony-motion-standard); }
.h-drawer-enter-from .h-drawer--left,
.h-drawer-leave-to .h-drawer--left { transform: translateX(-100%); }

/* ===== Mobile bottom sheet ===== */
.h-drawer-overlay--sheet {
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.h-drawer-sheet {
  width: 100%;
  max-height: 80vh;
  background: var(--harmony-comp-background-primary);
  backdrop-filter: blur(20px) saturate(1.2);
  border-radius: var(--harmony-corner-radius-level16) var(--harmony-corner-radius-level16) 0 0;
  box-shadow: var(--harmony-shadow-dialog);
  display: flex;
  flex-direction: column;
  outline: none;
  transition: transform var(--harmony-duration-normal) var(--harmony-motion-standard);
  overflow: hidden;
  padding-bottom: env(safe-area-inset-bottom, 0);
}

.h-drawer-sheet__handle {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px 0 4px;
  touch-action: none;
  cursor: grab;
}
.h-drawer-sheet__handle:active { cursor: grabbing; }
.h-drawer-sheet__handle-bar {
  width: 36px;
  height: 4px;
  border-radius: 2px;
  background: var(--harmony-comp-divider);
}

.h-drawer-sheet__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 20px 12px;
  border-bottom: 1px solid var(--harmony-comp-divider);
}
.h-drawer-sheet__title {
  font-size: var(--harmony-font-size-body-l);
  font-weight: 600;
  color: var(--harmony-font-primary);
}
.h-drawer-sheet__close {
  position: relative;
  overflow: hidden;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  cursor: pointer;
  color: var(--harmony-font-tertiary);
}
.h-drawer-sheet__close:hover {
  color: var(--harmony-font-primary);
  background: var(--harmony-interactive-hover);
}
.h-drawer-sheet__close:active {
  background: var(--harmony-interactive-pressed);
}
.h-drawer-sheet__body {
  flex: 1;
  padding: 16px 20px;
  overflow-y: auto;
  min-height: 0;
}

/* Mobile slide-up transitions */
.h-drawer-sheet-enter-active, .h-drawer-sheet-leave-active {
  transition: opacity var(--harmony-duration-normal) var(--harmony-motion-standard);
}
.h-drawer-sheet-enter-from, .h-drawer-sheet-leave-to { opacity: 0; }
.h-drawer-sheet-enter-active .h-drawer-sheet,
.h-drawer-sheet-leave-active .h-drawer-sheet {
  transition: transform var(--harmony-duration-normal) var(--harmony-motion-standard);
}
.h-drawer-sheet-enter-from .h-drawer-sheet,
.h-drawer-sheet-leave-to .h-drawer-sheet {
  transform: translateY(100%);
}
</style>

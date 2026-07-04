<script setup lang="ts">
interface Props {
  modelValue: boolean
  title?: string
  width?: string
  closeOnClickModal?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  title: '',
  width: '500px',
  closeOnClickModal: true,
})
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'close': []
}>()
function close() {
  emit('update:modelValue', false)
  emit('close')
}
</script>

<template>
  <Teleport to="body">
    <Transition name="h-dialog">
      <div v-if="modelValue" class="h-dialog-overlay" @click.self="closeOnClickModal && close()">
        <div class="h-dialog" :style="{ maxWidth: width }">
          <div class="h-dialog__header">
            <span class="h-dialog__title">{{ title }}</span>
            <span class="h-dialog__close" @click="close">✕</span>
          </div>
          <div class="h-dialog__body">
            <slot />
          </div>
          <div v-if="$slots.footer" class="h-dialog__footer">
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
  background: var(--color-overlay);
  display: flex; align-items: center; justify-content: center;
  z-index: var(--z-dialog);
}
.h-dialog {
  width: 100%;
  background: var(--color-bg-secondary);
  backdrop-filter: blur(20px) saturate(1.2);
  border: 1px solid var(--color-border);
  border-radius: var(--harmony-corner-radius-level16);
  box-shadow: var(--shadow-lg);
  overflow: hidden;
}
.h-dialog__header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 20px 24px 12px;
  border-bottom: 1px solid var(--color-border);
}
.h-dialog__title { font-size: var(--font-size-xl); font-weight: 600; color: var(--color-text-primary); }
.h-dialog__close {
  cursor: pointer; color: var(--color-text-tertiary); font-size: 16px; padding: 4px;
  position: relative; overflow: hidden; border-radius: var(--radius-sm);
}
.h-dialog__close:hover { color: var(--color-text-primary); background: var(--color-bg-hover); }
.h-dialog__close:active { background: var(--color-bg-active); }
.h-dialog__body { padding: 16px 24px; color: var(--color-text-secondary); }
.h-dialog__footer { display: flex; justify-content: flex-end; gap: 12px; padding: 16px 24px 20px; }
.h-dialog-enter-active, .h-dialog-leave-active { transition: opacity var(--duration-normal) var(--easing); }
.h-dialog-enter-from, .h-dialog-leave-to { opacity: 0; }
</style>

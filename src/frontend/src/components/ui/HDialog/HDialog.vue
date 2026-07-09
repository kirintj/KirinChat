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
            <span class="h-dialog__close" @click="close"><Icon icon="mdi:close" :width="18" :height="18" /></span>
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
  background: var(--harmony-overlay-light);
  display: flex; align-items: center; justify-content: center;
  z-index: var(--z-dialog);
}
.h-dialog {
  width: 100%;
  background: var(--harmony-comp-background-primary);
  backdrop-filter: blur(20px) saturate(1.2);
  border: 1px solid var(--harmony-comp-divider);
  border-radius: var(--harmony-corner-radius-level16);
  box-shadow: var(--harmony-shadow-dialog);
  overflow: hidden;
}
.h-dialog__header {
  display: flex; justify-content: space-between; align-items: center;
  padding: var(--harmony-padding-level10) var(--harmony-padding-level12) var(--harmony-padding-level6);
  border-bottom: 1px solid var(--harmony-comp-divider);
}
.h-dialog__title { font-size: var(--harmony-font-size-title-s); font-weight: 600; color: var(--harmony-font-primary); }
.h-dialog__close {
  cursor: pointer; color: var(--harmony-font-tertiary); font-size: var(--harmony-font-size-body-m); padding: var(--harmony-padding-level2);
  position: relative; overflow: hidden; border-radius: var(--harmony-corner-radius-level4);
}
.h-dialog__close:hover { color: var(--harmony-font-primary); background: var(--harmony-interactive-hover); }
.h-dialog__close:active { background: var(--harmony-interactive-pressed); }
.h-dialog__body { padding: var(--harmony-padding-level8) var(--harmony-padding-level12); color: var(--harmony-font-secondary); }
.h-dialog__footer { display: flex; justify-content: flex-end; gap: var(--harmony-padding-level6); padding: var(--harmony-padding-level8) var(--harmony-padding-level12) var(--harmony-padding-level10); }
.h-dialog-enter-active, .h-dialog-leave-active { transition: opacity var(--harmony-duration-normal) var(--harmony-motion-standard); }
.h-dialog-enter-from, .h-dialog-leave-to { opacity: 0; }
</style>

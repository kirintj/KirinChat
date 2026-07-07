<script setup lang="ts">
interface Props { modelValue: boolean; title?: string; direction?: 'right' | 'left'; size?: string }
withDefaults(defineProps<Props>(), { title: '', direction: 'right', size: '360px' })
const emit = defineEmits<{ 'update:modelValue': [value: boolean] }>()
const close = () => emit('update:modelValue', false)
</script>

<template>
  <Teleport to="body">
    <Transition name="h-drawer">
      <div v-if="modelValue" class="h-drawer-overlay" @click.self="close">
        <div
          class="h-drawer"
          :class="[`h-drawer--${direction}`, direction === 'left' ? 'is-left' : '']"
          :style="{ width: size }"
        >
          <div class="h-drawer__header">
            <span class="h-drawer__title">{{ title }}</span>
            <span class="h-drawer__close" @click="close">&#10005;</span>
          </div>
          <div class="h-drawer__body"><slot /></div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.h-drawer-overlay {
  position: fixed;
  inset: 0;
  background: var(--harmony-comp-background-secondary);
  z-index: var(--z-dialog);
}

.h-drawer {
  position: fixed;
  top: 0;
  bottom: 0;
  background: var(--harmony-comp-background-secondary);
  backdrop-filter: blur(20px) saturate(1.2);
  box-shadow: var(--harmony-shadow-dialog);
  display: flex;
  flex-direction: column;
  transition: transform var(--harmony-duration-normal) var(--harmony-motion-standard);
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
</style>

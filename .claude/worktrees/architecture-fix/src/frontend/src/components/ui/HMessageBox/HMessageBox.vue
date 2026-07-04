<script setup lang="ts">
import { ref } from 'vue'
import { onMounted } from 'vue'

interface Props {
  title?: string
  message: string
  confirmButtonText?: string
  cancelButtonText?: string
  type?: 'warning' | 'info' | 'success' | 'error'
  showCancel?: boolean
  onConfirm?: () => void
  onCancel?: () => void
  onClose?: () => void
}

const props = withDefaults(defineProps<Props>(), {
  title: '确认',
  confirmButtonText: '确定',
  cancelButtonText: '取消',
  type: 'warning',
  showCancel: true,
})

const visible = ref(false)

onMounted(() => {
  requestAnimationFrame(() => { visible.value = true })
})

function handleConfirm() {
  visible.value = false
  setTimeout(() => {
    props.onConfirm?.()
    props.onClose?.()
  }, 200)
}

function handleCancel() {
  visible.value = false
  setTimeout(() => {
    props.onCancel?.()
    props.onClose?.()
  }, 200)
}
</script>

<template>
  <div class="h-messagebox-overlay" :class="{ 'h-messagebox--visible': visible }" @click.self="handleCancel">
    <div class="h-messagebox" :class="{ 'h-messagebox--visible': visible }">
      <div class="h-messagebox__header">
        <span class="h-messagebox__title">{{ title }}</span>
        <span class="h-messagebox__close" @click="handleCancel">✕</span>
      </div>
      <div class="h-messagebox__body">
        <p>{{ message }}</p>
      </div>
      <div class="h-messagebox__footer">
        <button v-if="showCancel" class="h-messagebox__btn h-messagebox__btn--cancel" @click="handleCancel">
          {{ cancelButtonText }}
        </button>
        <button class="h-messagebox__btn h-messagebox__btn--confirm" @click="handleConfirm">
          {{ confirmButtonText }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.h-messagebox-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-dialog);
  opacity: 0;
  transition: opacity var(--duration-normal) var(--easing);
}
.h-messagebox--visible { opacity: 1; }
.h-messagebox {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  min-width: 360px;
  max-width: 420px;
  transform: scale(0.95);
  transition: transform var(--duration-normal) var(--easing);
}
.h-messagebox--visible .h-messagebox { transform: scale(1); }
.h-messagebox__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px 12px;
}
.h-messagebox__title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-text-primary);
}
.h-messagebox__close {
  cursor: pointer;
  color: var(--color-text-tertiary);
  font-size: 14px;
}
.h-messagebox__close:hover { color: var(--color-text-primary); }
.h-messagebox__body {
  padding: 12px 24px;
  text-align: center;
  color: var(--color-text-secondary);
  font-size: var(--font-size-base);
  line-height: 1.6;
}
.h-messagebox__footer {
  display: flex;
  justify-content: center;
  gap: 12px;
  padding: 16px 24px 20px;
}
.h-messagebox__btn {
  min-width: 88px;
  height: 36px;
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--font-size-base);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--duration-fast) var(--easing);
  font-family: var(--font-family);
}
.h-messagebox__btn--cancel {
  background: var(--color-bg-tertiary);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
}
.h-messagebox__btn--cancel:hover {
  border-color: var(--color-border-hover);
  color: var(--color-text-primary);
}
.h-messagebox__btn--confirm {
  background: var(--color-primary);
  color: #fff;
}
.h-messagebox__btn--confirm:hover {
  background: var(--color-primary-hover);
}
</style>

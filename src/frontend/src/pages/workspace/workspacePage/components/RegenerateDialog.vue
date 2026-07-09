<script setup lang="ts">
import { Icon } from '@iconify/vue'

interface Props {
  visible: boolean
  modelValue: string
  isMobile?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isMobile: false
})

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'update:modelValue', value: string): void
  (e: 'confirm'): void
  (e: 'cancel'): void
}>()

const close = () => {
  emit('update:visible', false)
  emit('cancel')
}

const handleInput = (event: Event) => {
  const target = event.target as HTMLTextAreaElement
  emit('update:modelValue', target.value)
}

const handleConfirm = () => {
  emit('confirm')
}
</script>

<template>
  <div
    v-if="visible"
    class="feedback-modal-overlay"
    :class="{ 'is-mobile': isMobile }"
    @click.self="close"
  >
    <div
      class="feedback-modal"
      :class="{ 'feedback-modal--mobile': isMobile }"
      @click.stop
    >
      <div class="modal-header">
        <h3 class="modal-title">重新生成指导手册</h3>
        <button class="close-btn" type="button" aria-label="关闭" @click="close">
          <Icon icon="mdi:close" :width="18" :height="18" />
        </button>
      </div>

      <div class="modal-body">
        <p class="feedback-tip">请告诉我您希望如何优化这个指导手册：</p>
        <div class="input-wrapper">
          <textarea
            :value="modelValue"
            placeholder="例如：更加详细一些、更简洁、调整某个步骤等..."
            maxlength="500"
            class="feedback-textarea"
            rows="4"
            @input="handleInput"
          />
          <div class="char-count">{{ modelValue.length }}/500</div>
        </div>
      </div>

      <div class="modal-footer">
        <button class="cancel-btn" type="button" @click="close">
          取消
        </button>
        <button class="confirm-btn" type="button" @click="handleConfirm">
          确认重新生成
        </button>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@use '@/styles/breakpoints.scss' as *;

.feedback-modal-overlay {
  position: fixed;
  inset: 0;
  background: var(--harmony-overlay-heavy);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-dialog);
  animation: dialog-fade-in 0.2s ease;

  &.is-mobile {
    align-items: flex-end;
  }
}

.feedback-modal {
  background: var(--harmony-comp-background-primary);
  border-radius: var(--harmony-corner-radius-level7);
  box-shadow: var(--harmony-shadow-dialog);
  width: 420px;
  max-width: 90vw;
  animation: dialog-slide-up 0.2s ease;
  overflow: hidden;

  &--mobile {
    width: 100%;
    max-width: 100%;
    border-radius: var(--harmony-corner-radius-level8) var(--harmony-corner-radius-level8) 0 0;
    max-height: 85vh;
    display: flex;
    flex-direction: column;
  }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--harmony-padding-level8) var(--harmony-padding-level10);
  border-bottom: 1px solid var(--harmony-comp-divider);
  background: var(--harmony-comp-background-primary);

  .modal-title {
    margin: 0;
    font-size: var(--harmony-font-size-body-m);
    font-weight: 700;
    color: var(--harmony-font-primary);
  }

  .close-btn {
    width: 28px;
    height: 28px;
    border: none;
    background: var(--harmony-comp-background-secondary);
    border-radius: var(--harmony-corner-radius-level3);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    color: var(--harmony-font-secondary);
    transition: background 0.15s ease;

    &:hover {
      background: var(--harmony-comp-divider);
      color: var(--harmony-font-primary);
    }
  }
}

.modal-body {
  padding: var(--harmony-padding-level10);

  .feedback-tip {
    margin: 0 0 var(--harmony-padding-level7);
    font-size: var(--harmony-font-size-subtitle-s);
    color: var(--harmony-font-secondary);
    line-height: 1.6;
  }

  .input-wrapper {
    position: relative;

    .feedback-textarea {
      width: 100%;
      min-height: 100px;
      padding: var(--harmony-padding-level6) var(--harmony-padding-level7);
      padding-bottom: var(--harmony-padding-level10);
      border: 1px solid var(--harmony-comp-divider);
      border-radius: var(--harmony-corner-radius-level6);
      font-family: var(--harmony-font-family);
      font-size: var(--harmony-font-size-subtitle-s);
      line-height: 1.6;
      color: var(--harmony-font-primary);
      background: var(--harmony-comp-background-primary);
      resize: none;
      box-sizing: border-box;

      &:focus {
        border-color: var(--harmony-brand);
        outline: none;
      }

      &::placeholder {
        color: var(--harmony-font-tertiary);
      }
    }

    .char-count {
      position: absolute;
      bottom: var(--harmony-padding-level3);
      right: var(--harmony-padding-level5);
      font-size: var(--harmony-font-size-body-s);
      color: var(--harmony-font-tertiary);
      pointer-events: none;
    }
  }
}

.modal-footer {
  display: flex;
  gap: var(--harmony-padding-level5);
  justify-content: flex-end;
  padding: var(--harmony-padding-level8) var(--harmony-padding-level10);
  border-top: 1px solid var(--harmony-comp-divider);
  background: var(--harmony-comp-background-primary);

  button {
    padding: var(--harmony-padding-level5) var(--harmony-padding-level8);
    border: none;
    border-radius: var(--harmony-corner-radius-level4);
    font-size: var(--harmony-font-size-subtitle-s);
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .cancel-btn {
    background: var(--harmony-comp-background-primary);
    color: var(--harmony-font-secondary);
    border: 1px solid var(--harmony-comp-divider);

    &:hover {
      background: var(--harmony-comp-background-secondary);
    }
  }

  .confirm-btn {
    background: var(--harmony-brand);
    color: var(--harmony-comp-background-primary);

    &:hover {
      background: var(--harmony-interactive-hover);
    }
  }
}

@include mobile {
  .feedback-modal--mobile {
    .modal-header,
    .modal-body,
    .modal-footer {
      padding: var(--harmony-padding-level6);
    }

    .close-btn,
    .cancel-btn,
    .confirm-btn {
      min-height: var(--harmony-control-height-56);
      min-width: var(--harmony-control-height-56);
    }

    .modal-footer {
      gap: var(--harmony-padding-level4);

      .cancel-btn,
      .confirm-btn {
        flex: 1;
      }
    }
  }
}

@keyframes dialog-fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes dialog-slide-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>

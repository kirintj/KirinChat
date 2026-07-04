<!-- src/frontend/src/components/ui/HInput/HInput.vue -->
<script setup lang="ts">
import { ref, computed } from 'vue'

interface Props {
  modelValue?: string
  type?: string
  placeholder?: string
  disabled?: boolean
  clearable?: boolean
  showPassword?: boolean
  size?: 'small' | 'medium' | 'large'
  error?: string
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  type: 'text',
  placeholder: '',
  disabled: false,
  clearable: false,
  showPassword: false,
  size: 'medium',
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
  'focus': [event: FocusEvent]
  'blur': [event: FocusEvent]
  'clear': []
  'keyup': [event: KeyboardEvent]
}>()

const focused = ref(false)
const passwordVisible = ref(false)

const inputType = computed(() => {
  if (props.showPassword) return passwordVisible.value ? 'text' : 'password'
  return props.type
})

const hasValue = computed(() => props.modelValue.length > 0)

function onInput(event: Event) {
  const target = event.target as HTMLInputElement
  emit('update:modelValue', target.value)
}

function onClear() {
  emit('update:modelValue', '')
  emit('clear')
}

function togglePassword() {
  passwordVisible.value = !passwordVisible.value
}
</script>

<template>
  <div
    class="h-input"
    :class="[
      `h-input--${size}`,
      {
        'h-input--focused': focused,
        'h-input--disabled': disabled,
        'h-input--error': error,
      }
    ]"
  >
    <div v-if="$slots.prefix" class="h-input__prefix">
      <slot name="prefix" />
    </div>
    <input
      class="h-input__inner"
      :type="inputType"
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      @input="onInput"
      @focus="focused = true; $emit('focus', $event)"
      @blur="focused = false; $emit('blur', $event)"
      @keyup="$emit('keyup', $event)"
    />
    <div class="h-input__suffix">
      <span v-if="clearable && hasValue" class="h-input__clear" @click="onClear">✕</span>
      <span v-if="showPassword" class="h-input__toggle" @click="togglePassword">
        {{ passwordVisible ? '🙈' : '👁' }}
      </span>
      <slot name="suffix" />
    </div>
    <div v-if="error" class="h-input__error">{{ error }}</div>
  </div>
</template>

<style scoped>
.h-input {
  position: relative;
  display: flex;
  align-items: center;
  background: var(--color-bg-tertiary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  transition: all var(--duration-fast) var(--easing);
}
.h-input:hover:not(.h-input--disabled) {
  border-color: var(--color-border-hover);
}
.h-input--focused {
  border-color: var(--color-border-focus);
  box-shadow: 0 0 0 3px var(--color-primary-bg);
}
.h-input--error {
  border-color: var(--color-error);
}
.h-input--disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Sizes */
.h-input--small { height: 32px; padding: 0 10px; }
.h-input--medium { height: 38px; padding: 0 12px; }
.h-input--large { height: 44px; padding: 0 16px; }

.h-input__inner {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  color: var(--color-text-primary);
  font-size: var(--font-size-base);
  font-family: var(--font-family);
  min-width: 0;
}
.h-input__inner::placeholder {
  color: var(--color-text-tertiary);
}
.h-input__inner:disabled {
  cursor: not-allowed;
}

.h-input__prefix,
.h-input__suffix {
  display: flex;
  align-items: center;
  gap: 4px;
  color: var(--color-text-tertiary);
}
.h-input__clear,
.h-input__toggle {
  cursor: pointer;
  font-size: 12px;
  padding: 2px;
}
.h-input__clear:hover {
  color: var(--color-text-primary);
}

.h-input__error {
  position: absolute;
  bottom: -20px;
  left: 0;
  font-size: var(--font-size-xs);
  color: var(--color-error);
}
</style>

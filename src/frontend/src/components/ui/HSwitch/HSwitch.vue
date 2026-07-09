<script setup lang="ts">
interface Props {
  modelValue?: boolean
  disabled?: boolean
}

defineProps<Props>()
const emit = defineEmits<{ 'update:modelValue': [value: boolean] }>()
</script>

<template>
  <button
    class="h-switch"
    :class="{
      'h-switch--on': modelValue,
      'h-switch--disabled': disabled,
    }"
    :disabled="disabled"
    @click="emit('update:modelValue', !modelValue)"
    role="switch"
    :aria-checked="modelValue"
  >
    <span class="h-switch__thumb" />
  </button>
</template>

<style scoped>
.h-switch {
  position: relative;
  width: 36px;
  height: 20px;
  border-radius: var(--harmony-corner-radius-level6);
  border: none;
  background: var(--harmony-interactive-pressed);
  cursor: pointer;
  padding: 0;
  transition: background var(--harmony-duration-normal) var(--harmony-motion-standard);
}

.h-switch--on {
  background: var(--harmony-brand);
}

.h-switch--disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.h-switch__thumb {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: white;
  box-shadow: var(--harmony-shadow-xs);
  transition: transform var(--harmony-duration-normal) var(--harmony-motion-standard);
}

.h-switch--on .h-switch__thumb {
  transform: translateX(16px);
}
</style>

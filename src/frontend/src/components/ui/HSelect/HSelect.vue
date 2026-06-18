<script setup lang="ts">
import { ref, provide, computed, onMounted, onUnmounted } from 'vue'

interface Props {
  modelValue: string | number | undefined
  placeholder?: string
  disabled?: boolean
  clearable?: boolean
  filterable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: '请选择',
  disabled: false,
  clearable: false,
  filterable: false,
})

const emit = defineEmits<{
  'update:modelValue': [value: string | number | undefined]
  'change': [value: string | number | undefined]
}>()

const open = ref(false)
const dropdownRef = ref<HTMLElement | null>(null)

provide('h-select', {
  modelValue: computed(() => props.modelValue),
  select: (value: string | number) => {
    emit('update:modelValue', value)
    emit('change', value)
    open.value = false
  },
})

function clear() {
  emit('update:modelValue', undefined)
  emit('change', undefined)
}

function toggle() {
  if (!props.disabled) open.value = !open.value
}

function onClickOutside(e: MouseEvent) {
  const target = e.target as HTMLElement
  if (!target.closest('.h-select')) {
    open.value = false
  }
}

onMounted(() => document.addEventListener('click', onClickOutside))
onUnmounted(() => document.removeEventListener('click', onClickOutside))
</script>

<template>
  <div class="h-select" :class="{ 'h-select--open': open, 'h-select--disabled': disabled }">
    <div class="h-select__trigger" @click="toggle">
      <slot name="trigger">
        <div class="h-select__value">
          <slot name="selected" :value="modelValue">
            <span v-if="modelValue !== undefined && modelValue !== ''">{{ modelValue }}</span>
            <span v-else class="h-select__placeholder">{{ placeholder }}</span>
          </slot>
        </div>
      </slot>
      <span class="h-select__arrow">&#9662;</span>
      <span v-if="clearable && modelValue" class="h-select__clear" @click.stop="clear">&#10005;</span>
    </div>
    <div v-show="open" class="h-select__dropdown" ref="dropdownRef">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.h-select { position: relative; display: inline-block; min-width: 180px; }
.h-select__trigger {
  display: flex; align-items: center; gap: 8px;
  height: 38px; padding: 0 12px;
  background: var(--color-bg-tertiary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--duration-fast) var(--easing);
}
.h-select--open .h-select__trigger { border-color: var(--color-border-focus); }
.h-select--disabled .h-select__trigger { opacity: 0.5; cursor: not-allowed; }
.h-select__value { flex: 1; font-size: var(--font-size-base); color: var(--color-text-primary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.h-select__placeholder { color: var(--color-text-tertiary); }
.h-select__arrow, .h-select__clear { color: var(--color-text-tertiary); font-size: 12px; }
.h-select__clear:hover { color: var(--color-text-primary); }
.h-select__dropdown {
  position: absolute; top: calc(100% + 4px); left: 0; right: 0;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  z-index: var(--z-dropdown);
  max-height: 240px; overflow-y: auto; padding: 4px;
}
</style>

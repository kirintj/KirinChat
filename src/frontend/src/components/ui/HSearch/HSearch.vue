<script setup lang="ts">
import { ref, computed } from 'vue'
import { HIcon } from '@/components/ui'

interface Props {
  modelValue?: string
  placeholder?: string
  disabled?: boolean
  clearable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  placeholder: '搜索',
  disabled: false,
  clearable: true,
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
  search: [value: string]
  clear: []
}>()

const focused = ref(false)
const inputValue = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v),
})

const onClear = () => {
  emit('update:modelValue', '')
  emit('clear')
}

const onKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Enter') emit('search', inputValue.value)
}
</script>

<template>
  <div
    class="h-search"
    :class="{
      'h-search--focused': focused,
      'h-search--disabled': disabled,
    }"
  >
    <HIcon name="Search" :size="16" class="h-search__icon" />
    <input
      v-model="inputValue"
      class="h-search__input"
      :placeholder="placeholder"
      :disabled="disabled"
      @focus="focused = true"
      @blur="focused = false"
      @keydown="onKeydown"
    />
    <button
      v-if="clearable && inputValue"
      class="h-search__clear"
      @click="onClear"
    >
      <HIcon name="Close" :size="14" />
    </button>
  </div>
</template>

<style scoped>
.h-search {
  display: flex;
  align-items: center;
  height: var(--harmony-control-height-40);
  padding: 0 var(--harmony-padding-level4);
  gap: var(--harmony-padding-level2);
  border-radius: var(--harmony-corner-radius-level10);
  background: var(--harmony-comp-background-secondary);
  border: 1px solid var(--harmony-comp-divider);
  transition: border-color var(--harmony-duration-fast) var(--harmony-motion-standard),
              box-shadow var(--harmony-duration-fast) var(--harmony-motion-standard);
  width: 100%;
  box-sizing: border-box;
}

.h-search--focused {
  border-color: var(--harmony-brand);
  box-shadow: 0 0 0 2px var(--harmony-comp-emphasize-tertiary);
}

.h-search--disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.h-search__icon {
  color: var(--harmony-font-tertiary);
  flex-shrink: 0;
}

.h-search--focused .h-search__icon {
  color: var(--harmony-brand);
}

.h-search__input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-size: var(--harmony-font-size-body-m);
  color: var(--harmony-font-primary);
  min-width: 0;
}

.h-search__input::placeholder {
  color: var(--harmony-font-fourth);
}

.h-search__clear {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border: none;
  background: var(--harmony-comp-divider);
  border-radius: 50%;
  cursor: pointer;
  color: var(--harmony-font-secondary);
  flex-shrink: 0;
  transition: background var(--harmony-duration-fast) var(--harmony-motion-standard);
}

.h-search__clear:hover {
  background: var(--harmony-interactive-hover);
}
</style>

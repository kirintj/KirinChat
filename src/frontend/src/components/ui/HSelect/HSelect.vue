<script setup lang="ts">
import { ref, reactive, provide, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { Icon } from '@iconify/vue'

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
const selectRef = ref<HTMLElement | null>(null)
const dropdownRef = ref<HTMLElement | null>(null)
const filterText = ref('')

const labelMap = ref<Record<string, string>>({})

const selectedLabel = computed(() => {
  if (props.modelValue === undefined || props.modelValue === '') return ''
  const key = String(props.modelValue)
  return labelMap.value[key] || String(props.modelValue)
})

provide('h-select', {
  modelValue: computed(() => props.modelValue),
  registerOption: (value: string | number, label: string) => {
    labelMap.value[String(value)] = label
  },
  unregisterOption: (value: string | number) => {
    delete labelMap.value[String(value)]
  },
  select: (value: string | number) => {
    emit('update:modelValue', value)
    emit('change', value)
    open.value = false
  },
  filterText: computed(() => filterText.value),
})

const dropdownStyle = reactive({
  position: 'fixed' as const,
  top: '0px',
  left: '0px',
  width: '0px',
})

function updateDropdownPosition() {
  if (!selectRef.value) return
  const rect = selectRef.value.getBoundingClientRect()
  dropdownStyle.top = `${rect.bottom + 4}px`
  dropdownStyle.left = `${rect.left}px`
  dropdownStyle.width = `${rect.width}px`
}

function clear() {
  emit('update:modelValue', undefined)
  emit('change', undefined)
}

function toggle() {
  if (!props.disabled) {
    open.value = !open.value
    filterText.value = ''
    if (open.value) {
      nextTick(() => updateDropdownPosition())
    }
  }
}

function onClickOutside(e: MouseEvent) {
  const target = e.target as HTMLElement
  if (!target.closest('.h-select') && !target.closest('.h-select__dropdown-teleported')) {
    open.value = false
  }
}

function onScroll() {
  if (open.value) updateDropdownPosition()
}

onMounted(() => {
  document.addEventListener('click', onClickOutside, true)
  window.addEventListener('scroll', onScroll, true)
  window.addEventListener('resize', onScroll)
})
onUnmounted(() => {
  document.removeEventListener('click', onClickOutside, true)
  window.removeEventListener('scroll', onScroll, true)
  window.removeEventListener('resize', onScroll)
})

watch(open, (val) => {
  if (val) {
    nextTick(() => updateDropdownPosition())
  }
})
</script>

<template>
  <div class="h-select" :class="{ 'h-select--open': open, 'h-select--disabled': disabled }" ref="selectRef">
    <div class="h-select__trigger" @click="toggle">
      <span class="h-select__overlay"></span>
      <slot name="trigger">
        <div class="h-select__value">
          <slot name="selected" :value="modelValue" :label="selectedLabel">
            <span v-if="modelValue !== undefined && modelValue !== ''">{{ selectedLabel }}</span>
            <span v-else class="h-select__placeholder">{{ placeholder }}</span>
          </slot>
        </div>
      </slot>
      <span class="h-select__arrow"><Icon icon="mdi:chevron-down" :width="14" :height="14" /></span>
      <span v-if="clearable && modelValue" class="h-select__clear" @click.stop="clear"><Icon icon="mdi:close" :width="14" :height="14" /></span>
    </div>
    <Teleport to="body">
      <div v-show="open" class="h-select__dropdown-teleported" ref="dropdownRef" :style="dropdownStyle">
        <div v-if="filterable" class="h-select__filter">
          <input
            v-model="filterText"
            class="h-select__filter-input"
            placeholder="搜索..."
            @click.stop
          />
        </div>
        <div class="h-select__dropdown-list">
          <slot />
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.h-select { position: relative; display: inline-block; min-width: 180px; }
.h-select__trigger {
  position: relative;
  display: flex; align-items: center; gap: 8px;
  height: 38px; padding: 0 12px;
  overflow: hidden;
  border: 1px solid var(--harmony-comp-divider);
  border-radius: var(--harmony-corner-radius-level10);
  cursor: pointer;
  transition: all var(--harmony-duration-fast) var(--harmony-motion-standard);
}
.h-select__overlay {
  position: absolute; inset: 0;
  pointer-events: none;
  opacity: 0;
  transition: opacity var(--harmony-duration-fast) var(--harmony-motion-standard);
}
.h-select__trigger:hover .h-select__overlay {
  opacity: 1;
  background: var(--harmony-interactive-hover);
}
.h-select__trigger:active .h-select__overlay {
  opacity: 1;
  background: var(--harmony-interactive-pressed);
}
.h-select--open .h-select__trigger {
  border-color: var(--harmony-interactive-focus);
  outline: 2px solid var(--harmony-interactive-focus);
  outline-offset: -1px;
}
.h-select--disabled .h-select__trigger { opacity: 0.5; cursor: not-allowed; }
.h-select__value {
  position: relative; z-index: 1;
  flex: 1; font-size: var(--harmony-font-size-body-m);
  color: var(--harmony-font-primary);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.h-select__placeholder { color: var(--harmony-font-tertiary); }
.h-select__arrow, .h-select__clear {
  position: relative; z-index: 1;
  color: var(--harmony-font-tertiary); font-size: var(--harmony-font-size-body-s);
}
.h-select__clear:hover { color: var(--harmony-font-primary); }
</style>

<style>
.h-select__dropdown-teleported {
  position: fixed;
  border: 1px solid var(--harmony-comp-divider);
  border-radius: var(--harmony-corner-radius-level8);
  box-shadow: var(--harmony-shadow-dialog);
  z-index: var(--z-dialog);
  background: var(--harmony-comp-background-primary);
  max-height: 280px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
.h-select__dropdown-teleported .h-select__filter {
  padding: 8px 8px 4px;
  flex-shrink: 0;
}
.h-select__dropdown-teleported .h-select__filter-input {
  width: 100%;
  height: 30px;
  padding: 0 8px;
  border: 1px solid var(--harmony-comp-divider);
  border-radius: var(--harmony-corner-radius-level6);
  font-size: var(--harmony-font-size-body-s);
  color: var(--harmony-font-primary);
  background: var(--harmony-comp-background-secondary);
  outline: none;
  box-sizing: border-box;
}
.h-select__dropdown-teleported .h-select__filter-input:focus {
  border-color: var(--harmony-interactive-focus);
}
.h-select__dropdown-teleported .h-select__dropdown-list {
  overflow-y: auto;
  padding: 4px;
  max-height: 240px;
}
</style>

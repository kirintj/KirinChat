<script setup lang="ts">
import { Icon } from '@iconify/vue'

interface Props {
  modelValue: string
  readOnly?: boolean
  placeholder?: string
}

const props = withDefaults(defineProps<Props>(), {
  readOnly: false,
  placeholder: '正在生成指导手册...'
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

const handleInput = (event: Event) => {
  const target = event.target as HTMLTextAreaElement
  emit('update:modelValue', target.value)
}
</script>

<template>
  <div class="guide-editor">
    <div class="editor-pane">
      <div class="pane-header">
        <span class="header-icon">
          <Icon icon="mdi:pencil-outline" :width="16" :height="16" />
        </span>
        <span class="header-title">原始文本</span>
      </div>
      <textarea
        :value="modelValue"
        :readonly="readOnly"
        :placeholder="placeholder"
        class="markdown-editor"
        @input="handleInput"
      />
    </div>
  </div>
</template>

<style lang="scss" scoped>
@use '@/styles/breakpoints.scss' as *;

.guide-editor {
  width: 100%;
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.editor-pane {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--harmony-comp-background-primary);
  border-radius: var(--harmony-corner-radius-level7);
  border: 1px solid var(--harmony-comp-divider);

  &:focus-within {
    border-color: var(--harmony-brand);
  }
}

.pane-header {
  display: flex;
  align-items: center;
  gap: var(--harmony-padding-level3);
  padding: var(--harmony-padding-level5) var(--harmony-padding-level7);
  background: var(--harmony-comp-background-secondary);
  border-bottom: 1px solid var(--harmony-comp-divider);
  font-size: var(--harmony-font-size-body-s);
  font-weight: 600;
  color: var(--harmony-font-secondary);

  .header-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--harmony-font-tertiary);
  }
}

.markdown-editor {
  flex: 1;
  width: 100%;
  min-height: 0;
  border: none;
  resize: none;
  padding: var(--harmony-padding-level7);
  font-family: var(--harmony-font-family);
  font-size: var(--harmony-font-size-subtitle-s);
  line-height: 1.6;
  color: var(--harmony-font-primary);
  background: var(--harmony-comp-background-primary);

  &::placeholder {
    color: var(--harmony-font-tertiary);
  }

  &:read-only {
    background: var(--harmony-comp-background-secondary);
    cursor: default;
  }

  &:focus {
    outline: none;
  }
}

@include mobile {
  .pane-header {
    padding: var(--harmony-padding-level4) var(--harmony-padding-level6);
  }

  .markdown-editor {
    padding: var(--harmony-padding-level6);
  }
}
</style>

<script setup lang="ts">
import { Icon } from '@iconify/vue'

interface Props {
  html: string
}

defineProps<Props>()
</script>

<template>
  <div class="guide-preview">
    <div class="pane-header">
      <span class="header-icon">
        <Icon icon="mdi:eye-outline" :width="16" :height="16" />
      </span>
      <span class="header-title">预览</span>
    </div>
    <div class="markdown-preview" v-html="html" />
  </div>
</template>

<style lang="scss" scoped>
@use '@/styles/breakpoints.scss' as *;

.guide-preview {
  width: 100%;
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--harmony-comp-background-secondary);
  border-radius: var(--harmony-corner-radius-level7);
  border: 1px solid var(--harmony-comp-divider);
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

.markdown-preview {
  flex: 1;
  overflow-y: auto;
  padding: var(--harmony-padding-level7) var(--harmony-padding-level10);

  :deep(h1), :deep(h2), :deep(h3), :deep(h4), :deep(h5), :deep(h6) {
    margin-top: var(--harmony-padding-level3);
    margin-bottom: 0;
    font-weight: 600;
    line-height: 1.2;
    color: var(--harmony-font-primary);
  }

  :deep(h1) {
    font-size: 1.8em;
    border-bottom: 1px solid var(--harmony-comp-divider);
    padding-bottom: 1px;
  }

  :deep(h2) {
    font-size: 1.5em;
    border-bottom: 1px solid var(--harmony-comp-divider);
    padding-bottom: 1px;
  }

  :deep(h3) { font-size: 1.25em; }
  :deep(h4) { font-size: 1.1em; }
  :deep(h5) { font-size: 1em; }
  :deep(h6) {
    font-size: 0.9em;
    color: var(--harmony-font-secondary);
  }

  :deep(p) {
    margin-top: 0;
    margin-bottom: var(--harmony-padding-level1);
    line-height: 1.5;
    color: var(--harmony-font-primary);
  }

  :deep(ul), :deep(ol) {
    padding-left: 1.8em;
    margin-top: var(--harmony-padding-level1);
    margin-bottom: var(--harmony-padding-level1);

    li {
      margin-bottom: 0;
      line-height: 1.4;
      color: var(--harmony-font-primary);
    }
  }

  :deep(ul.list-level-1) { list-style-type: disc; margin-left: 0; }
  :deep(ul.list-level-2) { list-style-type: circle; margin-left: 1.5em; }
  :deep(ul.list-level-3) { list-style-type: square; margin-left: 3em; }

  :deep(code) {
    background: var(--harmony-comp-background-secondary);
    padding: var(--harmony-padding-level1) var(--harmony-padding-level3);
    border-radius: var(--harmony-corner-radius-level2);
    font-family: var(--harmony-font-family);
    font-size: 0.9em;
    color: var(--harmony-warning);
  }

  :deep(pre) {
    background: var(--harmony-font-primary);
    color: var(--harmony-comp-background-primary);
    padding: var(--harmony-padding-level5);
    border-radius: var(--harmony-corner-radius-level3);
    overflow-x: auto;
    margin-top: var(--harmony-padding-level1);
    margin-bottom: var(--harmony-padding-level2);

    code {
      background: none;
      color: inherit;
      padding: 0;
      line-height: 1.4;
    }
  }

  :deep(blockquote) {
    border-left: 4px solid var(--harmony-brand);
    padding-left: var(--harmony-padding-level6);
    margin: var(--harmony-padding-level1) 0;
    color: var(--harmony-font-secondary);
    font-style: italic;
    line-height: 1.4;
  }

  :deep(table) {
    border-collapse: collapse;
    width: 100%;
    margin-top: var(--harmony-padding-level1);
    margin-bottom: var(--harmony-padding-level2);

    th, td {
      border: 1px solid var(--harmony-comp-divider);
      padding: var(--harmony-padding-level3) var(--harmony-padding-level5);
      text-align: left;
      line-height: 1.4;
    }

    th {
      background: var(--harmony-comp-background-secondary);
      font-weight: 600;
    }
  }

  :deep(a) {
    color: var(--harmony-brand);
    text-decoration: none;

    &:hover {
      text-decoration: underline;
    }
  }

  :deep(hr) {
    border: none;
    border-top: 1px solid var(--harmony-comp-divider);
    margin: var(--harmony-padding-level3) 0;
  }

  :deep(.placeholder) {
    color: var(--harmony-font-tertiary);
    font-style: italic;
  }
}

@include mobile {
  .pane-header {
    padding: var(--harmony-padding-level4) var(--harmony-padding-level6);
  }

  .markdown-preview {
    padding: var(--harmony-padding-level6);
  }
}
</style>

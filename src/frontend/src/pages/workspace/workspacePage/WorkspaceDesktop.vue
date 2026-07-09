<script setup lang="ts">
import { Icon } from '@iconify/vue'
import { useWorkspaceGuide } from './composables/useWorkspaceGuide'
import GuideEditor from './components/GuideEditor.vue'
import GuidePreview from './components/GuidePreview.vue'
import HistoryList from './components/HistoryList.vue'
import RegenerateDialog from './components/RegenerateDialog.vue'

const {
  historyContexts,
  showHistory,
  isExistingSession,
  expandedItems,
  guidePrompt,
  isStreaming,
  isEditable,
  renderedMarkdown,
  showFeedbackDialog,
  feedbackText,
  toggleExpand,
  handleRegenerate,
  handleCancelRegenerate,
  handleConfirmRegenerate,
  handleStartTask
} = useWorkspaceGuide()
</script>

<template>
  <div class="workspace-chat-page">
    <div class="chat-container">
      <HistoryList
        v-if="showHistory"
        :contexts="historyContexts"
        :expandedItems="expandedItems"
        @toggle="toggleExpand"
      />

      <template v-if="!isExistingSession">
        <div class="editor-section">
          <div class="editor-header">
            <div class="header-left">
              <span class="editor-icon">
                <Icon icon="mdi:file-document" :width="18" :height="18" />
              </span>
              <span class="editor-title">麒麟智聊指导手册</span>
            </div>
            <div class="header-right">
              <span v-if="isStreaming" class="streaming-indicator">
                <span class="loading-dot"></span>
                <span class="loading-text">生成中...</span>
              </span>
              <span v-else-if="isEditable" class="editable-indicator">
                <span class="edit-icon">
                  <Icon icon="mdi:pencil" :width="16" :height="16" />
                </span>
                <span class="edit-text">可编辑</span>
              </span>
            </div>
          </div>

          <div class="editor-wrapper">
            <div class="editor-content">
              <GuideEditor
                v-model="guidePrompt"
                :readOnly="!isEditable"
              />
              <GuidePreview :html="renderedMarkdown" />
            </div>
          </div>
        </div>

        <div class="action-section">
          <div class="action-buttons">
            <button
              class="action-btn regenerate-btn"
              :disabled="isStreaming"
              @click="handleRegenerate"
            >
              <span class="btn-icon">
                <Icon icon="mdi:refresh" :width="16" :height="16" />
              </span>
              <span class="btn-text">重新生成</span>
            </button>

            <button
              class="action-btn start-btn"
              :disabled="isStreaming || !guidePrompt.trim()"
              @click="handleStartTask"
            >
              <span class="btn-icon">
                <Icon icon="mdi:play" :width="16" :height="16" />
              </span>
              <span class="btn-text">开始执行</span>
            </button>
          </div>
        </div>
      </template>
    </div>

    <RegenerateDialog
      v-model:visible="showFeedbackDialog"
      v-model:modelValue="feedbackText"
      @confirm="handleConfirmRegenerate"
      @cancel="handleCancelRegenerate"
    />
  </div>
</template>

<style lang="scss" scoped>
@use '@/styles/breakpoints.scss' as *;

/* =============================
   WorkspaceDesktop — 指导手册编辑器（桌面端）
   ============================= */

.workspace-chat-page {
  width: 100%;
  height: 100%;
  background: var(--harmony-comp-background-secondary);
  padding: 0;
  overflow: hidden;
}

.chat-container {
  max-width: 1400px;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: 0;
}

/* 编辑器区域 */
.editor-section {
  flex: 1;
  display: flex;
  flex-direction: column;

  .editor-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
    padding: 0 4px;

    .header-left {
      display: flex;
      align-items: center;
      gap: 10px;

      .editor-icon {
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--harmony-brand);
        color: var(--harmony-comp-background-primary);
        border-radius: var(--harmony-corner-radius-level4);

        svg {
          width: 18px;
          height: 18px;
        }
      }

      .editor-title {
        font-size: var(--harmony-font-size-body-m);
        font-weight: 600;
        color: var(--harmony-font-primary);
      }
    }

    .header-right {
      display: flex;
      align-items: center;
      gap: 10px;

      .streaming-indicator {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 5px 12px;
        background: var(--harmony-comp-emphasize-tertiary);
        border-radius: var(--harmony-corner-radius-level18);
        border: 1px solid var(--harmony-brand);

        .loading-dot {
          width: 7px;
          height: 7px;
          background: var(--harmony-brand);
          border-radius: 50%;
          animation: harmony-pulse 1.5s ease-in-out infinite;
        }

        .loading-text {
          font-size: var(--harmony-font-size-body-s);
          color: var(--harmony-brand);
          font-weight: 500;
        }
      }

      .editable-indicator {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 5px 12px;
        background: var(--harmony-confirm-bg);
        border-radius: var(--harmony-corner-radius-level18);
        border: 1px solid var(--harmony-confirm);

        .edit-icon {
          display: flex;
          color: var(--harmony-confirm);
        }

        .edit-text {
          font-size: var(--harmony-font-size-body-s);
          color: var(--harmony-confirm);
          font-weight: 500;
        }
      }
    }
  }

  .editor-wrapper {
    flex: 1;
    background: var(--harmony-comp-background-primary);
    border: 1px solid var(--harmony-comp-divider);
    border-radius: var(--harmony-corner-radius-level7);
    overflow: hidden;
    transition: border-color 0.2s ease;

    &:focus-within {
      border-color: var(--harmony-brand);
    }

    :deep(.editor-pane),
    :deep(.guide-preview) {
      border: none;
      border-radius: 0;
    }

    :deep(.guide-editor .editor-pane) {
      border-right: 1px solid var(--harmony-comp-divider);
    }
  }

  .editor-content {
    height: 100%;
    display: flex;

    > * {
      flex: 1;
      min-width: 0;
    }
  }
}

/* 操作按钮区域 */
.action-section {
  .action-buttons {
    display: flex;
    gap: 12px;
    justify-content: flex-end;

    .action-btn {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 12px 24px;
      border: none;
      border-radius: var(--harmony-corner-radius-level5);
      font-size: var(--harmony-font-size-subtitle-s);
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s ease;

      .btn-icon svg {
        width: 16px;
        height: 16px;
      }

      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
    }

    .regenerate-btn {
      background: var(--harmony-comp-background-primary);
      color: var(--harmony-font-secondary);
      border: 1px solid var(--harmony-comp-divider);

      &:not(:disabled):hover {
        background: var(--harmony-comp-background-secondary);
        border-color: var(--harmony-comp-divider);
      }
    }

    .start-btn {
      background: var(--harmony-brand);
      color: var(--harmony-comp-background-primary);

      &:not(:disabled):hover {
        background: var(--harmony-interactive-hover);
      }
    }
  }
}
</style>

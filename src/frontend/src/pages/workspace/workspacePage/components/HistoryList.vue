<script setup lang="ts">
import { Icon } from '@iconify/vue'
import { MdPreview } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import type { HistoryContext } from '../composables/useWorkspaceGuide'

interface Props {
  contexts: HistoryContext[]
  expandedItems: Set<number>
}

defineProps<Props>()

const emit = defineEmits<{
  (e: 'toggle', index: number): void
}>()

const handleToggle = (index: number) => {
  emit('toggle', index)
}
</script>

<template>
  <div class="history-list">
    <div class="history-section-fullscreen">
      <div class="history-header">
        <div class="header-left">
          <span class="history-icon">
            <Icon icon="mdi:message-text" :width="20" :height="20" />
          </span>
          <h2 class="history-title">对话历史</h2>
        </div>
        <div class="header-right">
          <span class="history-count">共 {{ contexts.length }} 条对话</span>
        </div>
      </div>

      <div class="history-content">
        <div
          v-for="(context, index) in contexts"
          :key="index"
          class="conversation-item"
          :class="{ expanded: expandedItems.has(index) }"
        >
          <div
            class="conversation-header"
            role="button"
            tabindex="0"
            @click="handleToggle(index)"
            @keydown.enter.space.prevent="handleToggle(index)"
          >
            <div class="header-info">
              <span class="conversation-number">#{{ index + 1 }}</span>
              <span class="conversation-preview">
                {{ context.query.substring(0, 100) }}{{ context.query.length > 100 ? '...' : '' }}
              </span>
            </div>
            <div
              class="expand-icon"
              :class="{ expanded: expandedItems.has(index) }"
              aria-hidden="true"
            >
              <Icon icon="mdi:chevron-right" :width="12" :height="12" />
            </div>
          </div>

          <div v-show="expandedItems.has(index)" class="conversation-content">
            <div class="message-block user-block">
              <div class="message-header">
                <span class="message-icon">
                  <Icon icon="mdi:account" :width="16" :height="16" />
                </span>
                <span class="message-title">用户提问</span>
              </div>
              <div class="message-body">
                <MdPreview :editorId="`user-query-${index}`" :modelValue="context.query" />
              </div>
            </div>

            <div class="message-block ai-block">
              <div class="message-header">
                <span class="message-icon">
                  <Icon icon="mdi:robot" :width="16" :height="16" />
                </span>
                <span class="message-title">AI回答</span>
              </div>
              <div class="message-body">
                <MdPreview :editorId="`ai-answer-${index}`" :modelValue="context.answer" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@use '@/styles/breakpoints.scss' as *;

.history-list {
  width: 100%;
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.history-section-fullscreen {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--harmony-comp-background-primary);
  border: 1px solid var(--harmony-comp-divider);
  border-radius: var(--harmony-corner-radius-level7);
  overflow: hidden;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--harmony-padding-level8) var(--harmony-padding-level10);
  background: var(--harmony-comp-background-primary);
  border-bottom: 1px solid var(--harmony-comp-divider);

  .header-left {
    display: flex;
    align-items: center;
    gap: var(--harmony-padding-level5);

    .history-icon {
      width: var(--harmony-control-height-36);
      height: var(--harmony-control-height-36);
      display: flex;
      align-items: center;
      justify-content: center;
      background: var(--harmony-brand);
      color: var(--harmony-comp-background-primary);
      border-radius: var(--harmony-corner-radius-level5);

      svg {
        width: 20px;
        height: 20px;
      }
    }

    .history-title {
      margin: 0;
      font-size: var(--harmony-font-size-body-m);
      font-weight: 700;
      color: var(--harmony-font-primary);
    }
  }

  .header-right {
    .history-count {
      font-size: var(--harmony-font-size-body-s);
      color: var(--harmony-font-secondary);
      background: var(--harmony-comp-background-secondary);
      padding: var(--harmony-padding-level3) var(--harmony-padding-level7);
      border-radius: var(--harmony-corner-radius-level18);
      border: 1px solid var(--harmony-comp-divider);
    }
  }
}

.history-content {
  flex: 1;
  overflow-y: auto;
  padding: var(--harmony-padding-level8);
  background: var(--harmony-comp-background-secondary);

  .conversation-item {
    background: var(--harmony-comp-background-primary);
    border: 1px solid var(--harmony-comp-divider);
    border-radius: var(--harmony-corner-radius-level8);
    margin-bottom: var(--harmony-padding-level6);
    overflow: hidden;
    transition: box-shadow 0.2s ease;

    &:hover {
      box-shadow: var(--harmony-shadow-card);
    }

    &:last-child {
      margin-bottom: 0;
    }

    .conversation-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: var(--harmony-padding-level6) var(--harmony-padding-level8);
      background: var(--harmony-comp-background-primary);
      cursor: pointer;
      border-bottom: 1px solid var(--harmony-comp-divider);

      &:hover {
        background: var(--harmony-comp-background-secondary);
      }

      .header-info {
        display: flex;
        align-items: center;
        gap: var(--harmony-padding-level5);
        flex: 1;
        min-width: 0;

        .conversation-number {
          font-size: var(--harmony-font-size-body-s);
          font-weight: 700;
          color: var(--harmony-brand);
          background: var(--harmony-comp-emphasize-tertiary);
          padding: var(--harmony-padding-level1) var(--harmony-padding-level5);
          border-radius: var(--harmony-corner-radius-level18);
          flex-shrink: 0;
        }

        .conversation-preview {
          font-size: var(--harmony-font-size-subtitle-s);
          color: var(--harmony-font-primary);
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
      }

      .expand-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--harmony-font-tertiary);
        margin-left: var(--harmony-padding-level5);
        transition: transform 0.2s ease;

        &.expanded {
          transform: rotate(90deg);
        }
      }
    }

    .conversation-content {
      padding: var(--harmony-padding-level8);
      background: var(--harmony-comp-background-primary);

      .message-block {
        margin-bottom: var(--harmony-padding-level8);

        &:last-child {
          margin-bottom: 0;
        }

        .message-header {
          display: flex;
          align-items: center;
          gap: var(--harmony-padding-level4);
          margin-bottom: var(--harmony-padding-level5);
          padding-bottom: var(--harmony-padding-level4);
          border-bottom: 1px solid var(--harmony-comp-divider);

          .message-icon {
            width: 28px;
            height: 28px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            color: var(--harmony-font-primary);

            svg {
              width: 16px;
              height: 16px;
            }
          }

          .message-title {
            font-size: var(--harmony-font-size-body-s);
            font-weight: 600;
            color: var(--harmony-font-secondary);
          }
        }

        .message-body {
          background: var(--harmony-comp-background-secondary);
          border-radius: var(--harmony-corner-radius-level6);
          padding: var(--harmony-padding-level7);
          border: 1px solid var(--harmony-comp-divider);

          :deep(.md-editor-preview) {
            background: transparent;
            padding: 0;

            p {
              margin: var(--harmony-padding-level4) 0;
              line-height: 1.8;
              color: var(--harmony-font-primary);
            }

            h1, h2, h3, h4, h5, h6 {
              margin: var(--harmony-padding-level8) 0 var(--harmony-padding-level4);
              font-weight: 600;
              color: var(--harmony-font-primary);
            }

            ul, ol {
              margin: var(--harmony-padding-level5) 0;
              padding-left: var(--harmony-padding-level12);

              li {
                margin: var(--harmony-padding-level2) 0;
                line-height: 1.6;
                color: var(--harmony-font-primary);
              }
            }

            code {
              background: var(--harmony-comp-background-secondary);
              padding: var(--harmony-padding-level1) var(--harmony-padding-level3);
              border-radius: var(--harmony-corner-radius-level2);
              font-family: var(--harmony-font-family);
              font-size: 0.9em;
              color: var(--harmony-warning);
            }

            pre {
              background: var(--harmony-font-primary);
              color: var(--harmony-comp-background-primary);
              padding: var(--harmony-padding-level7);
              border-radius: var(--harmony-corner-radius-level4);
              overflow-x: auto;
              margin: var(--harmony-padding-level5) 0;

              code {
                background: none;
                color: inherit;
                padding: 0;
              }
            }

            blockquote {
              border-left: 4px solid var(--harmony-brand);
              padding-left: var(--harmony-padding-level7);
              margin: var(--harmony-padding-level5) 0;
              color: var(--harmony-font-secondary);
              font-style: italic;
            }

            table {
              border-collapse: collapse;
              width: 100%;
              margin: var(--harmony-padding-level5) 0;

              th, td {
                border: 1px solid var(--harmony-comp-divider);
                padding: var(--harmony-padding-level4) var(--harmony-padding-level6);
                text-align: left;
              }

              th {
                background: var(--harmony-comp-background-secondary);
                font-weight: 600;
              }
            }
          }
        }

        &.user-block {
          .message-header .message-icon {
            background: var(--harmony-comp-emphasize-tertiary);
          }
          .message-body {
            border-left: 3px solid var(--harmony-brand);
          }
        }

        &.ai-block {
          .message-header .message-icon {
            background: var(--harmony-confirm-bg);
          }
          .message-body {
            border-left: 3px solid var(--harmony-confirm);
          }
        }
      }
    }
  }
}

@include mobile {
  .history-header {
    padding: var(--harmony-padding-level6);
  }

  .history-content {
    padding: var(--harmony-padding-level6);

    .conversation-item {
      .conversation-header {
        min-height: var(--harmony-control-height-56);
        padding: var(--harmony-padding-level5) var(--harmony-padding-level6);

        .expand-icon {
          min-width: var(--harmony-control-height-56);
          min-height: var(--harmony-control-height-56);
          margin-right: calc(-1 * var(--harmony-padding-level4));
        }
      }

      .conversation-content {
        padding: var(--harmony-padding-level6);
      }
    }
  }
}
</style>

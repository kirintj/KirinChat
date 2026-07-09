<script setup lang="ts">
import { ref } from 'vue'
import { Icon } from '@iconify/vue'
import { useWorkspaceGuide } from './composables/useWorkspaceGuide'
import GuideEditor from './components/GuideEditor.vue'
import GuidePreview from './components/GuidePreview.vue'
import HistoryList from './components/HistoryList.vue'
import RegenerateDialog from './components/RegenerateDialog.vue'

const workspace = useWorkspaceGuide()

type TabKey = 'edit' | 'preview'
const activeTab = ref<TabKey>(workspace.guidePrompt ? 'preview' : 'edit')
const bodyRef = ref<HTMLElement | null>(null)
const isScrolled = ref(false)

const setTab = (tab: TabKey) => {
  activeTab.value = tab
}

const onScroll = () => {
  isScrolled.value = (bodyRef.value?.scrollTop ?? 0) > 10
}
</script>

<template>
  <div class="workspace-mobile">
    <!-- 顶部标题栏 -->
    <header class="mobile-header" :class="{ 'is-scrolled': isScrolled }">
      <div class="header-title">
        <span class="title-icon">
          <Icon icon="mdi:file-document" :width="20" :height="20" />
        </span>
        <h1 class="title-text">麒麟智聊指导手册</h1>
      </div>
      <div class="header-status">
        <span v-if="workspace.isStreaming" class="status-badge status-badge--streaming">
          <span class="status-dot" />
          <span class="status-text">生成中...</span>
        </span>
        <span v-else-if="workspace.isEditable" class="status-badge status-badge--editable">
          <Icon icon="mdi:pencil" :width="14" :height="14" />
          <span class="status-text">可编辑</span>
        </span>
      </div>
    </header>

    <main ref="bodyRef" class="mobile-body" @scroll="onScroll">
      <!-- 历史记录 -->
      <section v-if="workspace.showHistory" class="history-section">
        <HistoryList
          :contexts="workspace.historyContexts"
          :expanded-items="workspace.expandedItems"
          @toggle="workspace.toggleExpand"
        />
      </section>

      <!-- 编辑 / 预览 -->
      <template v-if="!workspace.isExistingSession">
        <nav class="tab-bar" aria-label="编辑与预览切换">
          <button
            type="button"
            class="tab-button"
            :class="{ active: activeTab === 'edit' }"
            aria-pressed="activeTab === 'edit'"
            @click="setTab('edit')"
          >
            <Icon icon="mdi:pencil-outline" :width="18" :height="18" />
            <span>编辑</span>
          </button>
          <button
            type="button"
            class="tab-button"
            :class="{ active: activeTab === 'preview' }"
            aria-pressed="activeTab === 'preview'"
            @click="setTab('preview')"
          >
            <Icon icon="mdi:eye-outline" :width="18" :height="18" />
            <span>预览</span>
          </button>
        </nav>

        <section class="tab-content">
          <div v-show="activeTab === 'edit'" class="tab-panel">
            <GuideEditor
              v-model="workspace.guidePrompt"
              :read-only="!workspace.isEditable"
              placeholder="正在生成指导手册..."
            />
          </div>
          <div v-show="activeTab === 'preview'" class="tab-panel">
            <GuidePreview :html="workspace.renderedMarkdown" />
          </div>
        </section>
      </template>
    </main>

    <!-- 底部固定操作栏 -->
    <footer v-if="!workspace.isExistingSession" class="action-bar">
      <button
        type="button"
        class="action-btn action-btn--secondary"
        :disabled="workspace.isStreaming"
        @click="workspace.handleRegenerate"
      >
        <Icon icon="mdi:refresh" :width="18" :height="18" />
        <span>重新生成</span>
      </button>
      <button
        type="button"
        class="action-btn action-btn--primary"
        :disabled="workspace.isStreaming || !workspace.guidePrompt.trim()"
        @click="workspace.handleStartTask"
      >
        <Icon icon="mdi:play" :width="18" :height="18" />
        <span>开始执行</span>
      </button>
    </footer>

    <!-- 重新生成弹窗（移动端底部抽屉） -->
    <RegenerateDialog
      v-model:visible="workspace.showFeedbackDialog"
      v-model:modelValue="workspace.feedbackText"
      :is-mobile="true"
      @confirm="workspace.handleConfirmRegenerate"
      @cancel="workspace.handleCancelRegenerate"
    />
  </div>
</template>

<style lang="scss" scoped>
@use '@/styles/breakpoints.scss' as *;

.workspace-mobile {
  width: 100%;
  max-width: var(--harmony-page-content-width-mobile);
  min-height: 100%;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  background: var(--harmony-comp-background-secondary);
  color: var(--harmony-font-primary);
}

.mobile-header {
  position: sticky;
  top: 0;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--harmony-padding-level4);
  min-height: 40px;
  padding: var(--harmony-padding-level3) 0;
  background: transparent;
  transition: background 0.2s ease, backdrop-filter 0.2s ease;

  &.is-scrolled {
    background: var(--harmony-comp-background-primary);
    backdrop-filter: blur(12px) saturate(1.2);
    -webkit-backdrop-filter: blur(12px) saturate(1.2);
  }
}

.header-title {
  display: flex;
  align-items: center;
  gap: var(--harmony-padding-level3);
  min-width: 0;

  .title-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    flex-shrink: 0;
    background: var(--harmony-brand);
    color: var(--harmony-comp-background-primary);
    border-radius: var(--harmony-corner-radius-level4);
  }

  .title-text {
    margin: 0;
    font-size: var(--harmony-font-size-body-m);
    font-weight: 700;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}

.header-status {
  flex-shrink: 0;

  .status-badge {
    display: inline-flex;
    align-items: center;
    gap: var(--harmony-padding-level2);
    padding: var(--harmony-padding-level2) var(--harmony-padding-level5);
    border-radius: var(--harmony-corner-radius-level18);
    font-size: var(--harmony-font-size-body-s);
    font-weight: 500;
  }

  .status-badge--streaming {
    background: var(--harmony-comp-emphasize-tertiary);
    border: 1px solid var(--harmony-brand);
    color: var(--harmony-brand);

    .status-dot {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: var(--harmony-brand);
      animation: harmony-pulse 1.5s ease-in-out infinite;
    }
  }

  .status-badge--editable {
    background: var(--harmony-confirm-bg);
    border: 1px solid var(--harmony-confirm);
    color: var(--harmony-confirm);
  }
}

.mobile-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  padding: var(--harmony-page-padding-mobile) 0;
  padding-bottom: calc(var(--harmony-control-height-56) + var(--harmony-page-padding-mobile) * 2 + env(safe-area-inset-bottom, 0px));
  gap: var(--harmony-section-gap-mobile);
  overflow-y: auto;
}

.history-section {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.tab-bar {
  display: flex;
  gap: var(--harmony-padding-level2);
  padding: var(--harmony-padding-level2);
  background: var(--harmony-comp-background-primary);
  border: 1px solid var(--harmony-comp-divider);
  border-radius: var(--harmony-corner-radius-level7);
}

.tab-button {
  flex: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--harmony-padding-level2);
  min-height: 48px;
  padding: var(--harmony-padding-level3) var(--harmony-padding-level5);
  border: none;
  border-radius: var(--harmony-corner-radius-level5);
  background: transparent;
  color: var(--harmony-font-secondary);
  font-size: var(--harmony-font-size-subtitle-s);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;

  &.active {
    background: var(--harmony-brand);
    color: var(--harmony-comp-background-primary);
  }

  &:active:not(:disabled) {
    opacity: 0.9;
  }
}

.tab-content {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.tab-panel {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.action-bar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 20;
  display: flex;
  gap: var(--harmony-padding-level4);
  padding: var(--harmony-page-padding-mobile) 0;
  padding-bottom: calc(var(--harmony-page-padding-mobile) + env(safe-area-inset-bottom, 0px));
  background: var(--harmony-comp-background-primary);
  border-top: 1px solid var(--harmony-comp-divider);
  box-shadow: var(--harmony-shadow-card);

  .action-btn {
    flex: 1 1 0;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: var(--harmony-padding-level2);
    min-height: var(--harmony-control-height-56);
    min-width: 140px;
    padding: var(--harmony-padding-level3) var(--harmony-padding-level6);
    border: none;
    border-radius: var(--harmony-corner-radius-level5);
    font-size: var(--harmony-font-size-subtitle-s);
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s ease;

    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  }

  .action-btn--secondary {
    background: var(--harmony-comp-background-primary);
    color: var(--harmony-font-secondary);
    border: 1px solid var(--harmony-comp-divider);

    &:not(:disabled):active {
      background: var(--harmony-comp-background-secondary);
    }
  }

  .action-btn--primary {
    background: var(--harmony-brand);
    color: var(--harmony-comp-background-primary);

    &:not(:disabled):active {
      background: var(--harmony-interactive-hover);
    }
  }
}

@include mobile {
  .action-bar {
    flex-wrap: wrap;

    .action-btn {
      flex: 1 1 calc(50% - var(--harmony-padding-level2));
    }
  }
}

@keyframes harmony-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}
</style>

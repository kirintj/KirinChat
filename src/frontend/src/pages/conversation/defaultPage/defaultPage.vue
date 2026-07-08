<script setup lang="ts">
import { ref, onMounted } from "vue"
import { getDialogListAPI } from "../../../apis/history"

const shouldShow = ref(false)

onMounted(async () => {
  try {
    const response = await getDialogListAPI()
    if (response.data.status_code === 200 && response.data.data && response.data.data.length > 0) {
      return
    }
  } catch (_) {
    // ignore
  }
  shouldShow.value = true
})
</script>

<template>
  <!-- 对话列表为空时，右侧展示空白 -->
  <div v-if="shouldShow"></div>
  <!-- 如果有会话记录，不显示任何内容，等待跳转 -->
</template>

<style lang="scss" scoped>
@use '../../../styles/breakpoints.scss' as *;

.default-page {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 24px;
  background: linear-gradient(135deg, var(--harmony-brand) 0%, #764ba2 100%);
  min-height: 100vh;

  .header-section {
    text-align: center;
    margin-bottom: 40px;

    .welcome-content {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 20px;

      .welcome-icon {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 50%;
        padding: 20px;
        backdrop-filter: blur(10px);
      }

      .welcome-text {
        .title {
          font-size: 2.5rem;
          font-weight: 700;
          color: white;
          margin: 0 0 12px 0;
          text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);

          .highlight {
            color: var(--harmony-alert);
            text-shadow: 0 2px 4px rgba(251, 191, 36, 0.3);
          }
        }

        .subtitle {
          font-size: 1.1rem;
          color: rgba(255, 255, 255, 0.9);
          margin: 0;
          font-weight: 400;
        }
      }
    }
  }

  .search-section {
    margin-bottom: 40px;

    .search-container {
      max-width: 600px;
      margin: 0 auto;

      .search-input {
        :deep(.el-input__wrapper) {
          border-radius: var(--harmony-corner-radius-level6);
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
          background: rgba(255, 255, 255, 0.95);
          backdrop-filter: blur(10px);
          
          &:hover {
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
          }
          
          &.is-focus {
            box-shadow: 0 0 0 2px var(--harmony-brand);
          }
        }

        :deep(.el-input-group__append) {
          .el-button {
            border-radius: 0 12px 12px 0;
            border: none;
            background: var(--harmony-brand);

            &:hover {
              background: var(--harmony-interactive-hover);
            }
          }
        }
      }
    }
  }

  .agents-section {
    flex: 1;
    background: rgba(255, 255, 255, 0.95);
    border-radius: var(--harmony-corner-radius-level10);
    padding: 32px;
    backdrop-filter: blur(10px);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);

    .section-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;

      .header-left {
        display: flex;
        align-items: center;
        gap: 8px;

        .section-title {
          font-size: 1.5rem;
          font-weight: 600;
          color: var(--harmony-font-primary);
          margin: 0;
        }

        .agent-count {
          font-size: 0.9rem;
          color: var(--harmony-font-secondary);
          background: var(--harmony-comp-background-secondary);
          padding: 4px 8px;
          border-radius: var(--harmony-corner-radius-level6);
        }
      }
    }

    .loading-state {
      padding: 40px 0;
    }

    .empty-state {
      text-align: center;
      padding: 60px 20px;
      color: var(--harmony-font-secondary);

      .empty-icon {
        font-size: 4rem;
        margin-bottom: 16px;
      }

      .empty-title {
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 8px;
        color: var(--harmony-font-primary);
      }

      .empty-description {
        font-size: 0.9rem;
        margin-bottom: 24px;
      }
    }

    .agents-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 24px;

      .agent-item {
        .agent-card {
          transition: all 0.3s ease;
          border-radius: var(--harmony-corner-radius-level8);
          overflow: hidden;
          box-shadow: var(--harmony-shadow-card);

          &:hover {
            transform: translateY(-4px);
            box-shadow: var(--harmony-shadow-card-hover);
          }
        }
      }
    }
  }
}

// 响应式设计
@include mobile {
  .default-page {
    padding: 16px;

    .header-section {
      .welcome-content {
        .welcome-text {
          .title {
            font-size: 2rem;
          }

          .subtitle {
            font-size: 1rem;
          }
        }
      }
    }

    .agents-section {
      padding: 20px;

      .section-header {
        flex-direction: column;
        gap: 16px;
        align-items: flex-start;
      }

      .agents-grid {
        grid-template-columns: 1fr;
        gap: 16px;
      }
    }
  }
}

@include mobile {
  .default-page {
    .header-section {
      .welcome-content {
        .welcome-text {
          .title {
            font-size: 1.5rem;
          }
        }
      }
    }
  }
}
</style>

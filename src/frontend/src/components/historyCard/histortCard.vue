/**
 * 历史会话卡片组件
 * 展示会话的基本信息、时间显示和操作按钮
 */
<script setup lang="ts">
import { computed } from "vue"
import { HistoryListType } from "../../type"

interface Props {
  item: HistoryListType
}

interface Emits {
  (e: 'delete'): void
  (e: 'select'): void
}

const props = defineProps<Props>()
const emits = defineEmits<Emits>()

// 时间常量（毫秒）
const MILLISECONDS = {
  SECOND: 1000,
  MINUTE: 1000 * 60,
  HOUR: 1000 * 60 * 60,
  DAY: 1000 * 60 * 60 * 24,
  WEEK: 1000 * 60 * 60 * 24 * 7
} as const

/**
 * 格式化时间显示
 * - 1小时内显示"刚刚"
 * - 24小时内显示"X小时前"
 * - 7天内显示"X天前"
 * - 超过7天显示具体日期
 */
const formattedTime = computed(() => {
  try {
    const date = new Date(props.item.createTime)
    const now = new Date()
    const diffInMs = now.getTime() - date.getTime()
    const diffInHours = diffInMs / MILLISECONDS.HOUR

    if (diffInHours < 1) {
      return '刚刚'
    } else if (diffInHours < 24) {
      return `${Math.floor(diffInHours)}小时前`
    } else if (diffInHours < 7) {
      const diffInDays = Math.floor(diffInMs / MILLISECONDS.DAY)
      return `${diffInDays}天前`
    } else {
      return date.toLocaleDateString('zh-CN', {
        month: 'short',
        day: 'numeric'
      })
    }
  } catch (error) {
    return '未知时间'
  }
})

/**
 * 删除卡片（阻止事件冒泡）
 */
const deleteCard = (event: Event) => {
  event.stopPropagation()
  emits('delete')
}

/**
 * 选择会话
 */
const selectCard = () => {
  emits('select')
}
</script>

<template>
  <div class="history-card" @click="selectCard">
    <!-- 卡片主体 -->
    <div class="card-main">
      <!-- 左侧图标和标题 -->
      <div class="card-left">
        <div class="avatar">
          <img :src="item.logo || '/default-avatar.png'" :alt="item.name || '会话'" />
        </div>
        <div class="content">
          <div class="title" :title="item.name">
            {{ item.name || '未命名会话' }}
          </div>
          <div class="subtitle">
            {{ item.agent || '智能助手' }}
          </div>
        </div>
      </div>

      <!-- 右侧操作区域 -->
      <div class="card-right">
        <div class="time">{{ formattedTime }}</div>
        <div class="actions">
          <button class="delete-btn" @click="deleteCard" title="删除会话">
            ×
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@use '../../styles/breakpoints.scss' as *;

/* 样式变量 */
$card-padding: 16px;
$border-radius-lg: 12px;
$border-radius-md: 8px;
$spacing-sm: 8px;
$spacing-md: 12px;
$transition-default: all 0.3s ease;

.history-card {
  position: relative;
  background-color: var(--harmony-comp-background-primary);
  border: 1px solid var(--harmony-comp-divider);
  border-radius: $border-radius-lg;
  padding: $card-padding;
  cursor: pointer;
  transition: $transition-default;
  margin-bottom: $spacing-sm;

  &:hover {
    border-color: var(--harmony-brand);
    box-shadow: var(--harmony-shadow-md);
    transform: translateY(-2px);
  }

  .card-main {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: $spacing-md;

    .card-left {
      display: flex;
      align-items: center;
      gap: $spacing-md;
      flex: 1;
      min-width: 0;

      .avatar {
        flex-shrink: 0;
        width: 40px;
        height: 40px;
        border-radius: $border-radius-md;
        overflow: hidden;
        background-color: var(--harmony-comp-background-tertiary);
        display: flex;
        align-items: center;
        justify-content: center;

        img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }
      }

      .content {
        flex: 1;
        min-width: 0;

        .title {
          font-size: var(--harmony-font-size-body-m);
          font-weight: 600;
          color: var(--harmony-font-primary);
          margin-bottom: 4px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .subtitle {
          font-size: var(--harmony-font-size-body-s);
          color: var(--harmony-font-secondary);
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
      }
    }

    .card-right {
      display: flex;
      flex-direction: column;
      align-items: flex-end;
      gap: $spacing-sm;
      flex-shrink: 0;

      .time {
        font-size: var(--harmony-font-size-caption-l);
        color: var(--harmony-font-tertiary);
        white-space: nowrap;
      }

      .actions {
        opacity: 1;
        transition: opacity 0.2s ease;

        .delete-btn {
          color: var(--harmony-font-tertiary);
          font-size: var(--harmony-font-size-subtitle-l);
          font-weight: bold;
          cursor: pointer;
          width: 20px;
          height: 20px;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: transform 0.2s;
          background: none;
          border: none;
          padding: 0;
          border-radius: var(--harmony-corner-radius-level2);

          &:hover {
            transform: scale(1.2);
            color: var(--harmony-warning);
            background-color: var(--harmony-warning-bg);
          }
        }
      }
    }
  }
}

/* 激活状态 */
.history-card.active {
  border-color: var(--harmony-brand);
  background-color: var(--harmony-comp-emphasize-tertiary);
  box-shadow: 0 0 0 1px var(--harmony-brand);

  .card-left .content .title {
    color: var(--harmony-brand);
  }
}

/* 响应式设计 */
@include mobile {
  .history-card {
    padding: 12px;

    .card-main {
      .card-left {
        gap: $spacing-sm;

        .avatar {
          width: 32px;
          height: 32px;
        }

        .content {
          .title {
            font-size: var(--harmony-font-size-subtitle-s);
          }

          .subtitle {
            font-size: var(--harmony-font-size-caption-l);
          }
        }
      }

      .card-right .time {
        font-size: var(--harmony-font-size-caption-m);
      }
    }
  }
}
</style>

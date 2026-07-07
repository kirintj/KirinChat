<script lang="ts" setup>
/**
 * 智能体卡片组件
 * 展示智能体的基本信息、统计数据和操作按钮
 */
import { computed } from "vue"
import { HMessage } from '@/components/ui'
import { Agent } from "../../type"
import { deleteAgentAPI } from '../../apis/agent'
import { showDeleteConfirm } from '../../utils/dialog'

interface Props {
  item: Agent
}

interface Emits {
  (e: 'delete'): void
  (e: 'edit', agent: Agent): void
}

const props = defineProps<Props>()
const emits = defineEmits<Emits>()

// 统计项配置
const stats = computed(() => [
  {
    icon: '🔧',
    label: '工具',
    count: props.item.tool_ids?.length || 0,
    title: `工具数量: ${props.item.tool_ids?.length || 0}`
  },
  {
    icon: '📚',
    label: '知识库',
    count: props.item.knowledge_ids?.length || 0,
    title: `知识库数量: ${props.item.knowledge_ids?.length || 0}`
  },
  {
    icon: '🤖',
    label: 'MCP',
    count: props.item.mcp_ids?.length || 0,
    title: `MCP数量: ${props.item.mcp_ids?.length || 0}`
  }
])

/**
 * 删除智能体
 */
const deleteAgent = async () => {
  try {
    await showDeleteConfirm(`确定要删除智能体 "${props.item.name}" 吗？`)

    const response = await deleteAgentAPI({ agent_id: props.item.agent_id })

    if (response.data?.status_code === 200) {
      HMessage.success('删除成功')
      emits('delete')
    } else {
      HMessage.error('删除失败')
    }
  } catch (error) {
    // 用户取消删除，静默处理
    if (error !== 'cancel') {
      console.error('删除操作失败:', error)
    }
  }
}

/**
 * 编辑智能体
 */
const editAgent = () => {
  emits('edit', props.item)
}
</script>

<template>
  <div class="agent-card">
    <div class="card-content">
      <!-- 头部：图标和名称 -->
      <div class="card-header">
        <img
          :src="props.item.logo_url"
          :alt="props.item.name"
          class="agent-logo"
        />
        <span class="agent-name">{{ props.item.name }}</span>
      </div>

      <!-- 描述信息 -->
      <div class="card-description">
        {{ props.item.description }}
      </div>

      <!-- 统计信息 -->
      <div class="card-stats">
        <div
          v-for="(stat, index) in stats"
          :key="index"
          class="stat-item"
          :title="stat.title"
        >
          <span class="stat-icon">{{ stat.icon }}</span>
          <span class="stat-label">{{ stat.label }}</span>
          <span class="stat-value">{{ stat.count }}</span>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="card-actions">
        <button class="action-btn edit-btn" @click.stop="editAgent">
          <img src="../../assets/set.svg" width="24px" />
        </button>
        <button class="action-btn delete-btn" @click.stop="deleteAgent">
          <img src="../../assets/delete.svg" width="28px" />
        </button>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
/* 样式变量定义 */
$card-height: 160px;
$border-radius-lg: 20px;
$border-radius-md: 10px;
$spacing-sm: 8px;
$spacing-md: 14px;
$transition-default: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);

.agent-card {
  margin: $spacing-sm $spacing-sm 0 0;
  display: flex;
  flex-direction: column;
  height: $card-height;
  background: var(--harmony-comp-background-primary);
  border-radius: $border-radius-lg;
  border: 1px solid var(--harmony-comp-divider);
  box-shadow: var(--harmony-shadow-md);
  transition: $transition-default;
  overflow: hidden;
  position: relative;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, var(--harmony-brand) 0%, #8b5cf6 50%, #06b6d4 100%);
    border-radius: $border-radius-lg $border-radius-lg 0 0;
  }

  .card-content {
    padding: $spacing-md;
    display: flex;
    flex-direction: column;
    height: 100%;
  }

  .card-header {
    display: flex;
    align-items: center;
    margin-bottom: 10px;

    .agent-logo {
      width: 36px;
      height: 36px;
      border-radius: $border-radius-md;
      margin-right: 10px;
      border: 2px solid var(--harmony-comp-emphasize-tertiary);
      object-fit: cover;
      transition: $transition-default;
    }

    .agent-name {
      font-size: 15px;
      font-weight: 600;
      color: var(--harmony-font-primary);
      font-family: var(--harmony-font-family);
      line-height: 1.3;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      flex: 1;
    }
  }

  .card-description {
    display: -webkit-box;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 2;
    overflow: hidden;
    font-size: 12px;
    font-weight: 400;
    line-height: 1.4;
    color: var(--harmony-font-secondary);
    margin-bottom: 10px;
    flex: 1;
    font-family: var(--harmony-font-family);
  }

  .card-stats {
    display: flex;
    gap: 4px;
    margin-bottom: $spacing-sm;

    .stat-item {
      display: flex;
      align-items: center;
      gap: 3px;
      padding: 2px 4px;
      background: var(--harmony-comp-emphasize-tertiary);
      border-radius: $spacing-sm;
      border: 1px solid var(--harmony-comp-emphasize-tertiary);
      transition: $transition-default;
      cursor: default;

      &:hover {
        background: var(--harmony-comp-emphasize-tertiary);
        border-color: var(--harmony-comp-emphasize-tertiary);
        transform: translateY(-1px);
      }

      .stat-icon {
        font-size: 12px;
        line-height: 1;
      }

      .stat-label {
        font-size: 9px;
        font-weight: 500;
        color: var(--harmony-font-secondary);
        white-space: nowrap;
      }

      .stat-value {
        font-size: 10px;
        font-weight: 600;
        color: var(--harmony-brand));
        background: var(--harmony-comp-emphasize-tertiary);
        padding: 1px 4px;
        border-radius: 4px;
        min-width: 16px;
        text-align: center;
        line-height: 1;
      }
    }
  }

  .card-actions {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    gap: 12px;
    margin-top: auto;

    .action-btn {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 28px;
      height: 28px;
      border-radius: $spacing-sm;
      cursor: pointer;
      transition: $transition-default;
      opacity: 0;
      transform: translateY(8px);
      border: none;
      background: none;
      padding: 0;

      img {
        width: 16px;
        height: 16px;
        transition: $transition-default;
      }
    }

    .edit-btn {
      background: var(--harmony-comp-emphasize-tertiary);
      border: 1px solid var(--harmony-comp-emphasize-tertiary);

      &:hover {
        background: var(--harmony-comp-emphasize-tertiary);
        border-color: var(--harmony-comp-emphasize-tertiary);
        transform: translateY(-2px);
        box-shadow: var(--harmony-shadow-dialog);

        img {
          filter: saturate(1.5);
          transform: scale(1.1);
        }
      }
    }

    .delete-btn {
      background: var(--harmony-warning-bg);
      border: 1px solid var(--harmony-warning-bg);

      &:hover {
        background: var(--harmony-warning-bg);
        border-color: var(--harmony-warning-bg);
        transform: translateY(-2px);
        box-shadow: var(--harmony-shadow-dialog);

        img {
          filter: saturate(1.5);
          transform: scale(1.1);
        }
      }
    }
  }

  &:hover {
    background: var(--harmony-comp-background-primary);
    border-color: var(--harmony-comp-emphasize-tertiary);
    box-shadow: var(--harmony-shadow-dialog);
    transform: translateY(-8px) scale(1.02);

    .card-content {
      .card-header {
        .agent-logo {
          border-color: var(--harmony-comp-emphasize-tertiary);
          transform: scale(1.05);
        }

        .agent-name {
          color: var(--harmony-brand));
        }
      }

      .card-actions {
        .action-btn {
          opacity: 1;
          transform: translateY(0);
        }
      }
    }
  }
}
</style>

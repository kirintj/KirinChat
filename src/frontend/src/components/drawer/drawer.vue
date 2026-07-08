<script setup lang="ts">
import { reactive, ref, onMounted, computed } from "vue"
import CommonCard from "../../components/commonCard"
import { getAgentsAPI } from "../../apis/agent"
import { Agent } from '../../type'
import { HMessage, HDrawer, HInput, HButton, HSkeleton } from "@/components/ui"

const emits = defineEmits<{
  (event: "goChat", item: Agent): void
}>()

const drawer = ref(false)
let cardList: Agent[] = reactive([])
const currentId = ref()
const curentItem = ref<Agent>()
const searchKeyword = ref('')
const loading = ref(false)

// 过滤后的智能体列表
const filteredAgents = computed(() => {
  if (!searchKeyword.value) {
    return cardList
  }
  return cardList.filter(agent => 
    agent.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
    agent.description.toLowerCase().includes(searchKeyword.value.toLowerCase())
  )
})

onMounted(async () => {
  await loadAgents()
})

const loadAgents = async () => {
  try {
    loading.value = true
    const response = await getAgentsAPI()
    cardList = response.data.data
    if (cardList.length > 0) {
      currentId.value = cardList[0].agent_id
      curentItem.value = cardList[0]
    }
  } catch (error) {
    console.error('获取智能体列表失败:', error)
    HMessage.error('获取智能体列表失败')
  } finally {
    loading.value = false
  }
}

const open = () => {
  drawer.value = true
  // 重置搜索
  searchKeyword.value = ''
}

const close = () => {
  drawer.value = false
}

const optionCard = (item: Agent) => {
  currentId.value = item.agent_id
  curentItem.value = item
}

const cancel = () => {
  close()
}

const primary = () => {
  if (curentItem.value) {
    emits("goChat", curentItem.value)
  } else {
    HMessage.warning('请选择一个智能体')
  }
  close()
}

defineExpose({
  open,
  close,
})
</script>

<template>
  <div class="drawer">
    <HDrawer
      v-model="drawer"
      title="选择智能体创建会话"
      size="500px"
      direction="right"
    >
      <div class="drawer-content">
        <!-- 搜索框 -->
        <div class="search-section">
          <HInput
            v-model="searchKeyword"
            placeholder="搜索智能体..."
            clearable
            size="large"
          />
        </div>

        <!-- 智能体列表 -->
        <div class="agents-section">
          <div class="section-header">
            <span class="title">可用智能体</span>
            <span class="count">({{ filteredAgents.length }})</span>
          </div>

          <div v-if="loading" class="loading-state">
            <HSkeleton :rows="3" animated />
          </div>

          <div v-else-if="filteredAgents.length === 0" class="empty-state">
            <div class="empty-icon">🤖</div>
            <div class="empty-text">
              {{ searchKeyword ? '没有找到相关智能体' : '暂无可用智能体' }}
            </div>
            <div v-if="!searchKeyword" class="empty-hint">
              请联系管理员添加智能体
            </div>
          </div>

          <div v-else class="agents-grid">
            <div
              v-for="item in filteredAgents"
              :key="item.agent_id"
              :class="['agent-card', currentId === item.agent_id ? 'active' : '']"
              @click="optionCard(item)"
            >
              <CommonCard
                :title="item.name"
                :detail="item.description"
                :imgUrl="item.logo_url"
              />
            </div>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="actions-section">
          <HButton @click="cancel" size="large" class="cancel-btn" type="secondary">
            取消
          </HButton>
          <HButton
            type="primary"
            @click="primary"
            size="large"
            class="confirm-btn"
            :disabled="!curentItem"
          >
            + 创建会话
          </HButton>
        </div>
      </div>
    </HDrawer>
  </div>
</template>

<style lang="scss" scoped>
@use '../../styles/breakpoints.scss' as *;

.drawer {
  .drawer-content {
    height: 100%;
    display: flex;
    flex-direction: column;
    padding: 0;

    .search-section {
      padding: 20px 24px 16px;
      border-bottom: 1px solid var(--harmony-comp-divider);
    }

    .agents-section {
      flex: 1;
      padding: 16px 24px;
      overflow-y: auto;

      .section-header {
        display: flex;
        align-items: center;
        gap: 4px;
        margin-bottom: 16px;

        .title {
          font-size: var(--harmony-font-size-body-l);
          font-weight: 600;
          color: var(--harmony-font-primary);
        }

        .count {
          font-size: var(--harmony-font-size-body-m);
          color: var(--harmony-font-secondary);
        }
      }

      .loading-state {
        padding: 20px 0;
      }

      .empty-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 200px;
        color: var(--harmony-font-tertiary);

        .empty-icon {
          font-size: 48px;
          margin-bottom: 16px;
        }

        .empty-text {
          font-size: var(--harmony-font-size-body-m);
          margin-bottom: 8px;
        }

        .empty-hint {
          font-size: var(--harmony-font-size-body-s);
          color: var(--harmony-font-fourth);
        }
      }

      .agents-grid {
        display: grid;
        grid-template-columns: 1fr;
        gap: 12px;

        .agent-card {
          cursor: pointer;
          border-radius: var(--harmony-corner-radius-level4);
          transition: all 0.2s ease;
          border: 2px solid transparent;

          &:hover {
            transform: translateY(-2px);
            box-shadow: var(--harmony-shadow-md);
          }

          &.active {
            border-color: var(--harmony-brand);
            background-color: var(--harmony-comp-emphasize-tertiary);
          }
        }
      }
    }

    .actions-section {
      padding: 20px 24px;
      border-top: 1px solid var(--harmony-comp-divider);
      display: flex;
      gap: 12px;

      .cancel-btn {
        flex: 1;
        border-radius: var(--harmony-corner-radius-level4);
      }

      .confirm-btn {
        flex: 1;
        border-radius: var(--harmony-corner-radius-level4);
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;

        &:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }
      }
    }
  }
}

// 响应式设计
@include mobile {
  .drawer {
    .drawer-content {
      .search-section,
      .agents-section,
      .actions-section {
        padding-left: 16px;
        padding-right: 16px;
      }
    }
  }
}
</style>

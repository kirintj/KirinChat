<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { HButton, HMessage, HMessageBox } from '@/components/ui'
import {
  getInterviewHistoryAPI,
  getSkillListAPI,
  deleteInterviewSessionAPI,
  type InterviewSession,
  type SkillInfo,
  type HistoryQueryParams,
} from '../../../apis/interview'

const router = useRouter()

// 状态 Tab
const activeTab = ref('')
const tabs = [
  { label: '全部', value: '' },
  { label: '进行中', value: 'IN_PROGRESS' },
  { label: '已完成', value: 'COMPLETED' },
  { label: '已评估', value: 'EVALUATED' },
]

// 筛选条件
const selectedSkillId = ref('')
const selectedDifficulty = ref('')
const keyword = ref('')
const sortBy = ref('create_time')
const sortOrder = ref('desc')

// 分页
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 数据
const sessions = ref<InterviewSession[]>([])
const skills = ref<SkillInfo[]>([])
const loading = ref(false)

// 难度选项
const difficulties = [
  { label: '全部难度', value: '' },
  { label: '简单', value: 'EASY' },
  { label: '中等', value: 'MEDIUM' },
  { label: '困难', value: 'HARD' },
]

// 搜索 debounce
let searchTimer: ReturnType<typeof setTimeout> | null = null
const onSearchInput = () => {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    currentPage.value = 1
    fetchHistory()
  }, 500)
}

// 总页数
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)))

// 页码列表（最多显示 5 个页码）
const pageNumbers = computed(() => {
  const pages: number[] = []
  const tp = totalPages.value
  const cp = currentPage.value
  let start = Math.max(1, cp - 2)
  let end = Math.min(tp, start + 4)
  if (end - start < 4) start = Math.max(1, end - 4)
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

// 获取历史列表
const fetchHistory = async () => {
  loading.value = true
  try {
    const params: HistoryQueryParams = {
      page: currentPage.value,
      page_size: pageSize.value,
      sort_by: sortBy.value,
      sort_order: sortOrder.value,
    }
    if (activeTab.value) params.status = activeTab.value
    if (selectedSkillId.value) params.skill_id = selectedSkillId.value
    if (selectedDifficulty.value) params.difficulty = selectedDifficulty.value
    if (keyword.value.trim()) params.keyword = keyword.value.trim()

    const res = await getInterviewHistoryAPI(params)
    if (res.data.status_code === 200 && res.data.data) {
      sessions.value = res.data.data.sessions || []
      total.value = res.data.data.total || 0
    }
  } catch {
    HMessage.error('加载面试历史失败')
  } finally {
    loading.value = false
  }
}

// 获取技能列表（用于筛选下拉）
const fetchSkills = async () => {
  try {
    const res = await getSkillListAPI()
    if (res.data.status_code === 200 && res.data.data) {
      skills.value = res.data.data.skills || []
    }
  } catch { /* ignore */ }
}

// 切换状态 Tab
const switchTab = (value: string) => {
  activeTab.value = value
  currentPage.value = 1
  fetchHistory()
}

// 切换排序
const toggleSort = (field: string) => {
  if (sortBy.value === field) {
    sortOrder.value = sortOrder.value === 'desc' ? 'asc' : 'desc'
  } else {
    sortBy.value = field
    sortOrder.value = 'desc'
  }
  currentPage.value = 1
  fetchHistory()
}

// 切换页码
const goToPage = (page: number) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  fetchHistory()
}

// 继续面试
const continueInterview = (sessionId: string) => {
  router.push({ path: '/interview/chat', query: { sessionId } })
}

// 查看报告
const viewReport = (sessionId: string) => {
  router.push({ path: '/interview/report', query: { sessionId } })
}

// 删除面试
const deleteSession = async (sessionId: string) => {
  try {
    await HMessageBox.confirm('确定要删除这条面试记录吗？此操作不可撤销。', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
  } catch {
    return
  }
  try {
    const res = await deleteInterviewSessionAPI(sessionId)
    if (res.data.status_code === 200) {
      HMessage.success('删除成功')
      fetchHistory()
    } else {
      HMessage.error(res.data.message || '删除失败')
    }
  } catch {
    HMessage.error('删除失败')
  }
}

// 返回 hubPage
const goBack = () => {
  router.push('/interview')
}

// 难度中文标签
const difficultyLabel = (d?: string | null) => {
  const map: Record<string, string> = { EASY: '简单', MEDIUM: '中等', HARD: '困难' }
  return map[d || ''] || d || ''
}

// 难度样式 class
const difficultyClass = (d?: string | null) => {
  const map: Record<string, string> = { EASY: 'easy', MEDIUM: 'medium', HARD: 'hard' }
  return map[d || ''] || ''
}

// 格式化时间
const formatTime = (t?: string | null) => {
  if (!t) return ''
  const d = new Date(t)
  return d.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

// 监听筛选条件变化
watch([selectedSkillId, selectedDifficulty], () => {
  currentPage.value = 1
  fetchHistory()
})

onBeforeUnmount(() => {
  if (searchTimer) clearTimeout(searchTimer)
})

onMounted(() => {
  fetchSkills()
  fetchHistory()
})
</script>

<template>
  <div class="history-page">
    <!-- 顶部导航 -->
    <div class="page-header">
      <button class="back-btn" @click="goBack">
        <span class="back-icon">&#8592;</span>
        <span>返回</span>
      </button>
      <h2 class="page-title">面试历史</h2>
      <div class="header-spacer"></div>
    </div>

    <!-- 搜索和筛选栏 -->
    <div class="filter-bar">
      <div class="search-box">
        <input
          v-model="keyword"
          type="text"
          placeholder="搜索技能名称..."
          @input="onSearchInput"
        />
      </div>
      <select v-model="selectedSkillId" class="filter-select">
        <option value="">全部技能</option>
        <option v-for="s in skills" :key="s.id" :value="s.id">{{ s.name }}</option>
      </select>
      <select v-model="selectedDifficulty" class="filter-select">
        <option v-for="d in difficulties" :key="d.value" :value="d.value">{{ d.label }}</option>
      </select>
    </div>

    <!-- 状态 Tab -->
    <div class="status-tabs">
      <button
        v-for="tab in tabs"
        :key="tab.value"
        :class="['tab-btn', { active: activeTab === tab.value }]"
        @click="switchTab(tab.value)"
      >
        {{ tab.label }}
      </button>
      <div class="sort-controls">
        <button
          :class="['sort-btn', { active: sortBy === 'create_time' }]"
          @click="toggleSort('create_time')"
        >
          时间 {{ sortBy === 'create_time' ? (sortOrder === 'desc' ? '↓' : '↑') : '' }}
        </button>
        <button
          :class="['sort-btn', { active: sortBy === 'total_score' }]"
          @click="toggleSort('total_score')"
        >
          分数 {{ sortBy === 'total_score' ? (sortOrder === 'desc' ? '↓' : '↑') : '' }}
        </button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">加载中...</div>

    <!-- 空状态 -->
    <div v-else-if="sessions.length === 0" class="empty-state">
      <p>暂无面试记录</p>
      <HButton type="primary" size="small" @click="router.push('/interview')">开始面试</HButton>
    </div>

    <!-- 列表 -->
    <div v-else class="session-list">
      <div v-for="s in sessions" :key="s.id" class="session-item">
        <div class="session-left">
          <div class="session-title">
            <span class="skill-name">{{ s.skill_name || s.skill_id }}</span>
            <span :class="['difficulty-tag', difficultyClass(s.difficulty)]">
              {{ difficultyLabel(s.difficulty) }}
            </span>
          </div>
          <div class="session-meta">
            <span class="status-text">{{ s.status === 'IN_PROGRESS' ? '进行中' : s.status === 'COMPLETED' ? '已完成' : '已评估' }}</span>
            <span class="time-text">{{ formatTime(s.create_time) }}</span>
          </div>
        </div>
        <div class="session-right">
          <div v-if="s.total_score != null" class="score-display">
            {{ Math.round(s.total_score) }}分
          </div>
          <div class="session-actions">
            <HButton
              v-if="s.status === 'IN_PROGRESS'"
              type="primary"
              size="small"
              @click="continueInterview(s.id)"
            >
              继续
            </HButton>
            <HButton
              v-if="s.status === 'COMPLETED' || s.status === 'EVALUATED'"
              type="primary"
              size="small"
              @click="viewReport(s.id)"
            >
              报告
            </HButton>
            <HButton
              type="text"
              size="small"
              class="delete-btn"
              @click="deleteSession(s.id)"
            >
              删除
            </HButton>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页器 -->
    <div v-if="total > pageSize" class="pagination">
      <button class="page-btn" :disabled="currentPage <= 1" @click="goToPage(currentPage - 1)">
        &lt;
      </button>
      <button
        v-for="p in pageNumbers"
        :key="p"
        :class="['page-btn', { active: p === currentPage }]"
        @click="goToPage(p)"
      >
        {{ p }}
      </button>
      <button class="page-btn" :disabled="currentPage >= totalPages" @click="goToPage(currentPage + 1)">
        &gt;
      </button>
      <span class="page-info">共 {{ total }} 条</span>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.history-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--harmony-comp-background-primary);
  overflow-y: auto;
}

.page-header {
  display: flex;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid var(--harmony-comp-divider);
  flex-shrink: 0;

  .back-btn {
    display: flex;
    align-items: center;
    gap: 4px;
    background: none;
    border: none;
    color: var(--harmony-font-secondary);
    cursor: pointer;
    font-size: 14px;
    padding: 4px 8px;
    border-radius: var(--harmony-corner-radius-level4);
    transition: all var(--harmony-duration-fast) var(--harmony-motion-standard);

    &:hover {
      color: var(--harmony-brand));
      background: var(--harmony-comp-emphasize-tertiary);
    }
  }

  .page-title {
    font-size: 18px;
    font-weight: 600;
    color: var(--harmony-font-primary);
    margin: 0;
    flex: 1;
    text-align: center;
  }

  .header-spacer {
    width: 60px;
  }
}

.filter-bar {
  display: flex;
  gap: 12px;
  padding: 12px 24px;
  border-bottom: 1px solid var(--harmony-comp-divider);
  flex-shrink: 0;

  .search-box {
    flex: 1;

    input {
      width: 100%;
      border: 1px solid var(--harmony-comp-divider);
      border-radius: var(--harmony-corner-radius-level6);
      padding: 8px 12px;
      font-size: 13px;
      background: var(--harmony-comp-background-primary);
      color: var(--harmony-font-primary);
      outline: none;
      transition: border-color var(--harmony-duration-fast) var(--harmony-motion-standard);

      &:focus {
        border-color: var(--harmony-brand));
      }

      &::placeholder {
        color: var(--harmony-font-tertiary);
      }
    }
  }

  .filter-select {
    border: 1px solid var(--harmony-comp-divider);
    border-radius: var(--harmony-corner-radius-level6);
    padding: 8px 12px;
    font-size: 13px;
    background: var(--harmony-comp-background-primary);
    color: var(--harmony-font-primary);
    outline: none;
    cursor: pointer;
    min-width: 100px;

    &:focus {
      border-color: var(--harmony-brand));
    }
  }
}

.status-tabs {
  display: flex;
  align-items: center;
  padding: 0 24px;
  border-bottom: 1px solid var(--harmony-comp-divider);
  flex-shrink: 0;

  .tab-btn {
    padding: 12px 16px;
    background: none;
    border: none;
    border-bottom: 2px solid transparent;
    color: var(--harmony-font-secondary);
    font-size: 14px;
    cursor: pointer;
    transition: all var(--harmony-duration-fast) var(--harmony-motion-standard);

    &:hover {
      color: var(--harmony-brand));
    }

    &.active {
      color: var(--harmony-brand));
      border-bottom-color: var(--harmony-brand));
      font-weight: 600;
    }
  }

  .sort-controls {
    margin-left: auto;
    display: flex;
    gap: 8px;

    .sort-btn {
      background: none;
      border: 1px solid var(--harmony-comp-divider);
      border-radius: var(--harmony-corner-radius-level4);
      padding: 4px 10px;
      font-size: 12px;
      color: var(--harmony-font-secondary);
      cursor: pointer;
      transition: all var(--harmony-duration-fast) var(--harmony-motion-standard);

      &:hover {
        border-color: var(--harmony-brand));
        color: var(--harmony-brand));
      }

      &.active {
        border-color: var(--harmony-brand));
        color: var(--harmony-brand));
        background: var(--harmony-comp-emphasize-tertiary);
      }
    }
  }
}

.loading-state,
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  color: var(--harmony-font-tertiary);
  font-size: 14px;
  gap: 16px;
}

.session-list {
  flex: 1;
  padding: 0;
}

.session-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  border-bottom: 1px solid var(--harmony-comp-divider);
  transition: background var(--harmony-duration-fast) var(--harmony-motion-standard);

  &:hover {
    background: var(--harmony-comp-background-secondary);
  }
}

.session-left {
  display: flex;
  flex-direction: column;
  gap: 6px;

  .session-title {
    display: flex;
    align-items: center;
    gap: 8px;

    .skill-name {
      font-size: 15px;
      font-weight: 600;
      color: var(--harmony-font-primary);
    }

    .difficulty-tag {
      font-size: 11px;
      padding: 2px 8px;
      border-radius: 10px;
      font-weight: 500;

      &.easy {
        background: #e6f9f0;
        color: #0a7c42;
      }

      &.medium {
        background: #fff7e6;
        color: #b35c00;
      }

      &.hard {
        background: #ffe6e6;
        color: #c0392b;
      }
    }
  }

  .session-meta {
    display: flex;
    gap: 12px;
    font-size: 12px;
    color: var(--harmony-font-tertiary);

    .status-text {
      font-weight: 500;
    }
  }
}

.session-right {
  display: flex;
  align-items: center;
  gap: 16px;

  .score-display {
    font-size: 20px;
    font-weight: 700;
    color: var(--harmony-brand));
    min-width: 50px;
    text-align: right;
  }

  .session-actions {
    display: flex;
    gap: 8px;
    align-items: center;

    .delete-btn {
      color: var(--harmony-warning) !important;
    }
  }
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 16px 24px;
  border-top: 1px solid var(--harmony-comp-divider);
  flex-shrink: 0;

  .page-btn {
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid var(--harmony-comp-divider);
    border-radius: var(--harmony-corner-radius-level4);
    background: var(--harmony-comp-background-primary);
    color: var(--harmony-font-secondary);
    font-size: 13px;
    cursor: pointer;
    transition: all var(--harmony-duration-fast) var(--harmony-motion-standard);

    &:hover:not(:disabled) {
      border-color: var(--harmony-brand));
      color: var(--harmony-brand));
    }

    &.active {
      background: var(--harmony-brand));
      border-color: var(--harmony-brand));
      color: #fff;
    }

    &:disabled {
      opacity: 0.4;
      cursor: not-allowed;
    }
  }

  .page-info {
    margin-left: 12px;
    font-size: 12px;
    color: var(--harmony-font-tertiary);
  }
}
</style>

# 面试历史管理 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现独立面试历史列表页，支持后端筛选/排序/分页，前端展示全部历史、筛选条件、继续面试、删除记录。

**Architecture:** 后端在现有 `GET /interview/history` 端点上扩展查询参数（status/skill_id/difficulty/keyword/sort_by/sort_order/page/page_size），在 Python 层面进行过滤和分页；`InterviewSessionResp` 补充 `skill_name` 和 `total_score` 字段。前端新建 `historyPage.vue`，提供 Tab 状态筛选、下拉技能/难度筛选、搜索框、排序切换、分页器，以及继续面试和删除功能。

**Tech Stack:** Python 3.12+, FastAPI, SQLModel, Vue 3.4+, TypeScript, Vue Router, Pinia, SCSS

---

## 文件结构

| 文件 | 操作 | 职责 |
|------|------|------|
| `src/backend/kirinchat/schemas/interview.py` | 修改 | `InterviewSessionResp` 新增字段；`InterviewHistoryResp` 新增分页字段 |
| `src/backend/kirinchat/api/v1/interview.py` | 修改 | history 端点支持查询参数；`_session_to_resp` 增加 `skill_name`/`total_score` |
| `src/frontend/src/apis/interview.ts` | 修改 | history API 函数支持查询参数；`deleteInterviewSessionAPI` 已存在无需新建 |
| `src/frontend/src/pages/interview/historyPage/historyPage.vue` | 新建 | 面试历史列表页（Tab、筛选、搜索、排序、列表、分页、操作） |
| `src/frontend/src/pages/interview/index.ts` | 修改 | 导出 `InterviewHistory` |
| `src/frontend/src/router/index.ts` | 修改 | 注册 `/interview/history` 路由 |
| `src/frontend/src/pages/interview/hubPage/hubPage.vue` | 修改 | "最近面试"标题旁添加"查看全部"链接 |

---

### Task 1: 后端 Schema — 扩展 InterviewSessionResp 和 InterviewHistoryResp

**Files:**
- Modify: `src/backend/kirinchat/schemas/interview.py:67-128`

- [ ] **Step 1: 修改 InterviewSessionResp 新增字段**

在 `InterviewSessionResp` 的 `progress` 字段之后新增：

```python
    skill_name: str = Field(default="", description="技能名称")
    total_score: Optional[float] = Field(None, description="总分（已评估时有值）")
```

- [ ] **Step 2: 修改 InterviewHistoryResp 新增分页字段**

将当前的：
```python
class InterviewHistoryResp(BaseModel):
    """面试历史响应"""
    sessions: List[InterviewSessionResp] = Field(default=[], description="会话列表")
```

改为：
```python
class InterviewHistoryResp(BaseModel):
    """面试历史响应"""
    sessions: List[InterviewSessionResp] = Field(default=[], description="会话列表")
    total: int = Field(default=0, description="总记录数")
    page: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=20, description="每页条数")
```

- [ ] **Step 3: 语法验证**

```bash
python -c "
import ast
for f in ['src/backend/kirinchat/schemas/interview.py']:
    with open(f, encoding='utf-8') as fh:
        ast.parse(fh.read())
    print(f'{f}: OK')
"
```

Expected: `src/backend/kirinchat/schemas/interview.py: OK`

- [ ] **Step 4: Commit**

```bash
git add src/backend/kirinchat/schemas/interview.py
git commit -m "feat(interview): 扩展 Schema 新增历史管理字段"
```

---

### Task 2: 后端 API — history 端点支持筛选/排序/分页

**Files:**
- Modify: `src/backend/kirinchat/api/v1/interview.py:53-62`（`_session_to_resp` 函数）
- Modify: `src/backend/kirinchat/api/v1/interview.py:451-469`（`get_interview_history` 端点）

依赖：Task 1 完成（Schema 已有新字段）

- [ ] **Step 1: 修改 `_session_to_resp` 辅助函数**

将当前的：
```python
def _session_to_resp(session) -> InterviewSessionResp:
    """Convert an InterviewSessionTable to an InterviewSessionResp."""
    return InterviewSessionResp(
        id=session.id,
        skill_id=session.skill_id,
        status=session.status,
        difficulty=session.difficulty,
        progress={},
    )
```

改为：
```python
def _session_to_resp(session, skill_name: str = "", total_score: float | None = None) -> InterviewSessionResp:
    """Convert an InterviewSessionTable to an InterviewSessionResp."""
    return InterviewSessionResp(
        id=session.id,
        skill_id=session.skill_id,
        status=session.status,
        difficulty=session.difficulty,
        progress={},
        skill_name=skill_name,
        total_score=total_score,
    )
```

- [ ] **Step 2: 修改 `get_interview_history` 端点**

在文件顶部 import 区新增：
```python
from typing import Optional
```

将 `get_interview_history` 端点（第 451-469 行）替换为：

```python
@router.get("/interview/history", response_model=UnifiedResponseModel)
async def get_interview_history(
    status: Optional[str] = None,
    skill_id: Optional[str] = None,
    difficulty: Optional[str] = None,
    keyword: Optional[str] = None,
    sort_by: str = "create_time",
    sort_order: str = "desc",
    page: int = 1,
    page_size: int = 20,
    login_user: UserPayload = Depends(get_login_user),
):
    """获取面试历史列表，支持筛选、排序、分页。"""
    try:
        # 查询用户所有会话
        sessions = await InterviewService.get_user_sessions(login_user.user_id)

        # 为每个会话补充 skill_name 和 total_score，同时做筛选
        enriched = []
        for s in sessions:
            # 获取技能名称
            skill = SkillService.get_skill_by_id(s.skill_id)
            skill_name = skill.get("name", "") if skill else ""

            # 获取总分（仅已评估的会话有）
            report = await EvaluationService.get_report_by_session(s.id)
            total_score = report.total_score if report else None

            # 计算进度
            progress = await InterviewService.calculate_progress(s.id)

            # 筛选：status
            if status and s.status != status:
                continue
            # 筛选：skill_id
            if skill_id and s.skill_id != skill_id:
                continue
            # 筛选：difficulty
            if difficulty and s.difficulty != difficulty:
                continue
            # 筛选：keyword（匹配技能名称）
            if keyword and keyword.lower() not in skill_name.lower():
                continue

            enriched.append({
                "session": s,
                "skill_name": skill_name,
                "total_score": total_score,
                "progress": progress,
            })

        # 排序
        reverse = sort_order.lower() == "desc"
        if sort_by == "total_score":
            # None 排到最后
            enriched.sort(key=lambda x: (x["total_score"] is None, x["total_score"] or 0), reverse=reverse)
        else:
            # 默认按 create_time 排序
            enriched.sort(key=lambda x: x["session"].create_time or datetime.min, reverse=reverse)

        # 分页
        total = len(enriched)
        start = (page - 1) * page_size
        end = start + page_size
        page_items = enriched[start:end]

        # 构建响应
        session_resps = [
            _session_to_resp(
                item["session"],
                skill_name=item["skill_name"],
                total_score=item["total_score"],
            )
            for item in page_items
        ]
        # 给每个 session_resp 填充 progress
        for resp_obj, item in zip(session_resps, page_items):
            resp_obj.progress = item["progress"]

        data = InterviewHistoryResp(
            sessions=session_resps,
            total=total,
            page=page,
            page_size=page_size,
        )
        return resp_200(data=data.model_dump())
    except Exception as err:
        logger.error(f"Get interview history error: {err}")
        return resp_500(message=str(err))
```

注意：需要在文件顶部 import 中确保 `datetime` 已导入：
```python
from datetime import datetime
```

- [ ] **Step 3: 语法验证**

```bash
python -c "
import ast
for f in ['src/backend/kirinchat/api/v1/interview.py']:
    with open(f, encoding='utf-8') as fh:
        ast.parse(fh.read())
    print(f'{f}: OK')
"
```

Expected: `src/backend/kirinchat/api/v1/interview.py: OK`

- [ ] **Step 4: Commit**

```bash
git add src/backend/kirinchat/api/v1/interview.py
git commit -m "feat(interview): history 端点支持筛选/排序/分页"
```

---

### Task 3: 前端接口 — 修改 history API 函数

**Files:**
- Modify: `src/frontend/src/apis/interview.ts`

依赖：Task 2 完成（后端 API 已就绪）

- [ ] **Step 1: 修改 InterviewSession 接口新增字段**

找到 `InterviewSession` 接口（约第 99-106 行），在 `progress` 之后新增：

```typescript
    skill_name?: string
    total_score?: number | null
```

- [ ] **Step 2: 修改 InterviewHistory 接口新增分页字段**

将当前的：
```typescript
export interface InterviewHistory {
    sessions: InterviewSession[]
}
```

改为：
```typescript
export interface InterviewHistory {
    sessions: InterviewSession[]
    total: number
    page: number
    page_size: number
}
```

- [ ] **Step 3: 修改 getInterviewHistoryAPI 函数支持查询参数**

将当前的：
```typescript
export function getInterviewHistoryAPI() {
    return request.get<UnifiedResponse<InterviewHistory>>('/api/v1/interview/history')
}
```

改为：
```typescript
export interface HistoryQueryParams {
    status?: string
    skill_id?: string
    difficulty?: string
    keyword?: string
    sort_by?: string
    sort_order?: string
    page?: number
    page_size?: number
}

export function getInterviewHistoryAPI(params?: HistoryQueryParams) {
    return request.get<UnifiedResponse<InterviewHistory>>('/api/v1/interview/history', { params })
}
```

- [ ] **Step 4: Commit**

```bash
git add src/frontend/src/apis/interview.ts
git commit -m "feat(interview): 前端 history API 支持查询参数"
```

---

### Task 4: 前端页面 — 新建 historyPage.vue

**Files:**
- Create: `src/frontend/src/pages/interview/historyPage/historyPage.vue`

依赖：Task 3 完成（前端 API 函数已就绪）

- [ ] **Step 1: 创建 historyPage.vue 完整实现**

```vue
<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { HButton, HMessage } from '@/components/ui'
import {
  getInterviewHistoryAPI,
  getSkillsAPI,
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
    const res = await getSkillsAPI()
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
  if (!confirm('确定要删除这条面试记录吗？此操作不可撤销。')) return
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
  background: var(--color-bg);
  overflow-y: auto;
}

.page-header {
  display: flex;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;

  .back-btn {
    display: flex;
    align-items: center;
    gap: 4px;
    background: none;
    border: none;
    color: var(--color-text-secondary);
    cursor: pointer;
    font-size: 14px;
    padding: 4px 8px;
    border-radius: var(--radius-sm);
    transition: all var(--duration-fast) var(--easing);

    &:hover {
      color: var(--color-primary);
      background: var(--color-primary-bg);
    }
  }

  .page-title {
    font-size: 18px;
    font-weight: 600;
    color: var(--color-text-primary);
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
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;

  .search-box {
    flex: 1;

    input {
      width: 100%;
      border: 1px solid var(--color-border);
      border-radius: var(--radius-md);
      padding: 8px 12px;
      font-size: 13px;
      background: var(--color-bg);
      color: var(--color-text-primary);
      outline: none;
      transition: border-color var(--duration-fast) var(--easing);

      &:focus {
        border-color: var(--color-primary);
      }

      &::placeholder {
        color: var(--color-text-tertiary);
      }
    }
  }

  .filter-select {
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    padding: 8px 12px;
    font-size: 13px;
    background: var(--color-bg);
    color: var(--color-text-primary);
    outline: none;
    cursor: pointer;
    min-width: 100px;

    &:focus {
      border-color: var(--color-primary);
    }
  }
}

.status-tabs {
  display: flex;
  align-items: center;
  padding: 0 24px;
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;

  .tab-btn {
    padding: 12px 16px;
    background: none;
    border: none;
    border-bottom: 2px solid transparent;
    color: var(--color-text-secondary);
    font-size: 14px;
    cursor: pointer;
    transition: all var(--duration-fast) var(--easing);

    &:hover {
      color: var(--color-primary);
    }

    &.active {
      color: var(--color-primary);
      border-bottom-color: var(--color-primary);
      font-weight: 600;
    }
  }

  .sort-controls {
    margin-left: auto;
    display: flex;
    gap: 8px;

    .sort-btn {
      background: none;
      border: 1px solid var(--color-border);
      border-radius: var(--radius-sm);
      padding: 4px 10px;
      font-size: 12px;
      color: var(--color-text-secondary);
      cursor: pointer;
      transition: all var(--duration-fast) var(--easing);

      &:hover {
        border-color: var(--color-primary);
        color: var(--color-primary);
      }

      &.active {
        border-color: var(--color-primary);
        color: var(--color-primary);
        background: var(--color-primary-bg);
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
  color: var(--color-text-tertiary);
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
  border-bottom: 1px solid var(--color-border);
  transition: background var(--duration-fast) var(--easing);

  &:hover {
    background: var(--color-bg-secondary);
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
      color: var(--color-text-primary);
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
    color: var(--color-text-tertiary);

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
    color: var(--color-primary);
    min-width: 50px;
    text-align: right;
  }

  .session-actions {
    display: flex;
    gap: 8px;
    align-items: center;

    .delete-btn {
      color: var(--color-danger) !important;
    }
  }
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 16px 24px;
  border-top: 1px solid var(--color-border);
  flex-shrink: 0;

  .page-btn {
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
    background: var(--color-bg);
    color: var(--color-text-secondary);
    font-size: 13px;
    cursor: pointer;
    transition: all var(--duration-fast) var(--easing);

    &:hover:not(:disabled) {
      border-color: var(--color-primary);
      color: var(--color-primary);
    }

    &.active {
      background: var(--color-primary);
      border-color: var(--color-primary);
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
    color: var(--color-text-tertiary);
  }
}
</style>
```

- [ ] **Step 2: Commit**

```bash
git add src/frontend/src/pages/interview/historyPage/historyPage.vue
git commit -m "feat(interview): 新建面试历史列表页"
```

---

### Task 5: 前端路由 — 注册历史页路由

**Files:**
- Modify: `src/frontend/src/pages/interview/index.ts`
- Modify: `src/frontend/src/router/index.ts`

依赖：Task 4 完成（historyPage.vue 已创建）

- [ ] **Step 1: 在 index.ts 中导出新页面**

在 `src/frontend/src/pages/interview/index.ts` 中新增：

```typescript
export { default as InterviewHistory } from './historyPage/historyPage.vue'
```

- [ ] **Step 2: 在 router/index.ts 中注册路由**

在面试相关路由组中（`InterviewReport` 路由之后）新增：

```typescript
    {
      path: 'history',
      name: 'InterviewHistory',
      component: InterviewHistory,
      meta: { requiresAuth: true },
    },
```

同时在 import 区加入 `InterviewHistory`。

- [ ] **Step 3: Commit**

```bash
git add src/frontend/src/pages/interview/index.ts src/frontend/src/router/index.ts
git commit -m "feat(interview): 注册面试历史页路由"
```

---

### Task 6: 前端 — hubPage 添加"查看全部"链接

**Files:**
- Modify: `src/frontend/src/pages/interview/hubPage/hubPage.vue`

依赖：Task 5 完成（路由已注册）

- [ ] **Step 1: 在"最近面试"标题旁添加"查看全部"链接**

在 hubPage.vue 中找到"最近面试"区域的标题（包含文字"最近面试"的 `<h3>` 或类似元素），在其旁边添加：

```html
<router-link to="/interview/history" class="view-all-link">查看全部 &rarr;</router-link>
```

在对应 SCSS 中添加样式：

```scss
.view-all-link {
  font-size: 13px;
  color: var(--color-primary);
  text-decoration: none;
  font-weight: 400;

  &:hover {
    text-decoration: underline;
  }
}
```

- [ ] **Step 2: Commit**

```bash
git add src/frontend/src/pages/interview/hubPage/hubPage.vue
git commit -m "feat(interview): hubPage 添加查看全部历史链接"
```

---

### Task 7: 最终集成验证

**Files:** 无新增/修改

- [ ] **Step 1: 后端语法验证**

```bash
python -c "
import ast
files = [
    'src/backend/kirinchat/schemas/interview.py',
    'src/backend/kirinchat/api/v1/interview.py',
]
for f in files:
    with open(f, encoding='utf-8') as fh:
        ast.parse(fh.read())
    print(f'{f}: OK')
"
```

Expected:
```
src/backend/kirinchat/schemas/interview.py: OK
src/backend/kirinchat/api/v1/interview.py: OK
```

- [ ] **Step 2: 前端构建验证**

```bash
cd src/frontend && npm run build
```

Expected: 无 TypeScript 错误，构建成功。

- [ ] **Step 3: 最终 Commit**

```bash
git add -A
git commit -m "feat(interview): 面试历史管理功能完整实现"
```

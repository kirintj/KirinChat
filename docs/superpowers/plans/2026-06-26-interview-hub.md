# Interview Hub 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在面试模块中新增 Interview Hub 入口页，展示快捷入口、进行中的面试、最近面试摘要和技能统计。

**Architecture:** 纯前端页面，新增 5 个 Vue 组件 + 1 个页面组件，修改路由和侧边栏。数据从现有 `GET /interview/history` 和 `GET /skill/list` 两个接口获取后在前端分流计算。

**Tech Stack:** Vue 3 Composition API, TypeScript, Pinia, Vue Router, SCSS

---

## 文件结构

### 新增文件

| 文件 | 职责 |
|------|------|
| `src/frontend/src/pages/interview/hubPage/hubPage.vue` | Hub 页面主组件，编排四个区块 |
| `src/frontend/src/components/hub/QuickEntryCard.vue` | 快捷入口卡片（纯展示 + 点击跳转） |
| `src/frontend/src/components/hub/ActiveSessionCard.vue` | 进行中面试卡片（session 数据 + 进度条） |
| `src/frontend/src/components/hub/RecentInterviewItem.vue` | 最近面试列表项（技能名 + 分数 + 时间） |
| `src/frontend/src/components/hub/SkillStatCard.vue` | 技能统计卡片（次数 + 平均分进度条） |

### 修改文件

| 文件 | 变更 |
|------|------|
| `src/frontend/src/pages/interview/index.ts` | 新增 `InterviewHub` 导出 |
| `src/frontend/src/router/index.ts` | 新增 `/interview/hub` 子路由 |
| `src/frontend/src/pages/interview/interview.vue` | 侧边栏新增"面试中心"导航项 |

---

## Task 1: 新增路由

**Files:**
- Modify: `src/frontend/src/pages/interview/index.ts`
- Modify: `src/frontend/src/router/index.ts`

- [ ] **Step 1: 在 index.ts 中添加 Hub 导出**

在 `src/frontend/src/pages/interview/index.ts` 末尾追加：

```ts
export { default as InterviewHub } from './hubPage/hubPage.vue'
```

- [ ] **Step 2: 在路由中添加 hub 子路由**

在 `src/frontend/src/router/index.ts` 的 interview children 数组中，在 `{ path: '', name: 'interviewDefault' }` 之前插入：

```ts
{
  path: 'hub',
  name: 'interviewHub',
  component: InterviewHub,
},
```

同时在文件顶部的 import 中确认 `InterviewHub` 已包含：

```ts
import { Interview, InterviewDefault, InterviewChat, InterviewReport, InterviewLearning, InterviewHub } from '../pages/interview'
```

- [ ] **Step 3: 创建 hubPage.vue 骨架**

创建 `src/frontend/src/pages/interview/hubPage/hubPage.vue`，写入最小骨架：

```vue
<script setup lang="ts">
</script>

<template>
  <div class="hub-page">
    <h2>面试中心</h2>
  </div>
</template>

<style lang="scss" scoped>
.hub-page {
  padding: 24px;
}
</style>
```

- [ ] **Step 4: 验证路由可用**

启动前端开发服务器，访问 `/interview/hub`，确认页面渲染"面试中心"标题且无报错。

- [ ] **Step 5: Commit**

```bash
git add src/frontend/src/pages/interview/index.ts src/frontend/src/router/index.ts src/frontend/src/pages/interview/hubPage/hubPage.vue
git commit -m "feat: add /interview/hub route with skeleton page"
```

---

## Task 2: 侧边栏添加"面试中心"导航项

**Files:**
- Modify: `src/frontend/src/pages/interview/interview.vue`

- [ ] **Step 1: 添加导航按钮**

在 `interview.vue` 的 `<template>` 中，找到 `.create-section` 区块（包含"开始新面试"按钮），在其**上方**插入：

```html
<div class="hub-nav">
  <button class="hub-btn" @click="router.push('/interview/hub')">
    <span class="hub-icon">
      <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"/>
        <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/>
      </svg>
    </span>
    <span>面试中心</span>
  </button>
</div>
```

- [ ] **Step 2: 添加样式**

在 `interview.vue` 的 `<style>` 中 `.create-section` 样式之前，添加：

```scss
.hub-nav {
  padding: 12px 16px 0;
}

.hub-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 10px 14px;
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 8px;
  background: var(--bg-secondary, #f9fafb);
  color: var(--text-primary, #1f2937);
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;

  &:hover {
    background: var(--bg-hover, #f3f4f6);
    border-color: var(--primary-color, #6366f1);
    color: var(--primary-color, #6366f1);
  }

  .hub-icon {
    display: flex;
    align-items: center;
  }
}
```

- [ ] **Step 3: 验证侧边栏**

访问 `/interview`，确认侧边栏顶部显示"面试中心"按钮，点击可跳转到 `/interview/hub`。

- [ ] **Step 4: Commit**

```bash
git add src/frontend/src/pages/interview/interview.vue
git commit -m "feat: add interview hub nav item to sidebar"
```

---

## Task 3: QuickEntryCard 组件

**Files:**
- Create: `src/frontend/src/components/hub/QuickEntryCard.vue`

- [ ] **Step 1: 创建组件**

```vue
<script setup lang="ts">
defineProps<{
  icon: string
  title: string
  description: string
}>()

const emit = defineEmits<{
  click: []
}>()
</script>

<template>
  <div class="quick-entry-card" @click="emit('click')">
    <div class="card-icon">{{ icon }}</div>
    <div class="card-title">{{ title }}</div>
    <div class="card-desc">{{ description }}</div>
  </div>
</template>

<style lang="scss" scoped>
.quick-entry-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 24px 16px;
  border-radius: 12px;
  border: 1px solid var(--border-color, #e5e7eb);
  background: var(--bg-primary, #ffffff);
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    border-color: var(--primary-color, #6366f1);
  }
}

.card-icon {
  font-size: 32px;
  line-height: 1;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary, #1f2937);
}

.card-desc {
  font-size: 12px;
  color: var(--text-secondary, #6b7280);
  line-height: 1.4;
}
</style>
```

- [ ] **Step 2: Commit**

```bash
git add src/frontend/src/components/hub/QuickEntryCard.vue
git commit -m "feat: add QuickEntryCard component"
```

---

## Task 4: ActiveSessionCard 组件

**Files:**
- Create: `src/frontend/src/components/hub/ActiveSessionCard.vue`

- [ ] **Step 1: 创建组件**

```vue
<script setup lang="ts">
defineProps<{
  skillName: string
  progress: { current: number; total: number }
}>()

const emit = defineEmits<{
  click: []
}>()

const progressPercent = (current: number, total: number) => {
  if (total === 0) return 0
  return Math.round((current / total) * 100)
}
</script>

<template>
  <div class="active-session-card" @click="emit('click')">
    <div class="card-header">
      <span class="skill-name">{{ skillName }}</span>
      <span class="status-badge">进行中</span>
    </div>
    <div class="progress-section">
      <div class="progress-bar">
        <div
          class="progress-fill"
          :style="{ width: progressPercent(progress.current, progress.total) + '%' }"
        />
      </div>
      <span class="progress-text">{{ progress.current }}/{{ progress.total }} 题</span>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.active-session-card {
  padding: 16px;
  border-radius: 10px;
  border: 1px solid var(--border-color, #e5e7eb);
  background: var(--bg-primary, #ffffff);
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 200px;

  &:hover {
    border-color: var(--primary-color, #6366f1);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.skill-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary, #1f2937);
}

.status-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 10px;
  background: var(--primary-light, #eef2ff);
  color: var(--primary-color, #6366f1);
}

.progress-section {
  display: flex;
  align-items: center;
  gap: 10px;
}

.progress-bar {
  flex: 1;
  height: 6px;
  border-radius: 3px;
  background: var(--bg-secondary, #f3f4f6);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 3px;
  background: var(--primary-color, #6366f1);
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 12px;
  color: var(--text-secondary, #6b7280);
  white-space: nowrap;
}
</style>
```

- [ ] **Step 2: Commit**

```bash
git add src/frontend/src/components/hub/ActiveSessionCard.vue
git commit -m "feat: add ActiveSessionCard component"
```

---

## Task 5: RecentInterviewItem 组件

**Files:**
- Create: `src/frontend/src/components/hub/RecentInterviewItem.vue`

- [ ] **Step 1: 创建组件**

```vue
<script setup lang="ts">
defineProps<{
  skillName: string
  score: number // 0-100 scale
  timeLabel: string
}>()

const emit = defineEmits<{
  click: []
}>()

const scoreColor = (score: number) => {
  if (score >= 80) return '#22c55e'
  if (score >= 60) return '#f59e0b'
  return '#ef4444'
}
</script>

<template>
  <div class="recent-item" @click="emit('click')">
    <div class="item-left">
      <span class="item-skill">{{ skillName }}</span>
      <span class="item-time">{{ timeLabel }}</span>
    </div>
    <div class="item-score" :style="{ color: scoreColor(score) }">
      {{ score }}分
    </div>
  </div>
</template>

<style lang="scss" scoped>
.recent-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid var(--border-light, #f3f4f6);
  cursor: pointer;
  transition: background 0.15s ease;

  &:hover {
    background: var(--bg-hover, #f9fafb);
  }

  &:last-child {
    border-bottom: none;
  }
}

.item-left {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.item-skill {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary, #1f2937);
}

.item-time {
  font-size: 12px;
  color: var(--text-tertiary, #9ca3af);
}

.item-score {
  font-size: 16px;
  font-weight: 700;
}
</style>
```

- [ ] **Step 2: Commit**

```bash
git add src/frontend/src/components/hub/RecentInterviewItem.vue
git commit -m "feat: add RecentInterviewItem component"
```

---

## Task 6: SkillStatCard 组件

**Files:**
- Create: `src/frontend/src/components/hub/SkillStatCard.vue`

- [ ] **Step 1: 创建组件**

```vue
<script setup lang="ts">
defineProps<{
  skillName: string
  count: number
  avgScore: number // 0-100 scale
}>()

const barColor = (score: number) => {
  if (score >= 80) return '#22c55e'
  if (score >= 60) return '#f59e0b'
  return '#ef4444'
}
</script>

<template>
  <div class="skill-stat-card">
    <div class="stat-header">
      <span class="stat-name">{{ skillName }}</span>
      <span class="stat-count">{{ count }} 次面试</span>
    </div>
    <div class="stat-bar-section">
      <div class="stat-bar">
        <div
          class="stat-bar-fill"
          :style="{ width: avgScore + '%', background: barColor(avgScore) }"
        />
      </div>
      <span class="stat-score" :style="{ color: barColor(avgScore) }">{{ avgScore }}分</span>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.skill-stat-card {
  padding: 12px 0;
  border-bottom: 1px solid var(--border-light, #f3f4f6);

  &:last-child {
    border-bottom: none;
  }
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.stat-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary, #1f2937);
}

.stat-count {
  font-size: 12px;
  color: var(--text-tertiary, #9ca3af);
}

.stat-bar-section {
  display: flex;
  align-items: center;
  gap: 10px;
}

.stat-bar {
  flex: 1;
  height: 6px;
  border-radius: 3px;
  background: var(--bg-secondary, #f3f4f6);
  overflow: hidden;
}

.stat-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
}

.stat-score {
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
}
</style>
```

- [ ] **Step 2: Commit**

```bash
git add src/frontend/src/components/hub/SkillStatCard.vue
git commit -m "feat: add SkillStatCard component"
```

---

## Task 7: hubPage 主组件

**Files:**
- Modify: `src/frontend/src/pages/interview/hubPage/hubPage.vue`

- [ ] **Step 1: 完善 hubPage.vue**

替换 `hubPage.vue` 全部内容：

```vue
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { HMessage } from '@/components/ui'
import { getInterviewHistoryAPI, getSkillListAPI } from '../../../apis/interview'
import type { InterviewSession, SkillInfo } from '../../../apis/interview'
import QuickEntryCard from '../../../components/hub/QuickEntryCard.vue'
import ActiveSessionCard from '../../../components/hub/ActiveSessionCard.vue'
import RecentInterviewItem from '../../../components/hub/RecentInterviewItem.vue'
import SkillStatCard from '../../../components/hub/SkillStatCard.vue'

const router = useRouter()
const loading = ref(true)
const sessions = ref<InterviewSession[]>([])
const skillMap = ref<Record<string, string>>({})

// --- Quick entry config ---
const quickEntries = [
  { icon: '✏️', title: '文字面试', description: '选择技能方向，开始 AI 面试', route: '/interview' },
  { icon: '🎙️', title: '语音面试', description: '实时语音对话，模拟真实面试', route: '/voice-interview' },
  { icon: '📄', title: '上传简历', description: '上传简历获取 AI 分析报告', route: '/interview/resume' },
  { icon: '🔍', title: '解析 JD', description: '粘贴职位描述，定制面试题目', route: '/interview/jd' },
]

// --- Computed data from sessions ---

const activeSessions = computed(() =>
  sessions.value.filter(s => s.status === 'IN_PROGRESS' || s.status === 'CREATED')
)

const recentInterviews = computed(() =>
  sessions.value
    .filter(s => s.status === 'EVALUATED' || s.status === 'COMPLETED')
    .slice(0, 5)
)

interface SkillStat {
  skillName: string
  count: number
  avgScore: number
}

const skillStats = computed<SkillStat[]>(() => {
  const evaluated = sessions.value.filter(s => s.status === 'EVALUATED' || s.status === 'COMPLETED')
  const grouped: Record<string, number> = {}

  for (const s of evaluated) {
    grouped[s.skill_id] = (grouped[s.skill_id] || 0) + 1
  }

  return Object.entries(grouped).map(([skillId, count]) => ({
    skillName: skillMap.value[skillId] || skillId,
    count,
    avgScore: 0, // InterviewSession 不含 total_score，暂显示为 0
  })).sort((a, b) => b.count - a.count)
})

const totalCount = computed(() => skillStats.value.reduce((sum, s) => sum + s.count, 0))
const overallAvg = computed(() => {
  // total_score 不在 InterviewSession 中，暂返回 0
  return 0
})

// --- Helpers ---

const getSkillName = (skillId: string) => skillMap.value[skillId] || skillId

const formatTime = (timeStr: string) => {
  try {
    if (!timeStr) return '未知时间'
    const date = new Date(timeStr)
    if (isNaN(date.getTime())) return '未知时间'
    const now = new Date()
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60)
    if (diffInHours < 1) return '刚刚'
    if (diffInHours < 24) return `${Math.floor(diffInHours)}小时前`
    if (diffInHours < 24 * 7) return `${Math.floor(diffInHours / 24)}天前`
    return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
  } catch {
    return '未知时间'
  }
}

// --- Data loading ---

const loadData = async () => {
  loading.value = true
  try {
    const [historyRes, skillRes] = await Promise.all([
      getInterviewHistoryAPI(),
      getSkillListAPI(),
    ])

    if (historyRes.data.status_code === 200 && historyRes.data.data) {
      sessions.value = historyRes.data.data.sessions || []
    }

    if (skillRes.data.status_code === 200 && skillRes.data.data) {
      const map: Record<string, string> = {}
      for (const skill of (skillRes.data.data.skills || [])) {
        map[skill.id] = skill.name
      }
      skillMap.value = map
    }
  } catch {
    HMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="hub-page">
    <!-- Header -->
    <div class="hub-header">
      <h2 class="hub-title">面试中心</h2>
    </div>

    <div v-if="loading" class="loading-state">加载中...</div>

    <template v-else>
      <!-- Section 1: Quick Entry -->
      <section class="hub-section">
        <h3 class="section-title">快捷入口</h3>
        <div class="quick-entry-grid">
          <QuickEntryCard
            v-for="entry in quickEntries"
            :key="entry.title"
            :icon="entry.icon"
            :title="entry.title"
            :description="entry.description"
            @click="router.push(entry.route)"
          />
        </div>
      </section>

      <!-- Section 2: Active Sessions -->
      <section class="hub-section">
        <div class="section-header">
          <h3 class="section-title">进行中的面试</h3>
          <span class="section-link" @click="router.push('/interview')">查看全部 &rarr;</span>
        </div>
        <div v-if="activeSessions.length > 0" class="active-grid">
          <ActiveSessionCard
            v-for="session in activeSessions"
            :key="session.id"
            :skill-name="getSkillName(session.skill_id)"
            :progress="session.progress"
            @click="router.push({ path: '/interview/chat', query: { sessionId: session.id } })"
          />
        </div>
        <div v-else class="empty-state">
          <p class="empty-text">没有进行中的面试</p>
          <button class="empty-btn" @click="router.push('/interview')">开始新面试</button>
        </div>
      </section>

      <!-- Section 3 & 4: Recent + Stats (side by side) -->
      <div class="bottom-grid">
        <!-- Recent Interviews -->
        <section class="hub-section">
          <div class="section-header">
            <h3 class="section-title">最近面试</h3>
            <span class="section-link" @click="router.push('/interview')">查看全部 &rarr;</span>
          </div>
          <div v-if="recentInterviews.length > 0" class="recent-list">
            <RecentInterviewItem
              v-for="session in recentInterviews"
              :key="session.id"
              :skill-name="getSkillName(session.skill_id)"
              :score="0"
              :time-label="'已完成'"
              @click="router.push({ path: '/interview/report', query: { sessionId: session.id } })"
            />
          </div>
          <div v-else class="empty-state">
            <p class="empty-text">暂无面试记录</p>
          </div>
        </section>

        <!-- Skill Stats -->
        <section class="hub-section">
          <div class="section-header">
            <h3 class="section-title">技能统计</h3>
          </div>
          <div v-if="skillStats.length > 0">
            <div class="stats-overview">
              <div class="stat-item">
                <span class="stat-value">{{ totalCount }}</span>
                <span class="stat-label">总面试次数</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ overallAvg }}</span>
                <span class="stat-label">总体平均分</span>
              </div>
            </div>
            <div class="stats-list">
              <SkillStatCard
                v-for="stat in skillStats"
                :key="stat.skillName"
                :skill-name="stat.skillName"
                :count="stat.count"
                :avg-score="stat.avgScore"
              />
            </div>
          </div>
          <div v-else class="empty-state">
            <p class="empty-text">暂无统计数据</p>
          </div>
        </section>
      </div>
    </template>
  </div>
</template>

<style lang="scss" scoped>
.hub-page {
  padding: 24px 32px;
  max-width: 1100px;
  overflow-y: auto;
  height: 100%;
}

.hub-header {
  margin-bottom: 24px;
}

.hub-title {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary, #1f2937);
  margin: 0;
}

.loading-state {
  text-align: center;
  padding: 48px 0;
  color: var(--text-secondary, #6b7280);
  font-size: 14px;
}

.hub-section {
  margin-bottom: 28px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary, #1f2937);
  margin: 0 0 14px 0;

  .section-header & {
    margin-bottom: 0;
  }
}

.section-link {
  font-size: 13px;
  color: var(--primary-color, #6366f1);
  cursor: pointer;

  &:hover {
    text-decoration: underline;
  }
}

// Quick entry grid
.quick-entry-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

// Active sessions horizontal scroll
.active-grid {
  display: flex;
  gap: 14px;
  overflow-x: auto;
  padding-bottom: 4px;
}

// Bottom two-column grid
.bottom-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

// Empty states
.empty-state {
  text-align: center;
  padding: 32px 16px;
  border-radius: 10px;
  border: 1px dashed var(--border-color, #e5e7eb);
}

.empty-text {
  font-size: 14px;
  color: var(--text-tertiary, #9ca3af);
  margin: 0 0 12px 0;
}

.empty-btn {
  padding: 8px 20px;
  border-radius: 8px;
  border: 1px solid var(--primary-color, #6366f1);
  background: transparent;
  color: var(--primary-color, #6366f1);
  font-size: 13px;
  cursor: pointer;

  &:hover {
    background: var(--primary-light, #eef2ff);
  }
}

// Stats overview
.stats-overview {
  display: flex;
  gap: 24px;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-light, #f3f4f6);
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary, #1f2937);
}

.stat-label {
  font-size: 12px;
  color: var(--text-tertiary, #9ca3af);
}

// Responsive
@media (max-width: 1199px) {
  .quick-entry-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .bottom-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 767px) {
  .hub-page {
    padding: 16px;
  }

  .quick-entry-grid {
    grid-template-columns: 1fr;
  }
}
</style>
```

- [ ] **Step 2: 验证页面**

访问 `/interview/hub`，确认：
- 四个快捷入口卡片显示正常
- 进行中的面试区块显示（可能为空状态）
- 最近面试和技能统计区块左右排列
- 点击快捷入口可正确跳转
- 窗口缩小时布局正确响应

- [ ] **Step 3: Commit**

```bash
git add src/frontend/src/pages/interview/hubPage/hubPage.vue
git commit -m "feat: implement Interview Hub page with all sections"
```

---

## Task 8: 最终集成验证

- [ ] **Step 1: 完整流程测试**

1. 访问 `/interview/hub`，确认页面加载无报错
2. 点击"文字面试"快捷入口，确认跳转到 `/interview`
3. 点击"语音面试"快捷入口，确认跳转到 `/voice-interview`
4. 点击"上传简历"快捷入口，确认跳转到 `/interview/resume`
5. 点击"解析 JD"快捷入口，确认跳转到 `/interview/jd`
6. 在侧边栏点击"面试中心"，确认导航回 `/interview/hub`
7. 如果有进行中的面试，确认卡片显示正确且可点击跳转
8. 缩小浏览器窗口，确认响应式布局正常

- [ ] **Step 2: Final Commit (if any fixes needed)**

```bash
git add -A
git commit -m "fix: interview hub integration fixes"
```

---

## 已知限制

1. **分数数据不可用**：当前 `InterviewSession` 接口只有 `id`、`skill_id`、`status`、`progress` 四个字段，不含 `total_score`、`create_time`、`difficulty`。因此：
   - 最近面试的分数显示为 "0分"（灰色）
   - 技能统计的平均分显示为 0
   - 进行中的面试卡片不显示难度标签和创建时间
2. **解决路径**：后续需扩展后端 `GET /interview/history` 接口，在响应中增加 `total_score`、`create_time`、`difficulty` 字段。扩展后只需修改 hubPage 的数据映射逻辑即可。

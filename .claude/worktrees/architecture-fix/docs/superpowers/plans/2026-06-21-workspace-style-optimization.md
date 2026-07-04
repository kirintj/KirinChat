# Workspace 样式结构优化实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 workspace 从独立顶级路由改为 index.vue 的子路由，复用统一的 ai-nav + 左侧菜单布局，使样式与 homepage 保持一致。

**Architecture:** workspace.vue 移除自有顶栏，改用 index.vue 的 ai-nav + 左侧菜单。taskGraph 和 defaultPage 作为 workspace 子路由，共享会话列表 sidebar。所有硬编码颜色替换为 CSS 变量。

**Tech Stack:** Vue 3 + Vue Router + SCSS + CSS Variables

---

## 文件结构

| 文件 | 改动类型 | 职责 |
|------|---------|------|
| `src/frontend/src/router/index.ts` | 修改 | 路由结构：workspace 移入 `/` 子路由 |
| `src/frontend/src/pages/workspace/workspace.vue` | 修改 | 移除顶栏，简化布局，CSS 变量替换 |
| `src/frontend/src/pages/workspace/taskGraphPage/taskGraphPage.vue` | 修改 | `height: 100vh` → `100%` |
| `src/frontend/src/pages/workspace/defaultPage/defaultPage.vue` | 修改 | 硬编码颜色 → CSS 变量 |

---

### Task 1: 路由结构变更

**Files:**
- Modify: `src/frontend/src/router/index.ts`

将 workspace 从独立顶级路由移入 `/` 路由的 children 数组，taskGraph 作为 workspace 的子路由。

- [ ] **Step 1: 修改路由结构**

在 `src/frontend/src/router/index.ts` 中，执行以下变更：

1. 删除原来的顶级 workspace 路由（第 50-68 行）
2. 删除原来的顶级 taskGraphPage 路由（第 69-76 行）
3. 在 `/` 路由的 children 数组末尾添加 workspace 路由（含 taskGraph 子路由）

将以下代码块：
```typescript
{
    path: '/workspace',
    name: 'workspace',
    component: Workspace,
    meta: {
      requiresAuth: true
    },
    children: [
      {
        path: '',
        name: 'workspaceDefaultPage',
        component: WorkspaceDefaultPage,
      },
      {
        path: 'workspacePage',
        name: 'workspacePage',
        component: WorkspacePage,
      }
    ]
  },
  {
    path: '/workspace/taskGraph',
    name: 'taskGraphPage',
    component: TaskGraphPage,
    meta: {
      requiresAuth: true
    }
  },
```

替换为（不保留为顶级路由），并在 `/` 路由的 children 数组中（在 dashboard 路由之后）添加：

```typescript
{
    path: '/workspace',
    name: 'workspace',
    component: Workspace,
    meta: {
      requiresAuth: true,
      current: 'workspace'
    },
    children: [
      {
        path: '',
        name: 'workspaceDefaultPage',
        component: WorkspaceDefaultPage,
      },
      {
        path: 'workspacePage',
        name: 'workspacePage',
        component: WorkspacePage,
      },
      {
        path: 'taskGraph',
        name: 'taskGraphPage',
        component: TaskGraphPage,
      }
    ]
  },
```

关键点：
- `taskGraph` 使用相对路径（不带前导 `/`），因为它是 workspace 的子路由，实际 URL 仍为 `/workspace/taskGraph`
- 添加 `meta: { current: 'workspace' }` 确保 index.vue 左侧菜单正确高亮"工作台"项
- 保留所有 children 的 `name` 不变，确保 `selectSession` 函数中的路由跳转不受影响

- [ ] **Step 2: 验证路由结构**

启动开发服务器，访问以下 URL 确认路由正常：
- `/workspace` — 应显示 workspace 布局（当前仍有独立顶栏）
- `/workspace/taskGraph` — 应显示 taskGraph 页面
- 左侧菜单"工作台"项应正确高亮

- [ ] **Step 3: Commit**

```bash
git add src/frontend/src/router/index.ts
git commit -m "refactor: move workspace routes under index layout"
```

---

### Task 2: workspace.vue 移除顶栏，简化布局

**Files:**
- Modify: `src/frontend/src/pages/workspace/workspace.vue`

移除 workspace 自有的顶部导航栏（workspace-nav），保留会话列表 sidebar 和 content 区域。

- [ ] **Step 1: 移除顶栏相关的 import 和变量**

在 `<script setup>` 中，删除以下 import（第 6-13 行的图标 import 中，仅保留 `workspaceIcon` 和 `applicationCenterIcon`，因为会话列表的"应用中心"按钮用到了）：

删除：
```typescript
import dialogIcon from '../../assets/dialog.svg'
import robotIcon from '../../assets/robot.svg'
import pluginIcon from '../../assets/plugin.svg'
import knowledgeIcon from '../../assets/knowledge.svg'
import modelIcon from '../../assets/model.svg'
import mcpIcon from '../../assets/mcp.svg'
```

保留（会话列表不需要这些，但 workspace.vue 的 script 中没有直接用到这些图标，只在 template 的顶栏中用到，后面会删除）：
- `workspaceIcon` — 不需要了（template 中不使用）
- `applicationCenterIcon` — 不需要了

实际上，检查 template 可以发现这些图标 import 仅在 `appCenterColumns` 中使用。删除所有图标 import：

```typescript
// 删除以下 import
import workspaceIcon from '../../assets/workspace.svg'
import applicationCenterIcon from '../../assets/application-center.svg'
import dialogIcon from '../../assets/dialog.svg'
import robotIcon from '../../assets/robot.svg'
import pluginIcon from '../../assets/plugin.svg'
import knowledgeIcon from '../../assets/knowledge.svg'
import modelIcon from '../../assets/model.svg'
import mcpIcon from '../../assets/mcp.svg'
```

同时删除不再需要的 import：
```typescript
// 删除（index.vue 已处理用户信息）
import { useUserStore } from '../../store/user'
import { logoutAPI, getUserInfoAPI } from '../../apis/auth'
```

- [ ] **Step 2: 移除顶栏相关的 script 逻辑**

删除以下变量和函数（它们只服务于顶栏用户菜单和应用中心下拉）：

```typescript
// 删除
const userStore = useUserStore()

// 删除
const showUserMenu = ref(false)
const userMenuRef = ref<HTMLElement | null>(null)

// 删除
const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
}

// 删除
const closeUserMenu = () => {
  showUserMenu.value = false
}

// 删除
const handleUserCommand = async (command: string) => { ... }

// 删除
const handleLogout = async () => { ... }

// 删除
const handleAvatarError = (event: Event) => { ... }

// 删除
const goToHomepage = () => { ... }

// 删除
const goToWorkspace = () => { ... }

// 删除
const showAppCenterMenu = ref(false)
let appCenterHoverTimer: any = null

// 删除
const openAppCenterMenu = () => { ... }

// 删除
const closeAppCenterMenu = () => { ... }

// 删除
const appCenterColumns = ref([...])

// 删除
const isWorkspaceActive = computed(...)
const isAppCenterActive = computed(...)
```

同时删除 onMounted 中的用户信息获取逻辑（index.vue 已处理）：
```typescript
// 删除 onMounted 中的这段
userStore.initUserState()
if (userStore.isLoggedIn && userStore.userInfo && !userStore.userInfo.avatar) {
  try {
    const response = await getUserInfoAPI(userStore.userInfo.id)
    ...
  } catch (error) {
    ...
  }
}
```

删除 onMounted 中的 `document.addEventListener('click', handleOutsideClick)` 和 onBeforeUnmount 中的 `document.removeEventListener('click', handleOutsideClick)`，以及 `handleOutsideClick` 函数。

删除不再需要的 import：
```typescript
import { useRoute } from 'vue-router'
const route = useRoute()
```

- [ ] **Step 3: 简化 template**

将整个 template 替换为以下内容（移除顶栏，保留会话列表和 content）：

```vue
<template>
  <div class="workspace-container">
    <!-- 左侧边栏：会话列表 -->
    <div class="sidebar">
      <!-- 应用中心按钮 -->
      <div class="create-section">
        <button @click="router.push('/homepage')" class="create-btn">
          <img src="../../assets/application-center.svg" width="18" height="18" />
          <span>应用中心</span>
        </button>
      </div>

      <!-- 会话列表 -->
      <div class="session-list">
        <!-- 加载状态 -->
        <div v-if="loading" class="loading-state">
          <div class="loading-icon">⏳</div>
          <div class="loading-text">正在加载会话列表...</div>
        </div>

        <!-- 空状态 -->
        <div v-else-if="sessions.length === 0" class="empty-state">
          <img src="../../assets/workspace-session.svg" alt="暂无会话" class="empty-icon-img" />
          <div class="empty-text">暂无会话记录</div>
        </div>

        <!-- 会话卡片 -->
        <div
          v-for="session in sessions"
          :key="session.sessionId"
          :class="['session-card', { active: selectedSession === session.sessionId }]"
          @click="selectSession(session.sessionId)"
        >
          <div class="session-icon">
            <img src="../../assets/workspace-session.svg" width="18" height="18" />
          </div>
          <div class="session-info">
            <div class="session-title">{{ session.title }}</div>
            <div class="session-time">{{ formatTime(session.createTime) }}</div>
          </div>
          <button
            class="delete-btn"
            @click="deleteSession(session.sessionId, $event)"
            title="删除会话"
          >
            ×
          </button>
        </div>
      </div>
    </div>

    <!-- 右侧内容区域 -->
    <div class="content">
      <router-view />
    </div>
  </div>
</template>
```

- [ ] **Step 4: 替换所有样式为 CSS 变量版本**

将整个 `<style>` 块替换为：

```scss
<style lang="scss" scoped>
.workspace-container {
  width: 100%;
  height: 100%;
  display: flex;
  background: var(--color-bg);
}

.sidebar {
  height: 100%;
  width: 280px;
  background: var(--color-bg);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;

  .create-section {
    padding: 16px;
    flex-shrink: 0;

    .create-btn {
      width: 100%;
      height: 44px;
      border-radius: var(--radius-sm);
      background: var(--color-bg);
      color: var(--color-primary);
      border: 1px solid var(--color-border);
      cursor: pointer;
      font-size: 14px;
      font-weight: 500;
      font-family: inherit;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      transition: all var(--duration-fast) var(--easing);

      &:hover {
        border-color: var(--color-primary);
        background: var(--color-primary-bg);
      }
    }
  }

  .session-list {
    flex: 1;
    padding: 0 8px 8px;
    overflow-y: auto;

    .loading-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 200px;

      .loading-icon {
        font-size: 32px;
        margin-bottom: 12px;
        animation: spin 1s linear infinite;
      }

      .loading-text {
        font-size: var(--font-size-sm);
        color: var(--color-text-secondary);
      }
    }

    .empty-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 200px;

      .empty-icon-img {
        width: 48px;
        height: 48px;
        margin-bottom: 12px;
        opacity: 0.4;
      }

      .empty-text {
        font-size: var(--font-size-base);
        color: var(--color-text-tertiary);
      }
    }

    .session-card {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 12px;
      margin-bottom: 4px;
      background: var(--color-bg);
      border: 1px solid transparent;
      border-radius: var(--radius-md);
      cursor: pointer;
      transition: all var(--duration-fast) var(--easing);
      position: relative;

      &:hover {
        background: var(--color-bg-secondary);
        border-color: var(--color-border);

        .delete-btn {
          opacity: 1;
        }
      }

      &.active {
        background: var(--color-primary-bg);
        border-color: var(--color-primary);
      }

      .session-icon {
        width: 28px;
        height: 28px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--color-primary-bg);
        border-radius: var(--radius-sm);
        flex-shrink: 0;
      }

      .session-info {
        flex: 1;
        min-width: 0;

        .session-title {
          font-size: var(--font-size-base);
          font-weight: 500;
          color: var(--color-text-primary);
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
          margin-bottom: 2px;
        }

        .session-time {
          font-size: var(--font-size-xs);
          color: var(--color-text-tertiary);
        }
      }

      .delete-btn {
        position: absolute;
        top: 6px;
        right: 6px;
        width: 22px;
        height: 22px;
        padding: 0;
        background: var(--color-bg);
        border: 1px solid var(--color-border);
        cursor: pointer;
        border-radius: var(--radius-sm);
        transition: all var(--duration-fast) var(--easing);
        font-size: 14px;
        opacity: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--color-text-secondary);

        &:hover {
          background: var(--color-danger-bg);
          color: var(--color-danger);
          border-color: var(--color-danger);
        }
      }
    }
  }
}

.content {
  flex: 1;
  min-width: 0;
  min-height: 0;
  background: var(--color-bg);
  overflow: hidden;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .sidebar {
    width: 240px;
  }
}

@media (max-width: 480px) {
  .workspace-container {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    height: auto;
    max-height: 240px;
  }
}
</style>
```

- [ ] **Step 5: 验证 workspace 页面**

启动开发服务器，访问 `/workspace`：
- 顶栏应由 index.vue 的 ai-nav 显示（不再是 workspace 自有的渐变顶栏）
- 左侧应有 index.vue 的功能菜单（200px）+ workspace 的会话列表 sidebar（280px）
- 会话卡片的 hover、active、删除功能应正常
- 点击会话应正确跳转

- [ ] **Step 6: Commit**

```bash
git add src/frontend/src/pages/workspace/workspace.vue
git commit -m "refactor: remove workspace nav, use index layout with CSS variables"
```

---

### Task 3: taskGraphPage 高度自适应

**Files:**
- Modify: `src/frontend/src/pages/workspace/taskGraphPage/taskGraphPage.vue`

- [ ] **Step 1: 修改页面容器高度**

在 `src/frontend/src/pages/workspace/taskGraphPage/taskGraphPage.vue` 的 `<style>` 中，找到 `.task-graph-page` 的样式块（约第 1048 行），修改：

```scss
// 原始
.task-graph-page {
  width: 100%;
  height: 100vh;
  background: linear-gradient(135deg, #ffffff 0%, #f0f9ff 50%, #ffffff 100%);
  overflow: hidden;
  position: relative;
```

替换为：

```scss
.task-graph-page {
  width: 100%;
  height: 100%;
  background: var(--color-bg-secondary, #f5f7fb);
  overflow: hidden;
  position: relative;
```

同时找到底部的 UI Refresh Overrides 部分（约第 2211 行），确认 `.task-graph-page` 的 `background: var(--bg)` 覆盖仍然生效。不需要额外修改，因为 `--bg` 变量已在页面内定义。

- [ ] **Step 2: 验证 taskGraph 布局**

访问 `/workspace/taskGraph`（可以直接访问 URL，或从 workspace 会话列表中点击一个灵寻类型的会话）：
- 三列布局应自适应 content 区域高度（不再是全屏）
- 会话列表 sidebar 应正常显示在左侧
- 三列内容不应溢出

- [ ] **Step 3: Commit**

```bash
git add src/frontend/src/pages/workspace/taskGraphPage/taskGraphPage.vue
git commit -m "refactor: taskGraph page height 100vh to 100% for index layout"
```

---

### Task 4: defaultPage CSS 变量替换

**Files:**
- Modify: `src/frontend/src/pages/workspace/defaultPage/defaultPage.vue`

- [ ] **Step 1: 替换页面背景色**

在 `defaultPage.vue` 的 `<style>` 中，找到 `.chat-page` 的样式（约第 689 行）：

```scss
// 原始
.chat-page {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  background: linear-gradient(180deg, #fafbfc 0%, #ffffff 100%);
  padding: 0;
  overflow-y: auto;

  &.chat-active {
    padding: 0;
    overflow: hidden;
    background-color: #f7f8fa;
  }
}
```

替换为：

```scss
.chat-page {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  background: var(--color-bg);
  padding: 0;
  overflow-y: auto;

  &.chat-active {
    padding: 0;
    overflow: hidden;
    background: var(--color-bg-secondary);
  }
}
```

- [ ] **Step 2: 替换输入区域背景色**

找到 `.input-section .input-fixed`（约第 889 行）：

```scss
// 原始
&.input-fixed {
  max-width: 100%;
  padding: 10px 20px 20px 20px;
  background: #f7f8fa;
```

替换为：

```scss
&.input-fixed {
  max-width: 100%;
  padding: 10px 20px 20px 20px;
  background: var(--color-bg-secondary);
```

- [ ] **Step 3: 替换输入框和对话区域的硬编码颜色**

找到 `.input-wrapper`（约第 901 行）：

```scss
// 原始
.input-wrapper {
  background: #ffffff;
  border: 2px solid #e5e7eb;
```

替换为：

```scss
.input-wrapper {
  background: var(--color-bg);
  border: 1px solid var(--color-border);
```

找到 `.chat-conversation`（约第 1406 行）：

```scss
// 原始
background-color: #f7f8fa;
```

替换为：

```scss
background: var(--color-bg-secondary);
```

- [ ] **Step 4: 验证 defaultPage**

访问 `/workspace`（默认显示 defaultPage）：
- 欢迎页面背景应为纯白/统一背景色
- 输入框边框、圆角应与 homepage 风格一致
- 模式选择按钮、下拉菜单应正常工作
- 对话功能应正常（日常模式发消息、灵寻模式跳转 taskGraph）

- [ ] **Step 5: Commit**

```bash
git add src/frontend/src/pages/workspace/defaultPage/defaultPage.vue
git commit -m "refactor: replace hardcoded colors with CSS variables in defaultPage"
```

---

### Task 5: 最终验证与清理

- [ ] **Step 1: 全面功能验证**

逐一检查以下功能，确保无回归：

1. 访问 `/workspace` — 布局正确，会话列表显示，defaultPage 欢迎页正常
2. 点击"应用中心"按钮 — 跳转到 `/homepage`
3. 会话列表加载、选择、删除功能正常
4. 点击会话（simple 模式）— 跳转到 defaultPage 并加载历史
5. 点击会话（lingseek 模式）— 跳转到 taskGraph 三列布局并加载历史
6. 在 defaultPage 发送消息（日常模式）— 流式对话正常
7. 在 defaultPage 选择灵寻模式发送 — 跳转 taskGraph
8. taskGraph 指导手册生成、任务执行、结果接收正常
9. index.vue 左侧菜单"工作台"项高亮正确
10. 顶栏用户菜单（个人资料、退出登录）正常

- [ ] **Step 2: Commit（如有额外修复）**

如果验证过程中发现并修复了问题：

```bash
git add -A
git commit -m "fix: address layout issues from workspace refactor"
```

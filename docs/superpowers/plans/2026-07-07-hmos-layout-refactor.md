# 鸿蒙风格布局重构实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 KirinChat 前端布局重构为 HarmonyOS 设计风格，桌面端采用毛玻璃浮动侧边栏，移动端引入 statusbar + titlebar + bottomtab 三层壳层。

**Architecture:** HAppShell 中心化方案 — HAppShell 通过 provide/inject 向下传递 isMobile 状态，index.vue 根据 isMobile 切换桌面端/移动端两套布局。桌面端侧边栏改为毛玻璃浮动面板，移动端使用已有 HStatusbar/HTitlebar/HBottomTab 壳层组件。

**Tech Stack:** Vue 3 + TypeScript + Composition API + SCSS + HarmonyOS Design Tokens

**Spec:** `docs/superpowers/specs/2026-07-07-hmos-layout-refactor-design.md`

---

## File Structure

| 操作 | 文件 | 职责 |
|------|------|------|
| 新增 | `src/frontend/src/composables/useNavigation.ts` | 导航菜单数据（coreTabs, secondaryItems, allMenuItems） |
| 改造 | `src/frontend/src/components/ui/shell/HAppShell.vue` | 添加 provide('isMobile') |
| 改造 | `src/frontend/src/pages/index.vue` | 主壳层：桌面端毛玻璃侧边栏 + 移动端三层壳层 |
| 改造 | `src/frontend/src/pages/homepage/homepage.vue` | 首页双端适配 |

---

### Task 1: 创建 useNavigation composable

**Files:**
- Create: `src/frontend/src/composables/useNavigation.ts`

- [ ] **Step 1: 创建 composable 文件**

```typescript
// src/frontend/src/composables/useNavigation.ts
export interface NavItem {
  key: string
  label: string
  icon: string
  route: string
}

export const coreTabs: NavItem[] = [
  { key: 'workspace', label: '工作台', icon: 'workspace', route: '/workspace' },
  { key: 'homepage', label: '探索', icon: 'explore', route: '/homepage' },
  { key: 'conversation', label: '会话', icon: 'dialog', route: '/conversation' },
  { key: 'agent', label: '智能体', icon: 'robot', route: '/agent' },
]

export const secondaryItems: NavItem[] = [
  { key: 'mcp-server', label: 'MCP', icon: 'mcp', route: '/mcp-server' },
  { key: 'knowledge', label: '知识库', icon: 'knowledge', route: '/knowledge' },
  { key: 'tool', label: '工具', icon: 'plugin', route: '/tool' },
  { key: 'agent-skill', label: 'Skill', icon: 'skill', route: '/agent-skill' },
  { key: 'interview', label: '面试', icon: 'skill', route: '/interview' },
  { key: 'model', label: '模型', icon: 'model', route: '/model' },
  { key: 'dashboard', label: '数据看板', icon: 'dashboard', route: '/dashboard' },
]

export const allMenuItems: NavItem[] = [...coreTabs, ...secondaryItems]

export function getTitleByRoute(routePath: string): string {
  const item = allMenuItems.find(m => routePath.startsWith(m.route))
  return item?.label || 'KirinChat'
}
```

- [ ] **Step 2: 验证 TypeScript 编译**

Run: `cd src/frontend && npx vue-tsc --noEmit 2>&1 | head -20`
Expected: 无新增错误

- [ ] **Step 3: Commit**

```bash
git add src/frontend/src/composables/useNavigation.ts
git commit -m "feat: add useNavigation composable for shared nav data"
```

---

### Task 2: 修改 HAppShell 支持 provide/inject

**Files:**
- Modify: `src/frontend/src/components/ui/shell/HAppShell.vue`

当前 HAppShell 通过 slot prop 传递 isMobile，但 index.vue 作为 router-view 的子组件无法接收 slot prop。需要额外通过 provide/inject 机制传递。

- [ ] **Step 1: 修改 HAppShell.vue script 部分**

在 `<script setup>` 中添加 `provide`：

```vue
<script setup lang="ts">
import { ref, onMounted, onUnmounted, provide } from 'vue'

const BREAKPOINT = 768
const isMobile = ref(window.innerWidth < BREAKPOINT)

const onResize = () => {
  isMobile.value = window.innerWidth < BREAKPOINT
}

onMounted(() => window.addEventListener('resize', onResize))
onUnmounted(() => window.removeEventListener('resize', onResize))

provide('isMobile', isMobile)
</script>
```

- [ ] **Step 2: 验证编译**

Run: `cd src/frontend && npx vue-tsc --noEmit 2>&1 | head -20`
Expected: 无新增错误

- [ ] **Step 3: Commit**

```bash
git add src/frontend/src/components/ui/shell/HAppShell.vue
git commit -m "feat: HAppShell provide isMobile for descendant injection"
```

---

### Task 3: 重构 index.vue — 提取逻辑 + 桌面端侧边栏改造

**Files:**
- Modify: `src/frontend/src/pages/index.vue`

这是最大的一个任务。分步骤改造 index.vue：先提取导航数据到 composable，再改造桌面端侧边栏为毛玻璃浮动面板。

- [ ] **Step 1: 替换 script 部分**

将 index.vue 的 `<script setup>` 替换为以下内容，使用 useNavigation composable 并 inject isMobile：

```vue
<script setup lang="ts">
import { onMounted, ref, watch, inject, type Ref } from "vue"
import { useRouter, useRoute } from "vue-router"
import { HMessage, HIcon, HDrawer } from '@/components/ui'
import { useAgentCardStore } from "../store/agent_card"
import { useUserStore } from "../store/user"
import { getAgentsAPI } from "../apis/agent"
import { logoutAPI, getUserInfoAPI } from "../apis/auth"
import { allMenuItems, coreTabs, secondaryItems, getTitleByRoute } from "../composables/useNavigation"

const agentCardStore = useAgentCardStore()
const userStore = useUserStore()
const route = useRoute()
const router = useRouter()
const isMobile = inject<Ref<boolean>>('isMobile', ref(false))

const sidebarCollapsed = ref(false)
const toggleSidebar = () => { sidebarCollapsed.value = !sidebarCollapsed.value }

const showUserMenu = ref(false)
const toggleUserMenu = () => { showUserMenu.value = !showUserMenu.value }

const showMoreDrawer = ref(false)

const current = ref(route.meta.current as string)

const goCurrent = (item: string) => {
  const routes: Record<string, string> = {}
  allMenuItems.forEach(m => { routes[m.key] = m.route })
  router.push(routes[item] || "/")
}

const handleUserCommand = async (command: string) => {
  switch (command) {
    case 'profile': router.push('/profile'); break
    case 'settings': router.push('/configuration'); break
    case 'logout': await handleLogout(); break
  }
}

const handleLogout = async () => {
  try { await logoutAPI() } catch (error) { console.error('调用登出接口失败:', error) }
  userStore.logout()
  HMessage.success('已退出登录')
  router.push('/login')
}

const handleAvatarError = (event: Event) => {
  const target = event.target as HTMLImageElement
  if (target) target.src = '/user.svg'
}

const godefault = () => {
  agentCardStore.clear()
  router.push("/")
}

onMounted(async () => {
  userStore.initUserState()
  if (userStore.isLoggedIn && userStore.userInfo && !userStore.userInfo.avatar) {
    try {
      const response = await getUserInfoAPI(userStore.userInfo.id)
      if (response.data.status_code === 200 && response.data.data) {
        const userData = response.data.data
        userStore.updateUserInfo({
          avatar: userData.user_avatar || userData.avatar || '/user.svg',
          description: userData.user_description || userData.description
        })
      }
    } catch (error) { console.error('初始化时获取用户信息失败:', error) }
  }
})

watch(route, (val) => { current.value = route.meta.current as string }, { immediate: true })

const mobileTitle = computed(() => getTitleByRoute(route.path))
const mobileTitleVariant = computed(() => route.path.startsWith('/homepage') ? 'big' : 'normal')
</script>
```

注意：需要在 import 中添加 `computed`。完整 import 行：

```typescript
import { onMounted, ref, watch, inject, computed, type Ref } from "vue"
```

- [ ] **Step 2: 替换 template 部分**

将 index.vue 的 `<template>` 替换为以下内容：

```vue
<template>
  <div class="ai-body" :class="{ 'ai-body--mobile': isMobile }">
    <!-- 桌面端布局 -->
    <template v-if="!isMobile">
      <div class="ai-desktop">
        <div class="sidebar" :class="{ collapsed: sidebarCollapsed }">
          <!-- 品牌区 -->
          <div class="sidebar-brand">
            <div class="brand-logo" @click="godefault">
              <img src="../assets/mars-agent.svg" alt="KirinChat" class="brand-logo-img" />
            </div>
            <span v-if="!sidebarCollapsed" class="brand-name" @click="godefault">KirinChat</span>
          </div>

          <div class="sidebar-divider" />

          <!-- 菜单 -->
          <div class="sidebar-menu">
            <div
              v-for="item in allMenuItems"
              :key="item.index"
              class="menu-item"
              :class="{ active: current === item.key }"
              @click="goCurrent(item.key)"
              :title="sidebarCollapsed ? item.label : ''"
            >
              <div class="menu-icon">
                <HIcon :svg="item.icon" :size="18" />
              </div>
              <span v-if="!sidebarCollapsed" class="menu-text">{{ item.label }}</span>
            </div>
          </div>

          <div class="sidebar-divider" />

          <!-- 用户区 -->
          <div class="sidebar-user">
            <div class="user-dropdown" @click="toggleUserMenu">
              <div class="user-avatar">
                <img
                  :src="userStore.userInfo?.avatar || '/user.svg'"
                  alt="用户头像"
                  @error="handleAvatarError"
                  referrerpolicy="no-referrer"
                />
              </div>
              <span v-if="!sidebarCollapsed" class="user-name">{{ userStore.userInfo?.name || '用户' }}</span>
            </div>
            <div v-if="showUserMenu" class="user-dropdown-menu">
              <div class="user-dropdown-item" @click="handleUserCommand('profile')">个人资料</div>
              <div class="user-dropdown-item user-dropdown-item--danger" @click="handleUserCommand('logout')">退出登录</div>
            </div>
          </div>

          <!-- 折叠按钮 -->
          <div class="sidebar-toggle" @click="toggleSidebar">
            <span class="toggle-icon">{{ sidebarCollapsed ? '›' : '‹' }}</span>
          </div>
        </div>

        <div class="content">
          <router-view />
        </div>
      </div>
    </template>

    <!-- 移动端布局 -->
    <template v-else>
      <div class="ai-mobile">
        <HStatusbar theme="light" />
        <HTitlebar
          :title="mobileTitle"
          :variant="mobileTitleVariant"
        >
          <template #actions>
            <div class="more-btn" @click="showMoreDrawer = true">
              <HIcon svg="plugin" :size="20" />
            </div>
          </template>
        </HTitlebar>

        <div class="mobile-content">
          <router-view />
        </div>

        <HBottomTab
          variant="4"
          :items="bottomTabItems"
          :active-key="currentTabKey"
          @update:active-key="onTabChange"
        />
      </div>

      <!-- 二级入口 Drawer -->
      <HDrawer v-model="showMoreDrawer" title="更多功能" size="300px">
        <div class="more-grid">
          <div
            v-for="item in secondaryItems"
            :key="item.key"
            class="more-grid-item"
            @click="goCurrent(item.key); showMoreDrawer = false"
          >
            <HIcon :svg="item.icon" :size="28" />
            <span class="more-grid-label">{{ item.label }}</span>
          </div>
        </div>
      </HDrawer>
    </template>
  </div>
</template>
```

需要在 script 中补充 `bottomTabItems`、`currentTabKey`、`onTabChange` 以及导入壳层组件。在 script setup 中添加：

```typescript
import { HStatusbar, HTitlebar, HBottomTab } from '@/components/ui/shell'

const bottomTabItems = coreTabs.map(t => ({
  key: t.key,
  label: t.label,
  icon: t.icon,
}))

const currentTabKey = computed(() => {
  const match = coreTabs.find(t => route.path.startsWith(t.route))
  return match?.key || 'workspace'
})

const onTabChange = (key: string) => {
  goCurrent(key)
}
```

- [ ] **Step 3: 替换 style 部分**

将 index.vue 的 `<style lang="scss" scoped>` 替换为以下内容：

```vue
<style lang="scss" scoped>
.ai-body {
  overflow: hidden;
  width: 100%;
  height: 100vh;
}

/* ========= 桌面端 ========= */
.ai-desktop {
  display: flex;
  width: 100%;
  height: 100%;
  padding: 16px;
  gap: 16px;
  box-sizing: border-box;
  background: linear-gradient(135deg, #e8edf5 0%, #f0f2f5 100%);
}

.sidebar {
  width: 200px;
  height: 100%;
  border-radius: 28px;
  padding: 16px 12px;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(80px);
  -webkit-backdrop-filter: blur(80px);
  box-shadow: 0 4px 48px rgba(0, 0, 0, 0.08),
              0 4px 8px rgba(0, 0, 0, 0.25);
  transition: width 0.2s ease;

  &.collapsed {
    width: 64px;
    padding: 16px 8px;
  }
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px 16px;

  .brand-logo {
    width: 32px;
    height: 32px;
    flex-shrink: 0;
    cursor: pointer;

    .brand-logo-img {
      width: 100%;
      height: 100%;
      border-radius: 10px;
      object-fit: cover;
    }
  }

  .brand-name {
    font-size: 15px;
    font-weight: 700;
    color: var(--harmony-font-primary);
    cursor: pointer;
    white-space: nowrap;
  }
}

.sidebar-divider {
  height: 1px;
  background: rgba(0, 0, 0, 0.08);
  margin: 0 8px 12px;
  flex-shrink: 0;
}

.sidebar-menu {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 4px;

  .menu-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 14px;
    border-radius: 14px;
    cursor: pointer;
    color: var(--harmony-font-secondary);
    font-size: var(--harmony-font-size-body-m);
    transition: all 0.15s ease;

    &:hover {
      background: var(--harmony-interactive-hover);
    }

    &:active {
      background: var(--harmony-interactive-pressed);
    }

    &.active {
      background: rgba(10, 89, 247, 0.098);
      color: var(--harmony-brand);

      .menu-icon {
        color: var(--harmony-brand);
      }
    }

    .menu-icon {
      width: 20px;
      height: 20px;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }

    .menu-text {
      white-space: nowrap;
      overflow: hidden;
    }
  }
}

.sidebar-user {
  position: relative;
  padding: 8px 12px;
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;

  .user-dropdown {
    display: flex;
    align-items: center;
    gap: 10px;
    cursor: pointer;
    width: 100%;
  }

  .user-avatar img {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    object-fit: cover;
    flex-shrink: 0;
  }

  .user-name {
    font-size: var(--harmony-font-size-body-s);
    color: var(--harmony-font-secondary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}

.user-dropdown-menu {
  position: absolute;
  bottom: 100%;
  left: 8px;
  margin-bottom: 8px;
  min-width: 140px;
  background: var(--harmony-comp-background-primary);
  border: 1px solid var(--harmony-comp-divider);
  border-radius: 14px;
  box-shadow: var(--harmony-shadow-md);
  z-index: var(--z-dropdown);
  overflow: hidden;

  .user-dropdown-item {
    padding: 10px 16px;
    font-size: var(--harmony-font-size-body-m);
    color: var(--harmony-font-primary);
    cursor: pointer;
    transition: background 0.15s ease;

    &:hover {
      background: var(--harmony-interactive-hover);
    }

    &--danger {
      color: var(--harmony-warning);
    }
  }
}

.sidebar-toggle {
  text-align: center;
  padding: 8px 0;
  cursor: pointer;
  flex-shrink: 0;

  .toggle-icon {
    display: inline-block;
    width: 24px;
    height: 24px;
    line-height: 24px;
    background: rgba(0, 0, 0, 0.05);
    border-radius: 8px;
    font-size: var(--harmony-font-size-body-s);
    color: var(--harmony-font-secondary);
  }
}

.content {
  flex: 1;
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(40px);
  -webkit-backdrop-filter: blur(40px);
  box-shadow: 0 2px 16px rgba(0, 0, 0, 0.04);
  overflow-y: auto;
}

/* ========= 移动端 ========= */
.ai-mobile {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--harmony-comp-background-primary);
  overflow: hidden;
}

.more-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  cursor: pointer;
  color: var(--harmony-font-secondary);
  transition: background 0.15s ease;

  &:hover {
    background: var(--harmony-interactive-hover);
  }
}

.mobile-content {
  flex: 1;
  overflow-y: auto;
  padding-bottom: 100px; /* 预留 bottomtab 安全区 */
}

.more-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;

  .more-grid-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 20px 12px;
    border-radius: 16px;
    background: var(--harmony-comp-background-tertiary);
    cursor: pointer;
    transition: all 0.15s ease;

    &:hover {
      background: var(--harmony-interactive-hover);
    }

    &:active {
      background: var(--harmony-interactive-pressed);
    }

    .more-grid-label {
      font-size: var(--harmony-font-size-body-s);
      color: var(--harmony-font-primary);
      font-weight: 500;
    }
  }
}
</style>
```

- [ ] **Step 4: 验证编译**

Run: `cd src/frontend && npx vue-tsc --noEmit 2>&1 | head -30`
Expected: 无新增类型错误

- [ ] **Step 5: Commit**

```bash
git add src/frontend/src/pages/index.vue
git commit -m "refactor(layout): HarmonyOS glass sidebar + mobile shell in index.vue"
```

---

### Task 4: 重构 homepage.vue — 桌面端样式更新

**Files:**
- Modify: `src/frontend/src/pages/homepage/homepage.vue`

- [ ] **Step 1: 更新搜索框和卡片样式**

修改 `<style>` 部分，将搜索框和卡片的圆角、边框、背景对齐鸿蒙风格。保留 `<script>` 和 `<template>` 不变。

替换 `<style>` 为：

```vue
<style lang="scss" scoped>
.homepage {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 24px;
  padding: 0 24px;
  background: transparent; /* 透明，继承父级毛玻璃背景 */
}

/* Logo */
.logo-section {
  display: flex;
  align-items: center;
  gap: 12px;

  .logo {
    width: 48px;
    height: 48px;
  }

  .brand-name {
    font-size: var(--harmony-font-size-title-s);
    font-weight: 700;
    color: var(--harmony-font-primary);
    margin: 0;
  }
}

/* 搜索框 */
.search-section {
  width: 100%;
  max-width: 500px;

  .search-box {
    background: rgba(255, 255, 255, 0.8);
    border: 1px solid rgba(0, 0, 0, 0.06);
    border-radius: 20px;
    padding: 16px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);

    &:focus-within {
      border-color: var(--harmony-brand);
    }
  }

  .search-input {
    width: 100%;
    min-height: 80px;
    border: none;
    background: transparent;
    padding: 8px;
    font-size: var(--harmony-font-size-body-m);
    line-height: 1.6;
    color: var(--harmony-font-primary);
    resize: none;
    font-family: inherit;

    &::placeholder {
      color: var(--harmony-font-tertiary);
    }
  }

  .search-footer {
    display: flex;
    justify-content: flex-end;
    padding-top: 8px;

    .send-btn {
      width: 36px;
      height: 36px;
      background: var(--harmony-brand);
      color: white;
      border: none;
      border-radius: 50%;
      font-size: var(--harmony-font-size-body-m);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;

      &:hover {
        opacity: 0.9;
      }
    }
  }
}

/* 案例 */
.examples-section {
  width: 100%;
  max-width: 560px;

  .examples-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }

  .example-card {
    background: rgba(255, 255, 255, 0.7);
    border: 1px solid rgba(0, 0, 0, 0.06);
    border-radius: 16px;
    padding: 16px;
    cursor: pointer;
    transition: all 0.15s ease;

    &:hover {
      border-color: var(--harmony-brand);
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
    }

    &:active {
      background: var(--harmony-interactive-pressed);
    }
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
  }

  .card-title {
    font-size: var(--harmony-font-size-body-m);
    font-weight: 600;
    color: var(--harmony-font-primary);
    margin: 0;
  }

  .card-tag {
    font-size: var(--harmony-font-size-body-s);
    color: var(--harmony-font-tertiary);
    background: rgba(0, 0, 0, 0.05);
    padding: 2px 8px;
    border-radius: 8px;
  }

  .card-desc {
    font-size: var(--harmony-font-size-body-s);
    color: var(--harmony-font-secondary);
    line-height: 1.5;
    margin: 0;
  }
}

/* 移动端适配 */
@media (max-width: 768px) {
  .homepage {
    justify-content: flex-start;
    padding-top: 16px;
    gap: 16px;
  }

  .search-section {
    max-width: 100%;
  }

  .examples-section {
    max-width: 100%;
  }
}
</style>
```

- [ ] **Step 2: Commit**

```bash
git add src/frontend/src/pages/homepage/homepage.vue
git commit -m "refactor(homepage): HarmonyOS glass card styles + mobile adaptation"
```

---

### Task 5: 验证并修复编译错误

**Files:**
- 可能修改: `src/frontend/src/pages/index.vue` (修复导入/类型问题)

- [ ] **Step 1: 运行 TypeScript 检查**

Run: `cd src/frontend && npx vue-tsc --noEmit 2>&1`
Expected: 可能有少量类型错误需要修复

- [ ] **Step 2: 修复发现的错误**

常见问题：
- `allMenuItems` 中使用 `.key` 而模板中写 `.index` → 统一为 `.key`
- `HStatusbar`/`HTitlebar`/`HBottomTab` 的导入路径
- `computed` 未导入

根据实际错误逐个修复。

- [ ] **Step 3: 再次验证编译通过**

Run: `cd src/frontend && npx vue-tsc --noEmit 2>&1`
Expected: 无错误

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "fix: resolve type errors after layout refactor"
```

---

### Task 6: 启动开发服务器验证

- [ ] **Step 1: 启动 dev server**

Run: `cd src/frontend && npm run dev`
Expected: 服务器启动成功

- [ ] **Step 2: 验证桌面端**

在浏览器中打开 http://localhost:5173（或实际端口），检查：
- 侧边栏显示毛玻璃浮动面板效果
- 品牌名和 logo 显示在侧边栏顶部
- 菜单项点击可导航，激活态为品牌蓝淡底
- 用户头像和下拉菜单在侧边栏底部
- 内容区为毛玻璃卡片
- 侧边栏折叠/展开功能正常

- [ ] **Step 3: 验证移动端**

缩小浏览器窗口到 768px 以下，或使用开发者工具切换到移动视图，检查：
- 显示 HStatusbar 状态栏
- 显示 HTitlebar 标题栏，标题随路由变化
- 显示 HBottomTab 底部导航栏（4 tab）
- 点击 bottomtab 可切换路由
- 点击 titlebar 右侧"更多"按钮可打开 drawer
- drawer 中展示 7 个二级入口
- 内容区可正常滚动，不被壳层遮挡

- [ ] **Step 4: 修复发现的 UI 问题**

根据实际验证结果修复样式或逻辑问题。

- [ ] **Step 5: 最终 Commit**

```bash
git add -A
git commit -m "fix: UI polish after visual verification"
```

---

### Task 7: 代码清理

- [ ] **Step 1: 移除 index.vue 中不再使用的旧代码**

检查并清理：
- 旧的 `showAppCenterMenu` / `appCenterHoverTimer` / `appCenterColumns` 逻辑（如仍存在）
- 旧的 `itemName` ref
- 不再需要的 import

- [ ] **Step 2: 确认无遗留 dead code**

Run: `cd src/frontend && npx vue-tsc --noEmit 2>&1`
Expected: 无错误

- [ ] **Step 3: 最终 Commit**

```bash
git add -A
git commit -m "chore: clean up dead code after layout refactor"
```

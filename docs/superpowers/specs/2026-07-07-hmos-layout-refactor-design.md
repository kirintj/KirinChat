# 鸿蒙风格布局重构设计文档

## 概述

将 KirinChat 前端布局重构为 HarmonyOS 设计风格，采用响应式双端策略：桌面端保留侧边栏但做鸿蒙风格大改，移动端引入完整三层系统壳层（statusbar + titlebar + bottomtab）。

### 范围

本次仅重构壳层布局 + 首页（homepage），验证方案可行后再推广到其他页面。

### 参考规范

- hmos-design-visual-mobile SKILL.md（鸿蒙移动端视觉还原规范）
- references/3.component/bottomtab.md、toolbar.md、list.md、titlebar.md、statusbar.md
- references/2.theme/harmony-tokens.css

---

## 1. 整体架构

### 1.1 方案选择

采用 **HAppShell 中心化改造** 方案：扩展现有 HAppShell 组件，在模板中通过 `v-if="isMobile"` 切换桌面端和移动端两套布局。

### 1.2 文件改动清单

| 操作 | 文件 | 说明 |
|------|------|------|
| 改造 | `src/pages/index.vue` | 主壳层，新增移动端布局分支 + 桌面端鸿蒙风格侧边栏 |
| 改造 | `src/pages/homepage/homepage.vue` | 首页双端适配 |
| 新增 | `src/composables/useNavigation.ts` | 导航菜单数据提取为共享 composable |
| 复用 | `components/ui/shell/HStatusbar.vue` | 已有，直接使用 |
| 复用 | `components/ui/shell/HTitlebar.vue` | 已有，直接使用 |
| 复用 | `components/ui/shell/HBottomTab.vue` | 已有，需微调适配 |
| 复用 | `components/ui/shell/HAppShell.vue` | 已有，提供 isMobile |

### 1.3 数据流

```
HAppShell.vue
│  提供: isMobile (ref<boolean>)
│  ↓ slot props
▼
index.vue
│  消费: isMobile → v-if 切换布局
│  依赖: useNavigation() → menuItems, activeKey
│  ↓ props
├── 桌面端分支
│   ├── .sidebar (毛玻璃浮动面板)
│   │   ├── 品牌名 + logo
│   │   ├── menuItems 循环
│   │   └── 用户头像 + 菜单
│   └── .content (router-view, 毛玻璃卡片)
│
└── 移动端分支
    ├── HStatusbar (36px)
    ├── HTitlebar (title, variant, actions slot)
    ├── .mobile-content (router-view, 可滚动)
    └── HBottomTab (4 tab, activeKey 双向绑定)
```

### 1.4 导航映射

**BottomTab 4 核心 tab：**

| Tab | 路由 | 图标 |
|-----|------|------|
| 工作台 | /workspace | workspace |
| 探索 | /homepage | explore |
| 会话 | /conversation | dialog |
| 智能体 | /agent | robot |

**7 个二级入口**（通过 titlebar 右侧"更多"按钮打开 HDrawer 网格菜单）：

MCP、知识库、工具、Skill、面试、模型、数据看板

---

## 2. 桌面端改造：鸿蒙风格侧边栏

### 2.1 设计目标

保留侧边栏结构，全面对齐鸿蒙视觉语言：毛玻璃材质、大圆角、品牌色激活态、list 交互状态。

### 2.2 移除顶部导航栏

现有的 `.ai-nav`（顶栏）移除，品牌名和用户头像融入侧边栏。

### 2.3 侧边栏容器 (.sidebar)

| 属性 | 改造前 | 改造后 |
|------|--------|--------|
| 圆角 | level6 (12px) | 28px（对齐 toolbar 规范） |
| 背景 | solid tertiary | `rgba(255,255,255,0.4)` + `backdrop-filter: blur(80px)` |
| 阴影 | 无 | `0 4px 48px rgba(0,0,0,0.08)` + `0 4px 8px rgba(0,0,0,0.25)` |
| 边框 | 1px solid divider | 无边框（毛玻璃材质自带层次） |
| 布局 | 贴边 | 浮动（16px margin，与内容区间距 16px） |
| 宽度 | 200px | 200px（不变） |

### 2.4 菜单项 (.menu-item)

| 属性 | 改造前 | 改造后 |
|------|--------|--------|
| 圆角 | level6 (12px) | 14px |
| 激活态背景 | solid bg + shadow | `rgba(10,89,247,0.098)` 品牌色淡底 |
| 激活色 | font-primary | `--harmony-brand` (rgba(10,89,247,1)) |
| hover | solid bg | `rgba(0,0,0,0.047)` (list 交互态) |
| pressed | 无 | `rgba(0,0,0,0.098)` (list 交互态) |

### 2.5 侧边栏结构

```
.sidebar (毛玻璃浮动面板)
├── 品牌区：logo + "KirinChat" 标题
├── divider
├── 菜单项列表（flex: 1, overflow-y: auto）
│   ├── 工作台 (active → brand 色)
│   ├── 探索
│   ├── 会话
│   ├── 智能体
│   ├── MCP
│   ├── 知识库
│   ├── 工具
│   ├── Skill
│   ├── 面试
│   ├── 模型
│   └── 数据看板
├── divider
└── 用户区：头像 + 用户名 + 下拉菜单
```

### 2.6 内容区 (.content)

| 属性 | 改造前 | 改造后 |
|------|--------|--------|
| 背景 | secondary | `rgba(255,255,255,0.6)` + `backdrop-filter: blur(40px)` |
| 圆角 | 无 | 28px（与侧边栏统一） |

### 2.7 整体容器 (.ai-main)

| 属性 | 改造前 | 改造后 |
|------|--------|--------|
| padding | 无 | 16px（浮动间距） |
| 背景 | secondary | 渐变背景（衬托毛玻璃层次） |

### 2.8 折叠态

折叠态从 64px 变为仅显示图标的紧凑 pill（宽度 64px，圆角保持 28px）。

---

## 3. 移动端壳层：三层系统壳层

### 3.1 壳层纵向结构

```
屏幕 (360px 宽)
├── HStatusbar (36px, 固定顶部)
├── HTitlebar (124px, 固定顶部浮层, z-index: 10)
│   └── 渐隐毛玻璃背板 + 标题
├── .mobile-content (flex: 1, 可滚动)
│   ├── padding-top: 预留 titlebar 空间
│   ├── padding-bottom: 预留 bottomtab 安全区 (100px)
│   └── <router-view />
└── HBottomTab (100px, 固定底部, z-index: 100)
    ├── 毛玻璃 pill bar (328px × 56px)
    ├── 4 个 tab: 工作台/探索/会话/智能体
    └── Home Indicator (112px × 5px)
```

### 3.2 壳层行为规则

- **HStatusbar**：固定顶部，36px，始终可见
- **HTitlebar**：固定顶部浮层，z-index: 10，渐隐毛玻璃背板，内容从 titlebar 背后滚过
- **HBottomTab**：固定底部，z-index: 100，毛玻璃 pill bar，内容通过 padding-bottom 预留安全区
- **内容区**：flex: 1，可滚动，从 titlebar 背后滚过形成渐变模糊效果

### 3.3 二级入口

bottomtab 4 个核心 tab 之外的 7 个功能，通过 titlebar 右侧"更多"图标按钮打开 HDrawer 抽屉，抽屉内展示网格入口。

---

## 4. 首页重构 (homepage.vue)

### 4.1 桌面端

| 属性 | 改造前 | 改造后 |
|------|--------|--------|
| 搜索框圆角 | level8 | 20px，毛玻璃背景 |
| 案例卡片圆角 | level8 | 16px，半透明白底 |
| 卡片边框 | 1px solid divider | 1px rgba(0,0,0,0.06) 更轻 |
| 卡片列数 | 4 列 grid | 2 列 grid（配合毛玻璃内容区） |
| 卡片 hover | border-color + shadow | 保留，对齐鸿蒙交互态 |

### 4.2 移动端

| 属性 | 说明 |
|------|------|
| 壳层 | HStatusbar + HTitlebar(big) + HBottomTab |
| 搜索框 | 100% 宽度，圆角 16px |
| 案例卡片 | 2 列 grid，圆角 16px |
| 标题 | "探索" 显示在 titlebar big 变体中 |
| 内容区 | padding-bottom 预留 bottomtab 100px 安全区 |

---

## 5. useNavigation composable

提取导航数据为共享 composable，桌面端和移动端共用：

```typescript
// src/composables/useNavigation.ts
export interface NavItem {
  key: string
  label: string
  icon: string
  route: string
}

// 核心 tab（bottomtab 使用）
export const coreTabs: NavItem[] = [
  { key: 'workspace', label: '工作台', icon: 'workspace', route: '/workspace' },
  { key: 'homepage', label: '探索', icon: 'explore', route: '/homepage' },
  { key: 'conversation', label: '会话', icon: 'dialog', route: '/conversation' },
  { key: 'agent', label: '智能体', icon: 'robot', route: '/agent' },
]

// 二级入口（drawer 菜单使用）
export const secondaryItems: NavItem[] = [
  { key: 'mcp-server', label: 'MCP', icon: 'mcp', route: '/mcp-server' },
  { key: 'knowledge', label: '知识库', icon: 'knowledge', route: '/knowledge' },
  { key: 'tool', label: '工具', icon: 'plugin', route: '/tool' },
  { key: 'agent-skill', label: 'Skill', icon: 'skill', route: '/agent-skill' },
  { key: 'interview', label: '面试', icon: 'skill', route: '/interview' },
  { key: 'model', label: '模型', icon: 'model', route: '/model' },
  { key: 'dashboard', label: '数据看板', icon: 'dashboard', route: '/dashboard' },
]

// 全量菜单（桌面端侧边栏使用）
export const allMenuItems: NavItem[] = [...coreTabs, ...secondaryItems]
```

---

## 6. Design Token 对齐

所有新增/改造的样式必须使用 `--harmony-*` Token，关键 Token 列表：

| Token | 值 | 用途 |
|-------|-----|------|
| `--harmony-brand` | rgba(10,89,247,1) | 品牌蓝，激活态 |
| `--harmony-comp-background-primary` | rgba(255,255,255,1) | 主背景 |
| `--harmony-comp-divider` | rgba(0,0,0,0.2) | 分割线 |
| `--harmony-interactive-hover` | rgba(0,0,0,0.047) | hover 态 |
| `--harmony-interactive-pressed` | rgba(0,0,0,0.098) | pressed 态 |
| `--harmony-font-primary` | rgba(0,0,0,0.898) | 主文字 |
| `--harmony-font-secondary` | rgba(0,0,0,0.6) | 次文字 |
| `--harmony-corner-radius-level8` | 20px | 大圆角 |

---

## 7. 交互状态规范

### 7.1 菜单项状态

| 状态 | 视觉表现 |
|------|----------|
| default | 背景透明，文字 `--harmony-font-secondary` |
| active | 背景 `rgba(10,89,247,0.098)`，文字 + 图标 `--harmony-brand` |
| hover | 背景 `--harmony-interactive-hover` |
| pressed | 背景 `--harmony-interactive-pressed` |

### 7.2 BottomTab 状态

| 状态 | 视觉表现 |
|------|----------|
| default | 图标 + 文字 `--harmony-font-secondary` |
| active | 图标 + 文字 `--harmony-brand` |

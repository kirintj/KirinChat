# Workspace 样式结构优化设计

## 目标

将 workspace 从独立顶级路由改为 index.vue 的子路由，复用统一的 `ai-nav` + 左侧菜单布局，使样式与 homepage 保持一致，不改变原有功能和逻辑。

## 当前状态

| 页面 | 路由层级 | 布局 |
|------|---------|------|
| workspace.vue | 顶级 `/workspace` | 自有 `workspace-nav` + sidebar + content |
| taskGraphPage.vue | 顶级 `/workspace/taskGraph` | 全屏 100vh 三列布局 |
| homepage.vue | `/` 子路由 | 使用 index.vue 的 `ai-nav` + 左侧菜单 |

## 设计方案

### 1. 路由变更 (`router/index.ts`)

将 workspace 和 taskGraph 都移入 `/` 路由的 children：

```
/ → Index (ai-nav + sidebar)
  /workspace → workspace.vue (会话列表 + router-view)
    (默认子路由) → defaultPage.vue
    /workspace/workspacePage → workspacePage.vue
  /workspace/taskGraph → taskGraphPage.vue (三列布局)
```

workspace 从独立顶级路由变为 index.vue 子路由，taskGraph 也作为 workspace 的同级子路由。

### 2. workspace.vue 改动

**移除内容：**
- `workspace-nav`（顶栏导航、logo、品牌名、用户头像菜单）
- 所有与顶栏相关的逻辑（`showUserMenu`、`toggleUserMenu`、`handleUserCommand`、`handleLogout`、`handleAvatarError`、`userMenuRef`、`handleOutsideClick`）
- 应用中心下拉菜单相关代码（`showAppCenterMenu`、`openAppCenterMenu`、`closeAppCenterMenu`、`appCenterColumns`）
- Google Fonts import（`@import url(...)`）

**保留内容：**
- 会话列表 sidebar（包含：应用中心按钮、会话卡片、删除功能、加载状态、空状态）
- `router-view` 子路由出口
- 所有 API 调用和业务逻辑（`fetchSessions`、`deleteSession`、`selectSession`、`formatTime`）

**样式改动：**
- 外层 `.workspace-container` 改为 `height: 100%; display: flex;`（不再使用 100vh，因为顶栏由 index.vue 控制）
- 移除 `.workspace-nav` 相关所有样式
- 将硬编码颜色替换为 CSS 变量：
  - `#f8f9fa` → `var(--color-bg-secondary)`
  - `#ffffff` → `var(--color-bg)`
  - `#e9ecef` → `var(--color-border)`
  - `#e5e7eb` → `var(--color-border)`
  - `#3b82f6` → `var(--color-primary)`
  - `#eff6ff` → `var(--color-primary-bg)`
  - `#1f2937` → `var(--color-text-primary)`
  - `#6b7280` → `var(--color-text-secondary)`
  - `#9ca3af` → `var(--color-text-tertiary)`
  - `#dc2626` → `var(--color-danger)`
  - `box-shadow: 2px 0 8px rgba(0,0,0,0.1)` → `var(--shadow-card)`
- 边框圆角：`border-radius: 12px` → `var(--radius-md)`
- 按钮 `border-radius: 8px` → `var(--radius-sm)`
- 删除按钮 hover 颜色改用 `var(--color-danger)` / `var(--color-danger-bg)`

### 3. taskGraphPage.vue 改动

taskGraphPage 作为 workspace 的子路由，会自动显示 workspace 的会话列表 sidebar。三列布局内容区会嵌套在 workspace 的 `.content` 区域中。

**布局嵌套关系：**
```
index.vue ai-nav (52px)
└── index.vue ai-main
    ├── index.vue sidebar (200px) — 左侧功能菜单
    └── index.vue content
        └── workspace.vue
            ├── workspace sidebar (280px) — 会话列表
            └── workspace content
                └── taskGraphPage — 三列布局
```

**样式改动（保持功能不变）：**
- `.task-graph-page` 的 `height: 100vh` → `height: 100%`（自适应父容器高度）
- `.three-column-layout` 的 `height: 100%` 保持不变（已自适应）
- 页面级 CSS 变量 `--bg` 改为 `var(--color-bg-secondary)` 或保持自定义
- 移除 `position: relative` + `overflow: hidden`（不再需要全屏占位）

### 4. defaultPage.vue 改动

**样式改动（保持功能不变）：**
- `.chat-page` 的背景 `linear-gradient(...)` 改为 `var(--color-bg-secondary)` 或 `var(--color-bg)`
- 硬编码颜色替换为 CSS 变量（`#e5e7eb` → `var(--color-border)` 等）

### 5. 涉及文件

| 文件 | 改动类型 |
|------|---------|
| `src/frontend/src/router/index.ts` | 路由结构变更 |
| `src/frontend/src/pages/workspace/workspace.vue` | 移除顶栏，样式统一 |
| `src/frontend/src/pages/workspace/taskGraphPage/taskGraphPage.vue` | 高度自适应 |
| `src/frontend/src/pages/workspace/defaultPage/defaultPage.vue` | CSS 变量替换 |

### 6. 不改动内容

- 所有业务逻辑和 API 调用不变
- 会话的创建、选择、删除功能不变
- taskGraph 的三列布局结构不变（仅高度从 100vh 改为 100%）
- defaultPage 的对话功能不变
- index.vue 本身不需要修改

## 风险与注意事项

1. taskGraph 三列布局在失去 100vh 后需要设置 `min-height: 0` 确保 flex 子元素正确收缩
2. workspace 的 sidebar 宽度（280px）+ index.vue 左侧菜单（200px）= 480px，taskGraph 三列内容区仅剩约 800px（1280px 屏幕），需要确认可接受性
3. taskGraph 成为 workspace 子路由后，会显示会话列表 sidebar，用户可在查看三列布局时切换会话
4. 路由变更后，`workspaceDefaultPage` 的 name 需要保持不变，否则 `selectSession` 函数中的路由跳转会失败

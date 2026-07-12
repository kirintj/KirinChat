# KirinChat Notion UI 重构设计规范

**日期**: 2026-07-12
**状态**: 已批准
**范围**: 全量重构 — Token + 组件 + 页面 + Shell 布局

---

## 1. 目标

将 KirinChat 前端从 HarmonyOS 设计系统整体迁移至 DESIGN.md 定义的 Notion 设计语言。移除所有 HarmonyOS 专有元素（毛玻璃、HMSymbol 字体、wearable token、暗色模式），建立统一的 Notion 风格视觉体系。

**设计原则：**
- 严格遵循 DESIGN.md 中所有配色、字体层级、按钮/卡片样式、间距、阴影、响应式规则
- 禁止自定义新颜色、圆角、字体
- 桌面优先，暖纸色文档式氛围

---

## 2. Design Token 系统

### 2.1 颜色

#### 品牌与强调色
| Token | 值 | 用途 |
|---|---|---|
| `--notion-primary` | `#0075de` | 主 CTA、链接、激活/聚焦态 |
| `--notion-primary-active` | `#005bab` | 主按钮按下态 |
| `--notion-secondary` | `#213183` | 深色 hero band（仅首页） |

#### 装饰色板（仅用于插画、图标、分类点，不用于结构或 CTA）
| Token | 值 |
|---|---|
| `--notion-accent-sky` | `#62aef0` |
| `--notion-accent-purple` | `#d6b6f6` |
| `--notion-accent-purple-deep` | `#391c57` |
| `--notion-accent-pink` | `#ff64c8` |
| `--notion-accent-orange` | `#dd5b00` |
| `--notion-accent-orange-deep` | `#793400` |
| `--notion-accent-teal` | `#2a9d99` |
| `--notion-accent-green` | `#1aae39` |
| `--notion-accent-brown` | `#523410` |

#### 表面色
| Token | 值 | 用途 |
|---|---|---|
| `--notion-canvas` | `#ffffff` | 导航栏、面板 |
| `--notion-canvas-soft` | `#f6f5f4` | 页面画布、footer |
| `--notion-surface` | `#ffffff` | 卡片、表单 |
| `--notion-hairline` | `#e6e6e6` | 1px 分割线、卡片边框 |

#### 文字色
| Token | 值 | 用途 |
|---|---|---|
| `--notion-ink` | `#000000` | 标题、正文 |
| `--notion-ink-secondary` | `#31302e` | 次级正文、footer |
| `--notion-ink-muted` | `#615d59` | 辅助文字 |
| `--notion-ink-faint` | `#a39e98` | 占位符、元数据 |

### 2.2 字体

**字体族**: `Inter, -apple-system, system-ui, "Segoe UI", Helvetica, Arial`

| Token | 字号 | 字重 | 行高 | 字距 | 用途 |
|---|---|---|---|---|---|
| `--notion-display-1` | 64px | 700 | 1.0 | -2.125px | Hero 标题 |
| `--notion-display-2` | 54px | 700 | 1.04 | -1.875px | 大段落标题 |
| `--notion-heading-1` | 40px | 700 | 1.1 | -1px | 段落标题 |
| `--notion-heading-2` | 26px | 700 | 1.23 | -0.625px | 子段落标题 |
| `--notion-heading-3` | 22px | 700 | 1.27 | -0.25px | 卡片标题 |
| `--notion-title` | 20px | 600 | 1.4 | -0.125px | 功能标题 |
| `--notion-body-md` | 16px | 400 | 1.5 | 0 | 默认正文 |
| `--notion-body-sm` | 15px | 400 | 1.33 | 0 | 紧凑正文、表格行、导航 |
| `--notion-button` | 16px | 500 | 1.5 | 0 | 按钮标签 |
| `--notion-caption` | 14px | 400 | 1.43 | 0 | 注释、脚注 |
| `--notion-eyebrow` | 12px | 600 | 1.33 | +0.125px | pill 标签、小标签 |

**原则：** 标题用重体 + 负字距，正文保持 400 字重。不使用装饰字体。

### 2.3 圆角

| Token | 值 | 用途 |
|---|---|---|
| `--notion-rounded-xs` | 4px | 表单字段、小标签 |
| `--notion-rounded-sm` | 5px | 菜单项、列表行 |
| `--notion-rounded-md` | 8px | 工具按钮、小卡片 |
| `--notion-rounded-lg` | 12px | 功能卡片、内容块 |
| `--notion-rounded-xl` | 16px | 大容器、弹窗、图片框 |
| `--notion-rounded-full` | 9999px | pill CTA、badge、圆形按钮 |

### 2.4 阴影

| Level | 样式 | 用途 |
|---|---|---|
| 0 — Flat | `border: 1px solid var(--notion-hairline)`, 无阴影 | 默认卡片 |
| 1 — Soft | 多层微阴影：`rgba(0,0,0,0.01) 0 0.175px 1.041px`, `0.02 0 0.8px 2.925px`, `0.027 0 2.025px 7.847px`, `0.04 0 4px 18px` | 浮起卡片、悬浮按钮 |
| 2 — Elevated | 5 层深阴影，最深 `rgba(0,0,0,0.05) 0 23px 52px` | 弹窗、弹出层 |

**原则：** 多层近乎透明的阴影叠加，不用硬阴影。

### 2.5 间距

8px 基数，7 级 token：

| Token | 值 |
|---|---|
| `--notion-spacing-xxs` | 4px |
| `--notion-spacing-xs` | 8px |
| `--notion-spacing-sm` | 12px |
| `--notion-spacing-md` | 16px |
| `--notion-spacing-lg` | 24px |
| `--notion-spacing-xl` | 28px |
| `--notion-spacing-xxl` | 32px |

### 2.6 响应式断点

| 名称 | 宽度 | 变化 |
|---|---|---|
| Wide | 1440px+ | 完整多列网格，最宽容器 |
| Desktop | 1080–1300px | 标准居中容器，3 列卡片网格 |
| Tablet | 768–840px | 2 列网格，导航压缩 |
| Mobile | ≤600px | 单列堆叠，汉堡菜单，全宽 CTA |

**策略：** 桌面优先。移动端侧边栏折叠为汉堡菜单，卡片单列堆叠。CTAs 保持 44×44px 最小点击区域。

---

## 3. Shell 布局架构

### 3.1 移除的组件
- `HStatusbar` — 移除
- `HAIBottomBar` — 移除，相关功能由各页面自行内嵌

### 3.2 重构的组件

**HAppShell → 三栏布局壳**
- 顶部导航栏 + 左侧边栏 + 内容区
- 移除 `isMobile` 手机式上下文，改为断点响应式

**HTitlebar → 顶部导航栏**
- 白底 `{colors.canvas}`，`{colors.ink}` 文字，`{typography.body-sm}`
- 内容：左侧 Logo/品牌名 + 导航链接，右侧搜索框 + 用户头像
- padding: `{spacing.md}` (16px)
- hairline 底部边框
- 移动端折叠为汉堡菜单

**HBottomTab → 左侧边栏**
- 固定宽度 200-240px（Wide/Desktop）
- 白底，hairline 右边框
- 导航项：body-sm 字体，当前页用 primary 色指示器
- padding: `{spacing.sm} {spacing.md}`
- 移动端折叠（汉堡菜单触发）

**内容区**
- 背景：`{colors.canvas-soft}` (#f6f5f4)
- 居中容器 max-width 1080-1300px
- 内容区 padding: `{spacing.lg}` (24px)

### 3.3 遮罩层
- 移除毛玻璃（blur + saturate）
- 改为纯色半透明 `rgba(0, 0, 0, 0.4)`

---

## 4. 组件库映射

### 4.1 按钮

| H 组件 | Notion 映射 | 圆角 | 样式 |
|---|---|---|---|
| HButton type="primary" | button-primary | `rounded-full` (9999px) | 背景 `#0075de`，文字 `#fff`，字重 500 |
| HButton type="secondary" | button-secondary | `rounded-full` | 白底 + hairline + Level-1 阴影 |
| HButton type="text" | button-utility | `rounded-md` (8px) | 白底，padding `4px 14px` |
| 图标按钮 | button-icon-circular | `rounded-full` | 半透明 `rgba(0,0,0,0.05)` 背景 |

**按下态**：button-primary → `#005bab`；其他按钮 `scale(0.9)` 变换。

### 4.2 卡片

| H 组件 | Notion 映射 | 样式 |
|---|---|---|
| HCardView | feature-card | 白底，hairline 边框，`rounded-lg` (12px)，padding 24px |
| 浮起卡片 | feature-card-elevated | 同上 + Level-1 阴影 |

**间距**：卡片间距 16px (`spacing.md`)。标题用 `typography.title` (20px/600)，正文用 `typography.body-md` (16px/400)。

### 4.3 输入框

| H 组件 | Notion 映射 | 样式 |
|---|---|---|
| HInput | text-input | 白底，1px `rgb(221,221,221)` 边框，`rounded-xs` (4px)，padding 6px |
| HSearch | text-input | 同上 |
| HSelect | text-input | 同上 |

**Focus 态**：添加 Level-1 微阴影。不使用 pill 圆角。

### 4.4 弹窗 & 浮层

| H 组件 | Notion 映射 | 样式 |
|---|---|---|
| HDialog | ex-modal-card | 白底，`rounded-xl` (16px)，padding 24px，Level-2 阴影 |
| HDrawer | 侧滑面板 | 白底 + hairline + Level-1 阴影 |
| HMessageBox | ex-modal-card | 同 HDialog |
| HMessage (toast) | ex-toast | 白底，`rounded-xl`，padding `12px 16px`，Level-1 阴影 |
| HDropdown | popover | 白底，`rounded-xl`，Level-2 阴影 |

### 4.5 其他组件

| H 组件 | Notion 映射 | 关键变化 |
|---|---|---|
| HTag | badge-pill | `rounded-full`, eyebrow 字体, primary 色文字, padding `4px 8px` |
| HTabs | nav tab | body-sm 字体, primary 色激活指示器 |
| HAvatar | 头像 | `rounded-full` (圆形) |
| HSwitch | 开关 | 激活色改为 primary |
| HTable | ex-data-table-cell | 表头 eyebrow 字体 + canvas-soft 背景, 行 hairline 分割 |
| HSkeleton | 骨架屏 | 底色改为 canvas-soft |
| HEmpty | ex-empty-state-card | canvas-soft 背景, `rounded-xl`, padding 32px |
| HDivider | 分割线 | 颜色改为 hairline |

### 4.6 业务组件

| 组件 | 变化 |
|---|---|
| agentCard | 改用 feature-card 样式，标题 title 字体，正文 body-md |
| commonCard | 同上 |
| historyCard | 改用 feature-card 样式 |
| drawer (业务) | 白底 + hairline + Level-1 阴影 |
| hub 组件 | 改用 feature-card / badge-pill 样式 |

---

## 5. 页面布局策略

### 5.1 通用页面模板

```
┌─────────────────────────────────────────────────┐
│ 顶部导航栏 (白底 + hairline)                      │
├────────────┬────────────────────────────────────┤
│            │  暖纸色画布 (#f6f5f4)               │
│  左侧边栏  │  ┌─ 页面标题 (heading-2) ──────────┐│
│  (白底)    │  │  页面描述 (body-sm)             ││
│            │  └─────────────────────────────────┘│
│  · 工作台  │  ┌─ 工具栏 ────────────────────────┐│
│  · 会话    │  │  [筛选] [排序]        [新建 CTA] ││
│  · Agent   │  └─────────────────────────────────┘│
│  · 知识库  │  ┌─ 卡片网格 ──────────────────────┐│
│  · 模型    │  │  ┌──────┐ ┌──────┐ ┌──────┐    ││
│            │  │  │card  │ │card  │ │card  │    ││
│  ────────  │  │  └──────┘ └──────┘ └──────┘    ││
│  · 配置    │  └─────────────────────────────────┘│
│  · 个人    │                                     │
├────────────┴────────────────────────────────────┤
```

### 5.2 各页面适配

| 页面 | 布局要点 |
|---|---|
| workspace | 3 列卡片网格 + 标题区，taskGraph 保留流程图布局 |
| conversation | 左侧会话列表 (240px) + 右侧聊天区 (白底圆角卡片) |
| login / register | 居中卡片 (ex-auth-form-card)，暖纸色背景，max-width 400px，不使用 Shell 布局（无侧边栏和导航栏） |
| interview hub | 卡片网格，ActiveSessionCard/QuickEntryCard/SkillStatCard |
| interview chat | 类 conversation 左右分栏 |
| agent / model / knowledge | 列表页 feature-card 网格 + 编辑器页 |
| agent-skill / mcp-server / tool | 列表页 feature-card 网格 |
| voice-interview | 居中对话式布局，音频控件用 button-utility |
| profile / configuration | 表单布局，text-input + button-primary |
| dashboard | 图表卡片网格 |
| mars | 类 conversation 布局 |
| construct | 列表/编辑器布局 |
| notFound | 居中 empty-state-card 风格 |

### 5.3 响应式规则

- **Wide (1440px+)**：完整多列，侧边栏展开
- **Desktop (1080-1300px)**：标准 3 列，侧边栏展开
- **Tablet (768-840px)**：2 列，侧边栏可折叠
- **Mobile (≤600px)**：单列，侧边栏隐藏（汉堡菜单），CTAs 全宽

移动端触控目标最小 44×44px。

---

## 6. 移除项清单

| 移除项 | 说明 |
|---|---|
| `--harmony-*` CSS 变量 | 全部替换为 `--notion-*` |
| HarmonyOS Sans 字体 | 替换为 Inter |
| HMSymbol 字体文件 | 删除 |
| HMOS Emoji 字体文件 | 删除 |
| wearable token 集 | 删除 |
| 暗色模式 (dark theme) | 删除 `data-theme="dark"` 相关逻辑 |
| 毛玻璃 (glass-mixins.css) | 删除，改用 hairline + 微阴影 |
| `mobile-scale.css` | 删除，移动端 token 直接使用 `--notion-*` 变量 + 断点 mixin 控制 |
| `harmony-editor-overrides.css` | 基于 Notion token 重写 |
| HStatusbar 组件 | 删除 |
| HAIBottomBar 组件 | 删除，功能由各页面内嵌 |

---

## 7. Do's and Don'ts

### Do
- `{colors.primary}` 仅用于主 CTA、链接和激活/聚焦态
- 页面使用 `{colors.canvas-soft}` 暖纸色画布，卡片用 `{colors.surface}` 白色
- 装饰色板仅用于插画、图标、分类点
- 标题用重体 `{typography.heading-*}` + 负字距
- pill `{rounded.full}` 用于营销 CTA，`{rounded.md}` 用于工具按钮
- 用 `{colors.hairline}` + 微阴影定义卡片层次
- `{colors.secondary}` 深靛蓝仅用于一个 hero band

### Don't
- 不用装饰色板颜色绘制 CTA 或结构填充
- 不引入第二个结构性强调色
- 不在表单字段上使用 pill 圆角（保持 `rounded-xs` 4px）
- 不使用硬阴影
- 不用重体设置正文（正文保持 400）
- 不在整页使用纯白背景（暖纸色 `canvas-soft` 是品牌核心）

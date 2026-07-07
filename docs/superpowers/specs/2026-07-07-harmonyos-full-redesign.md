# KirinChat 前端全面鸿蒙化重构设计

## 概述

以 `hmos-design-visual-mobile-master` 为唯一真相源，将 KirinChat 前端从"部分鸿蒙风格"重构为"像素级精确鸿蒙化"。涵盖 Token 体系、壳层组件、UI 组件库、HMSymbol 图标系统、响应式布局五个维度。

## 目标

- **全面鸿蒙化**：组件规范 + 视觉材质 + 壳层结构 + 图标系统全面对齐鸿蒙设计规范
- **响应式双端**：桌面端（≥768px）和移动端（<768px）自适应切换
- **基础层优先**：先建好 Token + 壳层 + 组件库，页面逐步迁移
- **参考驱动**：所有数值基线来自参考项目的 `component.json` 和 HTML 模板，不允许近似值

## 现状分析

### 现有基础（已具备）

- `harmony-tokens.css`（549 行）— 从参考项目复制，定义完整色彩/字体/交互态 token
- `mobile-scale.css`（59 行）— 从参考项目复制，定义间距/圆角/控件高度
- 18 个 `H` 前缀 UI 组件（HButton、HDialog、HDrawer 等）
- HarmonyOS Sans 字体已引入
- `style.css` — 业务变量映射层（`--color-*` → `--harmony-*`）

### 关键问题

1. **业务别名层冗余**：`style.css` 定义了 `--color-primary`、`--radius-md`、`--spacing-md` 等中间变量，组件间接引用鸿蒙 token，增加维护成本且与参考规范不同名
2. **缺少壳层组件**：无 statusbar、titlebar、bottomtab、aibottombar
3. **缺少液态玻璃效果**：无 backdrop-filter blur + plus-lighter 混合模式
4. **组件未对齐参考规范**：现有 H 组件样式基于自行设计，未与参考项目的数值基线和交互态一一对应
5. **使用 SVG 图标**：未引入 HMSymbol 字体图标系统

## 架构设计

### 四层架构

```
Layer 4: Pages (20+ 页面模块)
  conversation · workspace · agent · interview · knowledge · mcp-server · model ...

Layer 3: Shell Fragments (壳层组件)
  HStatusbar · HTitlebar (4 variants) · HBottomTab (6 variants) · HAIBottomBar

Layer 2: UI Components (13 参考组件 + 补充组件)
  HButton · HSearch · HSwitch · HChipsTab · HToolbar · HList · HDivider · HCardView
  HDialog · HDrawer · HDropdown · HForm · HInput · HSelect · HTabs · HTooltip ...

Layer 1: Foundation (基础设施)
  HarmonyOS Tokens · Mobile Scale · HMSymbol Icons · Glass Mixins · Theme System
```

### 文件结构

```
src/frontend/src/
├── styles/
│   ├── harmony-tokens.css      # 直接采用参考项目完整版（替换现有）
│   ├── mobile-scale.css        # 直接采用参考项目完整版（替换现有）
│   ├── glass-mixins.css        # 新增：液态玻璃效果 token
│   └── hmsymbol.css            # 新增：HMSymbol 字体引入
├── style.css                   # 精简：仅保留全局重置 + Vue transition 动画
├── assets/
│   ├── HMSymbolVF_1.ttf        # 新增：HMSymbol 图标字体
│   ├── HMOSColorEmoji*.ttf     # 新增：鸿蒙 Emoji 字体
│   └── statusbar-*.png         # 新增：状态栏 PNG 图标资源
├── components/
│   ├── ui/                     # 重构：鸿蒙组件库
│   │   ├── shell/              # 新增：壳层组件
│   │   │   ├── HStatusbar.vue
│   │   │   ├── HTitlebar.vue
│   │   │   ├── HBottomTab.vue
│   │   │   └── HAIBottomBar.vue
│   │   ├── HButton.vue         # 重构：对齐参考规范
│   │   ├── HSearch.vue         # 新增
│   │   ├── HSwitch.vue         # 新增
│   │   ├── HToolbar.vue        # 新增
│   │   ├── HList.vue           # 新增
│   │   ├── HDivider.vue        # 新增
│   │   ├── HCardView.vue       # 新增
│   │   ├── HChipsTab.vue       # 新增（或重构 HTabs）
│   │   └── ...                 # 保留升级：HDialog、HDrawer 等
│   └── business/               # 重构：业务组件鸿蒙化适配
│       ├── agentCard/          # agentCard.vue — 卡片样式对齐 HCardView
│       ├── commonCard/         # commonCard.vue — 卡片样式对齐 HCardView
│       ├── historyCard/        # histortCard.vue — 列表项对齐 HList
│       ├── hub/                # QuickEntryCard/ActiveSessionCard/RecentInterviewItem/SkillStatCard — 对齐 HCardView + HList
│       ├── dialog/             # AgentFormDialog — 对齐 HDialog 标准
│       └── drawer/             # drawer.vue — 对齐 HDrawer 标准
└── ...
```

## Token 体系设计

### 迁移策略：消除业务别名层

现有 `style.css` 中的业务变量将被删除，组件直接使用鸿蒙原生 token：

| 现有业务变量 | → 鸿蒙原生 Token | 动作 |
|---|---|---|
| `--color-primary` | `--harmony-brand` | 删除别名 |
| `--color-primary-hover` | `--harmony-interactive-hover` | 删除别名 |
| `--color-primary-active` | `--harmony-interactive-pressed` | 删除别名 |
| `--color-text-primary` | `--harmony-font-primary` | 删除别名 |
| `--color-text-secondary` | `--harmony-font-secondary` | 删除别名 |
| `--color-text-tertiary` | `--harmony-font-tertiary` | 删除别名 |
| `--color-text-disabled` | `--harmony-font-fourth` | 删除别名 |
| `--color-border` | `--harmony-comp-divider` | 删除别名 |
| `--color-border-focus` | `--harmony-interactive-focus` | 删除别名 |
| `--color-success` | `--harmony-confirm` | 删除别名 |
| `--color-warning` | `--harmony-alert` | 删除别名 |
| `--color-danger` | `--harmony-warning` | 删除别名 |
| `--radius-sm` | `--harmony-corner-radius-level4` | 删除别名 |
| `--radius-md` | `--harmony-corner-radius-level6` | 删除别名 |
| `--radius-lg` | `--harmony-corner-radius-level8` | 删除别名 |
| `--radius-full` | `--harmony-corner-radius-level18` | 删除别名 |
| `--spacing-xs` | `--harmony-padding-level4` | 删除别名 |
| `--spacing-sm` | `--harmony-padding-level6` | 删除别名 |
| `--spacing-md` | `--harmony-padding-level8` | 删除别名 |
| `--spacing-lg` | `--harmony-padding-level10` | 删除别名 |
| `--spacing-xl` | `--harmony-padding-level12` | 删除别名 |
| `--spacing-2xl` | `--harmony-padding-level16` | 删除别名 |
| `--font-size-xs` | `--harmony-font-size-body-s` | 删除别名 |
| `--font-size-sm` | `--harmony-font-size-subtitle-s` | 删除别名 |
| `--font-size-base` | `--harmony-font-size-body-m` | 删除别名 |
| `--font-size-lg` | `--harmony-font-size-body-l` | 删除别名 |
| `--font-size-xl` | `--harmony-font-size-title-s` | 删除别名 |
| `--font-size-2xl` | `--harmony-font-size-title-m` | 删除别名 |
| `--color-bg` | `--harmony-comp-background-primary` | 删除别名 |

### 新增 glass-mixins.css

液态玻璃效果的 CSS 变量，用于浮层组件（titlebar、bottomtab、dialog、drawer）：

```css
:root {
  --glass-blur: blur(20px);
  --glass-saturate: saturate(1.8);
  --glass-bg-light: rgba(255, 255, 255, 0.15);
  --glass-bg-dark: rgba(0, 0, 0, 0.15);
  --glass-border-light: 1px solid rgba(255, 255, 255, 0.2);
  --glass-border-dark: 1px solid rgba(255, 255, 255, 0.1);
  --glass-mix-blend: plus-lighter;
  --glass-box-shadow: 0 4px 48px rgba(0, 0, 0, 0.08),
                      0 4px 8px rgba(0, 0, 0, 0.25);
}
```

### Token 文件来源

- `harmony-tokens.css` — 直接复制自 `hmos-design-visual-mobile-master/references/2.theme/harmony-tokens.css`
- `mobile-scale.css` — 直接复制自 `hmos-design-visual-mobile-master/references/2.theme/mobile-scale.css`
- `component.json` 中的 `numeric_baseline` 作为每个组件的数值真值源

## 壳层组件设计

### HStatusbar

- 来源：`references/4.template/statusbar-tem.html` + `references/3.component/statusbar.md`
- 尺寸：360×36px
- 内容：WiFi / 信号 / 电池 PNG 图标（4 个 `<i>` 元素，position: absolute 精确定位）
- 变体：light / dark
- 约束：禁止改 DOM 结构、禁止改 CSS 布局方式、禁止改几何数值、禁止改资源引用方式

### HTitlebar

- 来源：`references/4.template/titlebar-tem.html` + `references/3.component/titlebar.md`
- 变体：big / normal / secondary / drawer
- 效果：渐隐背板（9 段曲线 mask-image）+ backdrop-filter 模糊
- z-index：10
- 响应式：移动端使用 big 变体，桌面端使用 normal/secondary 变体

### HBottomTab

- 来源：`references/4.template/bottomtab-tem.html` + `references/3.component/bottomtab.md`
- 变体：2 / 3 / 4 / 5 tab + 1bar + multibar
- 效果：液态玻璃胶囊（blur 80px + plus-lighter），home indicator（112×5px）
- z-index：100
- 响应式：仅移动端显示，桌面端用侧边栏替代

### HAIBottomBar

- 来源：`references/4.template/aibottombar-tem.html` + `references/3.component/aibottombar.md`
- 尺寸：360×28px
- 内容：横条拖拽指示器

### App.vue 壳层组装

移动端（<768px）：
```
<HStatusbar /> (内嵌于 HTitlebar)
<HTitlebar variant="big" />
<router-view class="layout-content" />
<HBottomTab variant="4" />
```

桌面端（≥768px）：
```
<HSidebar /> (现有侧边栏组件升级，非新建)
<div class="main-area">
  <HTitlebar variant="normal" />
  <router-view class="layout-content" />
</div>
```

## UI 组件库设计

### 新建组件（按参考模板）

| 组件 | 来源 | 关键规格 |
|---|---|---|
| HSearch | search.md + search-tem.html | off/on 模式 × 10 状态，浮动搜索栏 |
| HSwitch | switch.md + switch-tem.html | on/off × 5 状态 |
| HToolbar | toolbar.md + toolbar-tem.html | 浮动工具栏，5 变体 |
| HList | list.md + list-tem.html | 鸿蒙标准列表项 |
| HDivider | divider.md + divider-tem.html | 分割线 |
| HCardView | cardview.md + cardview-tem.html | 5 尺寸（max/larger/medium/small/mini） |

### 重构组件

| 组件 | 变更 |
|---|---|
| HButton | 对齐参考规范：5 类型 × 2 尺寸 × 6 状态 = 60 变体，液态玻璃填充 |
| HChipsTab | 对齐参考规范：胶囊标签栏，3 变体（替代现有 HTabs 的胶囊模式，HTabs 保留用于标准标签页） |

### 全面重构组件

HDialog、HDrawer、HDropdown/DropdownItem、HForm/FormItem、HInput、HSelect/HOption、HTabs/TabPane、HTooltip、HUpload、HAvatar、HSkeleton、HMessage/HMessageBox、HScrollbar、HTable、HTag

重构内容（与新建/重构组件统一标准）：
- 对齐参考规范数值基线（`component.json` 中的 `numeric_baseline`）
- 五态交互层（hover / pressed / focus / active / select）使用 `::before` / `::after` 伪元素
- 浮层组件（HDialog、HDrawer、HDropdown、HTooltip）添加液态玻璃效果
- 所有 token 引用统一为 `--harmony-*` 原生 token
- 样式结构与新建组件保持一致的代码规范

### HIcon 双模式扩展

```vue
<!-- HMSymbol 模式（壳层组件强制使用） -->
<HIcon name="&#xe900;" />

<!-- SVG 降级模式（业务组件可选） -->
<HIcon svg="chat-icon" />
```

## HMSymbol 图标系统

### 字体引入

```css
/* styles/hmsymbol.css */
@font-face {
  font-family: 'HMSymbol';
  src: url('../assets/HMSymbolVF_1.ttf') format('truetype');
  font-weight: normal;
  font-style: normal;
}

@font-face {
  font-family: 'HMOSColorEmoji';
  src: url('../assets/HMOSColorEmojiCompat.ttf') format('truetype');
}
```

### 资源来源

字体文件来自 `hmos-design-visual-mobile-master/assets/`：
- `HMSymbolVF_1.ttf` — HMSymbol 图标字体（Unicode 私有区编码）
- `HMOSColorEmojiFlags.ttf` — Emoji 国旗字体
- `HMOSColorEmojiCompat.ttf` — Emoji 兼容字体

### 使用规则

- 壳层组件（statusbar、titlebar、bottomtab）强制使用 HMSymbol 字体
- 业务组件可选择 HMSymbol 或 SVG 降级
- HIcon 组件扩展 `name` 属性支持 HMSymbol Unicode 字符

## 响应式布局设计

### 断点

| 断点 | 布局 | 导航 | Titlebar |
|---|---|---|---|
| < 768px | 360px 画布居中 | HBottomTab 浮底 | big |
| 768-1200px | 自适应宽度 | 侧边栏折叠 | normal |
| ≥ 1200px | 自适应宽度 | 侧边栏展开 | normal |

### Z 轴层级

| 组件 | z-index |
|---|---|
| HBottomTab | 100 |
| HSearch | 30 |
| HTitlebar | 10 |
| .layout-content | auto |

### 三种布局模式

参考项目定义了三种布局模式，按页面内容选择：
- `layout-card` — 卡片布局（如 dashboard、homepage）
- `layout-grid` — 网格布局（如 knowledge、agent 列表）
- `layout-list` — 列表布局（如 conversation 历史）

## 统一路由布局

### 现状问题

`App.vue` 仅包含 `<router-view>`，侧边栏和导航栏在各页面独立重写，导致：
- 壳层组件（statusbar/titlebar/bottomtab）无法全局注入
- 侧边栏样式和交互各页面不一致
- 响应式断点逻辑重复实现

### 目标方案

将 App.vue 改为统一路由布局容器：

```vue
<!-- App.vue -->
<template>
  <HAppShell>
    <!-- 移动端壳层 -->
    <template v-if="isMobile">
      <HTitlebar variant="big" />
      <router-view class="layout-content" />
      <HBottomTab variant="4" />
    </template>
    <!-- 桌面端壳层 -->
    <template v-else>
      <HSidebar />
      <div class="main-area">
        <HTitlebar variant="normal" />
        <router-view class="layout-content" />
      </div>
    </template>
  </HAppShell>
</template>
```

- **HAppShell**：新增根容器组件，管理响应式断点状态
- **HSidebar**：从各页面抽取为共享组件，桌面端固定左侧
- 各页面不再自行实现侧边栏和导航，仅关注内容区

## 动效系统统一

### 现状问题

30+ 处自定义 keyframes（fadeIn、slideIn、slideUp、scaleIn、pulse、float、cardAppear 等）分散在各页面，未使用统一的鸿蒙动效曲线。

### 目标方案

在 `style.css` 中集中定义鸿蒙标准动效：

```css
:root {
  /* 鸿蒙标准动效曲线 */
  --harmony-motion-standard: cubic-bezier(0.2, 0, 0.4, 1);
  --harmony-motion-decelerate: cubic-bezier(0, 0, 0.2, 1);
  --harmony-motion-accelerate: cubic-bezier(0.4, 0, 1, 1);
  --harmony-motion-spring: cubic-bezier(0.34, 1.56, 0.64, 1);

  /* 标准时长 */
  --harmony-duration-immediate: 100ms;
  --harmony-duration-fast: 150ms;
  --harmony-duration-normal: 200ms;
  --harmony-duration-slow: 300ms;
  --harmony-duration-extra: 500ms;
}

/* 标准入场动效 */
@keyframes harmony-fade-in { from { opacity: 0; } to { opacity: 1; } }
@keyframes harmony-slide-up { from { transform: translateY(16px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
@keyframes harmony-slide-in-right { from { transform: translateX(100%); } to { transform: translateX(0); } }
@keyframes harmony-scale-in { from { transform: scale(0.95); opacity: 0; } to { transform: scale(1); opacity: 1; } }
@keyframes harmony-pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
```

各页面/组件的自定义 keyframes 全部替换为上述标准动效。

## 硬编码样式清理

### 现状问题

- 35 个 .vue 文件含硬编码颜色（`#409eff`、`#67c23a`、`#f56c6c` 等）
- 100+ 处硬编码 `border-radius`（2px、8px、12px 等）
- 60+ 处 `style=""` 内联样式

### 清理规则

| 硬编码值 | → HarmonyOS Token |
|---|---|
| `#409eff`、`#3b82f6` 等蓝色 | `var(--harmony-brand)` 或对应语义色 |
| `#67c23a` 等绿色 | `var(--harmony-confirm)` |
| `#f56c6c` 等红色 | `var(--harmony-warning)` |
| `#e6a23c` 等橙色 | `var(--harmony-alert)` |
| `#cbd5e1` 等灰色 | `var(--harmony-font-tertiary)` 或 `var(--harmony-comp-divider)` |
| `border-radius: 4px` | `var(--harmony-corner-radius-level2)` |
| `border-radius: 8px` | `var(--harmony-corner-radius-level4)` |
| `border-radius: 12px` | `var(--harmony-corner-radius-level6)` |
| `border-radius: 16px` | `var(--harmony-corner-radius-level8)` |
| `border-radius: 999px` | `var(--harmony-corner-radius-level18)` |
| 内联 `style=""` | 迁移到 `<style scoped>` 中使用 token |

所有硬编码样式在 Phase 6 页面迁移时同步清理，每个页面迁移完成前必须通过 `grep` 检查无残留硬编码值。

## Shadow Token 体系

### 现状

`style.css` 中的 `--shadow-*` 系列全部使用硬编码 rgba 值（如 `0 4px 12px rgba(0,0,0,0.06)`），未映射到鸿蒙 token。

### 目标方案

在 `harmony-tokens.css` 中补充阴影 token，或在 `glass-mixins.css` 中定义语义化阴影：

```css
:root {
  --harmony-shadow-xs: 0 1px 2px rgba(0, 0, 0, 0.02);
  --harmony-shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.04);
  --harmony-shadow-md: 0 4px 12px rgba(0, 0, 0, 0.06);
  --harmony-shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.08);
  --harmony-shadow-card: 0 2px 8px rgba(0, 0, 0, 0.06);
  --harmony-shadow-card-hover: 0 4px 16px rgba(0, 0, 0, 0.08);
  --harmony-shadow-dialog: 0 8px 32px rgba(0, 0, 0, 0.12);
}

[data-theme="dark"] {
  --harmony-shadow-xs: 0 1px 2px rgba(0, 0, 0, 0.04);
  --harmony-shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.08);
  --harmony-shadow-md: 0 4px 12px rgba(0, 0, 0, 0.1);
  --harmony-shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.14);
  --harmony-shadow-card: 0 2px 8px rgba(0, 0, 0, 0.08);
  --harmony-shadow-card-hover: 0 4px 16px rgba(0, 0, 0, 0.12);
  --harmony-shadow-dialog: 0 8px 32px rgba(0, 0, 0, 0.2);
}
```

删除 `style.css` 中的 `--shadow-*` 定义，所有引用替换为 `--harmony-shadow-*`。

## Overlay/遮罩 Token 化

### 现状

- HMessageBox overlay 硬编码 `rgba(0,0,0,0.5)`，暗色模式不适配
- HDialog、HDrawer 各自实现遮罩样式，不统一

### 目标方案

在 `glass-mixins.css` 中统一定义遮罩 token：

```css
:root {
  --harmony-overlay-light: rgba(0, 0, 0, 0.4);
  --harmony-overlay-heavy: rgba(0, 0, 0, 0.6);
}

[data-theme="dark"] {
  --harmony-overlay-light: rgba(0, 0, 0, 0.5);
  --harmony-overlay-heavy: rgba(0, 0, 0, 0.7);
}
```

HMessageBox、HDialog、HDrawer 统一引用 `--harmony-overlay-*` token。

## 全局可访问性与降级

### ::selection 文本选中色

```css
::selection {
  background-color: var(--harmony-comp-emphasize-tertiary);
  color: var(--harmony-font-primary);
}
```

### ::focus 焦点指示器

删除所有业务页面中的 `outline: none`，统一使用鸿蒙焦点样式：

```css
:focus-visible {
  outline: 2px solid var(--harmony-interactive-focus);
  outline-offset: 2px;
}

/* 禁用默认 outline 的元素必须提供替代焦点指示 */
*:focus:not(:focus-visible) {
  outline: none;
}
```

### prefers-reduced-motion 动效降级

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

## 响应式断点统一

### 现状

15 个页面文件使用 7+ 种断点值（480/600/768/900/1100/1199/1200/1400px），无统一变量。

### 目标方案

在 `style.css` 中定义统一断点变量：

```css
:root {
  --bp-mobile: 480px;
  --bp-tablet: 768px;
  --bp-desktop: 1200px;
  --bp-wide: 1400px;
}
```

各页面媒体查询统一使用：
- `@media (max-width: var(--bp-mobile))` — 移动端
- `@media (max-width: var(--bp-tablet))` — 平板
- `@media (min-width: var(--bp-desktop))` — 桌面端
- `@media (min-width: var(--bp-wide))` — 宽屏

注意：CSS 自定义属性不能直接用在 `@media` 中，需使用 SCSS mixin 或 PostCSS 插件：
```scss
@mixin mobile { @media (max-width: 767px) { @content; } }
@mixin tablet { @media (max-width: 1199px) { @content; } }
@mixin desktop { @media (min-width: 1200px) { @content; } }
@mixin wide { @media (min-width: 1400px) { @content; } }
```

各页面全部替换为上述 mixin，删除零散断点值。

## 页面过渡动画

### 现状

router-view 无 `<Transition>` 包裹，页面切换无动效。

### 目标方案

在 App.vue 的 `<router-view>` 外添加鸿蒙标准页面过渡：

```vue
<router-view v-slot="{ Component, route }">
  <Transition name="harmony-page" mode="out-in">
    <component :is="Component" :key="route.path" />
  </Transition>
</router-view>
```

```css
.harmony-page-enter-active {
  animation: harmony-fade-in var(--harmony-duration-normal) var(--harmony-motion-decelerate);
}
.harmony-page-leave-active {
  animation: harmony-fade-in var(--harmony-duration-fast) var(--harmony-motion-accelerate) reverse;
}
```

## Dialog/Popup 样式统一

### 现状

agent、knowledge-file、mcp-server、tool、conversation 等页面各自实现 overlay + card + footer 弹窗样式，未复用 HDialog 组件。

### 目标方案

1. Phase 4 中 HDialog 组件全面重构后，所有页面的自定义弹窗替换为 `<HDialog>` 组件
2. 删除各页面中重复的 overlay/card/footer 样式
3. 特殊尺寸需求通过 HDialog 的 `width` 和 `custom-class` prop 满足

## Empty 状态统一

### 现状

drawer.vue 使用 emoji 🤖 作为 empty 状态，各页面 empty 样式不统一。

### 目标方案

新增 `HEmpty` 组件：

```vue
<!-- components/ui/HEmpty.vue -->
<template>
  <div class="h-empty">
    <HIcon :name="icon" class="h-empty__icon" />
    <p class="h-empty__text">{{ text }}</p>
    <slot name="action" />
  </div>
</template>
```

所有页面的 empty 状态统一使用 `<HEmpty>`，图标使用 HMSymbol 字体字符。

## CSS 体量瘦身

### 现状

- mcp-server.vue：1900 行 CSS（2 个 style 块，23 处内联 style）
- tool.vue：1370 行（大量 `.dark` 前缀手动适配）
- conversation.vue：1020 行（5 个 @keyframes，dialog 样式冗长）
- knowledge-file.vue：800 行（4 个 @keyframes）

### 瘦身策略

1. **提取公共样式到 SCSS mixin**：dialog overlay、card hover、loading spinner 等跨页面重复模式
2. **删除 `.dark` 前缀手动适配**：全部走 `[data-theme="dark"]` token 机制，tool.vue 重点清理
3. **合并重复 style 块**：mcp-server.vue 的 2 个 style 块合并为 1 个 scoped 块
4. **删除内联 style=""**：23 处 mcp-server 内联样式迁移到 `<style scoped>`

## non-scoped 样式清理

### 现状

4 处 non-scoped 样式存在泄漏风险：
- `AgentFormDialog.vue` — 第二段 non-scoped style
- `agent-skill.vue` — 第二段 non-scoped style
- `mcp-server.vue` — 第二段 non-scoped style
- `notFound.vue` — `<style>` 无 scoped

### 清理规则

1. 检查每处 non-scoped 样式是否有跨组件影响的意图
2. 如有跨组件需求，迁移到 `style.css` 全局样式中
3. 如无跨组件需求，添加 `scoped` 属性
4. 清理完成后 `grep -rn '<style' src/ | grep -v scoped` 返回 0 结果

## hubPage 命名空间修正

### 现状

`interview/hubPage.vue` 使用 `var(--text-primary, #1f2937)` 等非标准命名空间，存在两套 token 体系。

### 目标方案

全部替换为标准 `--harmony-*` 命名空间：
- `var(--text-primary, #1f2937)` → `var(--harmony-font-primary)`
- `var(--text-secondary, ...)` → `var(--harmony-font-secondary)`
- 其他非标准变量逐一替换

## 第三方库主题适配

### ECharts

```ts
// composables/useEChartsTheme.ts
const getEChartsTheme = () => {
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark'
  return {
    color: [/* 从 --harmony-* token 提取 */],
    backgroundColor: 'transparent',
    textStyle: { color: isDark ? 'rgba(255,255,255,0.87)' : 'rgba(0,0,0,0.87)' },
    // ...
  }
}
```

### Monaco Editor

```css
/* harmony-editor-overrides.css */
.monaco-editor {
  --vscode-editor-background: var(--harmony-comp-background-primary) !important;
  --vscode-editor-foreground: var(--harmony-font-primary) !important;
  border-radius: var(--harmony-corner-radius-level8);
}
```

## 图标迁移 HMSymbol

### 现状

`src/assets/` 下 28 个 SVG 图标 + 3 个 PNG 图标，均未通过 HMSymbol 加载。

### 迁移策略

1. **评估映射**：逐个检查 28 个 SVG 图标，判断是否有对应的 HMSymbol Unicode 字符
2. **可映射图标**：直接替换为 HMSymbol 字体引用（如 add、delete、copy、search、send 等常见图标）
3. **不可映射图标**：保留 SVG 但统一视觉风格（圆角、线宽、尺寸对齐鸿蒙规范）
4. **HIcon 组件**：所有图标统一通过 `<HIcon>` 组件调用，不再直接使用 `<img>` 或 `<svg>` 标签

### 第三方库样式适配

Monaco Editor、Vditor、ECharts、MdEditor 的样式覆盖：
- 定义 `harmony-editor-overrides.css` 统一管理第三方库样式覆盖
- 主题色、字体、圆角对齐鸿蒙 token
- 适配 light/dark 主题切换

## 实施分期

> 6 个阶段，按依赖关系排序。每阶段产出可独立验证，前一阶段未完成不得进入下一阶段。

### Phase 1: Design Token 基础层

**目标**：建立完整的鸿蒙设计 token 体系，消除所有间接映射和硬编码值。

**前置条件**：无

**任务清单**：

| # | 任务 | 涉及文件 | 验收标准 |
|---|---|---|---|
| 1.1 | 用参考项目替换 `harmony-tokens.css` | `styles/harmony-tokens.css` | 与参考项目文件 diff 为空 |
| 1.2 | 用参考项目替换 `mobile-scale.css` | `styles/mobile-scale.css` | 与参考项目文件 diff 为空 |
| 1.3 | 新增 `glass-mixins.css`（液态玻璃 + overlay + shadow token） | `styles/glass-mixins.css` 新建 | 包含 blur/saturate/bg/border/shadow/overlay 变量，light/dark 双模式 |
| 1.4 | 新增鸿蒙动效 token | `style.css` | 包含 `--harmony-motion-*` 和 `--harmony-duration-*` |
| 1.5 | 新增标准 keyframes | `style.css` | 包含 harmony-fade-in / slide-up / slide-in-right / scale-in / pulse |
| 1.6 | 新增响应式断点 mixin | `styles/breakpoints.scss` 新建 | 包含 mobile / tablet / desktop / wide 四个 mixin |
| 1.7 | 新增全局可访问性样式 | `style.css` | 包含 `::selection`、`:focus-visible`、`prefers-reduced-motion` |
| 1.8 | 删除 `style.css` 业务别名和 shadow 硬编码 | `style.css` | 无 `--color-*` / `--radius-*` / `--spacing-*` / `--font-size-*` / `--shadow-*` 定义 |
| 1.9 | 全局替换业务变量引用 | 全部 .vue + .css 文件 | `grep -r "var(--color-\|var(--radius-\|var(--spacing-\|var(--font-size-" src/` 返回 0 结果 |
| 1.10 | 全局替换硬编码阴影为 token | 全部 .vue 文件 | 所有 `box-shadow: rgba(...)` 替换为 `var(--harmony-shadow-*)` |
| 1.11 | 新增 `harmony-editor-overrides.css` | `styles/harmony-editor-overrides.css` 新建 | Monaco/ECharts/MdEditor 主题色 + 字体 + 圆角对齐 token |

**风险**：1.9 和 1.10 全局替换影响范围大，需逐文件验证不破坏功能。

---

### Phase 2: HMSymbol 图标系统

**目标**：完成图标字体引入和 HIcon 组件扩展，为壳层组件和后续迁移做准备。

**前置条件**：Phase 1 完成

**任务清单**：

| # | 任务 | 涉及文件 | 验收标准 |
|---|---|---|---|
| 2.1 | 部署 HMSymbol 字体文件 | `assets/HMSymbolVF_1.ttf`、`assets/HMOSColorEmojiCompat.ttf` 新增 | 文件存在且可加载 |
| 2.2 | 新增 `hmsymbol.css` | `styles/hmsymbol.css` 新建 | @font-face 声明正确，浏览器可渲染 HMSymbol 字符 |
| 2.3 | HIcon 组件双模式扩展 | `components/ui/HIcon.vue` | 支持 `name`（HMSymbol Unicode）和 `svg`（降级）两种模式 |
| 2.4 | 评估 28 个 SVG 到 HMSymbol 映射 | `assets/*.svg` | 产出映射表：可替换 / 不可替换（保留 SVG 统一风格） |
| 2.5 | 可映射图标替换为 HMSymbol | 相关 .vue 文件 | 替换后的图标通过 HIcon 组件渲染，视觉无差异 |
| 2.6 | 不可映射图标风格统一 | 相关 .svg 文件 | 圆角、线宽、尺寸对齐鸿蒙规范 |

**风险**：2.4 映射评估需逐个比对 HMSymbol 字符集，部分图标可能无对应字符。

---

### Phase 3: 壳层组件 + 统一路由布局 + 页面过渡

**目标**：实现 4 个壳层组件 + HAppShell + HSidebar + HEmpty，建立统一页面骨架和过渡动效。

**前置条件**：Phase 1（Token）、Phase 2（HMSymbol）完成

**任务清单**：

| # | 任务 | 涉及文件 | 验收标准 |
|---|---|---|---|
| 3.1 | 部署 statusbar PNG 图标资源 | `assets/statusbar-*.png` 新增（8 个文件） | light/dark 各 4 个图标文件存在 |
| 3.2 | 实现 HStatusbar | `components/ui/shell/HStatusbar.vue` 新建 | 4 个 `<i>` 元素，position: absolute，数值与模板一致 |
| 3.3 | 实现 HTitlebar | `components/ui/shell/HTitlebar.vue` 新建 | 4 种变体（big/normal/secondary/drawer），渐隐背板 + backdrop-filter |
| 3.4 | 实现 HBottomTab | `components/ui/shell/HBottomTab.vue` 新建 | 6 种变体（2/3/4/5 tab + 1bar + multibar），液态玻璃胶囊 |
| 3.5 | 实现 HAIBottomBar | `components/ui/shell/HAIBottomBar.vue` 新建 | 360×28px，home indicator 112×5px |
| 3.6 | 实现 HAppShell | `components/ui/shell/HAppShell.vue` 新建 | 管理响应式断点状态，提供 isMobile 计算属性 |
| 3.7 | 实现 HEmpty | `components/ui/HEmpty.vue` 新建 | HMSymbol 图标 + 文本 + action 插槽 |
| 3.8 | 抽取 HSidebar 为共享组件 | 从各页面提取侧边栏逻辑，统一到 `components/ui/shell/HSidebar.vue` | 桌面端固定左侧，响应式折叠/展开 |
| 3.9 | 重构 App.vue 统一布局 + 页面过渡 | `App.vue` | 统一壳层组装 + `<Transition name="harmony-page">` 包裹 router-view |
| 3.10 | 注册壳层组件到 UI 插件 | `components/ui/index.ts` | 全部壳层 + HEmpty 全局可用 |

**风险**：3.8 HSidebar 抽取涉及多页面改动，需逐页验证侧边栏功能不丢失。3.9 App.vue 重构后需全页面回归测试。

---

### Phase 4: UI 组件库重构

**目标**：新建 8 个参考组件 + 重构全部 17 个现有组件，统一为鸿蒙规范。

**前置条件**：Phase 1（Token）、Phase 2（HMSymbol）、Phase 3（壳层）完成

**任务清单**：

| # | 任务 | 涉及文件 | 验收标准 |
|---|---|---|---|
| **新建组件** | | | |
| 4.1 | 实现 HSearch | `components/ui/HSearch.vue` 新建 | off/on 模式 × 10 状态，数值基线与 search-tem.html 一致 |
| 4.2 | 实现 HSwitch | `components/ui/HSwitch.vue` 新建 | on/off × 5 状态 |
| 4.3 | 实现 HToolbar | `components/ui/HToolbar.vue` 新建 | 浮动工具栏，5 变体 |
| 4.4 | 实现 HList | `components/ui/HList.vue` 新建 | 鸿蒙标准列表项 |
| 4.5 | 实现 HDivider | `components/ui/HDivider.vue` 新建 | 分割线 |
| 4.6 | 实现 HCardView | `components/ui/HCardView.vue` 新建 | 5 尺寸（max/larger/medium/small/mini） |
| 4.7 | 实现 HChipsTab | `components/ui/HChipsTab.vue` 新建 | 胶囊标签栏，3 变体 |
| **重构现有组件** | | | |
| 4.8 | 重构 HButton | `components/ui/HButton.vue` | 5 类型 × 2 尺寸 × 6 状态，液态玻璃填充，数值基线对齐 |
| 4.9 | 重构 HDialog | `components/ui/HDialog.vue` | 液态玻璃 + 五态交互 + Token 直引 + 宽度/padding 对齐鸿蒙数值基线 |
| 4.10 | 重构 HDrawer | `components/ui/HDrawer.vue` | 液态玻璃 + 鸿蒙动效曲线 + 五态交互 |
| 4.11 | 重构 HDropdown/DropdownItem | `components/ui/HDropdown.vue`、`DropdownItem.vue` | 液态玻璃 + 五态交互 |
| 4.12 | 重构 HForm/FormItem | `components/ui/HForm.vue`、`FormItem.vue` | Token 直引 + 五态交互 + aria-invalid 关联 |
| 4.13 | 重构 HInput | `components/ui/HInput.vue` | Token 直引 + 五态交互 |
| 4.14 | 重构 HSelect/HOption | `components/ui/HSelect.vue`、`HOption.vue` | 液态玻璃 + 五态交互 |
| 4.15 | 重构 HTabs/TabPane | `components/ui/HTabs.vue`、`TabPane.vue` | Token 直引 + 五态交互 |
| 4.16 | 重构 HTooltip | `components/ui/HTooltip.vue` | 液态玻璃 + Token 直引 |
| 4.17 | 重构 HUpload | `components/ui/HUpload.vue` | Token 直引 + 五态交互 |
| 4.18 | 重构 HAvatar | `components/ui/HAvatar.vue` | Token 直引 |
| 4.19 | 重构 HSkeleton | `components/ui/HSkeleton.vue` | 鸿蒙标准 pulse 动效 |
| 4.20 | 重构 HMessage/HMessageBox | `components/ui/HMessage.vue`、`HMessageBox.vue` | 液态玻璃 + 鸿蒙动效 + overlay 改用 `--harmony-overlay-*` token |
| 4.21 | 重构 HScrollbar | `components/ui/HScrollbar.vue` | Token 直引 + Firefox fallback |
| 4.22 | 重构 HTable | `components/ui/HTable.vue` | Token 直引 + HDivider 分割线 |
| 4.23 | 重构 HTag | `components/ui/HTag.vue` | Token 直引 + 五态交互 |
| **注册** | | | |
| 4.24 | 注册新组件到 UI 插件 | `components/ui/index.ts` | HSearch/HSwitch/HToolbar/HList/HDivider/HCardView/HChipsTab/HEmpty 全局可用 |

---

### Phase 5: 业务组件 + 代码质量清理

**目标**：业务组件对齐 UI 组件库标准，清理动效、non-scoped 样式、命名空间、可访问性问题。

**前置条件**：Phase 4（UI 组件库）完成

**任务清单**：

| # | 任务 | 涉及文件 | 验收标准 |
|---|---|---|---|
| **业务组件重构** | | | |
| 5.1 | 重构 agentCard.vue | `components/agentCard/agentCard.vue` | 对齐 HCardView，Token 直引 |
| 5.2 | 重构 commonCard.vue | `components/commonCard/commonCard.vue` | 对齐 HCardView，Token 直引 |
| 5.3 | 重构 histortCard.vue | `components/historyCard/histortCard.vue` | 对齐 HList 列表项 |
| 5.4 | 重构 hub/QuickEntryCard.vue | `components/hub/QuickEntryCard.vue` | 对齐 HCardView |
| 5.5 | 重构 hub/ActiveSessionCard.vue | `components/hub/ActiveSessionCard.vue` | 对齐 HCardView |
| 5.6 | 重构 hub/RecentInterviewItem.vue | `components/hub/RecentInterviewItem.vue` | 对齐 HList 列表项 |
| 5.7 | 重构 hub/SkillStatCard.vue | `components/hub/SkillStatCard.vue` | 对齐 HCardView |
| 5.8 | 重构 dialog/AgentFormDialog.vue | `components/dialog/create_agent/AgentFormDialog.vue` | 对齐 HDialog 标准 + scoped 样式 |
| 5.9 | 重构 drawer/drawer.vue | `components/drawer/drawer.vue` | 对齐 HDrawer 标准 + empty 状态改用 HEmpty |
| **动效 + 代码质量清理** | | | |
| 5.10 | 清理自定义 keyframes | 30+ 处分散在各 .vue 文件中的 keyframes | 替换为 `harmony-*` 标准动效 |
| 5.11 | 统一 transition 曲线 | 各 .vue 文件中的 transition/animation 属性 | 使用 `var(--harmony-motion-*)` 和 `var(--harmony-duration-*)` |
| 5.12 | 修复 non-scoped 样式 | AgentFormDialog、agent-skill、mcp-server、notFound | `grep -rn '<style' src/ | grep -v scoped` 返回 0 结果 |
| 5.13 | 修复 hubPage 命名空间 | `pages/interview/hubPage/hubPage.vue` | 所有 `var(--text-*)` 替换为 `var(--harmony-font-*)` |
| 5.14 | 修复 focus 可访问性 | 10+ 业务页面 | 删除无替代的 `outline: none`，统一使用 `:focus-visible` |
| 5.15 | ECharts 暗色主题适配 | `composables/useEChartsTheme.ts` 新建 | ECharts 主题从鸿蒙 token 提取，light/dark 自动切换 |
| 5.16 | Monaco Editor 样式覆盖 | `harmony-editor-overrides.css` | 编辑器背景/前景色/圆角对齐鸿蒙 token |

---

### Phase 6: 页面迁移 + CSS 瘦身 + 硬编码清理

**目标**：20+ 页面逐步迁移到鸿蒙组件库，清理全部硬编码样式，CSS 瘦身到合理体量。

**前置条件**：Phase 3（壳层布局）、Phase 4（UI 组件库）、Phase 5（业务组件）完成

**每页迁移步骤**（严格执行，共 16 步）：

1. 替换业务变量为 `--harmony-*` 原生 token
2. 替换自定义样式为鸿蒙组件（HCardView、HList、HButton、HDialog、HEmpty 等）
3. 接入壳层组件（选择合适的 HTitlebar 变体）
4. 清理硬编码颜色 → 对应 `--harmony-*` 语义色 token
5. 清理硬编码圆角 → 对应 `--harmony-corner-radius-level*` token
6. 清理硬编码阴影 → 对应 `--harmony-shadow-*` token
7. 清理内联 `style=""` → 迁移到 `<style scoped>` 中使用 token
8. 替换自定义 keyframes 为鸿蒙标准动效
9. 替换硬编码 transition 为 `var(--harmony-motion-*)` + `var(--harmony-duration-*)`
10. 图标统一通过 `<HIcon>` 组件调用
11. 第三方库样式引用 `harmony-editor-overrides.css`
12. 自定义弹窗替换为 `<HDialog>` 组件，删除重复 overlay/card/footer 样式
13. 自定义 empty 状态替换为 `<HEmpty>` 组件
14. 响应式断点替换为 SCSS mixin（`+mobile` / `+tablet` / `+desktop`）
15. CSS 体量审查：合并重复 style 块、删除 `.dark` 前缀手动适配
16. 响应式验证（桌面端 + 移动端）

**迁移完成后自检**（每个页面）：
- `grep -rn "#[0-9a-fA-F]\{3,8\}" <page-file>` → 0 结果（无硬编码颜色）
- `grep -rn "border-radius: [0-9]" <page-file>` → 0 结果（无硬编码圆角）
- `grep -rn 'style="' <page-file>` → 0 结果（无内联样式）
- `grep -rn "box-shadow: rgba" <page-file>` → 0 结果（无硬编码阴影）
- `grep -rn "0\.[1-9]s\|[0-9]s ease" <page-file>` → 0 结果（无硬编码 transition）
- `grep -rn "outline: none" <page-file>` → 0 结果（无阻断焦点的 outline:none）

**批次 A — 核心页面**（优先级最高，影响全局体验）：

| 页面 | 涉及文件 | CSS行数 | 特殊注意 |
|---|---|---|---|
| conversation/chatPage | `chatPage.vue`、`conversation.vue` | 340+1020 | 最复杂页面，含 SSE 流式、5 个 @keyframes、18px 硬编码圆角 |
| workspace | `workspace.vue`、`defaultPage.vue`、`workspacePage.vue`、`taskGraphPage.vue` | 290 | 4 个子页面，scrollbar-width:none 需处理 |
| homepage | `homepage.vue` | 160 | 已基本使用 token，工作量小 |

**批次 B — 功能页面**：

| 页面 | 涉及文件 | CSS行数 | 特殊注意 |
|---|---|---|---|
| agent | `agent.vue`、`agent-editor.vue` | 570+560 | 3+1 @keyframes、5 处非 token box-shadow、Monaco Editor |
| knowledge | `knowledge-file.vue` | 800 | 4 个 @keyframes，虽用 token 但体量需瘦身 |
| mcp-server | `mcp-server.vue` | 1900 | 重灾区：2 个 style 块、23 处内联 style、需合并+瘦身 |
| model | `model/` 目录 | — | 含 model-editor.vue |

**批次 C — 扩展页面**：

| 页面 | 涉及文件 | CSS行数 | 特殊注意 |
|---|---|---|---|
| interview/hubPage | `hubPage.vue` | 170 | 命名空间修正（`--text-*` → `--harmony-font-*`）、10 处 var fallback 色值 |
| interview/chatPage | `chatPage.vue` | 250 | 18px 硬编码圆角、typingBounce keyframe |
| interview/reportPage | `reportPage.vue` | 290 | 7 处硬编码 font-size、评分颜色 `#4caf50/#ff9800/#f44336` |
| voice-interview | `voice-interview/` 目录 | — | 含 AudioPlayer/Recorder |
| dashboard | `dashboard.vue` | 220 | ECharts 暗色主题适配、5 处内联 style |
| tool | `tool.vue` | 1370 | 重灾区：大量 `.dark` 前缀手动适配暗色模式需全部删除 |
| agent-skill | `agent-skill/` 目录 | — | non-scoped 样式块需清理 |
| profile | `profile/` 目录 | — | |
| configuration | `configuration/` 目录 | — | |
| mars | `mars/` 目录 | — | |
| construct | `construct/` 目录 | — | |
| notFound | `notFound.vue` | — | non-scoped 样式需修复 |

**批次 D — 面试模块子页面**：

| 页面 | 涉及文件 | 预估工作量 |
|---|---|---|
| interview/learning | `learningPage.vue` | 中 |
| interview/resume | `resumePage.vue` | 中 |
| interview/history | `historyPage.vue` | 中 |
| interview/JD解析 | `jdPage.vue` | 中 |

## 参考项目关键路径

| 文件 | 用途 |
|---|---|
| `references/2.theme/harmony-tokens.css` | 完整 design token CSS，直接复制 |
| `references/2.theme/mobile-scale.css` | 移动端间距/尺寸 token，直接复制 |
| `references/0.governance/component.json` | 组件注册表，含 Figma 节点映射和数值基线 |
| `references/3.component/*.md` | 13 个组件规范文档 |
| `references/4.template/*-tem.html` | 13 个 HTML 组件模板 |
| `references/0.governance/HarmonyOS Design.md` | 页面级设计原则 |
| `assets/HMSymbolVF_1.ttf` | HMSymbol 图标字体 |
| `assets/HMOSColorEmojiCompat.ttf` | Emoji 字体 |
| `assets/statusbar-*.png` | 状态栏 PNG 图标资源 |

## 约束与规则

1. **数值基线锁定**：所有组件的尺寸、间距、圆角必须与 `component.json` 的 `numeric_baseline` 一一对应，不允许近似值
2. **五态交互层**：hover / pressed / focus / active / select 使用 `::before` / `::after` 伪元素，颜色引用 `--harmony-interactive-*` token
3. **液态玻璃材质**：浮层组件使用 `backdrop-filter: blur() saturate()` + `mix-blend-mode: plus-lighter`
4. **HMSymbol 优先**：壳层组件强制使用 HMSymbol 字体图标，不允许 SVG 或 CSS 手绘替代
6. **主题切换**：保持 `[data-theme="light"]` / `[data-theme="dark"]` 机制，兼容鸿蒙 token 的 4 种模式（system/wearable × light/dark）

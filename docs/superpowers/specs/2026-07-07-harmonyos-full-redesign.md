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
│   └── ...                     # 业务组件（不变）
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

## 实施分期

### Phase 1: 基础设施

1. 用参考项目的 `harmony-tokens.css` 替换现有文件
2. 用参考项目的 `mobile-scale.css` 替换现有文件
3. 新增 `glass-mixins.css`（液态玻璃效果 token）
4. 新增 `hmsymbol.css`（HMSymbol 字体引入）
5. 部署字体文件到 `assets/`（HMSymbolVF_1.ttf、HMOSColorEmojiCompat.ttf）
6. 删除 `style.css` 中的业务变量映射，精简为全局重置 + transition 动画
7. 全局搜索替换：所有 `--color-*` / `--radius-*` / `--spacing-*` / `--font-size-*` 引用替换为对应 `--harmony-*` token

### Phase 2: 壳层组件

1. 实现 HStatusbar（从 statusbar-tem.html 提取，部署 PNG 图标资源）
2. 实现 HTitlebar（4 种变体，渐隐背板 + backdrop-filter）
3. 实现 HBottomTab（6 种变体，液态玻璃胶囊 + home indicator）
4. 实现 HAIBottomBar（AI 底部指示栏）
5. 更新 App.vue 壳层组装（响应式条件渲染）

### Phase 3: UI 组件库

1. 新建 HSearch、HSwitch、HToolbar、HList、HDivider、HCardView（按参考模板）
2. 重构 HButton、HChipsTab（对齐参考规范数值基线 + 交互态）
3. 全面重构 HDialog、HDrawer、HDropdown 等 15 个组件（统一标准：数值基线 + 五态交互 + 液态玻璃 + Token 直引）
4. HIcon 双模式扩展（HMSymbol + SVG 降级）
5. 注册新组件到 UI 插件（main.ts 中 app.use(UI)）

### Phase 4: 页面迁移

**批次 A（核心页面）：**
- conversation/chatPage
- workspace（defaultPage + workspacePage + taskGraphPage）
- homepage

**批次 B（功能页面）：**
- agent（agent.vue + agent-editor.vue）
- knowledge（knowledge-file.vue）
- mcp-server
- model

**批次 C（扩展页面）：**
- interview（hubPage + chatPage + reportPage）
- voice-interview
- dashboard、profile、configuration、tool、agent-skill、mars、construct

每个页面迁移步骤：
1. 替换业务变量为 `--harmony-*` 原生 token
2. 替换自定义样式为鸿蒙组件
3. 接入壳层组件（选择合适的 titlebar 变体）
4. 响应式验证（桌面 + 移动端）

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

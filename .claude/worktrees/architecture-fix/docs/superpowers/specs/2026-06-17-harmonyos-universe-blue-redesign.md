# AgentChat 鸿蒙宇宙蓝 全局风格改造设计文档

> 日期: 2026-06-17
> 作者: Claude + 用户协作
> 版本: v1.0

---

## 1. 概述

将 AgentChat v2.5.0 前端的全局视觉风格从当前的黑白色系 + 混乱蓝色硬编码，全面改造为**鸿蒙宇宙蓝（HarmonyOS Universe Blue）**扁平极简风格。同时完全移除 Element Plus UI 库，自建完整的原生 Vue 3 组件库。

### 1.1 改造范围

- **31 个 .vue 页面文件**，分布在 15 个页面目录
- **5 个公共组件**（agentCard、commonCard、historyCard、drawer、create_agent）
- **294 个 Element Plus 模板标签**，跨 24 个文件
- **372 处 ElMessage API 调用**，跨 30 个文件
- **18 处 ElMessageBox 调用**，跨 13 个文件
- **12 处 v-loading 指令**
- **74 处 el-icon + @element-plus/icons-vue** 引用
- **全局 CSS 变量体系**（style.css）
- **Element Plus 依赖**（package.json、main.ts）

### 1.2 设计决策汇总

| 决策项 | 选择 | 理由 |
|--------|------|------|
| 色彩方案 | 双模式：深空蓝（暗）+ 晴空蓝（亮） | 兼顾不同使用场景和个人偏好 |
| UI 框架 | 移除 Element Plus，全部原生实现 | 完全掌控视觉风格，零第三方 UI 依赖 |
| 组件策略 | 自建完整组件库（19 个组件） | 架构干净，可维护性最强 |
| 图标系统 | HarmonyOS Sans Symbols | 与鸿蒙设计语言一致 |
| 默认主题 | 跟随系统偏好（prefers-color-scheme） | 最佳首次体验 |
| 动效风格 | 极简微动效（150-200ms，opacity + transform） | 扁平极简不喧宾夺主 |
| 圆角风格 | 大圆角（8-16px） | HarmonyOS 标志性圆润风格 |

---

## 2. 主题系统设计

### 2.1 CSS 变量体系

在 `src/frontend/src/style.css` 的 `:root` 上建立完整 token 体系。使用 `[data-theme="dark"]` 和 `[data-theme="light"]` 属性选择器区分暗亮模式。

#### 暗色模式 `[data-theme="dark"]`

```css
/* 背景层（三级） */
--color-bg:           #0a1628;   /* 主背景 */
--color-bg-secondary: #0d2137;   /* 次背景（侧边栏、卡片） */
--color-bg-tertiary:  #132d50;   /* 三级背景（输入框、悬浮） */

/* 主色 */
--color-primary:       #3370ff;  /* 主色蓝 */
--color-primary-hover: #5c9aff;  /* hover 态 */
--color-primary-active:#1a5cd7;  /* active 态 */
--color-primary-bg:    rgba(51,112,255,0.12);  /* 主色浅背景 */

/* 文字 */
--color-text-primary:   #e8f0fe; /* 主文字 */
--color-text-secondary: #a0b4d0; /* 次文字 */
--color-text-tertiary:  #6b8299; /* 辅助文字 */
--color-text-disabled:  #4a6070; /* 禁用文字 */

/* 边框 */
--color-border:          rgba(255,255,255,0.08);  /* 默认边框 */
--color-border-hover:    rgba(255,255,255,0.15);  /* hover 边框 */
--color-border-focus:    #3370ff;                  /* 聚焦边框 */

/* 功能色 */
--color-success:     #34d399;
--color-success-bg:  rgba(52,211,153,0.12);
--color-warning:     #fbbf24;
--color-warning-bg:  rgba(251,191,36,0.12);
--color-danger:      #f87171;
--color-danger-bg:   rgba(248,113,113,0.12);
--color-error:       #e5432a;
--color-error-bg:    rgba(229,67,42,0.12);

/* 阴影（暗色用蓝光辉光） */
--shadow-sm:    0 1px 3px rgba(0,0,0,0.3);
--shadow-md:    0 4px 12px rgba(0,0,0,0.4);
--shadow-card:  0 2px 8px rgba(0,0,0,0.3), 0 0 1px rgba(51,112,255,0.1);
--shadow-glow:  0 0 20px rgba(51,112,255,0.15);  /* 蓝光辉光 */
```

#### 亮色模式 `[data-theme="light"]`

```css
/* 背景层（三级） */
--color-bg:           #f0f5ff;   /* 主背景 */
--color-bg-secondary: #ffffff;   /* 次背景 */
--color-bg-tertiary:  #e8f0fe;   /* 三级背景 */

/* 主色 */
--color-primary:       #3370ff;
--color-primary-hover: #5c9aff;
--color-primary-active:#1a5cd7;
--color-primary-bg:    #e8f0fe;

/* 文字 */
--color-text-primary:   #0d2137;
--color-text-secondary: #4a6785;
--color-text-tertiary:  #8ca0b8;
--color-text-disabled:  #b0c0d0;

/* 边框 */
--color-border:          #d0e0ff;
--color-border-hover:    #b0ccff;
--color-border-focus:    #3370ff;

/* 功能色 */
--color-success:     #059669;
--color-success-bg:  #d1fae5;
--color-warning:     #d97706;
--color-warning-bg:  #fef3c7;
--color-danger:      #dc2626;
--color-danger-bg:   #fee2e2;
--color-error:       #dc2626;
--color-error-bg:    #fee2e2;

/* 阴影（亮色用柔和灰影） */
--shadow-sm:    0 1px 3px rgba(0,0,0,0.04);
--shadow-md:    0 4px 12px rgba(0,0,0,0.06);
--shadow-card:  0 2px 8px rgba(0,0,0,0.06);
--shadow-glow:  0 0 0 transparent;  /* 亮色不使用辉光 */
```

#### 共用 Tokens（不随主题变化）

```css
/* 圆角 */
--radius-sm:   8px;
--radius-md:   12px;
--radius-lg:   16px;
--radius-full: 9999px;

/* 间距 */
--spacing-xs:  8px;
--spacing-sm:  12px;
--spacing-md:  16px;
--spacing-lg:  20px;
--spacing-xl:  24px;
--spacing-2xl: 32px;

/* 动效 */
--duration-fast:   150ms;
--duration-normal: 200ms;
--easing:          cubic-bezier(0.4, 0, 0.2, 1);

/* 字体 */
--font-family: 'HarmonyOS Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
--font-size-xs:   12px;
--font-size-sm:   13px;
--font-size-base: 14px;
--font-size-lg:   16px;
--font-size-xl:   20px;
--font-size-2xl:  24px;

/* 层级 */
--z-dropdown:  100;
--z-dialog:    200;
--z-toast:     300;
--z-loading:   400;
```

### 2.2 主题切换机制

```typescript
// src/composables/useTheme.ts
import { ref, computed, watch, onMounted } from 'vue'
import { useLocalStorage } from '@vueuse/core'

type ThemeMode = 'light' | 'dark' | 'system'

export function useTheme() {
  const mode = useLocalStorage<ThemeMode>('agentchat-theme', 'system')
  const systemPrefersDark = ref(false)

  const resolved = computed<'light' | 'dark'>(() => {
    if (mode.value === 'system') {
      return systemPrefersDark.value ? 'dark' : 'light'
    }
    return mode.value
  })

  watch(resolved, (theme) => {
    document.documentElement.setAttribute('data-theme', theme)
  }, { immediate: true })

  onMounted(() => {
    const mq = window.matchMedia('(prefers-color-scheme: dark)')
    systemPrefersDark.value = mq.matches
    mq.addEventListener('change', (e) => {
      systemPrefersDark.value = e.matches
    })
  })

  function toggle() {
    mode.value = resolved.value === 'dark' ? 'light' : 'dark'
  }

  return { mode, resolved, toggle }
}
```

- `document.documentElement.setAttribute('data-theme', mode)` 切换主题
- 首次访问读取 `localStorage.agentchat-theme`，不存在则跟随系统
- 切换时背景和文字颜色通过 CSS transition 平滑过渡

---

## 3. 组件库设计

### 3.1 组件清单（19 个）

在 `src/components/ui/` 下建立鸿蒙风格组件库，所有组件统一前缀 `H`。

#### P0 — 核心基础组件（4 个）

| 组件 | 替换目标 | 使用量 | 说明 |
|------|---------|--------|------|
| HButton | el-button | 80 处 / 22 文件 | primary / secondary / text / danger 变体，支持 size、disabled、loading |
| HIcon | el-icon + @element-plus/icons-vue | 74 处 / 12 文件 | 封装 HarmonyOS Sans Symbols 图标 |
| HInput | el-input | 28 处 / 15 文件 | 支持 v-model、prefix/suffix 插槽、clearable、error 状态 |
| HMessage | ElMessage（API） | 372 处 / 30 文件 | HMessage.success/error/warning/info()，纯函数调用 |

#### P1 — 表单与交互组件（6 个）

| 组件 | 替换目标 | 使用量 | 说明 |
|------|---------|--------|------|
| HSelect + HOption | el-select + el-option | 33 处 / 5 文件 | 自定义下拉面板，支持搜索过滤 |
| HForm + HFormItem | el-form + el-form-item | 22 处 / 4 文件 | 表单容器 + 标签/校验/布局 |
| HDialog | el-dialog | 3 处 / 3 文件 | 模态对话框，遮罩 + 居中 + 关闭按钮 |
| HMessageBox | ElMessageBox（API） | 18 处 / 13 文件 | confirm/alert/prompt 函数式调用 |
| HTooltip | el-tooltip | 15 处 / 5 文件 | hover 提示，支持 4 方向定位 |
| HDropdown | el-dropdown | 9 处 / 2 文件 | 下拉菜单，点击触发 |

#### P2 — 专用组件（8 个）

| 组件 | 替换目标 | 使用量 | 说明 |
|------|---------|--------|------|
| HTag | el-tag | 7 处 / 3 文件 | 彩色标签，支持 closable |
| HTable | el-table | 仅 1 文件 | 表格（mcp-server.vue），简化实现 |
| HUpload | el-upload | 6 处 / 5 文件 | 文件上传，支持拖拽 |
| HDrawer | el-drawer | 1 处 | 侧边抽屉 |
| HTabs | el-tabs | 1 处 | 选项卡（tool.vue） |
| HScrollbar | el-scrollbar | 2 处 | 自定义滚动条 |
| HAvatar | el-avatar | 2 处 | 头像 |
| HSkeleton | el-skeleton | 1 处 | 骨架屏 |
| HLoading | v-loading 指令 | 12 处 | 自定义指令，loading 遮罩 |

### 3.2 组件 API 设计原则

1. **TypeScript props**：所有 props 使用 `defineProps<{}>()` + 接口类型
2. **v-model 支持**：HInput、HSelect 等表单组件统一 `modelValue` + `update:modelValue`
3. **CSS 变量驱动**：组件内部只引用 `var(--xxx)` tokens，零硬编码色值
4. **暗亮自适应**：组件样式天然跟随 `[data-theme]` 切换
5. **插槽优先**：保留 `default`、`prefix`、`suffix` 等具名插槽，与 Element Plus 的 slot 模式对齐降低迁移成本
6. **emit 事件对齐**：组件事件名与 Element Plus 尽量保持一致（如 `change`、`click`、`clear`、`close`）

### 3.3 组件目录结构

```
src/components/ui/
├── index.ts              # 统一导出 + Vue 全局注册插件
├── tokens/
│   └── _variables.scss   # SCSS 变量（与 CSS 变量同步）
├── HButton/
│   ├── HButton.vue
│   └── index.ts
├── HIcon/
│   ├── HIcon.vue
│   └── index.ts
├── HInput/
│   ├── HInput.vue
│   └── index.ts
├── HSelect/
│   ├── HSelect.vue
│   ├── HOption.vue
│   └── index.ts
├── HForm/
│   ├── HForm.vue
│   ├── HFormItem.vue
│   └── index.ts
├── HDialog/
│   ├── HDialog.vue
│   └── index.ts
├── HMessage/
│   ├── HMessage.vue      # 渲染单条消息
│   ├── service.ts        # HMessage.success/error/warning/info() API
│   └── index.ts
├── HMessageBox/
│   ├── HMessageBox.vue
│   ├── service.ts        # confirm/alert/prompt API
│   └── index.ts
├── HTooltip/
│   ├── HTooltip.vue
│   └── index.ts
├── HDropdown/
│   ├── HDropdown.vue
│   ├── HDropdownMenu.vue
│   ├── HDropdownItem.vue
│   └── index.ts
├── HTag/
│   ├── HTag.vue
│   └── index.ts
├── HTable/
│   ├── HTable.vue
│   ├── HTableColumn.vue
│   └── index.ts
├── HUpload/
│   ├── HUpload.vue
│   └── index.ts
├── HDrawer/
│   ├── HDrawer.vue
│   └── index.ts
├── HTabs/
│   ├── HTabs.vue
│   ├── HTabPane.vue
│   └── index.ts
├── HScrollbar/
│   ├── HScrollbar.vue
│   └── index.ts
├── HAvatar/
│   ├── HAvatar.vue
│   └── index.ts
├── HSkeleton/
│   ├── HSkeleton.vue
│   └── index.ts
└── HLoading/
    ├── directive.ts       # v-h-loading 指令
    └── index.ts
```

### 3.4 全局注册插件

```typescript
// src/components/ui/index.ts
import HButton from './HButton/HButton.vue'
import HInput from './HInput/HInput.vue'
// ... 所有组件

export { HButton, HInput, HMessage, ... }

export default {
  install(app: App) {
    app.component('HButton', HButton)
    app.component('HInput', HInput)
    // ...
    app.directive('h-loading', hLoadingDirective)
  }
}
```

在 `main.ts` 中注册：
```typescript
import UI from '@/components/ui'
app.use(UI)
```

---

## 4. 图标系统

### 4.1 HarmonyOS Sans Symbols

- 安装方式：npm 包或 CDN 引入 HarmonyOS Sans Symbols 字体文件
- 使用方式：`<HIcon name="edit" />` 渲染为 `<span class="h-icon h-icon-edit"></span>`
- HIcon 组件内部使用 CSS class + 字体图标实现
- 支持 size 和 color props，颜色默认继承父元素

### 4.2 迁移映射

保留一份 `src/components/ui/HIcon/icon-map.ts`，记录 Element Plus 图标到 HarmonyOS 图标的映射关系：

```typescript
// 常见映射
Edit       → edit
Delete     → delete
Search     → search
Plus       → add
Setting    → settings
User       → user
// ... 完整映射在实施时补充
```

---

## 5. 页面迁移方案

### 5.1 迁移顺序（5 批次，按复杂度递增）

**第一批 — 基础布局层（2 个文件）**

| 文件 | el- 标签数 | 复杂度 |
|------|-----------|--------|
| `pages/index.vue`（主布局） | 4 | 低 |
| `pages/workspace/workspace.vue` | 5 | 低 |

**第二批 — 低复杂度页面（5 个文件）**

| 文件 | el- 标签数 |
|------|-----------|
| `pages/login/login.vue` | 3 |
| `pages/login/register.vue` | 5 |
| `pages/agent/agent.vue` | 6 |
| `pages/configuration/configuration.vue` | 2 |
| `pages/conversation/test.vue` | 2 |

**第三批 — 中等复杂度页面（9 个文件）**

| 文件 | el- 标签数 |
|------|-----------|
| `pages/knowledge/knowledge-file.vue` | 3 |
| `pages/agent/AgentDebug.vue` | 3 |
| `pages/dashboard/dashboard.vue` | 12 |
| `pages/knowledge/knowledge.vue` | 12 |
| `pages/profile/profile.vue` | 13 |
| `pages/agent/agent-fixed.vue` | 9 |
| `pages/conversation/demo.vue` | 10 |
| `pages/model/model.vue` | 11 |
| `pages/conversation/chatPage/chatPage.vue` | 14 |

**第四批 — 高复杂度页面（5 个文件）**

| 文件 | el- 标签数 |
|------|-----------|
| `pages/mcp-server/mcp-chat.vue` | 14 |
| `pages/tool/tool.vue` | 14 |
| `pages/model/model-editor.vue` | 21 |
| `pages/mcp-server/mcp-server.vue` | 21 |
| `pages/agent/agent-editor.vue` | 34 |

**第五批 — 最重页面 + 公共组件（3 个文件）**

| 文件 | el- 标签数 |
|------|-----------|
| `components/dialog/create_agent/create_agent.vue` | 27 |
| `components/drawer/drawer.vue` | 6 |
| `pages/agent-skill/agent-skill.vue` | 43 |

### 5.2 每个文件的迁移步骤

1. **替换模板标签**：`<el-button>` → `<HButton>`，`<el-input>` → `<HInput>` 等
2. **替换 API 调用**：`ElMessage.success()` → `HMessage.success()`，`ElMessageBox.confirm()` → `HMessageBox.confirm()`
3. **替换图标**：`<el-icon><Edit /></el-icon>` → `<HIcon name="edit" />`
4. **样式适配**：移除 Element Plus 特有的 class 覆写，确认组件在新主题下视觉正确

### 5.3 ElMessage 批量替换策略

372 处 ElMessage 是最大的改动面，调用模式高度统一：

```typescript
// 替换前
import { ElMessage } from 'element-plus'
ElMessage.success('操作成功')
ElMessage.error('操作失败')

// 替换后
import { HMessage } from '@/components/ui'
HMessage.success('操作成功')
HMessage.error('操作失败')
```

- HMessage service API 完全对齐 Element Plus 的调用方式
- `utils/dialog.ts` 中的 `ElMessageBox.confirm()` 封装替换为 `HMessageBox.confirm()`
- 可通过全局搜索替换批量处理

### 5.4 类型迁移

| Element Plus 类型 | 替换为 |
|-------------------|--------|
| `UploadProps` | 自定义 `HUploadProps` |
| `UploadUserFile` | 自定义 `HUploadFile` |
| `FormInstance` | `HFormInstance` |
| `FormRules` | `HFormRules` |

---

## 6. 依赖清理

### 6.1 移除的依赖

在所有页面迁移完成后，从 `package.json` 中移除：

```json
// 移除
"element-plus": "^2.7.x"
"@element-plus/icons-vue": "^2.x.x"
"unplugin-vue-components": "^0.x.x"   // 如果仅用于 Element Plus 自动导入
"unplugin-auto-import": "^0.x.x"      // 如果仅用于 Element Plus
```

### 6.2 移除的配置

- `vite.config.ts` 中的 `Components({ resolvers: [ElementPlusResolver()] })` 和 `AutoImport({ resolvers: [ElementPlusResolver()] })`
- `main.ts` 中的 `import 'element-plus/dist/index.css'`
- `components.d.ts` 和 `auto-imports.d.ts` 中 Element Plus 相关的自动生成类型

### 6.3 新增的依赖

```json
// 新增
"harmonyos-sans-symbols": "latest"  // HarmonyOS Sans Symbols 图标字体
```

---

## 7. 验收标准

### 7.1 功能验收

- [ ] 全部 31 个页面在暗色和亮色模式下正常显示
- [ ] 主题切换（手动 + 系统跟随）工作正常
- [ ] 所有表单（登录、注册、创建智能体、编辑模型、编辑 Agent）提交正常
- [ ] 所有消息提示（成功、错误、警告、信息）显示正常
- [ ] 所有确认对话框（删除、退出）功能正常
- [ ] 文件上传功能正常
- [ ] 侧边栏下拉菜单正常
- [ ] MCP Server 表格页面正常
- [ ] 聊天页面流式对话正常
- [ ] ECharts 图表在暗色模式下可读

### 7.2 视觉验收

- [ ] 所有颜色通过 CSS 变量引用，无硬编码色值
- [ ] 暗色模式：深空蓝背景 + 亮蓝主色，层次分明
- [ ] 亮色模式：晴空蓝白背景 + 蓝色主色，清爽简洁
- [ ] 圆角统一 8-16px 范围
- [ ] 图标统一使用 HarmonyOS Sans Symbols
- [ ] 微动效 150-200ms，不突兀

### 7.3 技术验收

- [ ] Element Plus 依赖已从 package.json 移除
- [ ] `@element-plus/icons-vue` 依赖已移除
- [ ] 代码中无 `el-` 前缀标签残留
- [ ] 代码中无 `ElMessage`、`ElMessageBox`、`ElLoading` 引用残留
- [ ] 组件库通过 Vue 插件全局注册
- [ ] TypeScript 类型无报错
- [ ] 构建成功，无警告

---

## 8. 风险与注意事项

1. **Monaco Editor**：Monaco Editor 有自己独立的主题系统，需要单独配置暗色/亮色主题与鸿蒙蓝对齐
2. **md-editor-v3**：Markdown 编辑器主题也需要适配，通过其主题 API 切换
3. **ECharts**：图表组件需要根据当前主题动态切换配色方案
4. **vditor**：如使用了 vditor 编辑器，其主题也需单独适配
5. **Google Fonts**：当前加载了 ZCOOL KuaiLe、Zhi Mang Xing、Ma Shan Zheng 等字体，需确认是否保留或替换为 HarmonyOS Sans
6. **第三方组件样式泄漏**：确保 Monaco Editor、md-editor-v3 等第三方组件的样式不与新主题冲突

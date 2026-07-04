# AgentChat 鸿蒙宇宙蓝 全局风格改造 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 AgentChat v2.5.0 前端从 Element Plus + 黑白色系改造为鸿蒙宇宙蓝扁平极简风格，完全移除 Element Plus 依赖，自建 19 个原生 Vue 3 组件。

**Architecture:** 建立 CSS 变量驱动的双模式主题系统（深空蓝暗色 + 晴空蓝亮色），在 `src/components/ui/` 下构建前缀为 `H` 的完整组件库，按复杂度分 5 批次迁移 38 个 .vue 文件，最后移除 Element Plus 及相关依赖。

**Tech Stack:** Vue 3.4 + TypeScript + Vite 5 + Sass + @vueuse/core + HarmonyOS Sans Symbols

**参考文档:** `docs/superpowers/specs/2026-06-17-harmonyos-universe-blue-redesign.md`

---

## 文件结构总览

### 新建文件

```
src/frontend/src/
├── composables/
│   └── useTheme.ts                    # 主题切换 composable
├── components/ui/
│   ├── index.ts                       # 统一导出 + Vue 全局注册插件
│   ├── HButton/
│   │   ├── HButton.vue
│   │   └── index.ts
│   ├── HIcon/
│   │   ├── HIcon.vue
│   │   ├── icon-map.ts               # Element Plus 图标映射
│   │   └── index.ts
│   ├── HInput/
│   │   ├── HInput.vue
│   │   └── index.ts
│   ├── HMessage/
│   │   ├── HMessage.vue              # 单条消息渲染
│   │   ├── service.ts                # HMessage.success/error/warning/info()
│   │   └── index.ts
│   ├── HMessageBox/
│   │   ├── HMessageBox.vue
│   │   ├── service.ts                # confirm/alert/prompt API
│   │   └── index.ts
│   ├── HSelect/
│   │   ├── HSelect.vue
│   │   ├── HOption.vue
│   │   └── index.ts
│   ├── HForm/
│   │   ├── HForm.vue
│   │   ├── HFormItem.vue
│   │   └── index.ts
│   ├── HDialog/
│   │   ├── HDialog.vue
│   │   └── index.ts
│   ├── HTooltip/
│   │   ├── HTooltip.vue
│   │   └── index.ts
│   ├── HDropdown/
│   │   ├── HDropdown.vue
│   │   ├── HDropdownMenu.vue
│   │   ├── HDropdownItem.vue
│   │   └── index.ts
│   ├── HTag/
│   │   ├── HTag.vue
│   │   └── index.ts
│   ├── HTable/
│   │   ├── HTable.vue
│   │   ├── HTableColumn.vue
│   │   └── index.ts
│   ├── HUpload/
│   │   ├── HUpload.vue
│   │   └── index.ts
│   ├── HDrawer/
│   │   ├── HDrawer.vue
│   │   └── index.ts
│   ├── HTabs/
│   │   ├── HTabs.vue
│   │   ├── HTabPane.vue
│   │   └── index.ts
│   ├── HScrollbar/
│   │   ├── HScrollbar.vue
│   │   └── index.ts
│   ├── HAvatar/
│   │   ├── HAvatar.vue
│   │   └── index.ts
│   ├── HSkeleton/
│   │   ├── HSkeleton.vue
│   │   └── index.ts
│   └── HLoading/
│       ├── directive.ts              # v-h-loading 指令
│       └── index.ts
```

### 修改文件

```
src/frontend/src/
├── style.css                          # 替换 CSS 变量为鸿蒙蓝主题
├── main.ts                            # 注册 UI 插件，移除 Element Plus CSS
├── App.vue                            # 添加主题初始化
├── utils/dialog.ts                    # 迁移到 HMessageBox
├── utils/function.ts                  # 如有 ElMessage 引用则迁移
├── store/history_chat_msg/index.ts    # 如有 ElMessage 引用则迁移
├── pages/index.vue                    # 迁移 el-dropdown → HDropdown
├── pages/login/login.vue              # 迁移 el-input/el-button → HInput/HButton
├── pages/login/register.vue           # 同上
├── pages/agent/agent.vue              # 迁移 el-tag 等
├── pages/agent/agent-editor.vue       # 高复杂度，34 处 el- 标签
├── pages/agent/agent-fixed.vue
├── pages/agent/AgentDebug.vue
├── pages/agent-skill/agent-skill.vue  # 最重，43 处 el- 标签
├── pages/configuration/configuration.vue
├── pages/conversation/test.vue
├── pages/conversation/demo.vue
├── pages/conversation/chatPage/chatPage.vue
├── pages/dashboard/dashboard.vue
├── pages/knowledge/knowledge.vue
├── pages/knowledge/knowledge-file.vue
├── pages/model/model.vue
├── pages/model/model-editor.vue
├── pages/mcp-server/mcp-server.vue
├── pages/mcp-server/mcp-chat.vue
├── pages/profile/profile.vue
├── pages/tool/tool.vue
├── pages/workspace/workspace.vue
├── components/agentCard/agentCard.vue
├── components/commonCard/commonCard.vue
├── components/dialog/create_agent/create_agent.vue
├── components/dialog/create_agent/AgentFormDialog.vue
├── components/drawer/drawer.vue
└── components/historyCard/histortCard.vue

src/frontend/
├── package.json                       # 移除 element-plus 等依赖
└── vite.config.ts                     # 移除 ElementPlusResolver
```

---

## Phase 1: 主题系统基础

### Task 1: 替换 CSS 变量体系

**Files:**
- Modify: `src/frontend/src/style.css`

- [ ] **Step 1: 替换 style.css 中的 `:root` 变量块**

将 `style.css` 第 1-36 行的现有 `:root` 变量替换为完整的鸿蒙蓝双模式变量体系。保留 `:root` 作为暗色模式默认，添加 `[data-theme="dark"]` 和 `[data-theme="light"]` 选择器。

```css
/* ========== 鸿蒙宇宙蓝 主题变量 ========== */

/* 暗色模式（默认） */
:root,
[data-theme="dark"] {
  /* 背景层（三级） */
  --color-bg:           #0a1628;
  --color-bg-secondary: #0d2137;
  --color-bg-tertiary:  #132d50;

  /* 主色 */
  --color-primary:       #3370ff;
  --color-primary-hover: #5c9aff;
  --color-primary-active:#1a5cd7;
  --color-primary-bg:    rgba(51,112,255,0.12);

  /* 文字 */
  --color-text-primary:   #e8f0fe;
  --color-text-secondary: #a0b4d0;
  --color-text-tertiary:  #6b8299;
  --color-text-disabled:  #4a6070;

  /* 边框 */
  --color-border:          rgba(255,255,255,0.08);
  --color-border-hover:    rgba(255,255,255,0.15);
  --color-border-focus:    #3370ff;
  --color-border-secondary: rgba(255,255,255,0.12);

  /* 功能色 */
  --color-success:     #34d399;
  --color-success-bg:  rgba(52,211,153,0.12);
  --color-warning:     #fbbf24;
  --color-warning-bg:  rgba(251,191,36,0.12);
  --color-danger:      #f87171;
  --color-danger-bg:   rgba(248,113,113,0.12);
  --color-error:       #e5432a;
  --color-error-bg:    rgba(229,67,42,0.12);

  /* 阴影 */
  --shadow-sm:    0 1px 3px rgba(0,0,0,0.3);
  --shadow-md:    0 4px 12px rgba(0,0,0,0.4);
  --shadow-card:  0 2px 8px rgba(0,0,0,0.3), 0 0 1px rgba(51,112,255,0.1);
  --shadow-card-hover: 0 4px 16px rgba(0,0,0,0.4), 0 0 2px rgba(51,112,255,0.15);
  --shadow-glow:  0 0 20px rgba(51,112,255,0.15);
}

/* 亮色模式 */
[data-theme="light"] {
  --color-bg:           #f0f5ff;
  --color-bg-secondary: #ffffff;
  --color-bg-tertiary:  #e8f0fe;

  --color-primary:       #3370ff;
  --color-primary-hover: #5c9aff;
  --color-primary-active:#1a5cd7;
  --color-primary-bg:    #e8f0fe;

  --color-text-primary:   #0d2137;
  --color-text-secondary: #4a6785;
  --color-text-tertiary:  #8ca0b8;
  --color-text-disabled:  #b0c0d0;

  --color-border:          #d0e0ff;
  --color-border-hover:    #b0ccff;
  --color-border-focus:    #3370ff;
  --color-border-secondary: #d0e0ff;

  --color-success:     #059669;
  --color-success-bg:  #d1fae5;
  --color-warning:     #d97706;
  --color-warning-bg:  #fef3c7;
  --color-danger:      #dc2626;
  --color-danger-bg:   #fee2e2;
  --color-error:       #dc2626;
  --color-error-bg:    #fee2e2;

  --shadow-sm:    0 1px 3px rgba(0,0,0,0.04);
  --shadow-md:    0 4px 12px rgba(0,0,0,0.06);
  --shadow-card:  0 2px 8px rgba(0,0,0,0.06);
  --shadow-card-hover: 0 4px 16px rgba(0,0,0,0.08);
  --shadow-glow:  0 0 0 transparent;
}

/* 共用 Tokens（不随主题变化） */
:root {
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
}
```

- [ ] **Step 2: 更新全局基础样式**

在同一个 `style.css` 中，替换第 38 行以后的全局样式，移除所有 Element Plus 覆写（`.el-overlay`、`.el-message-box`、`.delete-confirm-dialog` 等），替换为：

```css
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: var(--font-family);
}

body {
  background-color: var(--color-bg);
  color: var(--color-text-primary);
  transition: background-color var(--duration-normal) var(--easing),
              color var(--duration-normal) var(--easing);
}

/* 主题过渡动画 */
html {
  transition: background-color var(--duration-normal) var(--easing);
}

/* Markdown 编辑器透明背景适配 */
.md-editor {
  background-color: transparent !important;
}

.md-editor-preview-wrapper {
  padding: 0 !important;
}
```

- [ ] **Step 3: 验证**

运行 `cd src/frontend && npm run dev`，打开浏览器确认：
- 暗色模式下页面背景变为深蓝色 `#0a1628`
- 文字变为浅蓝白色
- 页面整体呈深蓝色调

- [ ] **Step 4: 提交**

```bash
git add src/frontend/src/style.css
git commit -m "feat(theme): replace CSS variables with HarmonyOS Universe Blue dual-mode system"
```

---

### Task 2: 创建 useTheme composable

**Files:**
- Create: `src/frontend/src/composables/useTheme.ts`

- [ ] **Step 1: 创建 composables 目录和 useTheme.ts**

```typescript
// src/frontend/src/composables/useTheme.ts
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

- [ ] **Step 2: 在 App.vue 中初始化主题**

读取当前 `App.vue`，在 `<script setup>` 中添加：

```typescript
import { useTheme } from './composables/useTheme'
const { resolved } = useTheme()
```

- [ ] **Step 3: 验证**

运行 dev server，打开浏览器 DevTools → Application → Local Storage，确认 `agentchat-theme` 键存在。手动切换 `data-theme` 属性在 `light`/`dark` 之间，确认页面颜色随之变化。

- [ ] **Step 4: 提交**

```bash
git add src/frontend/src/composables/useTheme.ts src/frontend/src/App.vue
git commit -m "feat(theme): add useTheme composable with system preference detection"
```

---

## Phase 2: P0 核心组件（HButton、HIcon、HInput、HMessage）

### Task 3: HButton 组件

**Files:**
- Create: `src/frontend/src/components/ui/HButton/HButton.vue`
- Create: `src/frontend/src/components/ui/HButton/index.ts`

- [ ] **Step 1: 创建 HButton.vue**

```vue
<!-- src/frontend/src/components/ui/HButton/HButton.vue -->
<script setup lang="ts">
interface Props {
  type?: 'primary' | 'secondary' | 'text' | 'danger'
  size?: 'small' | 'medium' | 'large'
  disabled?: boolean
  loading?: boolean
  block?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  type: 'primary',
  size: 'medium',
  disabled: false,
  loading: false,
  block: false,
})

defineEmits<{
  click: [event: MouseEvent]
}>()
</script>

<template>
  <button
    class="h-button"
    :class="[
      `h-button--${type}`,
      `h-button--${size}`,
      { 'h-button--disabled': disabled, 'h-button--loading': loading, 'h-button--block': block }
    ]"
    :disabled="disabled || loading"
    @click="$emit('click', $event)"
  >
    <span v-if="loading" class="h-button__spinner"></span>
    <slot />
  </button>
</template>

<style scoped>
.h-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border: none;
  border-radius: var(--radius-md);
  font-family: var(--font-family);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--duration-fast) var(--easing);
  white-space: nowrap;
  user-select: none;
}

/* Sizes */
.h-button--small {
  height: 32px;
  padding: 0 12px;
  font-size: var(--font-size-sm);
}
.h-button--medium {
  height: 36px;
  padding: 0 16px;
  font-size: var(--font-size-base);
}
.h-button--large {
  height: 44px;
  padding: 0 24px;
  font-size: var(--font-size-lg);
}

/* Primary */
.h-button--primary {
  background: var(--color-primary);
  color: #ffffff;
}
.h-button--primary:hover:not(:disabled) {
  background: var(--color-primary-hover);
}
.h-button--primary:active:not(:disabled) {
  background: var(--color-primary-active);
}

/* Secondary */
.h-button--secondary {
  background: var(--color-primary-bg);
  color: var(--color-primary);
}
.h-button--secondary:hover:not(:disabled) {
  background: var(--color-primary);
  color: #ffffff;
}

/* Text */
.h-button--text {
  background: transparent;
  color: var(--color-primary);
}
.h-button--text:hover:not(:disabled) {
  background: var(--color-primary-bg);
}

/* Danger */
.h-button--danger {
  background: var(--color-danger);
  color: #ffffff;
}
.h-button--danger:hover:not(:disabled) {
  opacity: 0.9;
}

/* Disabled */
.h-button--disabled,
.h-button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* Loading */
.h-button--loading {
  position: relative;
  color: transparent;
}
.h-button__spinner {
  position: absolute;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: h-spin 0.6s linear infinite;
}

/* Block */
.h-button--block {
  width: 100%;
}

@keyframes h-spin {
  to { transform: rotate(360deg); }
}
</style>
```

- [ ] **Step 2: 创建 index.ts 导出**

```typescript
// src/frontend/src/components/ui/HButton/index.ts
export { default as HButton } from './HButton.vue'
```

- [ ] **Step 3: 提交**

```bash
git add src/frontend/src/components/ui/HButton/
git commit -m "feat(ui): add HButton component with primary/secondary/text/danger variants"
```

---

### Task 4: HIcon 组件

**Files:**
- Create: `src/frontend/src/components/ui/HIcon/HIcon.vue`
- Create: `src/frontend/src/components/ui/HIcon/icon-map.ts`
- Create: `src/frontend/src/components/ui/HIcon/index.ts`

- [ ] **Step 1: 创建图标映射表**

```typescript
// src/frontend/src/components/ui/HIcon/icon-map.ts
/** Element Plus 图标名 → HarmonyOS Sans Symbols 字符映射 */
export const iconMap: Record<string, string> = {
  Edit:           '',
  Delete:         '',
  Search:         '',
  Plus:           '',
  Setting:        '',
  User:           '',
  SwitchButton:   '',
  ArrowDown:      '',
  ArrowRight:     '',
  Close:          '',
  Check:          '',
  Warning:        '',
  InfoFilled:     '',
  SuccessFilled:  '',
  CircleClose:    '',
  Loading:        '',
  Upload:         '',
  Download:       '',
  More:           '',
  Refresh:        '',
  CopyDocument:   '',
  ChatDotRound:   '',
  Connection:     '',
  Document:       '',
  Folder:         '',
  View:           '',
  Hide:           '',
  Star:           '',
  StarFilled:     '',
  Menu:           '',
  Operation:      '',
}

export function getIconChar(name: string): string {
  return iconMap[name] || name
}
```

> **注意：** 上面的 Unicode 码位是占位符。实际实施时需要根据 HarmonyOS Sans Symbols 字体的实际码位表进行替换。如果字体不可用，可临时使用 SVG 图标方案或 emoji 替代。

- [ ] **Step 2: 创建 HIcon.vue**

```vue
<!-- src/frontend/src/components/ui/HIcon/HIcon.vue -->
<script setup lang="ts">
import { computed } from 'vue'
import { getIconChar } from './icon-map'

interface Props {
  name: string
  size?: number | string
  color?: string
}

const props = withDefaults(defineProps<Props>(), {
  size: 16,
})

const iconChar = computed(() => getIconChar(props.name))
const sizeStyle = computed(() => typeof props.size === 'number' ? `${this.size}px` : props.size)
</script>

<template>
  <span
    class="h-icon"
    :style="{ fontSize: sizeStyle, color: color || 'inherit' }"
    :title="name"
  >{{ iconChar }}</span>
</template>

<style scoped>
.h-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-family: 'HarmonyOS Sans Symbols', sans-serif;
  font-style: normal;
  line-height: 1;
  vertical-align: middle;
}
</style>
```

- [ ] **Step 3: 创建 index.ts 导出**

```typescript
export { default as HIcon } from './HIcon.vue'
export { iconMap } from './icon-map'
```

- [ ] **Step 4: 提交**

```bash
git add src/frontend/src/components/ui/HIcon/
git commit -m "feat(ui): add HIcon component with HarmonyOS Sans Symbols support"
```

---

### Task 5: HInput 组件

**Files:**
- Create: `src/frontend/src/components/ui/HInput/HInput.vue`
- Create: `src/frontend/src/components/ui/HInput/index.ts`

- [ ] **Step 1: 创建 HInput.vue**

```vue
<!-- src/frontend/src/components/ui/HInput/HInput.vue -->
<script setup lang="ts">
import { ref, computed } from 'vue'

interface Props {
  modelValue?: string
  type?: string
  placeholder?: string
  disabled?: boolean
  clearable?: boolean
  showPassword?: boolean
  size?: 'small' | 'medium' | 'large'
  error?: string
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  type: 'text',
  placeholder: '',
  disabled: false,
  clearable: false,
  showPassword: false,
  size: 'medium',
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
  'focus': [event: FocusEvent]
  'blur': [event: FocusEvent]
  'clear': []
  'keyup': [event: KeyboardEvent]
}>()

const focused = ref(false)
const passwordVisible = ref(false)

const inputType = computed(() => {
  if (props.showPassword) return passwordVisible.value ? 'text' : 'password'
  return props.type
})

const hasValue = computed(() => props.modelValue.length > 0)

function onInput(event: Event) {
  const target = event.target as HTMLInputElement
  emit('update:modelValue', target.value)
}

function onClear() {
  emit('update:modelValue', '')
  emit('clear')
}

function togglePassword() {
  passwordVisible.value = !passwordVisible.value
}
</script>

<template>
  <div
    class="h-input"
    :class="[
      `h-input--${size}`,
      {
        'h-input--focused': focused,
        'h-input--disabled': disabled,
        'h-input--error': error,
      }
    ]"
  >
    <div v-if="$slots.prefix" class="h-input__prefix">
      <slot name="prefix" />
    </div>
    <input
      class="h-input__inner"
      :type="inputType"
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      @input="onInput"
      @focus="focused = true; $emit('focus', $event)"
      @blur="focused = false; $emit('blur', $event)"
      @keyup="$emit('keyup', $event)"
    />
    <div class="h-input__suffix">
      <span v-if="clearable && hasValue" class="h-input__clear" @click="onClear">✕</span>
      <span v-if="showPassword" class="h-input__toggle" @click="togglePassword">
        {{ passwordVisible ? '🙈' : '👁' }}
      </span>
      <slot name="suffix" />
    </div>
    <div v-if="error" class="h-input__error">{{ error }}</div>
  </div>
</template>

<style scoped>
.h-input {
  position: relative;
  display: flex;
  align-items: center;
  background: var(--color-bg-tertiary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  transition: all var(--duration-fast) var(--easing);
}
.h-input:hover:not(.h-input--disabled) {
  border-color: var(--color-border-hover);
}
.h-input--focused {
  border-color: var(--color-border-focus);
  box-shadow: 0 0 0 3px var(--color-primary-bg);
}
.h-input--error {
  border-color: var(--color-error);
}
.h-input--disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Sizes */
.h-input--small { height: 32px; padding: 0 10px; }
.h-input--medium { height: 38px; padding: 0 12px; }
.h-input--large { height: 44px; padding: 0 16px; }

.h-input__inner {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  color: var(--color-text-primary);
  font-size: var(--font-size-base);
  font-family: var(--font-family);
  min-width: 0;
}
.h-input__inner::placeholder {
  color: var(--color-text-tertiary);
}
.h-input__inner:disabled {
  cursor: not-allowed;
}

.h-input__prefix,
.h-input__suffix {
  display: flex;
  align-items: center;
  gap: 4px;
  color: var(--color-text-tertiary);
}
.h-input__clear,
.h-input__toggle {
  cursor: pointer;
  font-size: 12px;
  padding: 2px;
}
.h-input__clear:hover {
  color: var(--color-text-primary);
}

.h-input__error {
  position: absolute;
  bottom: -20px;
  left: 0;
  font-size: var(--font-size-xs);
  color: var(--color-error);
}
</style>
```

- [ ] **Step 2: 创建 index.ts**

```typescript
export { default as HInput } from './HInput.vue'
```

- [ ] **Step 3: 提交**

```bash
git add src/frontend/src/components/ui/HInput/
git commit -m "feat(ui): add HInput component with v-model, clearable, password toggle"
```

---

### Task 6: HMessage 组件（API 式调用）

**Files:**
- Create: `src/frontend/src/components/ui/HMessage/HMessage.vue`
- Create: `src/frontend/src/components/ui/HMessage/service.ts`
- Create: `src/frontend/src/components/ui/HMessage/index.ts`

- [ ] **Step 1: 创建 HMessage.vue（单条消息渲染）**

```vue
<!-- src/frontend/src/components/ui/HMessage/HMessage.vue -->
<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface Props {
  type: 'success' | 'error' | 'warning' | 'info'
  message: string
  duration?: number
  onClose?: () => void
}

const props = withDefaults(defineProps<Props>(), {
  duration: 3000,
})

const visible = ref(false)

onMounted(() => {
  requestAnimationFrame(() => { visible.value = true })
  if (props.duration > 0) {
    setTimeout(() => {
      visible.value = false
      setTimeout(() => props.onClose?.(), 200)
    }, props.duration)
  }
})

function close() {
  visible.value = false
  setTimeout(() => props.onClose?.(), 200)
}

const icons: Record<string, string> = {
  success: '✓',
  error: '✕',
  warning: '!',
  info: 'i',
}
</script>

<template>
  <div
    class="h-message"
    :class="[`h-message--${type}`, { 'h-message--visible': visible }]"
    @click="close"
  >
    <span class="h-message__icon">{{ icons[type] }}</span>
    <span class="h-message__text">{{ message }}</span>
  </div>
</template>

<style scoped>
.h-message {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%) translateY(-20px);
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: var(--radius-md);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-md);
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
  opacity: 0;
  transition: all var(--duration-normal) var(--easing);
  z-index: var(--z-toast);
  cursor: pointer;
}
.h-message--visible {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}
.h-message__icon {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  color: #fff;
  flex-shrink: 0;
}
.h-message--success .h-message__icon { background: var(--color-success); }
.h-message--error .h-message__icon { background: var(--color-error); }
.h-message--warning .h-message__icon { background: var(--color-warning); color: #000; }
.h-message--info .h-message__icon { background: var(--color-primary); }
</style>
```

- [ ] **Step 2: 创建 service.ts（纯函数 API）**

```typescript
// src/frontend/src/components/ui/HMessage/service.ts
import { createVNode, render } from 'vue'
import HMessage from './HMessage.vue'

type MessageType = 'success' | 'error' | 'warning' | 'info'

function showMessage(type: MessageType, message: string, duration = 3000) {
  const container = document.createElement('div')
  document.body.appendChild(container)

  const vnode = createVNode(HMessage, {
    type,
    message,
    duration,
    onClose: () => {
      render(null, container)
      container.remove()
    },
  })

  render(vnode, container)
}

export const HMessage = {
  success: (msg: string, duration?: number) => showMessage('success', msg, duration),
  error:   (msg: string, duration?: number) => showMessage('error', msg, duration),
  warning: (msg: string, duration?: number) => showMessage('warning', msg, duration),
  info:    (msg: string, duration?: number) => showMessage('info', msg, duration),
}
```

- [ ] **Step 3: 创建 index.ts**

```typescript
export { HMessage } from './service'
export { default as HMessageComponent } from './HMessage.vue'
```

- [ ] **Step 4: 提交**

```bash
git add src/frontend/src/components/ui/HMessage/
git commit -m "feat(ui): add HMessage API with success/error/warning/info methods"
```

---

### Task 7: UI 库全局注册插件

**Files:**
- Create: `src/frontend/src/components/ui/index.ts`
- Modify: `src/frontend/src/main.ts`

- [ ] **Step 1: 创建统一导出文件**

```typescript
// src/frontend/src/components/ui/index.ts
import type { App } from 'vue'

// 组件导出
export { HButton } from './HButton'
export { HIcon } from './HIcon'
export { HInput } from './HInput'
export { HMessage } from './HMessage'

// Vue 插件：全局注册
export default {
  install(app: App) {
    // 目前 HMessage 是 API 式调用，无需全局注册组件
    // 后续组件添加后在此注册
  }
}
```

- [ ] **Step 2: 修改 main.ts 注册 UI 插件**

将 `main.ts` 修改为：

```typescript
import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router';
import { createPinia } from 'pinia'
import persistState from 'pinia-plugin-persistedstate';
import UI from './components/ui'

const app = createApp(App)
const pinia = createPinia();
pinia.use(persistState);

app.use(router);
app.use(pinia);
app.use(UI);
app.mount('#app')
```

关键变更：移除了 `import 'element-plus/dist/index.css'`，添加了 `import UI from './components/ui'` 和 `app.use(UI)`。

- [ ] **Step 3: 验证构建**

```bash
cd src/frontend && npm run build
```

此时构建应该会**失败**（因为其他 .vue 文件仍引用 Element Plus），但 `main.ts` 和新组件本身应该没有语法错误。确认错误来源是 Element Plus 引用而非新代码。

- [ ] **Step 4: 提交**

```bash
git add src/frontend/src/components/ui/index.ts src/frontend/src/main.ts
git commit -m "feat(ui): register UI library plugin, remove Element Plus CSS import"
```

---

## Phase 3: 页面迁移 — 第一、二批（低复杂度）

### Task 8: 迁移 index.vue（主布局）

**Files:**
- Modify: `src/frontend/src/pages/index.vue`

- [ ] **Step 1: 替换 script 中的 Element Plus 引用**

将第 5 行的 `import { ElMessage, ElMessageBox } from 'element-plus'` 替换为：
```typescript
import { HMessage } from '@/components/ui'
```

将第 17 行的 `import { User, SwitchButton, Setting } from '@element-plus/icons-vue'` 删除。

将第 170 行的 `ElMessage.success('已退出登录')` 替换为：
```typescript
HMessage.success('已退出登录')
```

- [ ] **Step 2: 替换 template 中的 el-dropdown**

将 `<el-dropdown @command="handleUserCommand" trigger="click">` 及其内部的 `<el-dropdown-menu>` 和 `<el-dropdown-item>` 替换为原生 HTML 实现。由于 HDropdown 组件尚未创建，使用临时原生实现：

```vue
<div class="user-info">
  <div class="user-dropdown" @click="toggleUserMenu">
    <div class="user-avatar-wrapper">
      <div class="user-avatar">
        <img
          :src="userStore.userInfo?.avatar || '/src/assets/user.svg'"
          alt="用户头像"
          @error="handleAvatarError"
          referrerpolicy="no-referrer"
        />
      </div>
    </div>
    <div v-if="showUserMenu" class="user-dropdown-menu">
      <div class="user-dropdown-item" @click="handleUserCommand('profile')">
        <span>个人资料</span>
      </div>
      <div class="user-dropdown-item user-dropdown-item--danger" @click="handleUserCommand('logout')">
        <span>退出登录</span>
      </div>
    </div>
  </div>
</div>
```

在 script 中添加：
```typescript
const showUserMenu = ref(false)
const toggleUserMenu = () => { showUserMenu.value = !showUserMenu.value }

// 点击外部关闭
const closeUserMenu = () => { showUserMenu.value = false }
onMounted(() => {
  document.addEventListener('click', (e) => {
    const target = e.target as HTMLElement
    if (!target.closest('.user-dropdown')) {
      showUserMenu.value = false
    }
  })
})
```

- [ ] **Step 3: 替换 style 中的 Element Plus 覆写**

移除 `:deep(.el-dropdown-menu)` 及其所有子样式（第 414-433 行），替换为：

```scss
.user-dropdown {
  position: relative;
  cursor: pointer;

  .user-dropdown-menu {
    position: absolute;
    top: 100%;
    right: 0;
    margin-top: 8px;
    min-width: 140px;
    background: var(--color-bg-secondary);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-md);
    z-index: var(--z-dropdown);
    overflow: hidden;
    animation: fadeSlideIn var(--duration-fast) var(--easing);
  }

  .user-dropdown-item {
    padding: 10px 16px;
    font-size: var(--font-size-base);
    color: var(--color-text-primary);
    cursor: pointer;
    transition: background var(--duration-fast) var(--easing);

    &:hover {
      background: var(--color-bg-tertiary);
    }

    &--danger {
      color: var(--color-danger);
    }
  }
}

@keyframes fadeSlideIn {
  from { opacity: 0; transform: translateY(-4px); }
  to { opacity: 1; transform: translateY(0); }
}
```

- [ ] **Step 4: 验证**

运行 dev server，确认：
- 顶栏显示正常，头像点击弹出下拉菜单
- 点击"个人资料"跳转正确
- 点击"退出登录"显示 HMessage 成功提示并跳转到登录页
- 点击菜单外部自动关闭下拉

- [ ] **Step 5: 提交**

```bash
git add src/frontend/src/pages/index.vue
git commit -m "feat(migrate): convert index.vue from Element Plus to native/HMessage"
```

---

### Task 9: 迁移 workspace.vue

**Files:**
- Modify: `src/frontend/src/pages/workspace/workspace.vue`

- [ ] **Step 1: 读取文件，识别所有 Element Plus 使用**

搜索 `el-` 标签和 `element-plus` import。

- [ ] **Step 2: 替换所有 el- 标签为原生 HTML 或 H 组件**

- `el-button` → `<HButton>` 或原生 `<button>`
- `el-input` → `<HInput>`
- `el-icon` → 移除，使用 SVG 或文本

- [ ] **Step 3: 替换 import 和 API 调用**

- `import { ElMessage } from 'element-plus'` → `import { HMessage } from '@/components/ui'`
- `ElMessage.success(...)` → `HMessage.success(...)`

- [ ] **Step 4: 验证页面功能正常**

- [ ] **Step 5: 提交**

```bash
git add src/frontend/src/pages/workspace/workspace.vue
git commit -m "feat(migrate): convert workspace.vue from Element Plus"
```

---

### Task 10: 迁移 login.vue 和 register.vue

**Files:**
- Modify: `src/frontend/src/pages/login/login.vue`
- Modify: `src/frontend/src/pages/login/register.vue`

- [ ] **Step 1: 迁移 login.vue**

替换文件中的：
- `import { ElMessage } from 'element-plus'` → `import { HMessage } from '@/components/ui'`
- `<el-input ...>` → `<HInput ...>`，注意 prop 映射：
  - `v-model` 保持不变
  - `size="large"` → `size="large"`
  - `show-password` → `:show-password="true"`
  - `@keyup.enter` → `@keyup.enter`
- `<el-button type="primary" size="large" :loading="loading">` → `<HButton type="primary" size="large" :loading="loading">`
- 所有 `ElMessage.xxx()` → `HMessage.xxx()`

同时将样式中的硬编码色值替换为 CSS 变量：
- `#4f81ff` → `var(--color-primary)`
- `#3b66db` → `var(--color-primary-active)`
- `background: white` → `background: var(--color-bg-secondary)`
- `color: #2c3e50` → `color: var(--color-text-primary)`
- `color: #555` / `color: #666` → `var(--color-text-secondary)`
- `#f8f9fc` → `var(--color-bg-tertiary)`
- `#e1e5e9` → `var(--color-border)`

- [ ] **Step 2: 迁移 register.vue**

同 login.vue 的替换策略。

- [ ] **Step 3: 验证登录/注册流程完整可用**

- [ ] **Step 4: 提交**

```bash
git add src/frontend/src/pages/login/
git commit -m "feat(migrate): convert login.vue and register.vue from Element Plus"
```

---

### Task 11: 迁移低复杂度页面（agent.vue、configuration.vue、test.vue）

**Files:**
- Modify: `src/frontend/src/pages/agent/agent.vue`
- Modify: `src/frontend/src/pages/configuration/configuration.vue`
- Modify: `src/frontend/src/pages/conversation/test.vue`

- [ ] **Step 1: 批量替换策略**

对这三个文件，执行以下统一替换：

1. `import { ElMessage } from 'element-plus'` → `import { HMessage } from '@/components/ui'`
2. `import { ElMessageBox } from 'element-plus'` → 后续 HMessageBox 完成后替换；临时使用 `utils/dialog.ts` 中的 `showDeleteConfirm`
3. `<el-button ...>` → `<HButton ...>`
4. `<el-input ...>` → `<HInput ...>`
5. `<el-tag ...>` → 原生 `<span class="h-tag">` 临时实现
6. `ElMessage.success/error/warning(...)` → `HMessage.success/error/warning(...)`

- [ ] **Step 2: 逐文件验证**

- [ ] **Step 3: 提交**

```bash
git add src/frontend/src/pages/agent/agent.vue src/frontend/src/pages/configuration/configuration.vue src/frontend/src/pages/conversation/test.vue
git commit -m "feat(migrate): convert agent.vue, configuration.vue, test.vue from Element Plus"
```

---

## Phase 4: P1 表单与交互组件

### Task 12: HMessageBox（confirm/alert API）

**Files:**
- Create: `src/frontend/src/components/ui/HMessageBox/HMessageBox.vue`
- Create: `src/frontend/src/components/ui/HMessageBox/service.ts`
- Create: `src/frontend/src/components/ui/HMessageBox/index.ts`
- Modify: `src/frontend/src/utils/dialog.ts`

- [ ] **Step 1: 创建 HMessageBox.vue**

```vue
<!-- src/frontend/src/components/ui/HMessageBox/HMessageBox.vue -->
<script setup lang="ts">
import { ref } from 'vue'

interface Props {
  title?: string
  message: string
  confirmButtonText?: string
  cancelButtonText?: string
  type?: 'warning' | 'info' | 'success' | 'error'
  showCancel?: boolean
  onConfirm?: () => void
  onCancel?: () => void
  onClose?: () => void
}

const props = withDefaults(defineProps<Props>(), {
  title: '确认',
  confirmButtonText: '确定',
  cancelButtonText: '取消',
  type: 'warning',
  showCancel: true,
})

const visible = ref(false)

import { onMounted } from 'vue'

onMounted(() => {
  requestAnimationFrame(() => { visible.value = true })
})

function handleConfirm() {
  visible.value = false
  setTimeout(() => {
    props.onConfirm?.()
    props.onClose?.()
  }, 200)
}

function handleCancel() {
  visible.value = false
  setTimeout(() => {
    props.onCancel?.()
    props.onClose?.()
  }, 200)
}
</script>

<template>
  <div class="h-messagebox-overlay" :class="{ 'h-messagebox--visible': visible }" @click.self="handleCancel">
    <div class="h-messagebox" :class="{ 'h-messagebox--visible': visible }">
      <div class="h-messagebox__header">
        <span class="h-messagebox__title">{{ title }}</span>
        <span class="h-messagebox__close" @click="handleCancel">✕</span>
      </div>
      <div class="h-messagebox__body">
        <p>{{ message }}</p>
      </div>
      <div class="h-messagebox__footer">
        <button v-if="showCancel" class="h-messagebox__btn h-messagebox__btn--cancel" @click="handleCancel">
          {{ cancelButtonText }}
        </button>
        <button class="h-messagebox__btn h-messagebox__btn--confirm" @click="handleConfirm">
          {{ confirmButtonText }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.h-messagebox-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-dialog);
  opacity: 0;
  transition: opacity var(--duration-normal) var(--easing);
}
.h-messagebox--visible {
  opacity: 1;
}
.h-messagebox {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  min-width: 360px;
  max-width: 420px;
  transform: scale(0.95);
  transition: transform var(--duration-normal) var(--easing);
}
.h-messagebox--visible .h-messagebox {
  transform: scale(1);
}
.h-messagebox__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px 12px;
}
.h-messagebox__title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-text-primary);
}
.h-messagebox__close {
  cursor: pointer;
  color: var(--color-text-tertiary);
  font-size: 14px;
}
.h-messagebox__close:hover { color: var(--color-text-primary); }
.h-messagebox__body {
  padding: 12px 24px;
  text-align: center;
  color: var(--color-text-secondary);
  font-size: var(--font-size-base);
  line-height: 1.6;
}
.h-messagebox__footer {
  display: flex;
  justify-content: center;
  gap: 12px;
  padding: 16px 24px 20px;
}
.h-messagebox__btn {
  min-width: 88px;
  height: 36px;
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--font-size-base);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--duration-fast) var(--easing);
  font-family: var(--font-family);
}
.h-messagebox__btn--cancel {
  background: var(--color-bg-tertiary);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
}
.h-messagebox__btn--cancel:hover {
  border-color: var(--color-border-hover);
  color: var(--color-text-primary);
}
.h-messagebox__btn--confirm {
  background: var(--color-primary);
  color: #fff;
}
.h-messagebox__btn--confirm:hover {
  background: var(--color-primary-hover);
}
</style>
```

- [ ] **Step 2: 创建 service.ts**

```typescript
// src/frontend/src/components/ui/HMessageBox/service.ts
import { createVNode, render } from 'vue'
import HMessageBox from './HMessageBox.vue'

interface MessageBoxOptions {
  title?: string
  message: string
  confirmButtonText?: string
  cancelButtonText?: string
  type?: 'warning' | 'info' | 'success' | 'error'
  showCancel?: boolean
}

function createMessageBox(options: MessageBoxOptions): Promise<void> {
  return new Promise((resolve, reject) => {
    const container = document.createElement('div')
    document.body.appendChild(container)

    const vnode = createVNode(HMessageBox, {
      ...options,
      onConfirm: () => {
        cleanup()
        resolve()
      },
      onCancel: () => {
        cleanup()
        reject(new Error('cancel'))
      },
      onClose: cleanup,
    })

    function cleanup() {
      render(null, container)
      container.remove()
    }

    render(vnode, container)
  })
}

export const HMessageBox = {
  confirm: (message: string, title?: string, options?: Partial<MessageBoxOptions>) =>
    createMessageBox({ message, title, showCancel: true, ...options }),

  alert: (message: string, title?: string, options?: Partial<MessageBoxOptions>) =>
    createMessageBox({ message, title, showCancel: false, ...options }),
}
```

- [ ] **Step 3: 更新 utils/dialog.ts**

```typescript
// src/frontend/src/utils/dialog.ts
import { HMessageBox } from '@/components/ui'

export const showDeleteConfirm = (message: string, title: string = '删除确认') => {
  return HMessageBox.confirm(message, title, {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    type: 'warning',
  })
}

export const showConfirm = (
  message: string,
  title: string = '确认',
  options: any = {}
) => {
  return HMessageBox.confirm(message, title, {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
    ...options,
  })
}
```

- [ ] **Step 4: 更新 ui/index.ts 导出**

在 `src/frontend/src/components/ui/index.ts` 中添加：
```typescript
export { HMessageBox } from './HMessageBox'
```

- [ ] **Step 5: 验证**

在已迁移的页面中触发删除操作，确认 HMessageBox 弹窗正常显示、确认/取消功能正确。

- [ ] **Step 6: 提交**

```bash
git add src/frontend/src/components/ui/HMessageBox/ src/frontend/src/utils/dialog.ts src/frontend/src/components/ui/index.ts
git commit -m "feat(ui): add HMessageBox with confirm/alert API, update dialog utils"
```

---

### Task 13: HSelect + HOption 组件

**Files:**
- Create: `src/frontend/src/components/ui/HSelect/HSelect.vue`
- Create: `src/frontend/src/components/ui/HSelect/HOption.vue`
- Create: `src/frontend/src/components/ui/HSelect/index.ts`

- [ ] **Step 1: 创建 HSelect.vue**

```vue
<!-- src/frontend/src/components/ui/HSelect/HSelect.vue -->
<script setup lang="ts">
import { ref, provide, computed } from 'vue'

interface Props {
  modelValue: string | number | undefined
  placeholder?: string
  disabled?: boolean
  clearable?: boolean
  filterable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: '请选择',
  disabled: false,
  clearable: false,
  filterable: false,
})

const emit = defineEmits<{
  'update:modelValue': [value: string | number | undefined]
  'change': [value: string | number | undefined]
}>()

const open = ref(false)
const search = ref('')
const dropdownRef = ref<HTMLElement | null>(null)

// 通过 provide/inject 与 HOption 通信
provide('h-select', {
  modelValue: computed(() => props.modelValue),
  select: (value: string | number) => {
    emit('update:modelValue', value)
    emit('change', value)
    open.value = false
    search.value = ''
  },
})

function clear() {
  emit('update:modelValue', undefined)
  emit('change', undefined)
}

function toggle() {
  if (!props.disabled) open.value = !open.value
}

// 点击外部关闭
function onClickOutside(e: MouseEvent) {
  const target = e.target as HTMLElement
  if (!target.closest('.h-select')) {
    open.value = false
  }
}

import { onMounted, onUnmounted } from 'vue'
onMounted(() => document.addEventListener('click', onClickOutside))
onUnmounted(() => document.removeEventListener('click', onClickOutside))
</script>

<template>
  <div class="h-select" :class="{ 'h-select--open': open, 'h-select--disabled': disabled }">
    <div class="h-select__trigger" @click="toggle">
      <slot name="trigger">
        <div class="h-select__value">
          <slot name="selected" :value="modelValue">
            <span v-if="modelValue !== undefined && modelValue !== ''">{{ modelValue }}</span>
            <span v-else class="h-select__placeholder">{{ placeholder }}</span>
          </slot>
        </div>
      </slot>
      <span class="h-select__arrow">▾</span>
      <span v-if="clearable && modelValue" class="h-select__clear" @click.stop="clear">✕</span>
    </div>
    <div v-show="open" class="h-select__dropdown" ref="dropdownRef">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.h-select {
  position: relative;
  display: inline-block;
  min-width: 180px;
}
.h-select__trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  height: 38px;
  padding: 0 12px;
  background: var(--color-bg-tertiary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--duration-fast) var(--easing);
}
.h-select--open .h-select__trigger {
  border-color: var(--color-border-focus);
}
.h-select--disabled .h-select__trigger {
  opacity: 0.5;
  cursor: not-allowed;
}
.h-select__value {
  flex: 1;
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.h-select__placeholder {
  color: var(--color-text-tertiary);
}
.h-select__arrow,
.h-select__clear {
  color: var(--color-text-tertiary);
  font-size: 12px;
}
.h-select__clear:hover { color: var(--color-text-primary); }
.h-select__dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  z-index: var(--z-dropdown);
  max-height: 240px;
  overflow-y: auto;
  padding: 4px;
}
</style>
```

- [ ] **Step 2: 创建 HOption.vue**

```vue
<!-- src/frontend/src/components/ui/HSelect/HOption.vue -->
<script setup lang="ts">
import { inject, computed } from 'vue'

interface Props {
  value: string | number
  label?: string
}

const props = defineProps<Props>()

const select = inject<any>('h-select')
const isSelected = computed(() => select?.modelValue.value === props.value)
</script>

<template>
  <div
    class="h-option"
    :class="{ 'h-option--selected': isSelected }"
    @click="select?.select(props.value)"
  >
    <slot>{{ label || value }}</slot>
  </div>
</template>

<style scoped>
.h-option {
  padding: 8px 12px;
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background var(--duration-fast) var(--easing);
}
.h-option:hover {
  background: var(--color-primary-bg);
}
.h-option--selected {
  background: var(--color-primary-bg);
  color: var(--color-primary);
  font-weight: 500;
}
</style>
```

- [ ] **Step 3: 创建 index.ts 并更新 ui/index.ts**

```typescript
export { default as HSelect } from './HSelect.vue'
export { default as HOption } from './HOption.vue'
```

- [ ] **Step 4: 提交**

```bash
git add src/frontend/src/components/ui/HSelect/
git commit -m "feat(ui): add HSelect + HOption with dropdown, selection, clearable"
```

---

### Task 14: HDialog 组件

**Files:**
- Create: `src/frontend/src/components/ui/HDialog/HDialog.vue`
- Create: `src/frontend/src/components/ui/HDialog/index.ts`

- [ ] **Step 1: 创建 HDialog.vue**

```vue
<!-- src/frontend/src/components/ui/HDialog/HDialog.vue -->
<script setup lang="ts">
interface Props {
  modelValue: boolean
  title?: string
  width?: string
  closeOnClickModal?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  width: '500px',
  closeOnClickModal: true,
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'close': []
}>()

function close() {
  emit('update:modelValue', false)
  emit('close')
}
</script>

<template>
  <Teleport to="body">
    <Transition name="h-dialog">
      <div v-if="modelValue" class="h-dialog-overlay" @click.self="closeOnClickModal && close()">
        <div class="h-dialog" :style="{ maxWidth: width }">
          <div class="h-dialog__header">
            <span class="h-dialog__title">{{ title }}</span>
            <span class="h-dialog__close" @click="close">✕</span>
          </div>
          <div class="h-dialog__body">
            <slot />
          </div>
          <div v-if="$slots.footer" class="h-dialog__footer">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.h-dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-dialog);
}
.h-dialog {
  width: 100%;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  overflow: hidden;
}
.h-dialog__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px 12px;
}
.h-dialog__title {
  font-size: var(--font-size-xl);
  font-weight: 600;
  color: var(--color-text-primary);
}
.h-dialog__close {
  cursor: pointer;
  color: var(--color-text-tertiary);
  font-size: 16px;
  padding: 4px;
}
.h-dialog__close:hover { color: var(--color-text-primary); }
.h-dialog__body {
  padding: 16px 24px;
  color: var(--color-text-secondary);
}
.h-dialog__footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px 20px;
}

/* 过渡动画 */
.h-dialog-enter-active,
.h-dialog-leave-active {
  transition: opacity var(--duration-normal) var(--easing);
}
.h-dialog-enter-from,
.h-dialog-leave-to {
  opacity: 0;
}
</style>
```

- [ ] **Step 2: 创建 index.ts 并更新 ui/index.ts**

- [ ] **Step 3: 提交**

```bash
git add src/frontend/src/components/ui/HDialog/
git commit -m "feat(ui): add HDialog with Teleport, transitions, click-outside close"
```

---

### Task 15: HTooltip + HDropdown + HTag 组件

**Files:**
- Create: `src/frontend/src/components/ui/HTooltip/HTooltip.vue` + `index.ts`
- Create: `src/frontend/src/components/ui/HDropdown/HDropdown.vue` + `HDropdownMenu.vue` + `HDropdownItem.vue` + `index.ts`
- Create: `src/frontend/src/components/ui/HTag/HTag.vue` + `index.ts`

- [ ] **Step 1: 创建 HTooltip.vue**

```vue
<!-- src/frontend/src/components/ui/HTooltip/HTooltip.vue -->
<script setup lang="ts">
import { ref } from 'vue'

interface Props {
  content: string
  placement?: 'top' | 'bottom' | 'left' | 'right'
  delay?: number
}

withDefaults(defineProps<Props>(), {
  placement: 'top',
  delay: 200,
})

const visible = ref(false)
let timer: ReturnType<typeof setTimeout> | null = null

function show() {
  timer = setTimeout(() => { visible.value = true }, 200)
}
function hide() {
  if (timer) clearTimeout(timer)
  visible.value = false
}
</script>

<template>
  <div class="h-tooltip-wrapper" @mouseenter="show" @mouseleave="hide">
    <slot />
    <div v-if="visible" :class="['h-tooltip', `h-tooltip--${placement}`]">
      <div class="h-tooltip__content">{{ content }}</div>
    </div>
  </div>
</template>

<style scoped>
.h-tooltip-wrapper {
  position: relative;
  display: inline-flex;
}
.h-tooltip {
  position: absolute;
  padding: 6px 10px;
  background: var(--color-bg-tertiary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-xs);
  color: var(--color-text-primary);
  white-space: nowrap;
  z-index: var(--z-dropdown);
  box-shadow: var(--shadow-sm);
  pointer-events: none;
}
.h-tooltip--top { bottom: calc(100% + 6px); left: 50%; transform: translateX(-50%); }
.h-tooltip--bottom { top: calc(100% + 6px); left: 50%; transform: translateX(-50%); }
.h-tooltip--left { right: calc(100% + 6px); top: 50%; transform: translateY(-50%); }
.h-tooltip--right { left: calc(100% + 6px); top: 50%; transform: translateY(-50%); }
</style>
```

- [ ] **Step 2: 创建 HDropdown 系列组件**

```vue
<!-- HDropdown.vue -->
<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

interface Props {
  trigger?: 'click' | 'hover'
}
withDefaults(defineProps<Props>(), { trigger: 'click' })

const visible = ref(false)
const toggle = () => { visible.value = !visible.value }
const close = () => { visible.value = false }

const wrapperRef = ref<HTMLElement | null>(null)
function onClickOutside(e: MouseEvent) {
  if (wrapperRef.value && !wrapperRef.value.contains(e.target as Node)) close()
}
onMounted(() => document.addEventListener('click', onClickOutside))
onUnmounted(() => document.removeEventListener('click', onClickOutside))
</script>

<template>
  <div class="h-dropdown" ref="wrapperRef" @click="trigger === 'click' && toggle()">
    <slot />
    <div v-if="visible" class="h-dropdown__menu" @click="close">
      <slot name="dropdown" />
    </div>
  </div>
</template>

<style scoped>
.h-dropdown { position: relative; display: inline-flex; }
.h-dropdown__menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 4px;
  min-width: 140px;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  z-index: var(--z-dropdown);
  overflow: hidden;
}
</style>
```

```vue
<!-- HDropdownItem.vue -->
<script setup lang="ts">
interface Props { command?: string }
defineProps<Props>()
defineEmits<{ click: [command: string | undefined] }>()
</script>

<template>
  <div class="h-dropdown-item" @click="$emit('click', command)">
    <slot />
  </div>
</template>

<style scoped>
.h-dropdown-item {
  padding: 10px 16px;
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
  cursor: pointer;
  transition: background var(--duration-fast) var(--easing);
}
.h-dropdown-item:hover { background: var(--color-bg-tertiary); }
</style>
```

- [ ] **Step 3: 创建 HTag.vue**

```vue
<!-- src/frontend/src/components/ui/HTag/HTag.vue -->
<script setup lang="ts">
interface Props {
  type?: 'default' | 'primary' | 'success' | 'warning' | 'danger'
  closable?: boolean
}
withDefaults(defineProps<Props>(), { type: 'default', closable: false })
defineEmits<{ close: [] }>()
</script>

<template>
  <span class="h-tag" :class="`h-tag--${type}`">
    <slot />
    <span v-if="closable" class="h-tag__close" @click="$emit('close')">✕</span>
  </span>
</template>

<style scoped>
.h-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 10px;
  border-radius: var(--radius-full);
  font-size: var(--font-size-xs);
  font-weight: 500;
  line-height: 20px;
}
.h-tag--default {
  background: var(--color-bg-tertiary);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
}
.h-tag--primary {
  background: var(--color-primary-bg);
  color: var(--color-primary);
}
.h-tag--success {
  background: var(--color-success-bg);
  color: var(--color-success);
}
.h-tag--warning {
  background: var(--color-warning-bg);
  color: var(--color-warning);
}
.h-tag--danger {
  background: var(--color-danger-bg);
  color: var(--color-danger);
}
.h-tag__close {
  cursor: pointer;
  font-size: 10px;
  opacity: 0.7;
}
.h-tag__close:hover { opacity: 1; }
</style>
```

- [ ] **Step 4: 创建各自的 index.ts，更新 ui/index.ts 导出**

- [ ] **Step 5: 提交**

```bash
git add src/frontend/src/components/ui/HTooltip/ src/frontend/src/components/ui/HDropdown/ src/frontend/src/components/ui/HTag/
git commit -m "feat(ui): add HTooltip, HDropdown, HTag components"
```

---

### Task 16: HForm + HFormItem 组件

**Files:**
- Create: `src/frontend/src/components/ui/HForm/HForm.vue` + `HFormItem.vue` + `index.ts`

- [ ] **Step 1: 创建 HForm.vue**

```vue
<script setup lang="ts">
import { provide } from 'vue'

interface Props {
  model?: Record<string, any>
  rules?: Record<string, any>
}

const props = defineProps<Props>()

provide('h-form', {
  model: props.model,
  rules: props.rules,
})
</script>

<template>
  <form class="h-form" @submit.prevent>
    <slot />
  </form>
</template>

<style scoped>
.h-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}
</style>
```

- [ ] **Step 2: 创建 HFormItem.vue**

```vue
<script setup lang="ts">
interface Props {
  label?: string
  prop?: string
  error?: string
}
defineProps<Props>()
</script>

<template>
  <div class="h-form-item">
    <label v-if="label" class="h-form-item__label">{{ label }}</label>
    <div class="h-form-item__content">
      <slot />
      <div v-if="error" class="h-form-item__error">{{ error }}</div>
    </div>
  </div>
</template>

<style scoped>
.h-form-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.h-form-item__label {
  font-size: var(--font-size-base);
  font-weight: 500;
  color: var(--color-text-primary);
}
.h-form-item__error {
  font-size: var(--font-size-xs);
  color: var(--color-error);
  margin-top: 4px;
}
</style>
```

- [ ] **Step 3: 创建 index.ts，更新 ui/index.ts**

- [ ] **Step 4: 提交**

```bash
git add src/frontend/src/components/ui/HForm/
git commit -m "feat(ui): add HForm + HFormItem with label/error layout"
```

---

## Phase 5: 页面迁移 — 第三批（中等复杂度）

### Task 17: 迁移第三批页面（9 个文件）

**Files:**
- Modify: `src/frontend/src/pages/knowledge/knowledge-file.vue`
- Modify: `src/frontend/src/pages/agent/AgentDebug.vue`
- Modify: `src/frontend/src/pages/dashboard/dashboard.vue`
- Modify: `src/frontend/src/pages/knowledge/knowledge.vue`
- Modify: `src/frontend/src/pages/profile/profile.vue`
- Modify: `src/frontend/src/pages/agent/agent-fixed.vue`
- Modify: `src/frontend/src/pages/conversation/demo.vue`
- Modify: `src/frontend/src/pages/model/model.vue`
- Modify: `src/frontend/src/pages/conversation/chatPage/chatPage.vue`

- [ ] **Step 1: 统一替换策略**

对每个文件执行以下操作：

1. **Import 替换：**
   - `import { ElMessage, ElMessageBox, ... } from 'element-plus'` → `import { HMessage, HMessageBox } from '@/components/ui'`
   - `import { XxxIcon } from '@element-plus/icons-vue'` → 删除，改用 `<HIcon name="xxx" />`

2. **模板标签替换：**
   - `<el-button>` → `<HButton>`
   - `<el-input>` → `<HInput>`
   - `<el-select>` + `<el-option>` → `<HSelect>` + `<HOption>`
   - `<el-form>` + `<el-form-item>` → `<HForm>` + `<HFormItem>`
   - `<el-dialog>` → `<HDialog>`
   - `<el-tooltip>` → `<HTooltip>`
   - `<el-tag>` → `<HTag>`
   - `<el-icon><Xxx /></el-icon>` → `<HIcon name="xxx" />`

3. **API 调用替换：**
   - `ElMessage.success(...)` → `HMessage.success(...)`
   - `ElMessage.error(...)` → `HMessage.error(...)`
   - `ElMessageBox.confirm(...)` → `HMessageBox.confirm(...)`

4. **v-loading 替换：**
   - `v-loading="xxx"` → 移除，后续通过 HLoading 指令替换；临时用 CSS class `.is-loading` + 条件遮罩

5. **样式替换：**
   - 移除 `:deep(.el-xxx)` 样式
   - 硬编码色值替换为 CSS 变量

- [ ] **Step 2: 逐文件验证**

对每个文件运行 dev server 检查页面是否正常渲染，交互是否正常。

- [ ] **Step 3: 提交（每 2-3 个文件一次提交）**

```bash
git add src/frontend/src/pages/knowledge/ src/frontend/src/pages/agent/AgentDebug.vue
git commit -m "feat(migrate): convert knowledge and AgentDebug pages from Element Plus"

git add src/frontend/src/pages/dashboard/ src/frontend/src/pages/profile/ src/frontend/src/pages/agent/agent-fixed.vue
git commit -m "feat(migrate): convert dashboard, profile, agent-fixed from Element Plus"

git add src/frontend/src/pages/conversation/demo.vue src/frontend/src/pages/model/ src/frontend/src/pages/conversation/chatPage/
git commit -m "feat(migrate): convert demo, model, chatPage from Element Plus"
```

---

## Phase 6: P2 专用组件

### Task 18: HTable + HUpload + HDrawer + HTabs 组件

**Files:**
- Create: `src/frontend/src/components/ui/HTable/` (HTable.vue, HTableColumn.vue, index.ts)
- Create: `src/frontend/src/components/ui/HUpload/` (HUpload.vue, index.ts)
- Create: `src/frontend/src/components/ui/HDrawer/` (HDrawer.vue, index.ts)
- Create: `src/frontend/src/components/ui/HTabs/` (HTabs.vue, HTabPane.vue, index.ts)

- [ ] **Step 1: 创建 HTable（简化实现，仅服务 mcp-server.vue）**

```vue
<!-- HTable.vue -->
<script setup lang="ts">
interface Props {
  data: any[]
  stripe?: boolean
}
withDefaults(defineProps<Props>(), { stripe: false })
</script>

<template>
  <div class="h-table-wrapper">
    <table class="h-table" :class="{ 'h-table--stripe': stripe }">
      <thead>
        <tr><slot name="header" /></tr>
      </thead>
      <tbody>
        <tr v-for="(row, index) in data" :key="index">
          <slot :row="row" :index="index" />
        </tr>
        <tr v-if="data.length === 0">
          <td class="h-table__empty" :colspan="100">暂无数据</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.h-table-wrapper {
  overflow-x: auto;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
}
.h-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--font-size-base);
}
.h-table th, .h-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
  color: var(--color-text-primary);
}
.h-table th {
  background: var(--color-bg-tertiary);
  font-weight: 600;
  color: var(--color-text-secondary);
}
.h-table--stripe tbody tr:nth-child(even) {
  background: var(--color-bg-tertiary);
}
.h-table__empty {
  text-align: center;
  padding: 32px 16px;
  color: var(--color-text-tertiary);
}
</style>
```

- [ ] **Step 2: 创建 HUpload.vue**

```vue
<script setup lang="ts">
import { ref } from 'vue'

interface HUploadFile {
  name: string
  url?: string
  size?: number
  status?: 'ready' | 'uploading' | 'success' | 'error'
}

interface Props {
  action?: string
  accept?: string
  multiple?: boolean
  drag?: boolean
  fileList?: HUploadFile[]
}

const props = withDefaults(defineProps<Props>(), {
  multiple: false,
  drag: false,
  fileList: () => [],
})

const emit = defineEmits<{
  'update:fileList': [files: HUploadFile[]]
  'change': [files: HUploadFile[]]
}>()

const inputRef = ref<HTMLInputElement | null>(null)

function triggerSelect() {
  inputRef.value?.click()
}

function onChange(event: Event) {
  const input = event.target as HTMLInputElement
  if (!input.files) return
  const newFiles: HUploadFile[] = Array.from(input.files).map(f => ({
    name: f.name,
    size: f.size,
    status: 'ready' as const,
  }))
  const merged = [...props.fileList, ...newFiles]
  emit('update:fileList', merged)
  emit('change', merged)
  input.value = ''
}

function remove(index: number) {
  const files = [...props.fileList]
  files.splice(index, 1)
  emit('update:fileList', files)
  emit('change', files)
}

function onDrop(event: DragEvent) {
  event.preventDefault()
  if (!event.dataTransfer?.files) return
  const newFiles: HUploadFile[] = Array.from(event.dataTransfer.files).map(f => ({
    name: f.name,
    size: f.size,
    status: 'ready' as const,
  }))
  const merged = [...props.fileList, ...newFiles]
  emit('update:fileList', merged)
  emit('change', merged)
}
</script>

<template>
  <div class="h-upload" :class="{ 'h-upload--drag': drag }">
    <div
      v-if="drag"
      class="h-upload__dropzone"
      @dragover.prevent
      @drop="onDrop"
      @click="triggerSelect"
    >
      <slot name="tip">
        <span class="h-upload__tip">将文件拖拽到此处，或 <em>点击上传</em></span>
      </slot>
    </div>
    <div v-else class="h-upload__trigger" @click="triggerSelect">
      <slot />
    </div>
    <input
      ref="inputRef"
      type="file"
      :accept="accept"
      :multiple="multiple"
      hidden
      @change="onChange"
    />
    <div v-if="fileList.length" class="h-upload__list">
      <div v-for="(file, i) in fileList" :key="i" class="h-upload__file">
        <span class="h-upload__filename">{{ file.name }}</span>
        <span class="h-upload__remove" @click="remove(i)">✕</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.h-upload__dropzone {
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-md);
  padding: 32px;
  text-align: center;
  cursor: pointer;
  transition: border-color var(--duration-fast) var(--easing);
  color: var(--color-text-tertiary);
}
.h-upload__dropzone:hover {
  border-color: var(--color-primary);
}
.h-upload__tip em {
  color: var(--color-primary);
  font-style: normal;
  cursor: pointer;
}
.h-upload__list {
  margin-top: 8px;
}
.h-upload__file {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 10px;
  background: var(--color-bg-tertiary);
  border-radius: var(--radius-sm);
  margin-top: 4px;
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
}
.h-upload__remove {
  cursor: pointer;
  color: var(--color-text-tertiary);
}
.h-upload__remove:hover {
  color: var(--color-danger);
}
</style>
```

- [ ] **Step 3: 创建 HDrawer.vue**

```vue
<script setup lang="ts">
interface Props {
  modelValue: boolean
  title?: string
  direction?: 'right' | 'left'
  size?: string
}
withDefaults(defineProps<Props>(), {
  title: '',
  direction: 'right',
  size: '360px',
})
const emit = defineEmits<{ 'update:modelValue': [value: boolean] }>()
const close = () => emit('update:modelValue', false)
</script>

<template>
  <Teleport to="body">
    <Transition name="h-drawer">
      <div v-if="modelValue" class="h-drawer-overlay" @click.self="close">
        <div
          class="h-drawer"
          :class="`h-drawer--${direction}`"
          :style="{ width: direction === 'right' || direction === 'left' ? size : undefined }"
        >
          <div class="h-drawer__header">
            <span class="h-drawer__title">{{ title }}</span>
            <span class="h-drawer__close" @click="close">✕</span>
          </div>
          <div class="h-drawer__body">
            <slot />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.h-drawer-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.4);
  z-index: var(--z-dialog);
}
.h-drawer {
  position: fixed;
  top: 0;
  bottom: 0;
  background: var(--color-bg-secondary);
  box-shadow: var(--shadow-md);
  display: flex;
  flex-direction: column;
  transition: transform var(--duration-normal) var(--easing);
}
.h-drawer--right { right: 0; }
.h-drawer--left { left: 0; }
.h-drawer__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--color-border);
}
.h-drawer__title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-text-primary);
}
.h-drawer__close {
  cursor: pointer;
  color: var(--color-text-tertiary);
}
.h-drawer__close:hover { color: var(--color-text-primary); }
.h-drawer__body {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}
</style>
```

- [ ] **Step 4: 创建 HTabs + HTabPane**

```vue
<!-- HTabs.vue -->
<script setup lang="ts">
import { ref, provide, computed } from 'vue'

interface Props {
  modelValue?: string
}
const props = defineProps<Props>()
const emit = defineEmits<{ 'update:modelValue': [value: string] }>()

const tabs = ref<{ name: string; label: string }[]>([])
provide('h-tabs', {
  active: computed(() => props.modelValue),
  register: (name: string, label: string) => {
    if (!tabs.value.find(t => t.name === name)) tabs.value.push({ name, label })
  },
})
</script>

<template>
  <div class="h-tabs">
    <div class="h-tabs__header">
      <div
        v-for="tab in tabs"
        :key="tab.name"
        class="h-tabs__item"
        :class="{ 'h-tabs__item--active': modelValue === tab.name }"
        @click="emit('update:modelValue', tab.name)"
      >{{ tab.label }}</div>
    </div>
    <div class="h-tabs__content">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.h-tabs__header {
  display: flex;
  gap: 4px;
  border-bottom: 1px solid var(--color-border);
  margin-bottom: 16px;
}
.h-tabs__item {
  padding: 10px 16px;
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all var(--duration-fast) var(--easing);
}
.h-tabs__item:hover {
  color: var(--color-text-primary);
}
.h-tabs__item--active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
  font-weight: 500;
}
</style>
```

```vue
<!-- HTabPane.vue -->
<script setup lang="ts">
import { inject, computed, onMounted } from 'vue'

interface Props {
  name: string
  label: string
}
const props = defineProps<Props>()
const tabs = inject<any>('h-tabs')
const isActive = computed(() => tabs?.active.value === props.name)
onMounted(() => tabs?.register(props.name, props.label))
</script>

<template>
  <div v-show="isActive" class="h-tab-pane">
    <slot />
  </div>
</template>
```

- [ ] **Step 5: 创建各自的 index.ts，更新 ui/index.ts**

- [ ] **Step 6: 提交**

```bash
git add src/frontend/src/components/ui/HTable/ src/frontend/src/components/ui/HUpload/ src/frontend/src/components/ui/HDrawer/ src/frontend/src/components/ui/HTabs/
git commit -m "feat(ui): add HTable, HUpload, HDrawer, HTabs components"
```

---

### Task 19: HScrollbar + HAvatar + HSkeleton + HLoading 组件

**Files:**
- Create: `src/frontend/src/components/ui/HScrollbar/` (HScrollbar.vue, index.ts)
- Create: `src/frontend/src/components/ui/HAvatar/` (HAvatar.vue, index.ts)
- Create: `src/frontend/src/components/ui/HSkeleton/` (HSkeleton.vue, index.ts)
- Create: `src/frontend/src/components/ui/HLoading/` (directive.ts, index.ts)

- [ ] **Step 1: 创建 HScrollbar.vue**

```vue
<script setup lang="ts">
interface Props {
  maxHeight?: string
}
withDefaults(defineProps<Props>(), { maxHeight: '100%' })
</script>

<template>
  <div class="h-scrollbar" :style="{ maxHeight }">
    <div class="h-scrollbar__view">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.h-scrollbar {
  overflow: auto;
}
.h-scrollbar::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
.h-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.h-scrollbar::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: 3px;
}
.h-scrollbar::-webkit-scrollbar-thumb:hover {
  background: var(--color-border-hover);
}
</style>
```

- [ ] **Step 2: 创建 HAvatar.vue**

```vue
<script setup lang="ts">
interface Props {
  src?: string
  size?: number | string
  shape?: 'circle' | 'square'
}
withDefaults(defineProps<Props>(), {
  size: 40,
  shape: 'circle',
})
</script>

<template>
  <div
    class="h-avatar"
    :class="`h-avatar--${shape}`"
    :style="{ width: typeof size === 'number' ? `${size}px` : size, height: typeof size === 'number' ? `${size}px` : size }"
  >
    <img v-if="src" :src="src" class="h-avatar__img" />
    <slot v-else />
  </div>
</template>

<style scoped>
.h-avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--color-primary-bg);
  color: var(--color-primary);
  overflow: hidden;
  flex-shrink: 0;
}
.h-avatar--circle { border-radius: 50%; }
.h-avatar--square { border-radius: var(--radius-md); }
.h-avatar__img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
</style>
```

- [ ] **Step 3: 创建 HSkeleton.vue**

```vue
<script setup lang="ts">
interface Props {
  rows?: number
  animated?: boolean
}
withDefaults(defineProps<Props>(), { rows: 3, animated: true })
</script>

<template>
  <div class="h-skeleton">
    <div v-for="i in rows" :key="i" class="h-skeleton__line" :class="{ 'h-skeleton--animated': animated }"></div>
  </div>
</template>

<style scoped>
.h-skeleton__line {
  height: 16px;
  background: var(--color-bg-tertiary);
  border-radius: var(--radius-sm);
  margin-bottom: 12px;
}
.h-skeleton__line:last-child {
  width: 60%;
}
.h-skeleton--animated {
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}
@keyframes skeleton-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}
</style>
```

- [ ] **Step 4: 创建 HLoading 指令**

```typescript
// src/frontend/src/components/ui/HLoading/directive.ts
import type { Directive } from 'vue'

export const vHLoading: Directive = {
  mounted(el, binding) {
    if (!binding.value) return
    createOverlay(el)
  },
  updated(el, binding) {
    if (binding.value && !el.querySelector('.h-loading-overlay')) {
      createOverlay(el)
    } else if (!binding.value) {
      removeOverlay(el)
    }
  },
  unmounted(el) {
    removeOverlay(el)
  },
}

function createOverlay(el: HTMLElement) {
  el.style.position = 'relative'
  const overlay = document.createElement('div')
  overlay.className = 'h-loading-overlay'
  overlay.innerHTML = '<div class="h-loading-spinner"></div>'
  el.appendChild(overlay)
}

function removeOverlay(el: HTMLElement) {
  const overlay = el.querySelector('.h-loading-overlay')
  if (overlay) overlay.remove()
}
```

```typescript
// src/frontend/src/components/ui/HLoading/index.ts
export { vHLoading } from './directive'
```

在 `style.css` 中追加全局 loading 样式：

```css
.h-loading-overlay {
  position: absolute;
  inset: 0;
  background: rgba(10, 22, 40, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-loading);
  border-radius: inherit;
}
.h-loading-spinner {
  width: 24px;
  height: 24px;
  border: 3px solid rgba(255,255,255,0.2);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: h-spin 0.6s linear infinite;
}
@keyframes h-spin {
  to { transform: rotate(360deg); }
}
```

- [ ] **Step 5: 更新 ui/index.ts 和 main.ts 注册 v-h-loading 指令**

在 `ui/index.ts` 的 install 方法中添加：
```typescript
import { vHLoading } from './HLoading'
app.directive('h-loading', vHLoading)
```

- [ ] **Step 6: 提交**

```bash
git add src/frontend/src/components/ui/HScrollbar/ src/frontend/src/components/ui/HAvatar/ src/frontend/src/components/ui/HSkeleton/ src/frontend/src/components/ui/HLoading/
git commit -m "feat(ui): add HScrollbar, HAvatar, HSkeleton, v-h-loading directive"
```

---

## Phase 7: 页面迁移 — 第四、五批（高复杂度 + 最重页面）

### Task 20: 迁移第四批页面（5 个高复杂度文件）

**Files:**
- Modify: `src/frontend/src/pages/mcp-server/mcp-chat.vue`
- Modify: `src/frontend/src/pages/tool/tool.vue`
- Modify: `src/frontend/src/pages/model/model-editor.vue`
- Modify: `src/frontend/src/pages/mcp-server/mcp-server.vue`
- Modify: `src/frontend/src/pages/agent/agent-editor.vue`

- [ ] **Step 1: 迁移 mcp-chat.vue（14 处 el- 标签）**

按照统一替换策略：el-button→HButton、el-input→HInput、el-select→HSelect、el-icon→HIcon、ElMessage→HMessage。

- [ ] **Step 2: 迁移 tool.vue（14 处 el- 标签）**

- [ ] **Step 3: 迁移 model-editor.vue（21 处 el- 标签）**

这个文件较重，特别注意：
- el-form + el-form-item → HForm + HFormItem
- el-select + el-option → HSelect + HOption
- v-loading → v-h-loading

- [ ] **Step 4: 迁移 mcp-server.vue（21 处 el- 标签）**

这个文件使用了 el-table，替换为 HTable。

- [ ] **Step 5: 迁移 agent-editor.vue（34 处 el- 标签）**

这是第二重的文件。注意：
- 大量 el-form-item 表单布局
- el-select + el-option 下拉选择
- el-tooltip 提示
- ElMessageBox 确认对话框
- el-upload 文件上传
- el-tag 标签
- el-tabs + el-tab-pane 选项卡

- [ ] **Step 6: 逐文件验证**

- [ ] **Step 7: 提交**

```bash
git add src/frontend/src/pages/mcp-server/ src/frontend/src/pages/tool/ src/frontend/src/pages/model/ src/frontend/src/pages/agent/agent-editor.vue
git commit -m "feat(migrate): convert batch 4 high-complexity pages from Element Plus"
```

---

### Task 21: 迁移第五批页面（最重 + 公共组件）

**Files:**
- Modify: `src/frontend/src/components/dialog/create_agent/create_agent.vue`（27 处）
- Modify: `src/frontend/src/components/dialog/create_agent/AgentFormDialog.vue`
- Modify: `src/frontend/src/components/drawer/drawer.vue`（6 处）
- Modify: `src/frontend/src/pages/agent-skill/agent-skill.vue`（43 处，最重）
- Modify: `src/frontend/src/components/agentCard/agentCard.vue`
- Modify: `src/frontend/src/components/commonCard/commonCard.vue`
- Modify: `src/frontend/src/components/historyCard/histortCard.vue`

- [ ] **Step 1: 迁移公共组件（agentCard、commonCard、histortCard、drawer）**

- [ ] **Step 2: 迁移 create_agent.vue 和 AgentFormDialog.vue**

- [ ] **Step 3: 迁移 agent-skill.vue（43 处，分区域处理）**

这是最重的文件。建议分区域：
1. 先替换 script 中的所有 import 和 API 调用
2. 再按模板中的功能区域逐一替换 el- 标签
3. 最后清理样式

- [ ] **Step 4: 迁移剩余未覆盖的页面**

检查是否有遗漏：
- `pages/conversation/conversation.vue`
- `pages/homepage/homepage.vue`
- `pages/mars/mars-chat.vue`
- `pages/workspace/defaultPage/defaultPage.vue`
- `pages/workspace/taskGraphPage/taskGraphPage.vue`
- `pages/workspace/workspacePage/workspacePage.vue`
- `pages/conversation/defaultPage/defaultPage.vue`

- [ ] **Step 5: 提交**

```bash
git add src/frontend/src/components/ src/frontend/src/pages/agent-skill/
git commit -m "feat(migrate): convert batch 5 heaviest pages and shared components"
```

---

## Phase 8: 依赖清理与最终验证

### Task 22: 移除 Element Plus 依赖

**Files:**
- Modify: `src/frontend/package.json`
- Modify: `src/frontend/vite.config.ts`

- [ ] **Step 1: 移除 vite.config.ts 中的 Element Plus 插件**

```typescript
// vite.config.ts - 移除 Element Plus 相关
import { loadEnv, defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd())
  return {
    server: {
      host: '0.0.0.0',
      port: 8090,
      https: false,
      proxy: {
        '/api': {
          target: env.VITE_API_BASE_URL || 'http://localhost:7860',
          changeOrigin: true,
        }
      },
    },
    plugins: [vue()],
  }
})
```

- [ ] **Step 2: 从 package.json 移除 Element Plus 依赖**

```bash
cd src/frontend
npm uninstall element-plus unplugin-auto-import unplugin-vue-components
```

- [ ] **Step 3: 删除自动生成的类型文件**

```bash
rm -f src/frontend/src/components.d.ts src/frontend/src/auto-imports.d.ts
```

- [ ] **Step 4: 安装 HarmonyOS Sans Symbols（如可用）**

```bash
cd src/frontend
npm install harmonyos-sans-symbols --save
```

如果 npm 上不可用，改为 CDN 引入或使用 SVG 图标替代方案。

- [ ] **Step 5: 验证构建成功**

```bash
cd src/frontend && npm run build
```

预期：构建成功，无 Element Plus 相关警告或错误。

- [ ] **Step 6: 提交**

```bash
git add -A
git commit -m "chore: remove Element Plus dependencies and auto-import configs"
```

---

### Task 23: 样式硬编码色值清理

**Files:**
- 全部已迁移的 .vue 文件

- [ ] **Step 1: 全局搜索硬编码色值**

```bash
cd src/frontend/src
grep -rn '#[0-9a-fA-F]\{3,6\}' --include='*.vue' --include='*.css' | grep -v 'node_modules' | grep -v 'var(--'
```

- [ ] **Step 2: 逐文件替换残留硬编码色值为 CSS 变量**

常见替换：
- `#ffffff` / `#fff` → `#ffffff`（纯白可保留，或用于特定场景）
- `#000000` / `#000` → `var(--color-text-primary)`
- `#333` / `#666` / `#999` → `var(--color-text-secondary/tertiary)`
- `#4f81ff` / `#3b66db` → `var(--color-primary/primary-active)`
- `#f5f7fa` / `#f5f5f5` → `var(--color-bg-secondary/tertiary)`
- `#e5e7eb` / `#dcdfe6` → `var(--color-border)`

- [ ] **Step 3: 验证暗色和亮色模式下所有页面视觉正确**

- [ ] **Step 4: 提交**

```bash
git add -A
git commit -m "style: replace all hardcoded color values with CSS variables"
```

---

### Task 24: 最终验收

- [ ] **Step 1: 功能验收清单**

逐项检查：
- [ ] 登录/注册流程正常
- [ ] 会话聊天（含流式对话）正常
- [ ] 智能体创建/编辑/删除正常
- [ ] MCP Server 页面表格正常
- [ ] 知识库文件上传正常
- [ ] 模型编辑表单正常
- [ ] 所有消息提示（success/error/warning/info）正常
- [ ] 所有确认对话框（删除/退出）正常
- [ ] 侧边栏折叠/展开正常
- [ ] 主题切换（手动 + 系统跟随）正常

- [ ] **Step 2: 技术验收清单**

```bash
# 检查无 el- 前缀标签残留
grep -rn '<el-' src/frontend/src/ --include='*.vue' | wc -l
# 预期：0

# 检查无 ElMessage 引用残留
grep -rn 'ElMessage\|ElMessageBox\|ElLoading' src/frontend/src/ --include='*.vue' --include='*.ts' | wc -l
# 预期：0

# 检查无 element-plus import 残留
grep -rn 'element-plus' src/frontend/src/ --include='*.vue' --include='*.ts' | wc -l
# 预期：0

# 构建成功
cd src/frontend && npm run build
# 预期：成功，无警告
```

- [ ] **Step 3: 最终提交**

```bash
git add -A
git commit -m "chore: complete HarmonyOS Universe Blue redesign verification"
```

---

## 执行统计

| Phase | Tasks | 新建文件 | 修改文件 | 预估步骤 |
|-------|-------|---------|---------|---------|
| 1. 主题系统 | 2 | 1 | 2 | 8 |
| 2. P0 组件 | 5 | 11 | 2 | 18 |
| 3. 第1-2批迁移 | 4 | 0 | 8 | 16 |
| 4. P1 组件 | 5 | 14 | 1 | 18 |
| 5. 第3批迁移 | 1 | 0 | 9 | 5 |
| 6. P2 组件 | 2 | 16 | 1 | 11 |
| 7. 第4-5批迁移 | 2 | 0 | 12 | 10 |
| 8. 清理验收 | 3 | 0 | 全部 | 12 |
| **总计** | **24** | **~42** | **~35** | **~98** |

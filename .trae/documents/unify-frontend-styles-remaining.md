# 前端样式统一 — 剩余任务执行计划

## 概述

本计划承接之前会话的工作，完成 4 项样式统一任务中的剩余部分。经过代码库探索，确认当前状态：

| 任务 | 优先级 | 状态 | 说明 |
|------|--------|------|------|
| Task 3: box-shadow 统一 | 中 | ✅ 已完成 | 仅剩 glass-mixins.css 中的 token 定义（合法） |
| Task 4: 合并多 `<style>` 块 | 中 | ✅ 已完成 | 仅剩 HSelect.vue（teleport 场景，需保留） |
| Task 2: rgba → harmony-tokens | 高 | 🔶 进行中 | chatPage.vue 已完成 8 处，剩余 58 处待处理 |
| Task 1: 统一根类名 `.page` | 高 | ⬜ 未开始 | HAppShell 已全局包裹，需统一子页面根类名 |

---

## Task 1: 统一 pages/ 一级页面根类名

### 现状分析

- `HAppShell` 已在 [App.vue](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/App.vue#L8-L16) 全局包裹 `<router-view />`，所有路由页面均已被 HAppShell 包裹
- `index` 路由 (`/`) 作为全局布局容器（[index.vue](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/index.vue)），提供侧边栏 + 移动端导航，子页面通过 `<router-view />` 渲染
- 各一级子页面当前使用各自独立的根类名（如 `.skill-page`、`.agent-page`、`.knowledge-page` 等），缺乏统一约定

### 实施方案

**步骤 1: 在 [style.css](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/style.css) 中添加 `.page` 通用类**

在全局重置区块之后添加：

```css
/* ========== 页面根容器通用类 ========== */
.page {
  min-height: 100%;
  width: 100%;
  background: transparent;
}
```

**步骤 2: 为一级子页面根 div 添加 `page` 类**

在 `index` 路由的一级子页面中，为根 `<div>` 追加 `page` 类（保留原有类名，不替换）：

| 页面文件 | 当前根类 | 修改后 |
|----------|----------|--------|
| [homepage.vue](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/homepage/homepage.vue) | 需确认 | 追加 `page` |
| [conversation.vue](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/conversation/conversation.vue) | 需确认 | 追加 `page` |
| [construct.vue](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/construct/construct.vue#L50) | `agent-card` | `agent-card page` |
| [agent.vue](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/agent/agent.vue#L143) | `agent-page` | `agent-page page` |
| [agent-editor.vue](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/agent/agent-editor.vue) | 需确认 | 追加 `page` |
| [mcp-server.vue](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/mcp-server/mcp-server.vue#L710) | `mcp-server-page` | `mcp-server-page page` |
| [mcp-chat.vue](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/mcp-server/mcp-chat.vue#L2) | `mcp-chat-container` | `mcp-chat-container page` |
| [knowledge.vue](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/knowledge/knowledge.vue#L253) | `knowledge-page` | `knowledge-page page` |
| [knowledge-file.vue](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/knowledge/knowledge-file.vue#L539) | `knowledge-file-page` | `knowledge-file-page page` |
| [tool.vue](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/tool/tool.vue) | 需确认 | 追加 `page` |
| [agent-skill.vue](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/agent-skill/agent-skill.vue#L470) | `skill-page` | `skill-page page` |
| [model.vue](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/model/model.vue) | 需确认 | 追加 `page` |
| [model-editor.vue](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/model/model-editor.vue#L218) | `model-editor-page` | `model-editor-page page` |
| [profile.vue](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/profile/profile.vue) | 需确认 | 追加 `page` |
| [mars-chat.vue](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/mars/mars-chat.vue#L2) | `mars-output-page` | `mars-output-page page` |
| [hubPage.vue](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/interview/hubPage/hubPage.vue#L119) | `hub-page` | `hub-page page` |
| [voice-interview/index.vue](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/voice-interview/index.vue#L232) | `voice-interview-page` | `voice-interview-page page` |
| [workspace.vue](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/workspace/workspace.vue) | 需确认 | 追加 `page` |

**注意**：
- `login.vue` 和 `register.vue` 不属于 `index` 子路由（顶级路由），使用 `.auth-page` 已统一，不需追加 `page` 类
- `index.vue` 本身作为布局容器（`.ai-body`），不追加 `page` 类
- 需先读取每个标记"需确认"的文件，确认其根 div 结构后再修改

---

## Task 2: 清理 rgba → harmony-tokens 颜色变量

### 现状分析

经 [Grep](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src) 统计，`.vue` 文件中剩余 **58 处** rgba 调用。按处理策略分类如下：

### 分类与映射方案

#### A. 保留不动（11 处）

**A1. var() 回退值（4 处）** — 这些 rgba 作为 CSS 变量的回退值，属合法用法：
- [agent-skill.vue:2215](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/agent-skill/agent-skill.vue#L2215) — `var(--harmony-alert-bg, rgba(232, 64, 38, 0.1))`
- [mcp-server.vue:3090](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/mcp-server/mcp-server.vue#L3090) — `var(--harmony-warning-bg, rgba(230, 162, 60, 0.12))`
- [mcp-server.vue:3104](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/mcp-server/mcp-server.vue#L3104) — `var(--harmony-confirm-bg, rgba(100, 187, 92, 0.15))`
- [model.vue:1494](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/model/model.vue#L1494) — `var(--harmony-alert-bg, rgba(232, 64, 38, 0.1))`

**A2. 玻璃效果背景（6 处）** — 配合 `backdrop-filter: blur()` 使用，属毛玻璃效果，保留：
- [index.vue:286](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/index.vue#L286) — sidebar 玻璃背景 `rgba(255, 255, 255, 0.4)` + blur(80px)
- [index.vue:419](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/index.vue#L419) — content 玻璃背景 `rgba(255, 255, 255, 0.4)` + blur(80px)
- [index.vue:518](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/index.vue#L518) — more-grid__card 玻璃背景 `rgba(255, 255, 255, 0.45)` + blur(12px)
- [model.vue:623](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/model/model.vue#L623) — page-header 玻璃背景 `rgba(255, 255, 255, 0.5)` + blur(60px)
- [HSearch.vue:76](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/components/ui/HSearch/HSearch.vue#L76) — 玻璃背景 `rgba(255, 255, 255, 0.4)` + blur(8px)
- [HToolbar.vue:44](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/components/ui/HToolbar/HToolbar.vue#L44) — 玻璃背景 `rgba(255, 255, 255, 0.4)` + blur(80px)

**A3. gradient / filter / text-shadow（7 处）** — CSS 函数中的 rgba，无法用变量替换：
- [construct.vue:108](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/construct/construct.vue#L108) — `linear-gradient(... rgba(255, 255, 255, 0.1) ... rgba(255, 255, 255, 0.05))` + blur(20px)
- [construct.vue:144](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/construct/construct.vue#L144) — `filter: ... drop-shadow(... rgba(255, 255, 255, 0.3))`
- [construct.vue:153](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/construct/construct.vue#L153) — `text-shadow: ... rgba(0, 0, 0, 0.2)`
- [construct.vue:162](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/construct/construct.vue#L162) — `text-shadow: ... rgba(0, 0, 0, 0.1)`
- [construct.vue:178](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/construct/construct.vue#L178) — `filter: ... drop-shadow(... rgba(255, 255, 255, 0.5))`
- [conversation/defaultPage.vue:60](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/conversation/defaultPage/defaultPage.vue#L60) — `text-shadow: ... rgba(0, 0, 0, 0.1)`
- [conversation/defaultPage.vue:64](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/conversation/defaultPage/defaultPage.vue#L64) — `text-shadow: ... rgba(251, 191, 36, 0.3)`

**A4. 主题指示器（5 处）** — 亮/暗主题专用指示条，需与背景对比，保留：
- [HBottomTab.vue:152](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/components/ui/shell/HBottomTab.vue#L152) — 亮色指示条 `rgba(0, 0, 0, 0.2)`
- [HBottomTab.vue:164](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/components/ui/shell/HBottomTab.vue#L164) — 暗色指示条 `rgba(255, 255, 255, 0.5)`
- [HAIBottomBar.vue:35](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/components/ui/shell/HAIBottomBar.vue#L35) — 亮色指示条 `rgba(0, 0, 0, 0.2)`
- [HAIBottomBar.vue:39](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/components/ui/shell/HAIBottomBar.vue#L39) — 暗色指示条 `rgba(255, 255, 255, 0.5)`
- [HAIBottomBar.vue:43](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/components/ui/shell/HAIBottomBar.vue#L43) — 透明主题指示条 `rgba(255, 255, 255, 0.7)`

**A5. 玻璃欢迎图标（1 处）** — 配合 backdrop-filter 的玻璃效果：
- [conversation/defaultPage.vue:48](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/conversation/defaultPage/defaultPage.vue#L48) — `rgba(255, 255, 255, 0.1)` + blur(10px)

#### B. 直接映射到现有 token（18 处）

**B1. 白色近不透明背景 → `--harmony-comp-background-primary`（9 处）**：
- [homepage.vue:152](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/homepage/homepage.vue#L152) — `rgba(255, 255, 255, 0.8)` → `var(--harmony-comp-background-primary)`
- [homepage.vue:216](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/homepage/homepage.vue#L216) — `rgba(255, 255, 255, 0.7)` → `var(--harmony-comp-background-primary)`
- [chatPage.vue:690](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/conversation/chatPage/chatPage.vue#L690) — `rgba(255, 255, 255, 0.7)` → `var(--harmony-comp-background-primary)`
- [conversation/defaultPage.vue:89](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/conversation/defaultPage/defaultPage.vue#L89) — `rgba(255, 255, 255, 0.95)` → `var(--harmony-comp-background-primary)`
- [conversation/defaultPage.vue:118](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/conversation/defaultPage/defaultPage.vue#L118) — `rgba(255, 255, 255, 0.95)` → `var(--harmony-comp-background-primary)`
- [voice-interview/index.vue:403](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/voice-interview/index.vue#L403) — `rgba(255, 255, 255, 0.95)` → `var(--harmony-comp-background-primary)`
- [workspace.vue:408](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/workspace/workspace.vue#L408) — `rgba(255, 255, 255, 0.7)` → `var(--harmony-comp-background-primary)`
- [workspace.vue:568](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/workspace/workspace.vue#L568) — `rgba(255, 255, 255, 0.5)` → `var(--harmony-comp-background-primary)`
- [workspace.vue:601](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/workspace/workspace.vue#L601) — `rgba(255, 255, 255, 0.5)` → `var(--harmony-comp-background-primary)`
- [WorkspaceMobile.vue:159](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/workspace/workspacePage/WorkspaceMobile.vue#L159) — `rgba(255, 255, 255, 0.85)` → `var(--harmony-comp-background-primary)`

**B2. 黑色半透明背景 → `--harmony-comp-background-tertiary` / `secondary`（5 处）**：
- [homepage.vue:250](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/homepage/homepage.vue#L250) — `rgba(0, 0, 0, 0.05)` → `var(--harmony-comp-background-tertiary)`
- [HChipsTab.vue:52](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/components/ui/HChipsTab/HChipsTab.vue#L52) — `rgba(0, 0, 0, 0.047)` → `var(--harmony-comp-background-tertiary)`
- [HToolbar.vue:71](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/components/ui/HToolbar/HToolbar.vue#L71) — `rgba(0, 0, 0, 0.05)` → `var(--harmony-comp-background-tertiary)`
- [HChipsTab.vue:56](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/components/ui/HChipsTab/HChipsTab.vue#L56) — `rgba(0, 0, 0, 0.098)` → `var(--harmony-comp-background-secondary)`
- [HToolbar.vue:75](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/components/ui/HToolbar/HToolbar.vue#L75) — `rgba(0, 0, 0, 0.1)` → `var(--harmony-comp-background-secondary)`

**B3. 暗色遮罩 → `--harmony-overlay-heavy`（2 处）**：
- [profile.vue:494](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/profile/profile.vue#L494) — `rgba(10, 22, 40, 0.6)` → `var(--harmony-overlay-heavy)`
- [profile.vue:591](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/profile/profile.vue#L591) — `rgba(0, 0, 0, 0.5)` → `var(--harmony-overlay-heavy)`

**B4. 品牌蓝半透明背景 → `--harmony-comp-emphasize-tertiary`（1 处）**：
- [index.vue:341](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/index.vue#L341) — `rgba(10, 89, 247, 0.098)` → `var(--harmony-comp-emphasize-tertiary)`

**B5. 灰色半透明背景 → `--harmony-comp-background-secondary` / `divider`（2 处）**：
- [interview/chatPage.vue:541](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/interview/chatPage/chatPage.vue#L541) — `rgba(128, 128, 128, 0.15)` → `var(--harmony-comp-background-secondary)`
- [interview/chatPage.vue:549](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/interview/chatPage/chatPage.vue#L549) — `rgba(0, 0, 0, 0.2)` → `var(--harmony-comp-divider)`

#### C. 使用 color-mix 映射（13 处）

**C1. 黑色细边框 → `--harmony-comp-divider`（2 处）**：
- [homepage.vue:153](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/homepage/homepage.vue#L153) — `rgba(0, 0, 0, 0.06)` border → `var(--harmony-comp-divider)`
- [homepage.vue:217](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/homepage/homepage.vue#L217) — `rgba(0, 0, 0, 0.06)` border → `var(--harmony-comp-divider)`

**C2. 白色半透明边框 → color-mix（3 处）**：
- [HButton.vue:164](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/components/ui/HButton/HButton.vue#L164) — `rgba(255, 255, 255, 0.3)` → `color-mix(in srgb, var(--harmony-font-on-primary) 30%, transparent)`
- [profile.vue:505](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/profile/profile.vue#L505) — `rgba(255, 255, 255, 0.2)` → `color-mix(in srgb, var(--harmony-font-on-primary) 20%, transparent)`
- [workspace/defaultPage.vue:934](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/workspace/defaultPage/defaultPage.vue#L934) — `rgba(255,255,255,0.3)` → `color-mix(in srgb, var(--harmony-font-on-primary) 30%, transparent)`

**C3. 品牌蓝半透明边框 → color-mix（3 处）**：
- [login.vue:266](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/login/login.vue#L266) — `rgba(10, 89, 247, 0.4)` → `color-mix(in srgb, var(--harmony-brand) 40%, transparent)`
- [register.vue:273](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/login/register.vue#L273) — `rgba(10, 89, 247, 0.4)` → `color-mix(in srgb, var(--harmony-brand) 40%, transparent)`
- [workspace/defaultPage.vue:701](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/workspace/defaultPage/defaultPage.vue#L701) — `rgba(102, 126, 234, 0.3)` → `color-mix(in srgb, var(--harmony-brand) 30%, transparent)`

**C4. 警告色半透明背景 → color-mix（5 处）**：
- [knowledge.vue:1310](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/knowledge/knowledge.vue#L1310) — `rgba(232, 64, 38, 0.1)` → `color-mix(in srgb, var(--harmony-warning) 10%, transparent)`
- [reportPage.vue:587](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/interview/reportPage/reportPage.vue#L587) — `rgba(244, 67, 54, 0.1)` → `color-mix(in srgb, var(--harmony-warning) 10%, transparent)`
- [mcp-server.vue:3125](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/mcp-server/mcp-server.vue#L3125) — `rgba(232, 64, 38, 0.1)` → `color-mix(in srgb, var(--harmony-warning) 10%, transparent)`
- [tool.vue:2660](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/tool/tool.vue#L2660) — `rgba(232, 64, 38, 0.1)` → `color-mix(in srgb, var(--harmony-warning) 10%, transparent)`

**C5. 白色文字色 → `--harmony-font-on-primary`（2 处）**：
- [construct.vue:161](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/construct/construct.vue#L161) — `rgba(255, 255, 255, 0.9)` → `var(--harmony-font-on-primary)`
- [conversation/defaultPage.vue:70](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/pages/conversation/defaultPage/defaultPage.vue#L70) — `rgba(255, 255, 255, 0.9)` → `var(--harmony-font-on-primary)`

### 执行顺序

按文件分组执行，减少上下文切换：

1. **homepage.vue** — 5 处（B1×2, C1×2, B2×1）
2. **HChipsTab.vue** — 2 处（B2×2）
3. **HToolbar.vue** — 2 处（B2×2，玻璃背景保留）
4. **HButton.vue** — 1 处（C2）
5. **workspace.vue** — 3 处（B1×3）
6. **WorkspaceMobile.vue** — 1 处（B1）
7. **conversation/defaultPage.vue** — 4 处（B1×2, C5×1, A5 保留）
8. **chatPage.vue (conversation)** — 1 处（B1）
9. **voice-interview/index.vue** — 1 处（B1）
10. **interview/chatPage.vue** — 2 处（B2×2）
11. **profile.vue** — 3 处（B3×2, C2）
12. **index.vue** — 1 处（B4，玻璃背景保留）
13. **login.vue + register.vue** — 2 处（C3×2）
14. **workspace/defaultPage.vue** — 2 处（C2, C3）
15. **knowledge.vue + reportPage.vue + mcp-server.vue + tool.vue** — 4 处（C4×4）
16. **construct.vue** — 1 处（C5，其余保留）

---

## 验证步骤

### 1. Task 1 验证
- `npm run lint` 通过，无语法错误
- 浏览器中检查页面高度撑满、背景透明，无视觉回归
- 确认所有一级子页面根 div 均含 `page` 类

### 2. Task 2 验证
- `npm run lint` 通过
- 浏览器中检查各页面颜色显示正常，无明显变色
- Grep 确认剩余 rgba 均为合法保留场景（var 回退、玻璃效果、gradient/text-shadow/filter、主题指示器）
- 暗色模式下检查颜色对比度正常

### 3. 最终统计
- rgba 总数从 58 → 约 24（保留场景）
- 所有可映射的 rgba 均已替换为 harmony-tokens 变量或 color-mix

---

## 假设与决策

1. **HAppShell 已全局包裹**：经确认 [App.vue](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/App.vue) 中 HAppShell 已包裹 router-view，Task 1 无需再处理 HAppShell 包裹，仅需统一根类名
2. **保留原有类名**：添加 `page` 类时不替换原有根类名，避免破坏现有样式
3. **玻璃效果保留**：配合 `backdrop-filter: blur()` 的 rgba 背景属合法毛玻璃效果，保留不动
4. **color-mix 兼容性**：项目已在 [HInput.vue](file:///d:/HuaweiMoveData/Users/28966/Desktop/PJDEMO/KirinChat/src/frontend/src/components/ui/HInput/HInput.vue) 中使用 color-mix，确认浏览器支持
5. **主题指示器保留**：HBottomTab/HAIBottomBar 的指示条需与背景对比，属主题专用元素，保留原值
6. **`login.vue` / `register.vue` 不追加 `.page`**：它们是顶级路由（非 index 子路由），使用统一的 `.auth-page` 已足够

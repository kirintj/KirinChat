# 工作台移动端企业级重构 Spec

## Why
工作台 `workspacePage.vue` 当前采用桌面端双栏 Markdown 编辑器布局（左侧原始文本 / 右侧预览），并在 `<style>` 中仅做了非常轻量的 `@include mobile` 样式覆盖。手机屏幕上双栏并排不可用，历史记录列表、操作按钮、反馈弹窗等也未针对移动端触摸场景优化，导致工作台在移动端体验差且难以维护。

## What Changes
- 将 `workspacePage.vue` 拆分为：入口视图 `workspacePage.vue` + 桌面视图 `WorkspaceDesktop.vue` + 移动视图 `WorkspaceMobile.vue`
- 将业务逻辑抽离到共享 composable `useWorkspaceGuide.ts`，供桌面/移动视图复用
- 桌面端保持现有双栏编辑器与操作按钮布局不变
- 移动端采用独立 DOM 与交互：编辑/预览 Tab 切换、底部固定操作栏、历史记录卡片化、全屏反馈 Bottom Sheet
- 提取公共子组件：`GuideEditor.vue`、`GuidePreview.vue`、`HistoryList.vue`、`RegenerateDialog.vue`
- **BREAKING**: `workspacePage.vue` 的 `<style>` 块将大幅精简，原有桌面端样式迁移到 `WorkspaceDesktop.vue`，移动端样式迁移到 `WorkspaceMobile.vue`，调用方无需修改

## Impact
- Affected specs: 无依赖其他 spec
- Affected code:
  - `src/frontend/src/pages/workspace/workspacePage/workspacePage.vue`
  - 新增 `src/frontend/src/pages/workspace/workspacePage/WorkspaceDesktop.vue`
  - 新增 `src/frontend/src/pages/workspace/workspacePage/WorkspaceMobile.vue`
  - 新增 `src/frontend/src/pages/workspace/workspacePage/composables/useWorkspaceGuide.ts`
  - 新增 `src/frontend/src/pages/workspace/workspacePage/components/GuideEditor.vue`
  - 新增 `src/frontend/src/pages/workspace/workspacePage/components/GuidePreview.vue`
  - 新增 `src/frontend/src/pages/workspace/workspacePage/components/HistoryList.vue`
  - 新增 `src/frontend/src/pages/workspace/workspacePage/components/RegenerateDialog.vue`

## ADDED Requirements

### Requirement: 工作台移动端专用视图
系统 SHALL 在工作台页面识别到移动端（`isMobile === true`）时渲染 `WorkspaceMobile.vue`，桌面端渲染 `WorkspaceDesktop.vue`。

#### Scenario: 设备切换
- **WHEN** 用户从桌面浏览器缩放到 < 768px，或在手机上打开工作台
- **THEN** 页面自动切换为移动视图；反之 ≥ 768px 时切换回桌面视图

### Requirement: 移动端编辑/预览体验
系统 SHALL 在移动端提供适合窄屏的 Markdown 编辑与预览方式。

#### Scenario: 编辑与预览切换
- **WHEN** 用户在手机上查看工作台
- **THEN** 看到「编辑 / 预览」两个 Tab，默认显示预览；点击 Tab 可在编辑区和预览区之间切换

#### Scenario: 编辑区可用性
- **WHEN** 用户切换到编辑 Tab
- **THEN** 编辑文本框占满可用区域，支持滚动，字号适合移动端阅读

### Requirement: 移动端历史记录展示
系统 SHALL 在移动端以卡片列表形式展示历史会话记录，并支持展开/收起。

#### Scenario: 查看历史记录
- **WHEN** 已有会话包含多条历史上下文
- **THEN** 每条历史以卡片呈现，默认收起，点击卡片头部可展开查看用户问题与 AI 回答

#### Scenario: 触摸友好
- **WHEN** 用户点击历史卡片头部
- **THEN** 点击区域高度 ≥ 48px，展开/收起动画流畅

### Requirement: 移动端操作入口
系统 SHALL 在移动端将「重新生成」和「开始执行」按钮固定在底部，便于单手操作。

#### Scenario: 执行操作
- **WHEN** 用户在手机上查看生成后的指导手册
- **THEN** 底部始终可见「重新生成」和「开始执行」两个按钮，点击后行为与桌面端一致

### Requirement: 移动端反馈弹窗
系统 SHALL 在移动端将重新生成反馈输入改为底部弹出的 Sheet 面板。

#### Scenario: 重新生成
- **WHEN** 用户点击「重新生成」
- **THEN** 从屏幕底部滑出全宽输入面板，包含反馈文本域、字数统计、取消和确认按钮

### Requirement: 共享业务逻辑
系统 SHALL 通过 `useWorkspaceGuide` composable 共享加载会话、生成/重新生成指导手册、跳转任务图等核心逻辑，避免在桌面/移动两个视图中重复实现。

#### Scenario: 复用逻辑
- **WHEN** 桌面视图和移动视图都需要启动生成流
- **THEN** 两者调用同一个 `startGenerateGuidePrompt` 方法，状态和回调一致

## MODIFIED Requirements

### Requirement: workspacePage.vue 作为入口
`workspacePage.vue` 当前同时承担布局、业务逻辑、样式。修改后：
- 仅负责注入 `isMobile` 并选择渲染 `WorkspaceDesktop.vue` 或 `WorkspaceMobile.vue`
- 不保留桌面端或移动端的具体布局样式
- 保留路由参数解析等最小化入口逻辑

## REMOVED Requirements

### Requirement: 无
本次改动不删除任何已有功能，仅重构代码结构并新增移动端专用视图。

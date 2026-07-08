# 统一移动端适配规范

## Why
项目已有 `breakpoints.scss` 定义了统一的断点 mixin（mobile/tablet/desktop），也有 `mobile-scale.css` 定义了 HarmonyOS 移动端设计令牌，还有 `HAppShell.vue` 通过 `provide('isMobile')` 提供了 JS 级响应式能力。但大量页面和组件未使用这些统一设施，而是各自内联 `@media` 查询且断点值不一致，导致移动端适配碎片化、难以维护。

## What Changes
- 将所有内联 `@media` 查询迁移为使用 `breakpoints.scss` 的 mixin 或 `mobile-scale.css` 变量
- 消除断点值不一致问题（当前存在 480px、600px、768px、767px、900px、1100px、1200px、1400px 等混乱值）
- 统一 JS 层与 CSS 层的断点来源（`HAppShell.vue` 中 `BREAKPOINT = 768` 硬编码，应引用统一配置）
- 建立 `useBreakpoint` composable 替代散落的 `inject('isMobile')` 和 `window.innerWidth` 监听
- **BREAKING**: 所有使用内联 `@media` 的页面和组件需改用 mixin，断点语义可能有细微变化（如 `@media (max-width: 767px)` → `@include mobile` 语义一致，但 `@media (max-width: 900px)` 等非标准断点需对齐到最近的统一断点）

## Impact
- Affected code:
  - **页面** (~20个): agent.vue, agent-editor.vue, agent-skill.vue, conversation.vue, chatPage.vue, defaultPage.vue, construct.vue, dashboard.vue, hubPage.vue, mars-chat.vue, mcp-server.vue, mcp-chat.vue, knowledge.vue, knowledge-file.vue, homepage.vue, index.vue, notFound.vue, login.vue, register.vue, model.vue, model-editor.vue, tool.vue, workspace.vue, workspacePage.vue, taskGraphPage.vue, 以及 interview/ 和 voice-interview/ 下的多个子页面
  - **组件** (~30个): HAppShell.vue, HTitlebar.vue, HEmpty.vue, HAIBottomBar.vue, drawer.vue, histortCard.vue, 以及所有 H* UI 组件中使用 @media 的文件
  - **共享设施**: breakpoints.scss, mobile-scale.css, HAppShell.vue

## ADDED Requirements

### Requirement: useBreakpoint Composable
系统 SHALL 提供 `useBreakpoint()` composable，返回响应式的 `isMobile`、`isTablet`、`isDesktop`、`isWide` 状态，断点值与 `breakpoints.scss` 保持一致。

#### Scenario: 页面使用 composable 获取响应式状态
- **WHEN** 页面组件调用 `const { isMobile, isDesktop } = useBreakpoint()`
- **THEN** 返回的 ref 在窗口 resize 时自动更新，且断点值与 `breakpoints.scss` 定义一致（mobile: <768, tablet: 768-1199, desktop: ≥1200, wide: ≥1400）

#### Scenario: 替代 inject('isMobile')
- **WHEN** 页面当前使用 `inject('isMobile')` 获取移动端状态
- **THEN** 迁移后应改用 `useBreakpoint().isMobile`，保持相同语义

### Requirement: CSS 断点统一
系统 SHALL 确保所有 Vue 组件的 `<style lang="scss">` 中不包含裸写 `@media` 查询，而是通过 `@use` 引入 `breakpoints.scss` 并使用 mixin。

#### Scenario: 迁移内联 @media 为 mixin
- **WHEN** 组件中存在 `@media (max-width: 768px)` 或 `@media (max-width: 767px)`
- **THEN** 替换为 `@include mobile { ... }`

#### Scenario: 非标准断点对齐
- **WHEN** 组件中存在非标准断点如 `@media (max-width: 900px)` 或 `@media (max-width: 1100px)`
- **THEN** 对齐到最近的统一断点（900px → tablet-and-below, 1100px → tablet-and-below），并在注释中说明对齐理由

### Requirement: JS 断点与 CSS 断点一致
系统 SHALL 确保 JS 层判断移动端的断点值与 CSS 层 `breakpoints.scss` 的 `$bp-tablet` (768px) 一致。

#### Scenario: HAppShell 使用统一断点
- **WHEN** `HAppShell.vue` 判断 `window.innerWidth < BREAKPOINT`
- **THEN** `BREAKPOINT` 的值应从统一配置中获取，而非硬编码 `768`

### Requirement: mobile-scale.css 变量使用
系统 SHALL 在移动端布局中优先使用 `mobile-scale.css` 中定义的 HarmonyOS 移动端设计令牌（如 `--harmony-page-canvas-width-mobile`、`--harmony-page-padding-mobile`），而非硬编码的像素值。

#### Scenario: 移动端布局使用设计令牌
- **WHEN** 页面在移动端需要设置内边距、内容宽度等
- **THEN** 使用 `var(--harmony-page-padding-mobile)` 等令牌变量，而非硬编码 `16px`、`328px` 等

## MODIFIED Requirements

### Requirement: HAppShell 响应式基础
`HAppShell.vue` 当前硬编码 `BREAKPOINT = 768` 并通过 `provide('isMobile')` 传递响应式状态。修改后：
- 使用 `useBreakpoint()` composable 获取 `isMobile` 状态
- 仍然通过 `provide('isMobile', isMobile)` 保持向后兼容（过渡期）
- 在 `<style>` 中使用 `breakpoints.scss` mixin 而非内联 @media

## REMOVED Requirements

### Requirement: 无
无需要移除的需求。本次改动为纯重构，不删除任何已有功能。

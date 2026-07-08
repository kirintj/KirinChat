# Tasks

- [x] Task 1: 创建 useBreakpoint composable
  - [ ] 1.1: 在 `src/frontend/src/composables/` 下创建 `useBreakpoint.ts`，导出 `isMobile`、`isTablet`、`isDesktop`、`isWide` 响应式 ref，断点值与 `breakpoints.scss` 一致（768/1200/1400）
  - [ ] 1.2: 使用 `window.matchMedia` + `addEventListener('change')` 替代 `window.innerWidth` + resize 监听（性能更优）
  - [ ] 1.3: 确保 SSR 安全（检查 `typeof window !== 'undefined'`）

- [x] Task 2: 更新 HAppShell.vue 使用 useBreakpoint
  - [ ] 2.1: 替换硬编码 `BREAKPOINT = 768` 和手动 resize 监听为 `useBreakpoint()`
  - [ ] 2.2: 保持 `provide('isMobile', isMobile)` 向后兼容

- [x] Task 3: 迁移页面组件的内联 @media 为 breakpoints.scss mixin
  - [ ] 3.1: 迁移 workspace 域页面：workspace.vue, workspacePage.vue, taskGraphPage.vue, defaultPage.vue（workspace）
  - [ ] 3.2: 迁移 conversation 域页面：conversation.vue, chatPage.vue, defaultPage.vue（conversation）
  - [ ] 3.3: 迁移 agent/model/tool 域页面：agent.vue, agent-editor.vue, agent-skill.vue, model.vue, model-editor.vue, tool.vue
  - [ ] 3.4: 迁移其他页面：construct.vue, dashboard.vue, mars-chat.vue, mcp-server.vue, mcp-chat.vue, knowledge.vue, knowledge-file.vue, homepage.vue, index.vue, notFound.vue, login.vue, register.vue
  - [ ] 3.5: 迁移 interview 域子页面：hubPage.vue, resumePage.vue, resumeDetailPage.vue, reportPage.vue, questionDetailPage.vue, learningPage.vue, jdParsePage.vue, chatPage.vue（interview）, historyPage.vue, defaultPage.vue（interview）
  - [ ] 3.6: 迁移 voice-interview 域组件：index.vue, VoiceControls.vue, VoiceConfigDialog.vue, RealtimeSubtitle.vue, AudioRecorder.vue, AudioPlayer.vue

- [x] Task 4: 迁移 UI 组件的内联 @media 为 breakpoints.scss mixin
  - [ ] 4.1: 迁移 shell 组件：HTitlebar.vue, HEmpty.vue, HAIBottomBar.vue, HBottomTab.vue, HStatusbar.vue
  - [ ] 4.2: 迁移其他 UI 组件：HUpload, HTooltip, HToolbar, HTag, HTabs, HTable, HSwitch, HSkeleton, HSelect, HSearch, HMessageBox, HMessage, HList, HInput, HIcon, HForm, HDropdown, HDrawer, HDivider, HDialog, HChipsTab, HCardView, HButton, HAvatar, HScrollbar 中使用了 @media 的组件
  - [ ] 4.3: 迁移业务组件：drawer.vue, histortCard.vue, commonCard.vue, agentCard.vue, SkillStatCard.vue, RecentInterviewItem.vue, QuickEntryCard.vue, ActiveSessionCard.vue

- [x] Task 5: 对齐非标准断点值
  - [ ] 5.1: 处理 agent.vue 中 `@media (max-width: 900px)` 和 `@media (max-width: 600px)` — 对齐到 tablet-and-below 和 mobile
  - [ ] 5.2: 处理 agent-editor.vue 中 `@media (max-width: 1100px)` — 对齐到 tablet-and-below
  - [ ] 5.3: 处理 dashboard.vue 中 `@media (max-width: 1400px)` — 对齐到 wide 的反向或 desktop
  - [ ] 5.4: 处理 tool.vue 中 `@media (max-width: 1200px)` — 对齐到 desktop 的反向
  - [ ] 5.5: 处理 construct.vue 中 `@media (max-width: 1200px)` — 对齐到 desktop 的反向
  - [ ] 5.6: 处理 hubPage.vue 中 `@media (max-width: 1199px)` 和 `@media (max-width: 767px)` — 对齐到 desktop 反向和 mobile
  - [ ] 5.7: 处理 model.vue 中多处 `@media (max-width: 768px)` — 统一为 mobile mixin

- [x] Task 6: 推广 mobile-scale.css 设计令牌使用
  - [ ] 6.1: 检查各页面移动端样式中的硬编码像素值（padding、width、gap 等），替换为对应的 `--harmony-*-mobile` 变量
  - [ ] 6.2: 确保已使用 `--harmony-*-mobile` 变量的页面（conversation.vue, model.vue, tool.vue, agent.vue 等）用法正确

# Task Dependencies
- [Task 2] depends on [Task 1]
- [Task 3] depends on [Task 1] （部分页面可同时迁移 @media 和 inject→useBreakpoint）
- [Task 4] depends on [Task 1]
- [Task 5] depends on [Task 3] （在迁移 @media 的过程中一并处理非标准断点）
- [Task 6] depends on [Task 3, Task 4] （迁移完成后统一检查令牌使用）
- [Task 3] 和 [Task 4] 可并行执行

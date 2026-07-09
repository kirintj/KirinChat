# Tasks

- [x] Task 1: 抽离共享业务逻辑到 useWorkspaceGuide composable
  - [x] 1.1: 创建 `src/frontend/src/pages/workspace/workspacePage/composables/useWorkspaceGuide.ts`
  - [x] 1.2: 从现有 `workspacePage.vue` 迁移状态、计算属性、API 调用、路由跳转逻辑到 composable
  - [x] 1.3: 确保 composable 返回桌面/移动视图所需的全部响应式状态和方法
  - [x] 1.4: 验证 `workspacePage.vue` 可通过 composable 复现现有行为

- [x] Task 2: 创建公共子组件
  - [x] 2.1: 创建 `GuideEditor.vue`：封装 Markdown 原始文本编辑 textarea
  - [x] 2.2: 创建 `GuidePreview.vue`：封装 Markdown 预览渲染（复用 `parseMarkdown` 和 MdPreview 样式）
  - [x] 2.3: 创建 `HistoryList.vue`：封装历史记录列表与展开/收起交互
  - [x] 2.4: 创建 `RegenerateDialog.vue`：封装反馈输入弹窗，同时支持桌面弹窗和移动 Sheet 两种展示形式
  - [x] 2.5: 确保子组件 Props/Events 定义清晰，可被桌面/移动视图共用

- [x] Task 3: 创建 WorkspaceDesktop.vue 并迁移桌面端布局
  - [x] 3.1: 创建 `WorkspaceDesktop.vue`，复用现有桌面端 DOM 结构
  - [x] 3.2: 将 `workspacePage.vue` 中的桌面端 SCSS 样式迁移到 `WorkspaceDesktop.vue`
  - [x] 3.3: 在 `WorkspaceDesktop.vue` 中调用 `useWorkspaceGuide` 和公共子组件
  - [x] 3.4: 保持桌面端视觉和交互与重构前一致

- [x] Task 4: 创建 WorkspaceMobile.vue 并实现移动端视图
  - [x] 4.1: 创建 `WorkspaceMobile.vue`，使用 `inject('isMobile')` 或 `useBreakpoint()` 确认设备
  - [x] 4.2: 实现顶部状态/标题区域、编辑/预览 Tab 切换
  - [x] 4.3: 实现移动端历史记录卡片列表
  - [x] 4.4: 实现底部固定「重新生成」和「开始执行」按钮
  - [x] 4.5: 实现移动端底部 Sheet 形式的反馈输入面板
  - [x] 4.6: 为移动端编写独立的 SCSS 样式，使用 `--harmony-*-mobile` 设计令牌

- [x] Task 5: 重构 workspacePage.vue 为入口组件
  - [x] 5.1: 移除 `workspacePage.vue` 中的业务逻辑、桌面端 DOM 和样式
  - [x] 5.2: 在 `workspacePage.vue` 中注入 `isMobile` 并条件渲染 `WorkspaceDesktop.vue` / `WorkspaceMobile.vue`
  - [x] 5.3: 保留最小化入口代码（路由参数读取、组件导入）
  - [x] 5.4: 验证 `workspacePage.vue` 无语法错误且能正确挂载

- [x] Task 6: 回归验证
  - [x] 6.1: 桌面端双栏编辑器、历史记录、操作按钮、反馈弹窗视觉和交互无回归
  - [x] 6.2: 移动端编辑/预览 Tab、历史记录卡片、底部按钮、反馈 Sheet 可正常使用
  - [x] 6.3: 运行 TypeScript/Vue 类型检查，无新增类型错误
  - [x] 6.4: 检查无 `!important` 新增，保持与之前清理一致

# Task Dependencies
- [Task 2] depends on [Task 1]
- [Task 3] depends on [Task 1, Task 2]
- [Task 4] depends on [Task 1, Task 2]
- [Task 5] depends on [Task 3, Task 4]
- [Task 3] 和 [Task 4] 可并行执行
- [Task 6] depends on [Task 5]

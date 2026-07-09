# 工作台移动端企业级重构 验证清单

## 共享逻辑
- [x] `useWorkspaceGuide.ts` 已创建并导出所有必要状态和方法
- [x] 桌面/移动视图均通过 composable 获取业务逻辑，无重复代码
- [x] 会话加载、流式生成、重新生成、跳转任务图等行为正常

## 公共子组件
- [x] `GuideEditor.vue` 封装 Markdown 编辑 textarea，支持 readOnly 状态
- [x] `GuidePreview.vue` 正确渲染 Markdown，样式与重构前一致
- [x] `HistoryList.vue` 支持展开/收起，移动端触摸区域 ≥ 48px
- [x] `RegenerateDialog.vue` 支持桌面弹窗和移动 Sheet 两种模式

## 桌面视图
- [x] `WorkspaceDesktop.vue` 保持现有双栏编辑器布局
- [x] 历史记录、操作按钮、反馈弹窗视觉和交互无回归
- [x] 桌面端样式已从 `workspacePage.vue` 完整迁移

## 移动视图
- [x] `WorkspaceMobile.vue` 在 < 768px 下正确渲染
- [x] 编辑/预览 Tab 可正常切换
- [x] 历史记录以卡片列表展示，可展开/收起
- [x] 底部固定「重新生成」和「开始执行」按钮可点击
- [x] 反馈 Sheet 从底部滑出，输入、字数统计、取消/确认功能正常
- [x] 移动端样式使用 `--harmony-*-mobile` 设计令牌，无硬编码像素陷阱

## 入口组件
- [x] `workspacePage.vue` 仅作为入口，根据 `isMobile` 渲染对应视图
- [x] 无残留桌面端 DOM 和样式
- [x] 路由参数解析正常

## 质量门禁
- [x] TypeScript/Vue 类型检查通过，无新增错误
- [x] 无新增 `!important`
- [x] 无新增裸写 `@media` 查询（统一使用 `breakpoints.scss` mixin）
- [x] 代码无语法错误

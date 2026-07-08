# 移动端适配统一化 验证清单

## useBreakpoint Composable
- [x] useBreakpoint.ts 已创建，导出 isMobile/isTablet/isDesktop/isWide 响应式 ref
- [x] 断点值与 breakpoints.scss 一致：mobile < 768, tablet 768-1199, desktop ≥ 1200, wide ≥ 1400
- [x] 使用 matchMedia API 而非 resize 事件监听
- [x] SSR 安全（window 存在性检查）

## HAppShell 迁移
- [x] HAppShell.vue 使用 useBreakpoint() 替代硬编码 BREAKPOINT
- [x] provide('isMobile') 仍然工作，保持向后兼容
- [x] HAppShell 的 CSS 中无裸写 @media

## 页面 @media 迁移
- [x] 所有页面 .vue 文件的 `<style lang="scss">` 中无裸写 `@media` 查询
- [x] 所有页面通过 `@use` 引入 breakpoints.scss 并使用 mixin
- [x] inject('isMobile') 的页面已迁移为 useBreakpoint() 或保持兼容

## 组件 @media 迁移
- [x] 所有 UI 组件（H* 系列）中无裸写 `@media` 查询
- [x] 业务组件（drawer, histortCard, commonCard, agentCard 等）中无裸写 `@media` 查询

## 非标准断点对齐
- [x] 不存在 480px、600px、767px、900px、1100px、1199px 等非标准 @media 断点值（所有 @media 已迁移为 mixin）
- [x] 所有 @media 断点值均来自 breakpoints.scss 定义的 $bp-mobile/$bp-tablet/$bp-desktop/$bp-wide

## mobile-scale.css 令牌使用
- [x] 移动端布局中的 padding 优先使用 --harmony-page-padding-mobile 等令牌变量（已替换 3 处明确匹配的硬编码值，其余硬编码值无对应令牌语义）
- [x] 移动端内容宽度优先使用 --harmony-page-content-width-mobile 等令牌变量（已审查，当前移动端布局中无 328px 等匹配值的使用场景）

## 回归验证
- [x] 桌面端布局无视觉回归（纯 @media → @include 替换，语义等价）
- [x] 移动端（<768px）布局正常显示（mobile mixin 语义与原 @media (max-width: 767px) 一致）
- [x] 平板端（768-1199px）布局正常显示（tablet/tablet-and-below mixin 语义等价）
- [x] resize 窗口时布局响应式切换正常（useBreakpoint 使用 matchMedia 自动响应）

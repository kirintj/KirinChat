# 全页面移动端布局适配设计文档

## 概述

在壳层（statusbar + titlebar + bottomtab）已就位的基础上，对所有子页面的内容区进行移动端布局适配，严格遵循 hmos mobile-scale token 和布局规范。

### 范围

所有功能页面的移动端内容区布局改造，不涉及壳层（index.vue）改动。

### 参考规范

- hmos-design-visual-mobile SKILL.md
- references/1.layout/layout-list.md（列表布局）
- references/1.layout/layout-card.md（卡片布局）
- references/2.theme/mobile-scale.css（移动端间距 token）
- references/2.theme/harmony-tokens.css（主题 token）

---

## 1. 页面布局分类

| 页面 | 路由 | hmos 布局类型 | 内容形式 |
|------|------|-------------|----------|
| homepage | /homepage | mobile-card | 搜索 + 案例卡片网格 |
| conversation | /conversation | mobile-list | 会话列表（入口型 list item） |
| agent | /agent | mobile-card | 智能体卡片网格 |
| knowledge | /knowledge | mobile-list | 知识库列表（入口型 list item） |
| profile | /profile | mobile-list | 个人中心设置列表 |
| configuration | /configuration | mobile-list | 配置项列表 |
| interview | /interview | mobile-card | 面试功能卡片 |
| model | /model | mobile-list | 模型列表 |
| mars-chat | /mars | 独立页 | 聊天页，全屏无 titlebar |
| workspace | /workspace | mobile-list | 工作区列表 |
| dashboard | /dashboard | mobile-card | 数据卡片 |
| mcp-server | /mcp-server | mobile-list | MCP 服务列表 |
| tool | /tool | mobile-list | 工具列表 |
| agent-skill | /agent-skill | mobile-list | 技能列表 |

---

## 2. 统一改造规则

### 2.1 移动端断点

所有页面统一使用 `@media (max-width: 768px)` 作为移动端断点，与壳层 HAppShell 的 BREAKPOINT 一致。

### 2.2 内容宽度与间距

```scss
// 移动端内容区标准样式
@media (max-width: 768px) {
  .page-xxx {
    padding: var(--harmony-padding-level8); // 16px
    gap: var(--harmony-card-gap-mobile);     // 12px

    // 内容卡片
    .card {
      border-radius: var(--harmony-corner-radius-level8); // 16px
      padding: var(--harmony-padding-level8); // 16px
    }
  }
}
```

| Token | 值 | 用途 |
|-------|-----|------|
| `--harmony-page-padding-mobile` | 16px | 页面左右 padding |
| `--harmony-card-gap-mobile` | 12px | 卡片间距 |
| `--harmony-section-gap-mobile` | 16px | 区块间距 |
| `--harmony-corner-radius-level8` | 16px | 卡片圆角 |
| `--harmony-corner-radius-level6` | 12px | 小组件圆角 |

### 2.3 触摸交互规范

| 元素 | 最小高度 | 说明 |
|------|---------|------|
| 列表项 | 48px | 单行 item |
| 列表项（双行） | 64px | title + subtitle |
| 按钮 | 40px | 操作按钮 |
| 搜索框 | 40px | 搜索输入 |

### 2.4 移动端隐藏元素

以下元素在移动端必须隐藏：
- 桌面端侧边栏（conversation 的 sidebar）
- 表格表头（knowledge 的 list-header）
- 桌面端专属的操作按钮组（改为长按或滑动操作）
- 多列 grid 超出 2 列的部分

---

## 3. 各页面改造详情

### 3.1 homepage（mobile-card）

**现状**：已有基础移动端样式，但间距和圆角未对齐 hmos token。

**改造点**：
- 搜索框圆角：`20px` → `var(--harmony-corner-radius-level10)`（20px）
- 案例卡片圆角：`16px` → `var(--harmony-corner-radius-level8)`
- 卡片间距：`10px` → `var(--harmony-card-gap-mobile)`（12px）
- 页面 padding：`16px` → `var(--harmony-padding-level8)`

### 3.2 conversation（mobile-list）

**现状**：移动端 sidebar 仅缩小到 240px，未完全重构为列表视图。

**改造点**：
- 隐藏 sidebar，内容区占满全屏
- 默认显示会话列表（不显示右侧空白内容区）
- 列表项改为 `harmony-list` 样式：左侧头像 + 标题 + 副标题，右侧时间 + chevron
- 列表项高度：`var(--harmony-control-height-64)`（64px，双行）
- 新建按钮改为页面顶部操作区（搜索框右侧或下方）
- 创建会话对话框改为底部弹出半模态

### 3.3 agent（mobile-card）

**现状**：已有响应式，移动端改为单列，但间距未对齐 hmos token。

**改造点**：
- 页面 padding：`20px 16px` → `var(--harmony-padding-level8)`
- 页面头部：改为纵向布局，搜索 + 创建按钮换行
- 卡片网格：`1fr`（单列），间距 `var(--harmony-card-gap-mobile)`
- 卡片圆角：`var(--harmony-corner-radius-level8)`

### 3.4 knowledge（mobile-list）

**现状**：桌面端表格布局，移动端无适配。

**改造点**：
- 隐藏表格表头（`.list-header`）
- 表格行改为卡片列表：左侧图标 + 名称 + 描述，右侧文件数 + 操作
- 每个知识库项改为独立圆角卡片
- 操作按钮改为图标按钮横向排列
- 创建/编辑对话框改为底部弹出

### 3.5 profile（mobile-list）

**改造点**：
- 个人信息区改为顶部 hero 卡片
- 设置项改为 `harmony-list` 样式：左侧图标 + 标题，右侧 chevron
- 分组卡片间距：`var(--harmony-section-gap-mobile)`

### 3.6 configuration（mobile-list）

**改造点**：
- 配置项改为 `harmony-list` 样式
- 开关项保留 switch 控件
- 分组卡片间距：`var(--harmony-section-gap-mobile)`

### 3.7 interview（mobile-card）

**改造点**：
- 功能入口卡片改为 2 列网格
- 卡片间距：`var(--harmony-card-gap-mobile)`
- 卡片圆角：`var(--harmony-corner-radius-level8)`

### 3.8 model（mobile-list）

**改造点**：
- 模型列表改为卡片列表
- 每个模型项：左侧图标 + 名称 + 描述，右侧状态 + 操作

### 3.9 mars-chat（独立页）

**现状**：聊天页，无需 titlebar。

**改造点**：
- 确保全屏布局，无多余 padding
- 输入框固定底部，适配安全区

### 3.10 workspace / dashboard / mcp-server / tool / agent-skill

**改造点**：
- 统一应用 mobile-list 或 mobile-card 布局
- 间距和圆角对齐 hmos token

---

## 4. 实施顺序

1. **conversation**（最高优先级，核心页面，改动最大）
2. **homepage**（已有基础，微调即可）
3. **agent**（已有响应式，微调）
4. **knowledge**（表格→列表，改动较大）
5. **profile / configuration**（设置类页面）
6. **其余页面**（interview, model, workspace, dashboard, mcp-server, tool, agent-skill）
7. **mars-chat**（独立页，最后处理）

---

## 5. 验收标准

- [ ] 所有页面在 360px 宽度下布局正确
- [ ] 间距和圆角全部使用 hmos token
- [ ] 无硬编码的 px 值（除特殊场景外）
- [ ] 触摸交互元素最小高度 48px
- [ ] 桌面端样式无回归
- [ ] 深色模式 token 正确映射

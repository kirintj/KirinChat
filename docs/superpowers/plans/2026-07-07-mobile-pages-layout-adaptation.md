# 全页面移动端布局适配实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将所有功能页面的内容区适配为 hmos 移动端布局规范

**Architecture:** 在各页面 Vue 组件的 `<style>` 中添加/更新 `@media (max-width: 768px)` 响应式样式，隐藏桌面端元素，将间距/圆角替换为 hmos mobile-scale token，表格布局转为卡片列表。

**Tech Stack:** Vue 3 + SCSS, hmos design tokens (harmony-tokens.css, mobile-scale.css)

---

## 文件结构

所有改动集中在各页面的 `<style lang="scss" scoped>` 块内，不新增文件。

| 操作 | 文件 | 布局类型 |
|------|------|----------|
| Modify | `src/frontend/src/pages/conversation/conversation.vue` | mobile-list |
| Modify | `src/frontend/src/pages/interview/interview.vue` | mobile-list |
| Modify | `src/frontend/src/pages/workspace/workspace.vue` | mobile-list |
| Modify | `src/frontend/src/pages/knowledge/knowledge.vue` | mobile-list |
| Modify | `src/frontend/src/pages/model/model.vue` | mobile-list |
| Modify | `src/frontend/src/pages/mcp-server/mcp-server.vue` | mobile-list |
| Modify | `src/frontend/src/pages/tool/tool.vue` | mobile-list |
| Modify | `src/frontend/src/pages/agent-skill/agent-skill.vue` | mobile-list |
| Modify | `src/frontend/src/pages/profile/profile.vue` | mobile-list |
| Modify | `src/frontend/src/pages/configuration/configuration.vue` | mobile-list |
| Modify | `src/frontend/src/pages/homepage/homepage.vue` | mobile-card |
| Modify | `src/frontend/src/pages/agent/agent.vue` | mobile-card |
| Modify | `src/frontend/src/pages/dashboard/dashboard.vue` | mobile-card |
| Modify | `src/frontend/src/pages/mars/mars-chat.vue` | 独立页 |

---

## 通用 Token 参考

```scss
// 移动端间距
$mobile-padding: var(--harmony-padding-level8);      // 16px
$mobile-card-gap: var(--harmony-card-gap-mobile);     // 12px
$mobile-section-gap: var(--harmony-section-gap-mobile); // 16px

// 圆角
$card-radius: var(--harmony-corner-radius-level8);    // 16px
$small-radius: var(--harmony-corner-radius-level6);   // 12px

// 控件高度
$control-h48: var(--harmony-control-height-48, 48px);
$control-h40: var(--harmony-control-height-40, 40px);

// 字体
$font-body-m: var(--harmony-font-size-body-m);        // 14px
$font-body-s: var(--harmony-font-size-body-s);        // 12px
$font-subtitle-m: var(--harmony-font-size-subtitle-m); // 16px
```

---

## Task 1: conversation（sidebar+content → 全屏列表）

**Files:**
- Modify: `src/frontend/src/pages/conversation/conversation.vue`

**当前问题:** 移动端 sidebar 缩到 240px 但仍显示，内容区被压缩。

- [ ] **Step 1: 替换移动端媒体查询**

找到现有的 `@media (max-width: 768px)` 和 `@media (max-width: 480px)` 块，替换为：

```scss
@media (max-width: 768px) {
  .conversation-main {
    flex-direction: column;
    height: 100%;

    .sidebar {
      display: none; // 隐藏桌面端侧边栏
    }

    .content {
      flex: 1;
      border-left: none;
      margin: 0;
    }
  }

  // 创建对话框改为底部弹出
  .create-dialog {
    width: 100%;
    max-width: 100%;
    height: auto;
    max-height: 85vh;
    border-radius: var(--harmony-corner-radius-level12) var(--harmony-corner-radius-level12) 0 0;

    .dialog-body {
      padding: var(--harmony-padding-level8);
      border-radius: var(--harmony-corner-radius-level12) var(--harmony-corner-radius-level12) 0 0;
    }

    .dialog-footer {
      padding: var(--harmony-padding-level6) var(--harmony-padding-level8);
    }
  }
}
```

- [ ] **Step 2: 在模板中添加移动端会话列表**

在 `<template>` 的 `.content` div 内、`<router-view />` 之前，添加移动端会话列表视图。需要先判断当前路由是否为默认页（无 dialog_id），如果是则显示列表。

在 `.conversation-main` 内、`.content` 之前添加：

```html
<!-- 移动端会话列表（当没有选中会话时显示） -->
<div v-if="isMobile && !selectedDialog" class="mobile-dialog-list">
  <div class="mobile-dialog-header">
    <h2>会话列表</h2>
    <button class="mobile-create-btn" @click="openCreateDialog">+ 新建</button>
  </div>
  <div class="mobile-dialog-items">
    <histortCard
      v-for="dialog in filteredDialogs"
      :key="dialog.dialogId"
      :item="dialog"
      @select="selectDialog(dialog.dialogId)"
      @delete="deleteDialog(dialog.dialogId)"
    />
  </div>
</div>
```

需要在 script 中注入 isMobile：

```typescript
const isMobile = inject<import('vue').Ref<boolean>>('isMobile', ref(false))
```

- [ ] **Step 3: 添加移动端列表样式**

```scss
.mobile-dialog-list {
  display: none;

  @media (max-width: 768px) {
    display: flex;
    flex-direction: column;
    height: 100%;
    padding: var(--harmony-padding-level8);
    gap: var(--harmony-card-gap-mobile);
    overflow-y: auto;

    .mobile-dialog-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: var(--harmony-padding-level4);

      h2 {
        font-size: var(--harmony-font-size-title-s);
        font-weight: 600;
        color: var(--harmony-font-primary);
        margin: 0;
      }

      .mobile-create-btn {
        height: var(--harmony-control-height-36, 36px);
        padding: 0 var(--harmony-padding-level8);
        background: var(--harmony-brand);
        color: white;
        border: none;
        border-radius: var(--harmony-corner-radius-level6);
        font-size: var(--harmony-font-size-body-m);
        font-weight: 500;
        cursor: pointer;
      }
    }

    .mobile-dialog-items {
      display: flex;
      flex-direction: column;
      gap: var(--harmony-card-gap-mobile);
    }
  }
}
```

- [ ] **Step 4: 在浏览器中验证**

在 360px 宽度下检查：侧边栏隐藏、会话列表全屏显示、点击会话可跳转、新建按钮可用。

- [ ] **Step 5: 提交**

```bash
git add src/frontend/src/pages/conversation/conversation.vue
git commit -m "feat(conversation): mobile list layout adaptation"
```

---

## Task 2: interview（sidebar+content → 全屏列表）

**Files:**
- Modify: `src/frontend/src/pages/interview/interview.vue`

**当前问题:** 无移动端适配，sidebar 固定 280px。

- [ ] **Step 1: 读取 interview.vue 的 <style> 部分**

确认当前无 @media 查询，记录 `.interview-container` 和 `.sidebar` 的结构。

- [ ] **Step 2: 添加移动端媒体查询**

在 `<style>` 末尾添加：

```scss
@media (max-width: 768px) {
  .interview-container {
    flex-direction: column;
    height: 100%;

    .sidebar {
      display: none;
    }

    .content {
      flex: 1;
      border-left: none;
    }
  }
}
```

- [ ] **Step 3: 在模板中注入 isMobile 并添加移动端列表**

参照 conversation 的模式，在模板中添加移动端会话列表视图。

- [ ] **Step 4: 验证并提交**

```bash
git add src/frontend/src/pages/interview/interview.vue
git commit -m "feat(interview): mobile list layout adaptation"
```

---

## Task 3: workspace（sidebar+content → 全屏列表）

**Files:**
- Modify: `src/frontend/src/pages/workspace/workspace.vue`

**当前问题:** 已有 @media 但 sidebar 仅缩到 240px，未完全隐藏。

- [ ] **Step 1: 更新现有媒体查询**

找到 `@media (max-width: 768px)` 块，将 sidebar 改为 `display: none`：

```scss
@media (max-width: 768px) {
  .workspace-root {
    flex-direction: column;

    .sidebar-panel {
      display: none;
    }

    .content-area {
      flex: 1;
      border-left: none;
    }
  }
}
```

- [ ] **Step 2: 添加移动端会话列表视图**

参照 conversation 的模式。

- [ ] **Step 3: 验证并提交**

```bash
git add src/frontend/src/pages/workspace/workspace.vue
git commit -m "feat(workspace): mobile list layout adaptation"
```

---

## Task 4: knowledge（表格 → 卡片列表）

**Files:**
- Modify: `src/frontend/src/pages/knowledge/knowledge.vue`

**当前问题:** 完全无移动端适配，6 列表格在小屏无法使用。

- [ ] **Step 1: 添加移动端媒体查询**

在 `<style>` 末尾添加：

```scss
@media (max-width: 768px) {
  .knowledge-page {
    padding: var(--harmony-padding-level8);

    .page-header {
      flex-direction: column;
      align-items: stretch;
      gap: var(--harmony-padding-level8);
      padding: var(--harmony-padding-level8);

      .header-title {
        h2 {
          font-size: var(--harmony-font-size-title-s);
        }
      }

      .header-actions {
        width: 100%;
      }
    }

    .knowledge-container {
      .list-header {
        display: none; // 隐藏表格头
      }

      .knowledge-list {
        .knowledge-row {
          display: flex;
          flex-direction: column;
          gap: var(--harmony-padding-level4);
          padding: var(--harmony-padding-level8);
          border-radius: var(--harmony-corner-radius-level8);
          margin-bottom: var(--harmony-card-gap-mobile);
          background: var(--harmony-comp-background-primary);
          border: 1px solid var(--harmony-comp-divider);

          .col-name {
            .knowledge-info {
              .knowledge-name {
                font-size: var(--harmony-font-size-body-l);
              }
            }
          }

          .col-desc {
            .knowledge-desc {
              white-space: normal;
              display: -webkit-box;
              -webkit-line-clamp: 2;
              -webkit-box-orient: vertical;
              font-size: var(--harmony-font-size-body-m);
            }
          }

          .col-files, .col-size, .col-time {
            display: none; // 隐藏次要信息
          }

          .col-actions {
            display: flex;
            gap: var(--harmony-padding-level4);
            justify-content: flex-end;
            padding-top: var(--harmony-padding-level4);
            border-top: 1px solid var(--harmony-comp-divider);
          }
        }
      }
    }
  }

  // 对话框移动端适配
  .dialog-container {
    width: calc(100% - var(--harmony-padding-level16));
    max-width: 100%;
  }

  .delete-dialog-container {
    width: calc(100% - var(--harmony-padding-level16));
    max-width: 100%;
  }
}
```

- [ ] **Step 2: 验证并提交**

```bash
git add src/frontend/src/pages/knowledge/knowledge.vue
git commit -m "feat(knowledge): mobile card list layout adaptation"
```

---

## Task 5: model（表格 → 卡片列表）

**Files:**
- Modify: `src/frontend/src/pages/model/model.vue`

**当前问题:** 已有 @media 但表格列仍然横向排列。

- [ ] **Step 1: 更新移动端媒体查询**

找到 `@media (max-width: 768px)` 块，替换为：

```scss
@media (max-width: 768px) {
  .model-page {
    padding: var(--harmony-padding-level8);

    .page-header {
      flex-direction: column;
      align-items: stretch;
      gap: var(--harmony-padding-level8);
      padding: var(--harmony-padding-level8);
    }

    .header-right {
      width: 100%;
      flex-wrap: wrap;
    }

    .search-box {
      flex: 1;
      min-width: 0;
    }

    .model-container {
      .list-header {
        display: none;
      }

      .model-list {
        .model-row {
          display: flex;
          flex-direction: column;
          gap: var(--harmony-padding-level4);
          padding: var(--harmony-padding-level8);
          border-radius: var(--harmony-corner-radius-level8);
          margin-bottom: var(--harmony-card-gap-mobile);

          .col-provider, .col-type, .col-url {
            display: none;
          }

          .col-actions {
            display: flex;
            justify-content: flex-end;
            padding-top: var(--harmony-padding-level4);
            border-top: 1px solid var(--harmony-comp-divider);
          }
        }
      }
    }
  }

  .dialog-container, .delete-dialog-container {
    width: calc(100% - var(--harmony-padding-level16));
    max-width: 100%;
  }
}
```

- [ ] **Step 2: 验证并提交**

```bash
git add src/frontend/src/pages/model/model.vue
git commit -m "feat(model): mobile card list layout adaptation"
```

---

## Task 6: mcp-server（表格 → 卡片列表）

**Files:**
- Modify: `src/frontend/src/pages/mcp-server/mcp-server.vue`

**当前问题:** 已有部分 @media 但 HTML `<table>` 在小屏溢出。

- [ ] **Step 1: 更新移动端媒体查询**

```scss
@media (max-width: 768px) {
  .mcp-server-page {
    padding: var(--harmony-padding-level8);

    .page-header {
      flex-direction: column;
      align-items: stretch;
      gap: var(--harmony-padding-level8);
      padding: var(--harmony-padding-level8);
    }

    .header-right {
      width: 100%;
      flex-wrap: wrap;
    }

    .server-list {
      .server-table-wrapper {
        overflow-x: auto;
      }

      // 如果有卡片式备用视图优先使用
      .server-table {
        min-width: 600px; // 保持表格可横向滚动
      }
    }
  }

  .modal-dialog, .config-dialog {
    width: calc(100% - var(--harmony-padding-level16));
    max-width: 100%;
    max-height: 85vh;
  }
}
```

- [ ] **Step 2: 验证并提交**

```bash
git add src/frontend/src/pages/mcp-server/mcp-server.vue
git commit -m "feat(mcp-server): mobile layout adaptation"
```

---

## Task 7: tool（表格 → 卡片列表）

**Files:**
- Modify: `src/frontend/src/pages/tool/tool.vue`

**当前问题:** 已有 @media 但 grid 列表在小屏仍有多列。

- [ ] **Step 1: 更新移动端媒体查询**

```scss
@media (max-width: 768px) {
  .tool-page {
    padding: var(--harmony-padding-level8);

    .page-header {
      flex-direction: column;
      align-items: stretch;
      gap: var(--harmony-padding-level8);
      padding: var(--harmony-padding-level8);
    }

    .tool-controls {
      flex-direction: column;
      gap: var(--harmony-padding-level4);
    }

    .tool-container {
      .list-header {
        display: none;
      }

      .tool-row {
        display: flex;
        flex-direction: column;
        gap: var(--harmony-padding-level4);
        padding: var(--harmony-padding-level8);
        border-radius: var(--harmony-corner-radius-level8);
        margin-bottom: var(--harmony-card-gap-mobile);
      }
    }
  }

  .drawer-content {
    width: 100%;
  }

  .delete-modal {
    width: calc(100% - var(--harmony-padding-level16));
    max-width: 100%;
  }
}
```

- [ ] **Step 2: 验证并提交**

```bash
git add src/frontend/src/pages/tool/tool.vue
git commit -m "feat(tool): mobile card list layout adaptation"
```

---

## Task 8: agent-skill（表格 → 卡片列表）

**Files:**
- Modify: `src/frontend/src/pages/agent-skill/agent-skill.vue`

- [ ] **Step 1: 更新移动端媒体查询**

```scss
@media (max-width: 768px) {
  .skill-page {
    padding: var(--harmony-padding-level8);

    .page-header {
      flex-direction: column;
      align-items: stretch;
      gap: var(--harmony-padding-level8);
      padding: var(--harmony-padding-level8);
    }

    .skill-container {
      .list-header {
        display: none;
      }

      .skill-row {
        display: flex;
        flex-direction: column;
        gap: var(--harmony-padding-level4);
        padding: var(--harmony-padding-level8);
        border-radius: var(--harmony-corner-radius-level8);
        margin-bottom: var(--harmony-card-gap-mobile);
      }
    }
  }

  // 详情对话框全屏
  .detail-dialog {
    width: 100%;
    max-width: 100%;
    height: 100vh;
    max-height: 100vh;
    border-radius: 0;

    .ide-body {
      .ide-sidebar {
        display: none;
      }
    }
  }

  .create-dialog, .add-file-dialog {
    width: calc(100% - var(--harmony-padding-level16));
    max-width: 100%;
  }
}
```

- [ ] **Step 2: 验证并提交**

```bash
git add src/frontend/src/pages/agent-skill/agent-skill.vue
git commit -m "feat(agent-skill): mobile card list layout adaptation"
```

---

## Task 9: profile（mobile-list 适配）

**Files:**
- Modify: `src/frontend/src/pages/profile/profile.vue`

**当前问题:** 完全无移动端适配。

- [ ] **Step 1: 添加移动端媒体查询**

```scss
@media (max-width: 768px) {
  .profile-page {
    padding: var(--harmony-padding-level8);

    .profile-header {
      flex-direction: column;
      align-items: stretch;
      gap: var(--harmony-padding-level8);
    }

    .profile-content {
      max-width: 100%;
      padding: var(--harmony-padding-level8);
      gap: var(--harmony-card-gap-mobile);

      .profile-card {
        padding: var(--harmony-padding-level8);
        border-radius: var(--harmony-corner-radius-level8);

        .avatar-section {
          flex-direction: column;
          align-items: center;
          gap: var(--harmony-padding-level8);

          .avatar-wrapper {
            width: 80px;
            height: 80px;
          }
        }
      }
    }
  }

  .custom-dialog {
    width: calc(100% - var(--harmony-padding-level16));
    max-width: 100%;
  }
}
```

- [ ] **Step 2: 验证并提交**

```bash
git add src/frontend/src/pages/profile/profile.vue
git commit -m "feat(profile): mobile list layout adaptation"
```

---

## Task 10: configuration（mobile-list 适配）

**Files:**
- Modify: `src/frontend/src/pages/configuration/configuration.vue`

**当前问题:** 完全无移动端适配。

- [ ] **Step 1: 添加移动端媒体查询**

```scss
@media (max-width: 768px) {
  .editor {
    padding: var(--harmony-padding-level8);

    .editor-container {
      width: 100%;
      height: auto;
      min-height: 60vh;
      padding: var(--harmony-padding-level8);
      border-radius: var(--harmony-corner-radius-level8);
    }

    .button {
      width: 100%;
      padding: var(--harmony-padding-level6) var(--harmony-padding-level8);
    }
  }
}
```

- [ ] **Step 2: 验证并提交**

```bash
git add src/frontend/src/pages/configuration/configuration.vue
git commit -m "feat(configuration): mobile list layout adaptation"
```

---

## Task 11: homepage（token 微调）

**Files:**
- Modify: `src/frontend/src/pages/homepage/homepage.vue`

**当前问题:** 已有移动端样式但部分硬编码 px。

- [ ] **Step 1: 更新移动端媒体查询**

```scss
@media (max-width: 768px) {
  .homepage {
    justify-content: flex-start;
    padding-top: var(--harmony-padding-level8);
    gap: var(--harmony-padding-level8);
    padding-left: var(--harmony-padding-level8);
    padding-right: var(--harmony-padding-level8);
  }

  .search-section {
    max-width: 100%;

    .search-box {
      border-radius: var(--harmony-corner-radius-level8);
      padding: var(--harmony-padding-level8);
    }
  }

  .examples-section {
    max-width: 100%;

    .examples-grid {
      gap: var(--harmony-card-gap-mobile);
    }

    .example-card {
      border-radius: var(--harmony-corner-radius-level8);
      padding: var(--harmony-padding-level8);
    }
  }
}
```

- [ ] **Step 2: 验证并提交**

```bash
git add src/frontend/src/pages/homepage/homepage.vue
git commit -m "feat(homepage): mobile token alignment"
```

---

## Task 12: agent（token 微调）

**Files:**
- Modify: `src/frontend/src/pages/agent/agent.vue`

**当前问题:** 已有响应式但断点和 token 不统一。

- [ ] **Step 1: 更新移动端媒体查询**

将 `@media (max-width: 600px)` 合并到 768px 断点：

```scss
@media (max-width: 768px) {
  .agent-page {
    padding: var(--harmony-padding-level8);

    .page-header {
      flex-direction: column;
      align-items: stretch;
      gap: var(--harmony-padding-level8);
      padding: var(--harmony-padding-level8);
      border-radius: var(--harmony-corner-radius-level8);
    }

    .header-right {
      width: 100%;
      flex-wrap: wrap;
      gap: var(--harmony-padding-level4);
    }

    .search-box {
      flex: 1;
      min-width: 0;
      width: auto;
    }

    .agent-grid {
      grid-template-columns: 1fr;
      gap: var(--harmony-card-gap-mobile);
    }

    .agent-card {
      padding: var(--harmony-padding-level8);
      border-radius: var(--harmony-corner-radius-level8);
    }
  }

  .dialog-card {
    width: calc(100% - var(--harmony-padding-level16));
    max-width: 100%;
  }
}
```

- [ ] **Step 2: 验证并提交**

```bash
git add src/frontend/src/pages/agent/agent.vue
git commit -m "feat(agent): mobile token alignment"
```

---

## Task 13: dashboard（token 微调）

**Files:**
- Modify: `src/frontend/src/pages/dashboard/dashboard.vue`

**当前问题:** 仅有 1400px 断点，无 768px 移动端适配。

- [ ] **Step 1: 添加 768px 断点**

```scss
@media (max-width: 768px) {
  .dashboard-container {
    padding: var(--harmony-padding-level8);
    gap: var(--harmony-card-gap-mobile);
  }

  .dashboard-header {
    flex-direction: column;
    align-items: stretch;
    gap: var(--harmony-padding-level8);
  }

  .filters-container {
    flex-direction: column;
    gap: var(--harmony-padding-level4);

    .filter-item {
      min-width: 0;
      width: 100%;
    }
  }

  .kpi-container {
    grid-template-columns: repeat(2, 1fr);
    gap: var(--harmony-card-gap-mobile);
  }

  .kpi-card {
    padding: var(--harmony-padding-level8);
    border-radius: var(--harmony-corner-radius-level8);
  }

  .charts-container {
    grid-template-columns: 1fr;
    gap: var(--harmony-card-gap-mobile);
  }

  .chart-wrapper {
    min-width: 0;
    border-radius: var(--harmony-corner-radius-level8);
    padding: var(--harmony-padding-level8);
  }
}
```

- [ ] **Step 2: 验证并提交**

```bash
git add src/frontend/src/pages/dashboard/dashboard.vue
git commit -m "feat(dashboard): mobile card layout adaptation"
```

---

## Task 14: mars-chat（微调）

**Files:**
- Modify: `src/frontend/src/pages/mars/mars-chat.vue`

**当前问题:** 已有 @media，仅需 token 对齐。

- [ ] **Step 1: 更新移动端媒体查询中的硬编码值**

```scss
@media (max-width: 768px) {
  .mars-output-page {
    padding: 0;
  }

  .mars-output-container {
    padding: var(--harmony-padding-level8);
  }

  .mars-content {
    gap: var(--harmony-card-gap-mobile);
  }

  .mars-chat-message {
    gap: var(--harmony-padding-level6);

    .mars-ai-avatar {
      width: var(--harmony-control-height-36, 36px);
      height: var(--harmony-control-height-36, 36px);
    }
  }
}
```

- [ ] **Step 2: 验证并提交**

```bash
git add src/frontend/src/pages/mars/mars-chat.vue
git commit -m "feat(mars-chat): mobile token alignment"
```

---

## 验收检查清单

完成所有任务后，在浏览器中逐页检查：

- [ ] conversation: 侧边栏隐藏，会话列表全屏，点击可跳转
- [ ] interview: 侧边栏隐藏，列表全屏
- [ ] workspace: 侧边栏隐藏，列表全屏
- [ ] knowledge: 表头隐藏，行改为卡片，操作按钮可见
- [ ] model: 表头隐藏，行改为卡片
- [ ] mcp-server: 表格可横向滚动或改为卡片
- [ ] tool: 表头隐藏，行改为卡片
- [ ] agent-skill: 表头隐藏，行改为卡片，详情对话框全屏
- [ ] profile: 卡片全宽，头像居中
- [ ] configuration: 编辑器全宽
- [ ] homepage: 搜索框和卡片间距正确
- [ ] agent: 单列卡片，搜索框和按钮换行
- [ ] dashboard: KPI 2列，图表单列
- [ ] mars-chat: 间距统一

所有页面通用检查：
- [ ] 360px 宽度下无水平溢出
- [ ] 触摸元素最小 48px 高度
- [ ] 间距使用 hmos token
- [ ] 桌面端样式无回归

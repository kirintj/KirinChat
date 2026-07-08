# 统一布局组件系统

## Context

当前 `src/pages/` 下的页面布局和样式各不相同：
- 每个页面自定义 padding（16/20/24/32px）、border-radius、高度计算
- Desktop/Mobile 分支逻辑在每个页面重复编写
- 主从布局（conversation/workspace/interview）各自实现 sidebar+content，宽度样式不统一
- CRUD 页面的 page-header 样式各异

**目标**：设计通用布局组件，统一所有页面的结构和样式，同时保留每个页面的完整功能。

---

## 组件架构

### 新增文件

```
src/components/layout/
├── HPageLayout.vue          # 基础页面容器
├── HPageHeader.vue          # 统一页面头部
├── HMasterDetailLayout.vue  # 主从布局（列表+详情）
├── HCenteredLayout.vue      # 居中布局（首页/落地页）
└── index.ts                 # 统一导出

src/styles/
└── layout-tokens.scss       # 布局设计令牌（新增）
```

---

## 组件规格

### 1. HPageLayout - 页面容器

**Props:**
```typescript
{
  variant?: 'standard' | 'compact' | 'flush'  // 默认 'standard'
  scrollable?: boolean  // 默认 true
}
```

**职责:**
- 统一页面 padding（desktop: 24px, compact: 16px, mobile: 16px）
- 处理高度计算 `calc(100vh - 32px)`
- 提供滚动容器

**Slots:**
- `default` - 页面内容

---

### 2. HPageHeader - 页面头部

**Props:**
```typescript
{
  title: string
  description?: string
  showBack?: boolean
}
```

**Slots:**
- `actions` - 右侧操作按钮
- `extra` - 头部下方额外内容

**职责:**
- 统一头部样式：padding 20px 24px
- 背景色、圆角、阴影统一
- 移动端自动垂直堆叠

---

### 3. HMasterDetailLayout - 主从布局

**Props:**
```typescript
{
  sidebarWidth?: string  // 默认 '280px'
  sidebarCollapsible?: boolean
  mobileShowBack?: boolean
}
```

**Slots:**
- `sidebar` - 左侧列表面板
- `default` - 右侧详情面板
- `mobile-list` - 移动端列表视图（可选）
- `mobile-detail` - 移动端详情视图（可选）

**职责:**
- Desktop: flex 布局，sidebar + content
- Mobile: 显示列表或详情（非同时），带返回导航
- 统一 sidebar 样式（背景、边框、backdrop-filter）

---

### 4. HCenteredLayout - 居中布局

**Props:**
```typescript
{
  maxWidth?: string  // 默认 '560px'
  verticalAlign?: 'top' | 'center'  // 默认 'center'
}
```

**职责:**
- Flexbox 居中
- 最大宽度约束
- 响应式 padding

---

## 布局令牌 (layout-tokens.scss)

```scss
// 页面 padding
$page-padding-desktop: 24px;
$page-padding-compact: 16px;
$page-padding-mobile: 16px;

// 头部
$header-padding: 20px 24px;
$header-radius: var(--harmony-corner-radius-level8);

// Sidebar 宽度
$sidebar-width-default: 280px;
$sidebar-width-narrow: 240px;

// 高度
$page-height-calc: calc(100vh - 32px);
```

---

## 页面迁移计划

### 阶段 1: 基础设施
1. 创建 `layout-tokens.scss`
2. 创建 4 个布局组件
3. 创建 `components/layout/index.ts` 导出

### 阶段 2: CRUD 页面迁移（使用 HPageLayout + HPageHeader）
按优先级：
1. `agent/agent.vue` - 卡片网格
2. `knowledge/index.vue` - 表格
3. `model/index.vue` - 卡片网格
4. `tool/index.vue` - 卡片网格
5. `mcp-server/index.vue` - 列表
6. `agent-skill/index.vue` - 列表
7. `dashboard/index.vue` - 统计卡片
8. `configuration/index.vue` - 设置表单
9. `profile/index.vue` - 用户资料
10. `construct/index.vue` - 构建界面

**迁移模式:**
```vue
<!-- 之前 -->
<div class="agent-page">
  <div class="page-header">...</div>
  <div class="agent-list">...</div>
</div>

<!-- 之后 -->
<HPageLayout>
  <HPageHeader title="智能体管理" description="创建和管理您的智能体">
    <template #actions>
      <HButton @click="createAgent">创建</HButton>
    </template>
  </HPageHeader>
  <div class="agent-list">...</div>
</HPageLayout>
```

### 阶段 3: 主从页面迁移（使用 HMasterDetailLayout）
1. `conversation/conversation.vue`
2. `workspace/workspace.vue`
3. `interview/interview.vue`

**迁移模式:**
```vue
<HMasterDetailLayout sidebar-width="280px">
  <template #sidebar>
    <div class="create-section">...</div>
    <div class="list">...</div>
  </template>
  <template #default>
    <router-view />
  </template>
</HMasterDetailLayout>
```

### 阶段 4: 特殊页面
1. `homepage/homepage.vue` - 使用 HCenteredLayout
2. `mars/mars-chat.vue` - 保持现有布局（聊天界面特殊）

---

## 验证清单

每个页面迁移后检查：
- [ ] Desktop 布局与原设计一致
- [ ] Mobile 布局与原设计一致
- [ ] 所有功能正常（搜索、创建、编辑、删除）
- [ ] 响应式断点正确触发
- [ ] 无控制台错误
- [ ] Padding/间距符合设计令牌
- [ ] 动画/过渡效果正常

---

## 关键文件

| 文件 | 操作 |
|------|------|
| `src/components/layout/HPageLayout.vue` | 新建 |
| `src/components/layout/HPageHeader.vue` | 新建 |
| `src/components/layout/HMasterDetailLayout.vue` | 新建 |
| `src/components/layout/HCenteredLayout.vue` | 新建 |
| `src/components/layout/index.ts` | 新建 |
| `src/styles/layout-tokens.scss` | 新建 |
| `src/pages/agent/agent.vue` | 迁移 |
| `src/pages/knowledge/index.vue` | 迁移 |
| `src/pages/model/index.vue` | 迁移 |
| `src/pages/tool/index.vue` | 迁移 |
| `src/pages/mcp-server/index.vue` | 迁移 |
| `src/pages/agent-skill/index.vue` | 迁移 |
| `src/pages/dashboard/index.vue` | 迁移 |
| `src/pages/configuration/index.vue` | 迁移 |
| `src/pages/profile/index.vue` | 迁移 |
| `src/pages/construct/index.vue` | 迁移 |
| `src/pages/conversation/conversation.vue` | 迁移 |
| `src/pages/workspace/workspace.vue` | 迁移 |
| `src/pages/interview/interview.vue` | 迁移 |
| `src/pages/homepage/homepage.vue` | 迁移 |

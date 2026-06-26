# Interview Hub 页面设计规范

**日期**: 2026-06-26
**状态**: 已批准
**范围**: 在 KirinChat 面试模块中新增 Interview Hub 入口页

---

## 1. 背景与目标

当前面试模块的入口是技能选择页（defaultPage），用户需要先选技能才能开始面试。缺少一个统一的总览页面来查看面试状态、历史成绩和快速进入各功能。

**目标**：新增 Interview Hub 页面，作为面试模块的"仪表盘 + 快捷入口"。

---

## 2. 路由设计

### 新增路由

```
/interview/hub  →  hubPage.vue（面试中心）
```

嵌套在现有 `interview.vue` 布局内（侧边栏 + 内容区）。

### 路由树（完整）

```
/interview              → interview.vue（layout shell）
  /interview/hub        → hubPage.vue（新）
  /interview/chat       → chatPage.vue
  /interview/report     → reportPage.vue
  /interview/learning   → learningPage.vue
  /interview/resume     → resumePage.vue
  /interview/resume/:id → resumeDetailPage.vue
  /interview/jd         → jdParsePage.vue
```

### 侧边栏变更

在现有"开始新面试"按钮上方新增"面试中心"导航项：
- 图标：compass/dashboard 类型
- 路由：`/interview/hub`
- 高亮规则：当前路由为 `/interview/hub` 时高亮

---

## 3. 页面布局（方案 A：分区卡片式）

```
┌─────────────────────────────────────────────┐
│  面试中心                                    │
├─────────────────────────────────────────────┤
│  快捷入口                                    │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐       │
│  │文字   │ │语音   │ │上传   │ │解析   │       │
│  │面试   │ │面试   │ │简历   │ │JD    │       │
│  └──────┘ └──────┘ └──────┘ └──────┘       │
├─────────────────────────────────────────────┤
│  进行中的面试                        [查看全部]│
│  ┌────────┐ ┌────────┐ ┌────────┐          │
│  │session1│ │session2│ │session3│          │
│  └────────┘ └────────┘ └────────┘          │
│  （空状态：没有进行中的面试 + 开始新面试按钮）   │
├──────────────────────┬──────────────────────┤
│  最近面试             │  技能统计             │
│  - Java后端  85分     │  java-backend: 5次   │
│  - 算法      72分     │  algorithm:   3次    │
│  - 系统设计  68分     │  平均分: 75          │
└──────────────────────┴──────────────────────┘
```

---

## 4. 各区块详细设计

### 4.1 快捷入口卡片

4 张卡片横排排列：

| 入口 | 图标 | 标题 | 描述 | 跳转目标 |
|------|------|------|------|----------|
| 文字面试 | edit-pen | 文字面试 | 选择技能方向，开始 AI 面试 | `/interview`（defaultPage） |
| 语音面试 | microphone | 语音面试 | 实时语音对话，模拟真实面试 | `/voice-interview` |
| 上传简历 | document | 上传简历 | 上传简历获取 AI 分析报告 | `/interview/resume` |
| 解析 JD | search | 解析 JD | 粘贴职位描述，定制面试题目 | `/interview/jd` |

**交互**：hover 时 `translateY(-2px)` + box-shadow 加深，200ms ease 过渡。

### 4.2 进行中的面试

**数据来源**：`GET /interview/history` 返回结果过滤 `status === 'IN_PROGRESS' || status === 'CREATED'`

**卡片内容**：
- 技能名称（通过 `GET /skill/list` 获取 skill_id → 中文名映射，页面加载时一次性获取并缓存）
- 进度条：`current / total`（复用 `progress` 字段）
- 创建时间（相对时间格式，如"3小时前"）

注：当前 `InterviewSession` 不含 `difficulty` 和 `create_time` 字段，卡片暂不展示难度标签。后续可扩展后端 history 接口返回更多字段。

**空状态**：居中显示"没有进行中的面试"文字 + "开始新面试"按钮（跳转 `/interview`）

**交互**：卡片点击跳转 `/interview/chat?sessionId=xxx`

**右侧**："查看全部"文字链接 → `/interview`（侧边栏完整列表）

### 4.3 最近面试摘要

**数据来源**：`GET /interview/history` 返回结果中取最近 5 条 `status === 'EVALUATED'`，按完成时间倒序

**列表项内容**：
- 技能名称
- 总分（颜色规则：绿色 >= 80 分、黄色 >= 60 分、红色 < 60 分，基于 0-100 显示）
- 完成时间（相对时间格式）

**空状态**："暂无面试记录"

**交互**：点击跳转 `/interview/report?sessionId=xxx`

**右侧**："查看全部"文字链接 → `/interview` 侧边栏

### 4.4 技能统计概览

**数据来源**：前端对 `GET /interview/history` 中 `status === 'EVALUATED'` 的 session 按 `skill_id` 聚合

**聚合逻辑**：
```
for each skill_id:
  count = 该技能的 EVALUATED session 数量
  avg_score = mean(所有 session 的 total_score)
  max_score = max(所有 session 的 total_score)
```

**顶部总览**：
- 总面试次数
- 总体平均分

**技能列表**：每行一个技能，显示：
- 技能名称
- 面试次数
- 平均分（带颜色进度条）

**空状态**："暂无统计数据"

---

## 5. 数据流

页面加载时发起**两个并行 API 调用**：

```
GET /interview/history          GET /skill/list
       │                              │
       ▼                              ▼
  allSessions[]                skillMap { id → name }
       │
       ├── 过滤 status=IN_PROGRESS/CREATED → 进行中的面试
       ├── 取最近5条 status=EVALUATED      → 最近面试摘要
       └── 按 skill_id 聚合                → 技能统计概览
```

`skillMap` 用于将 `skill_id` 转为中文显示名称，各区块共享此映射。

**评分显示**：后端 `total_score` 为 0-10 制，前端展示时乘以 10 转为 0-100 制，与 reportPage 保持一致。

---

## 6. 文件变更

### 新增文件

| 文件路径 | 说明 |
|----------|------|
| `src/frontend/src/pages/interview/hubPage/hubPage.vue` | Hub 页面主组件 |
| `src/frontend/src/components/hub/QuickEntryCard.vue` | 快捷入口卡片组件 |
| `src/frontend/src/components/hub/ActiveSessionCard.vue` | 进行中面试卡片组件 |
| `src/frontend/src/components/hub/RecentInterviewItem.vue` | 最近面试列表项组件 |
| `src/frontend/src/components/hub/SkillStatCard.vue` | 技能统计卡片组件 |

### 修改文件

| 文件路径 | 变更内容 |
|----------|----------|
| `src/frontend/src/router/index.ts` | 新增 `/interview/hub` 子路由 |
| `src/frontend/src/pages/interview/interview.vue` | 侧边栏新增"面试中心"导航项 |

---

## 7. 响应式策略

| 断点 | 快捷入口 | 下方区域 |
|------|---------|---------|
| >= 1200px | 4 列 | 左右两栏 |
| 768-1199px | 2 列 | 堆叠 |
| < 768px | 1 列 | 堆叠 |

---

## 8. 已知限制

- `InterviewSession` 接口不含 `difficulty`、`create_time`、`completed_at` 字段，进行中的面试卡片无法显示难度标签和精确时间
- `GET /interview/history` 返回全量数据，session 数量大时可能有性能问题（当前阶段可接受）

---

## 9. 不包含的内容

- 不新增后端接口（纯前端页面）
- 不修改现有面试流程
- 不改变现有路由结构（仅新增子路由）

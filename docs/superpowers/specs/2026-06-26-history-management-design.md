# 面试历史管理设计规范

**日期**: 2026-06-26
**状态**: 已批准
**范围**: 独立面试历史列表页，支持筛选、搜索、排序、继续面试、删除

---

## 1. 背景与目标

当前面试历史仅在 hubPage 内联展示最近 5 条，后端 API 无筛选/排序/分页，响应缺少 skill_name 和 total_score。

**目标**：
- 新建独立历史页 `/interview/history`
- 后端 API 支持筛选（状态/技能/难度）、搜索、排序、分页
- 响应数据补充 skill_name 和 total_score
- 支持继续未完成面试和删除记录

---

## 2. 改动范围

### 新增文件

| 文件 | 说明 |
|------|------|
| `src/frontend/src/pages/interview/historyPage/historyPage.vue` | 面试历史列表页 |

### 修改文件

| 文件 | 变更 |
|------|------|
| `src/backend/kirinchat/schemas/interview.py` | InterviewHistoryResp 新增分页字段，InterviewSessionResp 新增 skill_name/total_score |
| `src/backend/kirinchat/api/v1/interview.py` | history 端点支持查询参数和分页 |
| `src/frontend/src/apis/interview.ts` | history API 支持查询参数 |
| `src/frontend/src/pages/interview/index.ts` | 导出新页面 |
| `src/frontend/src/router/index.ts` | 注册路由 |
| `src/frontend/src/pages/interview/hubPage/hubPage.vue` | "查看全部"跳转到历史页 |

---

## 3. 后端 API 设计

### 3.1 改造 GET /interview/history

新增查询参数：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `status` | str (Query) | 不限 | 按状态筛选: IN_PROGRESS/COMPLETED/EVALUATED |
| `skill_id` | str (Query) | 不限 | 按技能ID筛选 |
| `difficulty` | str (Query) | 不限 | 按难度筛选: EASY/MEDIUM/HARD |
| `keyword` | str (Query) | 不限 | 搜索关键词（匹配技能名称） |
| `sort_by` | str (Query) | `create_time` | 排序字段: create_time/total_score |
| `sort_order` | str (Query) | `desc` | 排序方向: asc/desc |
| `page` | int (Query) | 1 | 页码（从1开始） |
| `page_size` | int (Query) | 20 | 每页条数 |

### 3.2 响应结构

```python
class InterviewHistoryResp(BaseModel):
    """面试历史响应"""
    sessions: List[InterviewSessionResp] = Field(default=[], description="会话列表")
    total: int = Field(default=0, description="总记录数")
    page: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=20, description="每页条数")
```

每个 session 补充字段：
```python
class InterviewSessionResp(BaseModel):
    # 现有字段: id, skill_id, status, difficulty, progress
    skill_name: str = Field(default="", description="技能名称")
    total_score: Optional[float] = Field(None, description="总分（已评估时有值）")
```

### 3.3 数据获取

- `skill_name`: 通过 `SkillService.get_skill_by_id(session.skill_id)` 获取
- `total_score`: 通过 `EvaluationReportDao.select_report_by_session(session.id)` 获取，取 `report.total_score`
- 筛选和分页在 Python 层面完成（先获取全量数据，再过滤/排序/分页）

---

## 4. 前端设计

### 4.1 历史页布局

```
┌─────────────────────────────────────────────┐
│ ← 返回    面试历史                    [搜索框] │
├─────────────────────────────────────────────┤
│ [全部] [进行中] [已完成]   技能: [下拉]  难度: [下拉] │
├─────────────────────────────────────────────┤
│ 列表项:                                      │
│   左侧: 技能名 + 难度标签 + 创建时间            │
│   右侧: 分数 + 操作按钮                        │
│   进行中 → [继续] [删除]                       │
│   已完成 → [报告] [删除]                       │
├─────────────────────────────────────────────┤
│            < 1  2  3 ... 5 >                │
└─────────────────────────────────────────────┘
```

### 4.2 交互逻辑

- **状态筛选**：Tab 切换，点击重新请求 API
- **技能/难度筛选**：下拉选择，选择后重新请求
- **搜索**：输入框 debounce 500ms，触发重新请求
- **排序**：点击"时间"/"分数"表头切换排序
- **继续面试**：跳转到 `/interview/chat?sessionId=xxx`
- **查看报告**：跳转到 `/interview/report?sessionId=xxx`
- **删除**：弹窗确认后调用 deleteInterviewSessionAPI，刷新列表
- **分页**：点击页码切换，重新请求

### 4.3 hubPage 改动

"最近面试"区域的标题旁添加"查看全部"链接，点击跳转到 `/interview/history`。

---

## 5. 已知限制

- 筛选在 Python 层面完成（先全量查询再过滤），适合面试记录不太多的场景
- 搜索仅匹配技能名称，不匹配题目内容
- 分页在内存中进行，数据量极大时可能有性能问题

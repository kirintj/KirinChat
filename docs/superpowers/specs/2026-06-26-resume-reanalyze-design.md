# 简历重新分析设计规范

**日期**: 2026-06-26
**状态**: 已批准
**范围**: 上传已存在的简历时自动重新触发失败的分析任务

---

## 1. 背景与目标

当简历分析失败时，用户只能删除后重新上传，但文件 hash 去重机制会阻止同一文件的二次上传，导致用户无法重试。

**目标**：用户重新上传同一份简历文件时，如果之前的分析状态为 FAILED，自动重置状态并重新触发分析。

**范围**：仅修改后端 Service 层，无前端改动，无新增 API。

---

## 2. 改动范围

### 改动文件

| 文件 | 变更 |
|------|------|
| `src/backend/kirinchat/api/services/resume.py` | 修改 `upload_resume` 中 hash 命中后的分支逻辑 |

### 不变的部分

- 数据库模型（`ResumeTable`）：无字段变更
- DAO 层（`ResumeDao`）：复用现有 `update_status` 方法
- API 路由（`api/v1/resume.py`）：无变更
- 前端页面、store、API 函数：无变更
- Celery 任务（`resume_tasks.py`）：复用现有 `analyze_resume_task`

---

## 3. 设计方案

### 3.1 修改 upload_resume 的 hash 命中分支

当前逻辑（第 28-31 行）：
```python
existing = await ResumeDao.select_by_hash(file_hash)
if existing:
    return existing  # 直接返回，无论状态
```

改为：
```python
existing = await ResumeDao.select_by_hash(file_hash)
if existing:
    if existing.status in ("COMPLETED", "PENDING", "PROCESSING"):
        return existing
    # status == "FAILED" → 重置并重新分析
    await ResumeDao.update_status(existing.id, "PENDING")
    try:
        from kirinchat.common.async_task.resume_tasks import analyze_resume_task
        analyze_resume_task.delay(existing.id)
    except Exception:
        logger.warning("Celery 未启动，跳过异步分析任务")
    return existing
```

### 3.2 行为矩阵

| 已有记录状态 | 行为 |
|-------------|------|
| COMPLETED | 直接返回已有结果 |
| PENDING | 直接返回（正在排队） |
| PROCESSING | 直接返回（正在分析） |
| FAILED | 重置为 PENDING，重新派发 Celery 任务 |

### 3.3 关键设计决策

- **复用已有记录**：不创建新记录，保留 MinIO 文件路径、hash 等元数据
- **不重新上传 MinIO**：文件内容没变，无需重复存储
- **Celery 任务覆盖写入**：`update_analysis` 会覆盖 `analysis_result`、`score`、`raw_text`
- **前端自动感知**：前端已有轮询机制（resumePage 和 resumeDetailPage 都会 poll status），状态变为 PENDING 后自动进入轮询

---

## 4. 已知限制

- 不支持对 COMPLETED 状态的简历强制重新分析（需删除后上传不同文件）
- 重新分析期间，旧的分析结果会被覆盖（无版本历史）

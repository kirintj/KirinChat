# 简历重新分析 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 上传已存在的简历时，如果之前分析失败，自动重新触发分析

**Architecture:** 修改 `ResumeService.upload_resume` 中 hash 命中后的分支逻辑，对 FAILED 状态的记录重置为 PENDING 并重新派发 Celery 任务

**Tech Stack:** Python, FastAPI, Celery

---

### Task 1: 修改 upload_resume 的 hash 命中分支

**Files:**
- Modify: `src/backend/kirinchat/api/services/resume.py:28-31`

- [ ] **Step 1: 修改 hash 命中分支逻辑**

找到 `upload_resume` 方法中的这一段（第 28-31 行）：
```python
        file_hash = cls._compute_hash(file_data)
        existing = await ResumeDao.select_by_hash(file_hash)
        if existing:
            return existing
```

替换为：
```python
        file_hash = cls._compute_hash(file_data)
        existing = await ResumeDao.select_by_hash(file_hash)
        if existing:
            # 已有记录：已完成或处理中则直接返回，失败则重新分析
            if existing.status in ("COMPLETED", "PENDING", "PROCESSING"):
                return existing
            # status == "FAILED" → 重置状态并重新触发分析
            await ResumeDao.update_status(existing.id, "PENDING")
            try:
                from kirinchat.common.async_task.resume_tasks import analyze_resume_task
                analyze_resume_task.delay(existing.id)
            except Exception:
                logger.warning("Celery 未启动，跳过异步分析任务")
            return existing
```

- [ ] **Step 2: 验证构建**

Run: `cd src/backend && python -c "from kirinchat.api.services.resume import ResumeService; print('OK')"`
Expected: OK

- [ ] **Step 3: Commit**

```bash
git add src/backend/kirinchat/api/services/resume.py
git commit -m "feat(resume): auto-reanalyze on re-upload when previous analysis failed"
```

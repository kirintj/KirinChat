# 综合学习平台设计文档

**日期**: 2026-06-21  
**状态**: Phase 1 设计完成  
**参考项目**: [interview-guide](https://github.com/Snailclimb/interview-guide)

---

## 一、项目背景

### 1.1 目标

将 interview-guide 的面试/学习场景融入 KirinChat，打造一个**综合技术学习平台**，支持：
- 模拟面试（AI 面试官）
- 个性化学习（学习路径推荐）
- 知识可视化（知识图谱）
- 自定义知识库（文档导入 + RAG 问答）

### 1.2 目标用户

- **求职者**: 准备校招/社招的程序员
- **在职开发者**: 想提升技能的在职程序员
- **企业内训**: 企业内部技术培训

---

## 二、整体架构

```
┌─────────────────────────────────────────────────────────┐
│                    KirinChat 前端                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ 对话界面    │  │ 面试配置    │  │ 评估报告    │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    API 层 (FastAPI)                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ /completion │  │ /interview  │  │   /skill    │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    服务层                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ Interview   │  │ Skill       │  │ Evaluation  │     │
│  │ Agent       │  │ Service     │  │ Service     │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    数据层                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ MySQL       │  │ Redis       │  │ 文件系统    │     │
│  │ (会话/评估) │  │ (缓存/状态) │  │ (Skill定义) │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────────────────────┘
```

---

## 三、Phase 1: 面试 Agent + Skill 体系 + 基础评估

### 3.1 核心组件

#### 3.1.1 Interview Agent

**文件**: `core/agents/interview_agent.py`

```python
class InterviewAgent(BaseAgent):
    """
    面试 Agent，负责面试对话管理、出题、追问
    """
    agent_type: str = "interview"
    
    # 核心职责
    - 绑定 Skill（面试方向）
    - 管理面试状态（进行中/已完成）
    - 生成面试题目（基于 Skill + 历史去重）
    - 智能追问（0-2 个追问）
    - 收集用户答案
```

#### 3.1.2 Skill Service

**文件**: `services/skill_service.py`

```python
class SkillService:
    """
    管理面试方向和内容
    """
    # 核心职责
    - 加载 Skill 定义文件（SKILL.md + skill.meta.yml）
    - 解析分类（categories）和优先级
    - 分配算法：ALWAYS_ONE → CORE → NORMAL
    - 注入参考资料（_shared/ 或 skill专属）
```

#### 3.1.3 Evaluation Service

**文件**: `services/evaluation_service.py`

```python
class EvaluationService:
    """
    评估面试表现
    """
    # 核心职责
    - 分批评估（每批 8 题）
    - 结构化输出（JSON Schema）
    - 二次汇总（LLM 总结）
    - 降级兜底（失败时返回默认分数）
    - 生成雷达图数据
```

### 3.2 Skill 文件结构

```
skills/
├── java-backend/
│   ├── SKILL.md           # 面试官 persona + 提问策略
│   └── skill.meta.yml     # 分类、优先级、显示配置
├── python-backend/
│   ├── SKILL.md
│   └── skill.meta.yml
├── frontend/
│   ├── SKILL.md
│   └── skill.meta.yml
└── _shared/
    └── references/        # 共享参考资料
        ├── java.md
        ├── mysql.md
        └── redis.md
```

**SKILL.md 格式**:
```markdown
---
name: java-backend
description: Java 后端开发面试
---

你是一位资深的 Java 后端开发面试官...
（面试官 persona 和提问策略）
```

**skill.meta.yml 格式**:
```yaml
display:
  icon: "☕"
  gradient: "from-orange-500 to-red-600"
  colors:
    primary: "#f97316"
    secondary: "#dc2626"

categories:
  - key: java
    label: Java 核心
    priority: CORE
    ref: java.md
  - key: mysql
    label: MySQL
    priority: CORE
    ref: mysql.md
  - key: redis
    label: Redis
    priority: NORMAL
    ref: redis.md
  - key: spring
    label: Spring
    priority: CORE
    ref: spring.md
  - key: system-design
    label: 系统设计
    priority: NORMAL
  - key: project
    label: 项目经历
    priority: ALWAYS_ONE
```

### 3.3 数据模型

#### 3.3.1 InterviewSession（面试会话）

```python
class InterviewSession(Base):
    __tablename__ = "interview_session"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("user.id"))
    agent_id = Column(String(36), ForeignKey("agent.id"))
    skill_id = Column(String(50))  # 面试方向
    difficulty = Column(String(20))  # EASY/MEDIUM/HARD
    question_count = Column(Integer)  # 题目数量
    status = Column(String(20))  # CREATED/IN_PROGRESS/COMPLETED/EVALUATED
    created_at = Column(DateTime)
    completed_at = Column(DateTime)
```

#### 3.3.2 InterviewQuestion（面试题目）

```python
class InterviewQuestion(Base):
    __tablename__ = "interview_question"
    
    id = Column(String(36), primary_key=True)
    session_id = Column(String(36), ForeignKey("interview_session.id"))
    type = Column(String(20))  # MAIN/FOLLOW_UP
    category = Column(String(50))  # 知识点分类
    content = Column(Text)  # 题目内容
    user_answer = Column(Text)  # 用户答案
    score = Column(Float)  # 分数 (0-10)
    created_at = Column(DateTime)
```

#### 3.3.3 EvaluationReport（评估报告）

```python
class EvaluationReport(Base):
    __tablename__ = "evaluation_report"
    
    id = Column(String(36), primary_key=True)
    session_id = Column(String(36), ForeignKey("interview_session.id"))
    total_score = Column(Float)  # 总分
    category_scores = Column(JSON)  # 各分类分数
    summary = Column(Text)  # AI 总结
    strengths = Column(JSON)  # 优势列表
    improvements = Column(JSON)  # 改进建议列表
    created_at = Column(DateTime)
```

---

## 四、API 接口设计

### 4.1 面试相关 API

#### POST /api/v1/interview/start

开始新面试

**请求**:
```json
{
  "skill_id": "java-backend",
  "difficulty": "MEDIUM",
  "question_count": 10
}
```

**响应**:
```json
{
  "session_id": "uuid-xxx",
  "first_question": {
    "id": "uuid-xxx",
    "type": "MAIN",
    "category": "java",
    "content": "请解释 Java 中的多态性是什么？"
  }
}
```

#### POST /api/v1/interview/answer

提交答案

**请求**:
```json
{
  "session_id": "uuid-xxx",
  "question_id": "uuid-xxx",
  "answer": "多态性是指..."
}
```

**响应**:
```json
{
  "next_question": {
    "id": "uuid-xxx",
    "type": "FOLLOW_UP",
    "category": "java",
    "content": "能举一个实际项目中使用多态的例子吗？"
  },
  "is_completed": false
}
```

#### GET /api/v1/interview/session/{id}

获取面试状态

**响应**:
```json
{
  "session": {
    "id": "uuid-xxx",
    "skill_id": "java-backend",
    "status": "IN_PROGRESS",
    "progress": {
      "current": 5,
      "total": 10
    }
  },
  "questions": [...]
}
```

#### POST /api/v1/interview/complete

完成面试

**请求**:
```json
{
  "session_id": "uuid-xxx"
}
```

**响应**:
```json
{
  "evaluation_id": "uuid-xxx",
  "status": "evaluating"
}
```

#### GET /api/v1/interview/evaluation/{id}

获取评估报告

**响应**:
```json
{
  "total_score": 7.5,
  "category_scores": {
    "java": 8.0,
    "mysql": 7.0,
    "redis": 6.5,
    "spring": 8.5,
    "system-design": 7.0,
    "project": 8.0
  },
  "summary": "整体表现良好，Java 基础扎实...",
  "strengths": ["Java 基础扎实", "项目经验丰富"],
  "improvements": ["Redis 理解需要加强", "系统设计能力待提升"]
}
```

#### GET /api/v1/interview/history

获取面试历史

**响应**:
```json
{
  "sessions": [
    {
      "id": "uuid-xxx",
      "skill_id": "java-backend",
      "status": "EVALUATED",
      "total_score": 7.5,
      "created_at": "2026-06-21T10:00:00Z"
    }
  ]
}
```

### 4.2 Skill 相关 API

#### GET /api/v1/skill/list

获取所有 Skill

**响应**:
```json
{
  "skills": [
    {
      "id": "java-backend",
      "name": "Java 后端开发",
      "description": "Java 后端开发面试",
      "icon": "☕",
      "categories": [
        { "key": "java", "label": "Java 核心", "priority": "CORE" },
        { "key": "mysql", "label": "MySQL", "priority": "CORE" }
      ]
    }
  ]
}
```

#### GET /api/v1/skill/{id}

获取 Skill 详情

**响应**:
```json
{
  "skill": {
    "id": "java-backend",
    "name": "Java 后端开发",
    "description": "Java 后端开发面试",
    "persona": "你是一位资深的 Java 后端开发面试官..."
  },
  "categories": [...],
  "references": {
    "java.md": "# Java 核心知识点...",
    "mysql.md": "# MySQL 核心知识点..."
  }
}
```

---

## 五、数据流设计

### 5.1 开始面试

```
用户 → 前端 → POST /interview/start
                ↓
         InterviewService.start_interview()
                ↓
         SkillService.load_skill(skill_id)
                ├── 加载 SKILL.md (persona)
                ├── 加载 skill.meta.yml (categories)
                └── 加载 references (参考资料)
                ↓
         InterviewAgent.generate_first_question()
                ├── 查询历史题目（去重）
                ├── 构建 Prompt (persona + categories + 历史)
                └── 调用 LLM 生成题目
                ↓
         保存 InterviewQuestion 到数据库
                ↓
         返回 { session_id, first_question }
```

### 5.2 用户答题 + 追问

```
用户 → 前端 → POST /interview/answer
                ↓
         InterviewService.submit_answer()
                ├── 保存用户答案到 InterviewQuestion
                └── 判断是否需要追问
                    ↓
            InterviewAgent.generate_follow_up()
                    ├── 构建追问 Prompt (原题 + 答案)
                    └── 调用 LLM 生成追问
                    ↓
            返回 { next_question (追问), is_completed=false }
```

### 5.3 完成面试 + 评估

```
用户 → 前端 → POST /interview/complete
                ↓
         InterviewService.complete_interview()
                ├── 更新 session.status = COMPLETED
                └── 发送评估任务到队列（异步）
                    ↓
            EvaluationService.evaluate()
                    ├── 分批评估（每批 8 题）
                    │   ├── 构建评估 Prompt
                    │   └── 调用 LLM 评分
                    ├── 二次汇总（LLM 总结）
                    └── 生成雷达图数据
                    ↓
            保存 EvaluationReport 到数据库
                    ↓
            返回 { evaluation_id }
```

---

## 六、错误处理与降级策略

### 6.1 LLM 调用失败处理

```python
# 分层降级策略
try:
    # 主模型调用
    result = llm_provider.call(model="qwen-plus", prompt=prompt)
except LLMTimeoutError:
    # 降级到备用模型
    result = llm_provider.call(model="qwen-turbo", prompt=prompt)
except LLMRateLimitError:
    # 限流时返回缓存结果或默认值
    result = cache.get(cache_key) or default_response
except Exception:
    # 最终兜底
    result = {"error": "服务暂时不可用，请稍后重试"}
```

### 6.2 评估失败降级

```python
# 评估引擎四层可靠性
1. 分批评估 → 成功则继续
2. 批次失败 → 返回零分报告，继续其他批次
3. 二次汇总失败 → 降级到批次聚合结果
4. 全部失败 → 返回默认评估报告
```

### 6.3 会话状态恢复

```python
# Redis 缓存 + 数据库双层
session = redis.get(session_id)  # 优先从缓存读取
if not session:
    session = database.get(session_id)  # 缓存未命中时从数据库恢复
    redis.set(session_id, session, ttl=3600)  # 回填缓存
```

### 6.4 Prompt 注入防护

```python
# 借鉴 interview-guide 的设计
class PromptSanitizer:
    - 检测用户输入中的恶意指令
    - 添加数据边界指令（DATA_BOUNDARY_INSTRUCTION）
    - 添加反注入指令（ANTI_INJECTION_INSTRUCTION）
```

---

## 七、测试策略

### 7.1 单元测试

```python
# 测试核心组件
- SkillService: 加载、解析、分配算法
- InterviewAgent: 出题、追问、去重
- EvaluationService: 评分、汇总、降级
```

### 7.2 集成测试

```python
# 测试完整流程
- 开始面试 → 答题 → 追问 → 完成 → 评估
- 错误场景：LLM 超时、评估失败、会话丢失
```

### 7.3 端到端测试

```python
# 测试用户场景
- 选择 Skill → 配置难度 → 开始面试 → 完成 → 查看报告
```

---

## 八、后续阶段预览

### Phase 2: 知识库增强 + 学习路径 (2-3 周)

- 扩展知识库模块，支持学习资料导入
- 学习路径推荐算法
- 个性化学习建议

### Phase 3: 知识可视化 + 高级评估 (3-4 周)

- 知识图谱可视化
- 语音面试支持
- 高级评估报告（PDF 导出）

---

## 九、参考资源

- [interview-guide 项目](https://github.com/Snailclimb/interview-guide)
- [KirinChat 现有架构](../README.md)

---

**文档版本**: v1.0  
**最后更新**: 2026-06-21

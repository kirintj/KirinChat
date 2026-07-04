# KirinChat 语音面试功能设计方案

## 概述

将 InterviewGuide（Java/React）的语音面试功能迁移到 KirinChat（Python/FastAPI/Vue3），实现基于 DashScope Qwen3 ASR/TTS 的实时语音面试体验。

**来源项目**：`github.com/Snailclimb/interview-guide`（语音面试模块）
**目标项目**：KirinChat v2.5.0
**技术栈变化**：Java 21 / Spring Boot / React → Python 3.12 / FastAPI / Vue 3

## 关键决策

| 决策点 | 选择 | 理由 |
|---|---|---|
| ASR/TTS 服务 | DashScope Qwen3 | 与 InterviewGuide 一致，迁移最顺畅 |
| 架构方案 | 单 FastAPI WebSocket Handler + asyncio 并发 TTS | 语音面试低并发，无需额外基础设施 |
| 集成方式 | 独立模块，共用 Skill/评估 | 解耦但不重复 |
| 提交模式 | 手动提交 | 用户可编辑 ASR 识别结果后提交，更可控 |
| 面试阶段 | 完整四阶段（INTRO/TECH/PROJECT/HR） | 与 InterviewGuide 功能对齐 |
| 简历集成 | 关联已有简历 | Prompt 注入简历上下文，提升面试针对性 |

## 数据模型

### voice_interview_session（语音面试会话表）

| 字段 | 类型 | 说明 |
|---|---|---|
| id | UUID | 主键 |
| user_id | UUID | 关联用户（外键 → user 表） |
| skill_id | VARCHAR | 面试方向（复用现有 Skill，如 `python-backend`、`frontend`） |
| difficulty | VARCHAR | 难度：`easy` / `medium` / `hard` |
| resume_id | UUID | 关联简历（可选，外键 → resume 表） |
| planned_duration | INT | 计划时长（分钟） |
| current_phase | VARCHAR | 当前阶段：`INTRO` / `TECH` / `PROJECT` / `HR` / `COMPLETED` |
| status | VARCHAR | 状态：`IN_PROGRESS` / `PAUSED` / `COMPLETED` |
| evaluate_status | VARCHAR | 评估状态：`PENDING` / `PROCESSING` / `COMPLETED` / `FAILED` |
| evaluate_error | TEXT | 评估失败时的错误信息 |
| llm_provider | VARCHAR | 使用的 LLM 提供商 |
| phases_enabled | JSON | 开启的阶段 `{"intro":true,"tech":true,"project":true,"hr":true}` |
| start_time | DATETIME | 开始时间 |
| end_time | DATETIME | 结束时间 |
| paused_at | DATETIME | 暂停时间 |
| resumed_at | DATETIME | 恢复时间 |
| actual_duration | INT | 实际时长（秒） |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### voice_interview_message（对话消息表）

| 字段 | 类型 | 说明 |
|---|---|---|
| id | UUID | 主键 |
| session_id | UUID | 关联会话（外键 → voice_interview_session） |
| phase | VARCHAR | 所属阶段 |
| user_text | TEXT | 用户语音识别文本 |
| ai_text | TEXT | AI 生成文本 |
| sequence_num | INT | 消息序号 |
| timestamp | DATETIME | 时间戳 |
| created_at | DATETIME | 创建时间 |

### voice_interview_evaluation（评估结果表）

| 字段 | 类型 | 说明 |
|---|---|---|
| id | UUID | 主键 |
| session_id | UUID | 关联会话（外键 → voice_interview_session） |
| overall_score | FLOAT | 综合评分（0-100） |
| overall_feedback | TEXT | 综合评价 |
| category_scores | JSON | 分类评分（用于雷达图） |
| question_evaluations | JSON | 逐题评估详情 |
| strengths | JSON | 优势列表 |
| improvements | JSON | 改进建议列表 |
| reference_answers | JSON | 参考答案 |
| interviewer_role | VARCHAR | 面试官角色 |
| interview_date | DATE | 面试日期 |
| created_at | DATETIME | 创建时间 |

## 后端架构

### 模块结构

```
src/backend/kirinchat/voice_interview/
├── __init__.py
├── models.py              # SQLModel 表定义（上述 3 张表）
├── dao.py                 # 数据访问层（CRUD 操作）
├── schemas.py             # Pydantic 请求/响应模型
├── router.py              # REST API 路由注册
├── ws_handler.py          # WebSocket 核心处理器
├── services/
│   ├── __init__.py
│   ├── asr_service.py     # DashScope ASR 实时语音识别封装
│   ├── tts_service.py     # DashScope TTS 实时语音合成封装
│   ├── llm_service.py     # LLM 流式调用 + 语音输出优化
│   └── prompt_service.py  # 语音面试 Prompt 构建（含简历注入）
└── tasks.py               # Celery 异步评估任务
```

### REST API

端点前缀：`/api/v1/voice-interview`

| 方法 | 路径 | 说明 | 请求体/参数 |
|---|---|---|---|
| POST | `/sessions` | 创建语音面试 | `{skill_id, difficulty, resume_id?, phases, duration}` |
| GET | `/sessions` | 列表 | `?status=IN_PROGRESS` |
| GET | `/sessions/{id}` | 获取会话详情 | — |
| POST | `/sessions/{id}/end` | 结束面试 | — |
| PUT | `/sessions/{id}/pause` | 暂停面试 | — |
| PUT | `/sessions/{id}/resume` | 恢复面试 | — |
| GET | `/sessions/{id}/messages` | 获取对话历史 | — |
| GET | `/sessions/{id}/evaluation` | 获取评估结果 | — |
| POST | `/sessions/{id}/evaluation` | 触发评估 | — |

### WebSocket 端点

`ws://host:7860/api/v1/voice-interview/ws/{session_id}`

#### 消息协议（Client → Server）

| type | 格式 | 说明 |
|---|---|---|
| `audio` | `{"type":"audio","data":"<base64 PCM>","timestamp":...}` | 麦克风音频流 |
| `control` (submit) | `{"type":"control","action":"submit","data":{"text":"..."},"timestamp":...}` | 手动提交回答 |
| `control` (end) | `{"type":"control","action":"end_interview","timestamp":...}` | 结束面试 |
| `control` (phase) | `{"type":"control","action":"start_phase","phase":"TECH","timestamp":...}` | 阶段切换 |

#### 消息协议（Server → Client）

| type | 格式 | 说明 |
|---|---|---|
| `subtitle` | `{"type":"subtitle","text":"...","isFinal":bool}` | ASR 实时字幕 |
| `text` | `{"type":"text","content":"...","final":bool}` | LLM 流式文本 |
| `audio` | `{"type":"audio","data":"<base64 WAV>","text":"..."}` | 完整 AI 语音 |
| `audio_chunk` | `{"type":"audio_chunk","data":"<base64 WAV>","index":N,"isLast":bool}` | 分块 AI 语音 |
| `control` | `{"type":"control","action":"...","message":"...","timestamp":...}` | 状态信号（asr_ready/asr_reconnecting/audio_complete/welcome/pause_timeout_warning/pause_timeout） |
| `error` | `{"type":"error","message":"..."}` | 错误 |

### WebSocket 处理器核心流程

```
客户端连接
  → 创建 ConcurrentWebSocketSession（10s 超时，512KB 缓冲）
  → 启动 DashScope ASR 实时会话
  → 发送 asr_ready
  → 若无历史记录：生成开场问题 + 预缓存 TTS 音频 → 发送 welcome

用户说话
  → 客户端发送 audio 帧（200ms 一块，Base64 PCM 16kHz）
  → 转发到 DashScope ASR
  → ASR 返回 partial → 推送 subtitle(isFinal=false)
  → ASR 返回 final → 累积到 mergeBuffer → 推送 subtitle(isFinal=false)

用户点击提交
  → 客户端发送 control(submit)，携带识别文本
  → 触发 LLM 流式生成（asyncio 任务）
  → LLM token 推送到客户端 text 消息（节流：≥180ms 且 ≥12 字符）
  → 按句号分割 → 并发调用 TTS（asyncio.create_task，最多 3 路并发）
  → TTS 完成的句子按序发送 audio_chunk
  → 全部完成发送 audio_complete

结束面试
  → 客户端发送 control(end_interview)
  → 保存会话状态为 COMPLETED
  → 发布 Celery 评估任务
  → 客户端轮询 evaluation 接口等待结果
```

### 关键技术实现

**DashScope ASR（asr_service.py）**
- 使用 `dashscope` Python SDK 的 `OmniRealtimeConversation`
- 连接 `wss://dashscope.aliyuncs.com/api-ws/v1/realtime`
- 配置：PCM 16kHz，中文，server_vad，静默 2000ms
- 回调：on_partial（实时字幕）、on_final（完成片段）、on_ready（连接就绪）
- 每个面试会话独立 ASR 连接，存入 `dict[str, AsrSession]`

**DashScope TTS（tts_service.py）**
- 使用 `QwenTtsRealtime`
- 每次合成创建新 WebSocket 连接（短连接模式）
- 输出：PCM 24kHz，Mono，16-bit
- 超时：30 秒
- 返回原始 PCM 字节，处理器层添加 44 字节 WAV 头

**LLM 服务（llm_service.py）**
- 复用现有 LangChain `ChatOpenAI`（DashScope OpenAI 兼容端点）
- 流式输出 `stream=True`
- 语音优化：去除 Markdown，折叠空白，截断到 120 字（在句号处截断）

**Prompt 服务（prompt_service.py）**
- 从 `SkillService` 获取面试方向定义
- 注入语音约束：每次最多 1 个问题，2-4 句话，纯口语，无 Markdown
- 注入简历上下文（如有关联简历）
- 注入反 Prompt 注入指令
- 按阶段（INTRO/TECH/PROJECT/HR）切换系统提示词

**并发 TTS（ws_handler.py 核心）**
```python
async def synthesize_and_send_ordered(sentences: list[str], ws: WebSocket):
    queue = asyncio.Queue()
    async def tts_task(sentence, index):
        pcm = await tts_service.synthesize(sentence)
        await queue.put((index, pcm))
    # 并发启动所有 TTS 任务
    tasks = [asyncio.create_task(tts_task(s, i)) for i, s in enumerate(sentences)]
    # 按序发送
    sent = 0
    while sent < len(sentences):
        index, pcm = await queue.get()
        wav = pcm_to_wav(pcm, sample_rate=24000)
        await ws.send_json({"type": "audio_chunk", "data": base64(wav), "index": index, "isLast": index == len(sentences)-1})
        sent += 1
```

**回声抑制**
- 维护 `ai_speaking: bool` 状态
- AI 播报期间 + 播报结束后 800ms 冷却期内，丢弃所有客户端音频帧

**暂停超时**
- `asyncio.create_task` 启动 5 分钟倒计时
- 4:30 发送 `pause_timeout_warning`
- 5:00 自动暂停会话
- 每次收到用户音频/提交时重置计时器

### Celery 评估任务（tasks.py）

```python
@celery_app.task
def voice_interview_evaluation_task(session_id: str):
    # 1. 查询所有 messages，组装 QA 对
    # 2. 复用 evaluation_service 的评估逻辑
    # 3. 保存结果到 voice_interview_evaluation 表
    # 4. 更新 session.evaluate_status = "COMPLETED"
```

## 前端架构

### 模块结构

```
src/frontend/src/
├── pages/voice-interview/
│   ├── index.vue                  # 主页面容器
│   └── components/
│       ├── VoiceConfigDialog.vue  # 配置对话框
│       ├── AudioRecorder.vue      # 麦克风采集 + PCM + 音量可视化
│       ├── RealtimeSubtitle.vue   # 实时字幕面板
│       ├── VoiceControls.vue      # 控制栏
│       └── AudioPlayer.vue        # AI 语音播放
├── api/
│   └── voice-interview.ts         # REST + WebSocket 客户端
├── stores/
│   └── voice-interview.ts         # Pinia 状态管理
public/
└── audio-worklet/
    └── pcm-processor.js           # AudioWorklet 麦克风 PCM 处理器
```

### 路由

`/voice-interview` — 独立路由，从面试中心 `/interview/default` 添加"语音面试"入口卡片

### 核心组件

**AudioRecorder.vue**
- `getUserMedia`：启用 `echoCancellation`、`noiseSuppression`、`autoGainControl`，请求 16kHz 采样率
- `AudioContext(16kHz)` → `AudioWorkletNode(pcm-processor)` → Float32 重采样到 16kHz → Int16 → 200ms 一块（3200 samples）→ Base64 → WebSocket
- `AnalyserNode` → 音量柱状可视化
- AI 播报期间自动禁用（`isAiSpeaking` 联动）

**pcm-processor.js（AudioWorklet）**
- 接收 Float32 音频输入
- 线性插值重采样到 16kHz
- Float32 → Int16 PCM（clamp [-1,1]，scale to 16-bit）
- 累积 3200 样本（200ms）→ `postMessage(ArrayBuffer)`

**RealtimeSubtitle.vue**
- 左侧 AI 气泡（流式文字 + 脉冲光标动画）
- 右侧用户气泡（ASR 实时文字 + "识别中..." 指示）
- 状态栏：AI 播报中 / 正在识别 / 空闲
- 自动滚动

**AudioPlayer.vue（分块流式播放）**
- 收到 `audio_chunk` → 剥离 44 字节 WAV 头 → Int16 PCM → Float32 → `AudioBuffer(24kHz)` → 入队
- `AudioBufferSourceNode` 按序播放，播完自动触发下一个
- 回退：完整 `audio` 消息 → `<audio src="data:audio/wav;base64,...">`

**VoiceControls.vue**
- 录音开关按钮（麦克风图标，AI 播报时禁用）
- "提交回答" 按钮（手动触发 LLM）
- 暂停/恢复按钮
- 结束面试按钮
- 当前阶段显示 + 阶段切换下拉

**VoiceConfigDialog.vue**
- Skill 选择（复用现有 Skill 列表）
- 难度选择（easy/medium/hard）
- 阶段开关（INTRO/TECH/PROJECT/HR 四个 checkbox）
- 时长选择（15/30/45/60 分钟）
- 关联简历（下拉选择已有简历，可选）

### WebSocket 客户端（voice-interview.ts）

```typescript
class VoiceInterviewWebSocket {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnects = 3

  connect(sessionId: string): void
  sendAudio(base64Pcm: string): void
  sendControl(action: 'submit' | 'end_interview' | 'start_phase', data?: any): void
  disconnect(): void

  // 回调（由页面组件注入）
  onSubtitle: (text: string, isFinal: boolean) => void
  onTextResponse: (content: string, final: boolean) => void
  onAudioChunk: (base64Wav: string, index: number, isLast: boolean) => void
  onControl: (action: string, message?: string) => void
  onError: (message: string) => void
}
```

### Pinia Store（voice-interview.ts）

```typescript
interface VoiceInterviewState {
  sessionId: string | null
  status: 'idle' | 'connecting' | 'recording' | 'ai_speaking' | 'paused' | 'completed'
  currentPhase: string
  userText: string
  aiText: string
  messages: Array<{ role: 'user' | 'ai'; text: string; phase: string }>
  isAiSpeaking: boolean
  isRecording: boolean
  evaluateStatus: string
  evaluation: any | null
}
```

## 集成点

| 模块 | 集成方式 |
|---|---|
| **Skill 服务** | 复用 `SkillService`，通过 `skill_id` 获取面试方向定义和参考知识 |
| **评估引擎** | 复用 `EvaluationService`，将语音 QA 对转换为评估输入 |
| **简历模块** | 创建面试时可选传入 `resume_id`，Prompt 构建时查询简历内容注入上下文 |
| **Celery** | 评估任务使用现有 Celery Worker，新增 `voice_interview_evaluation_task` |
| **用户认证** | 复用现有 JWT 认证，WebSocket 连接通过 query param 传递 token |

## 配置项

在 `config.yaml` / `config-dev.yaml` 中新增：

```yaml
voice_interview:
  asr:
    model: "qwen3-asr-flash-realtime"
    sample_rate: 16000
    language: "zh"
    vad_silence_ms: 2000
  tts:
    model: "qwen3-tts-flash-realtime"
    voice: "Cherry"
    sample_rate: 24000
    speech_rate: 1.0
    volume: 60
    timeout_seconds: 8
  llm:
    max_chars: 120
    stream_interval_ms: 180
    min_chars_delta: 12
  session:
    pause_timeout_ms: 300000
    ai_speak_cooldown_ms: 800
    max_concurrent_tts: 3
```

API Key 复用现有 `DASHSCOPE_API_KEY` 配置。

## 音频格式规范

| 方向 | 格式 | 采样率 | 位深 | 传输编码 |
|---|---|---|---|---|
| 浏览器 → 服务器（麦克风） | PCM Int16 | 16kHz | 16-bit | Base64 JSON |
| 服务器 → DashScope ASR | PCM Int16 | 16kHz | 16-bit | Base64 SDK |
| DashScope TTS → 服务器 | PCM Int16 | 24kHz | 16-bit | Base64 SDK |
| 服务器 → 浏览器（完整） | WAV（PCM + 44字节头） | 24kHz | 16-bit | Base64 JSON |
| 服务器 → 浏览器（分块） | WAV（PCM + 44字节头） | 24kHz | 16-bit | Base64 JSON |

## 依赖新增

### Python（pyproject.toml）
- `dashscope` — DashScope Python SDK（ASR/TTS）

### 前端（package.json）
- 无新增依赖（AudioWorklet + WebSocket 均为浏览器原生 API）
- `@ricky0123/vad-web`（可选，VAD 语音活动检测，通过 CDN 引入）

## 前端入口

在现有面试中心页面 `/interview/default` 添加"语音面试"入口卡片，点击跳转到 `/voice-interview`，打开 `VoiceConfigDialog` 配置后开始。

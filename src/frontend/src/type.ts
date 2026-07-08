export  interface DialogCreateType {
    name: string,
    agent_id: string,
    agent_type: string,
}

// searchType
export  interface searchType {
  name:string,
}

export interface HistoryListType {
  agent: string
  dialogId: string
  name: string
  createTime: string
  logo:string
}

export interface MessageType {
  content: string
  type?: string // 新增：支持消息类型
}

export interface ChatMessage {
  personMessage: MessageType
  aiMessage: MessageType
  eventInfo?: Array<{
    event_type: string
    show: boolean
    status: string
    message: string
  }>
}

// 知识库类型定义
export interface KnowledgeListType {
    id: string
    name: string
    description: string | null
    user_id: string | null
    create_time: string
    update_time: string
    count: number // 文件数量
    file_size: string // 文件总大小（已格式化）
}

// 知识库文件类型定义
export interface KnowledgeFileType {
    id: string
    file_name: string
    knowledge_id: string
    status: string
    user_id: string
    oss_url: string
    file_size: number
    create_time: string
    update_time: string
}

// 新增智能体相关类型定义
export interface Agent {
  agent_id: string
  name: string
  description: string
  logo_url: string
  tool_ids: string[]
  llm_id: string
  mcp_ids: string[]
  system_prompt: string
  knowledge_ids: string[]
  agent_skill_ids?: string[]
  enable_memory: boolean
  created_time?: string
  updated_time?: string
  user_id?: string
  is_custom?: boolean
}

export interface AgentFormData {
  name: string
  description: string
  logo_url: string
  tool_ids: string[]
  llm_id: string
  mcp_ids: string[]
  system_prompt: string
  knowledge_ids: string[]
  agent_skill_ids: string[]
  enable_memory: boolean
}

export interface ToolOption {
  id: string
  name: string
  description: string
  logo_url?: string
  en_name?: string
  zh_name?: string
}

export interface LLMOption {
  id: string
  name: string
  model: string
  provider?: string
  api_key?: string
  base_url?: string
}

export interface MCPOption {
  id: string
  name: string
  description: string
  url?: string
  type?: string
  tools?: string[]
}

export interface KnowledgeOption {
  id: string
  name: string
  description: string | null
  user_id: string | null
  create_time?: string
  update_time?: string
  file_count?: number
}
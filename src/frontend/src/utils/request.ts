import axios, {
  type AxiosInstance,
  type AxiosRequestConfig,
  type AxiosResponse,
  type InternalAxiosRequestConfig,
} from 'axios'

// ===================== 类型定义 =====================

/** 自定义请求配置（扩展重试字段） */
interface CustomAxiosRequestConfig extends InternalAxiosRequestConfig {
  _retryCount?: number       // 已重试次数
  _noRetry?: boolean         // 标记该请求禁止重试（如文件上传）
  _showError?: boolean       // 是否由全局拦截器弹出错误提示，默认 true
  _timeout?: number          // 单次请求超时覆盖（ms）
}

/** 后端统一响应体结构 */
interface ApiResponse<T = unknown> {
  status_code: number
  data: T
  message?: string
}

// ===================== 常量 =====================

const GLOBAL_TIMEOUT = 30_000       // 全局超时 30 秒（覆盖绝大多数正常请求）
const MAX_RETRY = 2                 // 最大重试次数（不含首次，共发 3 次）
const RETRY_DELAY = 1500           // 重试间隔 1.5 秒
const RETRY_STATUS_CODES = [408, 502, 503, 504]  // 可重试的 HTTP 状态码

// ===================== 工具函数 =====================

/** 延迟 */
const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

/** 判断是否为超时错误 */
const isTimeoutError = (error: unknown): boolean =>
  axios.isAxiosError(error) && error.code === 'ECONNABORTED'

/** 判断是否为网络错误（无 response） */
const isNetworkError = (error: unknown): boolean =>
  axios.isAxiosError(error) && !error.response && !error.code?.startsWith('ECONNABORTED')

/** 判断是否可重试 */
const isRetryable = (error: unknown): boolean => {
  if (axios.isAxiosError(error)) {
    // 超时 → 可重试
    if (isTimeoutError(error)) return true
    // 网络断开 → 可重试
    if (isNetworkError(error)) return true
    // 特定 HTTP 状态码 → 可重试
    if (error.response && RETRY_STATUS_CODES.includes(error.response.status)) return true
  }
  return false
}

/** 获取友好的中文错误信息 */
const getFriendlyMessage = (error: unknown): string => {
  if (!axios.isAxiosError(error)) return '发生未知错误'

  if (isTimeoutError(error)) {
    return '请求超时，服务器响应过慢，请稍后重试'
  }
  if (isNetworkError(error)) {
    return '网络连接失败，请检查网络或后端服务是否启动'
  }

  const status = error.response?.status
  const statusMap: Record<number, string> = {
    400: '请求参数错误',
    401: '登录已过期，请重新登录',
    403: '没有访问权限',
    404: '请求的资源不存在',
    409: '数据冲突，请刷新后重试',
    422: '提交的数据格式不正确',
    429: '请求过于频繁，请稍后重试',
    500: '服务器内部错误',
    502: '服务暂时不可用，请稍后重试',
    503: '服务维护中，请稍后重试',
    504: '服务响应超时，请稍后重试',
  }
  return statusMap[status ?? 0] ?? `请求失败 (${status})`
}

// ===================== 创建实例 =====================

const request: AxiosInstance = axios.create({
  baseURL: '',
  timeout: GLOBAL_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
})

// ===================== 请求拦截器 =====================

// 用于取消重复请求：key = method:url，value = AbortController
const pendingControllers = new Map<string, AbortController>()

request.interceptors.request.use(
  (config: CustomAxiosRequestConfig) => {
    // ---------- Token ----------
    const token = localStorage.getItem('token')
    if (token) {
      config.headers = config.headers || {}
      config.headers['Authorization'] = `Bearer ${token}`
    }

    // ---------- 单请求超时覆盖 ----------
    if (config._timeout) {
      config.timeout = config._timeout
    }

    // ---------- 取消重复请求（仅 GET） ----------
    if (config.method?.toUpperCase() === 'GET') {
      const key = `${config.method}:${config.url}`

      // 取消上一个未完成的同 key 请求
      const prevController = pendingControllers.get(key)
      if (prevController) {
        prevController.abort()
      }

      const controller = new AbortController()
      pendingControllers.set(key, controller)
      config.signal = controller.signal
    }

    return config
  },
  (error) => Promise.reject(error),
)

// ===================== 响应拦截器 =====================

request.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    // 请求成功，移除 pending 记录
    const key = `${response.config.method}:${response.config.url}`
    pendingControllers.delete(key)
    return response
  },
  async (error: unknown) => {
    // 被取消的请求不处理（去重导致的）
    if (axios.isAxiosError(error) && error.code === 'ERR_CANCELED') {
      return Promise.reject(error)
    }

    const config = error?.config as CustomAxiosRequestConfig | undefined
    const url = config?.url ?? 'unknown'
    const show = config?._showError !== false // 默认展示错误

    // ---------- 超时重试逻辑 ----------
    const retryCount = config?._retryCount ?? 0

    if (isRetryable(error) && retryCount < MAX_RETRY && !config?._noRetry) {
      console.warn(
        `[request] 第${retryCount + 1}次重试: ${config?.method?.toUpperCase()} ${url}`,
      )
      if (config) {
        config._retryCount = retryCount + 1
      }
      await sleep(RETRY_DELAY * (retryCount + 1)) // 递增延迟
      return request(config!) // 重新发起请求
    }

    // ---------- 超时专属日志 ----------
    if (isTimeoutError(error)) {
      console.error(`[request] 超时: ${url} (${GLOBAL_TIMEOUT / 1000}s)`)
    } else if (isNetworkError(error)) {
      console.error(`[request] 网络错误: ${url}`)
    } else {
      console.error(
        `[request] 错误: ${error?.response?.status} ${url}`,
        error?.response?.data ?? error?.message,
      )
    }

    // ---------- 401 清 token 跳登录 ----------
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
      window.location.href = '/login'
      return Promise.reject(error)
    }

    // ---------- 注入友好错误信息供页面读取 ----------
    if (axios.isAxiosError(error)) {
      // 挂到 error 上，页面 catch 里可以直接 e.friendlyMessage 使用
      error.friendlyMessage = getFriendlyMessage(error)
    }

    return Promise.reject(error)
  },
)

// ===================== 扩展 AxiosError 类型 =====================

declare module 'axios' {
  interface AxiosError {
    /** 拦截器注入的中文友好提示 */
    friendlyMessage?: string
  }
}

export { request }
export type { ApiResponse, CustomAxiosRequestConfig }

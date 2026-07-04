// axios 的封装处理
import axios, { AxiosError, AxiosResponse } from 'axios'

// ---------------------------------------------------------------------------
// 认证工具：供 SSE / 原生 fetch 等非 axios 场景复用
// ---------------------------------------------------------------------------

/** 获取当前存储的 JWT token（若无则返回空字符串） */
export function getStoredToken(): string {
  return localStorage.getItem('token') || ''
}

/**
 * 返回带 Authorization 头的标准 headers 对象。
 * 适用于 fetchEventSource / 原生 fetch 等不走 axios 拦截器的场景。
 */
export function getAuthHeaders(contentType = 'application/json'): Record<string, string> {
  const headers: Record<string, string> = {}
  if (contentType) {
    headers['Content-Type'] = contentType
  }
  const token = getStoredToken()
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  return headers
}

// ---------------------------------------------------------------------------
// Axios 实例
// ---------------------------------------------------------------------------

const request = axios.create({
  baseURL: '',
  timeout: 10000  // 全局超时10秒，对于耗时操作单独设置
})

// 请求拦截器：统一添加认证
request.interceptors.request.use(
  (config) => {
    const token = getStoredToken()
    if (token) {
      config.headers = config.headers || {}
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  (error: AxiosError) => {
    console.error('请求拦截器错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器：统一错误处理
request.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError) => {
    console.error('响应错误:', error.response?.status, error.config?.url)
    console.error('错误详情:', error.response?.data || error.message)

    if (error.response?.status === 401) {
      // token 过期，清除本地存储并跳转到登录页
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export { request }

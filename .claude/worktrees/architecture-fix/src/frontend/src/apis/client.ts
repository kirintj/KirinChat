/**
 * 统一 HTTP 客户端入口
 *
 * 对外导出经过拦截器封装的 axios 实例和辅助函数，
 * 让所有 apis/*.ts 模块从这里获取公共依赖。
 */
export { request, getAuthHeaders, getStoredToken } from '../utils/request'

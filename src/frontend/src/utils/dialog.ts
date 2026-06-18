import { HMessageBox } from '@/components/ui'

/**
 * 显示删除确认对话框
 * @param message 确认消息
 * @param title 对话框标题，默认为"删除确认"
 */
export const showDeleteConfirm = (message: string, title: string = '删除确认') => {
  return HMessageBox.confirm(message, title, {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    type: 'warning',
  })
}

/**
 * 显示通用确认对话框
 * @param message 确认消息
 * @param title 对话框标题
 * @param options 额外选项
 */
export const showConfirm = (
  message: string,
  title: string = '确认',
  options: any = {}
) => {
  return HMessageBox.confirm(message, title, {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
    ...options,
  })
}

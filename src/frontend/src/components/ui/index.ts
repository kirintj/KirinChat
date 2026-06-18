import type { App } from 'vue'

// 组件导出
export { HButton } from './HButton'
export { HDialog } from './HDialog'
export { HForm, HFormItem } from './HForm'
export { HIcon } from './HIcon'
export { HInput } from './HInput'
export { HMessage } from './HMessage'
export { HMessageBox } from './HMessageBox'
export { HSelect, HOption } from './HSelect'
export { HTooltip } from './HTooltip'
export { HDropdown, HDropdownItem } from './HDropdown'
export { HTag } from './HTag'
export { HTable } from './HTable'
export { HUpload } from './HUpload'
export { HDrawer } from './HDrawer'
export { HTabs, HTabPane } from './HTabs'

// Vue 插件：全局注册
export default {
  install(app: App) {
    // 目前 HMessage 是 API 式调用，无需全局注册组件
    // 后续组件添加后在此注册
  }
}

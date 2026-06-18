import type { App } from 'vue'
import { vHLoading } from './HLoading'

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
export { HScrollbar } from './HScrollbar'
export { HAvatar } from './HAvatar'
export { HSkeleton } from './HSkeleton'

// 指令导出
export { vHLoading } from './HLoading'

// Vue 插件：全局注册
export default {
  install(app: App) {
    app.directive('h-loading', vHLoading)
  }
}

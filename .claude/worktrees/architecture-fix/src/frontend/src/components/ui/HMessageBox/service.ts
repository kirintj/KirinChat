import { createVNode, render } from 'vue'
import HMessageBox from './HMessageBox.vue'

interface MessageBoxOptions {
  title?: string
  message: string
  confirmButtonText?: string
  cancelButtonText?: string
  type?: 'warning' | 'info' | 'success' | 'error'
  showCancel?: boolean
}

function createMessageBox(options: MessageBoxOptions): Promise<void> {
  return new Promise((resolve, reject) => {
    const container = document.createElement('div')
    document.body.appendChild(container)

    const vnode = createVNode(HMessageBox, {
      ...options,
      onConfirm: () => {
        cleanup()
        resolve()
      },
      onCancel: () => {
        cleanup()
        reject(new Error('cancel'))
      },
      onClose: cleanup,
    })

    function cleanup() {
      render(null, container)
      container.remove()
    }

    render(vnode, container)
  })
}

export const HMessageBox = {
  confirm: (message: string, title?: string, options?: Partial<MessageBoxOptions>) =>
    createMessageBox({ message, title, showCancel: true, ...options }),
  alert: (message: string, title?: string, options?: Partial<MessageBoxOptions>) =>
    createMessageBox({ message, title, showCancel: false, ...options }),
}

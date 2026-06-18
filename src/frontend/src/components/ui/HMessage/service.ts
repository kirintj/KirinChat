import { createVNode, render } from 'vue'
import HMessage from './HMessage.vue'

type MessageType = 'success' | 'error' | 'warning' | 'info'

function showMessage(type: MessageType, message: string, duration = 3000) {
  const container = document.createElement('div')
  document.body.appendChild(container)

  const vnode = createVNode(HMessage, {
    type,
    message,
    duration,
    onClose: () => {
      render(null, container)
      container.remove()
    },
  })

  render(vnode, container)
}

export const HMessage = {
  success: (msg: string, duration?: number) => showMessage('success', msg, duration),
  error:   (msg: string, duration?: number) => showMessage('error', msg, duration),
  warning: (msg: string, duration?: number) => showMessage('warning', msg, duration),
  info:    (msg: string, duration?: number) => showMessage('info', msg, duration),
}

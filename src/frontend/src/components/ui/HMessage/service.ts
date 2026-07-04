type MessageType = 'success' | 'error' | 'warning' | 'info'

const icons: Record<MessageType, string> = {
  success: '✓',
  error: '✕',
  warning: '!',
  info: 'i',
}

const bgColors: Record<MessageType, string> = {
  success: 'var(--color-success)',
  error: 'var(--color-error)',
  warning: 'var(--color-warning)',
  info: 'var(--color-primary)',
}

function showMessage(type: MessageType, message: string, duration = 3000) {
  const el = document.createElement('div')
  el.className = 'h-message'
  el.innerHTML = `
    <span class="h-message__icon" style="background:${bgColors[type]}${type === 'warning' ? ';color:var(--color-text-primary)' : ''}">${icons[type]}</span>
    <span class="h-message__text">${message}</span>
  `

  // 基础样式
  Object.assign(el.style, {
    position: 'fixed',
    top: '20px',
    left: '50%',
    transform: 'translateX(-50%) translateY(-20px)',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    padding: '10px 20px',
    borderRadius: 'var(--harmony-corner-radius-level10)',
    background: 'var(--color-bg-secondary)',
    backdropFilter: 'blur(20px) saturate(1.2)',
    border: '1px solid var(--color-border)',
    boxShadow: 'var(--shadow-lg)',
    fontSize: 'var(--font-size-base)',
    color: 'var(--color-text-primary)',
    opacity: '0',
    transition: 'all var(--duration-normal) var(--easing)',
    zIndex: 'var(--z-toast)',
    cursor: 'pointer',
  })

  const iconEl = el.querySelector('.h-message__icon') as HTMLElement
  if (iconEl) {
    Object.assign(iconEl.style, {
      width: '20px',
      height: '20px',
      borderRadius: '50%',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontSize: '12px',
      fontWeight: '700',
      color: 'var(--color-on-primary)',
      flexShrink: '0',
    })
  }

  document.body.appendChild(el)

  // 入场动画
  requestAnimationFrame(() => {
    el.style.opacity = '1'
    el.style.transform = 'translateX(-50%) translateY(0)'
  })

  const close = () => {
    el.style.opacity = '0'
    el.style.transform = 'translateX(-50%) translateY(-20px)'
    setTimeout(() => el.remove(), 200)
  }

  el.addEventListener('click', close)

  if (duration > 0) {
    setTimeout(close, duration)
  }
}

export const HMessage = {
  success: (msg: string, duration?: number) => showMessage('success', msg, duration),
  error:   (msg: string, duration?: number) => showMessage('error', msg, duration),
  warning: (msg: string, duration?: number) => showMessage('warning', msg, duration),
  info:    (msg: string, duration?: number) => showMessage('info', msg, duration),
}

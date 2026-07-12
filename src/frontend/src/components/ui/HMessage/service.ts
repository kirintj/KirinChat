type MessageType = 'success' | 'error' | 'warning' | 'info'

interface MessageOptions {
  duration?: number
  dedup?: boolean
}

const icons: Record<MessageType, string> = {
  success: '✓',
  error: '✕',
  warning: '!',
  info: 'i',
}

const iconBg: Record<MessageType, string> = {
  success: 'var(--harmony-confirm)',
  error: 'var(--harmony-warning)',
  warning: 'var(--harmony-alert)',
  info: 'var(--harmony-brand)',
}

const iconColor: Record<MessageType, string> = {
  success: 'var(--harmony-font-on-primary)',
  error: 'var(--harmony-font-on-primary)',
  warning: 'var(--harmony-font-primary)',
  info: 'var(--harmony-font-on-primary)',
}

const progressBg: Record<MessageType, string> = {
  success: 'var(--harmony-confirm)',
  error: 'var(--harmony-warning)',
  warning: 'var(--harmony-alert)',
  info: 'var(--harmony-brand)',
}

const MAX_VISIBLE = 5
const DEDUP_WINDOW = 3000
const recentMessages = new Map<string, number>()

// Respect the user's motion preference. matchMedia may be absent in some test
// environments (happy-dom); optional chaining + nullish coalescing falls back
// to "motion enabled" so existing behavior is unchanged.
const prefersReducedMotion =
  typeof window !== 'undefined' &&
  typeof window.matchMedia === 'function' &&
  window.matchMedia('(prefers-reduced-motion: reduce)').matches

let container: HTMLElement | null = null

function getContainer(): HTMLElement {
  if (container && document.body.contains(container)) return container
  container = document.createElement('div')
  container.className = 'h-message-container'
  Object.assign(container.style, {
    position: 'fixed',
    top: '20px',
    left: '50%',
    transform: 'translateX(-50%)',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: 'var(--harmony-padding-level2)',
    zIndex: 'var(--z-toast)',
    pointerEvents: 'none',
  } as CSSStyleDeclaration)
  document.body.appendChild(container)
  return container
}

function removeMessage(el: HTMLElement) {
  if (el.dataset.removing === 'true') return
  el.dataset.removing = 'true'
  if (prefersReducedMotion) {
    el.remove()
    return
  }
  el.style.opacity = '0'
  el.style.transform = 'translateY(-20px)'
  setTimeout(() => el.remove(), 200)
}

function showMessage(type: MessageType, message: string, options: MessageOptions = {}) {
  const duration = options.duration ?? 3000
  const dedup = options.dedup ?? true

  if (dedup) {
    const dedupKey = `${type}:${message}`
    const now = Date.now()
    const lastShown = recentMessages.get(dedupKey)
    if (lastShown && now - lastShown < DEDUP_WINDOW) return
    recentMessages.set(dedupKey, now)
    if (recentMessages.size > 50) {
      for (const [key, ts] of recentMessages) {
        if (now - ts > DEDUP_WINDOW) recentMessages.delete(key)
      }
    }
  }

  const cont = getContainer()

  const active = Array.from(cont.children).filter(
    (c): c is HTMLElement => c instanceof HTMLElement && c.dataset.removing !== 'true'
  )
  while (active.length >= MAX_VISIBLE) {
    const first = active.shift()
    if (first) removeMessage(first)
    else break
  }

  const el = document.createElement('div')
  el.className = 'h-message'
  el.setAttribute('role', 'alert')
  el.innerHTML = `
    <span class="h-message__icon"></span>
    <span class="h-message__text"></span>
    <span class="h-message__close" role="button" aria-label="关闭">✕</span>
    <span class="h-message__progress"></span>
  `

  const iconEl = el.querySelector('.h-message__icon') as HTMLElement
  const textEl = el.querySelector('.h-message__text') as HTMLElement
  const closeBtn = el.querySelector('.h-message__close') as HTMLElement
  const progressEl = el.querySelector('.h-message__progress') as HTMLElement

  iconEl.textContent = icons[type]
  textEl.textContent = message

  const transitionStr = prefersReducedMotion
    ? 'none'
    : 'opacity var(--harmony-duration-normal) var(--harmony-motion-standard), transform var(--harmony-duration-normal) var(--harmony-motion-standard)'

  Object.assign(el.style, {
    position: 'relative',
    display: 'flex',
    alignItems: 'center',
    gap: 'var(--harmony-padding-level2)',
    padding: 'var(--harmony-padding-level5) var(--harmony-padding-level10)',
    borderRadius: 'var(--harmony-corner-radius-level10)',
    background: 'var(--harmony-comp-background-primary)',
    backdropFilter: 'blur(20px) saturate(1.2)',
    boxShadow: 'var(--harmony-shadow-lg), inset 0 0 0 1px var(--harmony-comp-divider)',
    fontSize: 'var(--harmony-font-size-body-m)',
    color: 'var(--harmony-font-primary)',
    opacity: prefersReducedMotion ? '1' : '0',
    transform: prefersReducedMotion ? 'translateY(0)' : 'translateY(-20px)',
    transition: transitionStr,
    pointerEvents: 'auto',
    maxWidth: '480px',
    overflow: 'hidden',
  } as CSSStyleDeclaration)

  Object.assign(iconEl.style, {
    width: '20px',
    height: '20px',
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: 'var(--harmony-font-size-body-s)',
    fontWeight: '700',
    background: iconBg[type],
    color: iconColor[type],
    flexShrink: '0',
  } as CSSStyleDeclaration)

  Object.assign(textEl.style, {
    lineHeight: '1.5',
  } as CSSStyleDeclaration)

  Object.assign(closeBtn.style, {
    width: '20px',
    height: '20px',
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '12px',
    color: 'var(--harmony-font-tertiary)',
    cursor: 'pointer',
    flexShrink: '0',
    opacity: '0',
    transition: 'opacity var(--harmony-duration-fast) var(--harmony-motion-standard), color var(--harmony-duration-fast) var(--harmony-motion-standard)',
  } as CSSStyleDeclaration)

  // Progress bar: a thin accent-colored strip at the bottom that depletes
  // over `duration`. Skipped when persistent (duration <= 0) or when the user
  // prefers reduced motion.
  Object.assign(progressEl.style, {
    position: 'absolute',
    left: '0',
    bottom: '0',
    height: '2px',
    width: '100%',
    transform: 'scaleX(1)',
    transformOrigin: 'left',
    background: progressBg[type],
    opacity: duration > 0 ? '1' : '0',
  } as CSSStyleDeclaration)

  cont.appendChild(el)

  const close = () => removeMessage(el)

  closeBtn.addEventListener('click', (e) => {
    e.stopPropagation()
    close()
  })
  el.addEventListener('mouseenter', () => { closeBtn.style.opacity = '1' })
  el.addEventListener('mouseleave', () => { closeBtn.style.opacity = '0' })

  if (prefersReducedMotion) {
    // Already at final visible state; no enter animation.
  } else {
    requestAnimationFrame(() => {
      el.style.opacity = '1'
      el.style.transform = 'translateY(0)'
      if (duration > 0) {
        progressEl.style.transition = `transform ${duration}ms linear`
        progressEl.style.transform = 'scaleX(0)'
      }
    })
  }

  if (duration > 0) {
    setTimeout(close, duration)
  }
}

export const HMessage = {
  success: (msg: string, duration?: number, options?: Omit<MessageOptions, 'duration'>) =>
    showMessage('success', msg, { ...options, duration }),
  error: (msg: string, duration?: number, options?: Omit<MessageOptions, 'duration'>) =>
    showMessage('error', msg, { ...options, duration }),
  warning: (msg: string, duration?: number, options?: Omit<MessageOptions, 'duration'>) =>
    showMessage('warning', msg, { ...options, duration }),
  info: (msg: string, duration?: number, options?: Omit<MessageOptions, 'duration'>) =>
    showMessage('info', msg, { ...options, duration }),
}

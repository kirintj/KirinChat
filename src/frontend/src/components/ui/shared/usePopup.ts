import { watch, onBeforeUnmount, type Ref } from 'vue'

export interface UsePopupOptions {
  closeOnEsc?: boolean
  lockScroll?: boolean
  trapFocus?: boolean
  restoreFocus?: boolean
  initialFocus?: () => HTMLElement | null | undefined
  onClose: () => void
}

const FOCUSABLE_SELECTOR = [
  'a[href]',
  'button:not([disabled])',
  'textarea:not([disabled])',
  'input:not([disabled])',
  'select:not([disabled])',
  '[tabindex]:not([tabindex="-1"])',
].join(',')

let scrollLockCount = 0
let savedBodyOverflow = ''

const popupStack: Array<() => void> = []

function lockBodyScroll() {
  if (scrollLockCount === 0) {
    savedBodyOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
  }
  scrollLockCount++
}

function unlockBodyScroll() {
  if (scrollLockCount <= 0) return
  scrollLockCount--
  if (scrollLockCount === 0) {
    document.body.style.overflow = savedBodyOverflow
    savedBodyOverflow = ''
  }
}

function getFocusable(container: HTMLElement): HTMLElement[] {
  return Array.from(container.querySelectorAll<HTMLElement>(FOCUSABLE_SELECTOR))
    .filter(el => {
      if (el.hasAttribute('hidden')) return false
      if ('disabled' in el && (el as HTMLButtonElement).disabled) return false
      const style = window.getComputedStyle(el)
      if (style.display === 'none' || style.visibility === 'hidden') return false
      return true
    })
}

export function usePopup(
  isActive: Ref<boolean>,
  popupRef: Ref<HTMLElement | null>,
  options: UsePopupOptions
) {
  const {
    closeOnEsc = true,
    lockScroll = true,
    trapFocus = true,
    restoreFocus = true,
    initialFocus,
    onClose,
  } = options

  let savedFocus: HTMLElement | null = null
  let escHandler: ((e: KeyboardEvent) => void) | null = null
  let trapHandler: ((e: KeyboardEvent) => void) | null = null
  let isOpen = false

  function requestClose() {
    onClose()
  }

  function open() {
    if (isOpen) return
    isOpen = true
    savedFocus = (document.activeElement as HTMLElement) ?? null

    if (lockScroll) lockBodyScroll()

    if (closeOnEsc) {
      escHandler = (e: KeyboardEvent) => {
        if (e.key !== 'Escape') return
        if (popupStack[popupStack.length - 1] === requestClose) {
          e.stopPropagation()
          requestClose()
        }
      }
      popupStack.push(requestClose)
      document.addEventListener('keydown', escHandler, true)
    }

    if (trapFocus) {
      trapHandler = (e: KeyboardEvent) => {
        if (e.key !== 'Tab') return
        const container = popupRef.value
        if (!container) return
        const focusable = getFocusable(container)
        if (focusable.length === 0) {
          e.preventDefault()
          container.focus()
          return
        }
        const first = focusable[0]
        const last = focusable[focusable.length - 1]
        const active = document.activeElement
        if (e.shiftKey) {
          if (active === first || !container.contains(active)) {
            e.preventDefault()
            last.focus()
          }
        } else if (active === last || !container.contains(active)) {
          e.preventDefault()
          first.focus()
        }
      }
      document.addEventListener('keydown', trapHandler, true)
    }

    requestAnimationFrame(() => {
      const container = popupRef.value
      if (!container) return
      const focusable = getFocusable(container)
      const target = initialFocus?.() ?? focusable[0] ?? container
      target.focus()
    })
  }

  function removeListeners() {
    if (escHandler) {
      document.removeEventListener('keydown', escHandler, true)
      const idx = popupStack.indexOf(requestClose)
      if (idx >= 0) popupStack.splice(idx, 1)
      escHandler = null
    }
    if (trapHandler) {
      document.removeEventListener('keydown', trapHandler, true)
      trapHandler = null
    }
  }

  function close() {
    if (!isOpen) return
    isOpen = false
    removeListeners()
    if (lockScroll) unlockBodyScroll()
    if (restoreFocus && savedFocus && typeof savedFocus.focus === 'function') {
      const el = savedFocus
      requestAnimationFrame(() => el.focus())
    }
    savedFocus = null
  }

  if (isActive.value) open()
  const stopWatch = watch(
    isActive,
    (active) => {
      if (active) open()
      else close()
    },
    { flush: 'sync' }
  )

  onBeforeUnmount(() => {
    stopWatch()
    if (!isOpen) return
    isOpen = false
    removeListeners()
    if (lockScroll) unlockBodyScroll()
  })

  return { requestClose }
}

export const __test__ = {
  lockBodyScroll,
  unlockBodyScroll,
  popupStack,
  getFocusable,
  resetState: () => {
    scrollLockCount = 0
    savedBodyOverflow = ''
    popupStack.length = 0
  },
}

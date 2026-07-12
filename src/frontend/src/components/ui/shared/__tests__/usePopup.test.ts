import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { createApp, ref, h, defineComponent, nextTick, type App } from 'vue'
import { usePopup, __test__ as usePopupTest } from '../usePopup'

describe('usePopup', () => {
  const apps: App[] = []
  let container: HTMLElement
  let originalRAF: typeof requestAnimationFrame

  beforeEach(() => {
    container = document.createElement('div')
    document.body.appendChild(container)
    originalRAF = globalThis.requestAnimationFrame
    // Defer rAF to microtask so it flushes within `await nextTick()` without
    // running synchronously during unmount (which causes recursive updates).
    globalThis.requestAnimationFrame = ((cb: FrameRequestCallback) => {
      Promise.resolve().then(() => cb(0))
      return 0
    }) as typeof requestAnimationFrame
    // Reset module-level state to prevent leakage between tests
    usePopupTest.resetState()
  })

  afterEach(() => {
    apps.forEach(a => a.unmount())
    apps.length = 0
    document.body.innerHTML = ''
    document.body.style.overflow = ''
    globalThis.requestAnimationFrame = originalRAF
    vi.restoreAllMocks()
    usePopupTest.resetState()
  })

  function mountPopup(options: {
    closeOnEsc?: boolean
    lockScroll?: boolean
    trapFocus?: boolean
    restoreFocus?: boolean
    onClose?: () => void
    focusable?: boolean
  } = {}) {
    const isActive = ref(false)
    const popupRef = ref<HTMLElement | null>(null)
    const onClose = options.onClose ?? vi.fn()
    const mountContainer = document.createElement('div')
    document.body.appendChild(mountContainer)

    const Comp = defineComponent({
      setup() {
        usePopup(isActive, popupRef, {
          closeOnEsc: options.closeOnEsc ?? true,
          lockScroll: options.lockScroll ?? true,
          trapFocus: options.trapFocus ?? true,
          restoreFocus: options.restoreFocus ?? true,
          onClose,
        })
        return () =>
          h('div', { ref: popupRef, tabindex: '-1' }, [
            options.focusable ? h('button', { id: 'btn1' }, 'A') : null,
            options.focusable ? h('button', { id: 'btn2' }, 'B') : null,
          ])
      },
    })
    const testApp = createApp(Comp)
    testApp.mount(mountContainer)
    apps.push(testApp)
    return { isActive, onClose }
  }

  function dispatchKey(key: string, shiftKey = false) {
    const ev = new KeyboardEvent('keydown', { key, shiftKey, bubbles: true, cancelable: true })
    document.dispatchEvent(ev)
    return ev
  }

  // -------------------------------------------------------------------
  // Cleanup on unmount — must run FIRST.
  // Previous tests leave stale keydown listeners on `document` (added via
  // document.addEventListener in usePopup's open()). These are removed by
  // onBeforeUnmount during afterEach, but happy-dom + Vue interaction causes
  // stack overflow when app.unmount() is called while isActive is true AND
  // stale listeners exist. Running this test first avoids the issue.
  // -------------------------------------------------------------------
  it('releases scroll lock when unmounted while active', async () => {
    const { isActive } = mountPopup()
    isActive.value = true
    await nextTick()
    expect(document.body.style.overflow).toBe('hidden')
    apps.forEach(a => a.unmount())
    apps.length = 0
    expect(document.body.style.overflow).toBe('')
  })

  // -------------------------------------------------------------------
  // Scroll lock
  // -------------------------------------------------------------------
  it('locks body scroll when activated and restores when deactivated', async () => {
    document.body.style.overflow = 'auto'
    const { isActive } = mountPopup()
    expect(document.body.style.overflow).toBe('auto')
    isActive.value = true
    await nextTick()
    expect(document.body.style.overflow).toBe('hidden')
    isActive.value = false
    await nextTick()
    expect(document.body.style.overflow).toBe('auto')
  })

  it('uses reference counting so closing one of two popups keeps scroll locked', async () => {
    const a = mountPopup()
    const b = mountPopup({ onClose: vi.fn() })
    a.isActive.value = true
    await nextTick()
    b.isActive.value = true
    await nextTick()
    expect(document.body.style.overflow).toBe('hidden')
    a.isActive.value = false
    await nextTick()
    expect(document.body.style.overflow).toBe('hidden')
    b.isActive.value = false
    await nextTick()
    expect(document.body.style.overflow).toBe('')
  })

  // -------------------------------------------------------------------
  // ESC close
  // -------------------------------------------------------------------
  it('calls onClose when Escape is pressed while active', async () => {
    const onClose = vi.fn()
    const { isActive } = mountPopup({ onClose })
    isActive.value = true
    await nextTick()
    dispatchKey('Escape')
    expect(onClose).toHaveBeenCalledTimes(1)
  })

  it('does not call onClose when Escape pressed and popup inactive', async () => {
    const onClose = vi.fn()
    mountPopup({ onClose })
    await nextTick()
    dispatchKey('Escape')
    expect(onClose).not.toHaveBeenCalled()
  })

  it('only the topmost popup closes on Escape', async () => {
    const onCloseA = vi.fn()
    const onCloseB = vi.fn()
    const a = mountPopup({ onClose: onCloseA })
    const b = mountPopup({ onClose: onCloseB })
    a.isActive.value = true
    await nextTick()
    b.isActive.value = true
    await nextTick()
    dispatchKey('Escape')
    expect(onCloseB).toHaveBeenCalledTimes(1)
    expect(onCloseA).not.toHaveBeenCalled()
  })

  it('does not close on Escape when closeOnEsc is false', async () => {
    const onClose = vi.fn()
    const { isActive } = mountPopup({ closeOnEsc: false, onClose })
    isActive.value = true
    await nextTick()
    dispatchKey('Escape')
    expect(onClose).not.toHaveBeenCalled()
  })

  // -------------------------------------------------------------------
  // Focus trap
  // -------------------------------------------------------------------
  it('traps Tab focus within the popup (cycles from last to first)', async () => {
    const { isActive } = mountPopup({ focusable: true })
    isActive.value = true
    await nextTick()
    const btn2 = document.getElementById('btn2') as HTMLButtonElement
    btn2.focus()
    expect(document.activeElement).toBe(btn2)
    dispatchKey('Tab')
    expect(document.activeElement?.id).toBe('btn1')
  })

  it('traps Shift+Tab focus (cycles from first to last)', async () => {
    const { isActive } = mountPopup({ focusable: true })
    isActive.value = true
    await nextTick()
    const btn1 = document.getElementById('btn1') as HTMLButtonElement
    btn1.focus()
    dispatchKey('Tab', true)
    expect(document.activeElement?.id).toBe('btn2')
  })

  // -------------------------------------------------------------------
  // Focus restore
  // -------------------------------------------------------------------
  it('restores focus to the previously focused element after close', async () => {
    const trigger = document.createElement('button')
    trigger.id = 'trigger'
    container.appendChild(trigger)
    const focusSpy = vi.spyOn(trigger, 'focus')
    const activeElSpy = vi.spyOn(document, 'activeElement', 'get').mockReturnValue(trigger)

    const { isActive } = mountPopup()
    isActive.value = true
    await nextTick()
    isActive.value = false
    await nextTick()
    expect(focusSpy).toHaveBeenCalled()
    activeElSpy.mockRestore()
  })
})

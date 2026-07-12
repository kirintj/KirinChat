import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { createApp, ref, h, defineComponent, nextTick, type App, type Ref } from 'vue'
import HDrawer from '../HDrawer.vue'

/**
 * HDrawer switches between a desktop side panel and a mobile bottom sheet via
 * useBreakpoint().isMobile. happy-dom does not implement a real matchMedia
 * engine, so we stub window.matchMedia with a viewport-width model that
 * evaluates the media-query strings produced by useBreakpoint.
 */

function setupMatchMedia(viewportWidth: number) {
  const listeners = new Map<string, Set<(e: { matches: boolean }) => void>>()
  ;(window as unknown as { matchMedia: unknown }).matchMedia = vi.fn((query: string) => {
    const maxMatch = query.match(/max-width:\s*(\d+)px/)
    const minMatch = query.match(/min-width:\s*(\d+)px/)
    let matches = true
    if (maxMatch) matches = matches && viewportWidth <= parseInt(maxMatch[1], 10)
    if (minMatch) matches = matches && viewportWidth >= parseInt(minMatch[1], 10)
    return {
      matches,
      media: query,
      onchange: null,
      addEventListener: (_type: string, cb: (e: { matches: boolean }) => void) => {
        if (!listeners.has(query)) listeners.set(query, new Set())
        listeners.get(query)!.add(cb)
      },
      removeEventListener: (_type: string, cb: (e: { matches: boolean }) => void) => {
        listeners.get(query)?.delete(cb)
      },
      addListener: vi.fn(),
      removeListener: vi.fn(),
      dispatchEvent: vi.fn(),
    }
  })
}

describe('HDrawer', () => {
  const apps: App[] = []
  const visibleRefs: Ref<boolean>[] = []
  let container: HTMLElement
  let originalMatchMedia: unknown

  beforeEach(() => {
    container = document.createElement('div')
    document.body.appendChild(container)
    originalMatchMedia = (window as unknown as { matchMedia: unknown }).matchMedia
  })

  afterEach(async () => {
    for (const v of visibleRefs) v.value = false
    await nextTick()
    apps.forEach(a => a.unmount())
    apps.length = 0
    visibleRefs.length = 0
    document.body.innerHTML = ''
    document.body.style.overflow = ''
    ;(window as unknown as { matchMedia: unknown }).matchMedia = originalMatchMedia
    vi.restoreAllMocks()
  })

  function mountDrawer(props: Record<string, unknown> = {}) {
    const visible = ref(false)
    visibleRefs.push(visible)
    const mountContainer = document.createElement('div')
    document.body.appendChild(mountContainer)

    const Wrapper = defineComponent({
      setup() {
        return () =>
          h(HDrawer, {
            modelValue: visible.value,
            'onUpdate:modelValue': (v: boolean) => {
              visible.value = v
            },
            title: props.title ?? 'Test Drawer',
            ...props,
          }, {
            default: () => h('p', 'drawer body'),
          })
      },
    })
    const testApp = createApp(Wrapper)
    testApp.component('Icon', {
      props: ['icon', 'width', 'height'],
      render: () => h('span', { 'data-testid': 'icon-stub' }),
    })
    testApp.mount(mountContainer)
    apps.push(testApp)
    return { visible }
  }

  // -------------------------------------------------------------------
  // Desktop side panel
  // -------------------------------------------------------------------
  it('renders desktop side panel anchored right by default', async () => {
    setupMatchMedia(1280) // desktop
    const { visible } = mountDrawer({ size: '360px' })
    visible.value = true
    await nextTick()
    const panel = document.querySelector('.h-drawer')
    expect(panel).not.toBeNull()
    expect(panel!.classList.contains('h-drawer--right')).toBe(true)
    expect((panel as HTMLElement).style.width).toBe('360px')
    // bottom sheet must NOT be present in desktop mode
    expect(document.querySelector('.h-drawer-sheet')).toBeNull()
  })

  it('renders desktop side panel anchored left when direction=left', async () => {
    setupMatchMedia(1280)
    const { visible } = mountDrawer({ direction: 'left' })
    visible.value = true
    await nextTick()
    const panel = document.querySelector('.h-drawer')!
    expect(panel.classList.contains('h-drawer--left')).toBe(true)
    expect(panel.classList.contains('is-left')).toBe(true)
  })

  // -------------------------------------------------------------------
  // Mobile bottom sheet
  // -------------------------------------------------------------------
  it('renders mobile bottom sheet instead of side panel', async () => {
    setupMatchMedia(500) // mobile
    const { visible } = mountDrawer()
    visible.value = true
    await nextTick()
    expect(document.querySelector('.h-drawer')).toBeNull()
    const sheet = document.querySelector('.h-drawer-sheet')
    expect(sheet).not.toBeNull()
    expect(sheet!.classList.contains('h-drawer-overlay--sheet')).toBe(false) // overlay has that class, not sheet
  })

  it('mobile bottom sheet includes a drag handle', async () => {
    setupMatchMedia(500)
    const { visible } = mountDrawer()
    visible.value = true
    await nextTick()
    const handle = document.querySelector('.h-drawer-sheet__handle')
    expect(handle).not.toBeNull()
    const bar = handle!.querySelector('.h-drawer-sheet__handle-bar')
    expect(bar).not.toBeNull()
  })

  it('mobile bottom sheet applies maxHeight from mobileMaxHeight prop', async () => {
    setupMatchMedia(500)
    const { visible } = mountDrawer({ mobileMaxHeight: 60 })
    visible.value = true
    await nextTick()
    const sheet = document.querySelector('.h-drawer-sheet') as HTMLElement
    expect(sheet.style.maxHeight).toBe('60vh')
  })

  // -------------------------------------------------------------------
  // Drag-to-close
  // -------------------------------------------------------------------
  it('closes when drag handle pulled down beyond threshold', async () => {
    setupMatchMedia(500)
    const { visible } = mountDrawer()
    visible.value = true
    await nextTick()
    expect(visible.value).toBe(true)

    const handle = document.querySelector('.h-drawer-sheet__handle') as HTMLElement

    handle.dispatchEvent(new TouchEvent('touchstart', {
      touches: [{ clientY: 100 } as Touch],
      cancelable: true,
      bubbles: true,
    }))
    handle.dispatchEvent(new TouchEvent('touchmove', {
      touches: [{ clientY: 200 } as Touch], // delta = 100 > 80
      cancelable: true,
      bubbles: true,
    }))
    handle.dispatchEvent(new Event('touchend'))

    expect(visible.value).toBe(false)
  })

  it('does not close when drag delta is below threshold', async () => {
    setupMatchMedia(500)
    const { visible } = mountDrawer()
    visible.value = true
    await nextTick()
    expect(visible.value).toBe(true)

    const handle = document.querySelector('.h-drawer-sheet__handle') as HTMLElement

    handle.dispatchEvent(new TouchEvent('touchstart', {
      touches: [{ clientY: 100 } as Touch],
      cancelable: true,
      bubbles: true,
    }))
    handle.dispatchEvent(new TouchEvent('touchmove', {
      touches: [{ clientY: 130 } as Touch], // delta = 30 < 80
      cancelable: true,
      bubbles: true,
    }))
    handle.dispatchEvent(new Event('touchend'))

    expect(visible.value).toBe(true)
  })
})

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { createApp, ref, h, defineComponent, nextTick, type App, type Ref } from 'vue'
import HDialog from '../HDialog.vue'

describe('HDialog', () => {
  const apps: App[] = []
  const visibleRefs: Ref<boolean>[] = []
  let container: HTMLElement

  beforeEach(() => {
    container = document.createElement('div')
    document.body.appendChild(container)
  })

  afterEach(async () => {
    // Close any open dialogs before unmounting to avoid the usePopup
    // unmount-while-active stack overflow (stale document keydown listeners
    // + happy-dom interaction).
    for (const v of visibleRefs) v.value = false
    await nextTick()
    apps.forEach(a => a.unmount())
    apps.length = 0
    visibleRefs.length = 0
    document.body.innerHTML = ''
    document.body.style.overflow = ''
    vi.restoreAllMocks()
  })

  function mountDialog(props: Record<string, unknown> = {}) {
    const visible = ref(false)
    visibleRefs.push(visible)
    const mountContainer = document.createElement('div')
    document.body.appendChild(mountContainer)

    const Wrapper = defineComponent({
      setup() {
        return () =>
          h(HDialog, {
            modelValue: visible.value,
            'onUpdate:modelValue': (v: boolean) => {
              visible.value = v
            },
            title: props.title ?? 'Test Dialog',
            ...props,
          }, {
            default: () => h('p', 'body content'),
            footer: () => h('button', 'OK'),
          })
      },
    })
    const testApp = createApp(Wrapper)
    // Stub the globally-registered Icon component (HDialog renders <Icon>).
    testApp.component('Icon', {
      props: ['icon', 'width', 'height'],
      render: () => h('span', { 'data-testid': 'icon-stub' }),
    })
    testApp.mount(mountContainer)
    apps.push(testApp)
    return { visible }
  }

  function getDialog(): HTMLElement | null {
    return document.querySelector('.h-dialog')
  }

  // -------------------------------------------------------------------
  // Size variants
  // -------------------------------------------------------------------
  it('applies sm size (400px maxWidth) by default size=sm', async () => {
    const { visible } = mountDialog({ size: 'sm' })
    visible.value = true
    await nextTick()
    const dialog = getDialog()!
    expect(dialog.classList.contains('h-dialog--sm')).toBe(true)
    expect((dialog as HTMLElement).style.maxWidth).toBe('400px')
  })

  it('applies md size (500px maxWidth) by default', async () => {
    const { visible } = mountDialog()
    visible.value = true
    await nextTick()
    const dialog = getDialog()!
    expect(dialog.classList.contains('h-dialog--md')).toBe(true)
    expect((dialog as HTMLElement).style.maxWidth).toBe('500px')
  })

  it('applies lg size (720px maxWidth)', async () => {
    const { visible } = mountDialog({ size: 'lg' })
    visible.value = true
    await nextTick()
    const dialog = getDialog()!
    expect(dialog.classList.contains('h-dialog--lg')).toBe(true)
    expect((dialog as HTMLElement).style.maxWidth).toBe('720px')
  })

  // -------------------------------------------------------------------
  // Fullscreen
  // -------------------------------------------------------------------
  it('applies fullscreen class and no maxWidth style', async () => {
    const { visible } = mountDialog({ size: 'fullscreen' })
    visible.value = true
    await nextTick()
    const dialog = getDialog()!
    expect(dialog.classList.contains('h-dialog--fullscreen')).toBe(true)
    // fullscreen uses no inline maxWidth
    expect((dialog as HTMLElement).style.maxWidth).toBe('')
  })

  // -------------------------------------------------------------------
  // width prop precedence
  // -------------------------------------------------------------------
  it('width prop takes precedence over size', async () => {
    const { visible } = mountDialog({ size: 'lg', width: '480px' })
    visible.value = true
    await nextTick()
    const dialog = getDialog()!
    expect((dialog as HTMLElement).style.maxWidth).toBe('480px')
  })

  // -------------------------------------------------------------------
  // Footer alignment
  // -------------------------------------------------------------------
  it('aligns footer to the right by default', async () => {
    const { visible } = mountDialog()
    visible.value = true
    await nextTick()
    const footer = document.querySelector('.h-dialog__footer')!
    expect(footer.classList.contains('h-dialog__footer--right')).toBe(true)
  })

  it('aligns footer to center when alignFooter=center', async () => {
    const { visible } = mountDialog({ alignFooter: 'center' })
    visible.value = true
    await nextTick()
    const footer = document.querySelector('.h-dialog__footer')!
    expect(footer.classList.contains('h-dialog__footer--center')).toBe(true)
  })

  // -------------------------------------------------------------------
  // Body scroll constraint (structural — happy-dom does not compute
  // scoped CSS, so we verify the body element renders slotted content;
  // the overflow-y/max-height constraint lives in the scoped <style>).
  // -------------------------------------------------------------------
  it('renders slotted body content', async () => {
    const { visible } = mountDialog()
    visible.value = true
    await nextTick()
    const body = document.querySelector('.h-dialog__body') as HTMLElement
    expect(body).not.toBeNull()
    expect(body.textContent).toContain('body content')
  })
})

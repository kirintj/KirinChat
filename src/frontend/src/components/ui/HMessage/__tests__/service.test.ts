import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'

describe('HMessage service', () => {
  let HMessage: typeof import('../service').HMessage

  beforeEach(async () => {
    vi.resetModules()
    vi.useFakeTimers()
    HMessage = (await import('../service')).HMessage
  })

  afterEach(() => {
    vi.useRealTimers()
    document.body.innerHTML = ''
  })

  function activeMessageCount(): number {
    const cont = document.querySelector('.h-message-container')
    if (!cont) return 0
    return Array.from(cont.children).filter(
      c => (c as HTMLElement).dataset.removing !== 'true'
    ).length
  }

  it('creates a message element with role=alert and the message text', () => {
    HMessage.success('hello')
    const cont = document.querySelector('.h-message-container')
    expect(cont).toBeTruthy()
    const msg = cont!.querySelector('.h-message')
    expect(msg).toBeTruthy()
    expect(msg!.getAttribute('role')).toBe('alert')
    const text = cont!.querySelector('.h-message__text') as HTMLElement
    expect(text.textContent).toBe('hello')
  })

  it('uses a single shared container across calls', () => {
    HMessage.info('one')
    HMessage.info('two')
    const containers = document.querySelectorAll('.h-message-container')
    expect(containers.length).toBe(1)
  })

  it('deduplicates same type+message within the window', () => {
    HMessage.success('dup')
    HMessage.success('dup')
    expect(activeMessageCount()).toBe(1)
  })

  it('allows duplicate after dedup window elapses', () => {
    HMessage.success('dup2', 0)
    vi.advanceTimersByTime(3001)
    HMessage.success('dup2', 0)
    expect(activeMessageCount()).toBe(2)
  })

  it('does not dedup across different types or messages', () => {
    HMessage.success('a')
    HMessage.error('a')
    HMessage.success('b')
    expect(activeMessageCount()).toBe(3)
  })

  it('respects dedup:false option', () => {
    HMessage.success('nodup', undefined, { dedup: false })
    HMessage.success('nodup', undefined, { dedup: false })
    expect(activeMessageCount()).toBe(2)
  })

  it('limits visible messages to 5, removing the oldest', () => {
    for (let i = 0; i < 6; i++) HMessage.success(`msg${i}`)
    expect(activeMessageCount()).toBe(5)
    const cont = document.querySelector('.h-message-container')!
    const first = cont.firstElementChild as HTMLElement
    // The oldest ('msg0') should be marked for removal
    expect(first.dataset.removing).toBe('true')
  })

  it('auto-closes after the given duration', () => {
    HMessage.success('temp', 1000)
    expect(activeMessageCount()).toBe(1)
    vi.advanceTimersByTime(1000)
    // removal animation timeout (200ms) still pending
    expect(activeMessageCount()).toBe(0)
  })

  it('does not auto-close when duration is 0', () => {
    HMessage.success('persist', 0)
    vi.advanceTimersByTime(10000)
    expect(activeMessageCount()).toBe(1)
  })

  it('close button removes the message', () => {
    HMessage.success('closable', 0)
    const cont = document.querySelector('.h-message-container')!
    const closeBtn = cont.querySelector('.h-message__close') as HTMLElement
    closeBtn.click()
    vi.advanceTimersByTime(200)
    expect(activeMessageCount()).toBe(0)
  })

  it('exposes success/error/warning/info methods', () => {
    expect(typeof HMessage.success).toBe('function')
    expect(typeof HMessage.error).toBe('function')
    expect(typeof HMessage.warning).toBe('function')
    expect(typeof HMessage.info).toBe('function')
  })

  // -------------------------------------------------------------------
  // Progress bar
  // -------------------------------------------------------------------
  it('renders a progress bar element for timed messages', () => {
    HMessage.success('with progress', 1000)
    const progress = document.querySelector('.h-message__progress') as HTMLElement
    expect(progress).toBeTruthy()
    expect(progress.style.opacity).toBe('1')
  })

  it('hides the progress bar for persistent messages (duration=0)', () => {
    HMessage.success('no progress', 0)
    const progress = document.querySelector('.h-message__progress') as HTMLElement
    expect(progress).toBeTruthy()
    expect(progress.style.opacity).toBe('0')
  })
})

describe('HMessage service — reduced motion', () => {
  let HMessage: typeof import('../service').HMessage
  let originalMatchMedia: unknown

  beforeEach(async () => {
    vi.resetModules()
    vi.useFakeTimers()
    originalMatchMedia = (window as unknown as { matchMedia: unknown }).matchMedia
    ;(window as unknown as { matchMedia: unknown }).matchMedia = vi.fn((query: string) => ({
      matches: query.includes('prefers-reduced-motion'),
      media: query,
      onchange: null,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      addListener: vi.fn(),
      removeListener: vi.fn(),
      dispatchEvent: vi.fn(),
    }))
    HMessage = (await import('../service')).HMessage
  })

  afterEach(() => {
    vi.useRealTimers()
    ;(window as unknown as { matchMedia: unknown }).matchMedia = originalMatchMedia
    document.body.innerHTML = ''
  })

  function activeMessageCount(): number {
    const cont = document.querySelector('.h-message-container')
    if (!cont) return 0
    return Array.from(cont.children).filter(
      c => (c as HTMLElement).dataset.removing !== 'true'
    ).length
  }

  it('shows the message instantly without enter transition', () => {
    HMessage.success('instant')
    const el = document.querySelector('.h-message') as HTMLElement
    expect(el.style.opacity).toBe('1')
    expect(el.style.transform).toBe('translateY(0)')
    expect(el.style.transition).toBe('none')
  })

  it('removes the message immediately without fade-out delay', () => {
    HMessage.success('quick remove', 1000)
    expect(activeMessageCount()).toBe(1)
    vi.advanceTimersByTime(1000)
    // With reduced motion, removeMessage calls el.remove() synchronously —
    // no 200ms fade-out timer, so the element is gone immediately.
    expect(document.querySelector('.h-message')).toBeNull()
    expect(activeMessageCount()).toBe(0)
  })

  it('still respects duration for auto-close', () => {
    HMessage.success('timed', 500)
    expect(activeMessageCount()).toBe(1)
    vi.advanceTimersByTime(499)
    expect(activeMessageCount()).toBe(1)
    vi.advanceTimersByTime(1)
    expect(activeMessageCount()).toBe(0)
  })
})

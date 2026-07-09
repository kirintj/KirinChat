import { ref, onMounted, onUnmounted, Ref } from 'vue'

/*
 * 响应式断点 — 与 styles/breakpoints.scss 保持一致
 *
 *   phone:       ≤ 767px   (isMobile = true)
 *   tablet:   768 - 1199px (isTablet = true)
 *   desktop:  1200 - 1399px (isDesktop = true)
 *   wide:      ≥ 1400px    (isWide = true)
 */
const BP_TABLET = 768
const BP_DESKTOP = 1200
const BP_WIDE = 1400

function createMediaQuery(query: string): { matches: Ref<boolean>, cleanup: () => void } {
  if (typeof window === 'undefined') return { matches: ref(false), cleanup: () => {} }
  const mq = window.matchMedia(query)
  const matches = ref(mq.matches)
  const handler = (e: MediaQueryListEvent) => { matches.value = e.matches }
  mq.addEventListener('change', handler)
  const cleanup = () => mq.removeEventListener('change', handler)
  return { matches, cleanup }
}

export function useBreakpoint() {
  const mobile = createMediaQuery(`(max-width: ${BP_TABLET - 1}px)`)
  const tablet = createMediaQuery(`(min-width: ${BP_TABLET}px) and (max-width: ${BP_DESKTOP - 1}px)`)
  const desktop = createMediaQuery(`(min-width: ${BP_DESKTOP}px)`)
  const wide = createMediaQuery(`(min-width: ${BP_WIDE}px)`)
  const tabletAndBelow = createMediaQuery(`(max-width: ${BP_DESKTOP - 1}px)`)
  const tabletAndAbove = createMediaQuery(`(min-width: ${BP_TABLET}px)`)

  const cleanups = [mobile, tablet, desktop, wide, tabletAndBelow, tabletAndAbove]

  onUnmounted(() => {
    cleanups.forEach(c => c.cleanup())
  })

  return {
    isMobile: mobile.matches,
    isTablet: tablet.matches,
    isDesktop: desktop.matches,
    isWide: wide.matches,
    isTabletAndBelow: tabletAndBelow.matches,
    isTabletAndAbove: tabletAndAbove.matches,
  }
}

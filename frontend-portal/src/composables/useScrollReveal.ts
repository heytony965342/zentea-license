/**
 * 滚动淡入动效组合函数
 */
import { ref, onMounted, onUnmounted } from 'vue'

export function useScrollReveal(threshold = 0.1) {
  const elements = ref<Map<HTMLElement, boolean>>(new Map())
  let observer: IntersectionObserver | null = null

  onMounted(() => {
    observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('revealed')
            elements.value.set(entry.target as HTMLElement, true)
          }
        })
      },
      { threshold, rootMargin: '0px 0px -50px 0px' }
    )
  })

  onUnmounted(() => {
    observer?.disconnect()
  })

  function observe(el: HTMLElement | null) {
    if (el && observer) {
      el.classList.add('scroll-reveal')
      observer.observe(el)
      elements.value.set(el, false)
    }
  }

  return { observe }
}

// CSS 样式（需要在全局或组件中引入）
export const scrollRevealStyles = `
.scroll-reveal {
  opacity: 0;
  transform: translateY(40px);
  transition: opacity 0.8s cubic-bezier(0.4, 0, 0.2, 1),
              transform 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

.scroll-reveal.revealed {
  opacity: 1;
  transform: translateY(0);
}

/* 支持延迟 */
.scroll-reveal[data-delay="100"] { transition-delay: 100ms; }
.scroll-reveal[data-delay="200"] { transition-delay: 200ms; }
.scroll-reveal[data-delay="300"] { transition-delay: 300ms; }
.scroll-reveal[data-delay="400"] { transition-delay: 400ms; }
.scroll-reveal[data-delay="500"] { transition-delay: 500ms; }
`


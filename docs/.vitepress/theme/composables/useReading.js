// Estado da leitura da página aberta: progresso de rolagem, dock visível, parágrafo em foco,
// tempo de leitura e o capítulo mais avançado já aberto (trava de spoiler do site inteiro).
import { ref } from 'vue'

export const FURTHEST_KEY = 'lazaro:furthest-chapter'
const WORDS_PER_MINUTE = 200

const progress = ref(0)
const dockVisible = ref(true)
const minutes = ref(0)
const furthest = ref(1)
let lastY = 0
let ticking = false

export function loadFurthest() {
  try { furthest.value = Number(localStorage.getItem(FURTHEST_KEY)) || 1 } catch { /* sem storage */ }
  return furthest.value
}

export function track(chapter) {
  if (!chapter || chapter <= furthest.value) return
  furthest.value = chapter
  try { localStorage.setItem(FURTHEST_KEY, String(chapter)) } catch { /* modo privado: só vale na sessão */ }
}

export function measure() {
  const text = document.querySelector('.vp-doc')?.innerText ?? ''
  const words = text.trim() ? text.trim().split(/\s+/).length : 0
  minutes.value = Math.max(1, Math.ceil(words / WORDS_PER_MINUTE))
  progress.value = 0
  dockVisible.value = true
}

function markFocus() {
  if (!document.body.classList.contains('reader-mode-active')) return
  const line = window.innerHeight * 0.45
  let best = null
  document.querySelectorAll('.vp-doc p').forEach((p) => { if (p.getBoundingClientRect().top < line) best = p })
  document.querySelectorAll('.vp-doc p.in-focus').forEach((p) => p !== best && p.classList.remove('in-focus'))
  best?.classList.add('in-focus')
}

function onScroll() {
  if (ticking) return
  ticking = true
  requestAnimationFrame(() => {
    const y = window.scrollY
    const max = document.documentElement.scrollHeight - window.innerHeight
    progress.value = max > 0 ? Math.min(1, y / max) : 0
    // O dock some ao descer lendo e volta ao subir ou perto do fim.
    if (Math.abs(y - lastY) > 6) dockVisible.value = y < lastY || y < 120 || progress.value > 0.96
    lastY = y
    markFocus()
    ticking = false
  })
}

export function startReading() {
  window.addEventListener('scroll', onScroll, { passive: true })
  return () => window.removeEventListener('scroll', onScroll)
}

export const showDock = () => { dockVisible.value = true }

export function useReading() {
  return { progress, dockVisible, minutes, furthest }
}

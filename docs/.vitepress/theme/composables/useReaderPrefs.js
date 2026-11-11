// Tamanho, entrelinha, papel e letra do leitor, mais o modo foco. Guardado por leitor (localStorage).
import { ref, watch } from 'vue'
import { normalizePrefs, stepSize } from '../lib/reader-prefs.mjs'

const KEY = 'sodio:reader'
const prefs = ref(normalizePrefs())
const focus = ref(false)
let started = false

function apply(p) {
  const root = document.documentElement
  root.style.setProperty('--reader-font-scale', String(p.size / 100))
  root.style.setProperty('--reader-line-height', String(p.lineHeight))
  if (p.skin === 'auto') delete root.dataset.skin
  else root.dataset.skin = p.skin
  root.dataset.face = p.face
}

export function initReaderPrefs() {
  if (started || typeof window === 'undefined') return
  started = true
  try { prefs.value = normalizePrefs(JSON.parse(localStorage.getItem(KEY))) } catch { /* sem storage */ }
  apply(prefs.value)
  watch(prefs, (p) => {
    apply(p)
    try { localStorage.setItem(KEY, JSON.stringify(p)) } catch { /* modo privado */ }
  }, { deep: true })
  watch(focus, (on) => document.body.classList.toggle('reader-mode-active', on))
}

export const setPref = (key, value) => { prefs.value = normalizePrefs({ ...prefs.value, [key]: value }) }
export const changeSize = (dir) => setPref('size', stepSize(prefs.value.size, dir))
export const toggleFocus = () => { focus.value = !focus.value }
export const exitFocus = () => { focus.value = false }

export function useReaderPrefs() {
  return { prefs, focus }
}

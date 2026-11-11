// Atalhos de teclado do leitor (os mesmos do tema anterior):
// ` ou Ctrl/Cmd K → Lázaro · F → foco · Ctrl/Cmd + − 0 → fonte · Alt ← → → capítulos.
import { onMounted, onUnmounted } from 'vue'
import { changeSize, toggleFocus } from './useReaderPrefs.js'

const typing = (el) => el && (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA' || el.tagName === 'SELECT' || el.isContentEditable)

export function useShortcuts({ palette, prev, next }) {
  const onKey = (e) => {
    const mod = e.ctrlKey || e.metaKey
    if ((mod && e.key.toLowerCase() === 'k') || (e.key === '`' && !typing(document.activeElement))) {
      e.preventDefault()
      palette()
      return
    }
    if (typing(document.activeElement)) return
    if (e.key === 'f' && !mod && !e.altKey) { e.preventDefault(); toggleFocus() }
    else if (mod && (e.key === '+' || e.key === '=')) { e.preventDefault(); changeSize(1) }
    else if (mod && e.key === '-') { e.preventDefault(); changeSize(-1) }
    else if (mod && e.key === '0') { e.preventDefault(); changeSize(0) }
    else if (e.altKey && e.key === 'ArrowLeft') { e.preventDefault(); prev() }
    else if (e.altKey && e.key === 'ArrowRight') { e.preventDefault(); next() }
  }
  onMounted(() => window.addEventListener('keydown', onKey))
  onUnmounted(() => window.removeEventListener('keydown', onKey))
}

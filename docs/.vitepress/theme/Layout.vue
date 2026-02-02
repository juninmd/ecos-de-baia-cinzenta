<script setup>
import DefaultTheme from 'vitepress/theme'
import AudioPlayer from './AudioPlayer.vue'
import LazaroTerminal from './components/LazaroTerminal.vue'
import { useData, useRouter } from 'vitepress'
import { ref, onMounted, onUnmounted, computed } from 'vue'

const { Layout } = DefaultTheme
const { frontmatter, page } = useData()
const router = useRouter()

// Configuration constants
const MAX_CHAPTER = 114
const WORDS_PER_MINUTE = 200

const isTerminalOpen = ref(false)
const isReaderMode = ref(false)
const fontSize = ref(100) // percentage
const progress = ref(0)
const readingTime = ref(0)
let docHeight = 0
let ticking = false
let resizeObserver = null

const toggleTerminal = () => {
  isTerminalOpen.value = !isTerminalOpen.value
}

const toggleReaderMode = () => {
  isReaderMode.value = !isReaderMode.value
  if (isReaderMode.value) {
    document.body.classList.add('reader-mode-active')
  } else {
    document.body.classList.remove('reader-mode-active')
  }
}

const increaseFontSize = () => {
  if (fontSize.value < 150) {
    fontSize.value += 10
    document.documentElement.style.setProperty('--reader-font-scale', fontSize.value / 100)
  }
}

const decreaseFontSize = () => {
  if (fontSize.value > 70) {
    fontSize.value -= 10
    document.documentElement.style.setProperty('--reader-font-scale', fontSize.value / 100)
  }
}

const resetFontSize = () => {
  fontSize.value = 100
  document.documentElement.style.setProperty('--reader-font-scale', 1)
}

// Calculate reading time (average words per minute in Portuguese)
const calculateReadingTime = () => {
  const content = document.querySelector('.vp-doc')
  if (content) {
    const text = content.innerText || ''
    const words = text.trim().split(/\s+/).length
    readingTime.value = Math.ceil(words / WORDS_PER_MINUTE)
  }
}

// Navigation between chapters
const currentChapterNumber = computed(() => {
  const match = page.value.filePath?.match(/\/capitulo-(\d+)\.md$/)
  return match ? parseInt(match[1]) : null
})

const hasNextChapter = computed(() => {
  return currentChapterNumber.value !== null && currentChapterNumber.value < MAX_CHAPTER
})

const hasPrevChapter = computed(() => {
  return currentChapterNumber.value !== null && currentChapterNumber.value > 1
})

const goToNextChapter = () => {
  if (hasNextChapter.value) {
    router.go(`/capitulo-${currentChapterNumber.value + 1}`)
    window.scrollTo(0, 0)
  }
}

const goToPrevChapter = () => {
  if (hasPrevChapter.value) {
    router.go(`/capitulo-${currentChapterNumber.value - 1}`)
    window.scrollTo(0, 0)
  }
}

const handleKeydown = (e) => {
  // Toggle on '`' (backtick) or Ctrl+K
  if (e.key === '`' || (e.ctrlKey && e.key === 'k')) {
    e.preventDefault()
    toggleTerminal()
  }
  // Reader mode toggle with F (focus mode)
  if (e.key === 'f' && !e.ctrlKey && !e.metaKey && !e.altKey) {
    const activeElement = document.activeElement
    if (activeElement && (activeElement.tagName === 'INPUT' || activeElement.tagName === 'TEXTAREA')) {
      return // Don't interfere with form inputs
    }
    e.preventDefault()
    toggleReaderMode()
  }
  // Font size controls
  if (e.key === '+' && (e.ctrlKey || e.metaKey)) {
    e.preventDefault()
    increaseFontSize()
  }
  if (e.key === '-' && (e.ctrlKey || e.metaKey)) {
    e.preventDefault()
    decreaseFontSize()
  }
  if (e.key === '0' && (e.ctrlKey || e.metaKey)) {
    e.preventDefault()
    resetFontSize()
  }
  // Chapter navigation
  if (e.key === 'ArrowLeft' && e.altKey) {
    e.preventDefault()
    goToPrevChapter()
  }
  if (e.key === 'ArrowRight' && e.altKey) {
    e.preventDefault()
    goToNextChapter()
  }
}

const calculateDocHeight = () => {
  docHeight = document.body.scrollHeight - window.innerHeight
}

const updateProgress = () => {
  if (!ticking) {
    window.requestAnimationFrame(() => {
      const scrollTop = window.scrollY
      if (docHeight > 0) {
        progress.value = (scrollTop / docHeight) * 100
      }
      ticking = false
    })
    ticking = true
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
  calculateDocHeight()
  calculateReadingTime()
  window.addEventListener('resize', calculateDocHeight)

  if (window.ResizeObserver) {
    resizeObserver = new ResizeObserver(() => {
      calculateDocHeight()
    })
    resizeObserver.observe(document.body)
  }

  window.addEventListener('scroll', updateProgress)
  
  // Initialize font scale
  document.documentElement.style.setProperty('--reader-font-scale', 1)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
  window.removeEventListener('resize', calculateDocHeight)
  window.removeEventListener('scroll', updateProgress)
  if (resizeObserver) {
    resizeObserver.disconnect()
  }
  // Cleanup reader mode class
  document.body.classList.remove('reader-mode-active')
})
</script>

<template>
  <div class="reading-progress-bar" :style="{ width: progress + '%' }"></div>
  <Layout>
    <template #doc-before>
      <div v-if="frontmatter.image" class="chapter-cover-container">
        <img :src="frontmatter.image" class="chapter-cover" :alt="frontmatter.title || 'Imagem do Capítulo'" />
      </div>
      
      <!-- Reading Time Indicator -->
      <div v-if="readingTime > 0" class="reading-time">
        <span class="reading-time-icon">🕐</span>
        <span class="reading-time-text">{{ readingTime }} min de leitura</span>
      </div>
      
      <AudioPlayer />
    </template>

    <!-- Chapter Navigation -->
    <template #doc-after>
      <div class="chapter-navigation">
        <button 
          v-if="hasPrevChapter" 
          @click="goToPrevChapter" 
          class="chapter-nav-btn prev"
          aria-label="Capítulo Anterior"
        >
          <span class="nav-arrow">←</span>
          <span class="nav-label">Capítulo {{ currentChapterNumber - 1 }}</span>
        </button>
        <div v-else class="chapter-nav-spacer"></div>
        
        <button 
          v-if="hasNextChapter" 
          @click="goToNextChapter" 
          class="chapter-nav-btn next"
          aria-label="Próximo Capítulo"
        >
          <span class="nav-label">Capítulo {{ currentChapterNumber + 1 }}</span>
          <span class="nav-arrow">→</span>
        </button>
        <div v-else class="chapter-nav-spacer"></div>
      </div>
    </template>

    <!-- Floating Action Buttons -->
    <template #layout-bottom>
      <!-- Font Size Controls in Reader Mode -->
      <div v-if="isReaderMode" class="font-controls">
        <button @click="decreaseFontSize" class="font-btn" aria-label="Diminuir Fonte" title="Diminuir fonte (Ctrl/Cmd -)">
          A-
        </button>
        <button @click="resetFontSize" class="font-btn" aria-label="Resetar Fonte" title="Fonte padrão (Ctrl/Cmd 0)">
          A
        </button>
        <button @click="increaseFontSize" class="font-btn" aria-label="Aumentar Fonte" title="Aumentar fonte (Ctrl/Cmd +)">
          A+
        </button>
      </div>
      
      <button class="fab-btn reader-fab" @click="toggleReaderMode" :aria-label="isReaderMode ? 'Sair do Modo Leitura' : 'Modo Leitura'" :title="isReaderMode ? 'Sair do Modo Leitura (F)' : 'Modo Leitura (F)'">
        <span class="reader-icon">{{ isReaderMode ? '✕' : '📖' }}</span>
      </button>
      <button class="fab-btn terminal-fab" @click="toggleTerminal" aria-label="Abrir Terminal Lázaro" title="Acessar Sistema (` ou Ctrl+K)">
        <span class="terminal-icon">_></span>
      </button>
      <LazaroTerminal :is-open="isTerminalOpen" @close="isTerminalOpen = false" />
    </template>
  </Layout>
</template>

<style>
/* ===== READING PROGRESS BAR ===== */
.reading-progress-bar {
  position: fixed;
  top: 0;
  left: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--neon-purple, #a855f7), var(--neon-cyan, #06b6d4));
  z-index: 9999;
  transition: width 0.1s ease;
  box-shadow: 
    0 0 10px var(--neon-purple, #a855f7),
    0 0 25px rgba(168, 85, 247, 0.5),
    0 2px 10px rgba(168, 85, 247, 0.3);
}

/* ===== CHAPTER COVER ===== */
.chapter-cover-container {
  margin-bottom: 2.5rem;
  border-radius: 12px;
  overflow: hidden;
  position: relative;
}

.chapter-cover-container::before {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, transparent 50%, rgba(10, 10, 15, 0.9) 100%);
  pointer-events: none;
  z-index: 1;
}

.chapter-cover {
  width: 100%;
  max-height: 450px;
  object-fit: cover;
  display: block;
  filter: contrast(1.05) saturate(1.1);
}

.dark .chapter-cover-container {
  box-shadow: 
    0 8px 40px rgba(0, 0, 0, 0.5),
    0 0 60px rgba(168, 85, 247, 0.15),
    inset 0 0 0 1px rgba(168, 85, 247, 0.2);
}

/* ===== FLOATING ACTION BUTTON ===== */
.terminal-fab {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 52px;
  height: 52px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 9998;
  background: linear-gradient(135deg, #0d0d0d 0%, #1a1a1a 100%);
  border: 1px solid #10b981;
  color: #10b981;
  font-family: "Fira Code", monospace;
  font-weight: bold;
  font-size: 1.2rem;
  box-shadow: 
    0 4px 20px rgba(16, 185, 129, 0.3),
    inset 0 0 20px rgba(16, 185, 129, 0.1);
  animation: terminal-pulse 3s ease-in-out infinite;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes terminal-pulse {
  0%, 100% { box-shadow: 0 4px 20px rgba(16, 185, 129, 0.3), inset 0 0 20px rgba(16, 185, 129, 0.1); }
  50% { box-shadow: 0 4px 30px rgba(16, 185, 129, 0.5), inset 0 0 30px rgba(16, 185, 129, 0.15); }
}

.terminal-fab:hover {
  transform: scale(1.1) translateY(-2px);
  box-shadow: 
    0 0 30px rgba(16, 185, 129, 0.6),
    0 0 60px rgba(16, 185, 129, 0.3),
    inset 0 0 20px rgba(16, 185, 129, 0.2);
  border-color: #34d399;
  color: #34d399;
}

.terminal-icon {
  text-shadow: 0 0 10px currentColor;
}

/* ===== READER MODE FAB ===== */
.reader-fab {
  position: fixed;
  bottom: 90px;
  right: 24px;
  width: 52px;
  height: 52px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 9998;
  background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
  border: 1px solid var(--neon-purple, #a855f7);
  color: var(--neon-purple, #a855f7);
  font-size: 1.5rem;
  box-shadow:
    0 4px 20px rgba(168, 85, 247, 0.3),
    inset 0 0 20px rgba(168, 85, 247, 0.1);
  transition: all 0.3s ease;
}

.reader-fab:hover {
  transform: scale(1.1);
  background: var(--neon-purple, #a855f7);
  color: #fff;
  box-shadow:
    0 0 30px rgba(168, 85, 247, 0.6),
    0 0 60px rgba(168, 85, 247, 0.3);
}

body.reader-mode-active .reader-fab {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.5);
  color: #fff;
}

/* ===== READING TIME INDICATOR ===== */
.reading-time {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-family: var(--vp-font-family-base);
  font-size: 0.9rem;
  color: var(--vp-c-text-2);
  margin-bottom: 1.5rem;
  padding: 0.5rem 1rem;
  background: rgba(168, 85, 247, 0.05);
  border-left: 3px solid var(--neon-purple, #a855f7);
  border-radius: 4px;
}

.reading-time-icon {
  font-size: 1.1rem;
}

/* ===== CHAPTER NAVIGATION ===== */
.chapter-navigation {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 4rem;
  padding-top: 2rem;
  border-top: 1px solid var(--vp-c-divider);
  gap: 1rem;
}

.chapter-nav-btn {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  background: linear-gradient(135deg, rgba(168, 85, 247, 0.1) 0%, rgba(6, 182, 212, 0.05) 100%);
  border: 1px solid rgba(168, 85, 247, 0.3);
  border-radius: 8px;
  color: var(--vp-c-text-1);
  font-family: var(--vp-font-family-display);
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.chapter-nav-btn:hover {
  background: linear-gradient(135deg, rgba(168, 85, 247, 0.2) 0%, rgba(6, 182, 212, 0.1) 100%);
  border-color: var(--neon-purple);
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(168, 85, 247, 0.3);
}

.chapter-nav-btn .nav-arrow {
  font-size: 1.3rem;
  transition: transform 0.3s ease;
}

.chapter-nav-btn.prev:hover .nav-arrow {
  transform: translateX(-4px);
}

.chapter-nav-btn.next:hover .nav-arrow {
  transform: translateX(4px);
}

.chapter-nav-spacer {
  width: 1px;
}

/* ===== FONT SIZE CONTROLS ===== */
.font-controls {
  position: fixed;
  bottom: 156px;
  right: 24px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  z-index: 9998;
}

.font-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
  border: 1px solid rgba(168, 85, 247, 0.5);
  color: var(--neon-purple, #a855f7);
  font-size: 0.85rem;
  font-weight: bold;
  font-family: var(--vp-font-family-base);
  box-shadow: 0 2px 10px rgba(168, 85, 247, 0.2);
  transition: all 0.3s ease;
}

.font-btn:hover {
  background: var(--neon-purple, #a855f7);
  color: #fff;
  transform: scale(1.1);
  box-shadow: 0 0 20px rgba(168, 85, 247, 0.5);
}

/* ===== READER MODE ENHANCEMENTS ===== */
body.reader-mode-active .VPNav,
body.reader-mode-active .VPSidebar,
body.reader-mode-active .VPLocalNav {
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.3s ease;
}

body.reader-mode-active .VPContent {
  padding-left: 0 !important;
}

body.reader-mode-active .vp-doc {
  max-width: 800px;
  margin: 0 auto;
  padding: 3rem 2rem;
}

/* Font scale variable application */
body.reader-mode-active .vp-doc p {
  font-size: calc(1.18rem * var(--reader-font-scale, 1));
  line-height: 1.95;
}

body.reader-mode-active .vp-doc h1 {
  font-size: calc(2.6rem * var(--reader-font-scale, 1));
}

body.reader-mode-active .vp-doc h2 {
  font-size: calc(1.6rem * var(--reader-font-scale, 1));
}

body.reader-mode-active .vp-doc h3 {
  font-size: calc(1.35rem * var(--reader-font-scale, 1));
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .chapter-navigation {
    flex-direction: column;
    gap: 1rem;
  }
  
  .chapter-nav-btn {
    width: 100%;
    justify-content: center;
  }
  
  .font-controls {
    right: 12px;
    bottom: 140px;
  }
  
  .terminal-fab,
  .reader-fab {
    right: 12px;
  }
  
  .reading-time {
    font-size: 0.85rem;
  }
}

</style>

<script setup>
import DefaultTheme from 'vitepress/theme'
import AudioPlayer from './AudioPlayer.vue'
import LazaroTerminal from './components/LazaroTerminal.vue'
import { useData } from 'vitepress'
import { ref, onMounted, onUnmounted } from 'vue'

const { Layout } = DefaultTheme
const { frontmatter } = useData()

const isTerminalOpen = ref(false)
const isReaderMode = ref(false)
const progress = ref(0)
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

const handleKeydown = (e) => {
  // Toggle on '`' (backtick) or Ctrl+K
  if (e.key === '`' || (e.ctrlKey && e.key === 'k')) {
    e.preventDefault()
    toggleTerminal()
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
  window.addEventListener('resize', calculateDocHeight)

  if (window.ResizeObserver) {
    resizeObserver = new ResizeObserver(() => {
      calculateDocHeight()
    })
    resizeObserver.observe(document.body)
  }

  window.addEventListener('scroll', updateProgress)
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
      <AudioPlayer />
    </template>

    <!-- Floating Action Button for Terminal -->
    <template #layout-bottom>
      <button class="fab-btn reader-fab" @click="toggleReaderMode" :aria-label="isReaderMode ? 'Sair do Modo Leitura' : 'Modo Leitura'" :title="isReaderMode ? 'Sair do Modo Leitura' : 'Modo Leitura'">
        <span class="reader-icon">{{ isReaderMode ? '✕' : '📖' }}</span>
      </button>
      <button class="fab-btn terminal-fab" @click="toggleTerminal" aria-label="Abrir Terminal Lázaro" title="Acessar Sistema">
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
</style>

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
    e.preventDefault() // Prevent writing the character
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

  // Initialize and track document height changes efficiently
  calculateDocHeight()
  window.addEventListener('resize', calculateDocHeight)

  if (window.ResizeObserver) {
    resizeObserver = new ResizeObserver(() => {
      calculateDocHeight()
    })
    resizeObserver.observe(document.body)
  }

  window.addEventListener('scroll', updateProgress)

  // Check if reader mode was persisted (optional, but good UX)
  // For now, we start with it off to avoid flashing
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
  window.removeEventListener('resize', calculateDocHeight)
  window.removeEventListener('scroll', updateProgress)
  document.body.classList.remove('reader-mode-active') // Cleanup
  if (resizeObserver) {
    resizeObserver.disconnect()
  }
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
      <div class="fabs-container">
        <button class="fab-btn reader-fab" @click="toggleReaderMode" :title="isReaderMode ? 'Sair do Modo Leitura' : 'Modo Leitura'">
          <span class="icon">{{ isReaderMode ? '✕' : '📖' }}</span>
        </button>
        <button class="fab-btn terminal-fab" @click="toggleTerminal" aria-label="Abrir Terminal Lázaro" title="Acessar Sistema">
          <span class="terminal-icon">_></span>
        </button>
      </div>
      <LazaroTerminal :is-open="isTerminalOpen" @close="isTerminalOpen = false" />
    </template>
  </Layout>
</template>

<style>
.reading-progress-bar {
  position: fixed;
  top: 0;
  left: 0;
  height: 4px;
  background: var(--vp-c-brand);
  z-index: 9999;
  transition: width 0.1s ease;
  box-shadow: 0 0 10px var(--vp-c-brand);
}

.chapter-cover-container {
  margin-bottom: 2rem;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}

.chapter-cover {
  width: 100%;
  max-height: 400px;
  object-fit: cover;
  display: block;
}

.fabs-container {
  position: fixed;
  bottom: 20px;
  right: 20px;
  display: flex;
  flex-direction: column;
  gap: 15px;
  z-index: 9998;
  align-items: center;
}

.fab-btn {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: bold;
  font-size: 1.2rem;
  box-shadow: 0 4px 10px rgba(0,0,0,0.3);
}

.fab-btn:hover {
  transform: scale(1.1);
}

.terminal-fab {
  background-color: #0d0d0d;
  border: 1px solid #33ff00;
  color: #33ff00;
  font-family: monospace;
  box-shadow: 0 0 10px rgba(51, 255, 0, 0.4);
}

.terminal-fab:hover {
  box-shadow: 0 0 15px rgba(51, 255, 0, 0.7);
  background-color: #1a1a1a;
}

.reader-fab {
  background-color: #f4ecd8;
  border: 1px solid #d4c5a3;
  color: #5c4b37;
}

.reader-fab:hover {
  background-color: #fff;
  box-shadow: 0 0 15px rgba(255, 255, 255, 0.5);
}

/* READER MODE STYLES */
body.reader-mode-active {
  background-color: #f4ecd8 !important;
  overflow-x: hidden;
}

body.reader-mode-active .VPNav,
body.reader-mode-active .VPSidebar,
body.reader-mode-active .VPFooter,
body.reader-mode-active .on-this-page-container,
body.reader-mode-active .reading-progress-bar {
  display: none !important;
}

body.reader-mode-active .VPContent {
  padding: 0 !important;
  margin: 0 !important;
  max-width: 100% !important;
  background-color: #f4ecd8 !important;
  min-height: 100vh;
}

body.reader-mode-active .VPContent .container {
  max-width: 800px !important;
  margin: 0 auto !important;
  padding: 40px 20px !important;
}

body.reader-mode-active .VPContent .content-container {
  max-width: 100% !important;
}

body.reader-mode-active .main {
  max-width: 800px !important;
  margin: 0 auto !important;
}

body.reader-mode-active :is(h1, h2, h3, h4, h5, h6, p, li, span, div, strong, em) {
  font-family: 'Merriweather', serif !important;
  color: #2c2c2c !important;
}

body.reader-mode-active p {
  font-size: 1.3rem !important;
  line-height: 2 !important;
  margin-bottom: 1.5rem !important;
  text-align: justify;
}

body.reader-mode-active h1 {
  font-family: 'Playfair Display', serif !important;
  font-size: 3rem !important;
  text-align: center;
  margin-bottom: 3rem !important;
  color: #1a1a1a !important;
}

body.reader-mode-active blockquote {
  border-left: 4px solid #8b7d6b !important;
  background-color: rgba(0,0,0,0.05) !important;
  color: #5c4b37 !important;
  font-style: italic;
  padding: 1rem !important;
}
</style>

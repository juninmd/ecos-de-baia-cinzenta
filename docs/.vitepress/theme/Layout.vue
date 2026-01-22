<script setup>
import DefaultTheme from 'vitepress/theme'
import AudioPlayer from './AudioPlayer.vue'
import LazaroTerminal from './components/LazaroTerminal.vue'
import { useData } from 'vitepress'
import { ref, onMounted, onUnmounted } from 'vue'

const { Layout } = DefaultTheme
const { frontmatter } = useData()

const isTerminalOpen = ref(false)

const toggleTerminal = () => {
  isTerminalOpen.value = !isTerminalOpen.value
}

const handleKeydown = (e) => {
  // Toggle on '`' (backtick) or Ctrl+K
  if (e.key === '`' || (e.ctrlKey && e.key === 'k')) {
    e.preventDefault() // Prevent writing the character
    toggleTerminal()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<template>
  <Layout>
    <template #doc-before>
      <div v-if="frontmatter.image" class="chapter-cover-container">
        <img :src="frontmatter.image" class="chapter-cover" :alt="frontmatter.title || 'Imagem do Capítulo'" />
      </div>
      <AudioPlayer />
    </template>

    <!-- Floating Action Button for Terminal -->
    <template #layout-bottom>
      <button class="terminal-fab" @click="toggleTerminal" aria-label="Abrir Terminal Lázaro" title="Acessar Sistema">
        <span class="terminal-icon">_></span>
      </button>
      <LazaroTerminal :is-open="isTerminalOpen" @close="isTerminalOpen = false" />
    </template>
  </Layout>
</template>

<style>
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

.terminal-fab {
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background-color: #0d0d0d;
  border: 1px solid #33ff00;
  color: #33ff00;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 0 10px rgba(51, 255, 0, 0.4);
  z-index: 9998;
  transition: all 0.3s ease;
  font-family: monospace;
  font-weight: bold;
  font-size: 1.2rem;
}

.terminal-fab:hover {
  transform: scale(1.1);
  box-shadow: 0 0 15px rgba(51, 255, 0, 0.7);
  background-color: #1a1a1a;
}
</style>

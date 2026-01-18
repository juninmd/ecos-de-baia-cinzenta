<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vitepress'

const route = useRoute()
const isPlaying = ref(false)
const isPaused = ref(false)
const synth = ref(null)
const utterance = ref(null)
const rate = ref(1)
const availableVoices = ref([])
const selectedVoice = ref(null)

const initSynth = () => {
  if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
    synth.value = window.speechSynthesis

    const loadVoices = () => {
      availableVoices.value = synth.value.getVoices()
      // Try to find a PT-BR voice
      selectedVoice.value = availableVoices.value.find(v => v.lang === 'pt-BR') || availableVoices.value[0]
    }

    loadVoices()
    if (speechSynthesis.onvoiceschanged !== undefined) {
      speechSynthesis.onvoiceschanged = loadVoices
    }
  }
}

onMounted(() => {
  initSynth()
})

onUnmounted(() => {
  stop()
})

watch(() => route.path, () => {
  stop()
})

const getText = () => {
  const content = document.querySelector('.vp-doc')
  return content ? content.innerText : ''
}

const play = () => {
  if (!synth.value) return

  if (isPaused.value) {
    synth.value.resume()
    isPaused.value = false
    isPlaying.value = true
    return
  }

  // If already playing but not paused, stop first (restart)
  if (isPlaying.value) {
    stop()
  }

  const text = getText()
  if (!text) return

  utterance.value = new SpeechSynthesisUtterance(text)
  if (selectedVoice.value) {
    utterance.value.voice = selectedVoice.value
  }
  utterance.value.rate = rate.value
  utterance.value.lang = 'pt-BR'

  utterance.value.onend = () => {
    isPlaying.value = false
    isPaused.value = false
  }

  utterance.value.onerror = (e) => {
    console.error('Speech synthesis error', e)
    isPlaying.value = false
    isPaused.value = false
  }

  synth.value.speak(utterance.value)
  isPlaying.value = true
}

const pause = () => {
  if (synth.value && isPlaying.value) {
    synth.value.pause()
    isPaused.value = true
  }
}

const stop = () => {
  if (synth.value) {
    synth.value.cancel()
    isPlaying.value = false
    isPaused.value = false
  }
}
</script>

<template>
  <div class="audio-player" v-if="synth">
    <div class="controls">
      <button @click="play" :disabled="isPlaying && !isPaused" class="btn" title="Ouvir Capítulo">
        <span v-if="isPlaying && !isPaused">🔊 Ouvindo...</span>
        <span v-else>▶ Ouvir Capítulo</span>
      </button>

      <button @click="pause" :disabled="!isPlaying || isPaused" class="btn" title="Pausar">
        ⏸
      </button>

      <button @click="stop" :disabled="!isPlaying && !isPaused" class="btn" title="Parar">
        ⏹
      </button>

      <select v-model="rate" class="rate-select" title="Velocidade">
        <option :value="0.8">0.8x</option>
        <option :value="1">1x</option>
        <option :value="1.2">1.2x</option>
        <option :value="1.5">1.5x</option>
        <option :value="2">2x</option>
      </select>
    </div>
    <div v-if="isPlaying" class="status">
      Narrando...
    </div>
  </div>
</template>

<style scoped>
.audio-player {
  margin-bottom: 2rem;
  padding: 1rem;
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  background-color: var(--vp-c-bg-soft);
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 10px;
}

.controls {
  display: flex;
  gap: 10px;
  align-items: center;
}

.btn {
  padding: 0.5rem 1rem;
  border: 1px solid var(--vp-c-divider);
  border-radius: 4px;
  background-color: var(--vp-c-bg);
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.btn:hover:not(:disabled) {
  background-color: var(--vp-c-brand);
  color: white;
  border-color: var(--vp-c-brand);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.rate-select {
  padding: 0.5rem;
  border-radius: 4px;
  border: 1px solid var(--vp-c-divider);
  background-color: var(--vp-c-bg);
}

.status {
  font-size: 0.8rem;
  color: var(--vp-c-text-2);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
}
</style>

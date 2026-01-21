<script setup>
import { ref, onMounted, onUnmounted, watch, shallowRef, toRaw } from 'vue'
import { useRoute } from 'vitepress'

const route = useRoute()
const isPlaying = ref(false)
const isPaused = ref(false)
const synth = shallowRef(null)
const utterance = shallowRef(null)
const rate = ref(1) // Changed default to 1x
const availableVoices = shallowRef([])
const selectedVoice = shallowRef(null)

// Chunking state
const segments = shallowRef([])
const currentSegmentIndex = ref(0)

const initSynth = () => {
  if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
    synth.value = window.speechSynthesis

    const loadVoices = () => {
      // Get all voices
      const allVoices = synth.value.getVoices()

      // Filter for pt-BR
      const ptVoices = allVoices.filter(v => v.lang === 'pt-BR' || v.lang === 'pt_BR')

      // If we have PT voices, use them. Otherwise, fall back to all voices.
      if (ptVoices.length > 0) {
        availableVoices.value = ptVoices
      } else {
        availableVoices.value = allVoices
      }

      // Heuristic to find a male voice within the available voices:
      // - "Microsoft Daniel" is a common male voice on Windows
      // - "Google Português do Brasil" is usually female
      // - Look for names containing "Daniel", "Felipe", "Ricardo" or "Microsoft" (often higher quality)
      const maleVoice = availableVoices.value.find(v =>
        v.name.includes('Daniel') ||
        v.name.includes('Microsoft') ||
        (v.name.includes('Google') === false) // Prefer non-Google if Google is the only other option (often female)
      )

      // Default logic: Male/Better quality -> First available
      if (!selectedVoice.value) {
        selectedVoice.value = maleVoice || availableVoices.value[0]
      }
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

// Split text into meaningful chunks (sentences) to avoid browser timeouts
const chunkText = (text) => {
  // Split by common sentence terminators but keep the punctuation
  // This regex looks for (. ? ! or :) followed by whitespace
  const rawSegments = text.match(/[^.?!:]+[.?!:]+/g) || [text]
  return rawSegments.map(s => s.trim()).filter(s => s.length > 0)
}

const speakSegment = () => {
  if (!synth.value || currentSegmentIndex.value >= segments.value.length) {
    isPlaying.value = false
    isPaused.value = false
    currentSegmentIndex.value = 0
    return
  }

  const textSegment = segments.value[currentSegmentIndex.value]
  const u = new SpeechSynthesisUtterance(textSegment)
  utterance.value = u

  // Ensure we use the user-selected voice
  const voice = toRaw(selectedVoice.value)

  if (voice) {
    const currentVoices = synth.value.getVoices()
    const voiceObj = currentVoices.find(v => v.name === voice.name)

    if (voiceObj) {
        u.voice = voiceObj
        u.lang = voiceObj.lang
    } else {
        u.voice = voice
        u.lang = voice.lang || 'pt-BR'
    }
  } else {
    u.lang = 'pt-BR'
  }

  u.rate = rate.value

  u.onend = () => {
    // Successfully finished this segment, move to next
    currentSegmentIndex.value++
    if (isPlaying.value) { // Check if we are still supposed to be playing
        speakSegment()
    }
  }

  u.onerror = (e) => {
    console.error('Speech synthesis error', e)
    // Try to skip to next segment on error
    currentSegmentIndex.value++
    if (isPlaying.value) {
        speakSegment()
    }
  }

  synth.value.speak(u)
}

const play = () => {
  if (!synth.value) return

  if (isPaused.value) {
    synth.value.resume()
    isPaused.value = false
    isPlaying.value = true
    return
  }

  // If already playing, stop first to restart (or handle as "restart" logic)
  if (isPlaying.value) {
    stop()
  }

  const text = getText()
  if (!text) {
    console.warn('AudioPlayer: Nenhum texto encontrado para ler.')
    return
  }

  // Cancel any pending speech
  synth.value.cancel()

  // Initialize segments
  segments.value = chunkText(text)
  currentSegmentIndex.value = 0
  isPlaying.value = true

  // Use a small timeout to allow cancel() to complete
  setTimeout(() => {
    speakSegment()
  }, 50)
}

const pause = () => {
  if (synth.value) {
    synth.value.pause()
    isPaused.value = true
  }
}

const stop = () => {
  if (synth.value) {
    synth.value.cancel()
    isPlaying.value = false
    isPaused.value = false
    currentSegmentIndex.value = 0
  }
}
</script>

<template>
  <div class="audio-player" v-if="synth">
    <div class="controls-row">
      <div class="controls-main">
        <button @click="play" :disabled="isPlaying && !isPaused" class="btn primary" title="Ouvir Capítulo">
          <span v-if="isPlaying && !isPaused">🔊 Ouvindo...</span>
          <span v-else>▶ Ouvir</span>
        </button>

        <button @click="pause" :disabled="!isPlaying || isPaused" class="btn" title="Pausar">
          ⏸
        </button>

        <button @click="stop" :disabled="!isPlaying && !isPaused" class="btn" title="Parar">
          ⏹
        </button>
      </div>

      <div class="controls-settings">
        <div class="setting-group">
          <label for="voice-select" class="label-icon" title="Escolher Voz">🗣️</label>
          <select id="voice-select" v-model="selectedVoice" class="voice-select" :disabled="availableVoices.length === 0">
             <option v-if="availableVoices.length === 0" :value="null">Carregando vozes...</option>
             <option v-for="voice in availableVoices" :key="voice.name" :value="voice">
              {{ voice.name.replace('Microsoft ', '').replace('Google ', '') }}
            </option>
          </select>
        </div>

        <div class="setting-group">
          <label for="rate-select" class="label-icon" title="Velocidade">⚡</label>
          <select id="rate-select" v-model="rate" class="rate-select">
            <option :value="0.8">0.8x (Noir)</option>
            <option :value="0.9">0.9x</option>
            <option :value="1">1x</option>
            <option :value="1.2">1.2x</option>
            <option :value="1.5">1.5x</option>
          </select>
        </div>
      </div>
    </div>

    <div v-if="isPlaying" class="status-bar">
      <span class="status-text">Narrando: {{ selectedVoice?.name }}</span>
      <span class="progress-text" v-if="segments.length > 0">
        ({{ Math.round(((currentSegmentIndex) / segments.length) * 100) }}%)
      </span>
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
  flex-direction: column;
  gap: 10px;
}

.controls-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.controls-main {
  display: flex;
  gap: 8px;
}

.controls-settings {
  display: flex;
  gap: 10px;
  align-items: center;
}

.setting-group {
  display: flex;
  align-items: center;
  gap: 4px;
}

.btn {
  padding: 0.5rem 0.8rem;
  border: 1px solid var(--vp-c-divider);
  border-radius: 4px;
  background-color: var(--vp-c-bg);
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.btn.primary {
  font-weight: 600;
  border-color: var(--vp-c-brand);
  color: var(--vp-c-brand);
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

select {
  padding: 0.4rem;
  border-radius: 4px;
  border: 1px solid var(--vp-c-divider);
  background-color: var(--vp-c-bg);
  font-size: 0.85rem;
  max-width: 150px;
}

.voice-select {
  max-width: 200px;
}

.label-icon {
  font-size: 1rem;
  cursor: help;
}

.status-bar {
  border-top: 1px solid var(--vp-c-divider);
  padding-top: 8px;
  font-size: 0.8rem;
  color: var(--vp-c-text-2);
  display: flex;
  justify-content: space-between;
}

.status-text {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
}

@media (max-width: 600px) {
  .controls-row {
    flex-direction: column;
    align-items: stretch;
  }

  .controls-main, .controls-settings {
    justify-content: space-between;
  }

  .voice-select {
    max-width: 120px;
  }
}
</style>

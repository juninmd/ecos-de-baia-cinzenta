<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vitepress'

const route = useRoute()
const isPlaying = ref(false)
const isPaused = ref(false)
const synth = ref(null)
const utterance = ref(null)
const rate = ref(1) // Changed default to 1x
const availableVoices = ref([])
const selectedVoice = ref(null)

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

  // Ensure we use the user-selected voice
  if (selectedVoice.value) {
    // We need to match the name back to the actual voice object in the synth list
    // because some browsers might invalidate voice objects on reload
    const currentVoices = synth.value.getVoices()
    const voiceObj = currentVoices.find(v => v.name === selectedVoice.value.name)

    if (voiceObj) {
        utterance.value.voice = voiceObj
        // Use the voice's native language to prevent silence due to mismatch
        utterance.value.lang = voiceObj.lang
    } else {
        // Fallback to the stored value if we can't find it in the current list
        utterance.value.voice = selectedVoice.value
        utterance.value.lang = selectedVoice.value.lang || 'pt-BR'
    }
  } else {
    utterance.value.lang = 'pt-BR'
  }

  utterance.value.rate = rate.value

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
          <select id="voice-select" v-model="selectedVoice" class="voice-select">
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

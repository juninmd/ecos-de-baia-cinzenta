<script setup>
import { ref, onMounted, onUnmounted, watch, shallowRef, toRaw, nextTick } from 'vue'
import { useRoute, useData, useRouter } from 'vitepress'

const route = useRoute()
const { page } = useData()
const router = useRouter()

const isPlaying = ref(false)
const isPaused = ref(false)
const synth = shallowRef(null)
const utterance = shallowRef(null)
const rate = ref(1) // Changed default to 1x
const availableVoices = shallowRef([])
const selectedVoice = shallowRef(null)
const statusMessage = ref('')

// Chunking state
const segments = shallowRef([])
const currentSegmentIndex = ref(0)

const updateStorage = (val) => {
  if (typeof window !== 'undefined') {
    sessionStorage.setItem('tts_continuous', val ? 'true' : 'false')
  }
}

const getStorage = () => {
  if (typeof window !== 'undefined') {
    return sessionStorage.getItem('tts_continuous') === 'true'
  }
  return false
}

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

const clearHighlights = () => {
  if (typeof document === 'undefined') return
  const highlighted = document.querySelectorAll('.active-reading')
  highlighted.forEach(el => el.classList.remove('active-reading'))
}

const _stop = () => {
  if (synth.value) {
    synth.value.cancel()
    isPlaying.value = false
    isPaused.value = false
    currentSegmentIndex.value = 0
    statusMessage.value = ''
    clearHighlights()
  }
}

const stop = () => {
  updateStorage(false)
  _stop()
}

// Function to attach markers and click listeners to paragraphs
const attachParagraphListeners = () => {
  if (typeof document === 'undefined') return

  // Clean up old segments since we're re-parsing
  segments.value = []

  const paragraphs = document.querySelectorAll('.vp-doc p')
  let segmentCounter = 0
  const newSegments = []

  paragraphs.forEach((p, index) => {
    // Skip empty paragraphs
    const text = p.innerText.trim()
    if (!text) return

    // Add play icon/marker if not present
    if (!p.querySelector('.tts-marker')) {
      const marker = document.createElement('span')
      marker.className = 'tts-marker'
      marker.innerHTML = ' ▶'
      marker.title = 'Ouvir a partir daqui'
      marker.style.cursor = 'pointer'
      marker.style.color = 'var(--vp-c-brand)'
      marker.style.opacity = '0.5'
      marker.style.fontSize = '0.8em'
      marker.style.marginLeft = '5px'

      // Prevent selecting text when clicking marker
      marker.style.userSelect = 'none'

      marker.onclick = (e) => {
        e.stopPropagation()
        // Find the start index for this paragraph
        const targetIndex = newSegments.findIndex(s => s.element === p)
        if (targetIndex !== -1) {
            startFromSegment(targetIndex)
        }
      }

      p.appendChild(marker)
    }

    // Split paragraph text into chunks for better TTS handling
    // We match sentences but keep them associated with this paragraph element
    const rawChunks = text.match(/[^.?!:]+[.?!:]+/g) || [text]
    const chunks = rawChunks.map(s => s.trim()).filter(s => s.length > 0)

    chunks.forEach(chunk => {
        newSegments.push({
            text: chunk,
            element: p,
            originalIndex: index
        })
    })
  })

  segments.value = newSegments
}

const startFromSegment = (index) => {
    // If playing, stop but don't reset everything completely (keep segments)
    if (synth.value) synth.value.cancel()

    updateStorage(true) // Ensure continuous mode is on if user manually clicks
    currentSegmentIndex.value = index
    isPlaying.value = true
    isPaused.value = false
    statusMessage.value = ''

    speakSegment()
}

onMounted(() => {
  initSynth()

  // Initial setup of markers
  setTimeout(() => {
    attachParagraphListeners()

    if (getStorage()) {
        _play()
    }
  }, 500)
})

onUnmounted(() => {
  _stop()
})

watch(() => route.path, () => {
  _stop()
  // Re-attach listeners on new page
  setTimeout(() => {
    attachParagraphListeners()
    if (getStorage()) {
        _play()
    }
  }, 500)
})


const speakSegment = () => {
  if (!synth.value) return

  // Check if finished
  if (currentSegmentIndex.value >= segments.value.length) {
    if (getStorage() && page.value.next) {
        statusMessage.value = 'Próximo capítulo em 3s...'
        setTimeout(() => {
            router.go(page.value.next.link)
        }, 3000)
        return
    }

    isPlaying.value = false
    isPaused.value = false
    currentSegmentIndex.value = 0
    clearHighlights()
    return
  }

  const segment = segments.value[currentSegmentIndex.value]

  // Highlight logic
  clearHighlights()
  if (segment.element) {
    segment.element.classList.add('active-reading')
    // Scroll into view if needed
    segment.element.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }

  const u = new SpeechSynthesisUtterance(segment.text)
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

const _play = () => {
  if (!synth.value) return

  if (isPaused.value) {
    synth.value.resume()
    isPaused.value = false
    isPlaying.value = true
    return
  }

  // If segments are empty (e.g. fresh load), ensure we have them
  if (segments.value.length === 0) {
    attachParagraphListeners()
  }

  if (segments.value.length === 0) {
      console.warn('AudioPlayer: Nenhum texto encontrado.')
      return
  }

  isPlaying.value = true

  // If we are essentially restarting or just starting:
  // If currentSegmentIndex is 0, start from beginning.
  // If it is non-zero, it means we paused or selected a specific point.

  speakSegment()
}

const play = () => {
  updateStorage(true)
  // Check if we need to reset index (e.g. if we finished previously)
  if (!isPlaying.value && !isPaused.value && currentSegmentIndex.value >= segments.value.length) {
      currentSegmentIndex.value = 0
  }
  _play()
}

const _pause = () => {
  if (synth.value) {
    synth.value.pause()
    isPaused.value = true
  }
}

const pause = () => {
  updateStorage(false)
  _pause()
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

    <div v-if="isPlaying || statusMessage" class="status-bar">
      <span class="status-text">{{ statusMessage || (selectedVoice ? `Narrando: ${selectedVoice.name}` : '') }}</span>
      <span class="progress-text" v-if="segments.length > 0 && !statusMessage">
        {{ Math.round(((currentSegmentIndex) / segments.length) * 100) }}%
      </span>
    </div>

    <div v-if="(isPlaying || statusMessage) && segments.length > 0" class="progress-container">
        <div class="progress-fill" :style="{ width: ((currentSegmentIndex / segments.length) * 100) + '%' }"></div>
    </div>
  </div>
</template>

<style>
/* Global styles for markers and highlighting */
.active-reading {
    background-color: rgba(255, 255, 0, 0.1); /* Subtle yellow highlight */
    border-left: 3px solid var(--vp-c-brand);
    padding-left: 8px;
    transition: all 0.3s ease;
}

.tts-marker {
    display: inline-block;
    opacity: 0;
    transition: opacity 0.2s ease;
}

.vp-doc p:hover .tts-marker {
    opacity: 1 !important;
}

/* Ensure opacity is visible on mobile touches if needed, or leave as hover-only for clean UI */
</style>

<style scoped>
.progress-container {
  width: 100%;
  height: 4px;
  background-color: var(--vp-c-divider);
  border-radius: 2px;
  overflow: hidden;
  margin-top: 5px;
}

.progress-fill {
  height: 100%;
  background-color: var(--vp-c-brand);
  transition: width 0.3s ease;
}

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

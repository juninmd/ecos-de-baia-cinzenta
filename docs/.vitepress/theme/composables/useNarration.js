// Narração do capítulo (Web Speech API), compartilhada entre o dock, o painel e os marcadores ▶.
// Lê frase a frase, acende o parágrafo, marca a frase e, no fim, segue para o próximo capítulo.
import { ref, shallowRef, computed } from 'vue'
import { attachMarkers, clearHighlight, collectSegments, highlight } from '../lib/narration-dom.mjs'
import { speakable } from '../lib/sentences.mjs'
import { MAX_SKIPS_IN_A_ROW, NO_VOICE, speechErrorAction } from '../lib/speech-errors.mjs'
import { pickVoices } from '../lib/voices.mjs'

const CONTINUOUS_KEY = 'tts_continuous'
const PREFS_KEY = 'sodio:narration'

const supported = ref(false)
const playing = ref(false)
const paused = ref(false)
const rate = ref(1)
const voices = shallowRef([])
const voiceName = ref('')
const follow = ref(true) // seguir para o próximo capítulo ao terminar
const segments = shallowRef([])
const index = ref(0)
const countdown = ref(0) // segundos até abrir o próximo capítulo (0 = sem contagem)
const error = ref('') // aviso quando o aparelho não consegue narrar
let skips = 0
let synth = null
let goNext = null
let timer = null
let current = null // utterance em curso: eventos de uma fala cancelada são ignorados

const store = (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)) } catch { /* sem storage */ } }
const load = (k) => { try { return JSON.parse(localStorage.getItem(k)) } catch { return null } }
const setContinuous = (on) => { try { sessionStorage.setItem(CONTINUOUS_KEY, String(on)) } catch { /* privado */ } }
const isContinuous = () => { try { return sessionStorage.getItem(CONTINUOUS_KEY) === 'true' } catch { return false } }
const savePrefs = () => store(PREFS_KEY, { rate: rate.value, voice: voiceName.value, follow: follow.value })

function loadVoices() {
  const { list, name } = pickVoices(synth.getVoices(), voiceName.value)
  voices.value = list
  voiceName.value = name
}

export function initNarration(next) {
  goNext = next
  if (supported.value || typeof window === 'undefined' || !('speechSynthesis' in window)) return
  synth = window.speechSynthesis
  supported.value = true
  const saved = load(PREFS_KEY)
  if (saved) { rate.value = saved.rate ?? 1; voiceName.value = saved.voice ?? ''; follow.value = saved.follow ?? true }
  loadVoices()
  synth.addEventListener?.('voiceschanged', loadVoices)
}

function speakCurrent() {
  if (!playing.value) return
  if (index.value >= segments.value.length) return finish()
  const seg = segments.value[index.value]
  highlight(seg)
  seg.element.scrollIntoView({ behavior: 'smooth', block: 'center' })
  const u = new SpeechSynthesisUtterance(speakable(seg.text))
  const voice = synth.getVoices().find((v) => v.name === voiceName.value)
  if (voice) { u.voice = voice; u.lang = voice.lang } else u.lang = 'pt-BR'
  u.rate = rate.value
  const advance = () => { if (u !== current) return; index.value++; speakCurrent() }
  u.onstart = () => { skips = 0; error.value = '' }
  u.onend = advance
  u.onerror = (e) => {
    if (u !== current) return
    const { action, message } = speechErrorAction(e.error)
    if (action === 'skip' && ++skips < MAX_SKIPS_IN_A_ROW) advance()
    else if (action !== 'ignore') { stop(); error.value = message ?? NO_VOICE }
  }
  current = u
  synth.speak(u)
}

function finish() {
  reset()
  if (!follow.value || !isContinuous() || !goNext?.()) return
  countdown.value = 5
  timer = setInterval(() => {
    countdown.value--
    if (countdown.value > 0) return
    clearInterval(timer)
    goNext()?.()
  }, 1000)
}

export function cancelCountdown() {
  clearInterval(timer)
  countdown.value = 0
  setContinuous(false)
}

export function prepare() {
  if (typeof document === 'undefined') return
  segments.value = collectSegments()
  attachMarkers(segments.value, (el) => startFrom(segments.value.findIndex((s) => s.element === el)))
}

export function startFrom(i) {
  if (!supported.value || i < 0) return
  error.value = ''; skips = 0
  synth.cancel()
  cancelCountdown()
  setContinuous(true)
  if (!segments.value.length) prepare()
  index.value = Math.min(i, Math.max(segments.value.length - 1, 0))
  playing.value = true
  paused.value = false
  speakCurrent()
}

// Pausa = cancelar e lembrar a frase: speechSynthesis.pause() é ignorado no Linux e falha no
// Android. Retomar recomeça a frase em que parou, o que funciona em todo navegador.
export const play = () => { if (paused.value || !playing.value) startFrom(index.value) }
export const pause = () => { if (playing.value) { current = null; synth.cancel(); paused.value = true; setContinuous(false) } }
export const toggle = () => (playing.value && !paused.value ? pause() : play())

function reset() {
  current = null
  synth?.cancel()
  playing.value = false
  paused.value = false
  index.value = 0
  clearHighlight()
}

export function stop() { reset(); setContinuous(false) }

// Troca de página: para o que estava falando, recoleta e retoma se o modo contínuo estiver ligado.
export function onPageChange() {
  const resume = isContinuous()
  reset()
  clearInterval(timer)
  countdown.value = 0
  error.value = ''
  setTimeout(() => { prepare(); if (resume && supported.value) startFrom(0) }, 400)
}

export function setRate(v) { rate.value = v; savePrefs(); if (playing.value && !paused.value) startFrom(index.value) }
export function setVoice(name) { voiceName.value = name; savePrefs(); if (playing.value && !paused.value) startFrom(index.value) }
export function setFollow(on) { follow.value = on; savePrefs() }

const progress = computed(() => (segments.value.length ? index.value / segments.value.length : 0))

export function useNarration() {
  return { supported, playing, paused, rate, voices, voiceName, follow, segments, index, progress, countdown, error }
}

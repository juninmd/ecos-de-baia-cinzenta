// Narração do capítulo (Web Speech API), compartilhada entre o dock, o painel e os marcadores ▶.
// Lê frase a frase, acende o parágrafo, marca a frase e, no fim, segue para o próximo capítulo.
import { ref, shallowRef, computed } from 'vue'
import { attachMarkers, clearHighlight, collectSegments, highlight } from '../lib/narration-dom.mjs'
import { speakable } from '../lib/sentences.mjs'

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
let synth = null
let goNext = null
let timer = null
let current = null // utterance em curso: eventos de uma fala cancelada são ignorados

const store = (k, v) => { try { v === undefined ? localStorage.removeItem(k) : localStorage.setItem(k, JSON.stringify(v)) } catch { /* sem storage */ } }
const load = (k) => { try { return JSON.parse(localStorage.getItem(k)) } catch { return null } }
const setContinuous = (on) => { try { sessionStorage.setItem(CONTINUOUS_KEY, on ? 'true' : 'false') } catch { /* privado */ } }
const isContinuous = () => { try { return sessionStorage.getItem(CONTINUOUS_KEY) === 'true' } catch { return false } }
const savePrefs = () => store(PREFS_KEY, { rate: rate.value, voice: voiceName.value, follow: follow.value })

function loadVoices() {
  const all = synth.getVoices()
  const pt = all.filter((v) => /^pt[-_]BR$/i.test(v.lang))
  voices.value = pt.length ? pt : all
  if (!voices.value.some((v) => v.name === voiceName.value)) {
    // Preferência histórica: voz masculina/Microsoft quando houver.
    const male = voices.value.find((v) => /Daniel|Microsoft|Felipe|Ricardo/.test(v.name)) ?? voices.value.find((v) => !/Google/.test(v.name))
    voiceName.value = (male ?? voices.value[0])?.name ?? ''
  }
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
  u.onend = advance
  u.onerror = (e) => { if (e.error !== 'interrupted' && e.error !== 'canceled') advance() }
  current = u
  synth.speak(u)
}

function finish() {
  playing.value = false
  paused.value = false
  clearHighlight()
  index.value = 0
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
  synth.cancel()
  cancelCountdown()
  setContinuous(true)
  if (!segments.value.length) prepare()
  index.value = Math.min(i, Math.max(segments.value.length - 1, 0))
  playing.value = true
  paused.value = false
  speakCurrent()
}

export const play = () => {
  if (paused.value) { synth.resume(); paused.value = false; setContinuous(true); return }
  if (!playing.value) startFrom(index.value)
}
export const pause = () => { if (playing.value) { synth.pause(); paused.value = true; setContinuous(false) } }
export const toggle = () => (playing.value && !paused.value ? pause() : play())

export function stop() {
  current = null
  synth?.cancel()
  playing.value = false
  paused.value = false
  index.value = 0
  clearHighlight()
  setContinuous(false)
}

// Troca de página: para o que estava falando, recoleta e retoma se o modo contínuo estiver ligado.
export function onPageChange() {
  const resume = isContinuous()
  current = null
  synth?.cancel()
  clearInterval(timer)
  countdown.value = 0
  playing.value = false
  paused.value = false
  index.value = 0
  clearHighlight()
  setTimeout(() => { prepare(); if (resume && supported.value) startFrom(0) }, 400)
}

export function setRate(v) { rate.value = v; savePrefs(); if (playing.value && !paused.value) startFrom(index.value) }
export function setVoice(name) { voiceName.value = name; savePrefs(); if (playing.value && !paused.value) startFrom(index.value) }
export function setFollow(on) { follow.value = on; savePrefs() }

const progress = computed(() => (segments.value.length ? index.value / segments.value.length : 0))

export function useNarration() {
  return { supported, playing, paused, rate, voices, voiceName, follow, segments, index, progress, countdown }
}

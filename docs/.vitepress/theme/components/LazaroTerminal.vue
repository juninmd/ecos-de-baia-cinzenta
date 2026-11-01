<script setup>
import { ref, nextTick, watch } from 'vue'
import { complete, runCommand } from '../terminal-lore.mjs'

const props = defineProps({
  isOpen: Boolean,
  chapter: { type: Number, default: 1 },
  total: { type: Number, default: 1 },
})
const emit = defineEmits(['close', 'go'])

const input = ref('')
const isHacked = ref(false)
const output = ref([
  { type: 'system', text: 'Conexão estabelecida...' },
  { type: 'system', text: 'Sistema Operacional Lázaro v4.0.1' },
  { type: 'info', text: 'Digite "help" para ver os comandos disponíveis.' },
])
const history = []
let cursor = 0
const inputRef = ref(null)
const bodyRef = ref(null)

const scrollToBottom = () => nextTick(() => {
  if (bodyRef.value) bodyRef.value.scrollTop = bodyRef.value.scrollHeight
})

const submit = () => {
  const raw = input.value.trim()
  if (!raw) return
  history.push(raw)
  cursor = history.length
  output.value.push({ type: 'user', text: `> ${raw}` })
  const res = runCommand(raw, { chapter: props.chapter, total: props.total, hacked: isHacked.value })
  if (res.hacked) isHacked.value = true
  if (res.clear) output.value = []
  output.value.push(...res.lines)
  input.value = ''
  scrollToBottom()
  if (res.go) emit('go', res.go)
  if (res.close) emit('close')
}

const recall = (step) => {
  cursor = Math.min(Math.max(cursor + step, 0), history.length)
  input.value = history[cursor] ?? ''
}

const autocomplete = () => {
  const matches = complete(input.value)
  if (matches.length === 1) input.value = matches[0]
}

const onKey = (e) => {
  if (e.isComposing) return
  if (e.key === 'Enter') submit()
  else if (e.key === 'ArrowUp') { e.preventDefault(); recall(-1) }
  else if (e.key === 'ArrowDown') { e.preventDefault(); recall(1) }
  else if (e.key === 'Tab') { e.preventDefault(); autocomplete() }
}

watch(() => props.isOpen, (open) => {
  if (open) nextTick(() => { inputRef.value?.focus(); scrollToBottom() })
})
</script>

<template>
  <div v-if="isOpen" class="terminal-overlay" @click.self="emit('close')" @keydown.esc="emit('close')">
    <div :class="['terminal-window', { hacked: isHacked }]" role="dialog" aria-modal="true" aria-label="Terminal de acesso Lázaro">
      <div class="terminal-header">
        <span class="terminal-title">TERMINAL DE ACESSO LÁZARO // V4.0.1 {{ isHacked ? '[ADMIN]' : '' }}</span>
        <button class="close-btn" aria-label="Fechar terminal" @click="emit('close')">✕</button>
      </div>
      <div class="terminal-body" ref="bodyRef" @click="inputRef?.focus()">
        <div role="log" aria-live="polite">
          <div v-for="(line, index) in output" :key="index" :class="['line', line.type]">{{ line.text }}</div>
        </div>
        <div class="input-line">
          <span class="prompt" aria-hidden="true">&gt;</span>
          <input ref="inputRef" v-model="input" @keydown="onKey" type="text" class="terminal-input"
            aria-label="Comando" autocomplete="off" autocapitalize="off" spellcheck="false" />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.terminal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(4px);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.terminal-window {
  width: 100%;
  max-width: 800px;
  height: min(80vh, 80dvh);
  background: #0d0d0d;
  border: 1px solid #33ff00;
  box-shadow: 0 0 20px rgba(51, 255, 0, 0.2);
  display: flex;
  flex-direction: column;
  font-family: 'Fira Code', monospace;
  position: relative;
  overflow: hidden;
}

/* Scanlines */
.terminal-window::before {
  content: " ";
  position: absolute;
  inset: 0;
  background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
  background-size: 100% 2px, 3px 100%;
  z-index: 2;
  pointer-events: none;
}

.terminal-header {
  background: #1a1a1a;
  border-bottom: 1px solid #33ff00;
  padding: 10px 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.terminal-title { color: #33ff00; font-size: 0.9rem; font-weight: bold; letter-spacing: 1px; }
.close-btn { background: none; border: none; color: #33ff00; cursor: pointer; font-size: 1.2rem; min-width: 44px; min-height: 44px; }
.terminal-body { flex: 1; padding: 20px; overflow-y: auto; color: #33ff00; font-size: 1rem; line-height: 1.5; }
.line { margin-bottom: 5px; text-shadow: 0 0 5px rgba(51, 255, 0, 0.5); overflow-wrap: anywhere; }
.line.user { color: #fff; }
.line.error { color: #ff3333; text-shadow: 0 0 5px rgba(255, 51, 51, 0.5); }
.line.warning { color: #ffcc00; }
.line.system { color: #00ccff; }
.line.danger { color: #ff0000; font-weight: bold; }
.line.cmd-list { white-space: pre-wrap; }
.input-line { display: flex; align-items: center; margin-top: 10px; }
.prompt { color: #33ff00; margin-right: 10px; }
.terminal-input { background: transparent; border: none; color: #fff; font: inherit; flex: 1; outline: none; caret-color: #33ff00; min-width: 0; }

/* Modo administrador (Dante) */
.terminal-window.hacked { border-color: #f00; box-shadow: 0 0 20px rgba(255, 0, 0, 0.3); }
.terminal-window.hacked .terminal-header { border-bottom-color: #f00; }
.terminal-window.hacked .terminal-title,
.terminal-window.hacked .close-btn,
.terminal-window.hacked .terminal-body,
.terminal-window.hacked .prompt,
.terminal-window.hacked .line.success { color: #f00; }
.terminal-window.hacked .terminal-input { caret-color: #f00; }
.terminal-window.hacked .line.system { color: #f66; }
.terminal-window.hacked .line { text-shadow: 0 0 5px rgba(255, 0, 0, 0.5); }

@media (max-width: 640px) {
  .terminal-overlay { padding: 8px; }
  .terminal-window { height: 92dvh; }
  .terminal-body { padding: 14px; font-size: 0.92rem; }
}
</style>

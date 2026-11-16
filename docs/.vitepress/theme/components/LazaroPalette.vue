<script setup>
// Paleta Lázaro: busca + terminal numa janela só (Ctrl K ou `). Mesmos comandos e trava de spoiler.
import { computed, nextTick, ref, watch } from 'vue'
import { complete, runCommand } from '../terminal-lore.mjs'
import { chapterTitle, searchPalette } from '../lib/palette-search.mjs'
import { castAt } from '../lib/cast.mjs'

const props = defineProps({
  isOpen: Boolean,
  chapter: { type: Number, default: 1 },
  chapters: { type: Array, default: () => [] },
  pages: { type: Array, default: () => [] },
})
const emit = defineEmits(['close', 'go', 'link'])

const input = ref('')
const sel = ref(0)
const hacked = ref(false)
const log = ref([
  { type: 'system', text: 'Sistema Operacional Lázaro v5 · conexão estabelecida.' },
  { type: 'info', text: 'Busque um capítulo, um personagem ou digite "help".' },
])
const history = []
let cursor = 0
const inputRef = ref(null)

const total = computed(() => props.chapters.at(-1)?.number ?? 1)
const list = computed(() => props.chapters.map((c) => ({ number: c.number, title: chapterTitle(c.title) })))
const items = computed(() => {
  const found = searchPalette(input.value, { chapters: list.value, cast: castAt(props.chapter), pages: props.pages, furthest: props.chapter })
  return found.length || !input.value.trim() ? found : [{ group: 'Executar', kind: 'command', label: input.value.trim(), hint: 'Enter', run: input.value.trim() }]
})
const icon = { command: '›', chapter: '§', locked: '⊘', person: '◉', page: '▤' }

const logRef = ref(null)
const scrollEnd = () => nextTick(() => { if (logRef.value) logRef.value.scrollTop = logRef.value.scrollHeight })

function exec(raw) {
  history.push(raw)
  cursor = history.length
  log.value.push({ type: 'user', text: `> ${raw}` })
  const res = runCommand(raw, { chapter: props.chapter, total: total.value, hacked: hacked.value })
  if (res.hacked) hacked.value = true
  if (res.clear) log.value = []
  log.value.push(...res.lines)
  input.value = ''
  sel.value = 0
  scrollEnd()
  if (res.go) emit('go', res.go)
  if (res.close) emit('close')
}

function choose(item) {
  if (!item) return
  if (item.link) { emit('link', item.link); return }
  exec(item.run)
}

function onKey(e) {
  if (e.isComposing) return
  const n = items.value.length
  if (e.key === 'ArrowDown') { e.preventDefault(); sel.value = (sel.value + 1) % Math.max(n, 1) }
  else if (e.key === 'ArrowUp') {
    e.preventDefault()
    if (!input.value && history.length) { cursor = Math.max(cursor - 1, 0); input.value = history[cursor] ?? ''; return }
    sel.value = (sel.value - 1 + n) % Math.max(n, 1)
  } else if (e.key === 'Enter') { e.preventDefault(); choose(items.value[sel.value]) }
  else if (e.key === 'Tab') {
    e.preventDefault()
    const m = complete(input.value)
    if (m.length) input.value = m[0] + (m[0] === 'ir' ? ' ' : '')
  } else if (e.key === 'Escape') emit('close')
}

watch(input, () => { sel.value = 0 })
let opener = null
watch(() => props.isOpen, (open) => {
  if (open) { opener = document.activeElement; nextTick(() => { inputRef.value?.focus(); scrollEnd() }) } else opener?.focus?.()
})
</script>

<template>
  <Transition name="lz">
    <div v-if="isOpen" class="lz-overlay" @click.self="emit('close')">
      <div :class="['lz', { hacked }]" role="dialog" aria-modal="true" aria-label="Lázaro: buscar ou comandar">
        <div class="lz-in">
          <span aria-hidden="true">&gt;_</span>
          <input ref="inputRef" v-model="input" autocomplete="off" spellcheck="false" aria-label="Buscar ou comandar"
            role="combobox" aria-expanded="true" aria-controls="lz-list" :aria-activedescendant="`lz-opt-${sel}`"
            placeholder="buscar capítulo, personagem ou digitar comando…" @keydown="onKey">
          <kbd>Esc</kbd>
        </div>
        <div class="lz-out">
          <ul id="lz-list" role="listbox" class="lz-list">
            <template v-for="(it, i) in items" :key="it.group + it.label">
              <li v-if="i === 0 || items[i - 1].group !== it.group" class="lz-grp" role="presentation">{{ it.group }}</li>
              <li :id="`lz-opt-${i}`" role="option" :aria-selected="i === sel" :class="['lz-row', it.kind, { sel: i === sel }]"
                @mouseenter="sel = i" @click="choose(it)">
                <span class="k" aria-hidden="true">{{ icon[it.kind] }}</span><span class="l">{{ it.label }}</span><small>{{ it.hint }}</small>
              </li>
            </template>
          </ul>
          <div ref="logRef" class="lz-log" aria-live="polite">
            <div v-for="(l, i) in log" :key="i" :class="`t-${l.type}`">{{ l.text }}</div>
          </div>
        </div>
        <div class="lz-foot">
          <span><kbd>↑↓</kbd> navegar</span><span><kbd>Enter</kbd> abrir</span><span><kbd>Tab</kbd> completar</span>
          <span class="right">LÁZARO OS · leitura até o cap. {{ chapter }}</span>
        </div>
      </div>
    </div>
  </Transition>
</template>

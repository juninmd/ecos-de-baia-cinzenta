<script setup>
// Dock único de leitura: substitui os botões flutuantes. Anel = progresso do capítulo.
import { computed, ref, watch } from 'vue'
import { useReading, showDock } from '../composables/useReading.js'
import { useReaderPrefs, toggleFocus } from '../composables/useReaderPrefs.js'
import { useNarration, toggle as toggleVoice } from '../composables/useNarration.js'
import TypePanel from './TypePanel.vue'
import NarrationPanel from './NarrationPanel.vue'

defineProps({ prev: Object, next: Object, isChapter: Boolean })
const emit = defineEmits(['go', 'lazaro'])
const { progress, dockVisible } = useReading()
const { focus } = useReaderPrefs()
const { supported, playing, paused, progress: spoken, error } = useNarration()
const panel = ref('')
const C = 2 * Math.PI * 19
const pct = computed(() => Math.round((playing.value ? spoken.value : progress.value) * 100))
const speaking = computed(() => playing.value && !paused.value)

const open = (name) => { panel.value = panel.value === name ? '' : name }
const onPlay = () => toggleVoice()
// Sem voz no aparelho: abre o painel com o aviso em vez de falhar calado.
watch(error, (msg) => { if (msg) panel.value = 'audio' })
</script>

<template>
  <div :class="['reader-dock-wrap', { hidden: !dockVisible && !panel && !playing }]" @pointerenter="showDock">
    <Transition name="sd-pop">
      <TypePanel v-if="panel === 'type'" class="dock-pop" @close="panel = ''" />
    </Transition>
    <Transition name="sd-pop">
      <NarrationPanel v-if="panel === 'audio' && isChapter" class="dock-pop" @close="panel = ''" />
    </Transition>
    <nav class="reader-dock" aria-label="Controles de leitura">
      <button v-if="isChapter" type="button" :disabled="!prev" :aria-label="prev ? `Capítulo anterior: ${prev.title}` : 'Sem capítulo anterior'"
        data-tip="Anterior · Alt ←" @click="emit('go', prev)">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 6l-6 6 6 6" /></svg>
      </button>
      <button v-if="isChapter && supported" type="button" :aria-pressed="speaking" :aria-label="speaking ? 'Pausar narração' : 'Ouvir capítulo'"
        :data-tip="speaking ? 'Pausar' : 'Ouvir'" @click="onPlay">
        <svg v-if="!speaking" viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5l11 7-11 7z" class="fill" /></svg>
        <span v-else class="eq" aria-hidden="true"><i /><i /><i /><i /></span>
      </button>
      <button v-if="isChapter && supported" type="button" :aria-pressed="panel === 'audio'" aria-label="Opções de narração"
        data-tip="Voz e velocidade" @click="open('audio')">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 8h10M18 8h2M4 16h2M10 16h10" /><circle cx="16" cy="8" r="2" /><circle cx="8" cy="16" r="2" /></svg>
      </button>
      <button type="button" :aria-pressed="panel === 'type'" aria-label="Tipografia" data-tip="Tipografia · Ctrl ±" @click="open('type')">
        <span class="aa" aria-hidden="true">Aa</span>
      </button>
      <div class="dock-ring" role="progressbar" :aria-valuenow="pct" aria-valuemin="0" aria-valuemax="100" aria-label="Progresso do capítulo">
        <svg viewBox="0 0 44 44" aria-hidden="true">
          <circle cx="22" cy="22" r="19" class="track" />
          <circle cx="22" cy="22" r="19" class="bar" :stroke-dasharray="C" :stroke-dashoffset="C * (1 - pct / 100)" />
        </svg>
        <span>{{ pct }}%</span>
      </div>
      <button type="button" :aria-pressed="focus" :aria-label="focus ? 'Sair do modo foco' : 'Modo foco'" data-tip="Foco · F" @click="toggleFocus">
        <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="8" /><path d="M12 4a8 8 0 010 16z" class="fill" /></svg>
      </button>
      <button type="button" aria-label="Abrir Lázaro: buscar ou comandar" data-tip="Lázaro · Ctrl K" @click="emit('lazaro')">
        <span class="mono" aria-hidden="true">&gt;_</span>
      </button>
      <button v-if="isChapter" type="button" :disabled="!next" :aria-label="next ? `Próximo capítulo: ${next.title}` : 'Último capítulo'"
        data-tip="Próximo · Alt →" @click="emit('go', next)">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 6l6 6-6 6" /></svg>
      </button>
    </nav>
  </div>
</template>

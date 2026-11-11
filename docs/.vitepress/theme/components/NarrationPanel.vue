<script setup>
// Painel de narração: voz pt-BR, velocidade, seguir para o próximo capítulo e parar.
import { useNarration, setRate, setVoice, setFollow, stop } from '../composables/useNarration.js'

const emit = defineEmits(['close'])
const { voices, voiceName, rate, follow, playing, paused, index, segments } = useNarration()
const rates = [0.8, 0.9, 1, 1.2, 1.5]
const short = (n) => n.replace(/^(Microsoft|Google)\s+/, '').replace(/\s*\(.*\)$/, '')
</script>

<template>
  <div :class="['dock-panel narration-panel', { live: playing && !paused }]" role="dialog" aria-label="Narração" @keydown.esc="emit('close')">
    <div class="np-head">
      <span class="np-wave" aria-hidden="true"><i v-for="n in 12" :key="n" :style="{ animationDelay: `${n * -0.08}s` }" /></span>
      <div>
        <strong>Narração</strong>
        <small aria-live="polite">{{ playing ? `Frase ${index + 1} de ${segments.length}` : 'Toque ▶ ao lado de um parágrafo para começar dali' }}</small>
      </div>
    </div>
    <label class="dp-label" for="sd-voice">Voz</label>
    <select id="sd-voice" class="dp-select" :value="voiceName" :disabled="!voices.length" @change="setVoice($event.target.value)">
      <option v-if="!voices.length" value="">Carregando vozes…</option>
      <option v-for="v in voices" :key="v.name" :value="v.name">{{ short(v.name) }}</option>
    </select>
    <span class="dp-label">Velocidade</span>
    <div class="dp-seg" role="group" aria-label="Velocidade">
      <button v-for="r in rates" :key="r" type="button" :aria-pressed="rate === r" @click="setRate(r)">{{ r }}×</button>
    </div>
    <label class="dp-check"><input type="checkbox" :checked="follow" @change="setFollow($event.target.checked)"> Seguir para o próximo capítulo</label>
    <button v-if="playing" type="button" class="dp-stop" @click="stop(); emit('close')">Parar narração</button>
  </div>
</template>

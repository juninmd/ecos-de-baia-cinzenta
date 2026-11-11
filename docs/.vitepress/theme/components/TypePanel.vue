<script setup>
// Painel Aa: tamanho (70–150%), entrelinha, papel e letra.
import { useReaderPrefs, setPref, changeSize } from '../composables/useReaderPrefs.js'
import { LINE, SIZE } from '../lib/reader-prefs.mjs'

const emit = defineEmits(['close'])
const { prefs } = useReaderPrefs()
const skins = [['auto', 'Tema'], ['noite', 'Noite'], ['sepia', 'Sépia'], ['papel', 'Papel']]
const faces = [['serifa', 'Serifa'], ['condensada', 'Condensada']]
</script>

<template>
  <div class="dock-panel" role="dialog" aria-label="Tipografia" @keydown.esc="emit('close')">
    <div class="dp-row">
      <span class="dp-label">Tamanho</span>
      <div class="dp-stepper">
        <button type="button" aria-label="Diminuir fonte" title="Ctrl −" :disabled="prefs.size <= SIZE.min" @click="changeSize(-1)">A−</button>
        <button type="button" aria-label="Fonte padrão" title="Ctrl 0" @click="changeSize(0)">{{ prefs.size }}%</button>
        <button type="button" aria-label="Aumentar fonte" title="Ctrl +" :disabled="prefs.size >= SIZE.max" @click="changeSize(1)">A+</button>
      </div>
    </div>
    <label class="dp-label dp-split" for="sd-line">Entrelinha <span>{{ prefs.lineHeight.toFixed(2) }}</span></label>
    <input id="sd-line" type="range" :min="LINE.min" :max="LINE.max" step="0.05" :value="prefs.lineHeight"
      @input="setPref('lineHeight', +$event.target.value)">
    <span class="dp-label">Papel</span>
    <div class="dp-seg" role="group" aria-label="Papel">
      <button v-for="[v, l] in skins" :key="v" type="button" :class="`sw-${v}`" :aria-pressed="prefs.skin === v" @click="setPref('skin', v)">{{ l }}</button>
    </div>
    <span class="dp-label">Letra</span>
    <div class="dp-seg" role="group" aria-label="Letra">
      <button v-for="[v, l] in faces" :key="v" type="button" :class="`face-${v}`" :aria-pressed="prefs.face === v" @click="setPref('face', v)">{{ l }}</button>
    </div>
  </div>
</template>

<script setup>
// Dossiê do elenco: retratos canônicos com estado no capítulo mais avançado já lido.
// Quem o leitor ainda não conheceu fica CLASSIFICADO, salvo se ele pedir os spoilers.
import { computed, onMounted, ref } from 'vue'
import { withBase } from 'vitepress'
import { castAt } from '../lib/cast.mjs'
import { loadFurthest } from '../composables/useReading.js'

defineProps({ title: { type: String, default: 'Dossiê sem spoiler' } })
const chapter = ref(1)
const reveal = ref(false)
onMounted(() => { chapter.value = loadFurthest() })
const cast = computed(() => castAt(reveal.value ? 999 : chapter.value))
const locked = computed(() => cast.value.filter((p) => p.locked).length)
const reduced = typeof window !== 'undefined' && matchMedia('(prefers-reduced-motion: reduce)').matches

function tilt(e) {
  if (reduced || e.pointerType === 'touch') return
  const el = e.currentTarget
  const r = el.getBoundingClientRect()
  const x = (e.clientX - r.left) / r.width
  const y = (e.clientY - r.top) / r.height
  el.style.setProperty('--ry', `${(x - 0.5) * 14}deg`)
  el.style.setProperty('--rx', `${(0.5 - y) * 14}deg`)
  el.style.setProperty('--gx', `${x * 100}%`)
  el.style.setProperty('--gy', `${y * 100}%`)
}
const untilt = (e) => { e.currentTarget.style.setProperty('--rx', '0deg'); e.currentTarget.style.setProperty('--ry', '0deg') }
</script>

<template>
  <section class="cast-dossier">
    <div class="cd-head">
      <div>
        <p class="sd-eyebrow">Elenco · leitura até o cap. {{ chapter }}</p>
        <h2 class="sd-h2">{{ title }}</h2>
      </div>
      <label v-if="locked || reveal" class="dp-check cd-reveal">
        <input v-model="reveal" type="checkbox"> Mostrar todos (contém spoilers)
      </label>
    </div>
    <div class="cd-grid">
      <component :is="p.locked ? 'div' : 'a'" v-for="p in cast" :key="p.key" :class="['cast-card', { locked: p.locked }]"
        :href="p.locked ? undefined : withBase(`/personagens#${p.anchor}`)" @pointermove="tilt" @pointerleave="untilt">
        <img :src="withBase(p.retrato)" :alt="p.locked ? 'Personagem ainda não apresentado' : `Retrato de ${p.nome}`" loading="lazy" decoding="async">
        <span class="cc-glare" aria-hidden="true" />
        <span v-if="!p.locked && p.rotulo" :class="['cc-pill', p.tom]">{{ p.rotulo }}</span>
        <span class="cc-lbl">
          <strong>{{ p.locked ? '????' : p.nome }}</strong>
          <small>{{ p.locked ? 'Aparece mais adiante' : `${p.papel} · desde o cap. ${p.desde}` }}</small>
        </span>
      </component>
    </div>
  </section>
</template>

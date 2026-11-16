<script setup>
// Abertura da home: capa do capítulo 1 sob chuva viva, título em três tempos e números reais da obra.
import { computed, onMounted, ref } from 'vue'
import { withBase } from 'vitepress'
import { data as chapters } from '../chapters.data.mjs'
import { loadFurthest, useReading } from '../composables/useReading.js'
import RainCanvas from './RainCanvas.vue'

const { furthest } = useReading()
const ready = ref(false)
onMounted(() => { loadFurthest(); ready.value = true })

const words = chapters.reduce((s, c) => s + c.words, 0)
const stats = [
  [chapters.length, 'capítulos'],
  [4, 'livros'],
  [Math.round(words / 1000), 'mil palavras'],
  [Math.round(words / 200 / 60), 'horas de leitura'],
]
const resume = computed(() => (ready.value && furthest.value > 1 ? chapters.find((c) => c.n === furthest.value) : null))
</script>

<template>
  <header class="home-hero">
    <img class="hh-bg" :src="withBase('/capitulo_1.jpg')" alt="" fetchpriority="high" decoding="async">
    <RainCanvas />
    <div class="hh-in">
      <p class="hh-eyebrow">Thriller noir cyberpunk · escrito por IA sob supervisão humana</p>
      <h1 class="hh-title" aria-label="Ecos de Baía Cinzenta">
        <span><span>Ecos de</span></span><span><span>Baía</span></span><span><span>Cinzenta</span></span>
      </h1>
      <p class="hh-tag">A chuva em Baía Cinzenta não lavava nada; ela apenas empurrava a sujeira de um lado para o outro.</p>
      <div class="hh-ctas">
        <a v-if="resume" class="sd-btn pri" :href="withBase(`/capitulo-${resume.n}`)">Continuar · Cap. {{ resume.n }} <small>{{ resume.title }}</small></a>
        <a v-else class="sd-btn pri" :href="withBase('/capitulo-1')">Iniciar investigação <small>Cap. 1</small></a>
        <a class="sd-btn" href="#mapa">Abrir o mapa da obra</a>
        <a class="sd-btn ghost" :href="withBase('/cronologia')">Arquivos</a>
      </div>
      <dl class="hh-stats">
        <div v-for="[n, l] in stats" :key="l"><dt>{{ l }}</dt><dd>{{ n.toLocaleString('pt-BR') }}</dd></div>
      </dl>
    </div>
  </header>
</template>
